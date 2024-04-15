"""
Django views for the dot-dynamic-scopes package.
"""

import functools
import json

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.views import IntrospectTokenView
from oauthlib.oauth2 import Server

from .models import Scope
from .settings import app_settings


def protected_resource(scopes=None):
    """
    Implementation of protected_resource decorator that saves the client on the
    request for the view function to use.

    Cribbed from django-oauth-toolkit.
    """
    _scopes = scopes or []

    def decorator(view_func):
        @functools.wraps(view_func)
        def _validate(request, *args, **kwargs):
            validator = OAuth2Validator()
            core = OAuthLibCore(Server(validator))
            valid, oauthlib_req = core.verify_request(request, scopes=_scopes)
            if valid:
                request.client = oauthlib_req.client
                request.resource_owner = oauthlib_req.user
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()

        return _validate

    return decorator


@require_http_methods(["GET", "POST"])
@csrf_exempt
@protected_resource(scopes=[app_settings.INTROSPECT_SCOPE])
def introspect_token(request):
    """
    Version of the introspection view protected by a regular scope instead of
    read-write scopes.

    Also allows for the required scope to be changed using a setting.
    """
    if request.method == "GET":
        token = request.GET.get("token", None)
    else:
        token = request.POST.get("token", None)
    return IntrospectTokenView.get_token_response(token)


@require_POST
@csrf_exempt
@protected_resource(scopes=[app_settings.REGISTER_SCOPE_SCOPE])
def register_scope(request):
    """
    Implements an endpoint for registering a scope.
    """
    # Get the scope data from the request body
    scope_data = json.loads(request.body) if request.body else {}
    try:
        try:
            # If a scope with the given name already exists, find it
            scope = Scope.objects.get(name=scope_data["name"])
        except Scope.DoesNotExist:
            # If no scope with the given name exists, create it
            _ = Scope.objects.create(
                application=request.client,
                name=scope_data["name"],
                description=scope_data["description"],
                is_default=scope_data.get("is_default", False),
            )
            # Respond with a 201 Created
            return HttpResponse(status=201)
    except KeyError as exc:
        # A key missing in the data should be reported as a bad request
        return HttpResponse(
            status=400,
            content="'{}' must be given in request data".format(exc.args[0]),
            content_type="text/plain",
        )
    # If the scope does exist, check that the current application is the
    # owner of the scope before updating it
    if scope.application and scope.application == request.client:
        scope.description = scope_data["description"]
        scope.is_default = scope_data.get("is_default", False)
        scope.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)

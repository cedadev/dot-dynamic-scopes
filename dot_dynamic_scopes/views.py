"""
Django views for the dot-dynamic-scopes package.
"""

import re, json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import get_access_token_model
from oauth2_provider.views import ReadWriteScopedResourceView

from .models import Scope


@method_decorator(csrf_exempt, name = "dispatch")
class RegisterScopeView(ReadWriteScopedResourceView):
    """
    Implements an endpoint for registering a scope.

    To access this view the request must pass an OAuth2 Bearer Token which is
    allowed to write to the scope `register-scope`.
    """
    required_scopes = ["register-scope"]

    def post(self, request, *args, **kwargs):
        """
        Get the scope information from the request body and create the scope as
        required.
        """
        # Get the scope data from the request body
        scope_data = json.loads(request.body)
        try:
            # If a scope with the given name already exists, find it
            scope = Scope.objects.get(name = scope_data['name'])
        except Scope.DoesNotExist:
            # If no scope with the given name exists, create it
            _ = Scope.objects.create(
                application = request.client,
                name = scope_data['name'],
                description = scope_data['description'],
                is_default = scope_data.get('is_default', False)
            )
            # Respond with a 201 Created
            return HttpResponse(status = 201)
        # If the scope does exist, check that the current application is allowed
        # to update it before updating it
        if scope.application and scope.application.pk == request.client.pk:
            scope.description = scope_data['description']
            scope.is_default = scope_data.get('is_default', False)
            scope.save()
            return HttpResponse(status = 200)
        else:
            return HttpResponse(status = 403)

"""
Django signal handlers for the dot-dynamic-scopes package.
"""

from django.conf import settings

from oauth2_provider.settings import oauth2_settings

from .models import Scope


def register_scopes(app_config, verbosity = 2, interactive = True, **kwargs):
    """
    ``post_migrate`` signal handler that ensures the scopes required for the
    introspection and register-scope endpoints are registered when running as an
    authorisation server.

    The signal is connected in ``apps.py``.
    """
    # If we are running as an authorisation server, make
    endpoint = getattr(settings, 'DOT_DYNAMIC_SCOPES', {}).get(
        'RESOURCE_SERVER_REGISTER_SCOPE_URL',
        None
    )
    if not endpoint:
        Scope.register(
            name = oauth2_settings.READ_SCOPE,
            description = 'Reading scope'
        )
        Scope.register(
            name = oauth2_settings.WRITE_SCOPE,
            description = 'Writing scope'
        )
        Scope.register(
            name = 'introspection',
            description = 'Introspect token'
        )
        Scope.register(
            name = 'register-scope',
            description = 'Register scope'
        )

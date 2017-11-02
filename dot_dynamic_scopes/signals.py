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
    # Register any scopes in the oauth2_provider settings
    for name, description in oauth2_settings.SCOPES.items():
        Scope.register(
            name,
            description,
            name in oauth2_settings.DEFAULT_SCOPES
        )

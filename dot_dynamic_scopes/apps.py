"""
Django app config for the dot-dynamic-scopes package.
"""

from django.apps import AppConfig as BaseAppConfig
from django.db.models.signals import post_migrate
from django.conf import settings

from oauth2_provider import settings as dot_settings

from .models import Scope


class AppConfig(BaseAppConfig):
    def ready(self):
        # If we are running as an authorisation server, make sure that we register
        # the scopes required for the introspection and register-scope endpoints
        endpoint = getattr(settings, 'DOT_DYNAMIC_SCOPES', {}).get(
            'RESOURCE_SERVER_REGISTER_SCOPE_URL',
            None
        )
        if not endpoint:
            def register_scopes(*args, **kwargs):
                Scope.register(
                    name = dot_settings.READ_SCOPE,
                    description = 'Reading scope'
                )
                Scope.register(
                    name = dot_settings.WRITE_SCOPE,
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
            post_migrate.connect(register_scopes, sender = self)

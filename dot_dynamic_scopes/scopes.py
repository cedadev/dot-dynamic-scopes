"""Django OAuth Toolkit scopes backend for the dot-dynamic-scopes package."""

import django.core.cache
from oauth2_provider.scopes import BaseScopes

from .models import Scope


class DynamicScopes(BaseScopes):
    """Scopes backend that provides scopes from a Django model."""

    @staticmethod
    def _get_scopes():
        return {scope.name: scope.description for scope in Scope.objects.all()}

    def get_all_scopes(self):
        """Get all scopes."""
        return django.core.cache.cache.get_or_set(
            "dot-dynamic-scopes-scopes", self._get_scopes, 30
        )

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        """Get only scopes valid for this application and request."""
        return list(self.get_all_scopes().keys())

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        """Get scopes which are added by default."""
        return [scope.name for scope in Scope.objects.filter(is_default=True)]

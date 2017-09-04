"""
Django OAuth Toolkit scopes backend for the dot-dynamic-scopes package.
"""

from django.conf import settings
from django.utils import module_loading

from oauth2_provider.scopes import BaseScopes

from .models import Scope


class RestrictApplicationScopes(BaseScopes):
    """
    Scopes backend that provides scopes from a Django model.
    """
    def get_all_scopes(self):
        return { scope.name: scope.description for scope in Scope.objects.all() }

    def get_available_scopes(self, application = None, request = None, *args, **kwargs):
        return list(self.get_all_scopes().keys())

    def get_default_scopes(self, application = None, request = None, *args, **kwargs):
        return [scope.name for scope in Scope.objects.filter(is_default = True)]

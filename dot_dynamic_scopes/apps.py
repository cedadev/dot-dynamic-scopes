"""
Django app config for the dot-dynamic-scopes package.
"""

from django.apps import AppConfig as BaseAppConfig
from django.db.models.signals import post_migrate


class AppConfig(BaseAppConfig):
    name = 'dot_dynamic_scopes'

    def ready(self):
        from .signals import register_scopes
        post_migrate.connect(register_scopes, sender = self)

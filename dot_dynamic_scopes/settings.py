"""
Settings for the ``dot_dynamic_scopes`` app.
"""

from django.conf import settings

from jasmin_django_utils.appsettings import SettingsObject, Setting


class AppSettings(SettingsObject):
    RESOURCE_SERVER_REGISTER_SCOPE_URL = Setting(default = None)
    INTROSPECT_SCOPE = Setting()
    REGISTER_SCOPE_SCOPE = Setting()


app_settings = AppSettings('DOT_DYNAMIC_SCOPES', getattr(settings, 'DOT_DYNAMIC_SCOPES', {}))

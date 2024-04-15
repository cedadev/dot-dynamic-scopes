"""
Settings for the ``dot_dynamic_scopes`` app.
"""
from settings_object import Setting, SettingsObject


class AppSettings(SettingsObject):
    RESOURCE_SERVER_REGISTER_SCOPE_URL = Setting(default=None)
    INTROSPECT_SCOPE = Setting()
    REGISTER_SCOPE_SCOPE = Setting()


app_settings = AppSettings("DOT_DYNAMIC_SCOPES")

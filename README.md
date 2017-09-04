# dot-dynamic-scopes

Django OAuth Toolkit extension to provide dynamic scopes backed by a Django model.

In a vanilla Django OAuth Toolkit application, all the scopes that an access token
can be granted for must be defined in the settings on the authorisation server. In
the case where the authorisation and resource servers are the same, this is not too
much of a problem. However, in the case where the resource servers are separate,
and perhaps numerous, it means that the authorisation server must know *at deployment
time* about all the possible scopes on all the resource servers.

This Django application provides a scopes-backend for Django OAuth Toolkit that is
backed by a Django model, meaning that the scopes information is stored in the
database and can be dynamic. It also provides an additional view that can be used
by resource servers to register their scopes, meaning that the authorisation server
does not need to know about all the possible scopes and resource servers in advance.
This also means that a new resource can be protected by a new resource server without
needing to roll out any settings updates on the authorisation server. Similar
to the [introspection endpoint](https://github.com/evonove/django-oauth-toolkit/blob/master/docs/resource_server.rst),
this is implemented by having the scope registration view protected by a special
scope which is only granted to resource servers.


## Installation

Just install directly from Github using using `pip`:

```bash
pip install -e git+https://github.com/cedadev/dot-dynamic-scopes.git@tag_branch_or_commit_hash#egg=dot_dynamic_scopes
```

## Usage

The application must be enabled in `settings.py`:

```python
# Add dot_dynamic_scopes to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'dot_dynamic_scopes',
]

# Tell Django OAuth Toolkit to use the dynamic scopes backend
OAUTH2_PROVIDER = {
    'SCOPES_BACKEND_CLASS': 'dot_dynamic_scopes.scopes.DynamicScopes',
    # ...
}
```

If your authorisation and resource servers are the same, that is all the configuration
that is required.

If you have seperate resource servers, you also need to enable the scope registration
endpoint in `urls.py` on the authorisation server:

```python
urls = [
    # ...
    url(r'^o/register_scope/$', dot_dynamic_scopes.views.RegisterScopeView.as_view(), name = 'register-scope'),
    # ...
]
```

Then add the URL for that endpoint to `settings.py` on each resource server:

```python
DOT_DYNAMIC_SCOPES = {
    'RESOURCE_SERVER_REGISTER_SCOPE_URL': 'https://my-host.com/oauth/register_scope/',
}
```

You then need to register the scopes used by your application. This is done in the
same way regardless of whether you are using a separate resource server or not.
Scopes are registered using the `Scope.register` method - this method will transparently
either call out to the `RESOURCE_SERVER_REGISTER_SCOPE_URL` if it is defined, or
create an instance in the local database if it is not defined.

A good place to create scopes is in a post-migrate handler (assuming you are applying
your database migrations on each deploy, which you should be!). For example, in `apps.py`:

```python
from django.apps import AppConfig as BaseAppConfig
from django.db.models.signals import post_migrate

from dot_dynamic_scopes.models import Scope


class AppConfig(BaseAppConfig):
    def register_scopes(self, *args, **kwargs):
        Scope.register(
            name = 'https://my-host.com/resources/my-protected-resource',
            description = 'Access to my protected resource'
        )

    def ready(self):
        post_migrate.connect(self.register_scopes, sender = self)
```

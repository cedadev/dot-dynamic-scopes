# dot-dynamic-scopes

Django OAuth Toolkit extension to provide dynamic scopes backed by a Django model.

In a vanilla Django OAuth Toolkit application, all the scopes that an access token
can be granted for must be defined in the settings on the authorisation server. In
the case where the authorisation and resource servers are the same, this is fine.
However, in the case where the resource servers are separate, and perhaps numerous,
it means that the authorisation server must know *at deployment time* about all
the possible scopes on all the resource servers.

The `dot-dynamic-scopes` Django application provides a scopes-backend for Django
OAuth Toolkit that is backed by a Django model, meaning that the scopes information
is stored in the database and can be dynamic. It also provides an additional view
that can be used by resource servers to register their scopes, meaning that the
authorisation server does not need to know about all the possible scopes and
resource servers in advance. This also means that a new resource can be protected
by a new resource server without needing to roll out any settings updates on the
authorisation server. Similar to the
[introspection endpoint](https://github.com/evonove/django-oauth-toolkit/blob/master/docs/resource_server.rst),
this is implemented by having the scope registration view protected by a special
scope which is only granted to resource servers.

**NOTE:** The extra complication added by this package is only worth using if
you have separate authorisation and resource servers. The rest of the README
assumes that this is the case.


## Installation

Just install directly from Github using using `pip`:

```bash
pip install -e git+https://github.com/cedadev/dot-dynamic-scopes.git@tag_branch_or_commit_hash#egg=dot_dynamic_scopes
```

## Usage

On both authorisation and resource servers, `dot-dynamic-scopes` must be enabled
in `settings.py`:

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

On the authorisation server, the scope registration endpoint must be enabled in `urls.py`:

```python
urls = [
    # ...
    url(r'^o/register_scope/$', dot_dynamic_scopes.views.register_scope, name = 'register-scope'),
    # ...
]
```

Then add the URL for that endpoint to `settings.py` on each resource server, along
with the other required configuration for a separate resource server:

```python
OAUTH2_PROVIDER = {
    'RESOURCE_SERVER_INTROSPECTION_URL': 'https://my-authz-server.com/o/introspect/',
    'RESOURCE_SERVER_AUTH_TOKEN': '3yUqsWtwKYKHnfivFcJu',
}

DOT_DYNAMIC_SCOPES = {
    'RESOURCE_SERVER_REGISTER_SCOPE_URL': 'https://my-authz-server.com/o/register_scope/',
}
```

The scopes for the authorisation server and each resource server are then configured
using the usual ``SCOPES`` and ``DEFAULT_SCOPES`` settings. However, the ``SCOPES``
setting for the authorisation server only need contain the scopes used by the
authorisation server (i.e. the scopes for the introspect and register-scope endpoints),
and ``SCOPES`` on each resource server need only contain the scopes used by that
resource server.

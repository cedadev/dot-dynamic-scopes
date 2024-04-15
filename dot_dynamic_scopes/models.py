"""
Django models for the dot-dynamic-scopes package.
"""

import requests
from django.conf import settings
from django.db import models
from oauth2_provider.settings import oauth2_settings

from .settings import app_settings


class Scope(models.Model):
    """
    Django model for an OAuth scope.
    """

    id = models.AutoField(primary_key=True)

    #: The application that created the scope
    # NOTE: This is not used to limit access to the scope in any way - we want the
    #       scope to be available to other applications in order to request access
    #       to the resource it protects!
    application = models.ForeignKey(
        oauth2_settings.APPLICATION_MODEL,
        models.CASCADE,
        # This field is nullable because it is only set for scopes created by
        # external resource servers, which have a corresponding OAuth application
        # record on the authorisation server
        blank=True,
        null=True,
        help_text="The application to which the scope belongs.",
    )
    #: The name of the scope
    name = models.CharField(
        max_length=255, unique=True, help_text="The name of the scope."
    )
    #: A brief description of the scope
    description = models.TextField(
        help_text="A brief description of the scope. This text is displayed "
        "to users when authorising access for the scope."
    )
    #: Indicates if the scope should be included in the default scopes
    is_default = models.BooleanField(
        default=False,
        help_text="Indicates if this scope should be included in the default scopes.",
    )

    @classmethod
    def register(cls, name, description, is_default=False):
        """
        Registers a scope with the given values. It always creates an instance in
        the local database, but if this resource server has an external authorisation
        server, it will also register the scope there.

        Returns ``True`` on success. Should raise on failure.
        """
        endpoint = app_settings.RESOURCE_SERVER_REGISTER_SCOPE_URL
        if endpoint:
            # If the endpoint is set, make the callout to the authz server
            token = "Bearer {}".format(oauth2_settings.RESOURCE_SERVER_AUTH_TOKEN)
            # Let any failures bubble up
            # The idea is to call this method during deployment as a post-migrate
            # hook, so we want failures to halt the deployment
            response = requests.post(
                endpoint,
                json={
                    "name": name,
                    "description": description,
                    "is_default": is_default,
                },
                headers={"Authorization": token},
            )
            # Raise the exception for anything other than 20x responses
            response.raise_for_status()
        # Always create/update the scope record locally
        _ = Scope.objects.update_or_create(
            name=name, defaults={"description": description, "is_default": is_default}
        )
        return True

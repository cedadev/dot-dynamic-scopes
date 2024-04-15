"""
Django admin configuration for the dot-dynamic-scopes package.
"""

from django.contrib import admin

from .models import Scope


@admin.register(Scope)
class ScopeAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_default")

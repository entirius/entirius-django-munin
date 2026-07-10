# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.contrib import admin

from django_munin.models import ConfigEntry, Module

AUTO_DETECTED_FIELDS = (
    "label",
    "version",
    "has_models",
    "has_api",
    "has_admin_api",
    "has_admin",
    "has_management_commands",
    "has_urls",
    "has_channels",
    "has_translations",
    "has_fixtures",
    "is_active",
)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "label",
        "version",
        "is_active",
        "enabled_in_cms",
        "has_api",
        "has_admin_api",
        "display_order",
    )
    list_filter = ("is_active", "enabled_in_cms", "has_api", "has_admin_api", "has_channels")
    search_fields = ("key", "label", "app_label")
    readonly_fields = ("app_label", "key", "created_at", "modified_at") + AUTO_DETECTED_FIELDS
    fieldsets = (
        ("Identity", {"fields": ("app_label", "key")}),
        ("Auto-Detected", {"fields": AUTO_DETECTED_FIELDS}),
        ("Admin Settings", {"fields": ("enabled_in_cms", "display_order", "config")}),
        ("Timestamps", {"fields": ("created_at", "modified_at")}),
    )


@admin.register(ConfigEntry)
class ConfigEntryAdmin(admin.ModelAdmin):
    list_display = ("key", "is_public", "description", "modified_at")
    list_filter = ("is_public",)
    search_fields = ("key", "description")
    readonly_fields = ("created_at", "modified_at")

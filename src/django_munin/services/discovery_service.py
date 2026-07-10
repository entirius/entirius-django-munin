# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Discovery service — scans installed Volkanos apps and persists to Module DB table."""

from django.apps import apps

from django_munin.introspection import introspect_module
from django_munin.models import Module

AUTO_DETECTED_FIELDS = [
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
]


def get_volkanos_apps() -> list:
    """Return AppConfigs that have is_volkanos = True."""
    return [app for app in apps.get_app_configs() if getattr(app, "is_volkanos", False)]


def derive_key(app_label: str) -> str:
    """Derive module key from app_label by stripping django_ prefix."""
    return app_label.removeprefix("django_")


def scan_modules() -> tuple[int, int, int]:
    """Scan all volkanos apps, upsert Module records.

    Returns (created, updated, deactivated) counts.
    """
    volkanos_apps = get_volkanos_apps()
    active_labels = set()
    created = 0
    updated = 0

    for app in volkanos_apps:
        app_label = app.label
        active_labels.add(app_label)
        key = derive_key(app_label)
        capabilities = introspect_module(app)

        module, was_created = Module.objects.get_or_create(
            app_label=app_label, defaults={"key": key, "is_active": True, **capabilities}
        )

        if was_created:
            created += 1
        else:
            # Overwrite auto-detected fields, preserve admin-controlled
            changed = False
            for field_name in AUTO_DETECTED_FIELDS:
                new_val = capabilities[field_name]
                if getattr(module, field_name) != new_val:
                    setattr(module, field_name, new_val)
                    changed = True
            if not module.is_active:
                module.is_active = True
                changed = True
            if changed:
                module.save()
                updated += 1

    # Deactivate modules no longer in INSTALLED_APPS
    deactivated = Module.objects.filter(is_active=True).exclude(app_label__in=active_labels).update(is_active=False)

    return created, updated, deactivated

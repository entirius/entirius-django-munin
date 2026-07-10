# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for discovery service."""

import pytest

from django_munin.models import Module
from django_munin.services.discovery_service import derive_key, get_volkanos_apps, scan_modules
from tests.factories import ModuleFactory


class TestDeriveKey:
    def test_strips_django_prefix(self):
        assert derive_key("django_pim") == "pim"

    def test_no_prefix(self):
        assert derive_key("accounts") == "accounts"

    def test_django_only(self):
        assert derive_key("django_") == ""


@pytest.mark.django_db
class TestGetVolkanosApps:
    def test_returns_volkanos_apps(self):
        """django_munin has is_volkanos = True, so it should appear."""
        volkanos_apps = get_volkanos_apps()
        app_names = [app.name for app in volkanos_apps]
        assert "django_munin" in app_names

    def test_excludes_non_volkanos(self):
        """django.contrib.auth does not have is_volkanos."""
        volkanos_apps = get_volkanos_apps()
        app_names = [app.name for app in volkanos_apps]
        assert "django.contrib.auth" not in app_names


@pytest.mark.django_db
class TestScanModules:
    def test_scan_creates_records(self):
        # post_migrate auto-discovery pre-populates the table during test DB setup
        Module.objects.all().delete()
        created, updated, deactivated = scan_modules()
        assert created >= 1  # at least django_munin itself
        assert Module.objects.filter(key="munin").exists()

    def test_scan_preserves_admin_fields(self):
        """Admin-controlled fields are preserved on re-scan."""
        scan_modules()
        module = Module.objects.get(key="munin")
        module.enabled_in_cms = False
        module.display_order = 99
        module.config = {"custom": True}
        module.save()

        scan_modules()
        module.refresh_from_db()
        assert module.enabled_in_cms is False
        assert module.display_order == 99
        assert module.config == {"custom": True}

    def test_scan_deactivates_removed_modules(self):
        """Modules not in INSTALLED_APPS get is_active=False."""
        ModuleFactory(app_label="django_removed", key="removed", is_active=True)
        scan_modules()
        removed = Module.objects.get(key="removed")
        assert removed.is_active is False

    def test_scan_idempotent(self):
        """Second scan creates 0 new records."""
        scan_modules()
        created, updated, deactivated = scan_modules()
        assert created == 0

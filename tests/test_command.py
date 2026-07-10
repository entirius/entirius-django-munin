# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for discover_modules management command."""

from io import StringIO

import pytest
from django.core.management import call_command
from django.db.models.signals import post_migrate

from django_munin.apps import discover_modules_after_migrate
from django_munin.models import Module


@pytest.mark.django_db
class TestDiscoverModulesCommand:
    def test_command_runs_successfully(self):
        out = StringIO()
        call_command("discover_modules", stdout=out)
        output = out.getvalue()
        assert "Discovered" in output
        assert "created" in output

    def test_command_creates_records(self):
        call_command("discover_modules", verbosity=0)
        assert Module.objects.filter(key="munin").exists()

    def test_command_idempotent(self):
        call_command("discover_modules", verbosity=0)
        count_after_first = Module.objects.count()
        call_command("discover_modules", verbosity=0)
        assert Module.objects.count() == count_after_first


@pytest.mark.django_db
class TestPostMigrateDiscovery:
    def test_receiver_connected(self):
        uids = [receiver[0][0] for receiver in post_migrate.receivers]
        assert "munin.post_migrate.discover" in uids

    def test_receiver_populates_modules(self):
        Module.objects.all().delete()
        discover_modules_after_migrate(sender=None, verbosity=0)
        assert Module.objects.filter(key="munin").exists()

    def test_receiver_idempotent(self):
        discover_modules_after_migrate(sender=None, verbosity=0)
        count_after_first = Module.objects.count()
        discover_modules_after_migrate(sender=None, verbosity=0)
        assert Module.objects.count() == count_after_first

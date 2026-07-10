# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import factory

from django_munin.models import ConfigEntry, Module


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module

    app_label = factory.Sequence(lambda n: f"django_test_module_{n}")
    key = factory.Sequence(lambda n: f"test_module_{n}")
    label = factory.Sequence(lambda n: f"Test Module {n}")
    version = "1.0.0"
    has_models = True
    has_api = True
    has_admin_api = False
    has_admin = True
    has_management_commands = False
    has_urls = True
    has_channels = False
    has_translations = False
    has_fixtures = False
    is_active = True
    enabled_in_cms = True
    display_order = 0
    config = {}


class ConfigEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConfigEntry

    key = factory.Sequence(lambda n: f"test.config_key_{n}")
    value = factory.LazyFunction(lambda: {"enabled": True})
    is_public = False
    description = "Test config entry"

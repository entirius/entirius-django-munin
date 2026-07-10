# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for Module and ConfigEntry models."""

import pytest
from django.db import IntegrityError

from tests.factories import ConfigEntryFactory, ModuleFactory


@pytest.mark.django_db
class TestModuleModel:
    def test_create_valid_module(self):
        module = ModuleFactory(app_label="django_pim", key="pim", label="Product Information Management")
        assert module.app_label == "django_pim"
        assert module.key == "pim"
        assert module.is_active is True

    def test_unique_app_label_constraint(self):
        ModuleFactory(app_label="django_pim", key="pim")
        with pytest.raises(IntegrityError):
            ModuleFactory(app_label="django_pim", key="pim2")

    def test_str_representation(self):
        module = ModuleFactory(key="pim", label="Product Information Management")
        assert str(module) == "pim (Product Information Management)"


@pytest.mark.django_db
class TestConfigEntryModel:
    def test_create_valid_entry(self):
        entry = ConfigEntryFactory(key="faq.max_items", value=10)
        assert entry.key == "faq.max_items"
        assert entry.value == 10

    def test_unique_key_constraint(self):
        ConfigEntryFactory(key="faq.max_items")
        with pytest.raises(IntegrityError):
            ConfigEntryFactory(key="faq.max_items")

    def test_str_representation(self):
        entry = ConfigEntryFactory(key="global.maintenance_mode")
        assert str(entry) == "global.maintenance_mode"

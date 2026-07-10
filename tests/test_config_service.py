# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for config service."""

import pytest
from django.core.exceptions import ObjectDoesNotExist

from django_munin.services import config_service
from tests.factories import ModuleFactory


@pytest.mark.django_db
class TestConfigService:
    def test_module_list_returns_only_active(self):
        ModuleFactory(key="active_mod", is_active=True)
        ModuleFactory(key="inactive_mod", is_active=False)
        result = config_service.get_module_list(is_admin=False)
        assert "active_mod" in result["modules"]
        assert "inactive_mod" not in result["modules"]

    def test_admin_includes_extra_fields(self):
        ModuleFactory(key="admin_mod", enabled_in_cms=False, display_order=5)
        result = config_service.get_module_list(is_admin=True)
        mod_data = result["modules"]["admin_mod"]
        assert "enabled_in_cms" in mod_data
        assert "display_order" in mod_data
        assert mod_data["enabled_in_cms"] is False
        assert mod_data["display_order"] == 5

    def test_public_excludes_admin_fields(self):
        ModuleFactory(key="public_mod")
        result = config_service.get_module_list(is_admin=False)
        mod_data = result["modules"]["public_mod"]
        assert "enabled_in_cms" not in mod_data
        assert "display_order" not in mod_data
        assert "app_label" not in mod_data

    def test_module_detail_404_for_unknown(self):
        with pytest.raises(ObjectDoesNotExist):
            config_service.get_module_detail(key="nonexistent")

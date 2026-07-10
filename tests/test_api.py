# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for Munin API views."""

import pytest

from tests.factories import ModuleFactory


@pytest.mark.django_db
class TestMuninAPI:
    def test_list_allows_anonymous(self, api_client):
        ModuleFactory(key="pim", label="PIM")
        response = api_client.get("/api/munin/v2/")
        assert response.status_code == 200
        assert "platform" in response.data
        assert "modules" in response.data

    def test_anonymous_gets_public_depth(self, api_client):
        ModuleFactory(key="pim", label="PIM", enabled_in_cms=False)
        response = api_client.get("/api/munin/v2/")
        mod_data = response.data["modules"]["pim"]
        assert "enabled_in_cms" not in mod_data
        assert "display_order" not in mod_data

    def test_admin_gets_full_depth(self, admin_client):
        ModuleFactory(key="pim", label="PIM", enabled_in_cms=False, display_order=3)
        response = admin_client.get("/api/munin/v2/")
        mod_data = response.data["modules"]["pim"]
        assert mod_data["enabled_in_cms"] is False
        assert mod_data["display_order"] == 3
        assert "app_label" in mod_data

    def test_response_has_platform_and_modules(self, api_client):
        response = api_client.get("/api/munin/v2/")
        assert response.status_code == 200
        assert "platform" in response.data
        assert response.data["platform"]["version"] == "2.0.0"

    def test_only_active_modules_returned(self, api_client):
        ModuleFactory(key="active", is_active=True)
        ModuleFactory(key="inactive", is_active=False)
        response = api_client.get("/api/munin/v2/")
        assert "active" in response.data["modules"]
        assert "inactive" not in response.data["modules"]

    def test_retrieve_single_module(self, api_client):
        ModuleFactory(key="pim", label="PIM", version="1.14.0")
        response = api_client.get("/api/munin/v2/pim/")
        assert response.status_code == 200
        assert response.data["label"] == "PIM"

    def test_retrieve_404_for_unknown(self, api_client):
        response = api_client.get("/api/munin/v2/nonexistent/")
        assert response.status_code == 404

    def test_admin_retrieve_includes_admin_fields(self, admin_client):
        ModuleFactory(key="pim", label="PIM", enabled_in_cms=True, display_order=2)
        response = admin_client.get("/api/munin/v2/pim/")
        assert response.status_code == 200
        assert "enabled_in_cms" in response.data
        assert "display_order" in response.data

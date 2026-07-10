# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for ConfigEntry CRUD API."""

import pytest

from tests.factories import ConfigEntryFactory


@pytest.mark.django_db
class TestConfigEntryAPI:
    def test_list_401_no_auth(self, api_client):
        response = api_client.get("/api/munin/v2/admin/entries/")
        assert response.status_code == 401

    def test_list_403_regular_user(self, regular_client):
        response = regular_client.get("/api/munin/v2/admin/entries/")
        assert response.status_code == 403

    def test_list_200_admin(self, admin_client):
        ConfigEntryFactory(key="test.key1")
        response = admin_client.get("/api/munin/v2/admin/entries/")
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_create_201(self, admin_client):
        response = admin_client.post(
            "/api/munin/v2/admin/entries/",
            {"key": "faq.max_items", "value": 10, "is_public": False, "description": "Max FAQ items"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["key"] == "faq.max_items"
        assert response.data["value"] == 10

    def test_create_400_duplicate_key(self, admin_client):
        ConfigEntryFactory(key="faq.max_items")
        response = admin_client.post(
            "/api/munin/v2/admin/entries/", {"key": "faq.max_items", "value": 20}, format="json"
        )
        assert response.status_code == 400

    def test_create_400_invalid_key_format(self, admin_client):
        response = admin_client.post(
            "/api/munin/v2/admin/entries/", {"key": "INVALID-KEY!", "value": 10}, format="json"
        )
        assert response.status_code == 400

    def test_update_200(self, admin_client):
        ConfigEntryFactory(key="faq.max_items", value=10)
        response = admin_client.patch("/api/munin/v2/admin/entries/faq.max_items/", {"value": 20}, format="json")
        assert response.status_code == 200
        assert response.data["value"] == 20

    def test_update_404_unknown(self, admin_client):
        response = admin_client.patch("/api/munin/v2/admin/entries/nonexistent.key/", {"value": 20}, format="json")
        assert response.status_code == 404

    def test_delete_204(self, admin_client):
        ConfigEntryFactory(key="faq.max_items")
        response = admin_client.delete("/api/munin/v2/admin/entries/faq.max_items/")
        assert response.status_code == 204

    def test_delete_404_unknown(self, admin_client):
        response = admin_client.delete("/api/munin/v2/admin/entries/nonexistent.key/")
        assert response.status_code == 404

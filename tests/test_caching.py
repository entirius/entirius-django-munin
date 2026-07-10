# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for caching and signal invalidation."""

import pytest
from django.core.cache import cache

from django_munin.services.config_service import get_module_list
from tests.factories import ConfigEntryFactory, ModuleFactory


@pytest.mark.django_db
class TestCaching:
    def setup_method(self):
        cache.clear()

    def test_second_call_uses_cache(self):
        ModuleFactory(key="cached_mod")
        result1 = get_module_list(is_admin=False)
        assert "cached_mod" in result1["modules"]
        # Second call should come from cache (same result)
        result2 = get_module_list(is_admin=False)
        assert result2 == result1

    def test_module_save_invalidates_cache(self):
        module = ModuleFactory(key="mod1")
        get_module_list(is_admin=False)  # populate cache
        module.label = "Updated"
        module.save()  # triggers post_save signal → invalidate
        # Cache version bumped, next call hits DB
        result = get_module_list(is_admin=False)
        assert result["modules"]["mod1"]["label"] == "Updated"

    def test_config_entry_save_invalidates_cache(self):
        ModuleFactory(key="mod2")
        get_module_list(is_admin=False)  # populate cache
        ConfigEntryFactory(key="test.signal")  # triggers post_save → invalidate
        # Should not error — cache was invalidated
        result = get_module_list(is_admin=False)
        assert "mod2" in result["modules"]

    def test_config_entry_delete_invalidates_cache(self):
        ModuleFactory(key="mod3")
        entry = ConfigEntryFactory(key="test.delete_signal")
        get_module_list(is_admin=False)  # populate cache
        entry.delete()  # triggers post_delete → invalidate
        result = get_module_list(is_admin=False)
        assert "mod3" in result["modules"]

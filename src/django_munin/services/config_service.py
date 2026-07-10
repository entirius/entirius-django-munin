# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Config service — aggregates module and config entry data for the API."""

from django.core.cache import cache

from django_munin.models import ConfigEntry, Module
from django_munin.settings import MUNIN_CACHE_TTL

CACHE_VERSION_KEY = "munin:cache_version"
CACHE_KEY_PREFIX = "munin"


def _cache_version() -> int:
    version = cache.get(CACHE_VERSION_KEY)
    if version is None:
        version = 1
        cache.set(CACHE_VERSION_KEY, version, timeout=None)
    return version


def _make_cache_key(suffix: str) -> str:
    return f"{CACHE_KEY_PREFIX}:v{_cache_version()}:{suffix}"


def invalidate_munin_cache(**kwargs) -> None:
    """Bump cache version — called by post_save/post_delete signals."""
    current = cache.get(CACHE_VERSION_KEY, 0)
    cache.set(CACHE_VERSION_KEY, current + 1, timeout=None)


def get_platform_info() -> dict:
    return {"version": "2.0.0"}


def _module_to_public_dict(module: Module) -> dict:
    return {
        "label": module.label,
        "version": module.version,
        "has_models": module.has_models,
        "has_api": module.has_api,
        "has_admin_api": module.has_admin_api,
        "has_admin": module.has_admin,
        "has_management_commands": module.has_management_commands,
        "has_urls": module.has_urls,
        "has_channels": module.has_channels,
        "has_translations": module.has_translations,
        "has_fixtures": module.has_fixtures,
        "config": module.config,
    }


def _module_to_admin_dict(module: Module) -> dict:
    data = _module_to_public_dict(module)
    data.update(
        {
            "app_label": module.app_label,
            "is_active": module.is_active,
            "enabled_in_cms": module.enabled_in_cms,
            "display_order": module.display_order,
            "created_at": module.created_at.isoformat() if module.created_at else None,
            "modified_at": module.modified_at.isoformat() if module.modified_at else None,
        }
    )
    return data


def get_module_list(is_admin: bool = False) -> dict:
    """Return aggregated module list in R5 format."""
    cache_key = _make_cache_key(f"list:{'admin' if is_admin else 'public'}")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    modules = Module.objects.filter(is_active=True)
    converter = _module_to_admin_dict if is_admin else _module_to_public_dict
    result = {"platform": get_platform_info(), "modules": {m.key: converter(m) for m in modules}}

    cache.set(cache_key, result, timeout=MUNIN_CACHE_TTL)
    return result


def get_module_detail(key: str, is_admin: bool = False) -> dict:
    """Return single module data, raises ObjectDoesNotExist if not found/inactive."""
    cache_key = _make_cache_key(f"detail:{key}:{'admin' if is_admin else 'public'}")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    module = Module.objects.get(key=key, is_active=True)
    converter = _module_to_admin_dict if is_admin else _module_to_public_dict
    result = converter(module)

    cache.set(cache_key, result, timeout=MUNIN_CACHE_TTL)
    return result


# --- ConfigEntry CRUD ---


def list_config_entries():
    return ConfigEntry.objects.all()


def create_config_entry(key: str, value, is_public: bool = False, description: str = "") -> ConfigEntry:
    return ConfigEntry.objects.create(key=key, value=value, is_public=is_public, description=description)


def update_config_entry(key: str, **updates) -> ConfigEntry:
    entry = ConfigEntry.objects.get(key=key)
    for field_name, val in updates.items():
        setattr(entry, field_name, val)
    entry.save()
    return entry


def delete_config_entry(key: str) -> None:
    entry = ConfigEntry.objects.get(key=key)
    entry.delete()


def get_config_value(key: str, default=None):
    """Read interface for other modules — returns value or default."""
    try:
        entry = ConfigEntry.objects.get(key=key)
        return entry.value
    except ConfigEntry.DoesNotExist:
        return default


def get_public_config() -> dict:
    """Return all public config entries as a flat dict."""
    return {e.key: e.value for e in ConfigEntry.objects.filter(is_public=True)}

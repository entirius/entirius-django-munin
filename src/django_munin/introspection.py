# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Module structure introspection — pure functions that detect capabilities from AppConfig."""

import importlib
import importlib.metadata
import pkgutil
from pathlib import Path

from django.apps import AppConfig
from django.contrib import admin
from django.db import models


def detect_has_models(app: AppConfig) -> bool:
    return len(list(app.get_models())) > 0


def detect_has_api(app: AppConfig) -> bool:
    try:
        urls_module = importlib.import_module(f"{app.name}.urls")
        return bool(getattr(urls_module, "urlpatterns", []))
    except (ImportError, Exception):
        return False


def detect_has_admin_api(app: AppConfig) -> bool:
    for suffix in ("api.v2.urls", "api.admin.urls"):
        try:
            urls_module = importlib.import_module(f"{app.name}.{suffix}")
            if getattr(urls_module, "urlpatterns", []):
                return True
        except (ImportError, Exception):
            continue
    return False


def detect_has_admin(app: AppConfig) -> bool:
    try:
        importlib.import_module(f"{app.name}.admin")
    except (ImportError, Exception):
        return False
    return any(model._meta.app_label == app.label for model in admin.site._registry)


def detect_has_management_commands(app: AppConfig) -> bool:
    try:
        commands_pkg = importlib.import_module(f"{app.name}.management.commands")
        return any(True for _ in pkgutil.iter_modules(commands_pkg.__path__))
    except (ImportError, Exception):
        return False


def detect_has_channels(app: AppConfig) -> bool:
    for model in app.get_models():
        has_idx = False
        has_language_rel = False
        for field in model._meta.get_fields():
            if isinstance(field, models.CharField) and field.name == "idx":
                has_idx = True
            if field.name in ("languages", "default_language"):
                has_language_rel = True
        if has_idx and has_language_rel:
            return True
    return False


def detect_has_translations(app: AppConfig) -> bool:
    for model in app.get_models():
        # Check for _t9n JSONField (PIM pattern)
        for field in model._meta.get_fields():
            if isinstance(field, models.JSONField) and field.name.endswith("_t9n"):
                return True
        # Check for T9N model pattern (separate model with FK to parent + FK to Language)
        model_name = model.__name__
        if model_name.upper().endswith("T9N") or model_name.endswith("T9n"):
            fk_fields = [f for f in model._meta.get_fields() if isinstance(f, models.ForeignKey)]
            has_parent_fk = any(f.related_model._meta.app_label == app.label for f in fk_fields if f.related_model)
            has_language_fk = any(f.related_model and f.related_model.__name__ == "Language" for f in fk_fields)
            if has_parent_fk and has_language_fk:
                return True
    return False


def detect_has_fixtures(app: AppConfig) -> bool:
    fixtures_dir = Path(app.path) / "fixtures"
    if not fixtures_dir.is_dir():
        return False
    return any(fixtures_dir.glob("*.yaml")) or any(fixtures_dir.glob("*.json"))


def detect_version(app: AppConfig) -> str:
    # Try module __version__ attribute
    try:
        mod = importlib.import_module(app.name)
        version = getattr(mod, "__version__", None)
        if version:
            return str(version)
    except (ImportError, Exception):
        pass
    # Try importlib.metadata
    package_name = app.name.replace("_", "-")
    try:
        # version() returns None when dist-info METADATA has no Version field
        version = importlib.metadata.version(package_name)
        if version:
            return version
    except importlib.metadata.PackageNotFoundError:
        pass
    return ""


def introspect_module(app: AppConfig) -> dict:
    """Run all detectors on an AppConfig, return a dict of capabilities."""
    return {
        "label": getattr(app, "verbose_name", app.label),
        "version": detect_version(app),
        "has_models": detect_has_models(app),
        "has_api": detect_has_api(app),
        "has_admin_api": detect_has_admin_api(app),
        "has_admin": detect_has_admin(app),
        "has_management_commands": detect_has_management_commands(app),
        "has_urls": detect_has_api(app),
        "has_channels": detect_has_channels(app),
        "has_translations": detect_has_translations(app),
        "has_fixtures": detect_has_fixtures(app),
    }

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django_utils.models.base_model import BaseModel


class Module(BaseModel):
    # Identity (set once on create)
    app_label = models.CharField(max_length=128, unique=True)
    key = models.CharField(max_length=64, unique=True)

    # Auto-detected (overwritten on every discover_modules run)
    label = models.CharField(max_length=128)
    version = models.CharField(max_length=32, blank=True, default="")
    has_models = models.BooleanField(default=False)
    has_api = models.BooleanField(default=False)
    has_admin_api = models.BooleanField(default=False)
    has_admin = models.BooleanField(default=False)
    has_management_commands = models.BooleanField(default=False)
    has_urls = models.BooleanField(default=False)
    has_channels = models.BooleanField(default=False)
    has_translations = models.BooleanField(default=False)
    has_fixtures = models.BooleanField(default=False)

    # State (managed by discover_modules)
    is_active = models.BooleanField(default=True)

    # Admin-controlled (preserved across re-scans)
    enabled_in_cms = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict)

    class Meta:
        ordering = ["display_order", "key"]
        db_table = "munin_module"

    def __str__(self) -> str:
        return f"{self.key} ({self.label})"

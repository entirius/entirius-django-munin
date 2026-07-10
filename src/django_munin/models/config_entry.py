# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.db import models
from django_utils.models.base_model import BaseModel


class ConfigEntry(BaseModel):
    key = models.CharField(max_length=128, unique=True)
    value = models.JSONField()
    is_public = models.BooleanField(default=False)
    description = models.CharField(max_length=256, blank=True, default="")

    class Meta:
        ordering = ["key"]
        db_table = "munin_config_entry"
        verbose_name_plural = "config entries"

    def __str__(self) -> str:
        return self.key

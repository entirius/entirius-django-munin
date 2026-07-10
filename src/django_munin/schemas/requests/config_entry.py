# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Pydantic request schemas for ConfigEntry CRUD."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ConfigEntryCreateRequest(BaseModel):
    key: str = Field(
        description="Config key (dotted notation)", examples=["faq.max_items_per_page"], min_length=1, max_length=128
    )
    value: Any = Field(description="Config value (any JSON type)", examples=[10])
    is_public: bool = Field(
        default=False, description="Whether this entry is visible to unauthenticated users", examples=[False]
    )
    description: str = Field(
        default="", description="Human-readable description", examples=["Maximum items per FAQ page"], max_length=256
    )

    @field_validator("key")
    @classmethod
    def validate_key_format(cls, v: str) -> str:
        import re

        if not re.match(r"^[a-z][a-z0-9_.]*[a-z0-9]$", v):
            raise ValueError("Key must be lowercase alphanumeric with dots/underscores, no leading/trailing dots")
        return v


class ConfigEntryUpdateRequest(BaseModel):
    value: Any | None = Field(default=None, description="Config value", examples=[20])
    is_public: bool | None = Field(default=None, description="Whether this entry is public", examples=[True])
    description: str | None = Field(
        default=None, description="Description", examples=["Updated description"], max_length=256
    )

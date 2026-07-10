# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Pydantic response schemas for ConfigEntry."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConfigEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str = Field(description="Config key", examples=["faq.max_items_per_page"])
    value: Any = Field(description="Config value", examples=[10])
    is_public: bool = Field(description="Whether visible to unauthenticated users", examples=[False])
    description: str = Field(description="Human-readable description", examples=["Maximum items per FAQ page"])
    created_at: datetime = Field(description="Creation timestamp", examples=["2024-01-01T00:00:00Z"])
    modified_at: datetime = Field(description="Last update timestamp", examples=["2024-01-01T00:00:00Z"])


class ConfigEntryListResponse(BaseModel):
    count: int = Field(description="Total number of entries", examples=[5])
    next: str | None = Field(None, description="URL of next page", examples=[None])
    previous: str | None = Field(None, description="URL of previous page", examples=[None])
    results: list[ConfigEntryResponse] = Field(description="List of config entries")

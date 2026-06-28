"""Request/response models for GovFlags (data model: section 5 of the BRD)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

KEY_PATTERN = r"^[a-z0-9-]+$"


class Flag(BaseModel):
    """A feature flag: ``Flag { key, enabled, rollout_percent }``."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(pattern=KEY_PATTERN)
    enabled: bool = False
    rollout_percent: int = Field(default=0, ge=0, le=100)


class FlagUpdate(BaseModel):
    """Partial update for PATCH /flags/{key} (FR-4)."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool | None = None
    rollout_percent: int | None = Field(default=None, ge=0, le=100)


class Evaluation(BaseModel):
    """Result of GET /flags/{key}/evaluate (FR-5)."""

    key: str
    user_id: str
    on: bool

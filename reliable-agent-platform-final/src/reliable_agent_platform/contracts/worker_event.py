"""WorkerEvent model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from reliable_agent_platform.contracts.enums import EventType, SchemaVersion


class WorkerEvent(BaseModel):
    """Normalized worker event - rejects unknown fields and invalid versions."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion.V1_0
    run_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    timestamp: datetime  # Must be timezone-aware (validated by JSON Schema format: date-time)
    event_type: EventType
    attempt: int = Field(ge=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    artifact_refs: list[str] = Field(default_factory=list)

    @field_validator("timestamp")
    @classmethod
    def _timestamp_must_be_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("timestamp must be timezone-aware")
        return v

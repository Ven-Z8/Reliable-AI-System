"""TraceEvent model."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from reliable_agent_platform.contracts.enums import SchemaVersion, TraceStatus


class TraceEvent(BaseModel):
    """OpenTelemetry-compatible trace event."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion.V1_0
    trace_id: str = Field(min_length=1)
    span_id: str = Field(min_length=1)
    parent_span_id: str | None = None
    run_id: str = Field(min_length=1)
    project: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    agent_name: str | None = None
    worker_name: str | None = None
    model_name: str | None = None
    tool_name: str | None = None
    state_before: str | None = None
    state_after: str | None = None
    retry_number: int = Field(ge=0)
    started_at: datetime  # timezone-aware
    duration_ms: int = Field(ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    status: TraceStatus
    error_type: str | None = None
    policy_decision: str | None = None
    artifact_refs: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("schema_version")
    @classmethod
    def _schema_version_supported(cls, v: SchemaVersion) -> SchemaVersion:
        # Only V1_0 is supported; enum enforces this
        return v

    @field_validator("started_at")
    @classmethod
    def _started_at_must_be_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("started_at must be timezone-aware")
        return v

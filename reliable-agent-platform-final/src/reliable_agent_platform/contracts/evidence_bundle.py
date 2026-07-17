"""EvidenceBundle, Artifact, and Claim models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from reliable_agent_platform.contracts.enums import SchemaVersion


class Artifact(BaseModel):
    """Evidence artifact with SHA256 hash."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    artifact_type: str = Field(min_length=1)
    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    metadata: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseModel):
    """Verifiable claim referencing artifacts."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    artifact_ids: list[str] = Field(default_factory=list)
    verified: bool
    verifier: str | None = None


class EvidenceBundle(BaseModel):
    """Evidence bundle for a run - all fields required, rejects unknown."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion.V1_0
    run_id: str = Field(min_length=1)
    created_at: datetime  # timezone-aware
    artifacts: list[Artifact] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)

    @field_validator("schema_version")
    @classmethod
    def _schema_version_supported(cls, v: SchemaVersion) -> SchemaVersion:
        # Only V1_0 is supported; enum enforces this
        return v

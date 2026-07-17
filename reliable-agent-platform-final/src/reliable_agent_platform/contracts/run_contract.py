"""RunContract and nested models."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from reliable_agent_platform.contracts.enums import ApprovalPolicy, SchemaVersion


class Repository(BaseModel):
    """Repository specification."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    clean_required: bool


class Budgets(BaseModel):
    """Execution budgets - all non-negative with minimums."""

    model_config = ConfigDict(extra="forbid")

    max_attempts: int = Field(ge=1)
    timeout_seconds: int = Field(ge=1)
    max_changed_files: int = Field(ge=0)
    max_cost_usd: float | None = Field(default=None, ge=0)
    max_input_tokens: int | None = Field(default=None, ge=0)
    max_output_tokens: int | None = Field(default=None, ge=0)


class RunContract(BaseModel):
    """Versioned run contract - rejects unknown fields and unsupported versions."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion.V1_0
    task_id: str = Field(min_length=1)
    task: str = Field(min_length=1)
    goal_id: str | None = None
    repository: Repository
    worker: str = Field(min_length=1)
    allowed_paths: list[str] = Field(default_factory=list)
    denied_paths: list[str] = Field(default_factory=list)
    allowed_commands: list[str] | None = None
    denied_commands: list[str] | None = None
    required_checks: list[str] = Field(default_factory=list)
    budgets: Budgets
    approval_policy: ApprovalPolicy
    metadata: dict[str, Any] = Field(default_factory=dict)

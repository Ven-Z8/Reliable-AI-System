"""EvaluationResult model."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from reliable_agent_platform.contracts.enums import SchemaVersion, TerminalState


class EvaluationResult(BaseModel):
    """Evaluation result - worker-reported success is NOT final completion."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion.V1_0
    task_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    worker: str = Field(min_length=1)
    commit_sha: str | None = None
    terminal_state: TerminalState
    task_completed: bool
    tests_passed: bool
    evidence_valid: bool
    policy_valid: bool
    attempts: int = Field(ge=0)
    changed_files: int = Field(ge=0)
    denied_files_touched: list[str] = Field(default_factory=list)
    duration_ms: int = Field(ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    failure_category: str | None = None
    artifact_refs: list[str] = Field(default_factory=list)
    scores: dict[str, float] = Field(default_factory=dict)

    @field_validator("schema_version")
    @classmethod
    def _schema_version_supported(cls, v: SchemaVersion) -> SchemaVersion:
        # Only V1_0 is supported; enum enforces this
        return v

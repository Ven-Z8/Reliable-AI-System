"""Closed enums for contracts - must reject unknown values."""

from enum import StrEnum


class SchemaVersion(StrEnum):
    """Supported contract schema versions - only 1.0 currently."""

    V1_0 = "1.0"


class EventType(StrEnum):
    """Worker event types - closed enum."""

    WORKER_STARTED = "worker_started"
    MODEL_REQUEST = "model_request"
    MODEL_RESPONSE = "model_response"
    TOOL_REQUESTED = "tool_requested"
    TOOL_AUTHORIZED = "tool_authorized"
    TOOL_COMPLETED = "tool_completed"
    FILE_CHANGED = "file_changed"
    CHECKPOINT = "checkpoint"
    RETRY = "retry"
    WARNING = "warning"
    WORKER_FAILED = "worker_failed"
    WORKER_COMPLETED = "worker_completed"


class ApprovalPolicy(StrEnum):
    """Approval policy for irreversible actions."""

    AUTO = "auto"
    ASK = "ask"
    DENY = "deny"


class TerminalState(StrEnum):
    """Terminal states for a run - worker success is NOT a terminal state."""

    COMPLETED = "completed"
    AWAITING_HUMAN = "awaiting_human"
    REJECTED = "rejected"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    VALIDATION_FAILED = "validation_failed"
    WORKER_FAILED = "worker_failed"
    NO_PROGRESS = "no_progress"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TIMEOUT = "timeout"
    SYSTEM_ERROR = "system_error"


class TraceStatus(StrEnum):
    """Trace span status."""

    OK = "ok"
    ERROR = "error"
    UNSET = "unset"

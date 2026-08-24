"""Worker adapter protocol and types."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from reliable_agent_platform.contracts import RunContract, WorkerEvent
from reliable_agent_platform.worker_adapters.capabilities import WorkerCapabilities


@dataclass
class WorkerRequest:
    """Request to run a worker."""

    run_id: str
    task: str
    workspace_path: str
    contract: RunContract
    clock: Callable[[], float] | None = None
    id_source: Callable[[], str] | None = None


@dataclass
class WorkerResult:
    """Worker result - success is worker's REPORT only, not verified completion."""

    success: bool
    terminal_state: str | None = None  # From TerminalState enum, or None
    events: list[WorkerEvent] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    failure_category: str | None = None


class WorkerEventSink(Protocol):
    """Sink for worker events."""

    async def emit(self, event: WorkerEvent) -> None: ...


class WorkerAdapter(Protocol):
    """Worker adapter protocol - framework-neutral."""

    def capabilities(self) -> WorkerCapabilities: ...

    async def run(self, request: WorkerRequest, emit: WorkerEventSink) -> WorkerResult: ...

    async def cancel(self, run_id: str) -> None: ...


# Re-export WorkerCapabilities for convenience
__all__ = [
    "WorkerAdapter",
    "WorkerCapabilities",
    "WorkerEventSink",
    "WorkerRequest",
    "WorkerResult",
]

"""Deterministic MockWorker implementation."""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path

from reliable_agent_platform.contracts import (
    EventType,
    SchemaVersion,
    TerminalState,
    WorkerEvent,
)
from reliable_agent_platform.worker_adapters.protocol import (
    WorkerAdapter,
    WorkerCapabilities,
    WorkerEventSink,
    WorkerRequest,
    WorkerResult,
)


class MockWorker(WorkerAdapter):
    """Deterministic mock worker for testing.

    Supports scenarios:
    - success: emits full event sequence, writes file
    - worker_failure: emits WORKER_FAILED
    - timeout: simulates timeout
    - cancelled: handles cancellation
    - reported_success_without_evidence: claims success but no evidence events
    - repeated_equivalent_action: emits duplicate events for same action

    Features:
    - Injectable clock and ID source for deterministic testing
    - Path traversal prevention (.. blocked)
    - Symlink escape prevention
    - Writes only inside workspace_path
    """

    def __init__(
        self,
        scenario: str = "success",
        clock: Callable[[], float] | None = None,
        id_source: Callable[[], str] | None = None,
        configured_changes: dict[str, str] | None = None,
    ):
        self._scenario = scenario
        self._clock = clock or (lambda: 0.0)
        self._id_source = id_source or (lambda: "default-id")
        self._configured_changes = configured_changes or {}
        self._cancelled_runs: set[str] = set()

    def capabilities(self) -> WorkerCapabilities:
        """Return all capabilities as True for testing."""
        return WorkerCapabilities(
            filesystem=True,
            shell_command=True,
            streaming=True,
            cancellation=True,
            checkpoints=True,
            context_compaction=True,
            sub_agents=True,
            mcp=True,
            human_approval=True,
            sandbox=True,
            cost_reporting=True,
            token_reporting=True,
        )

    async def run(
        self,
        request: WorkerRequest,
        emit: WorkerEventSink,
    ) -> WorkerResult:
        """Execute the scenario, emitting events."""
        # Check cancellation before start
        if request.run_id in self._cancelled_runs:
            return WorkerResult(
                success=False,
                failure_category="cancelled",
            )

        events: list[WorkerEvent] = []
        changed_files: list[str] = []

        # Helper to emit events
        async def emit_event(
            event_type: EventType, payload: dict[str, object] | None = None
        ) -> None:
            # Clock returns float timestamp, convert to datetime
            ts = self._clock() if callable(self._clock) else 0.0
            event = WorkerEvent(
                schema_version=SchemaVersion.V1_0,
                run_id=request.run_id,
                event_id=self._id_source(),
                timestamp=datetime.fromtimestamp(ts, tz=UTC),
                event_type=event_type,
                attempt=1,
                payload=payload or {},
            )
            events.append(event)
            await emit.emit(event)

        # Dispatch scenario
        if self._scenario == "success":
            await self._run_success(request, emit_event, changed_files)
            return WorkerResult(
                success=True,
                terminal_state=None,
                events=events,
                changed_files=changed_files,
                artifact_refs=[],
                failure_category=None,
            )
        elif self._scenario == "worker_failure":
            await self._run_worker_failure(emit_event)
            return WorkerResult(
                success=False,
                terminal_state=TerminalState.WORKER_FAILED.value,
                events=events,
                changed_files=[],
                artifact_refs=[],
                failure_category="worker_error",
            )
        elif self._scenario == "timeout":
            await self._run_timeout(emit_event)
            return WorkerResult(
                success=False,
                terminal_state=TerminalState.TIMEOUT.value,
                events=events,
                changed_files=[],
                artifact_refs=[],
                failure_category="timeout",
            )
        elif self._scenario == "cancelled":
            await self._run_cancelled(emit_event)
            return WorkerResult(
                success=False,
                terminal_state=TerminalState.WORKER_FAILED.value,
                events=events,
                changed_files=[],
                artifact_refs=[],
                failure_category="cancelled",
            )
        elif self._scenario == "reported_success_without_evidence":
            await self._run_reported_success_without_evidence(emit_event)
            return WorkerResult(
                success=True,
                terminal_state=None,
                events=events,
                changed_files=[],
                artifact_refs=[],
                failure_category=None,
            )
        elif self._scenario == "repeated_equivalent_action":
            await self._run_repeated_equivalent_action(request, emit_event, changed_files)
            return WorkerResult(
                success=True,
                terminal_state=None,
                events=events,
                changed_files=changed_files,
                artifact_refs=[],
                failure_category=None,
            )
        else:
            # Default to success
            await self._run_success(request, emit_event, changed_files)
            return WorkerResult(
                success=True,
                terminal_state=None,
                events=events,
                changed_files=changed_files,
                artifact_refs=[],
                failure_category=None,
            )

    async def cancel(self, run_id: str) -> None:
        """Request cooperative cancellation."""
        self._cancelled_runs.add(run_id)

    async def _run_success(
        self,
        request: WorkerRequest,
        emit_event: Callable[[EventType, dict[str, object] | None], object],
        changed_files: list[str],
    ) -> None:
        """Success scenario: full event sequence + file write."""
        await emit_event(EventType.WORKER_STARTED, {"worker": "mock", "scenario": "success"})
        await emit_event(EventType.TOOL_REQUESTED, {"tool": "write_file", "path": "test.txt"})
        await emit_event(EventType.TOOL_AUTHORIZED, {"tool": "write_file"})
        await emit_event(EventType.TOOL_COMPLETED, {"tool": "write_file", "success": True})

        # Write configured files (with path validation)
        for path, content in self._configured_changes.items():
            if self._write_file_safely(request.workspace_path, path, content):
                changed_files.append(path)
                await emit_event(EventType.FILE_CHANGED, {"path": path})

        await emit_event(EventType.CHECKPOINT, {"step": "files_written"})
        await emit_event(EventType.WORKER_COMPLETED, {"success": True})

    async def _run_worker_failure(
        self, emit_event: Callable[[EventType, dict[str, object] | None], object]
    ) -> None:
        """Worker failure scenario."""
        await emit_event(EventType.WORKER_STARTED, {"worker": "mock", "scenario": "worker_failure"})
        await emit_event(EventType.WORKER_FAILED, {"error": "simulated failure"})

    async def _run_timeout(
        self, emit_event: Callable[[EventType, dict[str, object] | None], object]
    ) -> None:
        """Timeout scenario."""
        await emit_event(EventType.WORKER_STARTED, {"worker": "mock", "scenario": "timeout"})
        await emit_event(EventType.WARNING, {"message": "timeout approaching"})
        await emit_event(EventType.WORKER_FAILED, {"error": "timeout"})

    async def _run_cancelled(
        self, emit_event: Callable[[EventType, dict[str, object] | None], object]
    ) -> None:
        """Cancelled scenario."""
        await emit_event(EventType.WORKER_STARTED, {"worker": "mock", "scenario": "cancelled"})
        await emit_event(EventType.WARNING, {"message": "cancelled by control plane"})
        await emit_event(EventType.WORKER_FAILED, {"error": "cancelled"})

    async def _run_reported_success_without_evidence(
        self, emit_event: Callable[[EventType, dict[str, object] | None], object]
    ) -> None:
        """Worker claims success but produces no evidence events."""
        await emit_event(
            EventType.WORKER_STARTED,
            {"worker": "mock", "scenario": "reported_success_without_evidence"},
        )
        await emit_event(EventType.TOOL_REQUESTED, {"tool": "noop"})
        await emit_event(EventType.TOOL_AUTHORIZED, {"tool": "noop"})
        await emit_event(EventType.TOOL_COMPLETED, {"tool": "noop", "success": True})
        await emit_event(EventType.WORKER_COMPLETED, {"success": True})

    async def _run_repeated_equivalent_action(
        self,
        request: WorkerRequest,
        emit_event: Callable[[EventType, dict[str, object] | None], object],
        changed_files: list[str],
    ) -> None:
        """Repeated equivalent action - duplicate tool requests and file writes."""
        await emit_event(
            EventType.WORKER_STARTED, {"worker": "mock", "scenario": "repeated_equivalent_action"}
        )

        # First attempt
        await emit_event(EventType.TOOL_REQUESTED, {"tool": "write_file", "path": "test.txt"})
        await emit_event(EventType.TOOL_AUTHORIZED, {"tool": "write_file"})
        await emit_event(EventType.TOOL_COMPLETED, {"tool": "write_file", "success": True})

        if self._write_file_safely(request.workspace_path, "test.txt", "v1"):
            changed_files.append("test.txt")
            await emit_event(EventType.FILE_CHANGED, {"path": "test.txt"})

        # Second equivalent attempt (simulates retry or loop)
        await emit_event(EventType.TOOL_REQUESTED, {"tool": "write_file", "path": "test.txt"})
        await emit_event(EventType.TOOL_AUTHORIZED, {"tool": "write_file"})
        await emit_event(EventType.TOOL_COMPLETED, {"tool": "write_file", "success": True})

        if self._write_file_safely(request.workspace_path, "test.txt", "v2"):
            changed_files.append("test.txt")
            await emit_event(EventType.FILE_CHANGED, {"path": "test.txt"})

        await emit_event(EventType.CHECKPOINT, {"step": "files_written"})
        await emit_event(EventType.WORKER_COMPLETED, {"success": True})

    def _write_file_safely(self, workspace_path: str, relative_path: str, content: str) -> bool:
        """Write file only if it stays inside workspace (prevents traversal/symlink escape)."""
        workspace = Path(workspace_path).resolve()
        target = (workspace / relative_path).resolve()

        # Check if target is inside workspace (prevents .. traversal)
        try:
            target.relative_to(workspace)
        except ValueError:
            return False  # Path traversal attempt

        # Check for symlink escape - resolve and ensure still inside workspace
        real_target = target.resolve()
        try:
            real_target.relative_to(workspace)
        except ValueError:
            return False  # Symlink escape attempt

        # Safe to write
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return True
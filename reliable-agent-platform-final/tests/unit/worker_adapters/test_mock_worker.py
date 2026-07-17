"""Tests for MockWorker - TDD RED phase."""

import os
import tempfile
from pathlib import Path

import pytest

from reliable_agent_platform.contracts import (
    ApprovalPolicy,
    Budgets,
    EventType,
    Repository,
    RunContract,
    SchemaVersion,
    TerminalState,
    WorkerEvent,
)
from reliable_agent_platform.worker_adapters import (
    MockWorker,
    WorkerEventSink,
    WorkerRequest,
)


class TestMockWorker:
    """Test deterministic MockWorker."""

    def create_request(
        self, workspace_path: str, run_id: str = "run-1", task: str = "Test task"
    ) -> WorkerRequest:
        """Create a test WorkerRequest with minimal contract."""
        contract = RunContract(
            schema_version=SchemaVersion.V1_0,
            task_id="task-1",
            task="Test task",
            repository=Repository(path=".", revision="main", clean_required=True),
            worker="mock",
            allowed_paths=["**"],
            denied_paths=[],
            required_checks=[],
            budgets=Budgets(max_attempts=1, timeout_seconds=300, max_changed_files=20),
            approval_policy=ApprovalPolicy.ASK,
        )
        return WorkerRequest(
            run_id=run_id,
            task=task,
            workspace_path=workspace_path,
            contract=contract,
        )

    async def test_success_scenario_emits_expected_event_order(self):
        """Success scenario emits events in expected order."""
        worker = MockWorker(
            scenario="success",
            clock=lambda: 1000.0,
            id_source=lambda: "event-1",
            configured_changes={"test.txt": "hello"},
        )

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

            assert result.success is True
            assert len(events) == 7
            assert events[0].event_type == EventType.WORKER_STARTED
            assert events[1].event_type == EventType.TOOL_REQUESTED
            assert events[2].event_type == EventType.TOOL_AUTHORIZED
            assert events[3].event_type == EventType.TOOL_COMPLETED
            assert events[4].event_type == EventType.FILE_CHANGED
            assert events[5].event_type == EventType.CHECKPOINT
            assert events[6].event_type == EventType.WORKER_COMPLETED

            # File should be written (check inside the context manager)
            test_file = Path(tmpdir) / "test.txt"
            assert test_file.exists()
            assert test_file.read_text() == "hello"

    async def test_worker_failure_scenario(self):
        """Worker failure scenario emits WORKER_FAILED."""
        worker = MockWorker(scenario="worker_failure")

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        assert result.success is False
        assert result.terminal_state == TerminalState.WORKER_FAILED.value
        assert result.failure_category == "worker_error"
        assert any(e.event_type == EventType.WORKER_FAILED for e in events)

    async def test_timeout_scenario(self):
        """Timeout scenario."""
        worker = MockWorker(scenario="timeout")

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        assert result.success is False
        assert result.terminal_state == TerminalState.TIMEOUT.value
        assert result.failure_category == "timeout"
        assert any(e.event_type == EventType.WARNING for e in events)

    async def test_cancelled_scenario(self):
        """Cancelled scenario."""
        worker = MockWorker(scenario="cancelled")

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        assert result.success is False
        assert result.failure_category == "cancelled"
        assert any(e.event_type == EventType.WARNING for e in events)

    async def test_reported_success_without_evidence(self):
        """Reported success without evidence - no FILE_CHANGED, no CHECKPOINT."""
        worker = MockWorker(
            scenario="reported_success_without_evidence",
            clock=lambda: 1000.0,
            id_source=lambda: "event-1",
        )

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        assert result.success is True
        assert result.terminal_state is None  # Worker doesn't decide
        # Should NOT have FILE_CHANGED or CHECKPOINT
        event_types = [e.event_type for e in events]
        assert EventType.FILE_CHANGED not in event_types
        assert EventType.CHECKPOINT not in event_types
        # But should have tool events
        assert EventType.TOOL_REQUESTED in event_types
        assert EventType.TOOL_AUTHORIZED in event_types
        assert EventType.TOOL_COMPLETED in event_types
        assert EventType.WORKER_COMPLETED in event_types

    async def test_repeated_equivalent_action(self):
        """Repeated equivalent action emits duplicate events."""
        worker = MockWorker(
            scenario="repeated_equivalent_action",
            clock=lambda: 1000.0,
            id_source=lambda: "event-1",
            configured_changes={"test.txt": "v1"},
        )

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        assert result.success is True
        # Should have duplicate TOOL_REQUESTED and FILE_CHANGED
        tool_requested_count = sum(1 for e in events if e.event_type == EventType.TOOL_REQUESTED)
        file_changed_count = sum(1 for e in events if e.event_type == EventType.FILE_CHANGED)
        assert tool_requested_count == 2
        assert file_changed_count == 2

    async def test_path_traversal_blocked(self):
        """Path traversal (..) is blocked - no file written outside workspace."""
        worker = MockWorker(
            scenario="success",
            configured_changes={"../escape.txt": "malicious"},
        )

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        # File should NOT be written outside workspace
        escape_file = Path(tmpdir).parent / "escape.txt"
        assert not escape_file.exists()
        # No FILE_CHANGED event for the escape attempt
        file_changed_events = [e for e in events if e.event_type == EventType.FILE_CHANGED]
        assert len(file_changed_events) == 0

    async def test_symlink_escape_blocked(self):
        """Symlink escape attempt is blocked."""
        import sys

        if sys.platform == "win32":
            pytest.skip(
                "Symlinks require elevated privileges on Windows; test resolution logic directly"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()
            outside_dir = Path(tmpdir) / "outside"
            outside_dir.mkdir()

            # Create symlink inside workspace pointing outside
            symlink = workspace / "link.txt"
            target = outside_dir / "target.txt"
            target.write_text("outside")
            os.symlink(target, symlink)

            worker = MockWorker(
                scenario="success",
                configured_changes={"link.txt": "attempted write through symlink"},
            )

            events = []

            class Sink(WorkerEventSink):
                async def emit(self, event: WorkerEvent):
                    events.append(event)

            request = self.create_request(str(workspace))
            result = await worker.run(request, Sink())

            # File should NOT be written to outside directory
            assert not target.exists() or target.read_text() == "outside"
            # No FILE_CHANGED event
            file_changed_events = [e for e in events if e.event_type == EventType.FILE_CHANGED]
            assert len(file_changed_events) == 0

    async def test_deterministic_output(self):
        """Same inputs produce identical event sequences."""
        worker1 = MockWorker(
            scenario="success",
            clock=lambda: 1000.0,
            id_source=lambda: "event-1",
            configured_changes={"test.txt": "hello"},
        )

        worker2 = MockWorker(
            scenario="success",
            clock=lambda: 1000.0,
            id_source=lambda: "event-1",
            configured_changes={"test.txt": "hello"},
        )

        events1 = []
        events2 = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events1.append(event)

        class Sink2(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events2.append(event)

        with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
            request1 = self.create_request(tmpdir1)
            request2 = self.create_request(tmpdir2)
            await worker1.run(request1, Sink())
            await worker2.run(request2, Sink2())

        assert len(events1) == len(events2)
        for e1, e2 in zip(events1, events2, strict=True):
            assert e1.event_type == e2.event_type
            assert e1.attempt == e2.attempt
            assert e1.payload == e2.payload

    async def test_cancellation_before_start(self):
        """Cancel before run prevents execution."""
        worker = MockWorker(scenario="success", configured_changes={"test.txt": "hello"})

        events = []

        class Sink(WorkerEventSink):
            async def emit(self, event: WorkerEvent):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            await worker.cancel(request.run_id)
            result = await worker.run(request, Sink())

        assert result.success is False
        assert result.failure_category == "cancelled"
        assert len(events) == 0

    async def test_capabilities_all_true(self):
        """MockWorker capabilities returns all True."""
        worker = MockWorker()
        caps = worker.capabilities()
        assert caps.filesystem is True
        assert caps.shell is True
        assert caps.streaming is True
        assert caps.cancellation is True
        assert caps.checkpoints is True
        assert caps.context_compaction is True
        assert caps.sub_agents is True
        assert caps.mcp is True
        assert caps.human_approval is True
        assert caps.sandbox is True
        assert caps.cost_reporting is True
        assert caps.token_reporting is True

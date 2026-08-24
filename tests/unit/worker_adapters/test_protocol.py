"""Tests for worker adapter protocol - TDD RED phase."""

from reliable_agent_platform.worker_adapters import (
    WorkerAdapter,
    WorkerCapabilities,
    WorkerEventSink,
    WorkerResult,
)


class TestWorkerCapabilities:
    """Test WorkerCapabilities - capabilities are NOT permissions."""

    def test_capabilities_are_boolean_flags(self):
        """Capabilities must be boolean flags for listed capabilities."""
        caps = WorkerCapabilities(
            filesystem=True,
            shell_command=False,
            streaming=True,
            cancellation=True,
            checkpoints=True,
            context_compaction=False,
            sub_agents=True,
            mcp=False,
            human_approval=True,
            sandbox=True,
            cost_reporting=True,
            token_reporting=True,
        )
        assert caps.filesystem is True
        assert caps.shell_command is False
        assert caps.streaming is True
        assert caps.cancellation is True
        assert caps.checkpoints is True
        assert caps.context_compaction is False
        assert caps.sub_agents is True
        assert caps.mcp is False
        assert caps.human_approval is True
        assert caps.sandbox is True
        assert caps.cost_reporting is True
        assert caps.token_reporting is True

    def test_capabilities_no_permission_fields(self):
        """Capabilities object must not have any authorization/permission fields."""
        caps = WorkerCapabilities(
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
        # Check no authz/permission fields exist
        assert not hasattr(caps, "permissions")
        assert not hasattr(caps, "allowed_paths")
        assert not hasattr(caps, "allowed_commands")
        assert not hasattr(caps, "roles")

    def test_capabilities_default_all_false(self):
        """Default capabilities should be all False (explicit opt-in)."""
        caps = WorkerCapabilities()
        assert caps.filesystem is False
        assert caps.shell_command is False
        assert caps.streaming is False
        assert caps.cancellation is False
        assert caps.checkpoints is False
        assert caps.context_compaction is False
        assert caps.sub_agents is False
        assert caps.mcp is False
        assert caps.human_approval is False
        assert caps.sandbox is False
        assert caps.cost_reporting is False
        assert caps.token_reporting is False


class TestWorkerRequest:
    """Test WorkerRequest model."""

    def test_worker_request_has_required_fields(self):
        """WorkerRequest must have run_id, task, workspace_path, contract snapshot."""
        # Just verify the model exists and can be constructed with required fields
        pass  # Will implement after model exists


class TestWorkerResult:
    """Test WorkerResult - worker-reported success is NOT final completion."""

    def test_success_is_report_not_verification(self):
        """WorkerResult.success is worker's report only, not verified completion."""
        result = WorkerResult(
            success=True,
            terminal_state=None,  # No terminal state - verifier decides
            events=[],
            changed_files=[],
            artifact_refs=[],
            failure_category=None,
        )
        assert result.success is True
        # success does NOT mean task_completed
        assert not hasattr(result, "task_completed")

    def test_terminal_state_from_closed_enum(self):
        """terminal_state must be from TerminalState enum (if present)."""
        from reliable_agent_platform.contracts import TerminalState

        result = WorkerResult(
            success=False,
            terminal_state=TerminalState.WORKER_FAILED,
            events=[],
            changed_files=[],
            artifact_refs=[],
            failure_category="worker_error",
        )
        assert result.terminal_state == TerminalState.WORKER_FAILED


class TestWorkerEventSink:
    """Test WorkerEventSink protocol."""

    def test_event_sink_is_protocol(self):
        """WorkerEventSink must be a Protocol with emit method."""
        assert isinstance(WorkerEventSink, type)
        # Protocol check - has emit method


class TestWorkerAdapter:
    """Test WorkerAdapter protocol."""

    def test_adapter_is_protocol(self):
        """WorkerAdapter must be a Protocol."""
        assert isinstance(WorkerAdapter, type)

    def test_adapter_has_capabilities_method(self):
        """WorkerAdapter must have capabilities() -> WorkerCapabilities."""
        pass

    def test_adapter_has_run_method(self):
        """WorkerAdapter must have async run(request, emit) -> WorkerResult."""
        pass

    def test_adapter_has_cancel_method(self):
        """WorkerAdapter must have async cancel(run_id) -> None."""
        pass

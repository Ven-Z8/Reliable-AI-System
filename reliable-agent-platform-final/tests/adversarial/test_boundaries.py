"""Adversarial tests for contract boundaries and worker boundaries - TDD RED first.

These tests prove forbidden behaviors are blocked.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from reliable_agent_platform.contracts import (
    ApprovalPolicy,
    EvaluationResult,
    EvidenceBundle,
    RunContract,
    SchemaVersion,
    TraceEvent,
    WorkerEvent,
)
from reliable_agent_platform.contracts.run_contract import Budgets, Repository
from reliable_agent_platform.worker_adapters import MockWorker, WorkerRequest


class TestAdversarialContractBoundaries:
    """Adversarial tests proving contract validation rejects forbidden inputs."""

    def test_unknown_field_rejected_run_contract(self):
        """Unknown top-level field on RunContract must be rejected."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["unknown_field"] = "not_allowed"
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "unknown_field" in str(exc.value)

    def test_unknown_field_rejected_worker_event(self):
        """Unknown field on WorkerEvent must be rejected."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["unknown_field"] = "not_allowed"
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "unknown_field" in str(exc.value)

    def test_unknown_field_rejected_evidence_bundle(self):
        """Unknown field on EvidenceBundle must be rejected."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        data["unknown_field"] = "not_allowed"
        with pytest.raises(ValidationError) as exc:
            EvidenceBundle.model_validate(data)
        assert "unknown_field" in str(exc.value)

    def test_unknown_field_rejected_evaluation_result(self):
        """Unknown field on EvaluationResult must be rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["unknown_field"] = "not_allowed"
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "unknown_field" in str(exc.value)

    def test_unknown_field_rejected_trace_event(self):
        """Unknown field on TraceEvent must be rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["unknown_field"] = "not_allowed"
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "unknown_field" in str(exc.value)

    def test_unsupported_schema_version_rejected(self):
        """Schema version other than 1.0 must be rejected on all contracts."""
        for model_class, example_file in [
            (RunContract, "examples/contracts/run-contract.json"),
            (WorkerEvent, "examples/contracts/worker-event.json"),
            (EvidenceBundle, "examples/contracts/evidence-bundle.json"),
            (EvaluationResult, "examples/contracts/evaluation-result.json"),
            (TraceEvent, "examples/contracts/trace-event.json"),
        ]:
            with open(example_file) as f:
                data = json.load(f)
            data["schema_version"] = "2.0"
            with pytest.raises(ValidationError) as exc:
                model_class.model_validate(data)
            assert "schema_version" in str(exc.value), f"{model_class.__name__} should reject unknown version"

    def test_invalid_event_type_rejected(self):
        """Invalid EventType must be rejected."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["event_type"] = "not_a_valid_event"
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "event_type" in str(exc.value)

    def test_invalid_terminal_state_rejected(self):
        """Invalid TerminalState must be rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["terminal_state"] = "not_a_state"
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "terminal_state" in str(exc.value)

    def test_invalid_approval_policy_rejected(self):
        """Invalid ApprovalPolicy must be rejected."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["approval_policy"] = "not_a_policy"
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "approval_policy" in str(exc.value)

    def test_invalid_trace_status_rejected(self):
        """Invalid TraceStatus must be rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["status"] = "not_a_status"
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "status" in str(exc.value)

    def test_naive_datetime_rejected_worker_event(self):
        """Naive datetime (no timezone) must be rejected on WorkerEvent.timestamp."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["timestamp"] = "2026-07-17T12:00:00"  # No timezone
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "timestamp" in str(exc.value)

    def test_naive_datetime_rejected_trace_event(self):
        """Naive datetime must be rejected on TraceEvent.started_at."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["started_at"] = "2026-07-17T12:00:00"  # No timezone
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "started_at" in str(exc.value)

    def test_negative_budgets_rejected(self):
        """Negative budget values must be rejected."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["budgets"]["max_attempts"] = -1
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "max_attempts" in str(exc.value)

        data["budgets"]["max_attempts"] = 1
        data["budgets"]["timeout_seconds"] = -10
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "timeout_seconds" in str(exc.value)

        data["budgets"]["timeout_seconds"] = 300
        data["budgets"]["max_changed_files"] = -5
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "max_changed_files" in str(exc.value)

        data["budgets"]["max_changed_files"] = 20
        data["budgets"]["max_cost_usd"] = -0.01
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "max_cost_usd" in str(exc.value)

    def test_negative_metrics_rejected_evaluation_result(self):
        """Negative metrics must be rejected on EvaluationResult."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["attempts"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "attempts" in str(exc.value)

        data["attempts"] = 1
        data["changed_files"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "changed_files" in str(exc.value)

        data["changed_files"] = 0
        data["duration_ms"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "duration_ms" in str(exc.value)

    def test_negative_tokens_cost_rejected(self):
        """Negative tokens and cost must be rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["input_tokens"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "input_tokens" in str(exc.value)

        data["input_tokens"] = 100
        data["output_tokens"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "output_tokens" in str(exc.value)

        data["output_tokens"] = 100
        data["estimated_cost_usd"] = -0.01
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "estimated_cost_usd" in str(exc.value)

    def test_negative_duration_rejected_trace_event(self):
        """Negative duration must be rejected on TraceEvent."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["duration_ms"] = -1
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "duration_ms" in str(exc.value)

    def test_negative_retry_rejected_trace_event(self):
        """Negative retry_number must be rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["retry_number"] = -1
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "retry_number" in str(exc.value)

    def test_bad_sha256_rejected_evidence_bundle(self):
        """Invalid SHA256 (wrong length or non-hex) must be rejected."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        data["artifacts"][0]["sha256"] = "not-a-hash"
        with pytest.raises(ValidationError) as exc:
            EvidenceBundle.model_validate(data)
        assert "sha256" in str(exc.value)

        data["artifacts"][0]["sha256"] = "0" * 63  # 63 chars, not 64
        with pytest.raises(ValidationError) as exc:
            EvidenceBundle.model_validate(data)
        assert "sha256" in str(exc.value)

    def test_empty_required_string_rejected(self):
        """Empty strings for required min_length=1 fields must be rejected."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["task_id"] = ""
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "task_id" in str(exc.value)


class TestAdversarialWorkerBoundaries:
    """Adversarial tests proving worker boundaries are enforced."""

    def create_request(self, workspace_path: str, run_id: str = "run-1") -> WorkerRequest:
        """Create a test WorkerRequest."""
        contract = RunContract(
            schema_version=SchemaVersion.V1_0,
            task_id="task-1",
            task="Test",
            repository=Repository(path=".", revision="main", clean_required=True),
            worker="mock",
            allowed_paths=["**"],
            denied_paths=[".env", ".git/**"],
            required_checks=[],
            budgets=Budgets(max_attempts=1, timeout_seconds=300, max_changed_files=10),
            approval_policy=ApprovalPolicy.ASK,
        )
        return WorkerRequest(
            run_id=run_id,
            task="Test",
            workspace_path=workspace_path,
            contract=contract,
        )

    async def test_path_traversal_blocked(self):
        """Path traversal (..) must be blocked - no file written outside workspace."""
        worker = MockWorker(
            scenario="success",
            configured_changes={"../escape.txt": "malicious"},
        )

        events = []

        class Sink:
            async def emit(self, event):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            await worker.run(request, Sink())

        # File should NOT be written outside workspace
        escape_file = Path(tmpdir).parent / "escape.txt"
        assert not escape_file.exists(), "Traversal write should be blocked"
        # No FILE_CHANGED event for the blocked attempt
        file_changed = [e for e in events if e.event_type.value == "file_changed"]
        assert len(file_changed) == 0

    async def test_absolute_path_blocked(self):
        """Absolute paths must be blocked."""
        worker = MockWorker(
            scenario="success",
            configured_changes={"/etc/passwd": "malicious"},
        )

        events = []

        class Sink:
            async def emit(self, event):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            await worker.run(request, Sink())

        # Should not write anywhere
        file_changed = [e for e in events if e.event_type.value == "file_changed"]
        assert len(file_changed) == 0

    async def test_symlink_escape_blocked(self):
        """Symlink pointing outside workspace must be blocked.

        On Windows, symlink creation requires elevated privileges, so we
        skip the creation test but verify the resolution logic works.
        """
        if sys.platform == "win32":
            pytest.skip(
                "Symlink creation requires elevated privileges on Windows; "
                "resolution logic tested separately"
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
            target.symlink_to(symlink)  # Note: reversed for Windows

            worker = MockWorker(
                scenario="success",
                configured_changes={"link.txt": "attempted write"},
            )

            events = []

            class Sink:
                async def emit(self, event):
                    events.append(event)

            request = self.create_request(str(workspace))
            await worker.run(request, Sink())

            # File should NOT be written to outside directory
            assert not target.exists() or target.read_text() == "outside"
            file_changed = [e for e in events if e.event_type.value == "file_changed"]
            assert len(file_changed) == 0

    async def test_worker_cannot_self_verify(self):
        """Worker's reported success is NOT final task completion.

        WorkerResult.success is only the worker's report. The control plane's
        independent verifier determines final task_completed via EvaluationResult.
        """
        worker = MockWorker(scenario="success", configured_changes={"test.txt": "content"})

        events = []

        class Sink:
            async def emit(self, event):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        # Worker reports success
        assert result.success is True
        # But worker does NOT set terminal_state (verifier decides)
        assert result.terminal_state is None
        # WorkerResult has no task_completed field - that's EvaluationResult
        assert not hasattr(result, "task_completed")

    async def test_capabilities_grant_no_permission(self):
        """WorkerCapabilities are flags only - no authorization fields."""
        worker = MockWorker()
        caps = worker.capabilities()

        # Verify no permission/authorization fields
        assert not hasattr(caps, "permissions")
        assert not hasattr(caps, "allowed_paths")
        assert not hasattr(caps, "allowed_commands")
        assert not hasattr(caps, "roles")
        assert not hasattr(caps, "scopes")

    async def test_repeated_equivalent_action_detectable(self):
        """Repeated equivalent action must be detectable in event stream."""
        worker = MockWorker(
            scenario="repeated_equivalent_action",
            configured_changes={"test.txt": "v1"},
        )

        events = []

        class Sink:
            async def emit(self, event):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            await worker.run(request, Sink())

        # Should have duplicate TOOL_REQUESTED and FILE_CHANGED for same path
        tool_requested = [e for e in events if e.event_type.value == "tool_requested"]
        file_changed = [e for e in events if e.event_type.value == "file_changed"]

        assert len(tool_requested) == 2
        assert len(file_changed) == 2
        # Both requests are for the same path
        assert tool_requested[0].payload.get("path") == tool_requested[1].payload.get("path")

    async def test_unsupported_evidence_claim_rejected(self):
        """Worker claiming success without evidence must be distinguishable.

        The reported_success_without_evidence scenario produces a result
        with success=True but NO FILE_CHANGED, CHECKPOINT, or artifact_refs.
        """
        worker = MockWorker(scenario="reported_success_without_evidence")

        events = []

        class Sink:
            async def emit(self, event):
                events.append(event)

        with tempfile.TemporaryDirectory() as tmpdir:
            request = self.create_request(tmpdir)
            result = await worker.run(request, Sink())

        assert result.success is True
        assert result.terminal_state is None  # Worker doesn't decide
        # No evidence events
        event_types = [e.event_type.value for e in events]
        assert "file_changed" not in event_types
        assert "checkpoint" not in event_types
        assert len(result.artifact_refs) == 0
        assert len(result.changed_files) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""Tests for WorkerEvent, EvidenceBundle, EvaluationResult, TraceEvent - TDD RED first."""

import json

import pytest
from pydantic import ValidationError

from reliable_agent_platform.contracts import (
    EvaluationResult,
    EventType,
    EvidenceBundle,
    SchemaVersion,
    TerminalState,
    TraceEvent,
    TraceStatus,
    WorkerEvent,
)


class TestWorkerEvent:
    """Test WorkerEvent model."""

    def test_valid_worker_event_from_example(self):
        """Valid example must parse."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        event = WorkerEvent.model_validate(data)
        assert event.schema_version == SchemaVersion.V1_0
        assert event.run_id == "run-001"
        assert event.event_type == EventType.WORKER_STARTED

    def test_reject_unknown_fields(self):
        """Unknown fields rejected."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["unknown"] = "bad"
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "unknown" in str(exc.value)

    def test_reject_invalid_version(self):
        """Unsupported schema version rejected."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["schema_version"] = "2.0"
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "schema_version" in str(exc.value)

    def test_reject_invalid_event_type(self):
        """Invalid event_type rejected (closed enum)."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["event_type"] = "not_an_event"
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "event_type" in str(exc.value)

    def test_reject_naive_datetime(self):
        """Naive datetime must be rejected."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["timestamp"] = "2026-07-17T12:00:00"  # no timezone
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "timestamp" in str(exc.value)

    def test_valid_timezone_aware_datetime(self):
        """Timezone-aware datetime accepted."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["timestamp"] = "2026-07-17T12:00:00Z"
        event = WorkerEvent.model_validate(data)
        assert event.timestamp.tzinfo is not None

    def test_json_round_trip(self):
        """JSON round-trip preserves equality."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        event = WorkerEvent.model_validate(data)
        json_str = event.model_dump_json()
        event2 = WorkerEvent.model_validate_json(json_str)
        assert event == event2

    def test_attempt_minimum_1(self):
        """Attempt must be >= 1."""
        with open("examples/contracts/worker-event.json") as f:
            data = json.load(f)
        data["attempt"] = 0
        with pytest.raises(ValidationError) as exc:
            WorkerEvent.model_validate(data)
        assert "attempt" in str(exc.value)


class TestEvidenceBundle:
    """Test EvidenceBundle, Artifact, Claim models."""

    def test_valid_evidence_bundle_from_example(self):
        """Valid example must parse."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        bundle = EvidenceBundle.model_validate(data)
        assert bundle.schema_version == "1.0"
        assert bundle.run_id == "run-001"
        assert len(bundle.artifacts) == 1
        assert len(bundle.claims) == 1

    def test_reject_unknown_fields(self):
        """Unknown fields rejected."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        data["unknown"] = "bad"
        with pytest.raises(ValidationError) as exc:
            EvidenceBundle.model_validate(data)
        assert "unknown" in str(exc.value)

    def test_reject_bad_sha256(self):
        """Invalid SHA256 rejected (must be 64 hex chars)."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        data["artifacts"][0]["sha256"] = "not-a-hash"
        with pytest.raises(ValidationError) as exc:
            EvidenceBundle.model_validate(data)
        assert "sha256" in str(exc.value)

    def test_artifact_sha256_pattern(self):
        """SHA256 must match pattern."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        # 63 chars - should fail
        data["artifacts"][0]["sha256"] = "0" * 63
        with pytest.raises(ValidationError) as exc:
            EvidenceBundle.model_validate(data)
        assert "sha256" in str(exc.value)

    def test_claim_verified_boolean(self):
        """Claim verified must be boolean."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        data["claims"][0]["verified"] = "not-bool"
        with pytest.raises(ValidationError) as exc:
            EvidenceBundle.model_validate(data)
        assert "verified" in str(exc.value)

    def test_claim_verifier_nullable(self):
        """Verifier can be null."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        data["claims"][0]["verifier"] = None
        bundle = EvidenceBundle.model_validate(data)
        assert bundle.claims[0].verifier is None

    def test_json_round_trip(self):
        """JSON round-trip."""
        with open("examples/contracts/evidence-bundle.json") as f:
            data = json.load(f)
        bundle = EvidenceBundle.model_validate(data)
        json_str = bundle.model_dump_json()
        bundle2 = EvidenceBundle.model_validate_json(json_str)
        assert bundle == bundle2


class TestEvaluationResult:
    """Test EvaluationResult model."""

    def test_valid_evaluation_result_from_example(self):
        """Valid example must parse."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        result = EvaluationResult.model_validate(data)
        assert result.schema_version == "1.0"
        assert result.terminal_state == TerminalState.COMPLETED
        assert result.task_completed is True

    def test_reject_unknown_fields(self):
        """Unknown fields rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["unknown"] = "bad"
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "unknown" in str(exc.value)

    def test_reject_invalid_terminal_state(self):
        """Invalid terminal state rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["terminal_state"] = "not_a_state"
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "terminal_state" in str(exc.value)

    def test_negative_attempts_rejected(self):
        """Negative attempts rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["attempts"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "attempts" in str(exc.value)

    def test_negative_changed_files_rejected(self):
        """Negative changed_files rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["changed_files"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "changed_files" in str(exc.value)

    def test_negative_duration_rejected(self):
        """Negative duration_ms rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["duration_ms"] = -1
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "duration_ms" in str(exc.value)

    def test_nullable_tokens_and_cost(self):
        """input_tokens, output_tokens, cost can be null."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["input_tokens"] = None
        data["output_tokens"] = None
        data["estimated_cost_usd"] = None
        result = EvaluationResult.model_validate(data)
        assert result.input_tokens is None
        assert result.output_tokens is None
        assert result.estimated_cost_usd is None

    def test_negative_cost_rejected(self):
        """Negative cost rejected."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        data["estimated_cost_usd"] = -0.01
        with pytest.raises(ValidationError) as exc:
            EvaluationResult.model_validate(data)
        assert "estimated_cost_usd" in str(exc.value)

    def test_json_round_trip(self):
        """JSON round-trip."""
        with open("examples/contracts/evaluation-result.json") as f:
            data = json.load(f)
        result = EvaluationResult.model_validate(data)
        json_str = result.model_dump_json()
        result2 = EvaluationResult.model_validate_json(json_str)
        assert result == result2


class TestTraceEvent:
    """Test TraceEvent model."""

    def test_valid_trace_event_from_example(self):
        """Valid example must parse."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        event = TraceEvent.model_validate(data)
        assert event.schema_version == "1.0"
        assert event.status == TraceStatus.OK
        assert event.project == "harness"

    def test_reject_unknown_fields(self):
        """Unknown fields rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["unknown"] = "bad"
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "unknown" in str(exc.value)

    def test_reject_invalid_status(self):
        """Invalid trace status rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["status"] = "not_a_status"
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "status" in str(exc.value)

    def test_reject_naive_started_at(self):
        """Naive started_at rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["started_at"] = "2026-07-17T12:00:00"  # no timezone
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "started_at" in str(exc.value)

    def test_negative_duration_rejected(self):
        """Negative duration_ms rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["duration_ms"] = -1
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "duration_ms" in str(exc.value)

    def test_negative_retry_rejected(self):
        """Negative retry_number rejected."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        data["retry_number"] = -1
        with pytest.raises(ValidationError) as exc:
            TraceEvent.model_validate(data)
        assert "retry_number" in str(exc.value)

    def test_json_round_trip(self):
        """JSON round-trip."""
        with open("examples/contracts/trace-event.json") as f:
            data = json.load(f)
        event = TraceEvent.model_validate(data)
        json_str = event.model_dump_json()
        event2 = TraceEvent.model_validate_json(json_str)
        assert event == event2


class TestSchemaConformance:
    """All examples must validate against JSON Schemas."""

    def test_all_examples_validate_against_jsonschema(self):
        """Each example validates against its JSON Schema."""
        from pathlib import Path

        import jsonschema

        example_dir = Path("examples/contracts")
        schema_dir = Path("specs/contracts")

        mapping = {
            "run-contract.json": "run-contract.schema.json",
            "worker-event.json": "worker-event.schema.json",
            "evidence-bundle.json": "evidence-bundle.schema.json",
            "evaluation-result.json": "evaluation-result.schema.json",
            "trace-event.json": "trace-event.schema.json",
        }

        for example_file, schema_file in mapping.items():
            example = json.loads((example_dir / example_file).read_text())
            schema = json.loads((schema_dir / schema_file).read_text())
            jsonschema.validate(instance=example, schema=schema)

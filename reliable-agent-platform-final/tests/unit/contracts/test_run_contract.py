"""Tests for RunContract and nested models - TDD RED phase first."""

import json

import pytest
from pydantic import ValidationError

from reliable_agent_platform.contracts import RunContract


class TestRunContract:
    """Test RunContract model with strict validation."""

    def test_valid_run_contract_from_example(self):
        """Valid example from examples/contracts/run-contract.json must parse."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        contract = RunContract.model_validate(data)
        assert contract.schema_version == "1.0"
        assert contract.task_id == "task-001"
        assert contract.worker == "mock"
        assert contract.approval_policy == "ask"

    def test_reject_unknown_fields(self):
        """Unknown top-level fields must be rejected (additionalProperties: false)."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["unknown_field"] = "not allowed"
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "unknown_field" in str(exc.value)

    def test_reject_unsupported_schema_version(self):
        """Schema version other than '1.0' must be rejected (const)."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["schema_version"] = "2.0"
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "schema_version" in str(exc.value)

    def test_reject_negative_budgets(self):
        """Negative budget values must be rejected (minimum: 0 or 1)."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["budgets"]["max_attempts"] = -1
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "max_attempts" in str(exc.value)

        data["budgets"]["max_attempts"] = 1
        data["budgets"]["timeout_seconds"] = -5
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "timeout_seconds" in str(exc.value)

        data["budgets"]["timeout_seconds"] = 300
        data["budgets"]["max_changed_files"] = -1
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "max_changed_files" in str(exc.value)

        data["budgets"]["max_changed_files"] = 20
        data["budgets"]["max_cost_usd"] = -0.01
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "max_cost_usd" in str(exc.value)

    def test_reject_invalid_approval_policy(self):
        """Approval policy must be one of the closed enum values."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["approval_policy"] = "invalid_policy"
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "approval_policy" in str(exc.value)

    def test_valid_approval_policies(self):
        """All three enum values must be accepted."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        for policy in ["auto", "ask", "deny"]:
            data["approval_policy"] = policy
            contract = RunContract.model_validate(data)
            assert contract.approval_policy == policy

    def test_json_round_trip(self):
        """Model must serialize to JSON and deserialize with equality."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        contract = RunContract.model_validate(data)
        json_str = contract.model_dump_json()
        contract2 = RunContract.model_validate_json(json_str)
        assert contract == contract2

    def test_nested_repository_validation(self):
        """Repository nested model must validate required fields."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["repository"]["path"] = ""
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "path" in str(exc.value)

    def test_nested_budgets_validation(self):
        """Budgets nested model must validate all required fields."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        # Missing required field
        del data["budgets"]["max_attempts"]
        with pytest.raises(ValidationError) as exc:
            RunContract.model_validate(data)
        assert "max_attempts" in str(exc.value)

    def test_optional_fields_can_be_none(self):
        """Optional fields (goal_id, allowed_commands, denied_commands) accept null; metadata defaults to empty dict."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["goal_id"] = None
        data["allowed_commands"] = None
        data["denied_commands"] = None
        data["metadata"] = {}
        contract = RunContract.model_validate(data)
        assert contract.goal_id is None
        assert contract.allowed_commands is None
        assert contract.denied_commands is None
        assert contract.metadata == {}

    def test_allowed_commands_denied_commands_are_lists(self):
        """When provided, allowed_commands and denied_commands must be lists of strings."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        data["allowed_commands"] = ["pytest", "ruff"]
        data["denied_commands"] = ["rm -rf /"]
        contract = RunContract.model_validate(data)
        assert contract.allowed_commands == ["pytest", "ruff"]
        assert contract.denied_commands == ["rm -rf /"]

    def test_semantic_round_trip_equality(self):
        """Two models created from same data must be equal; different data must not."""
        with open("examples/contracts/run-contract.json") as f:
            data = json.load(f)
        c1 = RunContract.model_validate(data)
        c2 = RunContract.model_validate(data)
        assert c1 == c2
        data["task_id"] = "different-task"
        c3 = RunContract.model_validate(data)
        assert c1 != c3

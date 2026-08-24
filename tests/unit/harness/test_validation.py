"""Unit tests for the pre-execution contract validation gate - TDD red."""

import pytest

from reliable_agent_platform.contracts import RunContract
from reliable_agent_platform.harness.validation import (
    ValidationCode,
    ensure_valid,
    validate_run_contract,
)


def _base_contract_kwargs():
    return {
        "task_id": "task-042",
        "task": "Implement the widget.",
        "repository": {"path": ".", "revision": "main", "clean_required": True},
        "worker": "mock",
        "allowed_paths": ["src/**"],
        "denied_paths": [".env"],
        "required_checks": ["make test"],
        "budgets": {
            "max_attempts": 1,
            "timeout_seconds": 300,
            "max_changed_files": 5,
        },
        "approval_policy": "ask",
    }


def _make_contract(**overrides):
    data = _base_contract_kwargs()
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    return RunContract.model_validate(data)


class TestValidContracts:
    """Well-formed contracts pass through unchanged."""

    def test_example_fixture_is_clean(self):
        import json

        with open("examples/contracts/run-contract.json") as handle:
            contract = RunContract.model_validate(json.load(handle))
        assert validate_run_contract(contract) == ()

    def test_minimal_contract_is_clean(self):
        contract = _make_contract(
            allowed_commands=None,
            denied_commands=None,
            goal_id=None,
        )
        assert validate_run_contract(contract) == ()


class TestSemanticRejections:
    """Each malformed contract yields structured issues with reason codes."""

    def test_allowed_and_denied_overlap_rejected(self):
        contract = _make_contract(denied_paths=[".env", "src/**"])
        issues = validate_run_contract(contract)
        assert any(i.code is ValidationCode.ALLOWED_DENIED_PATH_OVERLAP for i in issues)

    def test_absolute_posix_path_rejected(self):
        contract = _make_contract(allowed_paths=["src/**", "/etc"])
        issues = validate_run_contract(contract)
        assert any(
            i.code is ValidationCode.PATH_NOT_NORMALIZED and i.field == "allowed_paths[1]"
            for i in issues
        )

    def test_drive_letter_path_rejected(self):
        contract = _make_contract(denied_paths=["C:/Windows"])
        issues = validate_run_contract(contract)
        assert any(i.code is ValidationCode.PATH_NOT_NORMALIZED for i in issues)

    def test_traversal_path_rejected(self):
        contract = _make_contract(allowed_paths=["../secrets/**"])
        issues = validate_run_contract(contract)
        assert any(i.code is ValidationCode.PATH_NOT_NORMALIZED for i in issues)

    def test_backslash_path_rejected(self):
        contract = _make_contract(allowed_paths=["src\\generated"])
        issues = validate_run_contract(contract)
        assert any(i.code is ValidationCode.PATH_NOT_NORMALIZED for i in issues)

    @pytest.mark.parametrize("field", ["task_id", "worker"])
    def test_whitespace_only_identifiers_rejected(self, field):
        kwargs = {field: "   "}
        contract = _make_contract(**kwargs)
        issues = validate_run_contract(contract)
        assert any(i.code is ValidationCode.WHITESPACE_ONLY and i.field == field for i in issues)

    def test_blank_task_text_rejected(self):
        contract = _make_contract(task="  \n\t ")
        issues = validate_run_contract(contract)
        assert any(i.code is ValidationCode.WHITESPACE_ONLY for i in issues)

    def test_duplicate_required_checks_rejected(self):
        contract = _make_contract(required_checks=["make test", "make test"])
        issues = validate_run_contract(contract)
        assert any(
            i.code is ValidationCode.DUPLICATE_ENTRY and i.field == "required_checks"
            for i in issues
        )

    def test_duplicate_denied_commands_rejected(self):
        contract = _make_contract(denied_commands=["git push", "git push"])
        issues = validate_run_contract(contract)
        assert any(i.code is ValidationCode.DUPLICATE_ENTRY for i in issues)


class TestVerifierGate:
    """No independent checks means false completion is undetectable - refuse."""

    def test_empty_required_checks_rejected(self):
        contract = _make_contract(required_checks=[])
        issues = validate_run_contract(contract)
        assert any(
            i.code is ValidationCode.EMPTY_REQUIRED_CHECKS and i.field == "required_checks"
            for i in issues
        )


class TestIssueAggregation:
    """All violations surface together, not just the first."""

    def test_multiple_issues_reported(self):
        contract = _make_contract(
            task_id=" ",
            required_checks=[],
            allowed_paths=["/abs", "src/**"],
        )
        codes = {i.code for i in validate_run_contract(contract)}
        assert {
            ValidationCode.WHITESPACE_ONLY,
            ValidationCode.EMPTY_REQUIRED_CHECKS,
            ValidationCode.PATH_NOT_NORMALIZED,
        } <= codes


class TestEnsureValid:
    """The raising convenience wrapper carries its issues."""

    def test_ensure_valid_accepts_good_contract(self):
        ensure_valid(_make_contract())

    def test_ensure_valid_raises_with_structured_issues(self):
        from reliable_agent_platform.harness.validation import ContractValidationError

        bad = _make_contract(required_checks=[], denied_paths=[".env", "src/**"])
        with pytest.raises(ContractValidationError) as excinfo:
            ensure_valid(bad)
        codes = {i.code for i in excinfo.value.issues}
        assert ValidationCode.EMPTY_REQUIRED_CHECKS in codes
        assert ValidationCode.ALLOWED_DENIED_PATH_OVERLAP in codes

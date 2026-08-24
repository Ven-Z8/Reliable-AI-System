"""Pre-execution contract validation gate.

Pydantic already enforces shape (types, enums, budget minimums). This gate
enforces *semantics* Pydantic cannot express: policy ambiguity, traversal
shapes, duplicate declarations, blank identifiers, and - most importantly -
contracts that make independent verification impossible by declaring no
required checks.
"""

import re
from enum import StrEnum
from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict

from reliable_agent_platform.contracts import RunContract


class ValidationCode(StrEnum):
    """Closed vocabulary of contract rejection reason codes."""

    ALLOWED_DENIED_PATH_OVERLAP = "allowed_denied_path_overlap"
    DUPLICATE_ENTRY = "duplicate_entry"
    WHITESPACE_ONLY = "whitespace_only"
    PATH_NOT_NORMALIZED = "path_not_normalized"
    EMPTY_REQUIRED_CHECKS = "empty_required_checks"


class ValidationIssue(BaseModel):
    """One structured rejection reason."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: ValidationCode
    field: str
    detail: str


class ContractValidationError(Exception):
    """Raised when a contract fails semantic validation."""

    def __init__(self, issues: tuple[ValidationIssue, ...]) -> None:
        self.issues = issues
        summary = "; ".join(f"{i.field}: {i.code.value}" for i in issues)
        super().__init__(f"contract rejected ({len(issues)} issue(s)): {summary}")


_DRIVE_LETTER = re.compile(r"^[A-Za-z]:")


def _path_issue(field: str, value: str) -> ValidationIssue | None:
    if "\\" in value or value.startswith("/") or _DRIVE_LETTER.match(value):
        return ValidationIssue(
            code=ValidationCode.PATH_NOT_NORMALIZED,
            field=field,
            detail=f"path must be workspace-relative with forward slashes: {value!r}",
        )
    if ".." in PurePosixPath(value).parts:
        return ValidationIssue(
            code=ValidationCode.PATH_NOT_NORMALIZED,
            field=field,
            detail=f"path must not traverse upward: {value!r}",
        )
    return None


def _duplicate_issues(field: str, values: list[str]) -> list[ValidationIssue]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return [
        ValidationIssue(
            code=ValidationCode.DUPLICATE_ENTRY,
            field=field,
            detail=f"duplicate entry: {value!r}",
        )
        for value in duplicates
    ]


def _blank_issues(field: str, value: str) -> list[ValidationIssue]:
    if not value.strip():
        return [
            ValidationIssue(
                code=ValidationCode.WHITESPACE_ONLY,
                field=field,
                detail="identifier must contain non-whitespace characters",
            )
        ]
    return []


def validate_run_contract(contract: RunContract) -> tuple[ValidationIssue, ...]:
    """Return every semantic violation of the contract; empty means valid."""
    issues: list[ValidationIssue] = []

    for identifier_field in ("task_id", "task", "worker"):
        issues.extend(_blank_issues(identifier_field, getattr(contract, identifier_field)))
    if contract.goal_id is not None:
        issues.extend(_blank_issues("goal_id", contract.goal_id))

    for list_field in ("allowed_paths", "denied_paths"):
        values: list[str] = getattr(contract, list_field)
        for index, value in enumerate(values):
            issue = _path_issue(f"{list_field}[{index}]", value)
            if issue is not None:
                issues.append(issue)
        issues.extend(_duplicate_issues(list_field, values))

    overlap = sorted(set(contract.allowed_paths) & set(contract.denied_paths))
    if overlap:
        issues.append(
            ValidationIssue(
                code=ValidationCode.ALLOWED_DENIED_PATH_OVERLAP,
                field="allowed_paths",
                detail=f"paths both allowed and denied: {overlap}",
            )
        )

    if contract.allowed_commands is not None:
        issues.extend(_duplicate_issues("allowed_commands", contract.allowed_commands))
    if contract.denied_commands is not None:
        issues.extend(_duplicate_issues("denied_commands", contract.denied_commands))

    issues.extend(_duplicate_issues("required_checks", contract.required_checks))

    if not contract.required_checks:
        issues.append(
            ValidationIssue(
                code=ValidationCode.EMPTY_REQUIRED_CHECKS,
                field="required_checks",
                detail=(
                    "no independent checks declared; false completion would be "
                    "undetectable - declare at least one verifier command"
                ),
            )
        )

    return tuple(issues)


def ensure_valid(contract: RunContract) -> None:
    """Raise :class:`ContractValidationError` unless the contract is clean."""
    issues = validate_run_contract(contract)
    if issues:
        raise ContractValidationError(issues)

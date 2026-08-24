"""Tests for the harness run state machine - written FIRST (TDD red)."""

import pytest

from reliable_agent_platform.contracts.enums import TerminalState
from reliable_agent_platform.harness.run_state import (
    IllegalTransitionError,
    RunPhase,
    RunStateMachine,
)


class TestRunPhase:
    """Phase vocabulary must align with M1 contract enums."""

    def test_terminal_phases_match_contract_terminal_states(self):
        """Terminal phases must equal contracts.TerminalState values - vocabulary cannot drift."""
        assert set(RunPhase.terminal_phases()) == set(TerminalState)

    def test_execution_phases_are_not_terminal(self):
        """Worker-reported success must never be treated as terminal."""
        assert RunPhase.RUNNING not in RunPhase.terminal_phases()
        assert RunPhase.VERIFYING not in RunPhase.terminal_phases()


class TestHappyPath:
    """Legal transitions through the normal lifecycle."""

    def test_new_machine_starts_created(self):
        machine = RunStateMachine(run_id="run-001")
        assert machine.phase is RunPhase.CREATED

    def test_full_lifecycle_to_verified_completion(self):
        machine = RunStateMachine(run_id="run-001")
        machine.transition(RunPhase.VALIDATED)
        machine.transition(RunPhase.RUNNING)
        machine.transition(RunPhase.VERIFYING)
        machine.transition(RunPhase.COMPLETED)
        assert machine.phase is RunPhase.COMPLETED
        assert machine.is_terminal

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ([RunPhase.VALIDATED, RunPhase.RUNNING, RunPhase.TIMEOUT], RunPhase.TIMEOUT),
            (
                [RunPhase.VALIDATED, RunPhase.RUNNING, RunPhase.BUDGET_EXHAUSTED],
                RunPhase.BUDGET_EXHAUSTED,
            ),
            (
                [RunPhase.VALIDATED, RunPhase.RUNNING, RunPhase.WORKER_FAILED],
                RunPhase.WORKER_FAILED,
            ),
            (
                [RunPhase.BLOCKED_BY_POLICY],
                RunPhase.BLOCKED_BY_POLICY,
            ),
            (
                [RunPhase.VALIDATION_FAILED],
                RunPhase.VALIDATION_FAILED,
            ),
            (
                [RunPhase.VALIDATED, RunPhase.RUNNING, RunPhase.NO_PROGRESS],
                RunPhase.NO_PROGRESS,
            ),
            (
                [RunPhase.VALIDATED, RunPhase.RUNNING, RunPhase.SYSTEM_ERROR],
                RunPhase.SYSTEM_ERROR,
            ),
        ],
    )
    def test_documented_paths_to_terminals(self, path, expected):
        machine = RunStateMachine(run_id="run-001")
        for step in path:
            machine.transition(step, reason="documented-path")
        assert machine.phase is expected


class TestIllegalTransitions:
    """The state machine must refuse impossible moves."""

    def test_skip_straight_to_completed_is_illegal(self):
        machine = RunStateMachine(run_id="run-001")
        with pytest.raises(IllegalTransitionError) as exc:
            machine.transition(RunPhase.COMPLETED)
        assert "created" in str(exc.value)
        assert "completed" in str(exc.value)

    def test_cannot_complete_without_verification(self):
        machine = RunStateMachine(run_id="run-001")
        machine.transition(RunPhase.VALIDATED)
        machine.transition(RunPhase.RUNNING)
        with pytest.raises(IllegalTransitionError):
            machine.transition(RunPhase.COMPLETED)


class TestTerminalAbsorption:
    """Terminal states are final - except the single sanctioned human resume."""

    def test_completed_absorbs_everything(self):
        machine = RunStateMachine(run_id="run-001")
        for step in (RunPhase.VALIDATED, RunPhase.RUNNING, RunPhase.VERIFYING):
            machine.transition(step)
        machine.transition(RunPhase.COMPLETED)
        for target in RunPhase:
            with pytest.raises(IllegalTransitionError):
                machine.transition(target)

    def test_worker_failed_is_absorbing(self):
        machine = RunStateMachine(run_id="run-001")
        machine.transition(RunPhase.VALIDATED)
        machine.transition(RunPhase.RUNNING)
        machine.transition(RunPhase.WORKER_FAILED, reason="worker process exited non-zero")
        with pytest.raises(IllegalTransitionError):
            machine.transition(RunPhase.RUNNING)

    def test_awaiting_human_resumes_only_with_approval_reference(self):
        machine = RunStateMachine(run_id="run-001")
        machine.transition(RunPhase.VALIDATED)
        machine.transition(RunPhase.RUNNING)
        machine.transition(RunPhase.AWAITING_HUMAN)
        assert machine.is_terminal

        with pytest.raises(IllegalTransitionError):
            machine.transition(RunPhase.RUNNING)

        machine.transition(RunPhase.RUNNING, approval_ref="approver:venki:2026-08-24")
        assert machine.phase is RunPhase.RUNNING


class TestEvidenceRequirements:
    """Terminal entries demand reasons; human resume demands an approval reference."""

    def test_reason_required_for_failure_terminals(self):
        machine = RunStateMachine(run_id="run-001")
        machine.transition(RunPhase.VALIDATED)
        machine.transition(RunPhase.RUNNING)
        with pytest.raises(IllegalTransitionError) as exc:
            machine.transition(RunPhase.TIMEOUT, reason=None)
        assert "reason" in str(exc.value)

    def test_completed_and_awaiting_human_need_no_reason(self):
        machine = RunStateMachine(run_id="run-001")
        machine.transition(RunPhase.VALIDATED)
        machine.transition(RunPhase.RUNNING)
        machine.transition(RunPhase.VERIFYING)
        machine.transition(RunPhase.COMPLETED)

        machine2 = RunStateMachine(run_id="run-002")
        machine2.transition(RunPhase.VALIDATED)
        machine2.transition(RunPhase.RUNNING)
        machine2.transition(RunPhase.AWAITING_HUMAN)


class TestHistory:
    """Every transition is recorded with monotonic timestamps."""

    def test_history_records_all_transitions(self):
        machine = RunStateMachine(run_id="run-001", clock=lambda: 1000.0)
        machine.transition(RunPhase.VALIDATED)
        machine.transition(RunPhase.RUNNING)
        assert len(machine.history) == 2
        assert [r.seq for r in machine.history] == [1, 2]
        stamps = [r.at for r in machine.history]
        assert stamps[1] >= stamps[0]

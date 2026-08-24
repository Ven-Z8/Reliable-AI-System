"""Run lifecycle state machine.

Invariants:
- Worker-reported success is never terminal; only verified outcomes are.
- Terminal phases are absorbing, except AWAITING_HUMAN which resumes solely
  on an explicit approval reference.
- Every transition becomes an immutable, hash-chained TransitionRecord so any
  run can be replayed bit-for-bit from its journal.
"""

import hashlib
import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from reliable_agent_platform.contracts.enums import TerminalState


class RunPhase(StrEnum):
    """Closed vocabulary of run lifecycle phases.

    The terminal members mirror ``contracts.TerminalState`` value-for-value;
    ``terminal_phases()`` plus its unit test enforce that alignment.
    """

    # Execution phases (non-terminal)
    CREATED = "created"
    VALIDATED = "validated"
    RUNNING = "running"
    VERIFYING = "verifying"

    # Terminal phases (mirror contracts.TerminalState)
    COMPLETED = "completed"
    AWAITING_HUMAN = "awaiting_human"
    REJECTED = "rejected"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    VALIDATION_FAILED = "validation_failed"
    WORKER_FAILED = "worker_failed"
    NO_PROGRESS = "no_progress"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TIMEOUT = "timeout"
    SYSTEM_ERROR = "system_error"

    @classmethod
    def terminal_phases(cls) -> frozenset["RunPhase"]:
        """The absorbing phases, equal by value to contracts.TerminalState."""
        return frozenset(
            phase for phase in cls if any(phase.value == state.value for state in TerminalState)
        )


#: Legal transitions. Any phase not listed as a key has no exits (absorbing).
TRANSITIONS: dict[RunPhase, frozenset[RunPhase]] = {
    RunPhase.CREATED: frozenset(
        {RunPhase.VALIDATED, RunPhase.VALIDATION_FAILED, RunPhase.BLOCKED_BY_POLICY}
    ),
    RunPhase.VALIDATED: frozenset({RunPhase.RUNNING, RunPhase.BLOCKED_BY_POLICY}),
    RunPhase.RUNNING: frozenset(
        {
            RunPhase.VERIFYING,
            RunPhase.WORKER_FAILED,
            RunPhase.TIMEOUT,
            RunPhase.BUDGET_EXHAUSTED,
            RunPhase.SYSTEM_ERROR,
            RunPhase.NO_PROGRESS,
            RunPhase.AWAITING_HUMAN,
            RunPhase.BLOCKED_BY_POLICY,
        }
    ),
    RunPhase.VERIFYING: frozenset(
        {
            RunPhase.COMPLETED,
            RunPhase.REJECTED,
            RunPhase.NO_PROGRESS,
            RunPhase.WORKER_FAILED,
            RunPhase.SYSTEM_ERROR,
            RunPhase.AWAITING_HUMAN,
        }
    ),
    RunPhase.AWAITING_HUMAN: frozenset({RunPhase.RUNNING}),
}

#: Terminal entries that demand a recorded reason.
_REASON_REQUIRED_TERMINALS: frozenset[RunPhase] = RunPhase.terminal_phases() - {
    RunPhase.COMPLETED,
    RunPhase.AWAITING_HUMAN,
}


class TransitionRecord(BaseModel):
    """Immutable, hash-chained record of one state-machine transition."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    seq: int = Field(ge=1)
    run_id: str = Field(min_length=1)
    at: AwareDatetime
    from_phase: RunPhase
    to_phase: RunPhase
    reason: str | None = None
    approval_ref: str | None = None
    prev_hash: str = Field(default="genesis")


def record_hash(record: TransitionRecord) -> str:
    """Content hash chaining a record to its predecessor."""
    payload = json.dumps(record.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class IllegalTransitionError(Exception):
    """Raised when a transition or evidence requirement violates lifecycle rules."""


class RunStateMachine:
    """Enforces the run lifecycle and records every transition.

    ``clock`` is injectable so tests can make timestamps deterministic.
    """

    def __init__(self, run_id: str, clock: Callable[[], float] | None = None) -> None:
        self.run_id = run_id
        self._clock = clock if clock is not None else time.time
        self._phase = RunPhase.CREATED
        self.history: list[TransitionRecord] = []
        self._last_hash: str = "genesis"

    @property
    def phase(self) -> RunPhase:
        return self._phase

    @property
    def is_terminal(self) -> bool:
        return self._phase in RunPhase.terminal_phases()

    def transition(
        self,
        to_phase: RunPhase,
        *,
        reason: str | None = None,
        approval_ref: str | None = None,
    ) -> TransitionRecord:
        target = RunPhase(to_phase)

        allowed = TRANSITIONS.get(self._phase, frozenset())
        if target not in allowed:
            raise IllegalTransitionError(
                f"illegal transition {self._phase.value} -> {target.value}"
            )

        if target in _REASON_REQUIRED_TERMINALS and not reason:
            raise IllegalTransitionError(
                f"reason required when entering terminal state {target.value}"
            )

        if self._phase is RunPhase.AWAITING_HUMAN and not approval_ref:
            raise IllegalTransitionError("resuming from awaiting_human requires an approval_ref")

        record = TransitionRecord(
            seq=len(self.history) + 1,
            run_id=self.run_id,
            at=datetime.fromtimestamp(self._clock(), tz=UTC),
            from_phase=self._phase,
            to_phase=target,
            reason=reason,
            approval_ref=approval_ref,
            prev_hash=self._last_hash,
        )
        self._adopt(record)
        return record

    def replay(self, records: list[TransitionRecord]) -> None:
        """Absorb pre-formed journal records verbatim (timestamps included)."""
        for record in records:
            self._adopt(record)

    def _adopt(self, record: TransitionRecord) -> None:
        """Validate a fully-formed record against current state and absorb it."""
        expected_seq = len(self.history) + 1
        if record.seq != expected_seq:
            raise IllegalTransitionError(
                f"sequence break: expected {expected_seq}, got {record.seq}"
            )
        if record.prev_hash != self._last_hash:
            raise IllegalTransitionError(f"hash chain broken at seq {record.seq}")

        allowed = TRANSITIONS.get(self._phase, frozenset())
        if record.to_phase not in allowed:
            raise IllegalTransitionError(
                f"illegal transition {self._phase.value} -> {record.to_phase.value}"
            )
        if RunPhase(record.from_phase) != self._phase:
            raise IllegalTransitionError(
                f"record claims origin {record.from_phase.value}, machine is at {self._phase.value}"
            )
        if record.to_phase in _REASON_REQUIRED_TERMINALS and not record.reason:
            raise IllegalTransitionError(
                f"reason required when entering terminal state {record.to_phase.value}"
            )
        if self._phase is RunPhase.AWAITING_HUMAN and not record.approval_ref:
            raise IllegalTransitionError("resuming from awaiting_human requires an approval_ref")

        self.history.append(record)
        self._phase = record.to_phase
        self._last_hash = record_hash(record)

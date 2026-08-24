"""Adversarial tests for the run state machine and its durable journal."""

import json

import pytest
from pydantic import ValidationError

from reliable_agent_platform.harness.run_state import (
    RunPhase,
    RunStateMachine,
    TransitionRecord,
)
from reliable_agent_platform.harness.store import (
    FileRunJournal,
    JournalCorruptionError,
)


def _drive_to_running(run_id: str = "run-adv") -> RunStateMachine:
    machine = RunStateMachine(run_id=run_id)
    machine.transition(RunPhase.VALIDATED)
    machine.transition(RunPhase.RUNNING)
    return machine


class TestClosedVocabulary:
    """Unknown phases must be impossible to introduce."""

    def test_unknown_phase_string_rejected(self):
        with pytest.raises((ValueError, ValidationError)):
            RunStateMachine(run_id="run-001").transition("teleported_to_mars")  # type: ignore[arg-type]

    def test_record_with_unknown_phase_rejected(self):
        with pytest.raises(ValidationError):
            TransitionRecord(
                seq=1,
                run_id="run-001",
                at="2026-08-24T12:00:00Z",
                from_phase="created",
                to_phase="not_a_phase",
            )


class TestJournalIntegrity:
    """The journal is evidence - it must be tamper-evident and replayable."""

    def _write_sample_journal(self, tmp_path):
        journal_path = tmp_path / "journal.jsonl"
        machine = RunStateMachine(run_id="run-001")
        journal = FileRunJournal(journal_path)
        for step in (RunPhase.VALIDATED, RunPhase.RUNNING, RunPhase.VERIFYING, RunPhase.COMPLETED):
            machine.transition(step)
            journal.append(machine.history[-1])
        return journal_path

    def test_replay_reconstructs_final_phase(self, tmp_path):
        journal_path = self._write_sample_journal(tmp_path)
        reloaded = FileRunJournal(journal_path)
        machine = reloaded.replay_into(RunStateMachine)
        assert machine.phase is RunPhase.COMPLETED
        assert len(machine.history) == 4

    def test_replay_is_deterministic_after_crash_simulation(self, tmp_path):
        journal_path = self._write_sample_journal(tmp_path)
        first = FileRunJournal(journal_path).replay_into(RunStateMachine)
        second = FileRunJournal(journal_path).replay_into(RunStateMachine)
        assert first.history == second.history

    def test_tampered_line_detected(self, tmp_path):
        journal_path = self._write_sample_journal(tmp_path)
        lines = journal_path.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[1])
        record["to_phase"] = "completed"  # forger tries to fake completion
        lines[1] = json.dumps(record)
        journal_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with pytest.raises(JournalCorruptionError):
            FileRunJournal(journal_path).replay_into(RunStateMachine)

    def test_sequence_gap_detected(self, tmp_path):
        journal_path = self._write_sample_journal(tmp_path)
        lines = journal_path.read_text(encoding="utf-8").splitlines()
        del lines[2]  # rip out a middle transition
        journal_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with pytest.raises(JournalCorruptionError):
            FileRunJournal(journal_path).replay_into(RunStateMachine)

    def test_trailing_garbage_line_detected(self, tmp_path):
        journal_path = self._write_sample_journal(tmp_path)
        with open(journal_path, "a", encoding="utf-8") as f:
            f.write("{not even json}\n")

        with pytest.raises(JournalCorruptionError):
            FileRunJournal(journal_path).replay_into(RunStateMachine)


class TestRecordStrictness:
    """Journal records are contracts - strict parsing applies."""

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError):
            TransitionRecord(
                seq=1,
                run_id="run-001",
                at="2026-08-24T12:00:00Z",
                from_phase="created",
                to_phase="validated",
                sneaky_field="nope",  # type: ignore[call-arg]
            )

    def test_naive_datetime_rejected(self):
        with pytest.raises(ValidationError):
            TransitionRecord(
                seq=1,
                run_id="run-001",
                at="2026-08-24T12:00:00",
                from_phase="created",
                to_phase="validated",
            )

    def test_zero_seq_rejected(self):
        with pytest.raises(ValidationError):
            TransitionRecord(
                seq=0,
                run_id="run-001",
                at="2026-08-24T12:00:00Z",
                from_phase="created",
                to_phase="validated",
            )


class TestAppendGuards:
    """Appending must respect the chain - no rewriting history."""

    def test_append_out_of_order_rejected(self, tmp_path):
        journal_path = tmp_path / "journal.jsonl"
        machine = RunStateMachine(run_id="run-001")
        journal = FileRunJournal(journal_path)

        machine.transition(RunPhase.VALIDATED)
        journal.append(machine.history[-1])

        # A forged record claiming seq 3 when the next valid is 2.
        forged = TransitionRecord(
            seq=3,
            run_id="run-001",
            at="2026-08-24T12:00:01Z",
            from_phase="validated",
            to_phase="running",
        )
        with pytest.raises(JournalCorruptionError):
            journal.append(forged)

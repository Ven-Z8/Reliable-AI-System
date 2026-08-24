"""Append-only, tamper-evident run journal.

The journal is evidence: each line is a hash-chained TransitionRecord, and a
sidecar file pins the hash of the final entry so even tail tampering is
detected. Replay verifies seq contiguity, the full hash chain, and the
sidecar before reconstructing machine state.
"""

import json
from pathlib import Path

from pydantic import ValidationError

from reliable_agent_platform.harness.run_state import (
    RunStateMachine,
    TransitionRecord,
    record_hash,
)

_GENESIS = "genesis"


class JournalCorruptionError(Exception):
    """Raised when the journal fails integrity or structural validation."""


class FileRunJournal:
    """JSONL-backed append-only journal for one run."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.tail_path = Path(str(self.path) + ".tail")

    def append(self, record: TransitionRecord) -> None:
        """Append a record whose seq and prev_hash continue the chain."""
        last_seq, last_hash = self._tail()
        if record.seq != last_seq + 1:
            raise JournalCorruptionError(
                f"append rejected: expected seq {last_seq + 1}, got {record.seq}"
            )
        if record.prev_hash != last_hash:
            raise JournalCorruptionError("append rejected: prev_hash does not chain to tail")

        line = json.dumps(record.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self.tail_path.write_text(record_hash(record), encoding="utf-8")

    def replay_into(self, machine_cls: type[RunStateMachine]) -> RunStateMachine:
        """Verify the whole chain and sidecar, then rebuild machine state."""
        records = self._verified_records()
        machine = machine_cls(run_id=records[0].run_id if records else "unknown")
        machine.replay(records)

        if records:
            stored_tail = self.tail_path.read_text(encoding="utf-8").strip()
            computed_tail = record_hash(records[-1])
            if stored_tail != computed_tail:
                raise JournalCorruptionError("tail hash does not match sidecar pin")
        return machine

    def _tail(self) -> tuple[int, str]:
        """Return (seq, entry_hash) of the last valid record; genesis if empty."""
        if not self.path.exists():
            return 0, _GENESIS
        lines = self.path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return 0, _GENESIS
        try:
            last = TransitionRecord.model_validate(json.loads(lines[-1]))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise JournalCorruptionError(f"unreadable tail line: {exc}") from exc
        return last.seq, record_hash(last)

    def _verified_records(self) -> list[TransitionRecord]:
        if not self.path.exists():
            return []

        records: list[TransitionRecord] = []
        previous_hash = _GENESIS
        for lineno, raw in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                record = TransitionRecord.model_validate_json(raw)
            except (ValidationError, ValueError) as exc:
                raise JournalCorruptionError(f"line {lineno}: invalid record: {exc}") from exc

            if record.seq != lineno:
                raise JournalCorruptionError(f"line {lineno}: sequence gap (got seq {record.seq})")
            if record.prev_hash != previous_hash:
                raise JournalCorruptionError(f"line {lineno}: hash chain broken")

            previous_hash = record_hash(record)
            records.append(record)
        return records

"""Validate the starter repository without third-party dependencies."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    ".hermes.md",
    "AGENTS.md",
    "README.md",
    "docs/FINALIZED_PLAN.md",
    "docs/status.md",
    "prompts/001-foundation-contracts-and-mock-worker.md",
    "specs/contracts/run-contract.schema.json",
    "specs/contracts/worker-event.schema.json",
    "specs/contracts/evidence-bundle.schema.json",
    "specs/contracts/evaluation-result.schema.json",
    "specs/contracts/trace-event.schema.json",
)


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    schema_dir = ROOT / "specs" / "contracts"
    for schema_path in sorted(schema_dir.glob("*.json")):
        try:
            value = json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {schema_path.relative_to(ROOT)}: {exc}")
            continue
        if value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{schema_path.relative_to(ROOT)} does not declare JSON Schema 2020-12")
        if value.get("additionalProperties") is not False:
            errors.append(f"{schema_path.relative_to(ROOT)} must reject unknown top-level fields")

    example_dir = ROOT / "examples" / "contracts"
    for example_path in sorted(example_dir.glob("*.json")):
        try:
            json.loads(example_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid example JSON {example_path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Starter validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Starter validation passed.")
    print(f"- required files: {len(REQUIRED_FILES)}")
    print(f"- schemas: {len(list(schema_dir.glob('*.json')))}")
    print(f"- examples: {len(list(example_dir.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

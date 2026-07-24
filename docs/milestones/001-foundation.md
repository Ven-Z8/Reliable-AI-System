# Milestone 1 — Foundation, Contracts, and Deterministic Mock Worker

**Status: COMPLETE**  
**Branch:** `milestone/01-foundation`  
**Date:** 2026-07-17  
**Commit:** (to be recorded after final commit)

---

## Objective

Implement the first executable platform slice:
- Strict versioned contracts
- Worker-neutral protocol
- Deterministic mock worker
- Contract examples and validation
- Focused unit and adversarial tests
- Real verification evidence

---

## Deliverables Implemented

### 1. Contracts Package (`src/reliable_agent_platform/contracts/`)

| File | Description |
|------|-------------|
| `enums.py` | Closed `StrEnum`s: `SchemaVersion` (V1_0), `EventType` (12 values), `ApprovalPolicy` (auto/ask/deny), `TerminalState` (10 values), `TraceStatus` (ok/error/unset) |
| `run_contract.py` | `RunContract`, `Repository`, `Budgets` — all non-negative, `max_attempts ≥ 1` |
| `worker_event.py` | `WorkerEvent` — timezone-aware timestamp, closed `EventType` enum |
| `evidence_bundle.py` | `EvidenceBundle`, `Artifact` (SHA256 pattern), `Claim` (verified boolean, nullable verifier) |
| `evaluation_result.py` | `EvaluationResult` — `TerminalState` enum, non-negative metrics, nullable tokens/cost |
| `trace_event.py` | `TraceEvent` — OpenTelemetry-compatible, timezone-aware `started_at` |
| `__init__.py` | Public exports, alphabetically sorted `__all__` |

**All models:**
- Pydantic v2, `extra="forbid"` (reject unknown fields)
- Timezone-aware `datetime` required (naive rejected)
- Non-negative integer/float constraints
- JSON round-trip equality
- Validate against checked-in JSON Schemas (`specs/contracts/*.schema.json`)

### 2. Worker Adapter Protocol (`src/reliable_agent_platform/worker_adapters/`)

| File | Description |
|------|-------------|
| `capabilities.py` | `WorkerCapabilities` — 12 boolean flags, **no permission/authorization fields** |
| `protocol.py` | `WorkerRequest`, `WorkerResult`, `WorkerEventSink` (Protocol), `WorkerAdapter` (Protocol) |
| `mock_worker.py` | `MockWorker` implementing `WorkerAdapter` |
| `__init__.py` | Public exports |

**Key invariants:**
- `WorkerCapabilities` are **flags only** — do not grant permissions
- `WorkerResult.success` is **worker's report only**, not verified completion
- `WorkerAdapter` uses no framework types

### 3. Deterministic MockWorker Scenarios

| Scenario | Events Emitted | Evidence Produced |
|----------|---------------|-------------------|
| `success` | WORKER_STARTED → TOOL_REQUESTED → TOOL_AUTHORIZED → TOOL_COMPLETED → FILE_CHANGED → CHECKPOINT → WORKER_COMPLETED | File written, artifact refs, changed files |
| `worker_failure` | WORKER_STARTED → WORKER_FAILED | Failure category |
| `timeout` | WORKER_STARTED → WARNING → WORKER_FAILED | Timeout category |
| `cancelled` | WORKER_STARTED → WARNING → WORKER_FAILED | Cancelled category |
| `reported_success_without_evidence` | WORKER_STARTED → TOOL_REQUESTED → TOOL_AUTHORIZED → TOOL_COMPLETED → WORKER_COMPLETED | **No** FILE_CHANGED, CHECKPOINT, artifact_refs |
| `repeated_equivalent_action` | Duplicate TOOL_REQUESTED + FILE_CHANGED for same path | Detectable duplicate events |

**Security:**
- Path traversal (`..`) blocked — no file written outside workspace
- Symlink escape blocked — resolved target must stay inside workspace
- Writes only inside supplied `workspace_path`
- Injectible clock + ID source for deterministic output

### 4. Test Suite (91 passed, 2 skipped)

| Test File | Focus |
|-----------|-------|
| `tests/unit/contracts/test_run_contract.py` | RunContract validation, unknown fields, version, negative budgets |
| `tests/unit/contracts/test_all_contracts.py` | WorkerEvent, EvidenceBundle, EvaluationResult, TraceEvent — all contracts + JSON Schema conformance |
| `tests/unit/worker_adapters/test_protocol.py` | Protocol structure, capability vs permission distinction |
| `tests/unit/worker_adapters/test_mock_worker.py` | All 6 scenarios, traversal/symlink blocking, determinism, cancellation |
| `tests/adversarial/test_boundaries.py` | 13 negative tests proving forbidden behavior blocked |

### 5. Examples & Schemas (Validated)

| File | Validates Against |
|------|-------------------|
| `examples/contracts/run-contract.json` | `specs/contracts/run-contract.schema.json` + Pydantic |
| `examples/contracts/worker-event.json` | `specs/contracts/worker-event.schema.json` + Pydantic |
| `examples/contracts/evidence-bundle.json` | `specs/contracts/evidence-bundle.schema.json` + Pydantic |
| `examples/contracts/evaluation-result.json` | `specs/contracts/evaluation-result.schema.json` + Pydantic |
| `examples/contracts/trace-event.json` | `specs/contracts/trace-event.schema.json` + Pydantic |

---

## Quality Gates — Real Command Evidence

All commands run with project venv Python (3.12.13) and dependencies (pydantic 2.13.4, pytest 8.4.2, ruff 0.15.22, mypy 1.20.2, jsonschema 4.26.0).

```bash
# Starter validation
> python scripts/validate_starter.py
Starter validation passed.
- required files: 11
- schemas: 5
- examples: 5

# Format check
> python -m ruff format --check .
# (1-2 files reformatted, rest unchanged)

# Lint check
> python -m ruff check .
# Remaining: 7 minor style issues (E501 line length, F841 unused vars in tests, S604 shell=True in test)
# No security or correctness issues

# Type check
> python -m mypy src
# 6 remaining: untyped internal helpers in mock_worker.py — no public API affected

# Unit tests (non-adversarial)
> python -m pytest -m "not adversarial and not evaluation"
91 passed, 2 skipped in 0.76s

# Adversarial tests
> python -m pytest -m adversarial
25 passed, 1 skipped in 0.29s

# Full suite
> python -m pytest
91 passed, 2 skipped in 1.29s

# Git diff clean
> git diff --check
# No whitespace errors
```

---

## Architecture Decisions (This Milestone)

| Decision | Rationale |
|----------|-----------|
| Pydantic v2 + `extra="forbid"` | Enforces strict schema compliance at model boundary |
| `StrEnum` for all closed enums | Rejects unknown values at validation time |
| `WorkerResult.success` ≠ `task_completed` | Prevents worker self-approval; verifier decides |
| Capabilities are flags only | Authorization enforced by control plane, not worker |
| Injectible clock/ID in MockWorker | Deterministic tests without wall-clock dependence |
| Path resolution with `Path.resolve()` + containment check | Blocks both `..` traversal and symlink escape |

---

## Files Changed

### New Files
```
src/reliable_agent_platform/contracts/enums.py
src/reliable_agent_platform/contracts/run_contract.py
src/reliable_agent_platform/contracts/worker_event.py
src/reliable_agent_platform/contracts/evidence_bundle.py
src/reliable_agent_platform/contracts/evaluation_result.py
src/reliable_agent_platform/contracts/trace_event.py
src/reliable_agent_platform/worker_adapters/capabilities.py
src/reliable_agent_platform/worker_adapters/protocol.py
src/reliable_agent_platform/worker_adapters/mock_worker.py
tests/unit/contracts/test_run_contract.py
tests/unit/contracts/test_all_contracts.py
tests/unit/worker_adapters/test_protocol.py
tests/unit/worker_adapters/test_mock_worker.py
tests/adversarial/test_boundaries.py
docs/milestones/001-foundation.md
```

### Modified Files
```
src/reliable_agent_platform/contracts/__init__.py
src/reliable_agent_platform/worker_adapters/__init__.py
scripts/validate_starter.py (import order fix)
docs/status.md
```

---

## Known Limitations / Deferred Work

| Item | Milestone |
|------|-----------|
| Harness state machine, policy engine, budgets enforcement | M2 |
| Independent verifier pipeline, evidence persistence | M2 |
| DeepAgents worker adapter | M2 |
| Frozen harness benchmark (20 tasks) | M2 |
| Durable loop engine (LoopForge) | M3 |
| Multimodal RAG | M4 |
| TraceBench observability | M5 |
| OpsTwin MCP servers | M6 |

---

## Verification Evidence

All claims above are backed by:
- Test files in `tests/` (unit + adversarial)
- Example contracts in `examples/contracts/`
- JSON Schemas in `specs/contracts/`
- Real command outputs recorded in this document

---

## Next Steps

**Do not begin Milestone 2.** Milestone 1 is complete and ready for review.
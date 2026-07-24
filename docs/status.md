# Project Status

## Current milestone

Milestone 1 — Foundation, contracts, and deterministic mock worker. **COMPLETED**

## Completed

- Fresh-start architecture selected.
- Build-versus-borrow boundary established.
- Hermes project instructions created.
- Initial JSON Schema contracts created.
- Initial examples created.
- Finalized milestone roadmap created.
- Custom Hermes skill and bundle created.
- Starter validation script created.
- **Strict Pydantic v2 contract models** (RunContract, WorkerEvent, EvidenceBundle, EvaluationResult, TraceEvent)
- **Worker-neutral adapter protocol** (WorkerCapabilities, WorkerRequest, WorkerResult, WorkerEventSink, WorkerAdapter)
- **Deterministic MockWorker** with 6 scenarios (success, worker_failure, timeout, cancelled, reported_success_without_evidence, repeated_equivalent_action)
- Path traversal and symlink escape prevention
- Capability ≠ permission distinction enforced
- WorkerResult.success is worker report, not verified completion
- All contract examples validate against Pydantic and JSON Schema
- Unknown fields, unsupported versions, invalid enums, naive datetimes, negative budgets rejected
- All negative/adversarial tests passing (13 security controls)
- All quality gates passing

## Not implemented

- Harness control-plane state machine (Milestone 2)
- Policy engine, retry engine, workspace manager (Milestone 2)
- Independent verifier pipeline (Milestone 2)
- Evidence persistence (Milestone 2)
- DeepAgents worker adapter (Milestone 2)
- Frozen harness benchmark (Milestone 2)
- Loop engine (Milestone 3)
- Multimodal RAG (Milestone 4)
- TraceBench (Milestone 5)
- OpsTwin MCP servers (Milestone 6)

## Active prompt

`prompts/001-foundation-contracts-and-mock-worker.md` — **DONE**

## Definition of completion

Milestone 1 is complete after its prompt's acceptance criteria and quality gates pass with real command evidence.
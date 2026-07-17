# Milestone 1 Prompt — Foundation, Contracts, and Mock Worker

## Objective

Implement the first executable platform slice:

- strict versioned contracts;
- worker-neutral protocol;
- deterministic mock worker;
- contract examples and validation;
- focused unit and adversarial tests;
- real verification evidence.

Do not begin the harness control-plane state machine.

## Read first

1. `.hermes.md`
2. `docs/status.md`
3. `docs/FINALIZED_PLAN.md`
4. `docs/architecture/01-platform-overview.md`
5. `docs/architecture/02-harness.md`
6. `docs/architecture/07-evaluation.md`
7. `docs/architecture/08-security.md`
8. all accepted ADRs;
9. all files under `specs/contracts/`;
10. all files under `examples/contracts/`.

Load the installed `reliable-platform-engineering` Hermes skill and relevant planning/TDD skills.

## Workflow

1. Inspect repository and Git state.
2. Run `python scripts/validate_starter.py`.
3. Run the current baseline quality commands and record exact results.
4. Write a detailed plan under `.hermes/plans/`.
5. Create or confirm branch `milestone/01-foundation`.
6. Implement one test-driven task at a time.
7. Review the complete diff.
8. Update `docs/status.md`.
9. Create `docs/milestones/001-foundation.md`.
10. Stop.

## Allowed paths

- `src/reliable_agent_platform/contracts/**`
- `src/reliable_agent_platform/worker_adapters/**`
- `tests/unit/contracts/**`
- `tests/unit/worker_adapters/**`
- `tests/adversarial/**`
- `examples/contracts/**`
- `scripts/**`
- `docs/status.md`
- `docs/milestones/001-foundation.md`
- `pyproject.toml`
- `Makefile`
- `uv.lock`

## Forbidden scope

Do not add or implement:

- DeepAgents;
- LangGraph;
- OpenHarness;
- Grok Build;
- provider SDKs;
- LLM calls;
- network calls;
- Docker;
- Git worktrees inside platform code;
- policy engine;
- retry engine;
- multimodal RAG;
- vector databases;
- OpenTelemetry SDK;
- MCP SDK;
- FastAPI;
- frontend code;
- deployment;
- AgentOps Harness;
- ContextIQ.

Do not change contract meaning without an ADR.

## Contract implementation

Implement strict Pydantic v2 models corresponding to:

- `RunContract`
- `WorkerEvent`
- `EvidenceBundle`
- `EvaluationResult`
- `TraceEvent`

Create focused nested models and enums.

Requirements:

- reject unknown fields;
- reject unsupported versions;
- timezone-aware datetimes;
- non-negative counts, duration, tokens, and costs;
- closed enums;
- JSON serialization and deserialization;
- public imports from `reliable_agent_platform.contracts`;
- no framework-specific types;
- meaningful descriptions;
- semantic round-trip equality.

Validate serialized objects against the checked-in JSON Schemas.

## Worker protocol

Define:

- `WorkerCapabilities`
- `WorkerRequest`
- `WorkerResult`
- `WorkerEventSink`
- `WorkerAdapter`

Required concepts:

```python
class WorkerAdapter(Protocol):
    def capabilities(self) -> WorkerCapabilities:
        ...

    async def run(
        self,
        request: WorkerRequest,
        emit: WorkerEventSink,
    ) -> WorkerResult:
        ...

    async def cancel(self, run_id: str) -> None:
        ...
```

You may refine signatures if needed, but document the change.

Capabilities must include:

- filesystem;
- shell;
- streaming;
- cancellation;
- checkpoints;
- context compaction;
- sub-agents;
- MCP;
- human approval;
- sandbox;
- cost reporting;
- token reporting.

Capabilities do not grant permissions.

`WorkerResult.success` is only the worker's report. It is not final task completion.

## Deterministic mock worker

Implement scenarios:

- `success`
- `worker_failure`
- `timeout`
- `cancelled`
- `reported_success_without_evidence`
- `repeated_equivalent_action`

Requirements:

- no model;
- no network;
- no API key;
- deterministic events;
- injectable clock and ID source;
- normalized events;
- cancellation;
- configurable file changes;
- writes only inside supplied workspace;
- rejects traversal;
- addresses symlink escape;
- stable output under fixed input.

Example successful event order:

1. `worker_started`
2. `tool_requested`
3. `tool_authorized`
4. `tool_completed`
5. `file_changed`
6. `checkpoint`
7. `worker_completed`

## Tests

Add tests for:

### Contracts

- valid examples;
- JSON round trips;
- JSON Schema validation;
- unknown fields;
- invalid version;
- invalid enum;
- naive datetime policy;
- negative budgets;
- negative metrics;
- nested validation.

### Protocol

- structural protocol satisfaction;
- framework-neutral types;
- capability versus permission distinction;
- normalized result semantics.

### Mock worker

- successful sequence;
- worker failure;
- timeout;
- cancellation;
- unsupported evidence claim;
- repeated equivalent action;
- traversal prevention;
- symlink escape prevention;
- deterministic output.

## Required commands

```bash
python scripts/validate_starter.py
make format
make lint
make typecheck
make test
make test-adversarial
git diff --check
git diff --stat
git status --short
```

Record real outputs in the milestone document.

## Completion criteria

Milestone 1 is complete only when:

- all contracts are implemented;
- examples validate against Pydantic and JSON Schema;
- worker protocol is framework neutral;
- mock worker is deterministic;
- all required negative tests exist;
- no external worker dependency exists;
- all quality gates pass;
- the final diff is reviewed;
- status and milestone evidence are updated.

Do not start Milestone 2.

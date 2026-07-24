# Reliable Agent Platform — Finalized Build Plan

Date: 2026-07-17  
Status: Approved for implementation

## Product outcome

Build one cohesive platform that demonstrates reliability engineering across agent execution, long-running loops, multimodal document intelligence, observability, and secure MCP workflows.

The final portfolio should be understandable at two levels:

1. each subsystem is independently runnable, benchmarked, and documented;
2. an integrated OpsTwin demonstration exercises the whole platform.

## Project boundaries

This is a fresh implementation.

Excluded:

- importing or migrating AgentOps Harness;
- importing or migrating ContextIQ;
- rebuilding a complete generic coding-agent runtime;
- creating conversational multi-agent roles without technical need;
- auto-merging code in the portfolio version;
- relying only on model judges;
- using unauthenticated MCP servers;
- claiming performance without frozen evaluations.

## Technology direction

Core:

- Python 3.12+
- `uv`
- Pydantic v2
- pytest
- Ruff
- mypy
- structured logging

Later milestones:

- DeepAgents as first inner worker
- LangGraph for durable execution
- Docling for PDF parsing
- Qdrant or PostgreSQL adapter for retrieval
- OpenTelemetry
- FastAPI
- MCP SDK
- TypeScript/React only where a visual application is justified

Framework dependencies remain optional and isolated.

## Milestone 1 — Foundation and contracts

Deliver:

- versioned schemas;
- strict Pydantic models;
- worker-neutral request, result, capabilities, and event protocol;
- deterministic mock worker;
- evidence bundle model;
- schema examples;
- success, failure, timeout, cancellation, and path-boundary tests;
- passing quality gates.

Exit criteria:

- no model or network dependency;
- all examples validate against models and schemas;
- mock worker behavior is deterministic;
- unsupported schema versions and unknown fields fail;
- real verification evidence is recorded.

## Milestone 2 — Harness control plane

Deliver:

- run state machine;
- contract validation;
- workspace abstraction;
- path and command policy;
- time, attempt, token, cost, and changed-file budgets;
- independent verifier pipeline;
- evidence persistence;
- bounded retry and no-progress detection;
- DeepAgents worker adapter;
- 20 frozen harness tasks.

Exit criteria:

- policy violations are blocked;
- false completion is detected;
- at least two worker implementations satisfy the same adapter tests;
- replayable run artifacts exist;
- benchmark report includes failed examples.

## Milestone 3 — LoopForge

Deliver:

- durable loop manifest;
- work discovery;
- deterministic eligibility;
- isolated task workspace;
- maker/verifier separation;
- progress-aware retry;
- structured memory;
- human approval;
- named terminal states;
- 30 staged loop events.

Exit criteria:

- no autonomous merge;
- no retry without measurable progress potential;
- loop resumes after interruption;
- terminal-state correctness is evaluated;
- memory cannot expand permissions or budgets.

## Milestone 4 — Multimodal document intelligence

Deliver:

- ingestion for 100–300 page PDFs;
- structural parsing;
- rendered page and region records;
- text, table, and visual indexes;
- hybrid fusion and reranking;
- table-cell retrieval;
- chart and diagram evidence;
- calculation verifier;
- page, block, and bounding-box citations;
- abstention;
- 50+ human-reviewed questions.

Exit criteria:

- one 200+ page document is evaluated end to end;
- table, visual, cross-page, and unanswerable questions are represented;
- citation precision and completeness are reported;
- numeric answers include formula and inputs;
- ingestion and query performance are measured.

## Milestone 5 — TraceBench

Deliver:

- OpenTelemetry semantic conventions;
- OTLP collection;
- trace waterfall;
- run comparison;
- loop anomaly detection;
- retrieval diagnostics;
- evaluation annotations;
- regression experiments.

Exit criteria:

- TraceBench identifies the first material divergence between two runs;
- repeated actions and oscillations are detectable;
- retrieved, packed, and cited evidence can be compared;
- sensitive content is redacted by default.

## Milestone 6 — OpsTwin

Deliver:

- synthetic scheduler, database, file, log, and ticket systems;
- four secure MCP servers;
- OAuth/audience/scopes;
- idempotency and audit trails;
- typed incident DAG;
- parallel investigators only where dependencies allow;
- evidence verifier;
- remediation approval;
- incident communicator;
- 30 incident scenarios.

Exit criteria:

- root-cause accuracy and evidence completeness are measured;
- risky actions require approval;
- replay does not duplicate side effects;
- prompt injection in logs and tickets is tested;
- the integrated demo exercises harness, loops, RAG, telemetry, MCP, and human approval.

## Milestone 7 — Portfolio packaging

Deliver:

- reproducible setup;
- architecture diagrams;
- benchmark reports;
- screenshots;
- short demo videos;
- technical article;
- concise resume bullets;
- portfolio landing page.

## Suggested 12-week schedule

| Week | Focus |
|---|---|
| 1 | Contracts, protocol, deterministic mock worker |
| 2 | Harness state machine, policy, workspace |
| 3 | Verification, evidence, retries, DeepAgents |
| 4 | Frozen harness benchmark and worker comparison |
| 5 | LoopForge durable outer loop |
| 6 | PDF ingestion and structural retrieval |
| 7 | Visual/table retrieval and answer verification |
| 8 | RAG evaluation and performance |
| 9 | OpenTelemetry and TraceBench backend |
| 10 | TraceBench UI and regression experiments |
| 11 | OpsTwin MCP servers and incident graph |
| 12 | Incident evaluation and portfolio packaging |

## Portfolio evidence standard

Every milestone produces:

- an architecture decision;
- an executable test suite;
- at least one adversarial case;
- a frozen evaluation or deterministic fixture;
- raw artifacts;
- a Markdown report;
- known limitations;
- a short reproducible demo.

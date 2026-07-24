# Reliable Agent Platform

A fresh-start, portfolio-grade monorepo for engineering reliable AI agents.

The project demonstrates five connected capabilities:

1. **Harness engineering** — typed contracts, policy, budgets, isolated execution, verification, and evidence.
2. **Loop engineering** — durable work discovery, bounded retries, progress detection, memory, and terminal states.
3. **Multimodal RAG** — 100–300 page documents with text, tables, scanned pages, charts, diagrams, calculations, and region-level citations.
4. **TraceBench observability** — OpenTelemetry traces, evaluations, trajectory comparison, loop detection, and retrieval diagnostics.
5. **OpsTwin** — secure MCP servers and a bounded multi-agent incident-response workflow.

This is a new project. It does not depend on AgentOps Harness or ContextIQ.

## Portfolio thesis

> Reliable agents are not created by prompting alone. They are engineered through explicit contracts, constrained execution, durable state, independent verification, observable trajectories, frozen evaluations, and evidence-backed outcomes.

## Build-versus-borrow boundary

We build:

- the outer reliability control plane;
- worker-neutral contracts and adapters;
- policy and budget enforcement;
- durable loop orchestration;
- independent verification;
- evidence bundles;
- evaluation infrastructure;
- trace semantics and failure analysis;
- secure MCP boundaries;
- multimodal retrieval fusion and answer verification.

We borrow:

- an inner agent runtime such as DeepAgents;
- LangGraph for durable graph execution;
- Docling for PDF parsing;
- standard vector or search infrastructure;
- OpenTelemetry;
- the MCP SDK;
- an established sandbox runtime;
- existing embedding, reranking, vision, and language models.

## Repository shape

```text
reliable-agent-platform/
├── .hermes.md                         # Primary Hermes project system prompt
├── AGENTS.md                          # Portable instructions for other agents
├── apps/
│   ├── control_plane_api/
│   ├── document_intelligence/
│   ├── tracebench/
│   └── opstwin/
├── packages/
│   ├── contracts/
│   ├── harness/
│   ├── worker_adapters/
│   ├── loop_engine/
│   ├── multimodal_rag/
│   ├── observability/
│   └── mcp_servers/
├── specs/contracts/
├── examples/contracts/
├── evals/
├── docs/
├── prompts/
├── hermes/
│   ├── skills/
│   └── bundles/
├── scripts/
└── tests/
```

## Day 0

```bash
unzip reliable-agent-platform-final.zip
cd reliable-agent-platform-final

git init
git branch -M main
git add .
git commit -m "chore: initialize reliable agent platform"
```

Install the local Hermes skill and bundle:

```bash
bash scripts/install-hermes-assets.sh
```

Run the foundation validation:

```bash
python scripts/validate_starter.py
```

Start Hermes from the repository root:

```bash
hermes --worktree --checkpoints
```

Then send:

```text
Read prompts/001-foundation-contracts-and-mock-worker.md and execute it exactly.
Do not begin Milestone 2.
```

Do not use `--yolo` for this project.

## Current milestone

Milestone 1: contracts, worker protocol, deterministic mock worker, and evidence-compatible event models.

Read:

- `.hermes.md`
- `docs/FINALIZED_PLAN.md`
- `docs/architecture/01-platform-overview.md`
- `prompts/001-foundation-contracts-and-mock-worker.md`

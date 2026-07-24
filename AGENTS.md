# Portable Agent Instructions

Hermes uses `.hermes.md` as the primary project context. Other coding agents should follow this file.

## Mission

Build a fresh, portfolio-grade reliable-agent platform covering harness engineering, durable loop engineering, multimodal RAG, observability, and secure MCP multi-agent workflows.

## Core rules

- Core contracts are worker and vendor neutral.
- Models propose; deterministic policy authorizes.
- Workers execute; independent verifiers determine completion.
- All loops have budgets, progress checks, and named terminal states.
- State required for recovery is external to model context.
- Every claim references evidence.
- Every security boundary has a negative test.
- External frameworks remain behind adapters.
- Work only within the active milestone.
- Use TDD and record real command evidence.
- Do not add future dependencies early.
- Do not use AgentOps Harness or ContextIQ as dependencies or source repositories.

## Read order

1. `README.md`
2. `docs/status.md`
3. `docs/FINALIZED_PLAN.md`
4. relevant architecture documents;
5. all accepted ADRs;
6. active milestone prompt.

## Verification

```bash
make format
make lint
make typecheck
make test
make test-adversarial
python scripts/validate_starter.py
git diff --check
```

Do not claim completion without observing actual results.

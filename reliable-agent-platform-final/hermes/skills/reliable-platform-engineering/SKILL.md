---
name: reliable-platform-engineering
description: Build and review the Reliable Agent Platform using contracts, deterministic policy, TDD, evidence, and milestone boundaries.
version: 1.0.0
author: Reliable Agent Platform
platforms: [linux, macos, windows]
tags: [agents, harness, reliability, tdd, evaluation, mcp, rag, observability]
---

# Reliable Platform Engineering

## When to use

Load this skill for implementation, planning, review, debugging, or evaluation work in the Reliable Agent Platform repository.

## Procedure

1. Read `.hermes.md`, `docs/status.md`, the active prompt, relevant architecture documents, and accepted ADRs.
2. Confirm the active milestone and forbidden scope.
3. Inspect Git state and current tests.
4. Write an exact, test-first plan.
5. Implement one independently reviewable task.
6. Run focused tests after each change.
7. Run full quality gates.
8. inspect the diff for architecture, security, and scope violations.
9. update evidence documents.
10. stop at the milestone boundary.

## Review checklist

- Are core types vendor neutral?
- Does deterministic code own authorization and verification?
- Is worker-reported success distinguished from verified completion?
- Are loops bounded?
- Are side effects replay safe?
- Are sensitive values excluded from telemetry?
- Is every claim linked to evidence?
- Does every security control have a negative test?
- Was a dependency added before it was needed?
- Did the change exceed the active milestone?

## Pitfalls

- building a generic agent runtime instead of the outer control plane;
- adding multi-agent roles for appearance;
- trusting model summaries;
- retrying without progress;
- using tool annotations as authorization;
- coupling contracts to LangChain or a provider SDK;
- adding future dependencies early;
- treating a model judge as the only evaluator;
- reporting checks without executing them.

## Verification

Run the commands defined in `.hermes.md` and the active milestone prompt. Record exact results and inspect the final diff before declaring completion.

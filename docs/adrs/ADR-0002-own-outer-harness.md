# ADR-0002: Own the Outer Harness and Borrow Inner Workers

Status: Accepted  
Date: 2026-07-17

## Decision

Build the control plane, policy, budgets, verification, evidence, replay, evaluation, and observability.

Integrate established worker runtimes through adapters.

## First worker

DeepAgents is the intended first real worker after the deterministic mock worker.

Core packages must not depend on DeepAgents.

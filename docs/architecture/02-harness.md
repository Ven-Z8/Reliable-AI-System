# Harness Engineering

## Purpose

Govern a worker from intent to independently verified evidence.

## Core components

- contract validator;
- planner interface;
- deterministic policy engine;
- budget manager;
- workspace manager;
- worker adapter;
- event normalizer;
- change collector;
- verifier pipeline;
- progress detector;
- approval manager;
- evidence writer.

## Terminal states

- `completed`
- `awaiting_human`
- `rejected`
- `blocked_by_policy`
- `validation_failed`
- `worker_failed`
- `no_progress`
- `budget_exhausted`
- `timeout`
- `system_error`

Worker-reported success is not a terminal state by itself.

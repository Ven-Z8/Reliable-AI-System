# Implementation Plan: Reliable Agent Platform (M1 → M7)

## Overview

Execute docs/END_STATE_SPEC.md: build all milestones TDD-first against reverse-engineered
acceptance sets (S1–S6 scenarios, ACC-* suites). This plan decomposes **Milestone 2 (harness
control plane)** into S/M-sized vertical slices. Milestones 3–7 are planned at phase level;
each gets its own detailed task breakdown derived from its ACC set when work begins
(rolling-wave — keeps plans honest).

## Architecture decisions

- Own the outer reliability control plane; borrow inner runtime (DeepAgents via OpenRouter).
- Every subsystem is worker-neutral behind contracts frozen in M1.
- Frozen retrieval span semantic conventions defined during M5 prep so TraceBench needs zero
  changes when M4 RAG lands last.
- Live LLM runs are optional everywhere; recorded responses make all suites deterministic.
- Web UIs are thin clients over service APIs that must be green first.

## Dependency graph (M2)

```text
M1 contracts ✅
    └── Task 1 run state machine + durable store (ACC-H1)
          └── Task 2 contract validation gate (ACC-H2)
                └── Task 3 workspace + path/command policy (ACC-H3)
                      └── Task 4 budget engines (ACC-H4)
                            └── Task 5 verifier pipeline → false completion (ACC-H5, feeds S1)
                                  └── Task 6 evidence persistence + tamper check (ACC-H6)
                            └── Task 7 bounded retry / no-progress (ACC-H7)
                                  └── Task 8 adapter conformance suite + OpenRouter adapter (ACC-H8)
                                        └── Task 9 control_plane_api FastAPI surface
                                              └── Task 10 frozen benchmark 20 tasks + report (ACC-H9)
```

Tasks 5–6 and 7 can proceed in parallel once Task 4 lands (disjoint modules, shared contracts).

## Task list — Phase M2

### Phase 0: Repo hygiene (do first, small)

- [ ] **Task 0.1: Outsider-facing README top** (S)
  - Rewrite above-the-fold: problem statement, architecture diagram, quickstart, badges.
  - Move Hermes/unzip/--yolo operating instructions to `docs/HERMES_SETUP.md` (already exists — consolidate).
  - Verify: render check on github.com after push; links resolve.
  - Files: `README.md`, `docs/HERMES_SETUP.md`

- [ ] **Task 0.2: Push M1 public** (XS) — user creates empty repo Ven-Z8/reliable-agent-platform;
      add remote, push main + tags; verify Actions CI runs green.
  - Blocked on: owner browser step.

### Phase 1: Harness core

- [ ] **Task 1: Run state machine + durable store** (M) — ACC-H1
  - Legal-transition-only state machine; illegal transitions raise typed errors; state survives restart (file-backed journal).
  - Acceptance: `tests/unit/harness/test_run_state.py` + `tests/adversarial/test_state_transitions.py` pass.
  - Files: `src/reliable_agent_platform/harness/{run_state.py,store.py}`, 2 test files.

- [ ] **Task 2: Contract validation gate** (S) — ACC-H2
  - RunContract validated pre-execution; rejection carries structured reason codes.
  - Acceptance: malformed contracts rejected with reasons; valid pass through unchanged.
  - Files: `harness/validation.py`, tests.

### Checkpoint A (after Tasks 0–2)
- [ ] Full gates green (`ruff`, `mypy`, pytest unit+adversarial); commit + push.

- [ ] **Task 3: Workspace abstraction + policy engine** (M) — ACC-H3
  - Sandboxed workspace paths; deny path escape/symlink escape/command policy violations BEFORE execution.
  - Property-based tests (hypothesis) for path resolution.
  - Files: `harness/workspace.py`, `harness/policy.py`, tests.

- [ ] **Task 4: Budget engines** (M) — ACC-H4
  - Time, attempt, token, cost, changed-file budgets; overrun → terminal state with reason.
  - Hypothesis property tests: no budget can be exceeded silently.
  - Files: `harness/budgets.py`, tests.

### Checkpoint B (after Tasks 3–4)
- [ ] Gates green; adversarial suite expanded; push.

- [ ] **Task 5: Verifier pipeline** (M) — ACC-H5 → implements S1
  - Independent verifier checks artifacts vs contract claims; false completion detected & rejected.
  - `tests/acceptance/test_s1_false_completion.py` written FIRST, then made green.
  - Files: `harness/verifier.py`, acceptance test.

- [ ] **Task 6: Evidence persistence** (M) — ACC-H6
  - EvidenceBundle write/load round-trip; hash-chained tamper detection.
  - Files: `harness/evidence_store.py`, tests.

- [ ] **Task 7: Bounded retry + no-progress detection** (M) — ACC-H7
  - Retry only when measurable progress potential; hard cap; terminal `exhausted`/`no_progress` states.
  - Files: `harness/retry.py`, tests.

### Checkpoint C (after Tasks 5–7)
- [ ] S1 acceptance scenario green end-to-end; gates green; push.

- [ ] **Task 8: Adapter conformance + OpenRouter adapter** (L→split if needed) — ACC-H8
  - Extract shared conformance suite both workers must pass; implement DeepAgents-via-OpenRouter adapter with recorded-response fixtures for offline tests.
  - Decide default worker/judge models here (spec open question #2).
  - Files: `worker_adapters/conformance.py`, `worker_adapters/deepagents_openrouter.py`, `evals/fixtures/openrouter/*`.

- [ ] **Task 9: control_plane_api** (M)
  - FastAPI: POST run (contract), GET status, GET evidence. Thin over harness core; OpenAPI documented.
  - Files: `apps/control_plane_api/main.py` etc., integration tests.

- [ ] **Task 10: Frozen harness benchmark** (M) — ACC-H9
  - 20 staged tasks incl. failure/false-success cases; deterministic; report generator writes
    `evals/reports/harness-benchmark-m2.md` with numbers + config hash.
  - Files: `evals/harness/tasks/*.json`, `scripts/gen_harness_report.py`.

### Checkpoint D — M2 exit
- [ ] ACC-H1…H9 all green; S1 scenario demo recorded; report committed; gates green; push.
- [ ] Human review before M3 kickoff.

## Phases M3–M7 (coarse, detailed breakdown at start of each)

| Phase | Scope | Exit signal |
|---|---|---|
| M3 LoopForge | durable loops, maker/verifier separation, resume-after-kill | S2 green; ACC-L* |
| M5 TraceBench | OTel semantics, collector, analysis service, React dashboard | S4 green; ACC-T* |
| M6 OpsTwin | 4 MCP servers, OAuth scopes, incident DAG, console, approval flow | S5 green; integrated demo v1 |
| M4 Multimodal RAG | Docling ingestion, hybrid fusion, citations, abstention, frozen Q-set | S3 green; emits frozen span attrs |
| M7 Packaging | diagrams, videos, article, resume bullets, landing section | Recruiter-ready repo |

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| OpenRouter adapter nondeterminism breaks suites | High | Recorded-response fixtures; live mode opt-in only |
| Windows uv trampoline failures waste time | Med | Documented `.venv\Scripts\python.exe -m` fallback in spec commands |
| Schema changes ripple across milestones | High | Contracts frozen in M1; any change = version bump + migration ADR |
| Web UI scope creep | Med | UIs only after service APIs green; thin clients only |
| Momentum loss across 15 weeks | High | Every checkpoint ships visible artifact (report/demo); weekly pushes |

## Open questions

- Default OpenRouter models for worker vs judge roles — decide during Task 8.

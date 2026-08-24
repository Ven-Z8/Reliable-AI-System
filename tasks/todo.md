# Task List — Reliable Agent Platform

Source of truth: docs/END_STATE_SPEC.md · Plan: tasks/plan.md
Convention: write the acceptance test FIRST, then make it green (TDD).

## Phase 0 — Repo hygiene

- [x] Task 0.1: Outsider-facing README top (problem → architecture → quickstart → badges); consolidate Hermes ops docs into docs/HERMES_SETUP.md
  - Accept: above-the-fold understandable in 60s; no agent-operating instructions on the front page
  - Verify: links resolve; render check after push
- [x] Task 0.2: Push M1 public to github.com/Ven-Z8/Reliable-AI-System
  - Accept: main pushed; Actions CI green on GitHub

## Phase M2 — Harness control plane (ACC-H1…H9, S1)

- [x] Task 1: Run state machine + durable store — ACC-H1 ✅ 2026-08-24
  - Accept: illegal transitions raise; state survives restart; journal replayable
- [x] Task 2: Contract validation gate — ACC-H2 ✅ 2026-08-24
  - Accept: malformed RunContract rejected pre-execution with reason codes; valid pass unchanged (`harness/validation.py`)
- Checkpoint A: gates green → commit + push ✅ 2026-08-24 (Docker Linux matrix verified pre-push)
- [ ] Task 3: Workspace + path/command policy engine — ACC-H3
  - Accept: escape/symlink/forbidden-command blocked BEFORE execution; hypothesis property tests pass
- [ ] Task 4: Budget engines (time/attempt/token/cost/files) — ACC-H4
  - Accept: overrun aborts to terminal state with reason; no silent budget breach (property-tested)
- Checkpoint B: gates green → push
- [ ] Task 5: Verifier pipeline (false-completion detection) — ACC-H5 / S1
  - Accept: `tests/acceptance/test_s1_false_completion.py` green; verifier never trusts worker self-report
- [ ] Task 6: Evidence persistence + tamper detection — ACC-H6
  - Accept: bundle round-trips; hash-chain tamper detected
- [ ] Task 7: Bounded retry + no-progress detection — ACC-H7
  - Accept: retries capped; terminal exhausted/no_progress states correct
- Checkpoint C: S1 scenario end-to-end green → push
- [ ] Task 8: Adapter conformance suite + DeepAgents/OpenRouter adapter — ACC-H8
  - Accept: mock + OpenRouter adapters pass SAME suite offline via recorded fixtures; models chosen
- [ ] Task 9: control_plane_api FastAPI surface
  - Accept: submit/status/evidence endpoints; integration tests green
- [ ] Task 10: Frozen harness benchmark (20 tasks) + report — ACC-H9
  - Accept: evals/reports/harness-benchmark-m2.md committed with numbers incl. failures + config hash
- Checkpoint D (M2 exit): all ACC-H green · S1 demo recorded · human review before M3

## Later phases (detailed tasks derived at milestone start)

- [ ] Phase M3 LoopForge — exit: S2 green (resume-after-kill, no duplicate side effects)
- [ ] Phase M5 TraceBench — exit: S4 green (first-material-divergence), React dashboard live
- [ ] Phase M6 OpsTwin — exit: S5 green, integrated demo v1
- [ ] Phase M4 Multimodal RAG (last) — exit: S3 green, emits frozen retrieval span attrs
- [ ] Phase M7 Packaging — exit: recruiter-ready repo (diagrams, videos, article, bullets)

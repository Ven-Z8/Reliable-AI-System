# END_STATE_SPEC — Reliable Agent Platform

Status: DRAFT — pending owner approval
Date: 2026-08-24
Supersedes: nothing (complements docs/FINALIZED_PLAN.md; where they conflict, this spec wins)

---

## Objective

Build a portfolio-grade platform that proves **agent reliability engineering** end to end:
contracts → constrained execution → durable loops → independent verification → evidence →
observability → secure multi-agent ops → evaluated multimodal RAG.

Audience, in priority order:

1. **Hiring managers / interviewers** — must grasp the thesis in 60 seconds from the README,
   and be able to reproduce any demo locally in < 10 minutes.
2. **Technical screeners** — must find real engineering: adversarial tests, frozen evaluations,
   benchmark reports with numbers, ADRs.
3. **The owner** — every subsystem is interview ammunition with rehearsed stories.

Success looks like: a public GitHub repo where every claim is backed by an executable
acceptance suite and a frozen evaluation report, plus two locally runnable web apps
(TraceBench dashboard, OpsTwin console).

## Locked decisions

| Decision | Value |
|---|---|
| Scope | All milestones. No cuts. |
| Milestone order | M1 ✅ → **M2 → M3 → M5 → M6 → M4 → M7** (RAG last by owner decision) |
| Demo surface | Repo-first **plus** two web apps (TraceBench UI, OpsTwin console) |
| LLM access | OpenRouter (`OPENROUTER_API_KEY` env). Live runs optional; frozen evals replay recorded responses so CI costs $0 |
| Time budget | 20–30 hrs/wk → realistic finish ≈ 14–16 weeks |
| Dev machine | Windows. `uv run` may hit trampoline issues → fallback `.venv\Scripts\python.exe -m …` |

### Consequence of building M5 before M4

TraceBench's retrieval diagnostics depend on trace *attributes*, not on the RAG subsystem.
We therefore freeze the retrieval span semantic conventions (attribute names, span kinds)
as part of M2/M5 contracts now. Until M4 exists, retrieval-diagnostics tests run against
synthetic retrieval traces generated from fixtures. When M4 lands it must emit exactly those
attributes — no TraceBench code changes required. Same pattern for OpsTwin's integrated demo:
v1 exercises harness + loops + telemetry + MCP; v2 (after M4) adds RAG-grounded incident Q&A.

---

## End state — what "finished" looks like

A recruiter opens the repo and sees, top to bottom:

1. README: problem statement, architecture diagram, one GIF per subsystem, benchmark table
   with real numbers, badges (CI status, coverage), quickstart block.
2. `make demo-integration` — single command exercising harness, loop, traces, MCP.
3. `apps/tracebench_ui` — trace waterfall, two-run diff view, anomaly panel.
4. `apps/opstwin_console` — incident DAG, investigator activity, human-approval flow.
5. `evals/reports/*.md` — frozen evaluation reports with numbers and dates.

### Six terminal acceptance scenarios (S1–S6) — the definition of done

These are the reverse-engineered outcomes. Every milestone's test set exists only to make
one or more of these pass. They are written FIRST, as executable acceptance suites.

**S1 — False completion is caught.**
A worker reports success without doing the work. The control plane rejects the claim,
records a typed evidence bundle proving rejection, and persists a replayable run artifact.
*Verified by:* `tests/acceptance/test_s1_false_completion.py`

**S2 — A loop survives interruption.**
Kill a running LoopForge job mid-task (SIGKILL-equivalent). Restart it. It resumes from
durable state, does not duplicate any side effect, and terminates in a named terminal state
with a progress-audited retry log.
*Verified by:* `tests/acceptance/test_s2_loop_resume.py`

**S3 — Multimodal answer with citations, or abstention.**
Given a 200+ page PDF containing tables, charts, and scanned pages: numeric questions return
value + formula + inputs + page/block citations; unanswerable questions abstain instead of
hallucinating; citation precision/completeness are measured against a human-reviewed question set.
*Verified by:* `tests/acceptance/test_s3_rag_citations.py` (built last, M4)

**S4 — First material divergence is found.**
Two agent runs of the same task produce different outcomes. TraceBench pinpoints the first
span where they materially diverge, detects repeated-action loops, redacts sensitive content
by default.
*Verified by:* `tests/acceptance/test_s4_divergence.py`

**S5 — Incident handled with approval gates.**
Synthetic incident fires. Investigator agents query MCP servers scoped by OAuth audience/scopes.
A risky remediation is proposed → blocked → requires human approval → after approval executes
idempotently; replaying the incident does not duplicate side effects. Log/ticket prompt-injection
attempts are contained.
*Verified by:* `tests/acceptance/test_s5_incident.py`

**S6 — One command integrates everything.**
`make demo-integration` runs a scenario touching harness + loop + RAG + telemetry + MCP +
human approval and exits green with an artifact trail.
*Verified by:* `tests/acceptance/test_s6_integration.py`

---

## Frozen milestone test sets

Each milestone owns an acceptance suite (pytest marker `acceptance`) + frozen fixtures
(`evals/<area>/`) + a Markdown report (`evals/reports/`). Exit criteria below are lifted from
FINALIZED_PLAN and converted to testable form.

### M2 — Harness control plane (next up)

Acceptance IDs ACC-H1…H9:

- **ACC-H1** Run state machine: legal transitions only; illegal transition raises; states persist across restart.
- **ACC-H2** Contract validation: malformed RunContract rejected pre-execution, with reason.
- **ACC-H3** Path/command policy: workspace escape, symlink escape, forbidden command → blocked before execution.
- **ACC-H4** Budgets: time, attempt, token, cost, changed-file budgets enforced; overrun aborts with terminal state.
- **ACC-H5** Verifier pipeline: independent verifier detects false success (feeds S1); verifier cannot be satisfied by worker self-report alone.
- **ACC-H6** Evidence persistence: evidence bundle written, loadable, schema-valid; tamper attempt detectable.
- **ACC-H7** Bounded retry + no-progress detection: retries stop when no measurable progress; never infinite.
- **ACC-H8** Worker adapters: ≥2 implementations (mock + OpenRouter-backed DeepAgents) pass the SAME adapter conformance suite.
- **ACC-H9** Frozen benchmark: 20 staged tasks incl. failure cases; report includes failures, not just successes.

### M3 — LoopForge

ACC-L1…L7: durable manifest resume-after-kill (= S2 core); deterministic eligibility; isolated
per-task workspaces; maker/verifier separation enforced; no retry without measurable progress;
memory cannot expand its own permissions/budgets; human approval gate; named terminal states
evaluated against 30 staged events.

### M5 — TraceBench

ACC-T1…T6: OTel semantic conventions exported + collected via OTLP; first material divergence
identified between two fixture runs (= S4 core); repeated actions/oscillations detected;
retrieval diagnostics work on synthetic traces using the frozen retrieval-span contract;
redaction default-on; regression experiment rerun flags a deliberately degraded run.

### M6 — OpsTwin

ACC-O1…O7: four MCP servers with OAuth audience/scopes enforced; idempotency keys prevent
duplicate side effects on replay; typed incident DAG executes investigators only where deps allow;
risky action requires explicit approval; injection payloads in logs/tickets do not escalate;
root-cause accuracy + evidence completeness measured over 30 scenarios; integrated demo v1 green.

### M4 — Multimodal RAG (last)

ACC-R1…R8: 200+ page ingestion end-to-end; table-cell retrieval; chart/diagram evidence with
region citations; hybrid fusion + reranking beats naive baseline on frozen question set (50+
human-reviewed questions incl. cross-page and unanswerable); calculation verifier emits formula
+ inputs; abstention precision reported; perf measured (ingestion + p95 query); emits frozen
retrieval span attributes consumed by TraceBench unchanged.

### M7 — Portfolio packaging

Checklist: reproducible fresh-machine setup ≤ 10 min; architecture diagrams; benchmark reports;
demo videos/GIFs; technical article; resume bullets; landing page section.

---

## Tech stack

Python 3.12+, uv, Pydantic v2, structlog, typer (existing).
Added per milestone as optional extras (already declared in pyproject):
`deepagents`, `loop`, `rag`, `observability`, `mcp`, `api`, `ui`.
Web apps: FastAPI backends; React + TypeScript frontends (only inside `apps/*` UIs).
Borrow, don't build: LangGraph, Docling, OpenTelemetry SDK, MCP SDK, Qdrant/Postgres adapter.

## Commands

```bash
# setup
uv sync --extra dev            # Windows fallback if uv trampoline fails:
                               #   .venv\Scripts\python.exe -m pip install -e ".[dev]"

# quality gates (every commit)
uv run ruff format --check . && uv run ruff check .
uv run mypy src
uv run pytest -m "not adversarial and not evaluation"
uv run pytest -m adversarial

# milestone-specific
uv run pytest -m acceptance              # current milestone acceptance suite
uv run pytest -m evaluation              # frozen evals (recorded, $0)
OPENROUTER_API_KEY=... make live-demo    # optional live model runs

# demos (arrive with later milestones)
make demo-integration                    # S6
```

CI (GitHub Actions, already scaffolded) runs all quality gates + non-live suites on every push.

## Project structure

```text
src/reliable_agent_platform/
  contracts/          done (M1)
  harness/            M2 — control plane, policy, budgets, verifier, evidence
  worker_adapters/    M2 — mock (done), deepagents_openrouter
  loop_engine/        M3
  observability/      M5 — otel semantics, collectors, analysis
  mcp_servers/        M6
  multimodal_rag/     M4 (last)
apps/
  control_plane_api/  M2 — FastAPI wrapper around harness
  tracebench/         M5 — analysis service + React dashboard
  opstwin/            M6 — orchestrator + React console
  document_intelligence/ M4
tests/
  unit/  adversarial/  integration/
  acceptance/         ← NEW: S1–S6 + ACC-* suites (the reverse-engineered test sets)
evals/
  harness/ loop/ observability/ ops/ rag/
  reports/            ← frozen Markdown reports with numbers
specs/contracts/  prompts/  docs/adrs/  docs/architecture/
```

## Code style

Strict mypy, ruff line-length 100, Pydantic v2 models with `model_config =
ConfigDict(extra="forbid", frozen=...)` where immutability applies (matches M1 conventions).
Result types over exceptions for expected domain failures; exceptions for programmer errors.
Every module has a docstring stating its invariant. No comments narrating obvious code.

## Testing strategy

- Markers: `unit` (default), `adversarial`, `integration`, `acceptance`, `evaluation`.
- Acceptance suites are deterministic and hermetic — recorded OpenRouter responses as JSON
  fixtures; live calls only behind explicit env flag, never in CI.
- Coverage floor: ≥ 90% lines on `src/reliable_agent_platform/**` (enforced in CI once M2 lands).
- Each frozen eval = fixture inputs + expected outputs + a report generator script; reports
  committed with date + config hash so numbers can't silently drift.
- Property-based tests (hypothesis) allowed for policy/budget engines from M2 onward.

## Boundaries

**Always:** run full gates before commit; ship adversarial case + frozen eval + report + known
limitations per milestone; commit specs and ADRs alongside code; keep main green.
**Ask first:** new runtime dependencies beyond declared extras; changing contract schemas
(versioned migration required); adding cloud services; publishing anything external.
**Never:** commit secrets/keys (OpenRouter key lives in `.env`, gitignored); autonomous merges;
claim performance without a frozen eval; delete failing tests to get green; `--yolo` agent runs.

## Open questions (non-blocking)

1. Create the public GitHub repo now and push M1, or wait until M2 lands? *(Owner: recommend now.)*
2. Which OpenRouter models for worker vs judge roles? Default proposal: cheap fast model for
   workers (e.g. a mini-class model), stronger model for verification judging. Decide at M2 adapter work.
3. Repo name stays `reliable-agent-platform`? Fine as-is.

# Development KPIs — with vs without Nornyx

GovFlags is small enough to reason about end-to-end, which makes it a fair lens
on what Nornyx actually changes about *how* the app is built. The application
code (`app/`) and the tests (`tests/test_api.py`, `tests/test_evaluation.py`) are
identical in both columns — Nornyx does not write app code. What changes is the
**control layer** around the work: where the rules live, and whether they can
drift.

This is a single-project, qualitative comparison, not a benchmark. The point is
*which work exists and where it lives*, not a productivity score.

## Side by side

| KPI | Without Nornyx | With Nornyx |
|-----|----------------|-------------|
| Source of the rules | BRD prose + tribal knowledge; `AGENTS.md` hand-written | One `govflags.nyx` contract; `AGENTS.md`, `policy.yaml`, `harness.yaml`, `evals.yaml`, `context.yaml`, skills, evidence contract **generated** from it |
| Agent-guidance drift | `AGENTS.md` edited by hand, silently goes stale | `scripts/check_drift.py` + CI fail on any drift (`test_no_drift_between_contract_and_agents_md`) |
| Policy as code | Rules live in reviewers' heads / PR templates | `deny secrets_to_llm`, `require tests_if_code_changed`, `deny nondeterministic_evaluation`, `require human_approval_before_merge` declared once, generated to `policy.yaml` |
| Determinism guarantee (NFR-2) | Hope; caught only if a reviewer notices `random`/`time` | Policy `deny nondeterministic_evaluation` + executable check `test_evaluation_module_uses_no_randomness_or_clock` |
| Evidence at merge | Ad-hoc; whatever the PR author pastes | Named evidence contract: `patch.diff`, `test_report.txt`, `brd_conformance.md`, `approval_log.json` |
| Requirement traceability | Manual, often skipped | `evidence/brd_conformance.md` maps every FR/NFR → code → test |
| Human-in-the-loop | Convention | `require human_approval_before_merge` + `approval_log.json`; AI is a surface, never the approver |
| Onboarding a new contributor | Read the BRD, the code, ask around | Read one `.nyx` + generated `AGENTS.md`; CI enforces the rest |
| Net new files to maintain by hand | `AGENTS.md`, policy notes, checklists (all hand-kept) | 1 hand-kept source (`govflags.nyx`); the rest are build output |

## Counts from this repo

| Metric | Value |
|--------|-------|
| Hand-authored governance sources | **1** (`govflags.nyx`, 135 lines) |
| Control artifacts generated from it | **12** (AGENTS.md, 3 skills, policy/harness/evals/context/trace/goals YAML, evidence contract, manifest) |
| Governance encoded as executable tests | **3** (`tests/test_governance.py`) |
| Total tests | **24**, all green |
| BRD requirements traced to tests | **7 FR + 4 NFR**, 100% in `brd_conformance.md` |
| Drift gate result | in-sync passes, drift blocks (exit 1), resync passes — verified |

## What Nornyx did **not** do

- It did **not** write `app/main.py` or the tests — engineers did.
- It is **not** a runtime: it does not run the agents, deploy, or touch
  credentials. It generates and validates the control artifacts.
- It does **not** replace human approval; it makes the requirement explicit and
  auditable.

## Takeaway

Without Nornyx, the governance for this app is *prose + discipline*: an
`AGENTS.md` someone keeps up to date, policy living in reviewers' heads, evidence
assembled by hand, and determinism enforced only by vigilance. With Nornyx the
same governance is *one checked source* that generates the agent guidance and
policy, fails CI on drift, and ships a named evidence pack — for the cost of
maintaining a single 135-line `.nyx` file instead of a dozen hand-kept artifacts.
The app is the same; the **control plane is now a build target instead of a
habit.**

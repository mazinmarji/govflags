# GovFlags — a feature-flag API built **under Nornyx governance**

GovFlags is a small, self-contained feature-flag service (create / list / get /
toggle / evaluate / delete boolean flags, with deterministic percentage
rollouts). It exists to demonstrate developing a real application **governed by a
[Nornyx](https://github.com/mazinmarji/nornyx) contract** — from a BRD, to a
`.nyx` contract, to generated control artifacts, to a tested app with a drift
gate — and to compare development KPIs **with vs without** Nornyx.

## The governed pipeline

```
docs/BRD.md  ──►  govflags.nyx  ──►  nornyx generate  ──►  AGENTS.md + policy.yaml
 (requirements)   (the contract)     (deterministic)       harness/evals/context/
                                                           skills/evidence contract
                        │
                        └──►  nornyx check  +  scripts/check_drift.py  (CI gate)
```

- **[docs/BRD.md](docs/BRD.md)** — business requirements (FR-1..FR-7, NFR-1..NFR-4,
  governance G-1..G-5).
- **[govflags.nyx](govflags.nyx)** — the single source of truth: constitution,
  intents, contexts, skills, policies, agents, harness, evals, evidence, approvals,
  budgets. Passes `nornyx check`.
- **[AGENTS.md](AGENTS.md)** — generated agent guidance at the repo root (what
  Claude Code / Cursor / Copilot read). Never hand-edited; the drift gate enforces it.
- **`.nyx-out/`** — full generated control artifact set (build output).

## The app

| Endpoint | Behaviour |
|----------|-----------|
| `POST /flags` | create a flag (`key` matches `^[a-z0-9-]+$`); duplicate → 409 |
| `GET /flags` | list all flags |
| `GET /flags/{key}` | get one; unknown → 404 |
| `PATCH /flags/{key}` | partial update; unknown → 404 |
| `GET /flags/{key}/evaluate?user_id=…` | deterministic on/off for that user |
| `DELETE /flags/{key}` | delete; 204; unknown → 404 |
| `GET /health` | `{"status":"ok"}` |

Evaluation is pure and deterministic: the on/off decision for a partial rollout
is a SHA-256 bucket of `(key, user_id)`, so the same inputs always give the same
answer and a 50% rollout lands ~half the users on — no randomness, no clock.

## Run it

```bash
python -m venv .venv && . .venv/Scripts/activate   # or .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload      # serve the API
pytest -q                          # 24 tests, all green
nornyx check govflags.nyx          # validate the contract
python scripts/check_drift.py      # fail if AGENTS.md drifts from the contract
```

Install the drift gate as a pre-commit hook:

```bash
cp scripts/hooks/pre-commit .git/hooks/pre-commit
```

## Governance

The BRD's governance constraints are generated into `policy.yaml` and made
executable in [tests/test_governance.py](tests/test_governance.py):

- `deny secrets_to_llm` (G-1) · `require tests_if_code_changed` (G-2)
- `deny nondeterministic_evaluation` (G-3) · `require human_approval_before_merge` (G-4)
- no artifact drift (G-5) — `scripts/check_drift.py`, enforced in CI

Delivery evidence (the contract's evidence pack) lives in
[evidence/](evidence/): `test_report.txt`, `brd_conformance.md`,
`approval_log.json`, `patch.diff`.

## With vs without Nornyx

See **[docs/KPI_COMPARISON.md](docs/KPI_COMPARISON.md)** — the app code is the
same either way; what Nornyx changes is that the control plane (agent guidance,
policy, evidence, determinism, approval) becomes a single checked build target
instead of hand-kept prose.

## Scope

In scope: HTTP API, in-memory storage, deterministic evaluation, full test suite.
Out of scope: persistence/DB, auth, multi-tenant, UI, deployment. Nornyx is a
spec/checker layer, not a runtime — it generates and validates control artifacts;
it does not run agents, deploy, or touch credentials.

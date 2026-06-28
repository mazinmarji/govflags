# Business Requirements Document — GovFlags

## 1. Purpose
GovFlags is a small, self-contained **feature-flag service**: teams create flags,
toggle them, and evaluate whether a flag is on for a given user — including
**percentage rollouts** that are deterministic per user. It is the product we
build to demonstrate developing a real app **under Nornyx governance**.

## 2. Scope
**In scope:** an HTTP API to manage and evaluate boolean feature flags with
optional percentage rollout; in-memory storage; a deterministic evaluation rule;
a full test suite.
**Out of scope:** persistence/DB, auth, multi-tenant, UI, deployment.

## 3. Functional requirements
- **FR-1 Create flag:** `POST /flags` with `{key, enabled, rollout_percent}` →
  201 + the flag. `key` is unique (`^[a-z0-9-]+$`); duplicate → 409.
- **FR-2 List flags:** `GET /flags` → all flags.
- **FR-3 Get flag:** `GET /flags/{key}` → the flag; unknown → 404.
- **FR-4 Toggle flag:** `PATCH /flags/{key}` with `{enabled?, rollout_percent?}`
  → the updated flag; unknown → 404.
- **FR-5 Evaluate:** `GET /flags/{key}/evaluate?user_id=...` → `{key, user_id, on}`.
  - If the flag is disabled → `on=false`.
  - If enabled and `rollout_percent == 100` → `on=true`.
  - If enabled with a partial rollout → `on` is **deterministic** per
    `(key, user_id)` (same inputs always give the same answer) and the share of
    users with `on=true` approximates `rollout_percent`.
- **FR-6 Delete flag:** `DELETE /flags/{key}` → 204; unknown → 404.
- **FR-7 Health:** `GET /health` → `{status:"ok"}`.

## 4. Non-functional requirements
- **NFR-1** `rollout_percent` is an integer 0–100; invalid input → 422.
- **NFR-2** Evaluation is pure and deterministic (no randomness, no clock).
- **NFR-3** No secrets, no external network calls, no credential handling.
- **NFR-4** Every code change ships with tests; the suite is green.

## 5. Data model
`Flag { key: str, enabled: bool, rollout_percent: int (0..100) }`

## 6. Governance constraints (these become Nornyx policy)
- **G-1** No secrets are read or sent to any model/tool (`deny secrets_to_llm`).
- **G-2** Every code change requires tests (`require tests_if_code_changed`).
- **G-3** Evaluation logic must stay deterministic (no `random`/`time` in eval).
- **G-4** A change is only mergeable after tests pass and a human approves.
- **G-5** The repo's control artifacts (AGENTS.md, policy, harness) are generated
  from one `.nyx` source and must not drift.

## 7. Acceptance criteria
- All FRs implemented; all NFRs satisfied.
- Deterministic rollout: evaluating the same `(key, user_id)` twice is identical;
  across many users a 50% rollout lands roughly half on.
- Test suite green; drift gate passes; AGENTS.md/policy generated from `govflags.nyx`.

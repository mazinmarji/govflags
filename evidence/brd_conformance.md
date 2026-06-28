# BRD conformance — GovFlags

Maps every requirement in [docs/BRD.md](../docs/BRD.md) to its implementation and
the test(s) that prove it. Generated as delivery evidence under the
`govflags.nyx` evidence contract.

## Functional requirements

| Req | Requirement | Implementation | Test |
|-----|-------------|----------------|------|
| FR-1 | `POST /flags`, unique `^[a-z0-9-]+$`, dup → 409 | `app/main.py::create_flag`, `app/models.py::Flag` | `test_create_flag_returns_201_and_body`, `test_create_duplicate_key_returns_409`, `test_create_invalid_key_returns_422` |
| FR-2 | `GET /flags` lists all | `app/main.py::list_flags` | `test_list_flags` |
| FR-3 | `GET /flags/{key}`, unknown → 404 | `app/main.py::get_flag` | `test_get_flag_and_404` |
| FR-4 | `PATCH /flags/{key}`, unknown → 404 | `app/main.py::update_flag`, `app/store.py::FlagStore.update` | `test_patch_flag_updates_fields`, `test_patch_partial_keeps_other_fields`, `test_patch_unknown_returns_404` |
| FR-5 | `GET /flags/{key}/evaluate?user_id=…` deterministic | `app/main.py::evaluate_flag`, `app/evaluation.py` | `test_evaluate_*`, `test_evaluation_is_deterministic_per_key_user`, `test_fifty_percent_rollout_approximates_half` |
| FR-6 | `DELETE /flags/{key}` → 204, unknown → 404 | `app/main.py::delete_flag` | `test_delete_flag_returns_204_then_404` |
| FR-7 | `GET /health` → `{status:"ok"}` | `app/main.py::health` | `test_health_ok` |

## Non-functional requirements

| Req | Requirement | How satisfied | Test |
|-----|-------------|---------------|------|
| NFR-1 | `rollout_percent` int 0–100, invalid → 422 | `Field(ge=0, le=100)` on `Flag`/`FlagUpdate` | `test_rollout_percent_out_of_range_returns_422` |
| NFR-2 | Evaluation pure/deterministic (no random/clock) | SHA-256 bucketing on `(key, user_id)` | `test_bucket_is_stable_across_calls`, `test_evaluation_module_uses_no_randomness_or_clock` |
| NFR-3 | No secrets, no network, no credentials | In-memory store only; no network/secret code paths | reviewed; policy `deny secrets_to_llm` |
| NFR-4 | Every change ships with green tests | 24 tests, suite green | `evidence/test_report.txt` |

## Governance constraints (G-1..G-5)

| Constraint | Mechanism | Evidence |
|------------|-----------|----------|
| G-1 no secrets to model/tool | `policy.yaml: deny secrets_to_llm` | generated from `govflags.nyx` |
| G-2 tests with every change | `policy.yaml: require tests_if_code_changed` + CI `pytest` | `.github/workflows/ci.yml` |
| G-3 deterministic evaluation | `policy.yaml: deny nondeterministic_evaluation` + static test | `test_evaluation_module_uses_no_randomness_or_clock` |
| G-4 human approval before merge | `policy.yaml: require human_approval_before_merge` | `evidence/approval_log.json` |
| G-5 artifacts generated, no drift | `scripts/check_drift.py` + CI drift gate | `test_no_drift_between_contract_and_agents_md` |

All functional and non-functional requirements implemented; the suite is green;
the drift gate passes; AGENTS.md/policy are generated from `govflags.nyx`.

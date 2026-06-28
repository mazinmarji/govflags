"""Determinism + distribution properties of flag evaluation (FR-5, NFR-2)."""

from __future__ import annotations

import inspect

from app import evaluation
from app.evaluation import bucket_of, evaluate


def test_evaluation_is_deterministic_per_key_user():  # FR-5 / NFR-2
    for user in ("u1", "u2", "alice", "bob-42"):
        first = evaluate(key="exp", user_id=user, enabled=True, rollout_percent=50)
        for _ in range(5):
            assert (
                evaluate(key="exp", user_id=user, enabled=True, rollout_percent=50)
                == first
            )


def test_bucket_is_stable_across_calls():  # NFR-2: no process-salted hashing
    assert bucket_of("exp", "alice") == bucket_of("exp", "alice")
    assert 0 <= bucket_of("exp", "alice") < 100


def test_same_user_differs_across_flags():  # rollout depends on (key, user_id)
    buckets = {bucket_of(key, "alice") for key in ("flag-a", "flag-b", "flag-c", "flag-d")}
    assert len(buckets) > 1  # not all flags bucket a user identically


def test_fifty_percent_rollout_approximates_half():  # FR-5 distribution
    users = [f"user-{i}" for i in range(2000)]
    on = sum(
        evaluate(key="exp", user_id=u, enabled=True, rollout_percent=50) for u in users
    )
    share = on / len(users)
    assert 0.45 <= share <= 0.55


def test_higher_rollout_never_turns_a_user_off():  # monotonic in rollout_percent
    for u in (f"user-{i}" for i in range(500)):
        history = [
            evaluate(key="exp", user_id=u, enabled=True, rollout_percent=p)
            for p in range(0, 101, 10)
        ]
        # once on, stays on as rollout grows
        assert history == sorted(history, key=lambda b: (b is True))


def test_evaluation_module_uses_no_randomness_or_clock():  # NFR-2 / G-3 (static)
    source = inspect.getsource(evaluation)
    for forbidden in ("import random", "import time", "datetime", "secrets"):
        assert forbidden not in source

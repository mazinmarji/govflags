"""Deterministic flag evaluation.

NFR-2 / G-3: evaluation is pure and deterministic — no randomness, no clock.
The on/off decision for a partial rollout depends only on ``(key, user_id)``
and ``rollout_percent``, so the same inputs always yield the same answer, and
across many users the share with ``on=True`` approximates ``rollout_percent``.
"""

from __future__ import annotations

import hashlib


def bucket_of(key: str, user_id: str) -> int:
    """Map ``(key, user_id)`` to a stable bucket in ``0..99``.

    Uses a SHA-256 digest of ``key:user_id`` (not Python's salted ``hash()``,
    which varies per process) so the result is reproducible across runs and
    machines. Including ``key`` means the same user can fall on different sides
    of the rollout for different flags.
    """
    digest = hashlib.sha256(f"{key}:{user_id}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def evaluate(*, key: str, user_id: str, enabled: bool, rollout_percent: int) -> bool:
    """Return whether ``key`` is on for ``user_id`` (FR-5).

    - Disabled flag -> always ``False``.
    - Enabled with ``rollout_percent == 100`` -> always ``True``.
    - Enabled with ``rollout_percent == 0`` -> always ``False``.
    - Enabled with a partial rollout -> deterministic per ``(key, user_id)``.
    """
    if not enabled:
        return False
    if rollout_percent >= 100:
        return True
    if rollout_percent <= 0:
        return False
    return bucket_of(key, user_id) < rollout_percent

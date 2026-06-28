"""HTTP-level conformance tests for the GovFlags API (FR-1..FR-7, NFR-1)."""

from __future__ import annotations


def _create(client, key="dark-mode", enabled=False, rollout_percent=0):
    return client.post(
        "/flags",
        json={"key": key, "enabled": enabled, "rollout_percent": rollout_percent},
    )


def test_health_ok(client):  # FR-7
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_flag_returns_201_and_body(client):  # FR-1
    resp = _create(client, enabled=True, rollout_percent=100)
    assert resp.status_code == 201
    assert resp.json() == {"key": "dark-mode", "enabled": True, "rollout_percent": 100}


def test_create_duplicate_key_returns_409(client):  # FR-1
    assert _create(client).status_code == 201
    assert _create(client).status_code == 409


def test_create_invalid_key_returns_422(client):  # FR-1 key pattern
    for bad in ["Dark_Mode", "dark mode", "UPPER", "with_underscore", ""]:
        assert client.post("/flags", json={"key": bad}).status_code == 422


def test_list_flags(client):  # FR-2
    _create(client, key="a")
    _create(client, key="b")
    resp = client.get("/flags")
    assert resp.status_code == 200
    assert {f["key"] for f in resp.json()} == {"a", "b"}


def test_get_flag_and_404(client):  # FR-3
    _create(client, key="a")
    assert client.get("/flags/a").status_code == 200
    assert client.get("/flags/missing").status_code == 404


def test_patch_flag_updates_fields(client):  # FR-4
    _create(client, key="a", enabled=False, rollout_percent=0)
    resp = client.patch("/flags/a", json={"enabled": True, "rollout_percent": 50})
    assert resp.status_code == 200
    assert resp.json() == {"key": "a", "enabled": True, "rollout_percent": 50}


def test_patch_partial_keeps_other_fields(client):  # FR-4
    _create(client, key="a", enabled=True, rollout_percent=30)
    resp = client.patch("/flags/a", json={"rollout_percent": 70})
    assert resp.json() == {"key": "a", "enabled": True, "rollout_percent": 70}


def test_patch_unknown_returns_404(client):  # FR-4
    assert client.patch("/flags/missing", json={"enabled": True}).status_code == 404


def test_delete_flag_returns_204_then_404(client):  # FR-6
    _create(client, key="a")
    assert client.delete("/flags/a").status_code == 204
    assert client.get("/flags/a").status_code == 404
    assert client.delete("/flags/a").status_code == 404


def test_rollout_percent_out_of_range_returns_422(client):  # NFR-1
    assert _create(client, rollout_percent=101).status_code == 422
    assert _create(client, rollout_percent=-1).status_code == 422
    assert client.post(
        "/flags", json={"key": "x", "rollout_percent": "half"}
    ).status_code == 422


def test_evaluate_unknown_flag_404(client):  # FR-5
    assert client.get("/flags/missing/evaluate?user_id=u1").status_code == 404


def test_evaluate_disabled_is_off(client):  # FR-5
    _create(client, key="a", enabled=False, rollout_percent=100)
    resp = client.get("/flags/a/evaluate?user_id=u1")
    assert resp.status_code == 200
    assert resp.json() == {"key": "a", "user_id": "u1", "on": False}


def test_evaluate_full_rollout_is_on(client):  # FR-5
    _create(client, key="a", enabled=True, rollout_percent=100)
    assert client.get("/flags/a/evaluate?user_id=u1").json()["on"] is True


def test_evaluate_zero_rollout_is_off(client):  # FR-5
    _create(client, key="a", enabled=True, rollout_percent=0)
    assert client.get("/flags/a/evaluate?user_id=u1").json()["on"] is False

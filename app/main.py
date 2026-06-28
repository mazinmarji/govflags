"""GovFlags HTTP API (FR-1..FR-7).

A self-contained feature-flag service: create, list, get, toggle, evaluate, and
delete boolean flags with optional deterministic percentage rollout. No
persistence, auth, or network calls (BRD scope + NFR-3).
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Response

from .evaluation import evaluate
from .models import Evaluation, Flag, FlagUpdate
from .store import DuplicateKeyError, FlagStore, UnknownKeyError

app = FastAPI(title="GovFlags", version="0.1.0")

# Single process-wide store. Exposed via a dependency so tests can override it.
_store = FlagStore()


def get_store() -> FlagStore:
    return _store


@app.get("/health")
def health() -> dict[str, str]:
    """FR-7: liveness probe."""
    return {"status": "ok"}


@app.post("/flags", status_code=201, response_model=Flag)
def create_flag(flag: Flag, store: FlagStore = Depends(get_store)) -> Flag:
    """FR-1: create a flag; duplicate key -> 409."""
    try:
        return store.create(flag)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail=f"flag '{flag.key}' already exists")


@app.get("/flags", response_model=list[Flag])
def list_flags(store: FlagStore = Depends(get_store)) -> list[Flag]:
    """FR-2: list all flags."""
    return store.list()


@app.get("/flags/{key}", response_model=Flag)
def get_flag(key: str, store: FlagStore = Depends(get_store)) -> Flag:
    """FR-3: fetch one flag; unknown -> 404."""
    try:
        return store.get(key)
    except UnknownKeyError:
        raise HTTPException(status_code=404, detail=f"flag '{key}' not found")


@app.patch("/flags/{key}", response_model=Flag)
def update_flag(key: str, update: FlagUpdate, store: FlagStore = Depends(get_store)) -> Flag:
    """FR-4: partially update a flag; unknown -> 404."""
    try:
        return store.update(
            key, enabled=update.enabled, rollout_percent=update.rollout_percent
        )
    except UnknownKeyError:
        raise HTTPException(status_code=404, detail=f"flag '{key}' not found")


@app.get("/flags/{key}/evaluate", response_model=Evaluation)
def evaluate_flag(
    key: str, user_id: str, store: FlagStore = Depends(get_store)
) -> Evaluation:
    """FR-5: deterministically evaluate a flag for a user; unknown flag -> 404."""
    try:
        flag = store.get(key)
    except UnknownKeyError:
        raise HTTPException(status_code=404, detail=f"flag '{key}' not found")
    on = evaluate(
        key=flag.key,
        user_id=user_id,
        enabled=flag.enabled,
        rollout_percent=flag.rollout_percent,
    )
    return Evaluation(key=key, user_id=user_id, on=on)


@app.delete("/flags/{key}", status_code=204)
def delete_flag(key: str, store: FlagStore = Depends(get_store)) -> Response:
    """FR-6: delete a flag; unknown -> 404."""
    try:
        store.delete(key)
    except UnknownKeyError:
        raise HTTPException(status_code=404, detail=f"flag '{key}' not found")
    return Response(status_code=204)

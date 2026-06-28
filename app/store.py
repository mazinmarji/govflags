"""In-memory flag storage (BRD scope: in-memory, no DB)."""

from __future__ import annotations

from .models import Flag


class DuplicateKeyError(KeyError):
    """Raised when creating a flag whose key already exists (FR-1 -> 409)."""


class UnknownKeyError(KeyError):
    """Raised when a flag key is not found (FR-3/4/6 -> 404)."""


class FlagStore:
    """A tiny dict-backed store. One instance per app; reset for tests."""

    def __init__(self) -> None:
        self._flags: dict[str, Flag] = {}

    def create(self, flag: Flag) -> Flag:
        if flag.key in self._flags:
            raise DuplicateKeyError(flag.key)
        self._flags[flag.key] = flag
        return flag

    def list(self) -> list[Flag]:
        return list(self._flags.values())

    def get(self, key: str) -> Flag:
        try:
            return self._flags[key]
        except KeyError as exc:
            raise UnknownKeyError(key) from exc

    def update(self, key: str, *, enabled: bool | None, rollout_percent: int | None) -> Flag:
        flag = self.get(key)
        updated = flag.model_copy(
            update={
                k: v
                for k, v in (("enabled", enabled), ("rollout_percent", rollout_percent))
                if v is not None
            }
        )
        self._flags[key] = updated
        return updated

    def delete(self, key: str) -> None:
        try:
            del self._flags[key]
        except KeyError as exc:
            raise UnknownKeyError(key) from exc

    def clear(self) -> None:
        self._flags.clear()

#!/usr/bin/env python3
"""Drift gate for GovFlags (BRD G-5).

The control artifacts (AGENTS.md and everything under .nyx-out/) are *build
output* of ``govflags.nyx``. This script re-runs ``nornyx check`` + ``nornyx
generate`` into a throwaway directory and fails if the committed root
``AGENTS.md`` differs from the freshly generated one. That keeps the contract as
the single source of truth: edit the .nyx, regenerate, or CI fails loudly.

Usage:
    python scripts/check_drift.py
Exit codes: 0 = in sync, 1 = drift or contract error.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "govflags.nyx"
ROOT_AGENTS = ROOT / "AGENTS.md"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "nornyx.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def main() -> int:
    check = _run("check", str(CONTRACT))
    if check.returncode != 0:
        sys.stderr.write(check.stdout + check.stderr)
        sys.stderr.write("\nContract failed `nornyx check`.\n")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        gen = _run("generate", str(CONTRACT), "--out", tmp)
        if gen.returncode != 0:
            sys.stderr.write(gen.stdout + gen.stderr)
            return 1
        fresh_agents = (Path(tmp) / "AGENTS.md").read_text(encoding="utf-8")

    if not ROOT_AGENTS.is_file():
        sys.stderr.write("AGENTS.md is missing at the repo root.\n")
        return 1

    committed = ROOT_AGENTS.read_text(encoding="utf-8")
    if committed != fresh_agents:
        sys.stderr.write(
            "DRIFT: AGENTS.md is out of sync with govflags.nyx.\n"
            "Fix: nornyx generate govflags.nyx --out .nyx-out "
            "&& cp .nyx-out/AGENTS.md AGENTS.md\n"
        )
        return 1

    print("Drift gate OK: AGENTS.md matches govflags.nyx.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

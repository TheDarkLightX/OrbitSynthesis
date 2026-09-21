#!/usr/bin/env python3
"""Portable fail-closed gate for the native first-mismatch refinement.

The gate replays the independent semantic oracle, quantitative sharpening, and
adaptive block schedule under normal and optimized Python, compares every
output with a committed version-independent receipt, scans the new Lean sources
for placeholders, and runs the complete six-layer Lean compilation script.

It does not promote the integrated compiler beyond its stated frozen premises
and makes no novelty, patent, license, or practical-performance finding.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "research/tournaments/2026-08-13-semantic-router-frontier"
LANE = FRONTIER / "lanes/native_mode_router"
FORMAL = FRONTIER / "lanes/formal_native_first_mismatch"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> bytes:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        rendered = " ".join(command)
        raise RuntimeError(
            f"command failed ({completed.returncode}): {rendered}\n"
            f"stdout:\n{completed.stdout.decode(errors='replace')}\n"
            f"stderr:\n{completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def replay(
    label: str,
    script: Path,
    committed: Path,
    temporary: Path,
) -> dict[str, str]:
    normal = temporary / f"{label}.normal.json"
    optimized = temporary / f"{label}.optimized.json"
    relative = str(script.relative_to(ROOT))
    run([sys.executable, relative, "--out", str(normal)])
    run([sys.executable, "-O", relative, "--out", str(optimized)])
    require(normal.read_bytes() == optimized.read_bytes(), f"{label}: normal/-O drift")
    require(normal.read_bytes() == committed.read_bytes(), f"{label}: committed receipt drift")
    parsed = json.loads(normal.read_text(encoding="utf-8"))
    semantic = parsed.get("semantic_sha256")
    require(isinstance(semantic, str), f"{label}: missing semantic hash")
    return {
        "file_sha256": sha256(normal),
        "semantic_sha256": semantic,
    }


def check_formal_sources() -> dict[str, str]:
    sources = [
        FORMAL / "NativeFirstMismatch.lean",
        FORMAL / "NativeModeBridge.lean",
        FORMAL / "NativeModeCost.lean",
    ]
    forbidden = re.compile(
        r"(^|[^A-Za-z0-9_])(sorry|admit)([^A-Za-z0-9_]|$)"
        r"|^[ \t]*(axiom|unsafe)[ \t]",
        re.MULTILINE,
    )
    hashes: dict[str, str] = {}
    for source in sources:
        text = source.read_text(encoding="utf-8")
        require(not forbidden.search(text), f"forbidden Lean declaration: {source}")
        hashes[source.name] = sha256(source)
    run(["bash", str((FORMAL / "check.sh").relative_to(ROOT))])
    return hashes


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="orbit-native-router-") as temp_name:
        temporary = Path(temp_name)
        results = {
            "native_semantics": replay(
                "native-semantics",
                LANE / "check_native_mode_portable.py",
                LANE / "portable_receipt.json",
                temporary,
            ),
            "sharpened_constants": replay(
                "native-sharpening",
                LANE / "check_router_sharpenings_portable.py",
                LANE / "portable_sharpening_receipt.json",
                temporary,
            ),
            "adaptive_block_constant": replay(
                "adaptive-block",
                LANE / "check_adaptive_block_compiler.py",
                LANE / "adaptive_block_receipt.json",
                temporary,
            ),
            "lean": check_formal_sources(),
        }

    output = {
        "schema": "orbit-synthesis/native-first-mismatch-gate/v2",
        "status": "PASS",
        "claim_boundary": (
            "Exact PASS for the native first-mismatch algebra, original-signature "
            "bridge, fused signed-router semantics, recurrence-level cost bounds, "
            "and bounded/adaptive compiler arithmetic. The end-to-end compiler "
            "remains conditional on the frozen interfaces inherited from the base "
            "paper. Novelty, FTO, serialized DAG extraction, practical performance, "
            "and global optimality are not established by this gate."
        ),
        "results": results,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

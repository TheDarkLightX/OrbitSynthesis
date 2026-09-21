#!/usr/bin/env python3
"""Deterministic receipt for the sharp-depth/census checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SOURCES = (
    HERE / "DepthAndCensus.lean",
    HERE / "AxiomAudit.lean",
    HERE / "check.sh",
    Path(__file__).resolve(),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    checked = subprocess.run(
        [str(HERE / "check.sh")], cwd=REPO, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if checked.returncode != 0:
        raise RuntimeError(checked.stdout)
    if "No proof placeholders found." not in checked.stdout:
        raise RuntimeError("placeholder scan missing")
    payload: dict[str, object] = {
        "schema": "orbit-synthesis/formal-gap-closure/v1",
        "status": "PASS_SHARP_DEPTH__PARTIAL_OUTPUT_CENSUS",
        "source_sha256": {path.name: digest(path) for path in SOURCES},
        "proved": [
            "sibling-shared depth <=3+Nat.clog 2 width",
            "combined exact size-envelope and sharp-depth checkpoint",
            "injective ternary truth-table evaluation",
            "gain/bad/not-bad tables equal frozen addressSummary semantics",
            "bad and not-bad table families are injective all-width",
            "bad/not-bad complementation and constant-separation witnesses",
        ],
        "open": [
            "gain quotient cardinality (q+1)/2",
            "unique signed sibling-overlap classification and count",
            "final inclusion-exclusion 4q/3 and 4q/3+1",
        ],
        "checks": {
            "warning_as_error": True,
            "proof_placeholders": 0,
            "custom_axiom_declarations": 0,
            "check_stdout_sha256": hashlib.sha256(checked.stdout.encode()).hexdigest(),
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["semantic_sha256"] = hashlib.sha256(canonical).hexdigest()
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

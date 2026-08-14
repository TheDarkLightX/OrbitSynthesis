#!/usr/bin/env python3
"""Fail-closed deterministic receipt for the formal optimized rail lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]

FROZEN = {
    "StrongSignedRouter.lean": (
        REPO / "research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean",
        "687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a",
    ),
    "ProgramVector.lean": (
        REPO / "research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean",
        "c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd",
    ),
    "ProgramVectorCost.lean": (
        REPO / "research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean",
        "ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2",
    ),
    "STATE.md": (
        REPO / "research/tournaments/2026-08-13-program-vector-optimization/STATE.md",
        "6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6",
    ),
    "lower_bound_REPORT.md": (
        REPO / "research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/REPORT.md",
        "be6288a6eac7f2a34012eff9e3283bf1d99929fb34460050bd17d67f9d293751",
    ),
    "lower_bound_checker.py": (
        REPO / "research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/check_lower_bound.py",
        "3b02d4cd842e7b8b252a38b3cdcb4fb2fc6044cf04f72b0b0250709a6cda2785",
    ),
    "lower_bound_receipt.json": (
        REPO / "research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/receipt.json",
        "11daf965c409e41192e3be2cf81655e554a5881c60d1011b1f1e52259b93d20b",
    ),
}

LANE_SOURCES = (
    HERE / "DirectRail.lean",
    HERE / "SiblingShared.lean",
    HERE / "AxiomAudit.lean",
    HERE / "check.sh",
    Path(__file__).resolve(),
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    frozen_hashes: dict[str, str] = {}
    for label, (path, expected) in FROZEN.items():
        observed = sha256_path(path)
        require(observed == expected, f"frozen hash drift: {label}")
        frozen_hashes[label] = observed

    completed = subprocess.run(
        [str(HERE / "check.sh")],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    require(completed.returncode == 0, completed.stdout)
    require("No proof placeholders found." in completed.stdout, "placeholder scan missing")
    require("warning:" not in completed.stdout.lower(), "Lean emitted a warning")
    require("error:" not in completed.stdout.lower(), "Lean emitted an error")
    require(
        "siblingSharedNodes_scaled_envelope' depends on axioms" in completed.stdout,
        "axiom dependency audit missing",
    )

    lean_version = subprocess.run(
        ["lake", "env", "lean", "--version"],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    ).stdout.strip()

    result: dict[str, object] = {
        "schema": "orbit-synthesis/formal-optimized-direct-rail/v2",
        "status": "PASS_EXACT_DIRECT_RAIL_AND_SIBLING_SHARED_ENVELOPE",
        "frozen_sha256": frozen_hashes,
        "lane_sha256": {path.name: sha256_path(path) for path in LANE_SOURCES},
        "lean_version": lean_version,
        "checks": {
            "theorem_modules_warning_as_error": True,
            "explicit_lean_path_chain": True,
            "proof_placeholders": 0,
            "user_axiom_declarations": 0,
            "axiom_audit_standard_dependencies": [
                "Classical.choice",
                "Quot.sound",
                "propext",
            ],
            "check_stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
        },
        "proved_checkpoints": [
            "absorbing direct-rail composition in original d/u semantics under A=2",
            "four-node one-digit rail library and original-signature legality",
            "exact signed projection-control formulas",
            "O_(a s)=O_a for every physical suffix s over {0,1}",
            "N_(a1)=O_(a2) for every valid earlier prefix summary a",
            "frozen direct-rail total <=3*3^w and scaled (2+o(1))*3^w envelope",
            "sibling-shared exact recurrences",
            "3*S(w)<=4*3^w+15*3^ceil(w/2)",
            "3*S(w)<=7*3^w",
        ],
        "scope": {
            "root_sign": "one fixed P or N sign",
            "circuit": "address-only scalar original-signature d/u same-DAG with free fanout",
            "anchor_premise": "A=2",
            "cost_link": "checked arithmetic ledger plus semantic reuse identities; no internal DAG datatype",
        },
        "nonclaims": [
            "No all-width distinct-output census is formalized in this lane.",
            "No exact finite-width optimum or global circuit lower bound.",
            "No formula-size, bounded-fanout, integrated compiler, novelty, patent, or FTO claim.",
        ],
    }
    result["semantic_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

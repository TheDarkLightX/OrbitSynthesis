#!/usr/bin/env python3
"""Fail-closed Research Kernel replay for the D3 minimal-core classification."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    summary_path = root / "runs/zag_discriminator_minimal_core_antichains/summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["table_count"] == 19683
    assert summary["nonempty_antichain_count"] == 19
    assert summary["realized_antichain_count"] == 15
    assert summary["symmetry_orbit_count"] == 9
    assert summary["realized_orbit_count"] == 7
    assert summary["singleton_clone_pair_intersections"] == {"0,1": 2, "0,2": 2, "1,2": 2}

    paths = [
        "runs/zag_discriminator_minimal_core_antichains/summary.json",
        "experiments/discriminator_minimal_core_antichains.py",
        "notes/DISCRIMINATOR_MINIMAL_CORE_ANTICHAINS.md",
        "formal/OrbitSynthesis/CoreAntichain.lean",
    ]
    artifacts = {path: digest(root / path) for path in paths}

    atoms = [
        {
            "id": "q_antichains",
            "type": "QUESTION",
            "status": "TESTABLE",
            "content": "Which nonempty core antichains are realized by binary polynomial operations of the pure three-element discriminator?",
            "parents": [],
        },
        {
            "id": "claim_binary_pair_collapse",
            "type": "CLAIM",
            "status": "SUPPORTED",
            "content": "For every pair of distinct singleton cores, their binary polynomial-language intersection is exactly the two-table parameter-free clone.",
            "parents": ["q_antichains"],
        },
        {
            "id": "claim_classification",
            "type": "CLAIM",
            "status": "SUPPORTED",
            "content": "Exactly 15 of 19 nonempty antichains are realized; the four missing families are the two- and three-singleton families.",
            "parents": ["claim_binary_pair_collapse"],
        },
        {
            "id": "claim_generic_pair_collapse",
            "type": "CLAIM",
            "status": "UNDER_TEST",
            "content": "For every arity greater than one, the intersection of two distinct singleton polynomial clones of D3 is the parameter-free term clone.",
            "parents": ["claim_binary_pair_collapse"],
        },
        {
            "id": "hyp_all_antichains",
            "type": "HYPOTHESIS",
            "status": "REFUTED",
            "content": "Every nonempty antichain of the three-element core lattice is realizable at binary arity.",
            "parents": ["q_antichains"],
        },
        {
            "id": "open_larger_discriminator",
            "type": "OPEN_PROBLEM",
            "status": "UNKNOWN",
            "content": "Classify realizable core antichains for pure discriminator algebras of arbitrary finite size and arity.",
            "parents": ["claim_classification"],
        },
    ]
    edges = [
        {
            "source_atom_id": atom["id"],
            "target_atom_id": parent,
            "edge_type": "DEPENDS_ON",
        }
        for atom in atoms
        for parent in atom["parents"]
    ]
    edges.append(
        {
            "source_atom_id": "claim_classification",
            "target_atom_id": "hyp_all_antichains",
            "edge_type": "REFUTES",
        }
    )
    report = {
        "schema": "research_kernel/report/v1",
        "supported_claims": [atom for atom in atoms if atom["status"] == "SUPPORTED"],
        "refuted_claims": [atom for atom in atoms if atom["status"] == "REFUTED"],
        "frontier": [atom for atom in atoms if atom["status"] in {"TESTABLE", "UNDER_TEST", "UNKNOWN"}],
        "artifacts": artifacts,
        "non_claims": [
            "The arbitrary-arity pair-collapse theorem remains UNDER_TEST.",
            "The classification is scoped to binary operations on D3.",
            "Publication novelty is not established by this replay packet.",
        ],
    }

    args.out_root.mkdir(parents=True, exist_ok=True)
    for name, rows in (("atoms.jsonl", atoms), ("edges.jsonl", edges)):
        (args.out_root / name).write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
    (args.out_root / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()

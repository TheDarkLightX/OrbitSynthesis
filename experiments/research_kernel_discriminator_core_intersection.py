#!/usr/bin/env python3
"""Fail-closed Research Kernel replay for the discriminator intersection law."""
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
    summary_path = root / "runs/zag_discriminator_core_intersection/summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["pair_count"] == 87376
    assert summary["incomparable_cover_pair_count"] == 8828
    assert summary["graph_mismatches"] == 0
    assert summary["witness_failures"] == 0
    assert summary["count_formula_failures"] == 0
    assert summary["D3_cover_intersection"] == 576
    assert summary["D4_disjoint_cover_intersection"] == 16
    assert summary["D3_census"]["pairwise_cover_failures"] == 0
    assert summary["semantic_sha256"] == "3f2fd8392938d4ee828bd3595ff4c5c684811f18525880d358369102a981bbfb"

    paths = [
        "runs/zag_discriminator_core_intersection/summary.json",
        "experiments/discriminator_core_intersection_law.py",
        "src/orbitsynthesis/discriminator_core.py",
        "notes/DISCRIMINATOR_CORE_INTERSECTION_LAW.md",
        "research/MORPH_DISCRIMINATOR_CORE_INTERSECTION_CERTIFICATE.md",
        "formal/OrbitSynthesis/CoreIntersection.lean",
    ]
    artifacts = {path: digest(root / path) for path in paths}

    atoms = [
        {
            "id": "q_core_intersection",
            "type": "QUESTION",
            "status": "TESTABLE",
            "content": "When does the intersection of two parameter-core polynomial clones of a finite pure discriminator collapse to their meet core?",
            "parents": [],
        },
        {
            "id": "claim_bounded_boundary",
            "type": "CLAIM",
            "status": "SUPPORTED",
            "content": "Across all 87,376 ordered core pairs on carriers of sizes two through eight, collapse-boundary predictions agree with transposition-support connectivity; all 8,828 exceptional cover pairs have checked strict witnesses.",
            "parents": ["q_core_intersection"],
        },
        {
            "id": "claim_exact_law",
            "type": "CLAIM",
            "status": "UNDER_TEST",
            "content": "For arity greater than one, meet collapse fails exactly for incomparable core pairs whose union is the whole carrier.",
            "parents": ["claim_bounded_boundary"],
        },
        {
            "id": "claim_cover_count",
            "type": "CLAIM",
            "status": "UNDER_TEST",
            "content": "The binary intersection size of an incomparable cover with block sizes (e,x,y) is e^(e^2)(e+1)^(4e+2)(e+2)^(2+[x>=2]+[y>=2]).",
            "parents": ["claim_exact_law"],
        },
        {
            "id": "claim_minimal_family_bound",
            "type": "CLAIM",
            "status": "UNDER_TEST",
            "content": "Distinct inclusion-minimal feasible cores pairwise cover the carrier, so their complements are disjoint and their multiplicity is at most the carrier size.",
            "parents": ["claim_exact_law"],
        },
        {
            "id": "hyp_universal_meet_collapse",
            "type": "HYPOTHESIS",
            "status": "REFUTED",
            "content": "Every pair of parameter cores collapses to the meet clone.",
            "parents": ["q_core_intersection"],
        },
        {
            "id": "cx_cover_pair",
            "type": "COUNTEREXAMPLE",
            "status": "REFUTED",
            "content": "For any incomparable full-cover pair C,D, the branch-selector witness belongs to both clones but not the meet clone.",
            "parents": ["hyp_universal_meet_collapse"],
        },
        {
            "id": "open_realizability",
            "type": "OPEN_PROBLEM",
            "status": "UNKNOWN",
            "content": "Determine whether every family whose core complements are pairwise disjoint is realizable as a minimal-core family at some arity.",
            "parents": ["claim_minimal_family_bound"],
        },
        {
            "id": "risk_lean_replay",
            "type": "RISK",
            "status": "UNDER_TEST",
            "content": "The abstract Lean consequence contains no placeholders, but compiler replay remains an infrastructure gate.",
            "parents": ["claim_minimal_family_bound"],
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
    edges.extend(
        [
            {
                "source_atom_id": "cx_cover_pair",
                "target_atom_id": "hyp_universal_meet_collapse",
                "edge_type": "REFUTES",
            },
            {
                "source_atom_id": "claim_bounded_boundary",
                "target_atom_id": "claim_exact_law",
                "edge_type": "TESTS",
            },
            {
                "source_atom_id": "risk_lean_replay",
                "target_atom_id": "claim_minimal_family_bound",
                "edge_type": "TESTS",
            },
        ]
    )
    report = {
        "schema": "research_kernel/report/v1",
        "supported_claims": [atom for atom in atoms if atom["status"] == "SUPPORTED"],
        "refuted_claims": [atom for atom in atoms if atom["status"] == "REFUTED"],
        "frontier": [
            atom for atom in atoms
            if atom["status"] in {"TESTABLE", "UNDER_TEST", "UNKNOWN"}
        ],
        "artifacts": artifacts,
        "semantic_sha256": summary["semantic_sha256"],
        "non_claims": [
            "The arbitrary-carrier theorem is a paper derivation and remains UNDER_TEST in the promotion ledger.",
            "The Lean file formalizes only the abstract minimal-core consequence, not the discriminator stabilizer theorem.",
            "Publication novelty and general realizability are unresolved.",
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

#!/usr/bin/env python3
"""Write a fail-closed Research Kernel packet for the core-antichain witness."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    summary = json.loads((root / "runs/zag_fixed_domain_core_antichain/summary.json").read_text())
    api = summary["api_witness"]
    census = summary["direct_census"]
    assert api["minimum_rank_cores"] == [[0, 1], [0, 2]]
    assert api["least_core"] is None
    assert census["minimum_core_multiplicity_counts"] == {"1": 18151, "2": 1488, "3": 44}
    paths = [
        "runs/zag_fixed_domain_core_antichain/summary.json",
        "experiments/quasiprimal_fixed_domain_core_antichain.py",
        "src/orbitsynthesis/fixed_domain.py",
        "formal/OrbitSynthesis/TableSafetyReduction.lean",
        "notes/FIXED_DOMAIN_PARAMETER_CORE_ANTICHAIN.md",
    ]
    artifacts = {path: digest(root / path) for path in paths}
    atoms = [
        {"id": "q", "type": "QUESTION", "status": "TESTABLE", "content": "Must one fixed winning domain have a least adequate parameter core?", "parents": []},
        {"id": "reduction", "type": "CLAIM", "status": "UNDER_TEST", "content": "Operation-table membership reduces exactly to full-domain graph safety.", "parents": ["q"]},
        {"id": "witness", "type": "CLAIM", "status": "SUPPORTED", "content": "The discriminator graph game has incomparable minimum cores {0,1} and {0,2} and no least core.", "parents": ["reduction"]},
        {"id": "census", "type": "CLAIM", "status": "SUPPORTED", "content": "Of 19683 binary tables, 1488 have two minimum cores and 44 have three.", "parents": ["witness"]},
        {"id": "unique", "type": "HYPOTHESIS", "status": "REFUTED", "content": "Every fixed-domain instance has one least adequate core.", "parents": ["q"]},
        {"id": "open", "type": "OPEN_PROBLEM", "status": "UNKNOWN", "content": "Characterize realizable minimum-core antichains.", "parents": ["census"]},
    ]
    edges = [{"source_atom_id": atom["id"], "target_atom_id": parent, "edge_type": "DEPENDS_ON"} for atom in atoms for parent in atom["parents"]]
    edges.append({"source_atom_id": "witness", "target_atom_id": "unique", "edge_type": "REFUTES"})
    report = {
        "schema": "research_kernel/report/v1",
        "supported_claims": [atom for atom in atoms if atom["status"] == "SUPPORTED"],
        "refuted_claims": [atom for atom in atoms if atom["status"] == "REFUTED"],
        "frontier": [atom for atom in atoms if atom["status"] in {"TESTABLE", "UNDER_TEST", "UNKNOWN"}],
        "artifacts": artifacts,
        "non_claims": ["Generic reduction remains UNDER_TEST until Lean compiler replay."],
    }
    args.out_root.mkdir(parents=True, exist_ok=True)
    for name, rows in (("atoms.jsonl", atoms), ("edges.jsonl", edges)):
        (args.out_root / name).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    (args.out_root / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()

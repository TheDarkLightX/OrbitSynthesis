#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
AUDIT = ROOT / "research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge_reconstruction"
ORDER = ROOT / "research/tournaments/2026-08-13-semantic-router-frontier/lanes/order_pair_program_vector"
EXPECTED = {
    "order_pair": (ORDER / "receipt.json", "orbit-synthesis/order-pair-program-vector/v1", "bc2378444813857cb3943fff3b45164e21a486fc588b89c9125e6fbdbc2fd83d"),
    "bridge": (AUDIT / "receipt.json", "orbit-synthesis/order-pair-integrated-compiler/v1", "b0dec4c34465d5b25e5aa35e59ac6016452afcb9df1307bbb6b52b5399b81e23"),
    "constant_15": (AUDIT / "receipt_constant_15.json", "orbit-synthesis/order-pair-integrated-constant-15/v1", "ad37969af91fee138674e66151ed1c55c6b4428f5786dce56a44e78744c25193"),
    "adaptive": (AUDIT / "receipt_adaptive_113_8.json", "orbit-synthesis/order-pair-adaptive-113-over-8/v1", "fb4bb1f1cac137e8bbe22a47070b733858009d60d6f3d2ddc755951ff1380142"),
    "hierarchical": (AUDIT / "receipt_hierarchical_49_5.json", "orbit-synthesis/order-pair-hierarchical-49-over-5/v1", "ea6d5cf35755fd04cc69b040af1152ae3f72e8a6c4d41a65cc0256551929c520"),
}
PROMOTED = {
    "OPV_EXACT",
    "BRIDGE_BOUNDED_SEMANTICS",
    "BRIDGE_34",
    "BRIDGE_15",
    "BRIDGE_113_8",
    "BRIDGE_49_5",
}
HELD = {
    "BYTE_EXACT_LOCAL_EQUIVALENCE",
    "PUBLICATION_NOVELTY",
    "EXTERNAL_REFEREE",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    bindings = {}
    for name, (path, schema, semantic) in EXPECTED.items():
        data = load(path)
        assert data["schema"] == schema
        assert data["semantic_sha256"] == semantic
        bindings[name] = {"schema": schema, "semantic_sha256": semantic}

    atoms_data = load(HERE / "atoms.json")
    edges_data = load(HERE / "edges.json")
    atoms = {item["id"]: item for item in atoms_data["atoms"]}
    assert len(atoms) == len(atoms_data["atoms"])
    assert all(atoms[name]["status"] == "SUPPORTED" for name in PROMOTED)
    assert all(atoms[name]["status"] == "UNKNOWN" for name in HELD)
    assert atoms["HOSTED_CI"]["status"] == "BLOCKED_INFRASTRUCTURE"
    assert all(
        edge["from"] in atoms and edge["to"] in atoms
        for edge in edges_data["edges"]
    )

    result = {
        "schema": "orbit-synthesis/research-kernel-integrated-reconstruction/v1",
        "status": "PASS",
        "promoted": sorted(PROMOTED),
        "not_promoted": sorted(HELD),
        "infrastructure": {"HOSTED_CI": "BLOCKED_INFRASTRUCTURE"},
        "bindings": bindings,
        "atom_count": len(atoms),
        "edge_count": len(edges_data["edges"]),
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(raw).hexdigest()
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

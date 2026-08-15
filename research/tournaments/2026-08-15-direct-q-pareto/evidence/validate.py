#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANE = HERE.parent
ROOT = LANE.parents[2]
EXPECTED = {
    "pareto": (
        LANE / "receipt.json",
        "orbit-synthesis/direct-q-pareto-size-8/v1",
        "9a121cea2251c4039dde487bddf3b7477d434f4134e2c63d1515639143182a41",
    ),
    "mux_minimality": (
        LANE / "receipt_mux_minimality.json",
        "orbit-synthesis/direct-q-mux-minimality/v1",
        "f3c706a0b912e1a492bfefffe9ae0af33777ea2acd6d245d00212c3c24d6e45f",
    ),
}
PROMOTED = {
    "DIRECT_Q_MUX_CORRECT",
    "DIRECT_Q_MUX_MINIMAL",
    "DIRECT_Q_CODE_BRIDGE",
    "PARETO_BOUNDED_SEMANTICS",
    "PARETO_SIZE_8",
    "PARETO_DEPTH_6LOG",
}
UNDER_TEST = {"DIRECT_Q_LEAN"}
UNKNOWN = {"GLOBAL_PARETO_OPTIMALITY", "PUBLICATION_NOVELTY"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    bindings = {}
    for name, (path, schema, semantic) in EXPECTED.items():
        data = load(path)
        if data.get("schema") != schema:
            raise AssertionError(f"{name}: schema drift")
        if data.get("semantic_sha256") != semantic:
            raise AssertionError(f"{name}: semantic drift")
        bindings[name] = {"schema": schema, "semantic_sha256": semantic}

    atoms_data = load(HERE / "atoms.json")
    edges_data = load(HERE / "edges.json")
    atoms = {atom["id"]: atom for atom in atoms_data["atoms"]}
    if len(atoms) != len(atoms_data["atoms"]):
        raise AssertionError("duplicate atom id")
    if not all(atoms[name]["status"] == "SUPPORTED" for name in PROMOTED):
        raise AssertionError("supported-atom drift")
    if not all(atoms[name]["status"] == "UNDER_TEST" for name in UNDER_TEST):
        raise AssertionError("formal-status drift")
    if not all(atoms[name]["status"] == "UNKNOWN" for name in UNKNOWN):
        raise AssertionError("unsafe promotion")

    valid_edge_types = {"supports", "insufficient_for", "not_required"}
    for edge in edges_data["edges"]:
        if edge["from"] not in atoms or edge["to"] not in atoms:
            raise AssertionError("edge references unknown atom")
        if edge["type"] not in valid_edge_types:
            raise AssertionError("unknown edge type")

    lean_source = (LANE / "DirectQMux.lean").read_text(encoding="utf-8")
    forbidden = re.compile(
        r"(^|[^A-Za-z0-9_])(sorry|admit)([^A-Za-z0-9_]|$)"
        r"|^[ \t]*(axiom|unsafe)[ \t]",
        re.MULTILINE,
    )
    if forbidden.search(lean_source):
        raise AssertionError("forbidden Lean placeholder or declaration")

    result = {
        "schema": "orbit-synthesis/direct-q-pareto-evidence/v1",
        "status": "PASS",
        "promoted": sorted(PROMOTED),
        "under_test": sorted(UNDER_TEST),
        "unknown": sorted(UNKNOWN),
        "bindings": bindings,
        "atom_count": len(atoms),
        "edge_count": len(edges_data["edges"]),
        "lean_source_sha256": hashlib.sha256(lean_source.encode()).hexdigest(),
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

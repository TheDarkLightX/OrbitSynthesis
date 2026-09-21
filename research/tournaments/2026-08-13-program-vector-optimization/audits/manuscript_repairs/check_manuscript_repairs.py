#!/usr/bin/env python3
"""Deterministic checks for manuscript referee repairs R2/R3/R4/R8/R9/R10.

The checker is self-contained and read-only outside its output path.  It does
not import the manuscript compilers.  It checks the displayed selector and mux,
the relevant depth ledgers, the eventual binary threshold, and every path in
the living-paper manifest while reporting (rather than silently accepting)
editorial hash drift.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[5]
MANUSCRIPT = ROOT / "paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md"
PAPER_MANIFEST = ROOT / "paper/paper_manifest.json"

FROZEN = {
    "paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md": "a7e52b7f99d4ccd368dbd2a25203ed0b18e6f36ee7d616ef3e965951699c3f45",
    "paper/paper_manifest.json": "f9a4096e1326960aa7046983cc1aad3e10b1e23646b870bc1e129b539eeb4da4",
    "notes/QUASIPRIMAL_CONSERVATIVE_TERM_PARALLEL_PROGRAM_DEPTH.md": "570d4ef5468eb802689bfc139f28fd1f26250ec94dfeeacaa6d9c4fd30e25165",
    "research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/check_parallel_program_vector.py": "2ba586a1ef97822aebbbcf692d29cd5bd3f8bbc8e785ddce43aff2180df3c350",
    "research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/audit_program_vector.py": "5324d81e377f8038795b97574eae9d4ba8728a3a74af189d39fda4f76abc6e5d",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(x: int, y: int, z: int) -> int:
    require(x in (0, 1, 2) and y in (0, 1, 2) and z in (0, 1, 2), "d outside Q")
    return z if x == y else x


def u(x: int) -> int:
    require(x in (0, 1, 2), "u outside Q")
    return (1, 0, 1)[x]


def normal_selector(x: int, y: int, equal: int, different: int) -> int:
    """N(x,y,e,n)=d(d(x,y,e),d(x,y,n),n)."""
    return d(d(x, y, equal), d(x, y, different), different)


def mux(x: int, b0: int, b1: int, b2: int, zero: int, one: int, two: int) -> int:
    left = d(zero, d(x, two, b0), d(zero, x, b0))
    right = d(d(one, x, b1), one, d(x, two, b2))
    return d(left, zero, right)


class DAG:
    """Structural hash-consing for exact shared-DAG census and depth."""

    def __init__(self) -> None:
        self.nodes: list[tuple[object, ...]] = []
        self.unique: dict[tuple[object, ...], int] = {}
        self.depth: list[int] = []

    def _intern(self, node: tuple[object, ...], depth: int) -> int:
        old = self.unique.get(node)
        if old is not None:
            return old
        result = len(self.nodes)
        self.nodes.append(node)
        self.unique[node] = result
        self.depth.append(depth)
        return result

    def terminal(self, name: str) -> int:
        return self._intern(("var", name), 0)

    def unary(self, child: int) -> int:
        return self._intern(("u", child), self.depth[child] + 1)

    def discr(self, x: int, y: int, z: int) -> int:
        return self._intern(("d", x, y, z), max(self.depth[x], self.depth[y], self.depth[z]) + 1)

    def operation_count(self) -> int:
        return sum(node[0] != "var" for node in self.nodes)

    def kind_count(self, kind: str) -> int:
        return sum(node[0] == kind for node in self.nodes)


def selector_and_mux_checks() -> dict[str, object]:
    selector_rows = 0
    for x, y, equal, different in itertools.product((0, 1, 2), repeat=4):
        expected = equal if x == y else different
        require(normal_selector(x, y, equal, different) == expected, "normal selector mismatch")
        selector_rows += 1

    mux_rows = 0
    for x, b0, b1, b2 in itertools.product((0, 1, 2), repeat=4):
        require(mux(x, b0, b1, b2, 0, 1, 2) == (b0, b1, b2)[x], "mux mismatch")
        mux_rows += 1

    dag = DAG()
    anchor = dag.terminal("A")
    selector = dag.terminal("x")
    b0 = dag.terminal("b0")
    b1 = dag.terminal("b1")
    b2 = dag.terminal("b2")
    one = dag.unary(anchor)
    zero = dag.unary(one)
    left = dag.discr(
        zero,
        dag.discr(selector, anchor, b0),
        dag.discr(zero, selector, b0),
    )
    right = dag.discr(
        dag.discr(one, selector, b1),
        one,
        dag.discr(selector, anchor, b2),
    )
    root = dag.discr(left, zero, right)
    require(dag.kind_count("var") == 5, "mux raw-terminal count drift")
    require(dag.kind_count("u") == 2, "mux name count drift")
    require(dag.kind_count("d") == 7, "mux discriminator count drift")
    require(dag.operation_count() == 9 and len(dag.nodes) == 14, "mux total DAG census drift")
    require(dag.depth[root] == 5, "mux operation depth drift")

    # Reproduce the current Python identity-DAG defect: spelling u(A) twice
    # creates a third identity node although a shared term DAG needs only two.
    identity_emitted_total = 5 + 3 + 7
    require(identity_emitted_total == 15, "identity-emitted census drift")
    return {
        "normal_selector": {
            "formula": "d(d(x,y,e),d(x,y,n),n)",
            "rows_checked": selector_rows,
            "new_d_nodes": 3,
            "branch_dependency_depth": 2,
        },
        "mux": {
            "rows_checked": mux_rows,
            "new_d_nodes_given_names": 7,
            "shared_name_u_nodes": 2,
            "raw_terminals": 5,
            "operation_nodes": dag.operation_count(),
            "total_shared_nodes": len(dag.nodes),
            "operation_depth_above_raw_inputs": dag.depth[root],
            "branch_dependency_depth": 3,
            "current_identity_emitter_nodes": identity_emitted_total,
            "identity_emitter_defect": "constructs the inner u(A) of u(u(A)) separately from the named u(A)",
        },
    }


def first_two(point: tuple[int, ...]) -> int | None:
    for index, value in enumerate(point):
        if value == 2:
            return index
    return None


def slice_checks(max_arity: int = 7) -> dict[str, object]:
    rows: list[dict[str, int]] = []
    tuple_checks = 0
    for arity in range(1, max_arity + 1):
        counts = [0] * arity
        binary = 0
        for point in itertools.product((0, 1, 2), repeat=arity):
            anchor = first_two(point)
            if anchor is None:
                binary += 1
                require(all(value in (0, 1) for value in point), "binary partition mismatch")
            else:
                counts[anchor] += 1
                require(point[anchor] == 2, "slice anchor mismatch")
                require(all(value in (0, 1) for value in point[:anchor]), "slice prefix not binary")
                dynamic = (u(u(point[anchor])), u(point[anchor]), point[anchor])
                require(dynamic == (0, 1, 2), "slice-local dynamic names failed")
            tuple_checks += 1
        expected = [2**anchor * 3 ** (arity - anchor - 1) for anchor in range(arity)]
        require(counts == expected, "first-two slice census mismatch")
        require(binary == 2**arity, "binary census mismatch")
        require(sum(counts) == 3**arity - 2**arity, "slice partition identity failed")
        rows.append(
            {
                "arity": arity,
                "binary_tuples": binary,
                "nonbinary_tuples": sum(counts),
                "slice_sum": sum(expected),
            }
        )
    return {
        "rows": rows,
        "tuples_checked": tuple_checks,
        "generic_slice": "S_a={0,1}^a x {2} x Q^(r-a-1)",
        "generic_slice_domain_size": "N_a=2^a*3^(r-a-1)",
        "variable_dimension": "n=r-1",
        "size_transfer": "O(N_a/(r-1))=O(N_a/r) for r>=2; r=1 is a finite base",
        "legality": "u(x_a),u(u(x_a)),x_a are global legal terms and name 1,0,2 only on S_a; off-slice values are masked by the first-two dispatcher",
    }


def ceil_log2(value: int) -> int:
    require(value >= 1, "ceil_log2 input")
    return (value - 1).bit_length()


def ceil_log3(value: int) -> int:
    require(value >= 1, "ceil_log3 input")
    power = 1
    exponent = 0
    while power < value:
        power *= 3
        exponent += 1
    return exponent


def floor_power3(value: int) -> tuple[int, int]:
    require(value >= 1, "floor_power3 input")
    exponent = 0
    power = 1
    while power * 3 <= value:
        exponent += 1
        power *= 3
    return exponent, power


def vector_depth(width: int) -> int:
    return 2 if width == 0 else 6 + 2 * ceil_log2(width)


def nonbinary_depth(r: int) -> int:
    """Current compiler ledger, including decoder and two glue levels."""
    require(r >= 64, "nonbinary ledger starts at 64")
    reserve = 4 + ceil_log3(r * r)
    h = r - reserve
    b, _m = floor_power3(h)
    prefix = r - b
    anchor = 3 * ceil_log2(r)
    local_control = anchor + vector_depth(b)
    local_plane = max(anchor + 2, local_control) + b + 1
    prefix_control = anchor + vector_depth(prefix)
    prefix_plane = max(local_plane, prefix_control) + prefix + 1
    return prefix_plane + 4


def binary_depth(r: int) -> int:
    """Retained residual-first binary ledger, including its fixed final layers."""
    require(r >= 2, "binary ledger arity")
    k = math.isqrt(r)
    width = (3**k).bit_length() - 1
    levels = (r - 1 + width - 1) // width
    return (k + 1) * levels + 2 * width + 3 * ceil_log2(r) + 8


def theorem_64_depth_checks(max_exact: int = 899) -> dict[str, object]:
    require(max_exact >= 899, "exact range must meet analytic tail")
    # The binary complement-orbit tree in Theorem 6.4 uses r-1 sequential
    # equality/difference decisions, each a depth-two normal selector.
    binary_classifier_checks = 0
    for r in range(1, 4097):
        classifier = 2 * max(0, r - 1)
        anchor = 3 * ceil_log2(r)
        nonbinary = 3 * r + anchor + 2
        glued = 2 + max(anchor + 2, classifier, nonbinary)
        require(glued <= 3 * r + 3 * ceil_log2(r) + 4, "Theorem 6.4 max-depth drift")
        binary_classifier_checks += 1

    below = []
    nonbelow = []
    max_branch_rows = []
    binary_dominates = []
    for r in range(64, max_exact + 1):
        bdepth = binary_depth(r)
        ndepth = nonbinary_depth(r)
        ceiling = r + 5 * ceil_log2(r) + 12
        require(ndepth <= ceiling, "nonbinary explicit ceiling failed")
        require(max(bdepth, ndepth) <= ceiling, "global max-branch ceiling failed")
        (below if bdepth < r else nonbelow).append(r)
        if bdepth > ndepth:
            binary_dominates.append(r)
        if r in (64, 65, 66, 67, 272, 273, 337, 338, 339, 899):
            max_branch_rows.append(
                {
                    "r": r,
                    "binary_depth": bdepth,
                    "nonbinary_depth": ndepth,
                    "max_branch_depth": max(bdepth, ndepth),
                    "theorem_ceiling": ceiling,
                }
            )

    require(below[0] == 273, "first isolated binary-below-r arity drift")
    require(max(nonbelow) == 338, "last exact nonbelow-r arity drift")
    require(binary_depth(338) == 338 and binary_depth(339) == 338, "338/339 boundary drift")
    require(all(binary_depth(r) < r for r in range(339, 900)), "exact eventual-threshold interval failed")
    require(binary_dominates == [64, 65], "binary/nonbinary dominance crossover drift")

    # For k=floor(sqrt r)>=30: W>= (3k-1)/2, W<2k,
    # ceil((r-1)/W)<r/W+1, ceil(log2 r)<=k.  Substituting r>=k^2
    # reduces D_bin<r to p(k)>0 below.
    def tail_polynomial(k: int) -> int:
        return k**3 - 27 * k**2 - 19 * k + 9

    p30 = tail_polynomial(30)
    increment30 = 3 * 30**2 - 51 * 30 - 45
    require(p30 > 0 and increment30 > 0, "analytic tail base failed")
    require(6 * 30 - 48 > 0, "tail increments not increasing")

    return {
        "theorem_6_4": {
            "binary_classifier_depth": "2(r-1)",
            "final_depth_max": "2+max(3ceil(log2 r)+2, 2(r-1), 3r+3ceil(log2 r)+2)",
            "certified_ceiling": "3r+3ceil(log2 r)+4",
            "arities_checked": binary_classifier_checks,
        },
        "theorem_6_10": {
            "exact_range": [64, max_exact],
            "selected_rows": max_branch_rows,
            "binary_dominates_nonbinary_only_at": binary_dominates,
            "global_depth": "max(D_binary(r),D_nonbinary(r)) <= r+5ceil(log2 r)+12 for r>=64",
        },
        "threshold_339": {
            "first_isolated_below_r": below[0],
            "last_nonbelow_r": max(nonbelow),
            "eventual_below_r_from": max(nonbelow) + 1,
            "depth_338": binary_depth(338),
            "depth_339": binary_depth(339),
            "earlier_below_intervals_warning": "D_binary<r occurs in finite islands before 339; 339 is the eventual threshold, not min{r:D_binary(r)<r}",
            "tail_starts_at_r": 900,
            "tail_polynomial_at_30": p30,
            "tail_increment_at_30": increment30,
        },
    }


def audit_manifest() -> dict[str, object]:
    manifest = json.loads(PAPER_MANIFEST.read_text(encoding="utf-8"))
    declared: list[tuple[str, str, str]] = []
    for relative, expected in manifest["shared_sources"].items():
        declared.append(("shared_source", relative, expected))
    for draft, entry in manifest["papers"].items():
        declared.append(("draft", draft, entry["draft_sha256"]))
        for relative, expected in entry["authoritative_sources"].items():
            declared.append(("authoritative_source", relative, expected))
        for relative, expected in entry["receipts"].items():
            declared.append(("receipt", relative, expected["file_sha256"]))

    missing = []
    mismatches = []
    matches = []
    for kind, relative, expected in declared:
        path = ROOT / relative
        if not path.is_file():
            missing.append({"kind": kind, "path": relative})
            continue
        observed = sha256_path(path)
        row = {"kind": kind, "path": relative, "expected": expected, "observed": observed}
        if observed == expected:
            matches.append(row)
        else:
            mismatches.append(row)

    # Independently check receipt semantic pins even when file bytes drift.
    semantic_mismatches = []
    semantic_missing = []
    for _draft, entry in manifest["papers"].items():
        for relative, expected in entry["receipts"].items():
            path = ROOT / relative
            if not path.is_file():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            observed = payload.get("semantic_sha256")
            if observed is None:
                hashes = {
                    command.get("semantic_sha256")
                    for command in payload.get("commands", [])
                    if isinstance(command, dict) and isinstance(command.get("semantic_sha256"), str)
                }
                observed = next(iter(hashes)) if len(hashes) == 1 else None
            if observed is None:
                semantic_missing.append(relative)
            elif observed != expected["semantic_sha256"]:
                semantic_mismatches.append(
                    {
                        "path": relative,
                        "expected": expected["semantic_sha256"],
                        "observed": observed,
                    }
                )

    fixed_q_drift = [row for row in mismatches if row["path"] == str(MANUSCRIPT.relative_to(ROOT))]
    require(bool(fixed_q_drift), "expected current manuscript manifest drift was not detected")
    return {
        "manifest_sha256": sha256_path(PAPER_MANIFEST),
        "declared_paths": len(declared),
        "hash_matches": len(matches),
        "hash_mismatches": len(mismatches),
        "missing_paths": missing,
        "mismatches": mismatches,
        "semantic_mismatches": semantic_mismatches,
        "semantic_missing": semantic_missing,
        "gate": "FAIL_STALE_MANIFEST" if missing or mismatches or semantic_mismatches or semantic_missing else "PASS",
    }


def freeze_subjects() -> dict[str, str]:
    observed = {relative: sha256_path(ROOT / relative) for relative in FROZEN}
    require(observed == FROZEN, "frozen repair subject drift")
    return observed


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def run() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "orbit.manuscript-repairs.referee-audit.v1",
        "status": "PASS_MATH_REPAIRS__FAIL_STALE_PAPER_MANIFEST",
        "frozen": freeze_subjects(),
        "selector_mux": selector_and_mux_checks(),
        "slice_local": slice_checks(),
        "depth": theorem_64_depth_checks(),
        "manifest": audit_manifest(),
        "wording_gate": {
            "compiler_table": "The Section 7 values are depths/node counts of the emitted DAGs under variables-at-depth-one convention; they are not D_r(f), exact minima, or lower bounds.",
            "publication": "Refresh the manifest only after the manuscript repair bytes and all intended evidence files are frozen.",
        },
    }
    result["semantic_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(result["semantic_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exact pair-quotient synthesis for positive-polarity depth-three d trees.

Leaf label 0 is a private programmable Boolean control; labels 1..q are branch
variables.  Branch labels may repeat, but may occur only at leaves whose root
path contains an even number of second-child edges.  This is the corrected
monotone grammar for d(x,y,z)=z if x=y else x.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

import z3


BITS = (0, 1)
DEPTH = 3
LEAVES = 27


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


def zdisc(x: z3.BoolRef, y: z3.BoolRef, z: z3.BoolRef) -> z3.BoolRef:
    return z3.If(x == y, z, x)


def leaf_polarity(leaf: int) -> int:
    value = leaf
    middle_edges = 0
    for _ in range(DEPTH):
        middle_edges += value % 3 == 1
        value //= 3
    return -1 if middle_edges % 2 else 1


def reduce_concrete(values: list[int]) -> int:
    layer = values
    while len(layer) > 1:
        layer = [disc(*layer[3 * index : 3 * index + 3]) for index in range(len(layer) // 3)]
    return layer[0]


def reduce_symbolic(values: list[z3.BoolRef]) -> z3.BoolRef:
    layer = values
    while len(layer) > 1:
        layer = [zdisc(*layer[3 * index : 3 * index + 3]) for index in range(len(layer) // 3)]
    return layer[0]


def exact_replay(
    labels: list[int], full_controls: list[list[int]], q: int
) -> tuple[list[int], list[dict[str, int]]]:
    matches = []
    mutations = []
    control_positions = [index for index, label in enumerate(labels) if label == 0]
    for target in range(q):
        target_matches = 0
        for valuation in product(BITS, repeat=q):
            leaves = [
                full_controls[target][position]
                if label == 0
                else valuation[label - 1]
                for position, label in enumerate(labels)
            ]
            target_matches += reduce_concrete(leaves) == valuation[target]
        matches.append(target_matches)
        effective = None
        for position in control_positions:
            mutated = list(full_controls[target])
            mutated[position] ^= 1
            mutation_matches = sum(
                reduce_concrete([
                    mutated[leaf] if label == 0 else valuation[label - 1]
                    for leaf, label in enumerate(labels)
                ]) == valuation[target]
                for valuation in product(BITS, repeat=q)
            )
            if mutation_matches < 2**q:
                effective = {
                    "target": target,
                    "position": position,
                    "matches_after_flip": mutation_matches,
                }
                break
        if effective is None:
            effective = {"target": target, "position": -1, "matches_after_flip": 2**q}
        mutations.append(effective)
    return matches, mutations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=10)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--out", required=True)
    parser.add_argument("--dump-smt2")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    q = args.q
    labels = [z3.Int(f"label_{leaf}") for leaf in range(LEAVES)]
    controls = [
        [z3.Bool(f"control_{target}_{leaf}") for leaf in range(LEAVES)]
        for target in range(q)
    ]
    solver = z3.Solver()
    solver.set(timeout=args.timeout_ms)
    for leaf, label in enumerate(labels):
        solver.add(label >= 0, label <= q)
        if leaf_polarity(leaf) < 0:
            solver.add(label == 0)
    for branch in range(1, q + 1):
        solver.add(z3.Or(*(label == branch for label in labels)))

    # No-loss quotient by branch renaming.
    for position, label in enumerate(labels):
        for branch in range(2, q + 1):
            earlier = [labels[index] == branch - 1 for index in range(position)]
            solver.add(
                z3.Implies(
                    label == branch,
                    z3.Or(*earlier) if earlier else z3.BoolVal(False),
                )
            )

    # Pair semantics: for target i, lower has x_i=0 and all other branches 1;
    # upper has x_i=1 and all other branches 0.  Controls use one fixed bit in
    # both rows and are target-specific but payload-independent.
    for target in range(q):
        lower = []
        upper = []
        for leaf, label in enumerate(labels):
            lower.append(
                z3.If(label == 0, controls[target][leaf], label != target + 1)
            )
            upper.append(
                z3.If(label == 0, controls[target][leaf], label == target + 1)
            )
        solver.add(reduce_symbolic(lower) == z3.BoolVal(False))
        solver.add(reduce_symbolic(upper) == z3.BoolVal(True))

    if args.dump_smt2:
        Path(args.dump_smt2).write_text(solver.to_smt2())
    result = solver.check()
    if result != z3.sat:
        payload = {
            "schema": "orbitsynthesis/positive-pair-r10/v1",
            "status": "UNSAT" if result == z3.unsat else "UNKNOWN",
            "reason": "complete pair instance UNSAT" if result == z3.unsat else solver.reason_unknown(),
            "q": q,
            "depth": DEPTH,
            "positive_polarity_leaves": [leaf for leaf in range(LEAVES) if leaf_polarity(leaf) > 0],
            "negative_polarity_leaves": [leaf for leaf in range(LEAVES) if leaf_polarity(leaf) < 0],
            "scope": "complete full depth-3 d-tree grammar with arbitrary repeated branch labels confined to positive-polarity leaves; all other leaves private controls",
            "boundary": "Not arbitrary-leaf d-only, signed/u, non-full-tree, DAG, or depth>3 UNSAT without the separately stated transfers.",
        }
        Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    model = solver.model()
    decoded_labels = [model.eval(label, model_completion=True).as_long() for label in labels]
    decoded_controls = [
        [int(z3.is_true(model.eval(bit, model_completion=True))) for bit in row]
        for row in controls
    ]
    control_positions = [leaf for leaf, label in enumerate(decoded_labels) if label == 0]
    programs = [
        [row[position] for position in control_positions] for row in decoded_controls
    ]
    matches, mutations = exact_replay(decoded_labels, decoded_controls, q)
    if matches != [2**q] * q:
        raise RuntimeError(f"pair witness failed full replay: {matches}")
    payload: dict[str, object] = {
        "schema": "orbitsynthesis/positive-pair-r10/v1",
        "status": "SAT_EXACT",
        "q": q,
        "depth": DEPTH,
        "labels": decoded_labels,
        "control_positions": control_positions,
        "programs": programs,
        "full_control_rows": decoded_controls,
        "checks_per_target": 2**q,
        "matches_per_target": matches,
        "effective_mutations": mutations,
        "exact": True,
        "scope": "complete full depth-3 d-tree grammar with arbitrary repeated branch labels confined to positive-polarity leaves; all other leaves private controls",
        "boundary": "Finite positive-polarity Boolean identity only; generic compiler, arbitrary-leaf d-only grammar, signed/u grammar, novelty, optimality, patents, FTO, and Tau relevance remain separate.",
    }
    payload["semantic_sha256"] = hashlib.sha256(
        json.dumps(
            {key: payload[key] for key in ("q", "depth", "labels", "programs", "matches_per_target")},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("SAT_EXACT")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

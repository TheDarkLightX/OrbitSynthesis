#!/usr/bin/env python3
"""Fail-closed audit of the proposed and corrected two-extreme lemmas."""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path


BITS = (0, 1)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


def majority(x: int, y: int, z: int) -> int:
    return int(x + y + z >= 2)


def is_monotone(table: tuple[int, ...], arity: int) -> bool:
    rows = tuple(product(BITS, repeat=arity))
    values = dict(zip(rows, table, strict=True))
    return all(
        values[left] <= values[right]
        for left in rows
        for right in rows
        if all(a <= b for a, b in zip(left, right, strict=True))
    )


def projection_table(arity: int, target: int) -> tuple[int, ...]:
    return tuple(row[target] for row in product(BITS, repeat=arity))


def extreme_pair(table: tuple[int, ...], arity: int, target: int) -> tuple[int, int]:
    rows = tuple(product(BITS, repeat=arity))
    values = dict(zip(rows, table, strict=True))
    lower = tuple(0 if index == target else 1 for index in range(arity))
    upper = tuple(1 if index == target else 0 for index in range(arity))
    return values[lower], values[upper]


def leaf_polarities(depth: int) -> tuple[int, ...]:
    result = []
    for leaf in range(3**depth):
        digits = []
        value = leaf
        for _ in range(depth):
            digits.append(value % 3)
            value //= 3
        result.append(-1 if sum(digit == 1 for digit in digits) % 2 else 1)
    return tuple(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args()
    truth_rows = []
    majority_mismatches = []
    twisted_mismatches = []
    complement_mismatches = []
    for x, y, z in product(BITS, repeat=3):
        value = disc(x, y, z)
        row = {
            "input": [x, y, z],
            "d": value,
            "majority_xyz": majority(x, y, z),
            "majority_x_noty_z": majority(x, 1 - y, z),
        }
        truth_rows.append(row)
        if value != row["majority_xyz"]:
            majority_mismatches.append(row)
        if value != row["majority_x_noty_z"]:
            twisted_mismatches.append(row)
        if disc(1 - x, 1 - y, 1 - z) != 1 - value:
            complement_mismatches.append(row)
    require(majority_mismatches, "incorrect majority identity unexpectedly survived")
    require(not twisted_mismatches, "correct twisted-majority identity failed")
    require(not complement_mismatches, "Boolean complement equivariance failed")

    # Minimal counterexample to the frozen proposal.  Controls are fixed at 0.
    # F(x0,x1)=d(x0,x1,0), target x0.
    f_table = tuple(disc(x0, x1, 0) for x0, x1 in product(BITS, repeat=2))
    f_extremes = extreme_pair(f_table, 2, 0)
    require(f_extremes == (0, 1), "counterexample no longer passes proposed extremes")
    require(f_table != projection_table(2, 0), "counterexample became a projection")
    counterexample = {
        "term": "d(x0,x1,0)",
        "target": "x0",
        "table_order_00_01_10_11": list(f_table),
        "proposed_extremes": list(f_extremes),
        "f_1_1": disc(1, 1, 0),
        "x0_at_1_1": 1,
    }

    # Exhaust all 3-ary Boolean functions to calibrate the corrected generic
    # theorem: among monotone functions, passing the two target extremes is
    # equivalent to being the corresponding projection.
    monotone_count = 0
    calibrated = 0
    for bits in product(BITS, repeat=8):
        if not is_monotone(bits, 3):
            continue
        monotone_count += 1
        for target in range(3):
            passes = extreme_pair(bits, 3, target) == (0, 1)
            is_projection = bits == projection_table(3, target)
            require(passes == is_projection, "corrected monotone lemma calibration failed")
            calibrated += 1
    require(monotone_count == 20, "Dedekind M(3) calibration drift")

    polarities = leaf_polarities(3)
    require(polarities.count(1) == 14 and polarities.count(-1) == 13, "polarity census drift")
    summary: dict[str, object] = {
        "schema": "orbitsynthesis/extreme-lemma-audit/v1",
        "actual_boolean_identity": "d(x,y,z)=majority(x,1-y,z)",
        "claimed_majority_identity_mismatch_count": len(majority_mismatches),
        "first_claimed_identity_counterexample": majority_mismatches[0],
        "twisted_majority_checks": len(truth_rows),
        "complement_equivariance_checks": len(truth_rows),
        "two_extreme_counterexample": counterexample,
        "corrected_theorem": "If F is monotone nondecreasing in every branch variable, then F=x_i iff F(x_i=0,others=1)=0 and F(x_i=1,others=0)=1.",
        "monotone_ternary_functions_checked": monotone_count,
        "monotone_target_checks": calibrated,
        "depth3_positive_polarity_leaves": [index for index, sign in enumerate(polarities) if sign == 1],
        "depth3_negative_polarity_leaves": [index for index, sign in enumerate(polarities) if sign == -1],
        "claim_boundary": "The frozen arbitrary-leaf quotient is refuted. The corrected theorem applies only when every branch occurrence has positive path polarity; negative-polarity leaves may be fixed controls.",
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS extreme-lemma audit")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

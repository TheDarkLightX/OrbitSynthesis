#!/usr/bin/env python3
"""Deterministic replay for the exact order-pair program-vector theorem."""

import argparse
import hashlib
import json
from pathlib import Path
from audit_core import (
    verify_arithmetic, verify_lower_bound,
    verify_materialization, verify_monoid,
)
from order_pair_model import vector_nodes


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate receipt field: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-finite receipt constant: {value}")


def check_expected(data, text):
    expected = json.loads(text, object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    # Python equality identifies 1 with True and 1.0. Receipt fields retain
    # their JSON types; only object ordering and whitespace may vary.
    if canonical(data) != canonical(expected):
        raise ValueError("generated receipt differs from committed receipt")


def make_receipt(semantic_width: int, lower_width: int, arithmetic_width: int):
    materialized, cases = verify_materialization(semantic_width)
    data = {
        "schema": "orbit-synthesis/order-pair-program-vector/v1",
        "claim": {
            "exact_size_recurrence":
                "C_s(w)=2+A(w)+X(ceil(w/2))-h_s(w), w>=2",
            "uniform_size_bound": "2*C_s(w) <= 5*3^w-1",
            "depth_bound": "3+ceil(log2(w))",
            "lower_bound": {
                "positive_root":
                    "4*3^w/3-1 distinct nonconstant outputs",
                "negative_root":
                    "4*3^w/3 distinct nonconstant outputs",
            },
            "asymptotic": "C_s(w)=(4/3+o(1))*3^w",
        },
        "parameters": {
            "semantic_width": semantic_width,
            "lower_bound_width": lower_width,
            "arithmetic_width": arithmetic_width,
        },
        "checks": {
            "monoid_and_mutation": verify_monoid(),
            "semantic_projection_cases": cases,
            "arithmetic_assertions": verify_arithmetic(arithmetic_width),
        },
        "materialized": materialized,
        "output_lower_bound": verify_lower_bound(lower_width),
        "ratio_samples": [
            {
                "width": width,
                "q": str(3**width),
                "negative_root_nodes": str(vector_nodes(width, True)),
                "nodes_over_q":
                    format(vector_nodes(width, True) / 3**width, ".12f"),
            }
            for width in (10, 20, 40)
        ],
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    data["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--semantic-width", type=int, default=7)
    parser.add_argument("--lower-bound-width", type=int, default=5)
    parser.add_argument("--arithmetic-width", type=int, default=500)
    parser.add_argument("--write-receipt", type=Path)
    parser.add_argument("--expected-receipt", type=Path)
    args = parser.parse_args()
    if not 1 <= args.semantic_width <= 8:
        raise SystemExit("semantic width must be 1..8")
    if not 2 <= args.lower_bound_width <= 6:
        raise SystemExit("lower-bound width must be 2..6")
    if args.arithmetic_width < 1:
        raise SystemExit("arithmetic width must be positive")

    data = make_receipt(
        args.semantic_width, args.lower_bound_width, args.arithmetic_width
    )
    rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.expected_receipt is not None:
        check_expected(data, args.expected_receipt.read_text(encoding="utf-8"))
    if args.write_receipt is not None:
        args.write_receipt.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

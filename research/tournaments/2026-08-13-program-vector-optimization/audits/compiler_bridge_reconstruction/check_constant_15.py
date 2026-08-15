#!/usr/bin/env python3
"""Audit the all-arity strengthening from 34 to 15 for the reconstructed bridge."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from compiler_bridge_model import (
    binary_node_upper,
    compiler_parameters,
    order_pair_vector_nodes,
    require,
    total_node_upper,
)


def check_sharp_vector_bound() -> dict[str, object]:
    checks = 0
    worst = (Fraction(0), 0)
    for width in range(7, 501):
        q = 3**width
        vector = order_pair_vector_nodes(width, False)
        require(2 * vector <= 3 * q, "3q/2 positive-vector bound")
        ratio = Fraction(vector, q)
        if ratio > worst[0]:
            worst = (ratio, width)
        checks += 1
    require(worst[1] == 7, "unexpected vector extremum")
    return {
        "widths": [7, 500],
        "checks": checks,
        "bound": "C_+(w)<=3*3^w/2",
        "worst_width": worst[1],
        "worst_decimal": format(float(worst[0]), ".15f"),
    }


def check_finite_range() -> dict[str, object]:
    worst = (Fraction(0), 0)
    checks = 0
    for arity in range(64, 512):
        total = total_node_upper(arity)
        require(total * arity < 15 * 3**arity, "finite 15-constant bound")
        ratio = Fraction(total * arity, 3**arity)
        if ratio > worst[0]:
            worst = (ratio, arity)
        checks += 1
    require(worst[1] == 93, "unexpected finite maximum")
    return {
        "arities": [64, 511],
        "checks": checks,
        "worst_arity": worst[1],
        "worst_decimal": format(float(worst[0]), ".15f"),
    }


def check_tail() -> dict[str, object]:
    checks = 0
    worst_binary = (Fraction(0), 0)
    for arity in range(512, 16385):
        ell, _, local, local_width, prefix, prefix_width = compiler_parameters(arity)
        require(32 * (ell + 4) <= arity, "tail logarithm reserve")
        require(96 * local > 31 * arity, "tail local lower bound")
        require(prefix_width >= 7, "prefix vector width")
        require(
            2 * order_pair_vector_nodes(prefix_width, False) <= 3 * prefix,
            "tail prefix-vector bound",
        )
        require(
            100
            * (order_pair_vector_nodes(local_width, False) + 4 * arity + 3)
            * arity
            < 3**arity,
            "tail lower-order bound",
        )
        require(
            4 * binary_node_upper(arity) * arity < 3 * 3**arity,
            "binary three-quarter bound",
        )
        binary_ratio = Fraction(binary_node_upper(arity) * arity, 3**arity)
        if binary_ratio > worst_binary[0]:
            worst_binary = (binary_ratio, arity)
        checks += 6
    return {
        "arities": [512, 16384],
        "checks": checks,
        "prefix_bound": "<(432/31)*3^r/r",
        "local_library_bound": "<(1/27)*3^r/r",
        "lower_order_bound": "<(1/100)*3^r/r",
        "binary_bound": "<(3/4)*3^r/r",
        "sum": "308278/20925<15",
        "worst_binary_arity": worst_binary[1],
        "worst_binary_decimal": format(float(worst_binary[0]), ".6e"),
    }


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "orbit-synthesis/order-pair-integrated-constant-15/v1",
        "status": "finite replay plus unbounded analytic-tail certificate",
        "vector": check_sharp_vector_bound(),
        "finite": check_finite_range(),
        "tail": check_tail(),
        "theorem": "total size <15*3^r/r for every r>=64",
        "depth": "<=r+4*ceil(log2 r)+9",
        "claim_boundary": (
            "The analytic proof uses the exact PR #15 recurrence, the explicit "
            "reconstructed compiler ledger, and the previously audited binary "
            "branch bounds. It is independent of the byte-exact 01ddf456 packet."
        ),
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(raw).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_receipt(), sort_keys=True, indent=2) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

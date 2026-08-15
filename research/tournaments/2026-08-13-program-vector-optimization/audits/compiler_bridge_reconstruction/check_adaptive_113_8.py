#!/usr/bin/env python3
"""Audit an adaptive order-pair compiler constant below 113/8."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from compiler_bridge_model import (
    binary_node_upper,
    ceil_log3,
    floor_log3,
    order_pair_vector_nodes,
    require,
)


def parameters(r: int) -> tuple[int, int, int, int, int, int]:
    ell = ceil_log3(r * r)
    headroom = r + 1 - ell
    b = floor_log3(headroom)
    local = 3**b
    s = r - b
    prefix = 3**s
    return ell, headroom, local, b, prefix, s


def total_nodes(r: int) -> int:
    _, _, local, b, prefix, s = parameters(r)
    return (
        (3 * local - 1) * 3**local
        + order_pair_vector_nodes(b, False)
        + (3 * prefix - 1)
        + order_pair_vector_nodes(s, False)
        + 4 * r
        + 3
        + binary_node_upper(r)
    )


def check_vector() -> dict[str, object]:
    worst = (Fraction(0), 0)
    for width in range(10, 501):
        q = 3**width
        count = order_pair_vector_nodes(width, False)
        require(20 * count <= 27 * q, "27q/20 vector bound")
        ratio = Fraction(count, q)
        if ratio > worst[0]:
            worst = (ratio, width)
    require(worst[1] == 10, "unexpected vector maximum")
    return {
        "widths": [10, 500],
        "checks": 491,
        "bound": "C_+(w)<=27*3^w/20",
        "worst_width": worst[1],
        "worst_decimal": format(float(worst[0]), ".15f"),
    }


def check_finite() -> dict[str, object]:
    worst = (Fraction(0), 0)
    for r in range(64, 1024):
        total = total_nodes(r)
        require(8 * total * r < 113 * 3**r, "finite 113/8 bound")
        ratio = Fraction(total * r, 3**r)
        if ratio > worst[0]:
            worst = (ratio, r)
    require(worst[1] == 88, "unexpected finite maximum")
    return {
        "arities": [64, 1023],
        "checks": 960,
        "worst_arity": worst[1],
        "worst_decimal": format(float(worst[0]), ".15f"),
    }


def check_tail() -> dict[str, object]:
    checks = 0
    cases = {"gap_equal": 0, "ratio_at_most_three": 0, "ratio_above_three": 0}
    for r in range(1024, 16385):
        ell, headroom, local, b, prefix, s = parameters(r)
        gap = r - local
        x = Fraction(r, local)
        lower = order_pair_vector_nodes(b, False) + 4 * r + 3
        binary = binary_node_upper(r)
        local_library = (3 * local - 1) * 3**local

        require(local <= headroom < 3 * local, "power bracketing")
        require(local >= 729 and b >= 6, "tail local floor")
        require(64 * (ell - 1) <= r, "tail logarithm reserve")
        require(21 * r < 64 * local, "tail block lower bound")
        require(ell <= 2 * b + 3, "logarithm conversion")
        require(50 * (ell - 1) <= local, "small transition offset")
        require(
            s >= 10 and 20 * order_pair_vector_nodes(s, False) <= 27 * prefix,
            "tail prefix-vector bound",
        )
        require(100 * lower * r < 3**r, "lower-order hundredth")
        require(100 * binary * r < 3**r, "binary hundredth")

        prefix_main = Fraction(87, 20) * x
        if gap == ell - 1:
            require(x <= Fraction(51, 50), "equal-gap ratio")
            main = Fraction(9, 1) / x + prefix_main
            require(main <= Fraction(267, 20), "equal-gap main bound")
            cases["gap_equal"] += 1
        else:
            require(gap >= ell, "gap dichotomy")
            if r <= 3 * local:
                main = Fraction(3, 1) / x + prefix_main
                require(main <= Fraction(281, 20), "ratio<=3 main bound")
                cases["ratio_at_most_three"] += 1
            else:
                require(
                    100 * local_library * r < 3**r,
                    "ratio>3 local hundredth",
                )
                require(
                    prefix_main < Fraction(13137, 1000),
                    "ratio>3 prefix bound",
                )
                cases["ratio_above_three"] += 1
        checks += 12

    require(all(value > 0 for value in cases.values()), "tail case not exercised")
    return {
        "arities": [1024, 16384],
        "checks": checks,
        "cases": cases,
        "vector_coefficient": "27/20",
        "lower_order": "<1/100",
        "binary": "<1/100",
        "tail_total": "<1407/100<113/8",
    }


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "orbit-synthesis/order-pair-adaptive-113-over-8/v1",
        "status": "exact finite replay plus analytic-tail certificate",
        "parameter_rule": "H=r+1-ceil(log_3(r^2)); M=largest power of 3 <=H",
        "vector": check_vector(),
        "finite": check_finite(),
        "tail": check_tail(),
        "theorem": "size <(113/8)*3^r/r for every r>=64",
        "depth": "<=r+4*ceil(log2 r)+9",
        "claim_boundary": (
            "This is a fresh-room optimization of the reconstructed compiler, "
            "not a claim about the byte-exact 01ddf456 packet."
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

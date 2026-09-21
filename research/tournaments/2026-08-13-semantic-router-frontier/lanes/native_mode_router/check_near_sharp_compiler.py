#!/usr/bin/env python3
"""Exact replay for the adaptive total constant below 326/25."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

from check_adaptive_block_compiler import adaptive_nodes, adaptive_params
from native_mode_model import mode_nodes


def binary_nodes_upper(r: int) -> int:
    k = math.isqrt(r)
    q = 3**k
    binary_capacity = 2 ** (q.bit_length() - 1)
    leaves = 2 ** (r - 1)
    return (
        6 * (leaves + binary_capacity)
        + 6 * r * q * q
        + 4 * r
        + 10
    )


def build_receipt() -> dict[str, object]:
    target_numerator = 326
    target_denominator = 25
    worst = (Fraction(0), 0)
    finite_checks = 0

    for r in range(64, 16385):
        total = adaptive_nodes(r) + binary_nodes_upper(r)
        if not target_denominator * total * r < target_numerator * 3**r:
            raise AssertionError(f"326/25 bound failed at r={r}")
        ratio = Fraction(total * r, 3**r)
        if ratio > worst[0]:
            worst = (ratio, r)
        finite_checks += 1

    if worst[1] != 88:
        raise AssertionError(f"unexpected maximum arity: {worst[1]}")

    tail_checks = 0
    for r in range(741, 16385):
        ell, _headroom, m, b, _p = adaptive_params(r)
        x = Fraction(r, m)
        gap = r - m
        remainder = mode_nodes(b) + 4 * r + 7
        binary = binary_nodes_upper(r)

        if not 2000 * remainder * r < 3**r:
            raise AssertionError(f"remainder certificate failed at r={r}")
        if not 2000 * binary * r < 3**r:
            raise AssertionError(f"binary certificate failed at r={r}")
        if not x < Fraction(151, 50):
            raise AssertionError(f"x bound failed at r={r}")

        if gap == ell - 1:
            main = Fraction(9, 1) / x + Fraction(109, 27) * x
            if not main <= Fraction(352, 27):
                raise AssertionError(f"case-A bound failed at r={r}")
        else:
            if not gap >= ell:
                raise AssertionError(f"gap dichotomy failed at r={r}")
            if x <= 2:
                main = Fraction(3, 1) / x + Fraction(109, 27) * x
                if not main <= Fraction(517, 54):
                    raise AssertionError(f"case-B-small bound failed at r={r}")
            else:
                local = (3 * m - 1) * 3**m
                if not 2000 * local * r < 3**r:
                    raise AssertionError(f"case-B local bound failed at r={r}")
                if not Fraction(109, 27) * x < Fraction(109, 27) * Fraction(151, 50):
                    raise AssertionError(f"case-B prefix bound failed at r={r}")
        tail_checks += 1

    result: dict[str, object] = {
        "theorem": "adaptive native-mode compiler total constant below 13.04",
        "status": "exact finite replay plus analytic-tail certificate",
        "constant": "326/25",
        "finite": {
            "arities": [64, 16384],
            "checks": finite_checks,
            "worst_arity": worst[1],
            "worst_decimal": format(float(worst[0]), ".15f"),
            "worst_exact": f"{worst[0].numerator}/{worst[0].denominator}",
        },
        "tail": {
            "start": 741,
            "end": 16384,
            "checks": tail_checks,
            "nonbinary_remainder": "<1/2000",
            "binary_upper": "<1/2000",
            "case_A_main": "<=352/27",
            "case_B_main": "strictly below case_A",
        },
        "depth": "<=r+4*ceil(log2 r)+9",
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(encoded).hexdigest()
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

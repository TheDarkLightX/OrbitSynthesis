#!/usr/bin/env python3
"""Independent exact checks for the adaptive block schedule."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

from native_mode_model import ceil_log3, clog2, floor_log3, mode_nodes, req


def adaptive_params(r: int) -> tuple[int, int, int, int, int]:
    ell = ceil_log3(r * r)
    headroom = r + 1 - ell
    b = floor_log3(headroom)
    m = 3**b
    p = 3 ** (r - b)
    return ell, headroom, m, b, p


def adaptive_nodes(r: int) -> int:
    _ell, _headroom, m, b, p = adaptive_params(r)
    return (
        (3 * m - 1) * 3**m
        + mode_nodes(b)
        + (3 * p - 1)
        + mode_nodes(r - b)
        + 4 * r
        + 7
    )


def adaptive_depth(r: int) -> int:
    _ell, _headroom, _m, b, _p = adaptive_params(r)
    c = clog2(r)
    prefix = r - b
    local = 3 * c + 3 + clog2(b) + b + 1
    prefix_mode = 3 * c + 3 + clog2(prefix)
    return max(local, prefix_mode) + prefix + 1 + 4


def check_finite() -> dict[str, object]:
    worst = (Fraction(0), 0)
    minimum_depth_slack = None
    checks = 0
    for r in range(64, 16385):
        ell, headroom, m, b, p = adaptive_params(r)
        n = adaptive_nodes(r)
        req(m <= headroom < 3 * m, "power bracketing")
        req(m == 3**b and m * p == 3**r, "parameter identities")
        req(4 * n * r < 53 * 3**r, "nonbinary 53/4 bound")
        req(4 * n * r + 3 * 3**r < 56 * 3**r, "total 14 bound")
        cap = r + 4 * clog2(r) + 9
        depth = adaptive_depth(r)
        req(depth <= cap, "depth bound")
        ratio = Fraction(n * r, 3**r)
        if ratio > worst[0]:
            worst = (ratio, r)
        slack = cap - depth
        minimum_depth_slack = slack if minimum_depth_slack is None else min(
            minimum_depth_slack, slack
        )
        req(ell >= 1 and headroom >= 1, "positive parameters")
        checks += 8
    req(worst[1] == 88, "unexpected finite maximum")
    return {
        "arities": [64, 16384],
        "checks": checks,
        "parameter_rule": "H=r+1-ceil(log_3(r^2)); M=largest power of 3 <=H",
        "nonbinary": "<53/4*3^r/r",
        "binary_allowance": "<3/4*3^r/r",
        "total": "<14*3^r/r",
        "depth": "<=r+4*ceil(log2 r)+9",
        "worst_arity": worst[1],
        "worst_decimal": format(float(worst[0]), ".15f"),
        "worst_exact": f"{worst[0].numerator}/{worst[0].denominator}",
        "minimum_depth_slack": minimum_depth_slack,
    }


def check_analytic_tail() -> dict[str, object]:
    checks = 0
    for r in range(741, 16385):
        ell, _headroom, m, b, p = adaptive_params(r)
        prefix = r - b
        req(m >= 729 and b >= 6, "tail block floor")
        req(8 * ell <= r, "ell <= r/8")
        req(7 * r < 24 * m, "r/M <24/7")
        req(ell <= 2 * b + 3, "logarithm conversion")
        req(50 * (ell - 1) <= m, "ell/M <=1/50")
        req(3**r > 104 * r * r, "remainder domination")
        req(prefix >= 8 and 27 * mode_nodes(prefix) <= 28 * p, "prefix vector")
        checks += 7
    return {
        "start": 741,
        "end": 16384,
        "checks": checks,
        "proof_note": "ADAPTIVE_BLOCK_CONSTANT_14.md",
    }


def check_binary_allowance() -> dict[str, object]:
    checks = 0
    for r in range(64, 16385):
        k = math.isqrt(r)
        req(24 * r * 2**r < 3**r, "router skeleton <1/4")
        req(3 ** (r - 2 * k) >= r**4, "control exponent")
        req(24 < r * r, "control tables <1/4")
        req(4 * (4 * r + 10) * r < 3**r, "fixed overhead <1/4")
        checks += 4
    return {
        "arities": [64, 16384],
        "checks": checks,
        "components": ["<1/4", "<6/r^2<1/4", "<1/4"],
        "sum": "<3/4",
    }


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "theorem": "adaptive native-mode compiler constant below fourteen",
        "status": "exact finite replay plus analytic-tail certificate",
        "finite": check_finite(),
        "analytic_tail": check_analytic_tail(),
        "binary_allowance": check_binary_allowance(),
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(encoded).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_receipt(), sort_keys=True, indent=2) + "\n"
    if args.out is not None:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

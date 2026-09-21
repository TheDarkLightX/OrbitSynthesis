#!/usr/bin/env python3
"""Exact follow-up checks for two quantitative router/compiler sharpenings."""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from functools import lru_cache

from native_mode_model import (
    ceil_log3,
    clog2,
    mode_nodes,
    nonbinary_depth,
    nonbinary_nodes,
    params,
    req,
)


@lru_cache(None)
def gain_loss_nodes(width: int) -> int:
    """Nodes for all L roots and only the distinct nonzero G roots.

    G for a physical word depends only on its prefix ending at its last 2;
    words with no 2 share the zero root.
    """
    if width == 0:
        return 0
    if width == 1:
        return 4
    left = width // 2
    right = (width + 1) // 2
    q = 3**width
    distinct_nonzero_right_gain = (3**right - 1) // 2
    return (
        gain_loss_nodes(left)
        + gain_loss_nodes(right)
        + q
        + 3**left * distinct_nonzero_right_gain
    )


def negative_cells(root_negative: int, width: int) -> int:
    q = 3**width
    even = (q + 1) // 2
    odd = (q - 1) // 2
    return even if root_negative else odd


def reusable_vector_nodes(root_negative: int, width: int) -> int:
    return 2 + gain_loss_nodes(width) + negative_cells(root_negative, width)


def check_reusable_vector() -> dict[str, object]:
    worst = (Fraction(0), 0, 0)
    checks = 0
    for width in range(1, 257):
        q = 3**width
        req(3 * gain_loss_nodes(width) <= 7 * q, "state-vector 7q/3 bound")
        for root in (0, 1):
            nodes = reusable_vector_nodes(root, width)
            req(nodes <= 3 * q, "reusable vector 3q bound")
            ratio = Fraction(nodes, q)
            if ratio > worst[0]:
                worst = (ratio, root, width)
            checks += 2
    req(worst == (Fraction(3), 1, 2), "unexpected reusable-vector extremum")
    return {
        "widths": [1, 256],
        "checks": checks,
        "exact_bound": "V_root(w) <= 3*3^w",
        "asymptotic": "V_root(w) = 2*3^w + O(3^ceil(w/2))",
        "worst_ratio": "3",
        "worst_root": "negative",
        "worst_width": 2,
    }


def check_compiler_constant() -> dict[str, object]:
    worst = (Fraction(0), 0)
    checks = 0
    for r in range(64, 16385):
        n = nonbinary_nodes(r)
        req(n * r < 14 * 3**r, "nonbinary constant 14")
        req(n * r + 3**r < 15 * 3**r, "inclusive constant 15")
        req(nonbinary_depth(r) <= r + 4 * clog2(r) + 9, "depth regression")
        ratio = Fraction(n * r, 3**r)
        if ratio > worst[0]:
            worst = (ratio, r)
        checks += 3
    req(worst[1] == 93, "unexpected compiler extremum")

    tail_checks = 0
    for r in range(258, 16385):
        ell = ceil_log3(r * r)
        _reserve, _headroom, m, b, _p = params(r)
        req(m >= 243 and b >= 5, "tail block floor")
        req(8 * ell <= r, "ell <= r/8")
        req(r < 4 * m, "coarse tail ratio")
        req(ell <= 2 * b + 3, "logarithm conversion")
        req(ell + 4 <= m // 9, "reserve versus block")
        req(9 * r < 28 * m, "r/M < 28/9")
        tail_checks += 6

    return {
        "finite_arities": [64, 16384],
        "finite_checks": checks,
        "analytic_tail_start": 258,
        "analytic_side_checks": tail_checks,
        "nonbinary": "<14*3^r/r",
        "inclusive_with_existing_binary_allowance": "<15*3^r/r",
        "depth": "<=r+4*ceil(log2 r)+9",
        "worst_arity": 93,
        "worst_decimal": format(float(worst[0]), ".15f"),
    }


def main() -> int:
    result = {
        "theorem": "sharpened reusable vector and conditional compiler constants",
        "status": "exact recurrences plus finite replay; analytic proof in note",
        "python": sys.version.split()[0],
        "reusable_vector": check_reusable_vector(),
        "compiler": check_compiler_constant(),
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

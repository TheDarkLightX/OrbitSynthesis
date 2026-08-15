#!/usr/bin/env python3
"""Audit the recursive local library and the 19/2 integrated bound."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path

from check_compiler_bridge import random_selector
from compiler_bridge_model import (
    Q,
    binary_node_upper,
    clog2,
    require,
)
from hierarchical_compiler_model import residual_nodes
from recursive_local_compiler_model import (
    compile_recursive_small,
    parameters,
    recursive_library_nodes,
    total_depth_upper,
    total_node_upper,
)


def check_semantics() -> dict[str, object]:
    cases = [
        (3, 1, random_selector(3, seed))
        for seed in range(64)
    ]
    cases += [
        (4, 2, random_selector(4, 2000 + seed))
        for seed in range(2)
    ]

    tables = 0
    rows = 0
    maximum_nodes = 0
    maximum_depth = 0
    library_sizes: set[int] = set()
    for arity, local_width, selector in cases:
        dag, build = compile_recursive_small(
            arity,
            selector,
            local_width=local_width,
        )
        for point in product(Q, repeat=arity):
            require(
                dag.evaluate(build.root, point) == point[selector[point]],
                "recursive-library semantic mismatch",
            )
            rows += 1
        tables += 1
        library_sizes.add(build.local_library_size)
        maximum_nodes = max(maximum_nodes, len(dag.reachable([build.root])))
        maximum_depth = max(maximum_depth, dag.depth(build.root))

    return {
        "selector_tables": tables,
        "row_checks": rows,
        "arities": [3, 4],
        "local_widths": [1, 2],
        "library_sizes": sorted(library_sizes),
        "maximum_nodes": maximum_nodes,
        "maximum_depth": maximum_depth,
    }


def check_finite_range() -> dict[str, object]:
    worst = (Fraction(0), 0)
    for arity in range(64, 1024):
        total = total_node_upper(arity)
        require(2 * total * arity < 19 * 3**arity, "finite 19/2 bound")
        require(
            total_depth_upper(arity) <= arity + 4 * clog2(arity) + 9,
            "recursive-library depth bound",
        )
        ratio = Fraction(total * arity, 3**arity)
        if ratio > worst[0]:
            worst = (ratio, arity)
    require(worst[1] == 85, "unexpected finite maximum")
    return {
        "arities": [64, 1023],
        "checks": 960,
        "worst_arity": worst[1],
        "worst_decimal": format(float(worst[0]), ".15f"),
    }


def check_analytic_tail() -> dict[str, object]:
    cases = {
        "transition": 0,
        "ratio_at_most_two": 0,
        "ratio_above_two": 0,
    }
    checks = 0
    for arity in range(1024, 16385):
        ell, _, local, local_width, residual_width, _, _ = parameters(arity)
        gap = arity - local
        ratio = Fraction(arity, local)
        residual_lower = residual_nodes(residual_width) - 3 * 3**residual_width
        fixed = 4 * arity + 3
        binary = binary_node_upper(arity)
        library = recursive_library_nodes(local_width)

        require(50 * ell <= local, "transition offset")
        require(100 * residual_lower * arity < 3**arity, "residual lower terms")
        require(100 * fixed * arity < 3**arity, "fixed terms")
        require(100 * binary * arity < 3**arity, "binary terms")
        require(library < 9 * 3**local, "recursive library bound")

        if gap == ell:
            require(ell == local_width + 1, "transition exponent")
            require(50 * (ratio - 1) <= 1, "transition ratio")
            require(6 * ratio <= Fraction(153, 25), "transition main terms")
            cases["transition"] += 1
        else:
            require(gap >= ell + 1, "gap dichotomy")
            if ratio <= 2:
                require(3 * ratio + 3 <= 9, "small-ratio main terms")
                cases["ratio_at_most_two"] += 1
            else:
                require(
                    100 * library * arity < 3**arity,
                    "large-ratio local library",
                )
                require(
                    3 * ratio < Fraction(453, 50),
                    "large-ratio residual skeleton",
                )
                cases["ratio_above_two"] += 1
        checks += 8

    require(all(cases.values()), "analytic case not exercised")
    return {
        "arities": [1024, 16384],
        "checks": checks,
        "cases": cases,
        "tail_bound": "<91/10<19/2",
    }


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "orbit-synthesis/order-pair-recursive-local-19-over-2/v1",
        "status": "recursive local library plus hierarchical residual proof",
        "semantics": check_semantics(),
        "finite": check_finite_range(),
        "tail": check_analytic_tail(),
        "theorem": "size <(19/2)*3^r/r for every r>=64",
        "depth": "<=r+4*ceil(log2 r)+9",
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

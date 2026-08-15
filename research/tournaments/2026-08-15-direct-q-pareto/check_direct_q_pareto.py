#!/usr/bin/env python3
"""Audit the five-node Q-mux compiler and its size/depth Pareto theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = (
    HERE.parents[2]
    / "research/tournaments/2026-08-13-program-vector-optimization"
    / "audits/compiler_bridge_reconstruction"
)
sys.path.insert(0, str(BASE))

from check_compiler_bridge import random_selector  # noqa: E402
from compiler_bridge_model import Q, order_pair_vector_nodes, require  # noqa: E402
from direct_q_pareto_model import (  # noqa: E402
    compile_pareto_small,
    direct_library_nodes,
    parameters,
    residual_nodes,
    total_depth_upper,
    total_node_upper,
)


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


def mux_value(x: int, b0: int, b1: int, b2: int) -> int:
    gated0 = disc(0, x, b0)
    gated1 = disc(1, x, b1)
    gated2 = disc(x, 2, b2)
    tail = disc(gated1, 1, gated2)
    return disc(gated0, 0, tail)


def encode_value(value: int) -> tuple[int, int]:
    return disc(0, value, 1), disc(value, 2, 0)


def decode_value(first: int, second: int) -> int:
    return disc(second, first, 2)


def check_gadgets() -> dict[str, object]:
    mux_checks = 0
    for x, b0, b1, b2 in product(Q, repeat=4):
        require(mux_value(x, b0, b1, b2) == (b0, b1, b2)[x], "mux mismatch")
        mux_checks += 1

    codes = {}
    for value in Q:
        code = encode_value(value)
        require(code in {(1, 0), (0, 1), (0, 0)}, "illegal code")
        require(decode_value(*code) == value, "decode mismatch")
        codes[str(value)] = list(code)

    return {
        "mux_checks": mux_checks,
        "mux_nodes": 5,
        "mux_depth": 3,
        "codes": codes,
        "encoder_nodes_per_value": 2,
        "decoder_nodes": 1,
    }


def check_semantics() -> dict[str, object]:
    cases = [
        (3, 1, 1, random_selector(3, seed))
        for seed in range(64)
    ]
    cases += [
        (5, 2, 2, random_selector(5, 3000 + seed))
        for seed in range(2)
    ]

    tables = 0
    rows = 0
    maximum_nodes = 0
    maximum_depth = 0
    library_sizes: set[int] = set()
    for arity, local_width, direct_width, selector in cases:
        dag, build = compile_pareto_small(
            arity,
            selector,
            local_width=local_width,
            direct_width=direct_width,
        )
        for point in product(Q, repeat=arity):
            require(
                dag.evaluate(build.root, point) == point[selector[point]],
                "complete Pareto compiler mismatch",
            )
            rows += 1
        tables += 1
        library_sizes.add(build.local_library_size)
        maximum_nodes = max(maximum_nodes, len(dag.reachable([build.root])))
        maximum_depth = max(maximum_depth, dag.depth(build.root))

    return {
        "selector_tables": tables,
        "row_checks": rows,
        "arities": [3, 5],
        "local_widths": [1, 2],
        "direct_widths": [1, 2],
        "library_sizes": sorted(library_sizes),
        "maximum_nodes": maximum_nodes,
        "maximum_depth": maximum_depth,
    }


def check_finite_range() -> dict[str, object]:
    worst = (Fraction(0), 0)
    minimum_depth_slack = None
    for arity in range(64, 1024):
        total = total_node_upper(arity)
        require(total * arity < 8 * 3**arity, "finite size-eight bound")
        target_depth = arity + 6 * (arity - 1).bit_length() + 9
        depth = total_depth_upper(arity)
        require(depth <= target_depth, "finite Pareto depth bound")
        ratio = Fraction(total * arity, 3**arity)
        if ratio > worst[0]:
            worst = (ratio, arity)
        slack = target_depth - depth
        minimum_depth_slack = slack if minimum_depth_slack is None else min(
            minimum_depth_slack,
            slack,
        )
    require(worst[1] == 84, "unexpected finite maximum")
    return {
        "arities": [64, 1023],
        "checks": 960,
        "worst_arity": worst[1],
        "worst_decimal": format(float(worst[0]), ".15f"),
        "minimum_depth_slack": minimum_depth_slack,
    }


def check_analytic_tail() -> dict[str, object]:
    cases = {
        "transition": 0,
        "small_ratio": 0,
        "large_ratio": 0,
    }
    checks = 0
    limsup_samples = []

    for arity in range(1024, 16385):
        (
            ell,
            headroom,
            local,
            local_width,
            direct_width,
            signed_width,
            direct_capacity,
            signed_capacity,
            prefix_capacity,
        ) = parameters(arity)
        gap = arity - local
        ratio = Fraction(arity, local)
        library = direct_library_nodes(local_width)
        previous_library = library - 5 * 3**local
        residual = residual_nodes(arity)
        residual_lower_twice = 2 * residual - 5 * prefix_capacity
        fixed = 4 * arity + 2

        require(local <= headroom < 3 * local, "power bracketing")
        require(local >= 729 and local_width >= 6, "tail local floor")
        require(direct_width == local_width + 1, "direct-width rule")
        require(signed_width >= 7, "outer vector width")
        require(50 * (ell - 1) <= local, "transition offset")
        require(50 * arity < 151 * local, "ratio below 151/50")
        require(
            2 * order_pair_vector_nodes(signed_width, False)
            <= 3 * signed_capacity,
            "outer vector 3/2 bound",
        )
        require(100 * previous_library * arity < 3**arity, "earlier library terms")
        require(
            100 * residual_lower_twice * arity < 2 * 3**arity,
            "residual lower terms",
        )
        require(100 * fixed * arity < 3**arity, "fixed lower terms")
        from compiler_bridge_model import binary_node_upper

        binary = binary_node_upper(arity)
        require(100 * binary * arity < 3**arity, "binary lower terms")

        residual_main = Fraction(5 * arity, 2 * local)
        local_main = Fraction(5 * arity, 3**gap)
        if gap == ell - 1:
            require(ell == local_width + 1, "transition exponent")
            require(ratio <= Fraction(51, 50), "transition ratio")
            require(
                local_main + residual_main <= Fraction(153, 20),
                "transition main bound",
            )
            cases["transition"] += 1
        else:
            require(gap >= ell, "gap dichotomy")
            if ratio <= Fraction(9, 5):
                require(
                    local_main + residual_main <= Fraction(15, 2),
                    "small-ratio main bound",
                )
                cases["small_ratio"] += 1
            else:
                require(100 * local_main < 1, "large-ratio local hundredth")
                require(
                    residual_main < Fraction(151, 20),
                    "large-ratio residual bound",
                )
                cases["large_ratio"] += 1
        require(
            total_depth_upper(arity)
            <= arity + 6 * (arity - 1).bit_length() + 9,
            "tail Pareto depth bound",
        )
        checks += 13

    for local_width in range(6, 11):
        transition = 3**local_width + local_width - 1
        before = transition - 1
        if before >= 64:
            ratio = Fraction(total_node_upper(before) * before, 3**before)
            limsup_samples.append(
                {
                    "local_width": local_width,
                    "arity": before,
                    "normalized_decimal": format(float(ratio), ".12f"),
                }
            )

    require(all(cases.values()), "analytic case not exercised")
    return {
        "arities": [1024, 16384],
        "checks": checks,
        "cases": cases,
        "common_lower_terms": "four terms below 1/100",
        "tail_total": "<769/100<8",
        "architecture_limsup": "15/2",
        "limsup_samples": limsup_samples,
    }


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "orbit-synthesis/direct-q-pareto-size-8/v1",
        "status": "explicit bounded construction plus finite/analytic proof",
        "gadgets": check_gadgets(),
        "semantics": check_semantics(),
        "finite": check_finite_range(),
        "tail": check_analytic_tail(),
        "theorem": "size <8*3^r/r for every r>=64",
        "depth": "<=r+6*ceil(log2 r)+9",
        "claim_boundary": (
            "This is a post-referee Pareto refinement on a separate branch. "
            "The 15/2 limsup is construction-specific and is not a lower bound "
            "for arbitrary d/u DAGs."
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

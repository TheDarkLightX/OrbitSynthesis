#!/usr/bin/env python3
"""Calibrate recursive-subcube local coding for conservative Q-terms."""
from __future__ import annotations

import hashlib
import json
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.quasiprimal_orbit_term_compiler import (
    compatible_tables,
    random_compatible_table,
    reduction_selector_table,
)
from orbitsynthesis.orbit_term_compile import (
    Q,
    distinct_node_count,
    evaluate,
    expression_depth,
)
from orbitsynthesis.orbit_term_compile_local import (
    SlicePlan,
    compile_local_coding_coordinate_selector,
    slice_plans,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def best_term(
    arity: int,
    table: dict[tuple[int, ...], int],
    schedule: str,
):
    candidates = []
    for cap in range(1, 5):
        term = compile_local_coding_coordinate_selector(
            arity,
            table,
            block_assignment_cap=cap,
            library_schedule=schedule,
        )
        candidates.append((distinct_node_count(term), cap, term))
    return min(candidates, key=lambda candidate: (candidate[0], candidate[1]))


def verify_term(
    arity: int,
    table: dict[tuple[int, ...], int],
    term,
) -> int:
    checked = 0
    for point in product(Q, repeat=arity):
        require(
            evaluate(term, point) == point[table[point]],
            f"subcube term disagrees at arity {arity}, point {point}",
        )
        checked += 1
    return checked


def alphabet_sizes(arity: int, plan: SlicePlan) -> tuple[int, ...]:
    return tuple(2 if position < plan.anchor else 3 for position in plan.block_positions)


def subcube_selector_calls(alphabets: tuple[int, ...]) -> int:
    """Count normal-selector calls across every recursive library level."""

    suffix_assignments = 1
    selectors = 0
    for alphabet in reversed(alphabets):
        require(alphabet in {2, 3}, "unsupported subcube alphabet")
        suffix_assignments *= alphabet
        selectors += (alphabet - 1) * 3**suffix_assignments
    return selectors


def selector_census_rows() -> list[dict[str, int | list[int]]]:
    rows = []
    patterns = (
        (2,),
        (3,),
        (2, 2),
        (2, 3),
        (3, 2),
        (3, 3),
        (2, 2, 3),
    )
    for alphabets in patterns:
        assignments = 1
        for alphabet in alphabets:
            assignments *= alphabet
        selectors = subcube_selector_calls(alphabets)
        require(
            selectors < 3 * 3**assignments,
            "subcube selector count lost O(3^M) dominance",
        )
        rows.append(
            {
                "alphabet_sizes": list(alphabets),
                "block_assignments": assignments,
                "library_functions": 3**assignments,
                "normal_selector_calls": selectors,
                "selector_depth_levels": sum(
                    2 if alphabet == 2 else 4 for alphabet in alphabets
                ),
            }
        )
    return rows


def plan_rows() -> list[dict[str, int]]:
    rows = []
    for arity in (8, 12, 16, 24, 32, 48, 64):
        plans = slice_plans(arity)
        max_scaled_size_proxy = 0
        max_library_ratio_numerator = 0
        max_library_ratio_denominator = 1
        for plan in plans:
            alphabets = alphabet_sizes(arity, plan)
            assignments = plan.block_assignments
            require(
                assignments
                == _product(alphabets),
                "block-assignment product drift",
            )
            selector_calls = subcube_selector_calls(alphabets)
            require(
                selector_calls < 3 * plan.library_functions,
                "library selector dominance failed",
            )

            block_depth = sum(
                2 if position < plan.anchor else 4
                for position in plan.block_positions
            )
            prefix_depth = 2 * (plan.anchor - sum(
                position < plan.anchor for position in plan.block_positions
            )) + 4 * (
                arity
                - plan.anchor
                - 1
                - sum(position > plan.anchor for position in plan.block_positions)
            )
            executable_depth_bound = (
                1
                + 2
                + block_depth
                + prefix_depth
                + 2 * (plan.anchor + 1)
            )
            require(
                executable_depth_bound == 4 * arity + 1,
                "subcube depth cancellation failed",
            )

            # Each normal selector expands to three discriminator nodes.  A
            # full mixed-radix prefix tree has exactly prefix_leaves-1 selector
            # calls after weighting a q-way node by q-1.
            size_proxy = 3 * (
                selector_calls + max(0, plan.prefix_assignments - 1)
            )
            max_scaled_size_proxy = max(
                max_scaled_size_proxy,
                arity * size_proxy // plan.domain_size,
            )
            ratio_numerator = arity * plan.library_functions
            if (
                ratio_numerator * max_library_ratio_denominator
                > max_library_ratio_numerator * plan.domain_size
            ):
                max_library_ratio_numerator = ratio_numerator
                max_library_ratio_denominator = plan.domain_size

        rows.append(
            {
                "arity": arity,
                "slice_count": len(plans),
                "executable_depth_bound": 4 * arity + 1,
                "max_floor_r_times_size_proxy_over_slice_domain": (
                    max_scaled_size_proxy
                ),
                "max_library_ratio_numerator": max_library_ratio_numerator,
                "max_library_ratio_denominator": max_library_ratio_denominator,
            }
        )
    return rows


def _product(values: tuple[int, ...]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


def bounded_rows() -> tuple[list[dict[str, int]], int]:
    rows = []
    total_checked = 0
    for arity in range(1, 8):
        table = random_compatible_table(arity, 20260814 + arity)
        layered_nodes, layered_cap, layered = best_term(arity, table, "layered")
        subcube_nodes, subcube_cap, subcube = best_term(arity, table, "subcube")
        checked = verify_term(arity, table, subcube)
        total_checked += checked
        layered_depth = expression_depth(layered)
        subcube_depth = expression_depth(subcube)
        require(subcube_depth <= 4 * arity + 1, "explicit depth bound failed")
        require(
            subcube_depth <= layered_depth,
            f"subcube depth regression at arity {arity}",
        )
        rows.append(
            {
                "arity": arity,
                "tuples_checked": checked,
                "layered_dag_nodes": layered_nodes,
                "layered_depth": layered_depth,
                "layered_cap": layered_cap,
                "subcube_dag_nodes": subcube_nodes,
                "subcube_depth": subcube_depth,
                "subcube_cap": subcube_cap,
                "nodes_saved_vs_layered": layered_nodes - subcube_nodes,
                "depth_saved_vs_layered": layered_depth - subcube_depth,
            }
        )
    require(rows[-1]["depth_saved_vs_layered"] > 0, "no strict depth gain")
    return rows, total_checked


def mutation_checks() -> dict[str, bool]:
    table = random_compatible_table(3, 7022)
    invalid_schedule_rejected = False
    try:
        compile_local_coding_coordinate_selector(
            3,
            table,
            block_assignment_cap=3,
            library_schedule="recursive_guess",
        )
    except RuntimeError:
        invalid_schedule_rejected = True

    alphabets = (3, 3)
    assignments = _product(alphabets)
    selectors = subcube_selector_calls(alphabets)
    layered_census_rejected = selectors != 3**assignments - 1
    top_only_census_rejected = selectors != (
        (alphabets[0] - 1) * 3**assignments
    )

    plan = slice_plans(64)[0]
    recursive_block_depth = sum(
        2 if position < plan.anchor else 4
        for position in plan.block_positions
    )
    sequential_point_depth = 2 * plan.block_assignments
    sequential_point_depth_penalty_detected = (
        sequential_point_depth > recursive_block_depth
    )
    checks = {
        "invalid_schedule_rejected": invalid_schedule_rejected,
        "layered_selector_census_rejected": layered_census_rejected,
        "top_level_only_census_rejected": top_only_census_rejected,
        "sequential_point_depth_penalty_detected": (
            sequential_point_depth_penalty_detected
        ),
    }
    require(all(checks.values()), "one or more subcube mutations survived")
    return checks


def main() -> None:
    exhaustive_arity_two_tables = 0
    for table in compatible_tables(2):
        term = compile_local_coding_coordinate_selector(
            2,
            table,
            block_assignment_cap=3,
            library_schedule="subcube",
        )
        verify_term(2, table, term)
        require(expression_depth(term) <= 9, "arity-two depth bound failed")
        exhaustive_arity_two_tables += 1
    require(exhaustive_arity_two_tables == 128, "arity-two table census drift")

    rows, total_checked = bounded_rows()
    reduction_arity, reduction_table = reduction_selector_table()
    layered_nodes, layered_cap, layered = best_term(
        reduction_arity,
        reduction_table,
        "layered",
    )
    subcube_nodes, subcube_cap, subcube = best_term(
        reduction_arity,
        reduction_table,
        "subcube",
    )
    reduction_checked = verify_term(reduction_arity, reduction_table, subcube)
    layered_depth = expression_depth(layered)
    subcube_depth = expression_depth(subcube)
    require(subcube_nodes < layered_nodes, "no reduction node improvement")
    require(subcube_depth < layered_depth, "no reduction depth improvement")
    require(
        subcube_depth == 4 * reduction_arity + 1,
        "reduction did not attain the explicit depth bound",
    )

    summary = {
        "schema": "orbit-synthesis/quasiprimal-subcube-local-coding/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "construction": (
            "recursive mixed-radix subcube library over first-2 dynamic constants"
        ),
        "selector_census_rows": selector_census_rows(),
        "plan_rows": plan_rows(),
        "exhaustive_arity_two_selector_tables": exhaustive_arity_two_tables,
        "bounded_rows": rows,
        "bounded_random_tuples_checked": total_checked,
        "reduction_row": {
            "arity": reduction_arity,
            "tuples_checked": reduction_checked,
            "layered_dag_nodes": layered_nodes,
            "layered_depth": layered_depth,
            "layered_cap": layered_cap,
            "subcube_dag_nodes": subcube_nodes,
            "subcube_depth": subcube_depth,
            "subcube_cap": subcube_cap,
            "nodes_saved_vs_layered": layered_nodes - subcube_nodes,
            "depth_saved_vs_layered": layered_depth - subcube_depth,
        },
        "mutation_checks": mutation_checks(),
        "claim_boundary": (
            "Finite compiler and arithmetic calibration only. The generic same-DAG "
            "O(3^r/r) size and operation-depth at most 4r theorem rests on the "
            "separate manuscript proof. Recursive Shannon expansion, local coding, "
            "and linear finite-basis depth theory are prior art."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal subcube local-coding compiler")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

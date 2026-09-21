#!/usr/bin/env python3
"""Fail-closed calibration of the local-coding conservative-Q compiler."""
from __future__ import annotations

import hashlib
import json
import sys
from itertools import pairwise, product
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
    compile_orbit_coordinate_selector,
    complement,
    distinct_node_count,
    evaluate,
    expression_depth,
)
from orbitsynthesis.orbit_term_compile_local import (
    compile_local_coding_coordinate_selector,
    reflected_ternary_gray,
    slice_plans,
    suggested_block_assignment_cap,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def gray_is_valid(words: tuple[tuple[int, ...], ...], length: int) -> bool:
    return (
        len(words) == 3**length
        and len(set(words)) == len(words)
        and words[0] == (0,) * length
        and all(
            sum(left != right for left, right in zip(a, b, strict=True)) == 1
            for a, b in pairwise(words)
        )
    )


def verify_term(
    arity: int,
    table: dict[tuple[int, ...], int],
    term,
) -> int:
    checked = 0
    for point in product(Q, repeat=arity):
        require(
            evaluate(term, point) == point[table[point]],
            f"local-coded term disagrees at arity {arity}, point {point}",
        )
        checked += 1
    return checked


def best_bounded_local_term(
    arity: int,
    table: dict[tuple[int, ...], int],
):
    candidates = []
    for cap in range(1, 5):
        term = compile_local_coding_coordinate_selector(
            arity,
            table,
            block_assignment_cap=cap,
        )
        candidates.append((distinct_node_count(term), cap, term))
    return min(candidates, key=lambda candidate: (candidate[0], candidate[1]))


def bounded_rows() -> tuple[list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    total_checked = 0
    for arity in range(1, 8):
        table = random_compatible_table(arity, 20260814 + arity)
        baseline = compile_orbit_coordinate_selector(arity, table)
        local_nodes, selected_cap, local = best_bounded_local_term(arity, table)
        checked = verify_term(arity, table, local)
        total_checked += checked
        baseline_nodes = distinct_node_count(baseline)
        if arity >= 5:
            require(local_nodes < baseline_nodes, f"no bounded saving at arity {arity}")
        rows.append(
            {
                "arity": arity,
                "tuples_checked": checked,
                "baseline_dag_nodes": baseline_nodes,
                "local_coding_dag_nodes": local_nodes,
                "dag_nodes_saved": baseline_nodes - local_nodes,
                "local_coding_depth": expression_depth(local),
                "selected_block_assignment_cap": selected_cap,
                "block_assignments": [
                    plan.block_assignments
                    for plan in slice_plans(
                        arity,
                        block_assignment_cap=selected_cap,
                    )
                ],
            }
        )
    return rows, total_checked


def asymptotic_plan_rows() -> list[dict[str, int]]:
    rows = []
    for arity in (8, 12, 16, 24, 32, 48, 64):
        plans = slice_plans(arity)
        domain_sum = sum(plan.domain_size for plan in plans)
        prefix_sum = sum(plan.prefix_assignments for plan in plans)
        library_sum = sum(plan.library_functions for plan in plans)
        require(domain_sum == 3**arity - 2**arity, "slice partition identity failed")
        require(
            prefix_sum * arity <= 24 * domain_sum,
            f"prefix O(3^r/r) arithmetic failed at {arity}",
        )
        require(
            library_sum * (arity - 1) <= domain_sum,
            f"library O(3^r/r) arithmetic failed at {arity}",
        )
        for plan in plans:
            cap = suggested_block_assignment_cap(arity, plan.anchor)
            require(plan.block_assignments <= cap, "block exceeded assignment cap")
            if cap >= 2:
                require(
                    3 * plan.block_assignments > cap,
                    "block failed constant-factor cap saturation",
                )
        rows.append(
            {
                "arity": arity,
                "nonbinary_slice_rows": domain_sum,
                "prefix_assignments": prefix_sum,
                "library_functions": library_sum,
                "prefix_scaled_by_arity": prefix_sum * arity,
                "library_scaled_by_arity_minus_one": (
                    library_sum * (arity - 1)
                ),
                "minimum_block_assignments": min(
                    plan.block_assignments for plan in plans
                ),
                "maximum_block_assignments": max(
                    plan.block_assignments for plan in plans
                ),
            }
        )
    return rows


def mutation_checks() -> dict[str, bool]:
    words = list(reflected_ternary_gray(2))
    words[1], words[3] = words[3], words[1]
    corrupted_gray_rejected = not gray_is_valid(tuple(words), 2)

    table = random_compatible_table(3, 991)
    binary = next(point for point in table if all(value in (0, 1) for value in point))
    table[complement(binary)] = (table[binary] + 1) % 3
    complement_mutation_rejected = False
    try:
        compile_local_coding_coordinate_selector(
            3,
            table,
            block_assignment_cap=3,
        )
    except RuntimeError:
        complement_mutation_rejected = True

    invalid_cap_rejected = False
    try:
        slice_plans(3, block_assignment_cap=0)
    except RuntimeError:
        invalid_cap_rejected = True

    checks = {
        "corrupted_gray_path_rejected": corrupted_gray_rejected,
        "complement_asymmetry_rejected": complement_mutation_rejected,
        "nonpositive_block_cap_rejected": invalid_cap_rejected,
    }
    require(all(checks.values()), "one or more local-coding mutations survived")
    return checks


def main() -> None:
    gray_rows = []
    for length in range(5):
        words = tuple(reflected_ternary_gray(length))
        require(gray_is_valid(words, length), f"invalid ternary Gray path at {length}")
        gray_rows.append({"length": length, "words": len(words)})

    exhaustive_arity_two_tables = 0
    for table in compatible_tables(2):
        term = compile_local_coding_coordinate_selector(
            2,
            table,
            block_assignment_cap=3,
        )
        verify_term(2, table, term)
        exhaustive_arity_two_tables += 1
    require(exhaustive_arity_two_tables == 128, "arity-2 table census drift")

    rows, total_checked = bounded_rows()
    reduction_arity, reduction_table = reduction_selector_table()
    baseline_reduction = compile_orbit_coordinate_selector(
        reduction_arity,
        reduction_table,
    )
    local_reduction_nodes, reduction_cap, local_reduction = best_bounded_local_term(
        reduction_arity,
        reduction_table,
    )
    reduction_checks = verify_term(
        reduction_arity,
        reduction_table,
        local_reduction,
    )
    baseline_reduction_nodes = distinct_node_count(baseline_reduction)
    require(
        local_reduction_nodes < baseline_reduction_nodes,
        "local coding did not improve the arity-9 reduction",
    )

    summary = {
        "schema": "orbit-synthesis/quasiprimal-local-coding-compiler/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "construction": (
            "first-2 dynamic constants plus ternary-Gray local function library"
        ),
        "gray_rows": gray_rows,
        "exhaustive_arity_two_selector_tables": exhaustive_arity_two_tables,
        "bounded_rows": rows,
        "bounded_random_tuples_checked": total_checked,
        "asymptotic_plan_rows": asymptotic_plan_rows(),
        "reduction_row": {
            "arity": reduction_arity,
            "tuples_checked": reduction_checks,
            "baseline_dag_nodes": baseline_reduction_nodes,
            "local_coding_dag_nodes": local_reduction_nodes,
            "dag_nodes_saved": baseline_reduction_nodes - local_reduction_nodes,
            "local_coding_depth": expression_depth(local_reduction),
            "selected_block_assignment_cap": reduction_cap,
            "block_assignments": [
                plan.block_assignments
                for plan in slice_plans(
                    reduction_arity,
                    block_assignment_cap=reduction_cap,
                )
            ],
        },
        "mutation_checks": mutation_checks(),
        "claim_boundary": (
            "Finite construction and plan-arithmetic calibration only. The generic "
            "Theta(3^r/r) Shannon-complexity theorem rests on the separate manuscript "
            "proof and classical Lupanov-style local coding; novelty is unknown."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal local-coding compiler")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

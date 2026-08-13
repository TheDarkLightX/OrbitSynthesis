#!/usr/bin/env python3
"""Compare Gray and layered schedules for the local-coded Q-term compiler."""
from __future__ import annotations

import hashlib
import json
import math
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
    compile_local_coding_coordinate_selector,
    layered_ternary_selector_count,
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
            f"layered term disagrees at arity {arity}, point {point}",
        )
        checked += 1
    return checked


def selector_census_rows() -> list[dict[str, int]]:
    rows = []
    previous = 0
    for length in range(9):
        selectors = layered_ternary_selector_count(length)
        require(selectors == 3**length - 1, "closed selector census failed")
        if length:
            require(selectors == 3 * previous + 2, "selector recurrence failed")
        rows.append(
            {
                "block_assignments": length,
                "layered_selectors": selectors,
                "gray_selectors": 3**length - 1,
                "layered_dependency_levels": length,
                "gray_dependency_edges": max(0, 3**length - 1),
            }
        )
        previous = selectors
    return rows


def conservative_log_count(arity: int) -> float:
    base_two_exponent = 5 * 2 ** (arity - 1) - 5
    base_three_exponent = 3**arity - 3 * 2**arity + 3
    return base_two_exponent * math.log(2) + base_three_exponent * math.log(3)


def depth_term_log_upper(arity: int, operation_depth: int) -> float:
    """Upper-bound log A_h from A_(h+1) <= 3*A_h^3."""

    require(arity >= 2, "depth count requires at least two variables")
    require(operation_depth >= 0, "operation depth must be nonnegative")
    return 3**operation_depth * (math.log(arity) + math.log(3) / 2)


def depth_count_rows() -> list[dict[str, float | int]]:
    rows = []
    for arity in (8, 12, 16, 24, 32, 48, 64):
        threshold = max(
            0,
            math.floor(arity - math.log(math.log(arity), 3) - 3),
        )
        semantic_log = conservative_log_count(arity)
        shallow_log_upper = depth_term_log_upper(arity, threshold)
        gap = semantic_log - shallow_log_upper
        require(gap > 0, f"depth-count lower bound failed at {arity}")
        rows.append(
            {
                "arity": arity,
                "shallow_operation_depth": threshold,
                "semantic_log": semantic_log,
                "shallow_term_log_upper": shallow_log_upper,
                "log10_fraction_upper": -gap / math.log(10),
            }
        )
    return rows


def bounded_rows() -> tuple[list[dict[str, int]], int]:
    rows = []
    total_checked = 0
    for arity in range(1, 8):
        table = random_compatible_table(arity, 20260814 + arity)
        gray_nodes, gray_cap, gray = best_term(arity, table, "gray")
        layered_nodes, layered_cap, layered = best_term(arity, table, "layered")
        checked = verify_term(arity, table, layered)
        total_checked += checked
        gray_depth = expression_depth(gray)
        layered_depth = expression_depth(layered)
        require(layered_nodes <= gray_nodes, f"layered node regression at {arity}")
        require(layered_depth <= gray_depth, f"layered depth regression at {arity}")
        rows.append(
            {
                "arity": arity,
                "tuples_checked": checked,
                "gray_dag_nodes": gray_nodes,
                "gray_depth": gray_depth,
                "gray_cap": gray_cap,
                "layered_dag_nodes": layered_nodes,
                "layered_depth": layered_depth,
                "layered_cap": layered_cap,
                "nodes_saved_vs_gray": gray_nodes - layered_nodes,
                "depth_saved_vs_gray": gray_depth - layered_depth,
            }
        )
    require(rows[-1]["depth_saved_vs_gray"] > 0, "no strict bounded depth gain")
    return rows, total_checked


def mutation_checks() -> dict[str, bool]:
    table = random_compatible_table(3, 7021)
    invalid_schedule_rejected = False
    try:
        compile_local_coding_coordinate_selector(
            3,
            table,
            block_assignment_cap=3,
            library_schedule="breadth_guess",
        )
    except RuntimeError:
        invalid_schedule_rejected = True

    wrong_binary_recurrence_rejected = any(
        layered_ternary_selector_count(length)
        != 2 * layered_ternary_selector_count(length - 1) + 2
        for length in range(2, 7)
    )
    mutation_arity = 64
    dropping_loglog_rejected = depth_term_log_upper(
        mutation_arity,
        mutation_arity - 1,
    ) >= conservative_log_count(mutation_arity)
    checks = {
        "invalid_schedule_rejected": invalid_schedule_rejected,
        "dropping_loglog_depth_correction_rejected": dropping_loglog_rejected,
        "wrong_binary_selector_recurrence_rejected": (
            wrong_binary_recurrence_rejected
        ),
    }
    require(all(checks.values()), "one or more layered mutations survived")
    return checks


def main() -> None:
    exhaustive_arity_two_tables = 0
    for table in compatible_tables(2):
        term = compile_local_coding_coordinate_selector(
            2,
            table,
            block_assignment_cap=3,
            library_schedule="layered",
        )
        verify_term(2, table, term)
        exhaustive_arity_two_tables += 1
    require(exhaustive_arity_two_tables == 128, "arity-2 table census drift")

    rows, total_checked = bounded_rows()
    reduction_arity, reduction_table = reduction_selector_table()
    gray_nodes, gray_cap, gray = best_term(
        reduction_arity,
        reduction_table,
        "gray",
    )
    layered_nodes, layered_cap, layered = best_term(
        reduction_arity,
        reduction_table,
        "layered",
    )
    reduction_checked = verify_term(reduction_arity, reduction_table, layered)
    gray_depth = expression_depth(gray)
    layered_depth = expression_depth(layered)
    require(layered_nodes < gray_nodes, "no reduction node improvement")
    require(layered_depth < gray_depth, "no reduction depth improvement")

    summary = {
        "schema": "orbit-synthesis/quasiprimal-layered-local-coding/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "construction": (
            "zero-reusing layered prefix library over first-2 dynamic constants"
        ),
        "selector_census_rows": selector_census_rows(),
        "depth_count_rows": depth_count_rows(),
        "exhaustive_arity_two_selector_tables": exhaustive_arity_two_tables,
        "bounded_rows": rows,
        "bounded_random_tuples_checked": total_checked,
        "reduction_row": {
            "arity": reduction_arity,
            "tuples_checked": reduction_checked,
            "gray_dag_nodes": gray_nodes,
            "gray_depth": gray_depth,
            "gray_cap": gray_cap,
            "layered_dag_nodes": layered_nodes,
            "layered_depth": layered_depth,
            "layered_cap": layered_cap,
            "nodes_saved_vs_gray": gray_nodes - layered_nodes,
            "depth_saved_vs_gray": gray_depth - layered_depth,
        },
        "mutation_checks": mutation_checks(),
        "claim_boundary": (
            "Finite schedule and compiler calibration only. The generic simultaneous "
            "O(3^r/r) size and O(r) depth theorem rests on the separate manuscript "
            "proof; classical local coding and finite-basis depth theory are prior art."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal layered local-coding compiler")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

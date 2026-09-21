#!/usr/bin/env python3
"""Fail-closed calibration of the parameter-free orbit-selector term compiler."""
from __future__ import annotations

import hashlib
import json
import random
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.quasiprimal_cnf_initial_safety import build_reduction
from orbitsynthesis.orbit_term_compile import (
    Expr,
    Q,
    compile_orbit_coordinate_selector,
    complement,
    distinct_node_count,
    evaluate,
    expanded_tree_size,
    expression_depth,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def random_compatible_table(arity: int, seed: int) -> dict[tuple[int, ...], int]:
    rng = random.Random(seed)
    table: dict[tuple[int, ...], int] = {}
    for point in product(Q, repeat=arity):
        if point in table:
            continue
        index = rng.randrange(arity)
        table[point] = index
        if all(value in (0, 1) for value in point):
            table[complement(point)] = index
    return table


def compatible_tables(arity: int):
    """Enumerate all compatible selector-index tables at a small arity."""

    binary_orbits = tuple(
        (point, complement(point))
        for point in product((0, 1), repeat=arity)
        if point[0] == 0
    )
    nonbinary_orbits = tuple(
        (point,) for point in product(Q, repeat=arity) if 2 in point
    )
    orbits = binary_orbits + nonbinary_orbits
    for indices in product(range(arity), repeat=len(orbits)):
        table: dict[tuple[int, ...], int] = {}
        for orbit, index in zip(orbits, indices, strict=True):
            for point in orbit:
                table[point] = index
        yield table


def direct_expanded_tree_size(expr: Expr) -> int:
    """Independently count an unshared tree; use only on small calibrations."""

    from orbitsynthesis.orbit_term_compile import Disc, UnaryU, Var

    if isinstance(expr, Var):
        return 1
    if isinstance(expr, UnaryU):
        return 1 + direct_expanded_tree_size(expr.value)
    if isinstance(expr, Disc):
        return (
            1
            + direct_expanded_tree_size(expr.x)
            + direct_expanded_tree_size(expr.y)
            + direct_expanded_tree_size(expr.z)
        )
    raise TypeError(type(expr))


def structural_profile(arity: int) -> dict[str, int]:
    """Exact reachable syntax shape of this compiler, independent of leaves."""

    require(arity >= 1, "arity must be positive")
    dag_nodes = (
        6
        if arity == 1
        else 3 * 3**arity - 3 * 2 ** (arity - 1) + 6 * arity - 4
    )
    tree_numerator = 35 * 7**arity - 9 * 3**arity - 50
    require(tree_numerator % 12 == 0, "tree-size formula is not integral")
    return {
        "closed_form_dag_nodes": dag_nodes,
        "closed_form_expanded_tree_nodes": tree_numerator // 12,
        "closed_form_depth": 4 * arity + 1,
    }


def verify_table(
    arity: int,
    table: dict[tuple[int, ...], int],
    *,
    verify_direct_unsharing: bool,
) -> tuple[dict[str, int], Expr]:
    term = compile_orbit_coordinate_selector(arity, table)
    checked = 0
    for point in product(Q, repeat=arity):
        require(
            evaluate(term, point) == point[table[point]],
            f"compiled term disagrees at {point}",
        )
        checked += 1
    row = {
        "arity": arity,
        "explicit_table_rows": 3**arity,
        "tuples_checked": checked,
        "dag_nodes": distinct_node_count(term),
        "expanded_term_tree_nodes": expanded_tree_size(term),
        "term_depth": expression_depth(term),
        **structural_profile(arity),
    }
    require(
        row["dag_nodes"] == row["closed_form_dag_nodes"],
        "exact DAG-size formula failed",
    )
    require(
        row["expanded_term_tree_nodes"]
        == row["closed_form_expanded_tree_nodes"],
        "exact unshared-tree-size formula failed",
    )
    require(
        row["term_depth"] == row["closed_form_depth"],
        "exact depth formula failed",
    )
    if verify_direct_unsharing:
        require(
            direct_expanded_tree_size(term) == row["expanded_term_tree_nodes"],
            "memoized and direct unsharing counts disagree",
        )
    return row, term


def reduction_selector_table() -> tuple[int, dict[tuple[int, ...], int]]:
    # All eight sign clauses make this three-variable formula unsatisfiable and
    # exercise every clause-state output list.
    clauses = tuple(
        tuple(index if bit == 0 else -index for index, bit in enumerate(bits, 1))
        for bits in product((0, 1), repeat=3)
    )
    reduction = build_reduction(3, clauses)
    game = reduction.game
    arity = 2 * game.state_arity + game.input_arity
    table: dict[tuple[int, ...], int] = {}
    for state in game.states:
        for input_value in game.inputs:
            for output in game.outputs:
                flat = state + input_value + output
                if game.is_safe(state, input_value, output):
                    table[flat] = 0
                else:
                    separator = next(
                        (i for i in range(1, arity) if flat[i] != flat[0]),
                        None,
                    )
                    require(separator is not None, "forbidden constant tuple")
                    table[flat] = separator
    return arity, table


def mutation_check() -> bool:
    table = random_compatible_table(3, 17)
    binary = next(point for point in table if all(value in (0, 1) for value in point))
    paired = complement(binary)
    table[paired] = (table[binary] + 1) % 3
    try:
        compile_orbit_coordinate_selector(3, table)
    except ValueError:
        return True
    return False


def main() -> None:
    exhaustive_small_counts: dict[str, int] = {}
    for arity, expected in ((1, 1), (2, 128)):
        count = 0
        for table in compatible_tables(arity):
            verify_table(arity, table, verify_direct_unsharing=True)
            count += 1
        require(count == expected, f"unexpected exhaustive table count at {arity}")
        exhaustive_small_counts[str(arity)] = count

    generic_rows = []
    for arity in range(1, 5):
        row, _term = verify_table(
            arity,
            random_compatible_table(arity, 20260813 + arity),
            verify_direct_unsharing=True,
        )
        generic_rows.append(row)
    reduction_arity, reduction_table = reduction_selector_table()
    reduction_row, _term = verify_table(
        reduction_arity,
        reduction_table,
        verify_direct_unsharing=False,
    )
    safe_equation_checks = 0
    reduction = build_reduction(
        3,
        tuple(
            tuple(index if bit == 0 else -index for index, bit in enumerate(bits, 1))
            for bits in product((0, 1), repeat=3)
        ),
    )
    for state in reduction.game.states:
        for input_value in reduction.game.inputs:
            for output in reduction.game.outputs:
                flat = state + input_value + output
                require(
                    (flat[0] == flat[reduction_table[flat]])
                    == reduction.game.is_safe(state, input_value, output),
                    "selector equation disagrees with safety",
                )
                safe_equation_checks += 1

    require(mutation_check(), "non-equivariant selector mutation was accepted")
    summary = {
        "schema": "orbit-synthesis/quasiprimal-orbit-term-compiler/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "exhaustive_compatible_selector_tables": exhaustive_small_counts,
        "generic_random_rows": generic_rows,
        "reduction_row": reduction_row,
        "safe_equation_checks": safe_equation_checks,
        "mutation_rejected": True,
        "compiler_shape_formulas": {
            "dag_total_nodes": (
                "6 if r=1; 3*3^r-3*2^(r-1)+6r-4 if r>=2"
            ),
            "expanded_tree_nodes": "(35*7^r-9*3^r-50)/12",
            "depth": "4r+1",
        },
        "claim_boundary": (
            "Finite calibration of an explicit parameter-free compiler. The generic "
            "compiler and polynomial size bound rest on the separate structural proof."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal orbit-selector term compiler")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

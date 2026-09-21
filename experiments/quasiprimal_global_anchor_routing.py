#!/usr/bin/env python3
"""Calibrate optimal shallow routing and the global-anchor Q-term compiler."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from functools import cache
from itertools import product
from pathlib import Path

import z3

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.quasiprimal_orbit_term_compiler import (
    compatible_tables,
    random_compatible_table,
    reduction_selector_table,
)
from orbitsynthesis.orbit_term_compile import (
    Disc,
    Expr,
    Q,
    UnaryU,
    Var,
    distinct_node_count,
    evaluate,
    expression_depth,
)
from orbitsynthesis.orbit_term_compile_local import (
    absorbing_two,
    balanced_absorbing_two,
    compile_global_subcube_coordinate_selector,
    compile_local_coding_coordinate_selector,
    shallow_ternary_selector,
    suggested_global_block_assignment_cap,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def operation_depth(expr: Expr) -> int:
    return expression_depth(expr) - 1


def branch_depth(expr: Expr, branch_indices: frozenset[int]) -> int | None:
    """Maximum operation distance from a selected variable occurrence."""

    if isinstance(expr, Var):
        return 0 if expr.index in branch_indices else None
    if isinstance(expr, UnaryU):
        child = branch_depth(expr.value, branch_indices)
        return None if child is None else child + 1
    if isinstance(expr, Disc):
        child_depths = tuple(
            branch_depth(child, branch_indices)
            for child in (expr.x, expr.y, expr.z)
        )
        present = tuple(depth for depth in child_depths if depth is not None)
        return None if not present else max(present) + 1
    raise TypeError(type(expr))


def absorbing_depth_closure() -> dict[str, object]:
    points = tuple(product(Q, repeat=2))
    target = tuple(2 if 2 in point else point[0] for point in points)

    def unary(function: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(0 if value == 1 else 1 for value in function)

    def disc(
        left: tuple[int, ...],
        right: tuple[int, ...],
        equal: tuple[int, ...],
    ) -> tuple[int, ...]:
        return tuple(
            equal[index] if left[index] == right[index] else left[index]
            for index in range(len(points))
        )

    functions = {
        tuple(point[index] for point in points)
        for index in range(2)
    }
    level_sizes = [len(functions)]
    first_depth = 0 if target in functions else None
    for depth in range(1, 4):
        previous = tuple(functions)
        functions.update(unary(function) for function in previous)
        functions.update(
            disc(left, right, equal)
            for left in previous
            for right in previous
            for equal in previous
        )
        level_sizes.append(len(functions))
        if first_depth is None and target in functions:
            first_depth = depth

    candidate = absorbing_two(Var(0), Var(1))
    require(
        tuple(evaluate(candidate, point) for point in points) == target,
        "absorbing-two candidate semantics failed",
    )
    require(first_depth == 3, "absorbing-two minimal depth drift")
    require(operation_depth(candidate) == 3, "absorbing-two syntax depth drift")
    return {
        "domain_rows_checked": len(points),
        "depth_at_most_function_counts": level_sizes,
        "first_target_depth": first_depth,
        "candidate_operation_depth": operation_depth(candidate),
        "candidate_distinct_nodes": distinct_node_count(candidate),
    }


def shallow_mux_checks() -> dict[str, object]:
    anchor = Var(0)
    selector = Var(1)
    branches = (Var(2), Var(3), Var(4))
    zero = UnaryU(UnaryU(anchor))
    one = UnaryU(anchor)
    term = shallow_ternary_selector(
        selector,
        zero,
        one,
        anchor,
        *branches,
    )

    checked = 0
    for x, b0, b1, b2 in product(Q, repeat=4):
        arguments = (2, x, b0, b1, b2)
        require(
            evaluate(term, arguments) == arguments[x + 2],
            f"shallow mux failed at {arguments}",
        )
        checked += 1
    weighted_depth = branch_depth(term, frozenset((2, 3, 4)))
    require(weighted_depth == 3, "shallow mux branch depth drift")

    mutated = shallow_ternary_selector(
        selector,
        zero,
        anchor,
        one,
        *branches,
    )
    mutation_mismatches = sum(
        evaluate(mutated, (2, x, b0, b1, b2)) != (b0, b1, b2)[x]
        for x, b0, b1, b2 in product(Q, repeat=4)
    )
    require(mutation_mismatches > 0, "mux constant-swap mutation survived")

    out_of_scope_mismatches = sum(
        evaluate(term, (a, x, b0, b1, b2)) != (b0, b1, b2)[x]
        for a in (0, 1)
        for x, b0, b1, b2 in product(Q, repeat=4)
    )
    require(out_of_scope_mismatches > 0, "branch-scoped mux became global")
    return {
        "anchor_two_rows_checked": checked,
        "branch_depth": weighted_depth,
        "operation_depth_with_dynamic_anchor": operation_depth(term),
        "distinct_nodes": distinct_node_count(term),
        "constant_swap_mutation_mismatches": mutation_mismatches,
        "binary_anchor_out_of_scope_mismatches": out_of_scope_mismatches,
    }


def weighted_depth_two_unsat() -> dict[str, object]:
    """Rule out branch depth two with every unary selector test free."""

    depth = 2
    unary_count = 27
    last_terminal = 29
    unary_kind = 30
    disc_kind = 31

    def unary_value(code: int, selector: int) -> int:
        return (code // (3**selector)) % 3

    def tree_depth(index: int) -> int:
        result = 0
        while index:
            index = (index - 1) // 3
            result += 1
        return result

    node_count = sum(3**level for level in range(depth + 1))
    kinds = [z3.BitVec(f"mux_kind_{index}", 5) for index in range(node_count)]
    solver = z3.SolverFor("QF_BV")
    for index, kind in enumerate(kinds):
        maximum = last_terminal if tree_depth(index) == depth else disc_kind
        solver.add(z3.ULE(kind, maximum))
    def terminal(kind, values):
        selector, b0, b1, b2 = values
        choices = tuple(
            z3.BitVecVal(unary_value(code, selector), 2)
            for code in range(unary_count)
        ) + tuple(z3.BitVecVal(value, 2) for value in (b0, b1, b2))
        result = choices[-1]
        for offset in reversed(range(len(choices) - 1)):
            result = z3.If(kind == offset, choices[offset], result)
        return result

    @cache
    def semantics(index: int, values: tuple[int, int, int, int]):
        kind = kinds[index]
        base = terminal(kind, values)
        if tree_depth(index) == depth:
            return base
        children = tuple(
            semantics(3 * index + offset, values)
            for offset in (1, 2, 3)
        )
        unary_result = z3.If(
            children[0] == 1,
            z3.BitVecVal(0, 2),
            z3.BitVecVal(1, 2),
        )
        disc_result = z3.If(
            children[0] == children[1],
            children[2],
            children[0],
        )
        return z3.If(
            kind == unary_kind,
            unary_result,
            z3.If(kind == disc_kind, disc_result, base),
        )

    valuations = tuple(product(Q, repeat=4))
    for values in valuations:
        solver.add(semantics(0, values) == values[values[0] + 1])
    result = solver.check()
    require(result == z3.unsat, f"weighted depth-two search returned {result}")
    return {
        "solver": "Z3 QF_BV",
        "solver_version": z3.get_version_string(),
        "result": str(result),
        "selector_only_terminal_functions": unary_count,
        "branch_terminals": 3,
        "grammar_nodes": node_count,
        "valuations_checked": len(valuations),
    }


def verify_global_term(
    arity: int,
    table: dict[tuple[int, ...], int],
    term: Expr,
) -> int:
    checked = 0
    for point in product(Q, repeat=arity):
        require(
            evaluate(term, point) == point[table[point]],
            f"global-anchor term failed at arity {arity}, point {point}",
        )
        checked += 1
    return checked


def best_local_term(arity: int, table: dict[tuple[int, ...], int]):
    candidates = []
    for cap in range(1, 5):
        term = compile_local_coding_coordinate_selector(
            arity,
            table,
            block_assignment_cap=cap,
            library_schedule="subcube",
        )
        candidates.append((distinct_node_count(term), cap, term))
    return min(candidates, key=lambda candidate: (candidate[0], candidate[1]))


def best_global_term(arity: int, table: dict[tuple[int, ...], int]):
    candidates = []
    for cap in range(1, 5):
        term = compile_global_subcube_coordinate_selector(
            arity,
            table,
            block_assignment_cap=cap,
        )
        candidates.append((distinct_node_count(term), cap, term))
    return min(candidates, key=lambda candidate: (candidate[0], candidate[1]))


def bounded_compiler_rows() -> tuple[list[dict[str, int]], int]:
    rows = []
    total_checked = 0
    for arity in range(1, 8):
        table = random_compatible_table(arity, 20260817 + arity)
        local_nodes, local_cap, local = best_local_term(arity, table)
        global_nodes, global_cap, global_term = best_global_term(arity, table)
        checked = verify_global_term(arity, table, global_term)
        total_checked += checked
        rows.append(
            {
                "arity": arity,
                "tuples_checked": checked,
                "local_subcube_nodes": local_nodes,
                "local_subcube_depth": expression_depth(local),
                "local_subcube_cap": local_cap,
                "global_anchor_nodes": global_nodes,
                "global_anchor_depth": expression_depth(global_term),
                "global_anchor_cap": global_cap,
            }
        )
    return rows, total_checked


def structural_rows() -> list[dict[str, int]]:
    rows = []
    for arity in (8, 12, 16, 20, 24, 32, 48, 64, 96, 128, 256):
        cap = suggested_global_block_assignment_cap(arity)
        block_positions = 0
        block_assignments = 1
        while (
            block_positions < arity
            and block_assignments * 3 <= cap
        ):
            block_positions += 1
            block_assignments *= 3

        anchor_depth_bound = 3 * math.ceil(math.log2(arity))
        operation_depth_bound = 3 * arity + anchor_depth_bound + 4
        rows.append(
            {
                "arity": arity,
                "block_assignment_cap": cap,
                "block_positions": block_positions,
                "block_assignments": block_assignments,
                "library_functions": 3**block_assignments,
                "prefix_leaves": 3**arity // block_assignments,
                "local_subcube_operation_depth_bound": 4 * arity,
                "global_anchor_operation_depth_bound": operation_depth_bound,
                "global_anchor_executable_depth_bound": operation_depth_bound + 1,
                "depth_bound_improvement": 4 * arity - operation_depth_bound,
            }
        )
    require(rows[-1]["depth_bound_improvement"] > 0, "no asymptotic depth gain")
    return rows


def fold_rows() -> list[dict[str, int]]:
    rows = []
    for arity in range(1, 8):
        term = balanced_absorbing_two(tuple(Var(index) for index in range(arity)))
        checked = 0
        for point in product(Q, repeat=arity):
            expected = 2 if 2 in point else point[0]
            require(evaluate(term, point) == expected, "balanced anchor fold failed")
            checked += 1
        rows.append(
            {
                "arity": arity,
                "tuples_checked": checked,
                "operation_depth": operation_depth(term),
                "distinct_nodes": distinct_node_count(term),
            }
        )
    return rows


def mutation_checks() -> dict[str, bool]:
    table = random_compatible_table(3, 7031)
    invalid_table = dict(table)
    invalid_table.pop(next(iter(invalid_table)))
    invalid_table_rejected = False
    try:
        compile_global_subcube_coordinate_selector(3, invalid_table)
    except RuntimeError:
        invalid_table_rejected = True

    wrong_absorber = Disc(Var(0), UnaryU(UnaryU(Var(0))), Var(1))
    wrong_absorber_rejected = any(
        evaluate(wrong_absorber, point) != (2 if 2 in point else point[0])
        for point in product(Q, repeat=2)
    )
    checks = {
        "invalid_table_rejected": invalid_table_rejected,
        "wrong_absorber_rejected": wrong_absorber_rejected,
    }
    require(all(checks.values()), "one or more global-anchor mutations survived")
    return checks


def main() -> None:
    exhaustive_arity_two_tables = 0
    for table in compatible_tables(2):
        term = compile_global_subcube_coordinate_selector(
            2,
            table,
            block_assignment_cap=3,
        )
        verify_global_term(2, table, term)
        exhaustive_arity_two_tables += 1
    require(exhaustive_arity_two_tables == 128, "arity-two table census drift")

    bounded_rows, bounded_checked = bounded_compiler_rows()
    reduction_arity, reduction_table = reduction_selector_table()
    local_nodes, local_cap, local = best_local_term(
        reduction_arity,
        reduction_table,
    )
    global_nodes, global_cap, global_term = best_global_term(
        reduction_arity,
        reduction_table,
    )
    reduction_checked = verify_global_term(
        reduction_arity,
        reduction_table,
        global_term,
    )

    summary = {
        "schema": "orbit-synthesis/quasiprimal-global-anchor-routing/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "absorbing_depth_closure": absorbing_depth_closure(),
        "shallow_mux": shallow_mux_checks(),
        "weighted_depth_two_search": weighted_depth_two_unsat(),
        "fold_rows": fold_rows(),
        "structural_rows": structural_rows(),
        "exhaustive_arity_two_selector_tables": exhaustive_arity_two_tables,
        "bounded_rows": bounded_rows,
        "bounded_random_tuples_checked": bounded_checked,
        "reduction_row": {
            "arity": reduction_arity,
            "tuples_checked": reduction_checked,
            "local_subcube_nodes": local_nodes,
            "local_subcube_depth": expression_depth(local),
            "local_subcube_cap": local_cap,
            "global_anchor_nodes": global_nodes,
            "global_anchor_depth": expression_depth(global_term),
            "global_anchor_cap": global_cap,
        },
        "mutation_checks": mutation_checks(),
        "claim_boundary": (
            "The finite primitive lower bound concerns selector-only routing "
            "skeletons, not arbitrary global Q-term depth. Compiler evaluations and "
            "structural arithmetic are bounded evidence; the generic same-DAG "
            "O(3^r/r) size and 3r+O(log r) depth claim rests on a separate manuscript "
            "proof. Novelty and coefficient optimality remain unknown."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal global-anchor shallow routing")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

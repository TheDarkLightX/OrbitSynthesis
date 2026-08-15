#!/usr/bin/env python3
"""Exact bounded synthesis check for the five-node direct-Q multiplexer."""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

import z3

ROWS = tuple(product(range(3), repeat=4))  # x,b0,b1,b2
TERMINALS = 7  # x,b0,b1,b2,0,1,2


def terminal_values(row: tuple[int, int, int, int]) -> tuple[int, ...]:
    return row + (0, 1, 2)


def select_expr(
    selector: z3.ArithRef,
    node_index: int,
    row_index: int,
    values: list[list[z3.ArithRef]],
) -> z3.ArithRef:
    options: list[z3.ArithRef] = [
        z3.IntVal(value) for value in terminal_values(ROWS[row_index])
    ]
    options.extend(values[j][row_index] for j in range(node_index))
    expression = options[-1]
    for index in range(len(options) - 2, -1, -1):
        expression = z3.If(selector == index, options[index], expression)
    return expression


def unary(value: z3.ArithRef) -> z3.ArithRef:
    return z3.If(value == 1, 0, 1)


def discriminator(
    left: z3.ArithRef,
    middle: z3.ArithRef,
    right: z3.ArithRef,
) -> z3.ArithRef:
    return z3.If(left == middle, right, left)


def solve_size(node_count: int) -> str:
    solver = z3.Solver()
    operations = [z3.Int(f"op_{i}") for i in range(node_count)]
    first = [z3.Int(f"a_{i}") for i in range(node_count)]
    second = [z3.Int(f"b_{i}") for i in range(node_count)]
    third = [z3.Int(f"c_{i}") for i in range(node_count)]
    values = [
        [z3.Int(f"v_{i}_{row}") for row in range(len(ROWS))]
        for i in range(node_count)
    ]

    for i in range(node_count):
        solver.add(z3.Or(operations[i] == 0, operations[i] == 1))
        solver.add(first[i] >= 0, first[i] < TERMINALS + i)
        solver.add(second[i] >= 0, second[i] < TERMINALS + i)
        solver.add(third[i] >= 0, third[i] < TERMINALS + i)
        solver.add(
            z3.Implies(
                operations[i] == 0,
                z3.And(second[i] == 0, third[i] == 0),
            )
        )

        for row_index in range(len(ROWS)):
            left = select_expr(first[i], i, row_index, values)
            middle = select_expr(second[i], i, row_index, values)
            right = select_expr(third[i], i, row_index, values)
            solver.add(
                values[i][row_index]
                == z3.If(
                    operations[i] == 0,
                    unary(left),
                    discriminator(left, middle, right),
                )
            )
            solver.add(values[i][row_index] >= 0, values[i][row_index] <= 2)

    # Search exact-size irredundant programs. Circuits of every smaller exact
    # size are checked separately below.
    for earlier in range(node_count - 1):
        uses = []
        for later in range(earlier + 1, node_count):
            reference = TERMINALS + earlier
            uses.extend(
                [
                    first[later] == reference,
                    z3.And(operations[later] == 1, second[later] == reference),
                    z3.And(operations[later] == 1, third[later] == reference),
                ]
            )
        solver.add(z3.Or(*uses))

    # Syntactically duplicate nodes never improve a minimum circuit.
    for i in range(node_count):
        for j in range(i):
            solver.add(
                z3.Not(
                    z3.And(
                        operations[i] == operations[j],
                        first[i] == first[j],
                        second[i] == second[j],
                        third[i] == third[j],
                    )
                )
            )

    for row_index, row in enumerate(ROWS):
        solver.add(values[-1][row_index] == row[1 + row[0]])

    result = solver.check()
    if result == z3.sat:
        return "SAT"
    if result == z3.unsat:
        return "UNSAT"
    raise RuntimeError(f"unexpected solver result: {result}")


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


def witness(x: int, b0: int, b1: int, b2: int) -> int:
    node0 = disc(0, x, b0)
    node1 = disc(1, x, b1)
    node2 = disc(x, 2, b2)
    node3 = disc(node1, 1, node2)
    return disc(node0, 0, node3)


def build_receipt() -> dict[str, object]:
    exact_sizes = {str(size): solve_size(size) for size in range(1, 6)}
    if any(exact_sizes[str(size)] != "UNSAT" for size in range(1, 5)):
        raise AssertionError("a sub-five-node mux was found")
    if exact_sizes["5"] != "SAT":
        raise AssertionError("the five-node grammar is unexpectedly unsatisfiable")

    checks = 0
    for x, b0, b1, b2 in ROWS:
        if witness(x, b0, b1, b2) != (b0, b1, b2)[x]:
            raise AssertionError("five-node witness mismatch")
        checks += 1

    result: dict[str, object] = {
        "schema": "orbit-synthesis/direct-q-mux-minimality/v1",
        "status": "exact bounded synthesis",
        "solver": {
            "name": "Z3",
            "version": z3.get_version_string(),
        },
        "grammar": {
            "terminals": ["x", "b0", "b1", "b2", "0", "1", "2"],
            "operations": ["u", "d"],
            "output": "last operation node",
            "sharing": "arbitrary references to earlier nodes",
        },
        "truth_table_rows": len(ROWS),
        "exact_size_results": exact_sizes,
        "witness_nodes": 5,
        "witness_semantic_checks": checks,
        "conclusion": "five operation nodes are necessary and sufficient in the declared grammar",
        "scope_boundary": (
            "This is a local gadget lower bound with dynamic value names treated "
            "as available terminals. It is not a lower bound for the complete "
            "integrated compiler or for richer signatures."
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

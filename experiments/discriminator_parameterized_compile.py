#!/usr/bin/env python3
"""Exhaustive calibration of the parameterized discriminator compiler.

Checks every scalar function on a three-element carrier for arities 1 and 2:

- unary: 3^3 = 27 truth tables;
- binary: 3^9 = 19,683 truth tables.

Also checks the derived selector directly on every x,y,u,v combination.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from orbitsynthesis.discriminator_compile import (  # noqa: E402
    Const,
    Var,
    compile_table,
    distinct_node_count,
    evaluate,
    selector,
)

CARRIER = (0, 1, 2)


def check_selector() -> int:
    checked = 0
    expr = selector(Var(0), Var(1), Var(2), Var(3))
    for values in product(CARRIER, repeat=4):
        x, y, u, v = values
        expected = u if x == y else v
        assert evaluate(expr, values) == expected, values
        checked += 1
    return checked


def check_all_functions(arity: int) -> tuple[int, int]:
    points = tuple(product(CARRIER, repeat=arity))
    functions = 0
    max_nodes = 0

    for outputs in product(CARRIER, repeat=len(points)):
        table = dict(zip(points, outputs))
        expr = compile_table(CARRIER, arity, table)
        for point, expected in table.items():
            assert evaluate(expr, point) == expected, (arity, point, expected)
        functions += 1
        max_nodes = max(max_nodes, distinct_node_count(expr))

    return functions, max_nodes


def main() -> None:
    selector_checks = check_selector()
    unary, unary_nodes = check_all_functions(1)
    binary, binary_nodes = check_all_functions(2)

    assert selector_checks == 3**4
    assert unary == 3**3
    assert binary == 3**9

    print("PASS: parameterized discriminator compiler")
    print(f"selector valuations checked: {selector_checks}")
    print(f"all unary truth tables checked: {unary}; max DAG nodes={unary_nodes}")
    print(f"all binary truth tables checked: {binary}; max DAG nodes={binary_nodes}")


if __name__ == "__main__":
    main()

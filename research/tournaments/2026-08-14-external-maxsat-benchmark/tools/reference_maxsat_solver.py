#!/usr/bin/env python3
"""Independent exhaustive WCNF reference process for adapter tests."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Clause:
    weight: int
    literals: tuple[int, ...]


def parse_wcnf(path: Path) -> tuple[int, int, tuple[Clause, ...]]:
    variable_count = clause_count = top_weight = None
    clauses: list[Clause] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue
        fields = line.split()
        if fields[0] == "p":
            if len(fields) != 5 or fields[1].lower() != "wcnf":
                raise ValueError(f"unsupported WCNF header: {line!r}")
            variable_count = int(fields[2])
            clause_count = int(fields[3])
            top_weight = int(fields[4])
            continue
        if variable_count is None or top_weight is None:
            raise ValueError("WCNF clause appeared before the header")
        values = tuple(int(field) for field in fields)
        if not values or values[-1] != 0:
            raise ValueError(f"WCNF clause is not zero terminated: {line!r}")
        weight = values[0]
        literals = values[1:-1]
        if weight <= 0:
            raise ValueError("WCNF clause weights must be positive")
        if any(not 1 <= abs(literal) <= variable_count for literal in literals):
            raise ValueError("WCNF literal outside the declared variable range")
        clauses.append(Clause(weight, literals))

    if variable_count is None or clause_count is None or top_weight is None:
        raise ValueError("missing WCNF header")
    if len(clauses) != clause_count:
        raise ValueError(
            f"header declares {clause_count} clauses, parsed {len(clauses)}"
        )
    return variable_count, top_weight, tuple(clauses)


def literal_value(mask: int, literal: int) -> bool:
    value = bool(mask & (1 << (abs(literal) - 1)))
    return value if literal > 0 else not value


def solve(
    variable_count: int,
    top_weight: int,
    clauses: tuple[Clause, ...],
) -> tuple[int, int] | None:
    best: tuple[tuple[int, int], int, int] | None = None
    for mask in range(1 << variable_count):
        if any(
            clause.weight >= top_weight
            and not any(literal_value(mask, literal) for literal in clause.literals)
            for clause in clauses
        ):
            continue
        cost = sum(
            clause.weight
            for clause in clauses
            if clause.weight < top_weight
            and not any(literal_value(mask, literal) for literal in clause.literals)
        )
        key = (cost, -mask)
        if best is None or key < best[0]:
            best = (key, mask, cost)
    if best is None:
        return None
    return best[1], best[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--max-vars", type=int, default=24)
    args = parser.parse_args()

    variable_count, top_weight, clauses = parse_wcnf(args.input)
    if variable_count > args.max_vars:
        raise SystemExit(
            f"reference process refuses {variable_count} variables; "
            f"limit is {args.max_vars}"
        )
    result = solve(variable_count, top_weight, clauses)
    if result is None:
        print("s UNSATISFIABLE")
        return 0

    mask, cost = result
    print(f"o {cost}")
    print("s OPTIMUM FOUND")
    literals = [
        str(index + 1 if mask & (1 << index) else -(index + 1))
        for index in range(variable_count)
    ]
    print("v " + " ".join(literals) + " 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

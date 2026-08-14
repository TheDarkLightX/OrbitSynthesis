#!/usr/bin/env python3
"""Exact-group theorem layered on the recursive Boolean compiler."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

from group_optimizer import (
    audit_endpoint_optimizer,
    endpoint_optimum,
    require,
    variable_cost,
)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

ROOT = Path(__file__).resolve().parents[3]
PARENT = (
    ROOT
    / "research/tournaments/2026-08-14-recursive-boolean-library"
    / "check_recursive_boolean_library.py"
)
spec = importlib.util.spec_from_file_location("recursive_boolean_parent", PARENT)
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)

DELTAS = (-2, -1, 0, 1, 2)


def decimal(numerator: int, denominator: int, digits: int = 18) -> str:
    whole, remainder = divmod(numerator, denominator)
    tail = []
    for _ in range(digits):
        remainder *= 10
        digit, remainder = divmod(remainder, denominator)
        tail.append(str(digit))
    return f"{whole}." + "".join(tail)


def candidate(arity: int, delta: int, optimized: bool = True) -> dict[str, object]:
    budget, center, _ = parent.budget(arity)
    width = center + delta
    require(1 <= width < arity, "local width")
    rows = 3**width
    prefix_width = arity - width
    prefix_capacity = 3**prefix_width

    if optimized:
        grouping = endpoint_optimum(rows, width, prefix_capacity)
    else:
        groups = (rows + budget - 1) // budget
        value, table_sum, quotient, remainder = variable_cost(
            rows, width, prefix_capacity, groups
        )
        grouping = {
            "g": groups,
            "variable_cost": value,
            "table_sum": table_sum,
            "row_quotient": quotient,
            "row_remainder": remainder,
            "max_rows": quotient + (1 if remainder else 0),
            "intervals": 0,
        }

    local = 4 * width * grouping["table_sum"] + 5 * width
    prefix = grouping["g"] * (3 * prefix_capacity - 1)
    require(local + prefix == grouping["variable_cost"], "group decomposition")

    branch = parent.binary(arity)
    selector = 3 * rows - 1
    total = (
        local
        + prefix
        + parent.vector(width)
        + parent.vector(prefix_width)
        - 2
        + selector
        + (2 * arity - 1)
        + 6
        + branch["router"]
        + branch["control"]
    )

    ceiling = parent.clog2(arity)
    anchor_depth = ceiling + 2
    local_depth = anchor_depth + 2 * width + 3
    prefix_depth = max(
        local_depth,
        anchor_depth + parent.vdepth(prefix_width),
    ) + prefix_width + 1
    selector_depth = max(
        prefix_depth,
        anchor_depth + parent.vdepth(width),
    ) + width + 1
    depth = max(anchor_depth + 4, branch["depth"] + 2, selector_depth + 4)

    return {
        "delta": delta,
        "J": budget,
        "T": center,
        "t": width,
        "N": rows,
        "s": prefix_width,
        "P": prefix_capacity,
        **grouping,
        "local": local,
        "prefix": prefix,
        "selector": selector,
        "binary_router": branch["router"],
        "binary_control": branch["control"],
        "total": total,
        "depth": depth,
    }


def choose(arity: int) -> dict[str, object]:
    rows = [candidate(arity, delta) for delta in DELTAS]
    return min(rows, key=lambda row: (row["total"], row["delta"], row["g"]))


def analytic_tail() -> dict[str, object]:
    bases = []
    for arity in (340, 341):
        exponent = math.ceil(3 * arity / 2)
        require(9 * arity**3 * 2**exponent <= 3**arity, "tail base")
        bases.append([arity, exponent])
    require(8 * 342**3 < 9 * 340**3, "two-step tail induction")

    numerator = (
        2 * 9 * 340 * 36 * 340 * 1000
        + 26 * 36 * 340 * 1000
        + (3 * 340 + 1) * 9 * 340 * 1000
        + 4 * 9 * 340 * 36 * 340
    )
    denominator = 9 * 340 * 36 * 340 * 1000
    require(50 * numerator < 123 * denominator, "123/50 tail")
    return {
        "J_bases": bases,
        "J_step": "8*342^3<9*340^3",
        "tail_fraction": [numerator, denominator],
        "target": "123/50",
        "note": "optimized grouping is no larger than the scheduled tail candidate",
    }


def ledger_audit() -> dict[str, object]:
    maximum = (-1, 1, -1)
    finite_maximum = (-1, 1, -1)
    histogram = {delta: 0 for delta in DELTAS}
    selected = []
    minimum_depth_slack = (10**9, -1)

    for arity in range(64, 16385):
        if arity <= 339:
            row = choose(arity)
        else:
            budget, center, _ = parent.budget(arity)
            delta = 0 if 3**center == arity * budget else 1
            row = candidate(arity, delta, optimized=False)

        histogram[row["delta"]] += 1
        universe = 3**arity
        numerator = row["total"] * arity
        require(50 * numerator < 123 * universe, "123/50 size")

        ceiling = parent.clog2(arity)
        depth_bound = arity + ceiling + 2 * math.ceil((4 * ceiling + 2) / 3) + 15
        require(row["depth"] <= depth_bound, "depth theorem")
        slack = depth_bound - row["depth"]
        if slack < minimum_depth_slack[0]:
            minimum_depth_slack = (slack, arity)

        if numerator * maximum[1] > maximum[0] * universe:
            maximum = (numerator, universe, arity)
        if arity <= 339 and numerator * finite_maximum[1] > finite_maximum[0] * universe:
            finite_maximum = (numerator, universe, arity)

        if arity >= 340:
            budget = row["J"]
            require(2 * budget >= 3 * arity, "J/r bound")
            require(row["N"] >= arity * budget, "N lower bound")
            require(row["N"] < 3 * arity * budget, "N upper bound")
            require(row["g"] < 3 * arity + 1, "group bound")
            skeleton = row["local"] - 5 * row["t"]
            require(
                9 * skeleton * arity**3
                <= 4 * row["t"] * (3 * arity + 1) * universe,
                "local tail bound",
            )
            require(32 * ceiling <= arity, "ceiling/arity bound")
            require(
                1000 * 5 * 3 ** ((row["s"] + 1) // 2) * arity < universe,
                "prefix error",
            )
            fixed = (
                5 * row["t"]
                + parent.vector(row["t"])
                + row["selector"]
                + (2 * arity - 1)
                + 6
            )
            require(1000 * fixed * arity < universe, "fixed group")
            require(1000 * row["binary_router"] * arity < universe, "binary router")
            require(1000 * row["binary_control"] * arity < universe, "binary control")
            require(
                (9 * row["g"] + 4) * row["P"] * arity * budget
                <= (9 * arity + 13) * universe,
                "prefix main",
            )

        if arity in (64, 65, 66, 67, 68, 72, 100, 339, 340, 1000, 4096, 16384):
            selected.append(
                {
                    "r": arity,
                    "delta": row["delta"],
                    "t": row["t"],
                    "g": row["g"],
                    "max_rows": row["max_rows"],
                    "intervals": row["intervals"],
                    "size_ratio": decimal(numerator, universe),
                    "depth": row["depth"],
                    "depth_bound": depth_bound,
                }
            )

    require(maximum[2] == 65, "maximum location")
    require(finite_maximum[2] == 65, "finite maximum location")
    return {
        "range": [64, 16384],
        "finite_optimizer_range": [64, 339],
        "tail_schedule": "t=ceil(log_3(rJ)), g=ceil(3^t/J)",
        "deltas": list(DELTAS),
        "choice_histogram": {str(key): value for key, value in histogram.items()},
        "size_bound": "50*size*r<123*3^r",
        "depth_bound": "r+C+2*ceil((4C+2)/3)+15",
        "maximum": {"r": maximum[2], "ratio": decimal(maximum[0], maximum[1])},
        "finite": {
            "range": [64, 339],
            "maximum_r": finite_maximum[2],
            "maximum_ratio": decimal(finite_maximum[0], finite_maximum[1]),
        },
        "minimum_depth_slack": {
            "r": minimum_depth_slack[1],
            "value": minimum_depth_slack[0],
        },
        "selected": selected,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/optimal-group-recursive-boolean/v1",
        "optimizer": audit_endpoint_optimizer(),
        "analytic_tail": analytic_tail(),
        "ledger": ledger_audit(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    expected = None
    output = None
    arguments = iter(sys.argv[1:])
    for argument in arguments:
        if argument == "--expected":
            expected = Path(next(arguments))
        elif argument == "--out":
            output = Path(next(arguments))
        else:
            raise SystemExit(argument)

    result = make_receipt()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if expected is not None:
        require(result == json.loads(expected.read_text()), "receipt drift")
    if output is not None:
        output.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

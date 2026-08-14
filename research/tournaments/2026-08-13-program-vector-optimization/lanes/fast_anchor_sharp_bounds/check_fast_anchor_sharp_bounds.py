#!/usr/bin/env python3
"""Standalone audit for the pivot-normalized anchor and sharp compiler bounds."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
from functools import cache
from pathlib import Path

Q = (0, 1, 2)
B = (0, 1)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    return (1, 0, 1)[x]


def clog2(n: int) -> int:
    require(n >= 1, "clog2 domain")
    return (n - 1).bit_length()


def clog3(n: int) -> int:
    require(n >= 1, "clog3 domain")
    power = 1
    exponent = 0
    while power < n:
        power *= 3
        exponent += 1
    return exponent


def floor_power3(n: int) -> tuple[int, int]:
    require(n >= 1, "floor_power3 domain")
    power = 1
    exponent = 0
    while 3 * power <= n:
        power *= 3
        exponent += 1
    return exponent, power


def ratio(numerator: int, denominator: int, digits: int = 18) -> str:
    whole, remainder = divmod(numerator, denominator)
    tail = []
    for _ in range(digits):
        remainder *= 10
        digit, remainder = divmod(remainder, denominator)
        tail.append(str(digit))
    return f"{whole}." + "".join(tail)


def merge_status(left: int, identity: int, right: int) -> int:
    return d(left, identity, right)


def balanced_merge(values: list[int], identity: int) -> int:
    require(values, "empty status list")
    while len(values) > 1:
        next_values = []
        index = 0
        while index + 1 < len(values):
            next_values.append(merge_status(values[index], identity, values[index + 1]))
            index += 2
        if index < len(values):
            next_values.append(values[index])
        values = next_values
    return values[0]


def fast_anchor(point: tuple[int, ...]) -> int:
    arity = len(point)
    require(arity >= 1, "empty point")
    if arity == 1:
        return point[0]
    if arity == 2:
        pivot = point[1]
        return d(pivot, u(u(pivot)), point[0])

    pivot = point[1]
    identity = u(pivot)
    robust = d(pivot, u(identity), d(point[2], pivot, identity))
    statuses = [robust]
    statuses.extend(d(point[index], pivot, identity) for index in range(3, arity))
    statuses.append(point[0])
    return balanced_merge(statuses, identity)


def anchor_reference(point: tuple[int, ...]) -> int:
    return point[0] if all(value in B for value in point) else 2


def anchor_audit() -> dict[str, object]:
    rows = []
    evaluations = 0
    for arity in range(1, 9):
        for point in itertools.product(Q, repeat=arity):
            require(fast_anchor(point) == anchor_reference(point), "anchor semantics")
            evaluations += 1
        nodes = 0 if arity == 1 else 3 if arity == 2 else 2 * arity - 1
        depth = 0 if arity == 1 else 3 if arity == 2 else clog2(arity) + 2
        rows.append({"r": arity, "node_bound": nodes, "depth_bound": depth})

    mutation = None
    for point in itertools.product(Q, repeat=3):
        x0, pivot, witness = point
        identity = u(pivot)
        bad = d(pivot, identity, d(witness, pivot, identity))
        if bad != anchor_reference(point):
            mutation = {
                "point": list(point),
                "mutated": bad,
                "expected": anchor_reference(point),
            }
            break
    require(mutation is not None, "anchor mutation ineffective")
    return {
        "evaluations": evaluations,
        "r_ge_3_node_bound": "2r-1",
        "r_ge_3_depth_bound": "ceil(log2 r)+2",
        "rows": rows,
        "mutation": mutation,
    }


def split(width: int) -> tuple[int, int]:
    return (width + 1) // 2, width // 2


@cache
def generic_count(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 4
    left, right = split(width)
    return (
        generic_count(left)
        + generic_count(right)
        + 3**width
        + 3**left * (3**right - 1) // 2
    )


@cache
def extended_count(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 4
    left, right = split(width)
    return (
        generic_count(left)
        + extended_count(right)
        + 2 * 3**width
        - 3 ** (width - 1)
        + 3**left * (3**right - 1) // 2
    )


@cache
def p_vector_count(width: int) -> int:
    if width == 0:
        return 2
    if width == 1:
        return 5
    left, right = split(width)
    return (
        2
        + generic_count(left)
        + extended_count(right)
        + 3**left * (3**right - 1) // 2
        + 3**width
        - (3 ** (width - 1) + 1) // 2
    )


def vector_depth(width: int) -> int:
    return 2 if width == 0 else 3 + clog2(width)


def schedule(r: int) -> dict[str, int]:
    reserve = 4 + clog3(r * r)
    high = r - reserve
    b, block = floor_power3(high)
    s = r - b
    return {"L": reserve, "H": high, "M": block, "b": b, "s": s, "P": 3**s}


def binary_ledger(r: int) -> dict[str, int]:
    k = math.isqrt(r)
    q = 3**k
    width = q.bit_length() - 1
    count = r - 1
    residual = count % width
    chunks = ([residual] if residual else []) + [width] * (count // width)
    prefix = 1
    instances = 0
    controls = 0
    for chunk in chunks:
        instances += prefix
        controls += 6 * q * (2**chunk - 1)
        prefix *= 2**chunk
    require(prefix == 2 ** (r - 1), "binary partition")
    return {
        "router": (3 * q - 1) // 2 * instances,
        "control": controls,
        "depth": (k + 1) * len(chunks) + 2 * width + 1,
        "k": k,
        "w": width,
        "levels": len(chunks),
    }


def exact_row(r: int) -> dict[str, int]:
    plan = schedule(r)
    local = (3 * plan["M"] - 1) * 3 ** plan["M"]
    prefix = 3 * plan["P"] - 1
    vectors = p_vector_count(plan["b"]) + p_vector_count(plan["s"]) - 2
    anchor = 2 * r - 1
    nonbinary = local + prefix + vectors + anchor + 2 + 3
    binary = binary_ledger(r)
    total = nonbinary + binary["router"] + binary["control"] + 1

    c = clog2(r)
    anchor_depth = c + 2
    local_depth = anchor_depth + vector_depth(plan["b"]) + plan["b"] + 1
    prefix_depth = max(local_depth, anchor_depth + vector_depth(plan["s"])) + plan["s"] + 1
    before_glue = prefix_depth + 2
    final_depth = max(anchor_depth + 2, binary["depth"], before_glue) + 2
    return {
        **plan,
        "local": local,
        "prefix": prefix,
        "vectors": vectors,
        "anchor": anchor,
        "nonbinary": nonbinary,
        "binary_router": binary["router"],
        "binary_control": binary["control"],
        "binary_depth": binary["depth"],
        "before_glue": before_glue,
        "total": total,
        "final_depth": final_depth,
        "C": c,
    }


def analytic_bases() -> dict[str, object]:
    require(3**32 > 5000 * 65, "prefix error base")
    require(3**64 > 7000 * 64**2, "fixed group base")
    require(192 * 2**64 < 3**50, "binary router margin")
    require(24 * 64**2 < 3**42, "binary control margin")
    power_rows = []
    log_rows = []
    for c in range(6, 11):
        left_power = 6 * 3 ** (math.floor(3 * c / 5) - 2)
        right_power = 2 ** (c - 1)
        require(left_power <= right_power, "five-step power base")
        power_rows.append([c, left_power, right_power])
        left_log = c - 1
        right_log = 2 ** math.ceil(2 * c / 5)
        require(left_log <= right_log, "five-step log base")
        log_rows.append([c, left_log, right_log])
    require(9 * 93 == 31 * 27, "schedule equality")
    require(5 + 2 * math.log(105, 3) <= 4 * 105 / 31, "schedule tail base")
    require(4 / 31 - 2 / (105 * math.log(3)) > 0, "schedule derivative")
    return {
        "power_rows": power_rows,
        "log_rows": log_rows,
        "schedule_equality": "9*93=31*27",
        "prefix_error": "3^32>5000*65",
        "fixed_group": "3^64>7000*64^2",
        "binary_router": "192*2^64<3^50",
        "binary_control": "24*64^2<3^42",
    }


def ledger_audit() -> dict[str, object]:
    maximum = (-1, 1, -1)
    minimum_slack = (10**9, -1)
    selected = []
    for r in range(64, 16385):
        row = exact_row(r)
        unit = 3**r
        total_numerator = row["total"] * r

        require(9 * r <= 31 * row["M"], "r/M bound")
        require(total_numerator < 15 * unit, "exact size bound")
        require(row["local"] * 27 * r < unit, "local U/27")

        require(13 * row["P"] * r * 9 <= 403 * unit, "prefix main")
        error = 5 * 3 ** ((row["s"] + 1) // 2)
        require(error * 1000 * r < unit, "prefix error")

        fixed = p_vector_count(row["b"]) + row["anchor"] + 2 + 3 + 1
        require(fixed < 7 * r, "fixed group")
        require(fixed * 1000 * r < unit, "fixed U/1000")
        require(row["binary_router"] * 1000 * r < unit, "binary router U/1000")
        require(row["binary_control"] * 1000 * r < unit, "binary control U/1000")

        c = row["C"]
        require(row["b"] < c, "b<C")
        require(row["b"] >= c - math.ceil(2 * c / 5) - 1, "b lower")
        require(clog2(row["b"]) <= math.ceil(2 * c / 5), "log b")
        depth_bound = r + math.ceil(7 * c / 5) + 11
        require(row["final_depth"] <= depth_bound, "depth bound")
        slack = depth_bound - row["final_depth"]
        if slack < minimum_slack[0]:
            minimum_slack = (slack, r)

        if total_numerator * maximum[1] > maximum[0] * unit:
            maximum = (total_numerator, unit, r)
        if r in (64, 68, 82, 93, 94, 105, 128, 256, 512, 1024, 4096, 16384):
            selected.append(
                {
                    "r": r,
                    "C": c,
                    "M": row["M"],
                    "b": row["b"],
                    "s": row["s"],
                    "size_ratio": ratio(total_numerator, unit),
                    "binary_depth": row["binary_depth"],
                    "nonbinary_final_depth": row["before_glue"] + 2,
                    "final_depth": row["final_depth"],
                    "depth_bound": depth_bound,
                }
            )

    require(maximum[2] == 93, "maximum ratio arity")
    for r in range(64, 100):
        row = exact_row(r)
        require(
            row["binary_depth"] + 2
            <= r + math.ceil(7 * row["C"] / 5) + 11,
            "small binary depth",
        )
    tail = (
        100 / 3
        - (73 / 15) * math.sqrt(100)
        + (7 / 5) * math.log2(100)
        + 19 / 3
    )
    require(tail > 0, "binary tail base")
    require(1 / 3 - 73 / (30 * math.sqrt(100)) > 0, "binary tail derivative")
    return {
        "arity_range": [64, 16384],
        "size_bound": "total<15*3^r/r",
        "depth_bound": "r+ceil(7*ceil(log2 r)/5)+11",
        "maximum_ratio": {
            "r": maximum[2],
            "value": ratio(maximum[0], maximum[1]),
            "dominant_term": "403/27",
        },
        "minimum_depth_slack": {"r": minimum_slack[1], "value": minimum_slack[0]},
        "selected": selected,
        "binary_tail_base": f"{tail:.12f}",
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/fast-anchor-sharp-bounds/v1",
        "anchor": anchor_audit(),
        "analytic_bases": analytic_bases(),
        "ledger": ledger_audit(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    expected = None
    output = None
    args = iter(sys.argv[1:])
    for arg in args:
        if arg == "--expected":
            expected = Path(next(args))
        elif arg == "--out":
            output = Path(next(args))
        else:
            raise SystemExit(f"unknown argument: {arg}")

    result = make_receipt()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if expected is not None:
        require(result == json.loads(expected.read_text()), "receipt drift")
    if output is not None:
        output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

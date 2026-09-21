#!/usr/bin/env python3
"""Standalone audit for the two-slice smoothed fixed-Q compiler ledger."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import sys
from functools import cache
from pathlib import Path

Q = (0, 1, 2)
B = (0, 1)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


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
    require(n >= 1, "floor-power domain")
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


def binary_ledger(r: int) -> dict[str, int]:
    k = math.isqrt(r)
    q = 3**k
    width = q.bit_length() - 1
    remaining = r - 1
    residual = remaining % width
    chunks = ([residual] if residual else []) + [width] * (remaining // width)
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
    }


def schedule(r: int) -> dict[str, int]:
    reserve = 4 + clog3(r * r)
    high = r - reserve
    b, m = floor_power3(high)
    mode = 2 if 2 * m <= high else 1
    s = r - b if mode == 1 else r - b - 1
    return {
        "r": r,
        "L": reserve,
        "H": high,
        "b": b,
        "m": m,
        "mode": mode,
        "M": mode * m,
        "s": s,
        "P": 3**s,
    }


def exact_row(r: int) -> dict[str, int]:
    plan = schedule(r)
    b = plan["b"]
    m = plan["m"]
    s = plan["s"]
    p = plan["P"]
    anchor = 2 * r - 1
    binary = binary_ledger(r)
    c = clog2(r)
    anchor_depth = c + 2

    if plan["mode"] == 1:
        local_main = (3 * m - 1) * 3**m
        local_residual = 0
        prefix_routers = 3 * p - 1
        vectors = p_vector_count(b) + p_vector_count(s) - 2
        slice_selectors = 0
        local_depth = anchor_depth + vector_depth(b) + b + 1
        prefix_depth = max(local_depth, anchor_depth + vector_depth(s)) + s + 1
        nonbinary_final_depth = prefix_depth + 4
    else:
        local_main = (9 * m - 1) * 3 ** (2 * m)
        local_residual = (3 * m - 1) * 3**m
        prefix_routers = 6 * p - 2
        vectors = (
            p_vector_count(b + 1)
            + p_vector_count(b)
            + p_vector_count(s)
            - 4
        )
        slice_selectors = 6
        wide_depth = anchor_depth + vector_depth(b + 1) + b + 2
        narrow_depth = anchor_depth + vector_depth(b) + b + 1
        prefix_control_depth = anchor_depth + vector_depth(s)
        prefix_depth = max(wide_depth, narrow_depth, prefix_control_depth) + s + 1
        nonbinary_final_depth = prefix_depth + 6

    fixed_nodes = anchor + 2 + 3 + 1 + slice_selectors
    total = (
        local_main
        + local_residual
        + prefix_routers
        + vectors
        + fixed_nodes
        + binary["router"]
        + binary["control"]
    )
    final_depth = max(anchor_depth + 4, binary["depth"] + 2, nonbinary_final_depth)
    return {
        **plan,
        "local_main": local_main,
        "local_residual": local_residual,
        "prefix_routers": prefix_routers,
        "vectors": vectors,
        "fixed_nodes": fixed_nodes,
        "binary_router": binary["router"],
        "binary_control": binary["control"],
        "binary_final_depth": binary["depth"] + 2,
        "nonbinary_final_depth": nonbinary_final_depth,
        "final_depth": final_depth,
        "C": c,
        "total": total,
    }


def slice_tables(sigma):
    wide = {}
    narrow = {}
    for prefix in Q:
        # The third wide block is padding; the correct guard never selects it.
        wide[prefix] = {
            (digit, local): (prefix, digit, local)[sigma((prefix, digit, local))]
            if digit in B else 0
            for digit in Q for local in Q
        }
        narrow[prefix] = {
            local: (prefix, 2, local)[sigma((prefix, 2, local))]
            for local in Q
        }
    return wide, narrow


def route_slice(wide, narrow, point, *, invert_guard=False):
    prefix, digit, local = point
    if (digit == 2) != invert_guard:
        return narrow[prefix][local]
    return wide[prefix][(digit, local)]


def decomposition_audit() -> dict[str, object]:
    points = list(itertools.product(Q, repeat=3))
    rows = 0
    labels = []
    selectors = [
        ("projection-0", lambda point: 0),
        ("projection-1", lambda point: 1),
        ("projection-2", lambda point: 2),
    ]
    for seed in range(61):
        rng = random.Random(0x2A51CE + seed)
        table = {point: rng.randrange(3) for point in points}
        selectors.append((f"seed-{seed}", lambda point, table=table: table[point]))

    for label, sigma in selectors:
        wide, narrow = slice_tables(sigma)
        for point in points:
            reconstructed = route_slice(wide, narrow, point)
            require(reconstructed == point[sigma(point)], "slice reconstruction")
            rows += 1
        labels.append(label)

    mutation = None
    wide, narrow = slice_tables(lambda point: 1)
    for point in points:
        expected = point[1]
        bad = route_slice(wide, narrow, point, invert_guard=True)
        if bad != expected:
            mutation = {
                "point": list(point),
                "mutated": bad,
                "expected": expected,
            }
            break
    require(mutation is not None, "slice mutation ineffective")
    return {
        "selectors": len(selectors),
        "rows": rows,
        "wide_points": 6,
        "narrow_points": 3,
        "labels_sha256": hashlib.sha256("\n".join(labels).encode()).hexdigest(),
        "mutation": mutation,
    }


def analytic_bases() -> dict[str, object]:
    require(5000 * 65 < 3**32, "prefix error base")
    require(7000 * 64**2 < 3**64, "fixed error base")
    require(1500 * 64**2 < 3**32, "narrow error even base")
    require(1500 * 65**2 < 3**32, "narrow error odd base")
    require(192 * 2**64 < 3**50, "binary router margin")
    require(24 * 64**2 < 3**42, "binary control margin")

    mode2_log_rows = []
    for c in range(6, 11):
        left = (2 * (c - 1) + 2) // 3
        right = 2 ** ((2 * c + 4) // 5 - 1)
        require(left <= right, "mode-two logarithm base")
        mode2_log_rows.append([c, left, right])
    return {
        "prefix_error": "5000*65<3^32",
        "fixed_error": "7000*64^2<3^64",
        "narrow_even": "1500*64^2<3^32",
        "narrow_odd": "1500*65^2<3^32",
        "binary_router": "192*2^64<3^50",
        "binary_control": "24*64^2<3^42",
        "mode2_log_rows": mode2_log_rows,
    }


def ledger_audit() -> dict[str, object]:
    maximum = (-1, 1, -1)
    selected = []
    mode_counts = {1: 0, 2: 0}
    minimum_slack = (10**9, -1)

    for r in range(64, 16385):
        row = exact_row(r)
        mode_counts[row["mode"]] += 1
        unit = 3**r
        total_numerator = row["total"] * r
        require(2 * total_numerator < 21 * unit, "10.5-unit total")

        require(9 * r <= 31 * row["m"], "31/9 schedule bound")

        half_error = 5 * 3 ** ((row["s"] + 1) // 2)
        require(1000 * r * half_error < unit, "prefix half error")
        require(1000 * r * row["binary_router"] < unit, "binary router")
        require(1000 * r * row["binary_control"] < unit, "binary control")

        if row["mode"] == 1:
            require(27 * r <= 65 * row["m"], "mode-one ratio")
            if row["b"] == 3:
                require(r <= 65, "mode-one base interval")
            else:
                require(6 * (row["L"] - 1) <= row["m"], "mode-one reserve")
            require(27 * r * row["local_main"] < unit, "mode-one local")
            local_vectors = p_vector_count(row["b"])
            fixed_upper = local_vectors + (2 * r - 1) + 2 + 3 + 1
            require(fixed_upper < 7 * r, "mode-one fixed linear")
        else:
            require(2 * row["m"] <= row["H"], "mode-two availability")
            require(18 * r <= 31 * row["M"], "mode-two effective ratio")
            require(18 * r * row["local_main"] < unit, "mode-two wide local")
            require(1000 * r * row["local_residual"] < unit, "mode-two narrow")
            local_vectors = p_vector_count(row["b"] + 1) + p_vector_count(row["b"])
            fixed_upper = local_vectors + 6 + (2 * r - 1) + 2 + 3 + 1
            require(fixed_upper < 7 * r, "mode-two fixed linear")

            c = row["C"]
            require(3 ** row["b"] < 2 ** (c - 1), "mode-two exponent")
            require(
                clog2(row["b"] + 1) <= (2 * c + 4) // 5 - 1,
                "mode-two log b",
            )

        require(1000 * r * fixed_upper < unit, "fixed group")
        depth_bound = r + (7 * row["C"] + 4) // 5 + 12
        require(row["final_depth"] <= depth_bound, "depth bound")
        slack = depth_bound - row["final_depth"]
        if slack < minimum_slack[0]:
            minimum_slack = (slack, r)

        if total_numerator * maximum[1] > maximum[0] * unit:
            maximum = (total_numerator, unit, r)
        if r in (64, 65, 66, 93, 94, 175, 176, 256, 512, 1024, 4096, 16384):
            selected.append(
                {
                    "r": r,
                    "mode": row["mode"],
                    "M": row["M"],
                    "b": row["b"],
                    "s": row["s"],
                    "size_ratio": ratio(total_numerator, unit),
                    "final_depth": row["final_depth"],
                    "depth_bound": depth_bound,
                }
            )

    require(maximum[2] == 65, "maximum ratio arity")
    return {
        "arity_range": [64, 16384],
        "mode_counts": {str(key): value for key, value in mode_counts.items()},
        "size_bound": "2*size*r<21*3^r",
        "depth_bound": "r+ceil(7*ceil(log2 r)/5)+12",
        "maximum_ratio": {
            "r": maximum[2],
            "value": ratio(maximum[0], maximum[1]),
        },
        "minimum_depth_slack": {
            "r": minimum_slack[1],
            "value": minimum_slack[0],
        },
        "selected": selected,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/two-slice-compiler/v1",
        "decomposition": decomposition_audit(),
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
        require(rendered.encode("utf-8") == expected.read_bytes(), "receipt drift")
    if output is not None:
        output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

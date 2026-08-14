#!/usr/bin/env python3
"""Standalone audit for the early-switch two-slice fixed-Q compiler."""

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


def base_schedule(r: int) -> dict[str, int]:
    reserve = 4 + clog3(r * r)
    high = r - reserve
    b, m = floor_power3(high)
    return {"r": r, "L": reserve, "H": high, "b": b, "m": m}


def schedule(r: int) -> dict[str, int]:
    plan = base_schedule(r)
    mode = 2 if plan["H"] >= 2 * plan["m"] - 4 else 1
    plan["mode"] = mode
    plan["s"] = r - plan["b"] if mode == 1 else r - plan["b"] - 1
    plan["M"] = plan["m"] if mode == 1 else 2 * plan["m"]
    plan["P"] = 3 ** plan["s"]
    return plan


def exact_mode_row(r: int, mode: int) -> dict[str, int]:
    plan = base_schedule(r)
    b = plan["b"]
    m = plan["m"]
    s = r - b if mode == 1 else r - b - 1
    p = 3**s
    anchor = 2 * r - 1
    binary = binary_ledger(r)
    c = clog2(r)
    anchor_depth = c + 2

    if mode == 1:
        local_main = (3 * m - 1) * 3**m
        local_residual = 0
        prefix_routers = 3 * p - 1
        vectors = p_vector_count(b) + p_vector_count(s) - 2
        slice_selectors = 0
        local_depth = anchor_depth + vector_depth(b) + b + 1
        prefix_depth = max(local_depth, anchor_depth + vector_depth(s)) + s + 1
        nonbinary_final_depth = prefix_depth + 4
    elif mode == 2:
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
    else:
        raise RuntimeError("mode")

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
        "mode": mode,
        "s": s,
        "P": p,
        "M": m if mode == 1 else 2 * m,
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


def exact_row(r: int) -> dict[str, int]:
    plan = schedule(r)
    return exact_mode_row(r, plan["mode"])


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
        rng = random.Random(0xE4715E + seed)
        table = {point: rng.randrange(3) for point in points}
        selectors.append((f"seed-{seed}", lambda point, table=table: table[point]))

    for label, sigma in selectors:
        wide = {}
        narrow = {}
        for prefix in Q:
            wide[prefix] = {
                (slice_digit, local):
                    (prefix, slice_digit, local)[sigma((prefix, slice_digit, local))]
                for slice_digit in B
                for local in Q
            }
            narrow[prefix] = {
                local: (prefix, 2, local)[sigma((prefix, 2, local))]
                for local in Q
            }
        for point in points:
            prefix, slice_digit, local = point
            reconstructed = (
                narrow[prefix][local]
                if slice_digit == 2
                else wide[prefix][(slice_digit, local)]
            )
            require(reconstructed == point[sigma(point)], "slice reconstruction")
            rows += 1
        labels.append(label)

    mutation = None
    for point in points:
        prefix, slice_digit, local = point
        expected = point[1]
        bad = local if slice_digit == 2 else 2
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
    require(1500 * 64**2 < 3**32, "residual even base")
    require(1500 * 65**2 < 3**32, "residual odd base")
    require(192 * 2**64 < 3**50, "binary router margin")
    require(24 * 64**2 < 3**42, "binary control margin")

    mode1_rows = []
    for b in range(4, 12):
        require(2 * b + 1 <= 3 ** (b - 2), "mode-one induction base")
        mode1_rows.append([b, 2 * b + 1, 3 ** (b - 2)])

    exceptional_rows = []
    for b in range(4, 12):
        m = 3**b
        for offset in (0, 1):
            c = 2 * b + 2
            r = 2 * m + c + offset
            require(3 ** (c - 1) < r * r < 3**c, "exceptional ceiling")
            exceptional_rows.append([b, offset, r, c])

    require(5 * (248 * 250 + 27) < 46 * 27 * 250, "mode-one 46/5")
    require(31 * 172 * 5 < 46 * 729 * 5, "exceptional t0")
    require(25 * 173 * 5 < 46 * 729 * 5, "exceptional t1")
    require(
        (682 * 31 + 9 * 81) * 5 < 46 * 81 * 31,
        "mode-two tail",
    )
    return {
        "prefix_error": "5000*65<3^32",
        "fixed_error": "7000*64^2<3^64",
        "residual_even": "1500*64^2<3^32",
        "residual_odd": "1500*65^2<3^32",
        "binary_router": "192*2^64<3^50",
        "binary_control": "24*64^2<3^42",
        "mode1_rows": mode1_rows,
        "exceptional_rows": exceptional_rows,
        "clean_constant": "46/5",
    }


def ledger_audit() -> dict[str, object]:
    maximum = (-1, 1, -1)
    selected = []
    mode_counts = {1: 0, 2: 0}
    minimum_slack = (10**9, -1)
    crossover_mismatches = []
    threshold_rows = []

    for r in range(64, 16385):
        row = exact_row(r)
        mode_counts[row["mode"]] += 1
        unit = 3**r
        total_numerator = row["total"] * r
        require(5 * total_numerator < 46 * unit, "46/5 total")
        require(9 * r <= 31 * row["m"], "31/9 schedule bound")

        half_error = 5 * 3 ** ((row["s"] + 1) // 2)
        require(1000 * r * half_error < unit, "prefix half error")
        require(1000 * r * row["binary_router"] < unit, "binary router")
        require(1000 * r * row["binary_control"] < unit, "binary control")

        if row["mode"] == 1:
            require(row["H"] <= 2 * row["m"] - 5, "mode-one threshold")
            require(row["b"] >= 4, "mode-one small block")
            require(9 * r <= 19 * row["m"], "mode-one 19/9 ratio")
            require(27 * r * row["local_main"] < unit, "mode-one local")
            fixed_upper = (
                p_vector_count(row["b"])
                + (2 * r - 1)
                + 2
                + 3
                + 1
            )
            require(fixed_upper < 7 * r, "mode-one fixed linear")
        else:
            require(row["H"] >= 2 * row["m"] - 4, "mode-two threshold")
            residual = row["local_residual"]
            require(1000 * r * residual < unit, "mode-two residual")
            fixed_upper = (
                p_vector_count(row["b"] + 1)
                + p_vector_count(row["b"])
                + 6
                + (2 * r - 1)
                + 2
                + 3
                + 1
            )
            require(fixed_upper < 7 * r, "mode-two fixed linear")

            t = row["H"] - (2 * row["m"] - 4)
            if t == 0:
                require(row["b"] >= 4, "t0 small block")
                require(clog3(r * r) == 2 * row["b"] + 2, "t0 ceiling")
                require(81 * r <= 172 * row["m"], "t0 x bound")
                require(
                    729 * r * row["local_main"]
                    < 172 * row["m"] * 3**r,
                    "t0 wide bound",
                )
            elif t == 1:
                require(row["b"] >= 4, "t1 small block")
                require(clog3(r * r) == 2 * row["b"] + 2, "t1 ceiling")
                require(81 * r <= 173 * row["m"], "t1 x bound")
                require(
                    2187 * r * row["local_main"]
                    < 173 * row["m"] * 3**r,
                    "t1 wide bound",
                )
            else:
                require(t >= 2, "tail offset")
                require(
                    r * r * row["local_main"] < row["m"] * 3**r,
                    "tail wide bound",
                )

        require(1000 * r * fixed_upper < unit, "fixed group")

        depth_bound = r + math.ceil(7 * row["C"] / 5) + 12
        require(row["final_depth"] <= depth_bound, "depth bound")
        slack = depth_bound - row["final_depth"]
        if slack < minimum_slack[0]:
            minimum_slack = (slack, r)

        ordinary = exact_mode_row(r, 1)
        sliced = exact_mode_row(r, 2)
        exact_smaller = 1 if ordinary["total"] <= sliced["total"] else 2
        if exact_smaller != row["mode"]:
            crossover_mismatches.append(r)

        if total_numerator * maximum[1] > maximum[0] * unit:
            maximum = (total_numerator, unit, r)

        if (
            r in (64, 65, 66, 93, 94, 170, 171, 172, 173, 257, 258,
                  497, 498, 745, 746, 1471, 1472, 4096, 16384)
        ):
            selected.append(
                {
                    "r": r,
                    "mode": row["mode"],
                    "H": row["H"],
                    "m": row["m"],
                    "offset": row["H"] - (2 * row["m"] - 4),
                    "size_ratio": ratio(total_numerator, unit),
                    "final_depth": row["final_depth"],
                    "depth_bound": depth_bound,
                }
            )

        if row["H"] in (2 * row["m"] - 5, 2 * row["m"] - 4):
            threshold_rows.append(
                {
                    "r": r,
                    "H": row["H"],
                    "m": row["m"],
                    "selected_mode": row["mode"],
                    "ordinary_ratio": ratio(ordinary["total"] * r, unit),
                    "two_slice_ratio": ratio(sliced["total"] * r, unit),
                }
            )

    require(not crossover_mismatches, "early switch differs from exact smaller ledger")
    require(maximum[2] == 171, "maximum ratio arity")
    return {
        "arity_range": [64, 16384],
        "mode_counts": {str(key): value for key, value in mode_counts.items()},
        "switch": "mode 2 iff H>=2m-4",
        "size_bound": "5*size*r<46*3^r",
        "depth_bound": "r+ceil(7*ceil(log2 r)/5)+12",
        "maximum_ratio": {
            "r": maximum[2],
            "value": ratio(maximum[0], maximum[1]),
        },
        "minimum_depth_slack": {
            "r": minimum_slack[1],
            "value": minimum_slack[0],
        },
        "crossover_mismatches": crossover_mismatches,
        "threshold_rows": threshold_rows,
        "selected": selected,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/early-switch-two-slice/v1",
        "decomposition": decomposition_audit(),
        "analytic_bases": analytic_bases(),
        "ledger": ledger_audit(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    result["provenance"] = {
        "schema": "orbit-synthesis/source-bound-replay/v1",
        "source": (
            "research/tournaments/2026-08-14-early-switch-compiler/"
            "check_early_switch_compiler.py"
        ),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "replay_commands": [
            (
                "python3 research/tournaments/2026-08-14-early-switch-compiler/"
                "check_early_switch_compiler.py --expected "
                "research/tournaments/2026-08-14-early-switch-compiler/receipt.json"
            ),
            (
                "python3 -O research/tournaments/2026-08-14-early-switch-compiler/"
                "check_early_switch_compiler.py --expected "
                "research/tournaments/2026-08-14-early-switch-compiler/receipt.json"
            ),
        ],
        "required_equality": "normal_stdout == optimized_stdout == receipt_bytes",
    }
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

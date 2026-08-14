#!/usr/bin/env python3
"""Standalone audit for the plane-shared local-library fixed-Q compiler."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import sys
from functools import cache
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

Q = (0, 1, 2)
B = (0, 1)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def ceil_log2(value: int) -> int:
    require(value >= 1, "ceil_log2 domain")
    return (value - 1).bit_length()


def floor_power3(value: int) -> tuple[int, int]:
    require(value >= 1, "floor_power3 domain")
    exponent = 0
    power = 1
    while 3 * power <= value:
        power *= 3
        exponent += 1
    return exponent, power


def ratio_decimal(numerator: int, denominator: int, digits: int = 18) -> str:
    whole, remainder = divmod(numerator, denominator)
    tail = []
    for _ in range(digits):
        remainder *= 10
        digit, remainder = divmod(remainder, denominator)
        tail.append(str(digit))
    return f"{whole}." + "".join(tail)


def code_planes(value: int) -> tuple[int, int]:
    require(value in Q, "code domain")
    return ((0, 0), (0, 1), (1, 0))[value]


def decode_planes(high: int, low: int) -> int:
    require(high in B and low in B and (high, low) != (1, 1), "legal code")
    return {(0, 0): 0, (0, 1): 1, (1, 0): 2}[(high, low)]


def plane_factorization_audit() -> dict[str, object]:
    rows = 0
    plane_sets = {}
    for width in range(1, 6):
        domain = list(range(width))
        boolean_tables = set(itertools.product(B, repeat=width))
        observed_planes = set()
        q_tables = 0
        for values in itertools.product(Q, repeat=width):
            high = tuple(code_planes(value)[0] for value in values)
            low = tuple(code_planes(value)[1] for value in values)
            require(high in boolean_tables and low in boolean_tables, "plane outside library")
            reconstructed = tuple(
                decode_planes(high[index], low[index]) for index in domain
            )
            require(reconstructed == values, "plane decode mismatch")
            observed_planes.add(high)
            observed_planes.add(low)
            q_tables += 1
            rows += width
        require(observed_planes == boolean_tables, "Boolean plane library not saturated")
        plane_sets[str(width)] = {
            "q_tables": q_tables,
            "boolean_plane_roots": len(boolean_tables),
            "naive_plane_occurrences": 2 * q_tables,
        }

    high, low = code_planes(2)
    mutation = decode_planes(low, 0)
    require(mutation != 2, "plane mutation ineffective")
    return {
        "rows": rows,
        "widths": plane_sets,
        "mutation_value_2_low_as_high": mutation,
    }


def local_words(width: int) -> list[tuple[int, ...]]:
    return list(itertools.product(Q, repeat=width))


def balanced_partition(items: list[tuple[int, ...]], groups: int) -> list[list[tuple[int, ...]]]:
    require(1 <= groups <= len(items), "partition group count")
    quotient, remainder = divmod(len(items), groups)
    out = []
    cursor = 0
    for index in range(groups):
        size = quotient + (1 if index < remainder else 0)
        out.append(items[cursor : cursor + size])
        cursor += size
    require(cursor == len(items), "partition coverage")
    return out


def selector_reconstruction_audit() -> dict[str, object]:
    """Reconstruct x_sigma(x) from group-specific references to shared planes."""
    local = local_words(2)
    groups = balanced_partition(local, 4)
    group_of = {
        point: index for index, group in enumerate(groups) for point in group
    }
    points = list(itertools.product(Q, repeat=3))
    selectors = [
        ("projection-0", lambda point: 0),
        ("projection-1", lambda point: 1),
        ("projection-2", lambda point: 2),
    ]
    for seed in range(61):
        rng = random.Random(0xB001EA + seed)
        table = {point: rng.randrange(3) for point in points}
        selectors.append((f"seed-{seed}", lambda point, table=table: table[point]))

    rows = 0
    references = 0
    labels = []
    for label, sigma in selectors:
        labels.append(label)
        refs: dict[tuple[int, int], tuple[tuple[int, ...], tuple[int, ...]]] = {}
        for prefix in Q:
            for group_index, group in enumerate(groups):
                high = []
                low = []
                for local_point in group:
                    point = (prefix,) + local_point
                    value = point[sigma(point)]
                    h, l = code_planes(value)
                    high.append(h)
                    low.append(l)
                refs[(prefix, group_index)] = (tuple(high), tuple(low))
                references += 2

        for point in points:
            prefix = point[0]
            local_point = point[1:]
            group_index = group_of[local_point]
            group = groups[group_index]
            row_index = group.index(local_point)
            high, low = refs[(prefix, group_index)]
            got = decode_planes(high[row_index], low[row_index])
            expected = point[sigma(point)]
            require(got == expected, "selector reconstruction mismatch")
            rows += 1

    witness = None
    sigma = lambda point: 2
    for point in points:
        prefix = point[0]
        local_point = point[1:]
        good_group = group_of[local_point]
        bad_group = (good_group + 1) % len(groups)
        bad_local = groups[bad_group][0]
        bad_point = (prefix,) + bad_local
        bad_value = bad_point[sigma(bad_point)]
        expected = point[sigma(point)]
        if bad_value != expected:
            witness = {
                "point": list(point),
                "good_group": good_group,
                "bad_group": bad_group,
                "mutated": bad_value,
                "expected": expected,
            }
            break
    require(witness is not None, "group mutation ineffective")
    return {
        "selectors": len(selectors),
        "rows": rows,
        "plane_references": references,
        "group_sizes": [len(group) for group in groups],
        "labels_sha256": hashlib.sha256("\n".join(labels).encode()).hexdigest(),
        "mutation_wrong_group": witness,
    }


def split_width(width: int) -> tuple[int, int]:
    return (width + 1) // 2, width // 2


@cache
def generic_count(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 4
    left, right = split_width(width)
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
    left, right = split_width(width)
    return (
        generic_count(left)
        + extended_count(right)
        + 2 * 3**width
        - 3 ** (width - 1)
        + 3**left * (3**right - 1) // 2
    )


@cache
def vector_count(width: int) -> int:
    if width == 0:
        return 2
    if width == 1:
        return 5
    left, right = split_width(width)
    return (
        2
        + generic_count(left)
        + extended_count(right)
        + 3**left * (3**right - 1) // 2
        + 3**width
        - (3 ** (width - 1) + 1) // 2
    )


def vector_depth(width: int) -> int:
    return 2 if width == 0 else 3 + ceil_log2(width)


def binary_ledger(arity: int) -> dict[str, int]:
    k = math.isqrt(arity)
    capacity = 3**k
    chunk_width = capacity.bit_length() - 1
    remaining = arity - 1
    residual = remaining % chunk_width
    chunks = ([residual] if residual else []) + [chunk_width] * (
        remaining // chunk_width
    )
    live = 1
    instances = 0
    controls = 0
    for chunk in chunks:
        instances += live
        controls += 6 * capacity * (2**chunk - 1)
        live *= 2**chunk
    require(live == 2 ** (arity - 1), "binary partition")
    return {
        "router": (3 * capacity - 1) // 2 * instances,
        "control": controls,
        "depth": (k + 1) * len(chunks) + 2 * chunk_width + 1,
    }


def boolean_budget(arity: int) -> int:
    quotient = 3**arity // (9 * arity**3)
    require(quotient >= 8, "Boolean budget too small")
    return quotient.bit_length() - 1


def schedule(arity: int) -> dict[str, int]:
    j = boolean_budget(arity)
    cap = j - 3
    b, m = floor_power3(cap)
    require(b >= 2 and m % 9 == 0, "local base")
    local_width = b + 3
    local_capacity = 27 * m
    splitter_width = 5
    splitter_words = 3**splitter_width
    base_rows = m // 9
    max_group_words = cap // base_rows
    require(max_group_words >= 1, "group word capacity")
    groups = (splitter_words + max_group_words - 1) // max_group_words
    quotient, remainder = divmod(splitter_words, groups)
    max_actual_words = quotient + (1 if remainder else 0)
    require(max_actual_words <= max_group_words, "balanced group overflow")
    prefix_width = arity - local_width
    require(prefix_width >= 1, "prefix width")
    return {
        "r": arity,
        "J": j,
        "K": cap,
        "b": b,
        "m": m,
        "t": local_width,
        "N": local_capacity,
        "d": splitter_width,
        "base_rows": base_rows,
        "max_group_words": max_group_words,
        "g": groups,
        "word_quotient": quotient,
        "word_remainder": remainder,
        "s": prefix_width,
        "P": 3**prefix_width,
    }


def exact_row(arity: int) -> dict[str, int]:
    plan = schedule(arity)
    base_rows = plan["base_rows"]
    q = plan["word_quotient"]
    remainder = plan["word_remainder"]
    table_sum = (
        remainder * 2 ** ((q + 1) * base_rows)
        + (plan["g"] - remainder) * 2 ** (q * base_rows)
    )
    local_library = (3 * plan["N"] - 1) // 2 * table_sum
    prefix_routers = plan["g"] * (3 * plan["P"] - 1)
    program_vectors = (
        vector_count(plan["t"])
        + vector_count(plan["s"])
        + vector_count(plan["d"])
        - 4
    )
    group_selector = 3 * 3 ** plan["d"] - 1
    anchor = 2 * arity - 1
    binary = binary_ledger(arity)
    fixed = anchor + 2 + 3 + 1
    total = (
        local_library
        + prefix_routers
        + program_vectors
        + group_selector
        + fixed
        + binary["router"]
        + binary["control"]
    )

    c = ceil_log2(arity)
    anchor_depth = c + 2
    local_depth = (
        anchor_depth + vector_depth(plan["t"]) + plan["t"] + 1
    )
    prefix_depth = max(
        local_depth, anchor_depth + vector_depth(plan["s"])
    ) + plan["s"] + 1
    group_depth = max(
        prefix_depth, anchor_depth + vector_depth(plan["d"])
    ) + plan["d"] + 1
    final_depth = max(
        anchor_depth + 4,
        binary["depth"] + 2,
        group_depth + 4,
    )
    return {
        **plan,
        "table_sum": table_sum,
        "local_library": local_library,
        "prefix_routers": prefix_routers,
        "program_vectors": program_vectors,
        "group_selector": group_selector,
        "anchor": anchor,
        "binary_router": binary["router"],
        "binary_control": binary["control"],
        "total": total,
        "final_depth": final_depth,
        "depth_bound": (
            arity
            + c
            + ceil_log2(c + 2)
            + 17
        ),
    }


def analytic_tail_audit() -> dict[str, object]:
    bases = []
    for arity in (107, 108, 109):
        exponent = math.ceil(4 * arity / 3) + 3
        left = 9 * arity**3 * 2**exponent
        right = 3**arity
        require(left <= right, "K lower-bound base")
        bases.append([arity, exponent, right // left])
    require(
        16 * 110**3 < 27 * 107**3,
        "three-step K induction ratio",
    )

    prefix_table = []
    maximum = (-1, None)
    for h in range(9, 27):
        groups = (243 + h - 1) // h
        numerator = (9 * groups + 4) * (h + 1)
        denominator = 972
        prefix_table.append([h, groups, numerator, denominator])
        if maximum[1] is None or numerator * maximum[3] > maximum[0] * denominator:
            maximum = (numerator, h, groups, denominator)
    require(
        maximum[0] * 243 == 644 * maximum[3],
        "prefix maximum drift",
    )
    require(maximum[1] == 22 and maximum[2] == 12, "prefix argmax")

    tail_upper_numerator = (
        644 * 8 * 107 * 1000
        + 243 * 243 * 1000
        + 4 * 243 * 8 * 107
    )
    tail_upper_denominator = 243 * 8 * 107 * 1000
    require(
        tail_upper_numerator < 3 * tail_upper_denominator,
        "analytic tail below three",
    )

    require(5000 * 65 < 3**32, "prefix half-width error")
    require(149000 * 64**2 < 3**64, "fixed group error")
    require(192 * 2**64 < 3**50, "binary router error")
    require(24 * 64**2 < 3**42, "binary control error")
    return {
        "K_lower_bound": "K>=4r/3 for r>=107",
        "K_base_rows": bases,
        "three_step_ratio": "16*110^3<27*107^3",
        "prefix_discrete_table": prefix_table,
        "prefix_maximum": {
            "h": maximum[1],
            "g": maximum[2],
            "value": "644/243",
        },
        "local_library_bound": "local/U < 243/(8r)",
        "lower_order_bound": "4/1000",
        "tail_upper_fraction": [
            tail_upper_numerator,
            tail_upper_denominator,
        ],
    }


def ledger_audit() -> dict[str, object]:
    maximum = (-1, 1, -1)
    finite_maximum = (-1, 1, -1)
    selected = []
    group_counts: dict[int, int] = {}
    minimum_depth_slack = (10**9, -1)

    for arity in range(64, 16385):
        row = exact_row(arity)
        unit = 3**arity
        numerator = row["total"] * arity
        require(numerator < 3 * unit, "global size below three")
        require(row["final_depth"] <= row["depth_bound"], "depth bound")
        slack = row["depth_bound"] - row["final_depth"]
        if slack < minimum_depth_slack[0]:
            minimum_depth_slack = (slack, arity)

        group_counts[row["g"]] = group_counts.get(row["g"], 0) + 1
        if numerator * maximum[1] > maximum[0] * unit:
            maximum = (numerator, unit, arity)
        if arity <= 106 and numerator * finite_maximum[1] > finite_maximum[0] * unit:
            finite_maximum = (numerator, unit, arity)

        if arity in (
            64, 65, 66, 67, 84, 94, 100, 106, 107, 128,
            256, 500, 1000, 4096, 8192, 16384,
        ):
            selected.append({
                "r": arity,
                "J": row["J"],
                "K": row["K"],
                "t": row["t"],
                "g": row["g"],
                "group_word_sizes": [
                    row["word_quotient"] + (1 if index < row["word_remainder"] else 0)
                    for index in range(row["g"])
                ],
                "live_row_max": (
                    row["word_quotient"]
                    + (1 if row["word_remainder"] else 0)
                ) * row["base_rows"],
                "size_ratio": ratio_decimal(numerator, unit),
                "final_depth": row["final_depth"],
                "depth_bound": row["depth_bound"],
            })

    require(maximum[2] == 66, "maximum ratio arity")
    require(finite_maximum[2] == 66, "finite maximum arity")
    return {
        "arity_range": [64, 16384],
        "size_bound": "size<3*3^r/r",
        "depth_bound": "r+C+ceil(log_2(C+2))+17",
        "maximum_ratio": {
            "r": maximum[2],
            "value": ratio_decimal(maximum[0], maximum[1]),
        },
        "finite_range": {
            "range": [64, 106],
            "maximum_r": finite_maximum[2],
            "maximum_ratio": ratio_decimal(
                finite_maximum[0], finite_maximum[1]
            ),
        },
        "group_count_histogram": {
            str(key): value for key, value in sorted(group_counts.items())
        },
        "minimum_depth_slack": {
            "r": minimum_depth_slack[1],
            "value": minimum_depth_slack[0],
        },
        "selected": selected,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/plane-shared-library/v1",
        "plane_factorization": plane_factorization_audit(),
        "selector_reconstruction": selector_reconstruction_audit(),
        "analytic_tail": analytic_tail_audit(),
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
            raise SystemExit(f"unknown argument: {argument}")

    result = make_receipt()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if expected is not None:
        require(
            result == json.loads(expected.read_text()),
            "committed receipt drift",
        )
    if output is not None:
        output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

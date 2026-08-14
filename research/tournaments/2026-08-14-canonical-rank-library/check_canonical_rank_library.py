#!/usr/bin/env python3
"""Standalone audit for the canonical-rank Boolean-library compiler."""

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


def ceil_log3(value: int) -> int:
    require(value >= 1, "ceil_log3 domain")
    exponent = 0
    power = 1
    while power < value:
        power *= 3
        exponent += 1
    return exponent


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
    require(value in Q, "Q-code domain")
    return ((0, 0), (0, 1), (1, 0))[value]


def decode_planes(high: int, low: int) -> int:
    require((high, low) in ((0, 0), (0, 1), (1, 0)), "legal plane code")
    return {(0, 0): 0, (0, 1): 1, (1, 0): 2}[(high, low)]


def balanced_partition(size: int, groups: int) -> list[range]:
    require(1 <= groups <= size, "balanced partition")
    quotient, remainder = divmod(size, groups)
    result = []
    cursor = 0
    for index in range(groups):
        width = quotient + (1 if index < remainder else 0)
        result.append(range(cursor, cursor + width))
        cursor += width
    require(cursor == size, "partition coverage")
    return result


def base3_digits(value: int, width: int) -> tuple[int, ...]:
    require(0 <= value < 3**width, "base-three range")
    digits = [0] * width
    for index in range(width - 1, -1, -1):
        digits[index] = value % 3
        value //= 3
    return tuple(digits)


def canonical_rank_semantics_audit() -> dict[str, object]:
    local_size = 27
    groups = balanced_partition(local_size, 5)
    group_of: dict[int, int] = {}
    rank_of: dict[int, int] = {}
    for group_index, group in enumerate(groups):
        for rank, item in enumerate(group):
            group_of[item] = group_index
            rank_of[item] = rank

    maximum_rank = max(len(group) for group in groups)
    rank_width = ceil_log3(maximum_rank)
    group_width = ceil_log3(len(groups))
    rank_rows = []
    for item in range(local_size):
        rank_digits = base3_digits(rank_of[item], rank_width)
        group_digits = base3_digits(group_of[item], group_width)
        rank_rows.append([
            item,
            group_of[item],
            rank_of[item],
            list(rank_digits),
            list(group_digits),
        ])

    factor_rows = 0
    distinct_rank_functions = set()
    for group in groups:
        width = len(group)
        for values in itertools.product(B, repeat=width):
            padded = tuple(values) + (0,) * (maximum_rank - width)
            distinct_rank_functions.add(padded)
            for rank, value in enumerate(values):
                require(padded[rank] == value, "rank factorization")
                factor_rows += 1
    require(
        len(distinct_rank_functions) <= 2**maximum_rank,
        "rank library cardinality",
    )

    q_rows = 0
    for group in groups:
        width = len(group)
        for values in itertools.product(Q, repeat=width):
            high = tuple(code_planes(value)[0] for value in values)
            low = tuple(code_planes(value)[1] for value in values)
            high_root = high + (0,) * (maximum_rank - width)
            low_root = low + (0,) * (maximum_rank - width)
            for rank, expected in enumerate(values):
                got = decode_planes(high_root[rank], low_root[rank])
                require(got == expected, "Q rank-pair reconstruction")
                q_rows += 1

    mutation = None
    for item in range(local_size):
        group = groups[group_of[item]]
        if len(group) > 1:
            bad_rank = (rank_of[item] + 1) % len(group)
            if bad_rank != rank_of[item]:
                mutation = {
                    "item": item,
                    "group": group_of[item],
                    "rank": rank_of[item],
                    "mutated_rank": bad_rank,
                }
                break
    require(mutation is not None, "rank mutation ineffective")
    return {
        "local_size": local_size,
        "group_sizes": [len(group) for group in groups],
        "maximum_rank": maximum_rank,
        "rank_width": rank_width,
        "group_width": group_width,
        "rank_rows": rank_rows,
        "boolean_factor_rows": factor_rows,
        "q_pair_rows": q_rows,
        "distinct_padded_rank_functions": len(distinct_rank_functions),
        "universal_rank_capacity": 2**maximum_rank,
        "mutation_rank_shift": mutation,
    }


def selector_reconstruction_audit() -> dict[str, object]:
    local_words = list(itertools.product(Q, repeat=2))
    groups = balanced_partition(len(local_words), 4)
    group_of = {}
    rank_of = {}
    for group_index, group in enumerate(groups):
        for rank, item_index in enumerate(group):
            group_of[item_index] = group_index
            rank_of[item_index] = rank
    maximum_rank = max(len(group) for group in groups)

    points = list(itertools.product(Q, repeat=3))
    selectors = [
        ("projection-0", lambda point: 0),
        ("projection-1", lambda point: 1),
        ("projection-2", lambda point: 2),
    ]
    for seed in range(61):
        rng = random.Random(0xCA110A + seed)
        table = {point: rng.randrange(3) for point in points}
        selectors.append((f"seed-{seed}", lambda point, table=table: table[point]))

    rows = 0
    references = 0
    labels = []
    for label, sigma in selectors:
        labels.append(label)
        rank_roots: set[tuple[int, ...]] = set()
        prefix_refs = {}
        for prefix in Q:
            for group_index, group in enumerate(groups):
                high = [0] * maximum_rank
                low = [0] * maximum_rank
                for rank, item_index in enumerate(group):
                    local = local_words[item_index]
                    point = (prefix,) + local
                    value = point[sigma(point)]
                    high[rank], low[rank] = code_planes(value)
                high_root = tuple(high)
                low_root = tuple(low)
                rank_roots.add(high_root)
                rank_roots.add(low_root)
                prefix_refs[(prefix, group_index)] = (high_root, low_root)
                references += 2

        for point in points:
            prefix = point[0]
            item_index = local_words.index(point[1:])
            group_index = group_of[item_index]
            rank = rank_of[item_index]
            high_root, low_root = prefix_refs[(prefix, group_index)]
            got = decode_planes(high_root[rank], low_root[rank])
            expected = point[sigma(point)]
            require(got == expected, "selector rank reconstruction")
            rows += 1

        require(
            len(rank_roots) <= 2**maximum_rank,
            "selector roots exceed universal rank library",
        )

    mutation = None
    sigma = lambda point: 1
    for point in points:
        item_index = local_words.index(point[1:])
        good_group = group_of[item_index]
        bad_group = (good_group + 1) % len(groups)
        bad_item_index = next(iter(groups[bad_group]))
        bad_point = (point[0],) + local_words[bad_item_index]
        bad = bad_point[sigma(bad_point)]
        expected = point[sigma(point)]
        if bad != expected:
            mutation = {
                "point": list(point),
                "good_group": good_group,
                "bad_group": bad_group,
                "mutated": bad,
                "expected": expected,
            }
            break
    require(mutation is not None, "group mutation ineffective")
    return {
        "selectors": len(selectors),
        "rows": rows,
        "plane_references": references,
        "maximum_rank": maximum_rank,
        "labels_sha256": hashlib.sha256("\n".join(labels).encode()).hexdigest(),
        "mutation_group_shift": mutation,
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
    quotient = 3**arity // (9 * arity**2)
    require(quotient >= 8, "Boolean budget")
    return quotient.bit_length() - 1


def schedule(arity: int) -> dict[str, int]:
    j = boolean_budget(arity)
    k = j - 3
    b, m = floor_power3(k)
    local_width = b + 5
    splitter_width = min(9, local_width)
    base_rows = 3 ** (local_width - splitter_width)
    group_cap = k // base_rows
    require(group_cap >= 1, "group cap")
    splitter_words = 3**splitter_width
    groups = (splitter_words + group_cap - 1) // group_cap
    quotient, remainder = divmod(splitter_words, groups)
    maximum_rows = (quotient + (1 if remainder else 0)) * base_rows
    require(maximum_rows <= k, "group rows exceed K")
    rank_width = ceil_log3(maximum_rows)
    rank_capacity = 3**rank_width
    group_width = ceil_log3(groups)
    group_capacity = 3**group_width
    prefix_width = arity - local_width
    require(prefix_width >= 1, "prefix width")
    return {
        "r": arity,
        "J": j,
        "K": k,
        "b": b,
        "m": m,
        "t": local_width,
        "d": splitter_width,
        "u": base_rows,
        "h": group_cap,
        "g": groups,
        "word_quotient": quotient,
        "word_remainder": remainder,
        "M": maximum_rows,
        "w": rank_width,
        "R": rank_capacity,
        "e": group_width,
        "G": group_capacity,
        "N": 3**local_width,
        "s": prefix_width,
        "P": 3**prefix_width,
    }


def exact_row(arity: int) -> dict[str, int]:
    plan = schedule(arity)
    map_nodes = (plan["w"] + plan["e"]) * (3 * plan["N"] + 1)
    rank_library = ((3 * plan["R"] - 1) // 2) * 2 ** plan["M"]
    prefix_routers = plan["g"] * (3 * plan["P"] - 1)
    program_vectors = (
        vector_count(plan["t"])
        + vector_count(plan["w"])
        + vector_count(plan["s"])
        + vector_count(plan["e"])
        - 6
    )
    group_selector = 3 * plan["G"] - 1
    binary = binary_ledger(arity)
    total = (
        map_nodes
        + rank_library
        + prefix_routers
        + program_vectors
        + group_selector
        + (2 * arity - 1)
        + 2
        + 3
        + 1
        + binary["router"]
        + binary["control"]
    )

    c = ceil_log2(arity)
    anchor_depth = c + 2
    map_depth = anchor_depth + vector_depth(plan["t"]) + plan["t"] + 3
    rank_library_depth = map_depth + vector_depth(plan["w"]) + plan["w"] + 1
    prefix_depth = max(
        rank_library_depth,
        anchor_depth + vector_depth(plan["s"]),
    ) + plan["s"] + 1
    group_depth = max(
        prefix_depth,
        map_depth + vector_depth(plan["e"]),
    ) + plan["e"] + 1
    final_depth = max(
        anchor_depth + 4,
        binary["depth"] + 2,
        group_depth + 4,
    )

    clean_depth = (
        arity
        + c
        + math.ceil(2 * (c + 1) / 3)
        + 2 * ceil_log2(c + 4)
        + 23
    )
    return {
        **plan,
        "map_nodes": map_nodes,
        "rank_library": rank_library,
        "prefix_routers": prefix_routers,
        "program_vectors": program_vectors,
        "group_selector": group_selector,
        "binary_router": binary["router"],
        "binary_control": binary["control"],
        "total": total,
        "final_depth": final_depth,
        "depth_bound": clean_depth,
    }


def analytic_tail_audit() -> dict[str, object]:
    bases = []
    for arity in (268, 269):
        exponent = math.ceil(3 * arity / 2) + 3
        left = 9 * arity**2 * 2**exponent
        right = 3**arity
        require(left <= right, "K lower-bound base")
        bases.append([arity, exponent, right // left])
    require(4 * 270**2 < 9 * 268**2, "K two-step ratio")

    prefix_table = []
    maximum = (-1, None, None, None)
    for h in range(81, 243):
        groups = (19683 + h - 1) // h
        numerator = 2 * (9 * groups + 4) * (h + 1)
        denominator = 177147
        prefix_table.append([h, groups, numerator, denominator])
        if (
            maximum[1] is None
            or numerator * maximum[3] > maximum[0] * denominator
        ):
            maximum = (numerator, h, groups, denominator)
    require(
        maximum[0] == 361982
        and maximum[1] == 240
        and maximum[2] == 83
        and maximum[3] == 177147,
        "prefix maximum",
    )

    tail = (
        361982 * 8 * 1000
        + 177147 * 1000
        + 5 * 177147 * 8
    )
    denominator = 177147 * 8 * 1000
    require(5 * tail < 12 * denominator, "tail below 12/5")

    require(
        1459000 * 268**2 * (ceil_log2(268) + 5) < 3**268,
        "map thousandth base",
    )
    require(1155000 * 268**2 < 3**268, "fixed thousandth base")
    require(5000 * 65 < 3**32, "prefix error base")
    require(192 * 2**64 < 3**50, "binary router base")
    require(24 * 64**2 < 3**42, "binary control base")
    return {
        "tail_start": 268,
        "K_bound": "K>=3r/2",
        "K_bases": bases,
        "K_two_step": "4*270^2<9*268^2",
        "prefix_table": prefix_table,
        "prefix_maximum": {
            "h": maximum[1],
            "g": maximum[2],
            "value": "361982/177147",
        },
        "rank_library_bound": "1/8",
        "lower_order_bound": "5/1000",
        "tail_fraction": [tail, denominator],
        "target": "12/5",
    }


def ledger_audit() -> dict[str, object]:
    maximum = (-1, 1, -1)
    finite_maximum = (-1, 1, -1)
    selected = []
    minimum_slack = (10**9, -1)
    group_histogram: dict[int, int] = {}

    for arity in range(64, 16385):
        row = exact_row(arity)
        unit = 3**arity
        numerator = row["total"] * arity
        require(5 * numerator < 12 * unit, "size below 12/5")
        require(row["final_depth"] <= row["depth_bound"], "depth")
        slack = row["depth_bound"] - row["final_depth"]
        if slack < minimum_slack[0]:
            minimum_slack = (slack, arity)

        group_histogram[row["g"]] = group_histogram.get(row["g"], 0) + 1
        if numerator * maximum[1] > maximum[0] * unit:
            maximum = (numerator, unit, arity)
        if (
            arity <= 267
            and numerator * finite_maximum[1]
            > finite_maximum[0] * unit
        ):
            finite_maximum = (numerator, unit, arity)

        if arity in (
            64, 65, 66, 67, 100, 267, 268, 500,
            1000, 4096, 8192, 16384,
        ):
            selected.append({
                "r": arity,
                "J": row["J"],
                "K": row["K"],
                "t": row["t"],
                "g": row["g"],
                "M": row["M"],
                "w": row["w"],
                "e": row["e"],
                "size_ratio": ratio_decimal(numerator, unit),
                "final_depth": row["final_depth"],
                "depth_bound": row["depth_bound"],
            })

    require(maximum[2] == 64, "maximum arity")
    require(finite_maximum[2] == 64, "finite maximum")
    return {
        "arity_range": [64, 16384],
        "size_bound": "5*size*r<12*3^r",
        "depth_bound": (
            "r+C+ceil(2(C+1)/3)+2ceil(log_2(C+4))+23"
        ),
        "maximum": {
            "r": maximum[2],
            "ratio": ratio_decimal(maximum[0], maximum[1]),
        },
        "finite_proof": {
            "range": [64, 267],
            "maximum_r": finite_maximum[2],
            "maximum_ratio": ratio_decimal(
                finite_maximum[0], finite_maximum[1]
            ),
        },
        "minimum_depth_slack": {
            "r": minimum_slack[1],
            "value": minimum_slack[0],
        },
        "group_count_histogram": {
            str(key): value
            for key, value in sorted(group_histogram.items())
        },
        "selected": selected,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/canonical-rank-library/v1",
        "canonical_rank_semantics": canonical_rank_semantics_audit(),
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

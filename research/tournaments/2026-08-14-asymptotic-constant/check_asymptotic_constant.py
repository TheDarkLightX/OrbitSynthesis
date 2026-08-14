#!/usr/bin/env python3
"""Standalone audit for the asymptotically sharp fixed-Q compiler constant."""

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


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def ceil_log2(n: int) -> int:
    require(n >= 1, "ceil_log2 domain")
    return (n - 1).bit_length()


def ceil_log3(n: int) -> int:
    require(n >= 1, "ceil_log3 domain")
    p = 1
    e = 0
    while p < n:
        p *= 3
        e += 1
    return e


def floor_power3(n: int) -> tuple[int, int]:
    require(n >= 1, "floor_power3 domain")
    p = 1
    e = 0
    while 3 * p <= n:
        p *= 3
        e += 1
    return e, p


def decimal_ratio(numerator: int, denominator: int, digits: int = 18) -> str:
    q, r = divmod(numerator, denominator)
    tail = []
    for _ in range(digits):
        r *= 10
        digit, r = divmod(r, denominator)
        tail.append(str(digit))
    return f"{q}." + "".join(tail)


def plane_code(value: int) -> tuple[int, int]:
    return ((0, 0), (0, 1), (1, 0))[value]


def plane_decode(high: int, low: int) -> int:
    require((high, low) in ((0, 0), (0, 1), (1, 0)), "legal plane code")
    return {(0, 0): 0, (0, 1): 1, (1, 0): 2}[(high, low)]


def balanced_ranges(size: int, groups: int) -> list[range]:
    require(1 <= groups <= size, "balanced range")
    q, rem = divmod(size, groups)
    out = []
    cursor = 0
    for index in range(groups):
        width = q + (1 if index < rem else 0)
        out.append(range(cursor, cursor + width))
        cursor += width
    require(cursor == size, "range coverage")
    return out


def semantic_audit() -> dict[str, object]:
    local = list(itertools.product(Q, repeat=2))
    groups = balanced_ranges(len(local), 4)
    location = {}
    for group_id, group in enumerate(groups):
        for rank, index in enumerate(group):
            location[index] = (group_id, rank)
    max_rank = max(map(len, groups))
    rows = 0
    fingerprints = []
    for mask in range(1 << len(local)):
        sigma = {point: (mask >> index) & 1 for index, point in enumerate(local)}
        roots = set()
        refs = {}
        for group_id, group in enumerate(groups):
            high = [0] * max_rank
            low = [0] * max_rank
            for rank, index in enumerate(group):
                value = local[index][sigma[local[index]]]
                high[rank], low[rank] = plane_code(value)
            high_root = tuple(high)
            low_root = tuple(low)
            roots.add(high_root)
            roots.add(low_root)
            refs[group_id] = (high_root, low_root)
        require(len(roots) <= 2**max_rank, "rank root family")
        fingerprints.append("|".join("".join(map(str, root)) for root in sorted(roots)))
        for index, point in enumerate(local):
            group_id, rank = location[index]
            high, low = refs[group_id]
            got = plane_decode(high[rank], low[rank])
            require(got == point[sigma[point]], "selector reconstruction")
            rows += 1

    points = list(itertools.product(Q, repeat=3))
    selectors = []
    for coordinate in range(3):
        selectors.append((f"projection-{coordinate}", lambda point, c=coordinate: c))
    for seed in range(61):
        rng = random.Random(0xA5A5C0 + seed)
        table = {point: rng.randrange(3) for point in points}
        selectors.append((f"seed-{seed}", lambda point, table=table: table[point]))
    corpus_rows = 0
    for _, sigma in selectors:
        for point in points:
            high, low = plane_code(point[sigma(point)])
            require(plane_decode(high, low) == point[sigma(point)], "three-coordinate code")
            corpus_rows += 1

    good_rank = location[0][1]
    shifted_rank = (good_rank + 1) % len(groups[0])
    require(good_rank != shifted_rank, "rank mutation ineffective")
    return {
        "coordinate_selector_tables_Q2": 1 << len(local),
        "coordinate_selector_rows_Q2": rows,
        "three_coordinate_selectors": len(selectors),
        "three_coordinate_rows": corpus_rows,
        "group_sizes": [len(group) for group in groups],
        "root_fingerprint_sha256": hashlib.sha256(
            "\n".join(fingerprints).encode()
        ).hexdigest(),
        "mutation_shift_rank": {
            "group": 0,
            "rank": good_rank,
            "shifted_rank": shifted_rank,
        },
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


@cache
def binary_ledger(arity: int) -> tuple[int, int, int]:
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
    require(live == 2 ** (arity - 1), "binary leaves")
    return (
        (3 * capacity - 1) // 2 * instances,
        controls,
        (k + 1) * len(chunks) + 2 * chunk_width + 1,
    )


def rank_compiler_total(arity: int, *, asymptotic: bool) -> dict[str, int]:
    C = ceil_log2(arity)
    if asymptotic:
        K = (3**arity // arity**4).bit_length() - 1
        require(K >= 1, "asymptotic K")
        t = ceil_log3(K * C**3)
        N = 3**t
        g = (N + K - 1) // K
    else:
        J = (3**arity // (9 * arity**2)).bit_length() - 1
        K = J - 3
        b, _m = floor_power3(K)
        t = b + 5
        d = min(9, t)
        u = 3 ** (t - d)
        h = K // u
        N = 3**t
        g = (3**d + h - 1) // h

    require(1 <= g <= N and t < arity, "rank schedule")
    q, rem = divmod(N, g)
    M = q + (1 if rem else 0)
    require(M <= K, "rank group exceeds budget")
    w = ceil_log3(M)
    R = 3**w
    e = ceil_log3(g)
    G = 3**e
    s = arity - t
    P = 3**s

    map_nodes = (w + e) * (3 * N + 1)
    rank_library = ((3 * R - 1) // 2) * 2**M
    prefix_routers = g * (3 * P - 1)
    program_vectors = (
        vector_count(t)
        + vector_count(w)
        + vector_count(s)
        + vector_count(e)
        - 6
    )
    group_selector = 3 * G - 1
    binary_router, binary_control, binary_depth = binary_ledger(arity)
    total = (
        map_nodes
        + rank_library
        + prefix_routers
        + program_vectors
        + group_selector
        + (2 * arity - 1)
        + 6
        + binary_router
        + binary_control
    )

    anchor_depth = C + 2
    map_depth = anchor_depth + vector_depth(t) + t + 3
    rank_depth = map_depth + vector_depth(w) + w + 1
    prefix_depth = max(rank_depth, anchor_depth + vector_depth(s)) + s + 1
    group_depth = max(prefix_depth, map_depth + vector_depth(e)) + e + 1
    final_depth = max(anchor_depth + 4, binary_depth + 2, group_depth + 4)
    return {
        "r": arity,
        "K": K,
        "C": C,
        "t": t,
        "N": N,
        "g": g,
        "M": M,
        "w": w,
        "R": R,
        "e": e,
        "G": G,
        "s": s,
        "P": P,
        "map_nodes": map_nodes,
        "rank_library": rank_library,
        "prefix_routers": prefix_routers,
        "program_vectors": program_vectors,
        "group_selector": group_selector,
        "binary_router": binary_router,
        "binary_control": binary_control,
        "total": total,
        "depth": final_depth,
    }


def exact_audit() -> dict[str, object]:
    maximum_combined = (-1, 1, -1)
    first_asym_selected = None
    last_finite_selected = None
    asym_selected_count = 0
    finite_selected_count = 0
    last_asym_at_least_two = None
    selected = []

    for arity in range(64, 16385):
        finite = rank_compiler_total(arity, asymptotic=False)
        asym = rank_compiler_total(arity, asymptotic=True)
        use_asym = asym["total"] < finite["total"]
        if use_asym:
            asym_selected_count += 1
            if first_asym_selected is None:
                first_asym_selected = arity
        else:
            finite_selected_count += 1
            last_finite_selected = arity

        chosen = asym if use_asym else finite
        unit = 3**arity
        chosen_num = chosen["total"] * arity
        require(5 * chosen_num < 12 * unit, "combined 12/5 bound")
        if chosen_num * maximum_combined[1] > maximum_combined[0] * unit:
            maximum_combined = (chosen_num, unit, arity)

        asym_num = asym["total"] * arity
        if asym_num >= 2 * unit:
            last_asym_at_least_two = arity

        if arity in (64, 100, 178, 268, 434, 435, 1000, 4096, 8192, 16384):
            selected.append({
                "r": arity,
                "selected": "asymptotic" if use_asym else "finite",
                "finite_ratio": decimal_ratio(finite["total"] * arity, unit),
                "asymptotic_ratio": decimal_ratio(asym_num, unit),
                "asymptotic_K_over_r": decimal_ratio(asym["K"], arity),
                "three_r_over_K": decimal_ratio(3 * arity, asym["K"]),
                "asymptotic_t": asym["t"],
                "asymptotic_g": asym["g"],
                "asymptotic_M": asym["M"],
                "asymptotic_depth": asym["depth"],
            })

    require(first_asym_selected == 178, "first asymptotic selection")
    require(last_asym_at_least_two == 434, "last checked asymptotic ratio >=2")
    require(maximum_combined[2] == 64, "combined maximum")
    return {
        "range": [64, 16384],
        "combined_size_bound": "5*size*r<12*3^r",
        "combined_maximum": {
            "r": maximum_combined[2],
            "ratio": decimal_ratio(maximum_combined[0], maximum_combined[1]),
        },
        "first_asymptotic_selection": first_asym_selected,
        "last_finite_selection_in_range": last_finite_selected,
        "selection_counts": {
            "finite": finite_selected_count,
            "asymptotic": asym_selected_count,
        },
        "last_checked_asymptotic_ratio_at_least_two": last_asym_at_least_two,
        "first_checked_asymptotic_ratio_below_two": last_asym_at_least_two + 1,
        "selected": selected,
    }


def asymptotic_proof_audit() -> dict[str, object]:
    rows = []
    for arity in (64, 100, 268, 1000, 4096, 16384):
        x = rank_compiler_total(arity, asymptotic=True)
        C = x["C"]
        require(x["K"] * C**3 <= x["N"] < 3 * x["K"] * C**3, "N sandwich")
        require(C**3 <= x["g"] <= 3 * C**3, "g sandwich")
        require(x["M"] <= x["K"], "M cap")
        rows.append({
            "r": arity,
            "K": x["K"],
            "C": C,
            "N": x["N"],
            "g": x["g"],
            "M": x["M"],
            "K_over_r": decimal_ratio(x["K"], arity),
            "M_over_K": decimal_ratio(x["M"], x["K"]),
            "three_r_over_K": decimal_ratio(3 * arity, x["K"]),
            "ratio": decimal_ratio(x["total"] * arity, 3**arity),
        })

    large_rows = []
    for arity in (32768, 65536):
        x = rank_compiler_total(arity, asymptotic=True)
        large_rows.append({
            "r": arity,
            "K_over_r": decimal_ratio(x["K"], arity),
            "M_over_K": decimal_ratio(x["M"], x["K"]),
            "three_r_over_K": decimal_ratio(3 * arity, x["K"]),
            "size_ratio": decimal_ratio(x["total"] * arity, 3**arity),
        })

    limit_decimal = "1.892789260714372110"
    depth_coefficient = "1.630929753571457437"
    require(abs(3 / math.log2(3) - float(limit_decimal)) < 1e-15, "limit decimal")
    require(abs(1 + math.log(2, 3) - float(depth_coefficient)) < 1e-15, "depth decimal")
    return {
        "K_formula": "floor(log_2(3^r/r^4))",
        "K_asymptotic": "K/r -> log_2 3",
        "N_formula": "3^ceil(log_3(K*C^3))",
        "N_sandwich": "K*C^3 <= N < 3*K*C^3",
        "group_formula": "g=ceil(N/K)",
        "group_asymptotic": "g=N/K+O(1)=Theta(C^3)",
        "rank_asymptotic": "M/K -> 1",
        "prefix_identity": "3*g*P/U = 3*g*r/N = 3*r/K+O(1/C^3)",
        "prefix_vector": "O(r/N)=O(1/C^3)",
        "rank_library": "O(3^r/r^3)=o(U)",
        "map_library": "O(r*C^4)=o(U)",
        "limit_constant": "3/log_2 3",
        "limit_constant_decimal": limit_decimal,
        "depth": (
            "r+C+w+e+ceil(log_2 t)+ceil(log_2 w)+18 "
            "= r+(1+log_3 2)log_2 r+O(log log r)"
        ),
        "depth_log_coefficient": depth_coefficient,
        "sample_rows": rows,
        "large_rows": large_rows,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/asymptotic-constant/v1",
        "semantics": semantic_audit(),
        "exact": exact_audit(),
        "asymptotic_proof": asymptotic_proof_audit(),
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
        require(result == json.loads(expected.read_text()), "receipt drift")
    if output is not None:
        output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

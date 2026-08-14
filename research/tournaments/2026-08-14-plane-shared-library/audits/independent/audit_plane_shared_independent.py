#!/usr/bin/env python3
"""Independent no-import reconstruction of the plane-shared compiler ledger."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def ceiling_log_two(n: int) -> int:
    return (n - 1).bit_length()


def lower_power_three(n: int) -> tuple[int, int]:
    p = 1
    e = 0
    while 3 * p <= n:
        p *= 3
        e += 1
    return e, p


def decimal(n: int, d: int, digits: int = 18) -> str:
    q, r = divmod(n, d)
    out = []
    for _ in range(digits):
        r *= 10
        x, r = divmod(r, d)
        out.append(str(x))
    return str(q) + "." + "".join(out)


@lru_cache(maxsize=None)
def rail_census(w: int) -> tuple[int, int, int]:
    if w == 0:
        return 0, 0, 2
    if w == 1:
        return 4, 4, 5
    a = (w + 1) // 2
    b = w // 2
    ra, _, _ = rail_census(a)
    rb, eb, _ = rail_census(b)
    cross = 3**a * (3**b - 1) // 2
    regular = ra + rb + 3**w + cross
    extended = ra + eb + 2 * 3**w - 3 ** (w - 1) + cross
    vector = (
        2 + ra + eb + cross + 3**w - (3 ** (w - 1) + 1) // 2
    )
    return regular, extended, vector


def vector_nodes(w: int) -> int:
    return rail_census(w)[2]


def vector_height(w: int) -> int:
    return 2 if w == 0 else 3 + ceiling_log_two(w)


def relative_binary_cost(r: int) -> tuple[int, int, int]:
    k = math.isqrt(r)
    q = 3**k
    width = q.bit_length() - 1
    remaining = r - 1
    sizes = []
    if remaining % width:
        sizes.append(remaining % width)
    sizes += [width] * (remaining // width)
    population = 1
    routers = 0
    controls = 0
    for size in sizes:
        routers += population
        controls += 6 * q * (2**size - 1)
        population *= 2**size
    assert_true(population == 2 ** (r - 1), "binary population")
    return (
        routers * ((3 * q - 1) // 2),
        controls,
        (k + 1) * len(sizes) + 2 * width + 1,
    )


def budget(r: int) -> int:
    return (3**r // (9 * r**3)).bit_length() - 1


def parameters(r: int) -> dict[str, int]:
    j = budget(r)
    k = j - 3
    b, m = lower_power_three(k)
    t = b + 3
    n = 3**t
    unit = m // 9
    word_cap = k // unit
    group_count = (243 + word_cap - 1) // word_cap
    small, large_count = divmod(243, group_count)
    assert_true(small + (1 if large_count else 0) <= word_cap, "group cap")
    return {
        "J": j,
        "K": k,
        "b": b,
        "m": m,
        "t": t,
        "N": n,
        "unit": unit,
        "word_cap": word_cap,
        "g": group_count,
        "small_words": small,
        "large_count": large_count,
        "s": r - t,
    }


def charge(r: int) -> tuple[int, int, dict[str, int]]:
    p = parameters(r)
    table_roots = (
        p["large_count"] * 2 ** ((p["small_words"] + 1) * p["unit"])
        + (p["g"] - p["large_count"])
        * 2 ** (p["small_words"] * p["unit"])
    )
    local = ((3 * p["N"] - 1) // 2) * table_roots
    prefix_capacity = 3 ** p["s"]
    prefix = p["g"] * (3 * prefix_capacity - 1)
    vectors = vector_nodes(p["t"]) + vector_nodes(p["s"]) + vector_nodes(5) - 4
    group_mux = 728
    anchor_and_fixed = (2 * r - 1) + 6
    br, bc, bd = relative_binary_cost(r)
    total = local + prefix + vectors + group_mux + anchor_and_fixed + br + bc

    c = ceiling_log_two(r)
    anchor_depth = c + 2
    local_depth = anchor_depth + vector_height(p["t"]) + p["t"] + 1
    prefix_depth = max(
        local_depth, anchor_depth + vector_height(p["s"])
    ) + p["s"] + 1
    mux_depth = max(
        prefix_depth, anchor_depth + vector_height(5)
    ) + 6
    depth = max(anchor_depth + 4, bd + 2, mux_depth + 4)
    return total, depth, p


def semantic_plane_audit() -> dict[str, object]:
    checked = 0
    union_sizes = {}
    for h in range(0, 7):
        booleans = set(itertools.product((0, 1), repeat=h))
        seen = set()
        for table in itertools.product((0, 1, 2), repeat=h):
            hi = tuple(value == 2 for value in table)
            lo = tuple(value == 1 for value in table)
            rebuilt = tuple(
                2 if hi[i] else (1 if lo[i] else 0) for i in range(h)
            )
            assert_true(rebuilt == table, "plane rebuilding")
            seen.add(tuple(map(int, hi)))
            seen.add(tuple(map(int, lo)))
            checked += h
        assert_true(seen == booleans, "plane saturation")
        union_sizes[str(h)] = len(seen)

    mutation = tuple(
        2 if low else (1 if low else 0)
        for low in (0, 1)
    )
    assert_true(mutation != (0, 1), "plane mutation")
    return {
        "rows": checked,
        "boolean_root_counts": union_sizes,
        "mutation_low_used_as_both_planes": list(mutation),
    }


def arithmetic_audit() -> dict[str, object]:
    maximum = (-1, 1, -1)
    finite_maximum = (-1, 1, -1)
    selected = []
    tail_k_min = (10**9, -1)
    for r in range(64, 16385):
        total, depth, p = charge(r)
        universe = 3**r
        numerator = total * r
        assert_true(numerator < 3 * universe, "size theorem")
        c = ceiling_log_two(r)
        depth_bound = r + c + ceiling_log_two(c + 2) + 17
        assert_true(depth <= depth_bound, "depth theorem")
        if numerator * maximum[1] > maximum[0] * universe:
            maximum = (numerator, universe, r)
        if r <= 106 and numerator * finite_maximum[1] > finite_maximum[0] * universe:
            finite_maximum = (numerator, universe, r)
        if r >= 107:
            assert_true(3 * p["K"] >= 4 * r, "tail K/r")
            margin = 3 * p["K"] - 4 * r
            if margin < tail_k_min[0]:
                tail_k_min = (margin, r)
        if r in (64, 66, 67, 100, 106, 107, 500, 1000, 8192, 16384):
            selected.append({
                "r": r,
                "J": p["J"],
                "K": p["K"],
                "t": p["t"],
                "g": p["g"],
                "size_ratio": decimal(numerator, universe),
                "depth": depth,
                "depth_bound": depth_bound,
            })

    assert_true(maximum[2] == 66, "maximum location")
    assert_true(finite_maximum[2] == 66, "finite maximum location")

    prefix = []
    max_pair = (-1, 1, -1, -1)
    for h in range(9, 27):
        g = (243 + h - 1) // h
        numerator = (9 * g + 4) * (h + 1)
        denominator = 972
        prefix.append([h, g, numerator, denominator])
        if numerator * max_pair[1] > max_pair[0] * denominator:
            max_pair = (numerator, denominator, h, g)
    assert_true(max_pair[2:] == (22, 12), "prefix maximum location")
    assert_true(max_pair[0] * 243 == 644 * max_pair[1], "prefix value")

    return {
        "range": [64, 16384],
        "maximum": {
            "r": maximum[2],
            "ratio": decimal(maximum[0], maximum[1]),
        },
        "finite_64_106": {
            "maximum_r": finite_maximum[2],
            "maximum_ratio": decimal(
                finite_maximum[0], finite_maximum[1]
            ),
        },
        "tail_K_margin": {
            "minimum": tail_k_min[0],
            "r": tail_k_min[1],
        },
        "prefix_table": prefix,
        "prefix_maximum": "644/243",
        "selected": selected,
        "theorem": {
            "size": "size<3*3^r/r",
            "depth": "r+C+ceil(log_2(C+2))+17",
        },
    }


def base_inequalities() -> dict[str, object]:
    rows = []
    for r in (107, 108, 109):
        exponent = math.ceil(4 * r / 3) + 3
        assert_true(9 * r**3 * 2**exponent <= 3**r, "K base")
        rows.append([r, exponent])
    assert_true(16 * 110**3 < 27 * 107**3, "K induction")
    assert_true(5000 * 65 < 3**32, "prefix error")
    assert_true(149000 * 64**2 < 3**64, "fixed error")
    assert_true(192 * 2**64 < 3**50, "binary router")
    assert_true(24 * 64**2 < 3**42, "binary controls")
    return {
        "K_bases": rows,
        "K_three_step": "16*110^3<27*107^3",
        "lower_order_bases": [
            "5000*65<3^32",
            "149000*64^2<3^64",
            "192*2^64<3^50",
            "24*64^2<3^42",
        ],
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/plane-shared-independent/v1",
        "planes": semantic_plane_audit(),
        "bases": base_inequalities(),
        "arithmetic": arithmetic_audit(),
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
            raise SystemExit(arg)

    result = make_receipt()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if expected is not None:
        assert_true(
            result == json.loads(expected.read_text()),
            "receipt mismatch",
        )
    if output is not None:
        output.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

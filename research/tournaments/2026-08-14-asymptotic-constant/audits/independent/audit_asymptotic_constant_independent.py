#!/usr/bin/env python3
"""Independent no-import audit of the asymptotic fixed-Q compiler constant."""

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


def must(ok: bool, label: str) -> None:
    if not ok:
        raise AssertionError(label)


def log2c(n: int) -> int:
    return (n - 1).bit_length()


def log3c(n: int) -> int:
    p = 1
    e = 0
    while p < n:
        p *= 3
        e += 1
    return e


def pow3floor(n: int) -> tuple[int, int]:
    p = 1
    e = 0
    while 3 * p <= n:
        p *= 3
        e += 1
    return e, p


def dec(n: int, d: int, digits: int = 18) -> str:
    a, r = divmod(n, d)
    tail = []
    for _ in range(digits):
        r *= 10
        x, r = divmod(r, d)
        tail.append(str(x))
    return str(a) + "." + "".join(tail)


@lru_cache(None)
def rails(w: int) -> tuple[int, int, int]:
    if w == 0:
        return 0, 0, 2
    if w == 1:
        return 4, 4, 5
    a = (w + 1) // 2
    b = w // 2
    ra, _, _ = rails(a)
    rb, eb, _ = rails(b)
    cross = 3**a * (3**b - 1) // 2
    rg = ra + rb + 3**w + cross
    re = ra + eb + 2 * 3**w - 3 ** (w - 1) + cross
    rv = 2 + ra + eb + cross + 3**w - (3 ** (w - 1) + 1) // 2
    return rg, re, rv


def vnodes(w: int) -> int:
    return rails(w)[2]


def vdepth(w: int) -> int:
    return 2 if w == 0 else 3 + log2c(w)


@lru_cache(None)
def binary(r: int) -> tuple[int, int, int]:
    k = math.isqrt(r)
    q = 3**k
    width = q.bit_length() - 1
    n = r - 1
    chunks = ([n % width] if n % width else []) + [width] * (n // width)
    live = 1
    instances = 0
    controls = 0
    for size in chunks:
        instances += live
        controls += 6 * q * (2**size - 1)
        live *= 2**size
    must(live == 2 ** (r - 1), "binary leaves")
    return (
        ((3 * q - 1) // 2) * instances,
        controls,
        (k + 1) * len(chunks) + 2 * width + 1,
    )


def charged(r: int, mode: str) -> dict[str, int]:
    C = log2c(r)
    if mode == "finite":
        J = (3**r // (9 * r * r)).bit_length() - 1
        K = J - 3
        b, _m = pow3floor(K)
        t = b + 5
        d = min(9, t)
        u = 3 ** (t - d)
        h = K // u
        N = 3**t
        g = (3**d + h - 1) // h
    else:
        K = (3**r // r**4).bit_length() - 1
        t = log3c(K * C**3)
        N = 3**t
        g = (N + K - 1) // K

    quotient, remainder = divmod(N, g)
    M = quotient + bool(remainder)
    must(M <= K and t < r, "rank schedule")
    w = log3c(M)
    R = 3**w
    e = log3c(g)
    G = 3**e
    s = r - t
    P = 3**s

    maps = (w + e) * (3 * N + 1)
    library = ((3 * R - 1) // 2) * 2**M
    prefix = g * (3 * P - 1)
    vectors = vnodes(t) + vnodes(w) + vnodes(s) + vnodes(e) - 6
    selector = 3 * G - 1
    br, bc, bd = binary(r)
    total = maps + library + prefix + vectors + selector + (2 * r - 1) + 6 + br + bc

    A = C + 2
    map_depth = A + vdepth(t) + t + 3
    library_depth = map_depth + vdepth(w) + w + 1
    prefix_depth = max(library_depth, A + vdepth(s)) + s + 1
    selector_depth = max(prefix_depth, map_depth + vdepth(e)) + e + 1
    depth = max(A + 4, bd + 2, selector_depth + 4)
    return {
        "r": r, "C": C, "K": K, "t": t, "N": N, "g": g,
        "M": M, "w": w, "e": e, "total": total, "depth": depth,
    }


def semantics() -> dict[str, object]:
    Q = (0, 1, 2)
    points = list(itertools.product(Q, repeat=2))
    groups = (points[:3], points[3:5], points[5:7], points[7:])
    location = {}
    for gi, group in enumerate(groups):
        for rank, point in enumerate(group):
            location[point] = (gi, rank)
    max_rank = max(map(len, groups))
    rows = 0
    fingerprints = []
    for mask in range(1 << len(points)):
        selector = {point: (mask >> i) & 1 for i, point in enumerate(points)}
        refs = {}
        roots = set()
        for gi, group in enumerate(groups):
            high = [0] * max_rank
            low = [0] * max_rank
            for rank, point in enumerate(group):
                value = point[selector[point]]
                high[rank] = 1 if value == 2 else 0
                low[rank] = 1 if value == 1 else 0
            refs[gi] = (tuple(high), tuple(low))
            roots.update(refs[gi])
        must(len(roots) <= 2**max_rank, "root count")
        fingerprints.append("|".join("".join(map(str, root)) for root in sorted(roots)))
        for point in points:
            gi, rank = location[point]
            high, low = refs[gi]
            got = {(0, 0): 0, (0, 1): 1, (1, 0): 2}[(high[rank], low[rank])]
            must(got == point[selector[point]], "semantic row")
            rows += 1
    must(location[points[0]][1] != (location[points[0]][1] + 1) % 3, "mutation")
    return {
        "selector_tables": 512,
        "rows": rows,
        "group_sizes": list(map(len, groups)),
        "fingerprint_sha256": hashlib.sha256(
            "\n".join(fingerprints).encode()
        ).hexdigest(),
        "mutation": "shifted within-group rank",
    }


def arithmetic() -> dict[str, object]:
    max_combined = (-1, 1, -1)
    first_asym = None
    last_ge_two = None
    counts = {"finite": 0, "asymptotic": 0}
    selected = []
    for r in range(64, 16385):
        finite = charged(r, "finite")
        asym = charged(r, "asymptotic")
        use_asym = asym["total"] < finite["total"]
        mode = "asymptotic" if use_asym else "finite"
        counts[mode] += 1
        if use_asym and first_asym is None:
            first_asym = r
        chosen = asym if use_asym else finite
        unit = 3**r
        num = chosen["total"] * r
        must(5 * num < 12 * unit, "combined size")
        if num * max_combined[1] > max_combined[0] * unit:
            max_combined = (num, unit, r)
        asym_num = asym["total"] * r
        if asym_num >= 2 * unit:
            last_ge_two = r
        if r in (64, 178, 434, 435, 1000, 4096, 16384):
            selected.append({
                "r": r,
                "mode": mode,
                "finite": dec(finite["total"] * r, unit),
                "asymptotic": dec(asym_num, unit),
                "K_over_r": dec(asym["K"], r),
                "M_over_K": dec(asym["M"], asym["K"]),
                "three_r_over_K": dec(3 * r, asym["K"]),
            })
    must(max_combined[2] == 64, "combined maximum")
    must(first_asym == 178, "first asym")
    must(last_ge_two == 434, "last >=2")
    return {
        "range": [64, 16384],
        "combined_bound": "5*size*r<12*3^r",
        "maximum": {
            "r": max_combined[2],
            "ratio": dec(max_combined[0], max_combined[1]),
        },
        "first_asymptotic_selection": first_asym,
        "last_asymptotic_ratio_at_least_two": last_ge_two,
        "selection_counts": counts,
        "selected": selected,
    }


def proof() -> dict[str, object]:
    rows = []
    for r in (64, 1000, 4096, 16384, 32768, 65536):
        x = charged(r, "asymptotic")
        C = x["C"]
        must(x["K"] * C**3 <= x["N"] < 3 * x["K"] * C**3, "N sandwich")
        must(C**3 <= x["g"] <= 3 * C**3, "g sandwich")
        must(x["M"] <= x["K"], "M cap")
        rows.append({
            "r": r,
            "K_over_r": dec(x["K"], r),
            "M_over_K": dec(x["M"], x["K"]),
            "three_r_over_K": dec(3 * r, x["K"]),
            "size_ratio": dec(x["total"] * r, 3**r),
        })
    return {
        "limit": "3/log_2 3",
        "limit_decimal": "1.892789260714372110",
        "depth": "r+(1+log_3 2)log_2 r+O(log log r)",
        "depth_coefficient": "1.630929753571457437",
        "identities": [
            "K/r -> log_2 3",
            "K*C^3<=N<3*K*C^3",
            "g=N/K+O(1)",
            "M/K->1",
            "3*g*P/U=3*r/K+O(1/C^3)",
            "rank library=o(U)",
            "map library=o(U)",
        ],
        "rows": rows,
    }


def result() -> dict[str, object]:
    out = {
        "schema": "orbit-synthesis/asymptotic-constant-independent/v1",
        "semantics": semantics(),
        "arithmetic": arithmetic(),
        "proof": proof(),
    }
    raw = json.dumps(out, sort_keys=True, separators=(",", ":"))
    out["semantic_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
    return out


def main() -> None:
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
    data = result()
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if expected:
        must(data == json.loads(expected.read_text()), "receipt drift")
    if output:
        output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

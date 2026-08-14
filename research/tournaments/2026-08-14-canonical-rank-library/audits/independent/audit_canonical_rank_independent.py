#!/usr/bin/env python3
"""Independent no-import reconstruction of the canonical-rank compiler."""

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


def c2(n: int) -> int:
    return (n - 1).bit_length()


def c3(n: int) -> int:
    p = 1
    k = 0
    while p < n:
        p *= 3
        k += 1
    return k


def p3(n: int) -> tuple[int, int]:
    p = 1
    k = 0
    while 3 * p <= n:
        p *= 3
        k += 1
    return k, p


def decimal(n: int, d: int, digits: int = 18) -> str:
    q, r = divmod(n, d)
    tail = []
    for _ in range(digits):
        r *= 10
        x, r = divmod(r, d)
        tail.append(str(x))
    return str(q) + "." + "".join(tail)


@lru_cache(None)
def rail_counts(w: int) -> tuple[int, int, int]:
    if w == 0:
        return 0, 0, 2
    if w == 1:
        return 4, 4, 5
    a = (w + 1) // 2
    b = w // 2
    ra, _, _ = rail_counts(a)
    rb, eb, _ = rail_counts(b)
    cross = 3**a * (3**b - 1) // 2
    r = ra + rb + 3**w + cross
    e = ra + eb + 2 * 3**w - 3 ** (w - 1) + cross
    s = 2 + ra + eb + cross + 3**w - (3 ** (w - 1) + 1) // 2
    return r, e, s


def vnodes(w: int) -> int:
    return rail_counts(w)[2]


def vdepth(w: int) -> int:
    return 2 if w == 0 else 3 + c2(w)


@lru_cache(None)
def binary_part(r: int) -> tuple[int, int, int]:
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
        (3 * q - 1) // 2 * instances,
        controls,
        (k + 1) * len(chunks) + 2 * width + 1,
    )


def params(r: int) -> dict[str, int]:
    j = (3**r // (9 * r * r)).bit_length() - 1
    k = j - 3
    b, m = p3(k)
    t = b + 5
    d = min(9, t)
    u = 3 ** (t - d)
    h = k // u
    z = 3**d
    g = (z + h - 1) // h
    q, rem = divmod(z, g)
    max_rows = (q + bool(rem)) * u
    must(max_rows <= k, "row cap")
    w = c3(max_rows)
    e = c3(g)
    s = r - t
    must(s > 0, "prefix")
    return {
        "J": j, "K": k, "b": b, "m": m, "t": t, "d": d,
        "u": u, "h": h, "g": g, "M": max_rows,
        "w": w, "R": 3**w, "e": e, "G": 3**e,
        "N": 3**t, "s": s, "P": 3**s,
    }


def charged(r: int) -> tuple[int, int, dict[str, int]]:
    x = params(r)
    map_cost = (x["w"] + x["e"]) * (3 * x["N"] + 1)
    rank_cost = (3 * x["R"] - 1) // 2 * 2 ** x["M"]
    prefix_cost = x["g"] * (3 * x["P"] - 1)
    vec = vnodes(x["t"]) + vnodes(x["w"]) + vnodes(x["s"]) + vnodes(x["e"]) - 6
    group = 3 * x["G"] - 1
    br, bc, bd = binary_part(r)
    total = map_cost + rank_cost + prefix_cost + vec + group + (2 * r - 1) + 6 + br + bc

    C = c2(r)
    A = C + 2
    map_d = A + vdepth(x["t"]) + x["t"] + 3
    rank_d = map_d + vdepth(x["w"]) + x["w"] + 1
    prefix_d = max(rank_d, A + vdepth(x["s"])) + x["s"] + 1
    group_d = max(prefix_d, map_d + vdepth(x["e"])) + x["e"] + 1
    depth = max(A + 4, bd + 2, group_d + 4)
    return total, depth, x


def semantic_check() -> dict[str, object]:
    Q = (0, 1, 2)
    points = list(itertools.product(Q, repeat=2))
    groups = (points[:3], points[3:5], points[5:7], points[7:])
    index = {}
    for gi, group in enumerate(groups):
        for rank, point in enumerate(group):
            index[point] = (gi, rank)

    rows = 0
    root_fingerprints = []
    for mask in range(1 << len(points)):
        sigma = {
            point: (mask >> position) & 1
            for position, point in enumerate(points)
        }
        roots = set()
        references = {}
        max_rank = max(map(len, groups))
        for gi, group in enumerate(groups):
            high = [0] * max_rank
            low = [0] * max_rank
            for rank, point in enumerate(group):
                value = point[sigma[point]]
                high[rank] = 1 if value == 2 else 0
                low[rank] = 1 if value == 1 else 0
            roots.add(tuple(high))
            roots.add(tuple(low))
            references[gi] = (tuple(high), tuple(low))
        must(len(roots) <= 2**max_rank, "rank root count")
        root_fingerprints.append("|".join("".join(map(str, root)) for root in sorted(roots)))

        for point in points:
            gi, rank = index[point]
            high, low = references[gi]
            pair = (high[rank], low[rank])
            got = {(0, 0): 0, (0, 1): 1, (1, 0): 2}[pair]
            must(got == point[sigma[point]], "selector reconstruction")
            rows += 1

    point = groups[0][0]
    good = index[point][1]
    bad = (good + 1) % len(groups[0])
    must(good != bad, "rank mutation")
    return {
        "selector_tables": 1 << len(points),
        "rows": rows,
        "group_sizes": list(map(len, groups)),
        "root_fingerprint_sha256": hashlib.sha256(
            "\n".join(root_fingerprints).encode()
        ).hexdigest(),
        "mutation": {
            "point": list(point),
            "rank": good,
            "shifted_rank": bad,
        },
    }


def proof_checks() -> dict[str, object]:
    bases = []
    for r in (268, 269):
        exponent = math.ceil(3 * r / 2) + 3
        must(9 * r * r * 2**exponent <= 3**r, "K base")
        bases.append([r, exponent])
    must(4 * 270**2 < 9 * 268**2, "K induction")

    maximum = (-1, -1, -1)
    table = []
    for h in range(81, 243):
        g = (19683 + h - 1) // h
        num = 2 * (9 * g + 4) * (h + 1)
        table.append([h, g, num])
        if num > maximum[0]:
            maximum = (num, h, g)
    must(maximum == (361982, 240, 83), "prefix maximum")
    tail = 361982 * 8 * 1000 + 177147 * 1000 + 5 * 177147 * 8
    den = 177147 * 8 * 1000
    must(5 * tail < 12 * den, "tail closure")
    return {
        "K_bases": bases,
        "K_induction": "4*270^2<9*268^2",
        "prefix_table": table,
        "prefix_maximum": [361982, 177147, 240, 83],
        "tail": [tail, den],
    }


def arithmetic_check() -> dict[str, object]:
    maximum = (-1, 1, -1)
    finite = (-1, 1, -1)
    selected = []
    for r in range(64, 16385):
        total, depth, x = charged(r)
        unit = 3**r
        num = total * r
        must(5 * num < 12 * unit, "size")
        C = c2(r)
        depth_bound = r + C + math.ceil(2 * (C + 1) / 3) + 2 * c2(C + 4) + 23
        must(depth <= depth_bound, "depth")
        if num * maximum[1] > maximum[0] * unit:
            maximum = (num, unit, r)
        if r <= 267 and num * finite[1] > finite[0] * unit:
            finite = (num, unit, r)
        if r in (64, 65, 66, 67, 100, 267, 268, 1000, 4096, 16384):
            selected.append({
                "r": r,
                "J": x["J"],
                "K": x["K"],
                "t": x["t"],
                "g": x["g"],
                "M": x["M"],
                "ratio": decimal(num, unit),
                "depth": depth,
                "depth_bound": depth_bound,
            })
    must(maximum[2] == 64 and finite[2] == 64, "maximum")
    return {
        "range": [64, 16384],
        "maximum": {
            "r": maximum[2],
            "ratio": decimal(maximum[0], maximum[1]),
        },
        "finite": {
            "range": [64, 267],
            "r": finite[2],
            "ratio": decimal(finite[0], finite[1]),
        },
        "selected": selected,
        "size": "5*size*r<12*3^r",
    }


def result() -> dict[str, object]:
    out = {
        "schema": "orbit-synthesis/canonical-rank-independent/v1",
        "semantics": semantic_check(),
        "proof": proof_checks(),
        "arithmetic": arithmetic_check(),
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

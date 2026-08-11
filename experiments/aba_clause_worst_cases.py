#!/usr/bin/env python3
"""Finite constructions for notes/ABA_CLAUSE_WORST_CASES.md."""

from __future__ import annotations

from itertools import combinations
from math import ceil, log2


def middle_layer(n: int) -> list[int]:
    r = n // 2
    return [sum(1 << i for i in c) for c in combinations(range(n), r)]


def sperner_cycle_map(n: int):
    cells = middle_layer(n)

    def f(mask: int) -> int:
        out = 0
        for i, c in enumerate(cells):
            if mask & c == c:
                out |= cells[(i + 1) % len(cells)]
        return out

    return cells, f


def positive_cnf_clauses(n: int, f, coordinate: int) -> list[int]:
    """Prime positive clauses for `[coordinate in f(B)]`."""
    universe = (1 << n) - 1
    false_sets = [
        b for b in range(1 << n)
        if not (f(b) & (1 << coordinate))
    ]
    maximal_false = [
        b for b in false_sets
        if not any(b != c and (b & c) == b for c in false_sets)
    ]
    return [universe ^ b for b in maximal_false]


def build_predecessor_from_monotone_map(n: int, f):
    """Return clause-neighborhoods N[a][u] realizing P=f."""
    universe = (1 << n) - 1
    clauses = [positive_cnf_clauses(n, f, a) for a in range(n)]
    max_clauses = max(len(c) for c in clauses)
    input_count = 1 << ceil(log2(max(1, max_clauses)))
    neighborhoods: list[list[int]] = []
    for cs in clauses:
        neighborhoods.append(cs + [universe] * (input_count - len(cs)))
    return neighborhoods


def predecessor(neighborhoods: list[list[int]], target: int) -> int:
    out = 0
    for a, row in enumerate(neighborhoods):
        if all(target & neighborhood for neighborhood in row):
            out |= 1 << a
    return out


def canonical_hits(allowed: int, hits: list[int]) -> tuple[int, ...]:
    hits = [h & allowed for h in hits]
    if any(h == 0 for h in hits):
        return (0,)
    unique = sorted(set(h for h in hits if h != allowed))
    return tuple(
        h for h in unique
        if not any(g != h and (g & h) == g for g in unique)
    )


def check_sperner_n4() -> None:
    n = 4
    universe = (1 << n) - 1
    cells, f = sperner_cycle_map(n)
    assert len(cells) == 6
    assert f(universe) == universe
    assert all(f(cells[i]) == cells[(i + 1) % 6] for i in range(6))

    neighborhoods = build_predecessor_from_monotone_map(n, f)
    assert len(neighborhoods[0]) == 4  # four Boolean input labels
    assert all(predecessor(neighborhoods, b) == f(b) for b in range(1 << n))

    c0 = cells[0]
    hits: tuple[int, ...] = ()
    widths = [0]
    for _ in range(6):
        hits = canonical_hits(
            universe,
            [c0] + [predecessor(neighborhoods, h) for h in hits],
        )
        widths.append(len(hits))
    assert widths == list(range(7))

    stable = canonical_hits(
        universe,
        [c0] + [predecessor(neighborhoods, h) for h in hits],
    )
    assert stable == hits
    print("n=4 Sperner construction: widths", widths, "then stable")


def permutation_from_cycles(cycles: list[list[int]], n: int) -> list[int]:
    delta = list(range(n))
    for cycle in cycles:
        for i, a in enumerate(cycle):
            delta[a] = cycle[(i + 1) % len(cycle)]
    return delta


def inverse_image(delta: list[int], target: int) -> int:
    out = 0
    for a, v in enumerate(delta):
        if target & (1 << v):
            out |= 1 << a
    return out


def check_deterministic_n8() -> None:
    # n=8 admits permutation order lcm(5,3)=15.
    n = 8
    universe = (1 << n) - 1
    delta = permutation_from_cycles(
        [list(range(5)), [5, 6, 7]], n
    )

    # One distinguished point from each cycle has full orbit period 15.
    c0 = (1 << 0) | (1 << 5)
    orbit: list[int] = []
    c = c0
    while c not in orbit:
        orbit.append(c)
        c = inverse_image(delta, c)
    assert c == c0
    assert len(orbit) == 15
    assert len(set(x.bit_count() for x in orbit)) == 1

    hits: tuple[int, ...] = ()
    for t in range(15):
        hits = canonical_hits(
            universe,
            [c0] + [inverse_image(delta, h) for h in hits],
        )
        assert len(hits) == t + 1

    stable = canonical_hits(
        universe,
        [c0] + [inverse_image(delta, h) for h in hits],
    )
    assert stable == hits
    print("n=8 deterministic permutation: 15 incomparable hits then stable")


def main() -> None:
    check_sperner_n4()
    check_deterministic_n8()
    print("ABA clause worst-case constructions: all checks passed")


if __name__ == "__main__":
    main()

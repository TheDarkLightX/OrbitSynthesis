#!/usr/bin/env python3
"""Exact finite checks for atomic ABA predicate / group-testing results.

For the interior-y fiber with r coarse nonzero rows,

    F_r = {supports on [r]x{0,1} with no zero row and both columns nonzero}.

The theorem in notes/ABA_GROUP_TESTING.md says:

    |F_r| = 3^r - 2
    exact adaptive/non-adaptive intersection-query complexity = 2r  (r>=2)

The lower bound is witnessed by the full support and all of its single-cell
deletions: separating each deletion from the full support forces that singleton
query.
"""

from __future__ import annotations

from itertools import combinations
from math import ceil, log2


def family_F(r: int) -> list[int]:
    n = 2 * r
    out: list[int] = []
    for s in range(1, 1 << n):
        # Every row has at least one of its two cells.
        if any((s & (0b11 << (2 * row))) == 0 for row in range(r)):
            continue
        # Both columns occur.
        col0 = any(s & (1 << (2 * row)) for row in range(r))
        col1 = any(s & (1 << (2 * row + 1)) for row in range(r))
        if col0 and col1:
            out.append(s)
    return out


def outcome(support: int, query: int) -> bool:
    return bool(support & query)


def separating_queries(a: int, b: int, n: int) -> list[int]:
    return [q for q in range(1, 1 << n) if outcome(a, q) != outcome(b, q)]


def verify_coatom_forcing(r: int) -> None:
    assert r >= 2
    n = 2 * r
    fam = set(family_F(r))
    full = (1 << n) - 1
    assert full in fam

    for v in range(n):
        coat = full ^ (1 << v)
        assert coat in fam
        sep = separating_queries(full, coat, n)
        # The only query that distinguishes full support from this co-atom is
        # the singleton corresponding to the missing cell.
        assert sep == [1 << v]


def distinct_singleton_signatures(r: int) -> None:
    """Singleton queries identify every support exactly."""
    fam = family_F(r)
    signatures = {
        tuple(outcome(s, 1 << v) for v in range(2 * r))
        for s in fam
    }
    assert len(signatures) == len(fam)


def main() -> None:
    print("ABA interior-y fiber group-testing checks")
    for r in range(1, 6):
        fam = family_F(r)
        assert len(fam) == 3**r - 2
        if r == 1:
            optimum = 0
        else:
            verify_coatom_forcing(r)
            distinct_singleton_signatures(r)
            optimum = 2 * r
        info = 0 if len(fam) <= 1 else ceil(log2(len(fam)))
        print(
            f"  r={r}: |F_r|={len(fam):4d}, "
            f"information LB={info:2d}, atomic optimum={optimum:2d}"
        )

    # The ocLTL hardest ABA fiber.
    assert len(family_F(4)) == 79
    assert ceil(log2(79)) == 7
    print("hardest r=4 fiber: 7 unrestricted bits, but 8 atomic equation tests")


if __name__ == "__main__":
    main()

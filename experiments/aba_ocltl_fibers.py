#!/usr/bin/env python3
"""Exact verification of the ABA ocLTL projection-fiber formulas.

A complete 3-type is a nonempty support on the 8 cells of (m,x,y).
Project to the (m,x)-type and the y-type, then count fibers.

Expected distribution over T2 x T1:
    34 fibers of size 1
     6 fibers of size 7
     4 fibers of size 25
     1 fiber  of size 79
Weighted total: 255 complete 3-types.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from math import comb, ceil, log2

from aba_types import iter_types, restrict_support, type_count


def support_size(mask: int) -> int:
    return mask.bit_count()


def projection_pair(type_mask: int) -> tuple[int, int]:
    """Project a 3-type on (m,x,y) to ((m,x)-type, y-type)."""
    mx = restrict_support(type_mask, 3, (0, 1))
    y = restrict_support(type_mask, 3, (2,))
    return mx, y


def no_zero_row_col_count(r: int, c: int) -> int:
    """Number of r x c binary matrices with no zero row or zero column."""
    return sum(
        (-1) ** j * comb(c, j) * ((1 << (c - j)) - 1) ** r
        for j in range(c + 1)
    )


def enumerate_fibers() -> dict[tuple[int, int], list[int]]:
    fibers: dict[tuple[int, int], list[int]] = defaultdict(list)
    for t in iter_types(3):
        fibers[projection_pair(t)].append(t)
    return dict(fibers)


def theoretical_fiber_size(mx_type: int, y_type: int) -> int:
    r = support_size(mx_type)
    c = support_size(y_type)
    return no_zero_row_col_count(r, c)


def self_test() -> None:
    fibers = enumerate_fibers()

    # Every T2 x T1 projection pair occurs.
    assert len(fibers) == type_count(2) * type_count(1) == 45

    # Every enumerated fiber agrees with the inclusion-exclusion formula.
    for pair, members in fibers.items():
        assert len(members) == theoretical_fiber_size(*pair)

    distribution = Counter(map(len, fibers.values()))
    assert distribution == Counter({1: 34, 7: 6, 25: 4, 79: 1})
    assert sum(size * count for size, count in distribution.items()) == type_count(3) == 255

    max_fiber = max(distribution)
    assert max_fiber == 79
    assert ceil(log2(max_fiber)) == 7

    # Information-theoretic consequences.
    assert (1 << 6) < max_fiber <= (1 << 7)
    assert (1 << 7) < type_count(3) <= (1 << 8)


def main() -> None:
    self_test()
    fibers = enumerate_fibers()
    distribution = Counter(map(len, fibers.values()))
    print("ABA ocLTL projection-fiber distribution")
    for size in sorted(distribution):
        print(f"  {distribution[size]:2d} fibers of size {size}")
    print(f"  projection signatures: {len(fibers)}")
    print(f"  complete T3 types:     {type_count(3)}")
    print(f"  largest fiber:         {max(distribution)}")
    print("  extra predicate bits needed for possible full refinement: 7")


if __name__ == "__main__":
    main()

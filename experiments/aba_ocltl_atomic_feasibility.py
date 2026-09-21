#!/usr/bin/env python3
"""Exhaustive validator for notes/ABA_OCLTL_ATOMIC_FEASIBILITY.md.

For random families of atomic ABA equations on the eight `(m,x,y)` minterm
cells, compare:

1. explicit feasibility by enumerating all 255 nonempty T3 supports; and
2. the closed-form maximal-available-support criterion.

For each tested predicate family the checker ranges over all 15 T2 row-support
codes, all 3 y T1 column-support codes, and every truth pattern D.
"""

from __future__ import annotations

import random


def row_projection(q: int) -> int:
    p = 0
    for row in range(4):
        if q & ((1 << (2 * row)) | (1 << (2 * row + 1))):
            p |= 1 << row
    return p


def col_projection(q: int) -> int:
    r = 0
    for col in range(2):
        if any(q & (1 << (2 * row + col)) for row in range(4)):
            r |= 1 << col
    return r


def explicit_feasible(p: int, r: int, d_bits: int, masks: list[int]) -> bool:
    for q in range(1, 256):
        if row_projection(q) != p or col_projection(q) != r:
            continue
        if all(
            ((q & mask) == 0) == bool(d_bits & (1 << i))
            for i, mask in enumerate(masks)
        ):
            return True
    return False


def available_support(p: int, r: int, d_bits: int, masks: list[int]) -> int:
    available = 0
    for row in range(4):
        if not (p & (1 << row)):
            continue
        for col in range(2):
            if not (r & (1 << col)):
                continue
            edge = 2 * row + col
            forbidden = any(
                (d_bits & (1 << i)) and (mask & (1 << edge))
                for i, mask in enumerate(masks)
            )
            if not forbidden:
                available |= 1 << edge
    return available


def closed_form_feasible(p: int, r: int, d_bits: int, masks: list[int]) -> bool:
    if p == 0 or r == 0:
        return False

    available = available_support(p, r, d_bits, masks)

    # Every selected row must survive.
    for row in range(4):
        if p & (1 << row):
            row_mask = (1 << (2 * row)) | (1 << (2 * row + 1))
            if not (available & row_mask):
                return False

    # Every selected column must survive.
    for col in range(2):
        if r & (1 << col):
            if not any(available & (1 << (2 * row + col)) for row in range(4)):
                return False

    # Every equation declared false must be nonzero somewhere.
    for i, mask in enumerate(masks):
        if not (d_bits & (1 << i)) and not (available & mask):
            return False

    return True


def verify_family(masks: list[int]) -> None:
    for d_bits in range(1 << len(masks)):
        for p in range(1, 16):
            for r in range(1, 4):
                closed = closed_form_feasible(p, r, d_bits, masks)
                explicit = explicit_feasible(p, r, d_bits, masks)
                assert closed == explicit, (
                    masks,
                    d_bits,
                    p,
                    r,
                    available_support(p, r, d_bits, masks),
                    closed,
                    explicit,
                )


def edge_cases() -> None:
    verify_family([])
    verify_family([0])       # equation 0=0: always true, never false
    verify_family([255])     # equation 1=0: never true, false on every type
    verify_family([1, 2])    # distinct singleton minterm equations
    verify_family([0b01010101, 0b10101010])


def randomized_checks(seed: int = 12) -> None:
    rng = random.Random(seed)
    # Exhaustiveness over outer assignments costs 45*2^d per family. Keep many
    # samples at low d and a smaller but still complete set at higher d.
    schedule = {
        1: 100,
        2: 100,
        3: 80,
        4: 40,
        5: 15,
        6: 8,
    }
    for d, samples in schedule.items():
        for _ in range(samples):
            masks = [rng.randrange(256) for _ in range(d)]
            verify_family(masks)
        print(f"d={d}: {samples} randomized families passed exhaustive validation")


def main() -> None:
    edge_cases()
    randomized_checks()
    print("ABA ocLTL atomic feasibility: all exact checks passed")


if __name__ == "__main__":
    main()

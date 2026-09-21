#!/usr/bin/env python3
"""Exact finite checker for ABA clause projection.

A clause over fine support cells has the form

    AND_{u in Z} not w_u
    AND
    AND_j OR_{u in G_j} w_u.

The theorem in notes/ABA_CLAUSE_PROJECTION.md projects an existential block
without enumerating witnesses.  This script compares that closed form against
exhaustive enumeration of every legal fine refinement for bounded instances.
"""

from __future__ import annotations

import itertools
import random


def fibers(n_coarse: int, r_added: int) -> list[int]:
    m = 1 << r_added
    out: list[int] = []
    for i in range(n_coarse):
        mask = 0
        for b in range(m):
            mask |= 1 << (i * m + b)
        out.append(mask)
    return out


def enumerate_extensions(coarse_support: int, n_coarse: int, r_added: int):
    m = 1 << r_added
    choices = []
    for i in range(n_coarse):
        if coarse_support & (1 << i):
            choices.append(range(1, 1 << m))
        else:
            choices.append((0,))

    for local_supports in itertools.product(*choices):
        fine = 0
        for i, local in enumerate(local_supports):
            for b in range(m):
                if local & (1 << b):
                    fine |= 1 << (i * m + b)
        yield fine


def clause_holds(fine_support: int, forbidden: int, positive_sets: list[int]) -> bool:
    if fine_support & forbidden:
        return False
    return all(fine_support & g for g in positive_sets)


def exhaustive_projection(
    n_coarse: int,
    r_added: int,
    forbidden: int,
    positive_sets: list[int],
) -> set[int]:
    out: set[int] = set()
    for z in range(1, 1 << n_coarse):
        if any(
            clause_holds(w, forbidden, positive_sets)
            for w in enumerate_extensions(z, n_coarse, r_added)
        ):
            out.add(z)
    return out


def closed_projection(
    n_coarse: int,
    r_added: int,
    forbidden: int,
    positive_sets: list[int],
) -> set[int]:
    fs = fibers(n_coarse, r_added)
    fine_width = n_coarse * (1 << r_added)
    allowed = ((1 << fine_width) - 1) & ~forbidden

    dead = {
        i
        for i, fib in enumerate(fs)
        if not (allowed & fib)
    }

    coarse_hit_sets: list[set[int]] = []
    for g in positive_sets:
        coarse_hit_sets.append(
            {
                i
                for i, fib in enumerate(fs)
                if allowed & g & fib
            }
        )

    out: set[int] = set()
    for z in range(1, 1 << n_coarse):
        if any(z & (1 << i) for i in dead):
            continue
        if all(any(z & (1 << i) for i in h) for h in coarse_hit_sets):
            out.add(z)
    return out


def self_test(seed: int = 0) -> None:
    rng = random.Random(seed)

    for n_coarse in range(1, 5):
        for r_added in (1, 2):
            fine_width = n_coarse * (1 << r_added)
            for _ in range(100):
                forbidden = rng.randrange(1 << fine_width)
                q = rng.randrange(4)
                positive_sets = [
                    rng.randrange(1 << fine_width)
                    for _ in range(q)
                ]

                exact = exhaustive_projection(
                    n_coarse, r_added, forbidden, positive_sets
                )
                closed = closed_projection(
                    n_coarse, r_added, forbidden, positive_sets
                )
                assert exact == closed


def main() -> None:
    self_test()
    print("ABA clause-projection exhaustive checks passed")
    print("  n_coarse = 1..4")
    print("  eliminated BA variables r = 1,2")
    print("  100 randomized clauses per (n_coarse,r)")
    print("  0..3 positive disequation obligations")


if __name__ == "__main__":
    main()

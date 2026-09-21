#!/usr/bin/env python3
"""Exact bounded checker for notes/ABA_BLOCK_QE.md.

A complete ABA type on k+r variables is represented as a nonzero support on
2^(k+r) fine minterm cells.  The first k coordinates are retained; the last r
are existentially eliminated.

For a normalized clause

    f=0 AND g_1!=0 AND ... AND g_m!=0

we compare:

1. exhaustive search over every fine support extending a coarse support; and
2. the direct block projection theorem:

       no active coarse cell may have all fine labels forbidden by f,
       and each g_i must have an allowed witness label in some active coarse cell.

The exhaustive side is exponential and intended only for bounded validation.
"""

from __future__ import annotations

from itertools import product
import random


def fine_extensions(coarse_support: int, k: int, r: int):
    """Enumerate every fine support whose projection is coarse_support."""
    n_coarse = 1 << k
    labels_per_coarse = 1 << r
    active = [v for v in range(n_coarse) if coarse_support & (1 << v)]

    # Every active coarse cell chooses an arbitrary nonempty subset of its
    # 2^r fine labels; inactive cells choose the empty subset.
    local_choices = [range(1, 1 << labels_per_coarse) for _ in active]
    for choices in product(*local_choices):
        fine = 0
        for v, local_mask in zip(active, choices):
            for b in range(labels_per_coarse):
                if local_mask & (1 << b):
                    fine |= 1 << (v * labels_per_coarse + b)
        yield fine


def direct_projection(f_mask: int, g_masks: list[int], k: int, r: int):
    """Return (bad_coarse_mask, witness_coarse_masks)."""
    n_coarse = 1 << k
    labels_per_coarse = 1 << r

    bad = 0
    for v in range(n_coarse):
        if all(
            f_mask & (1 << (v * labels_per_coarse + b))
            for b in range(labels_per_coarse)
        ):
            bad |= 1 << v

    witnesses: list[int] = []
    for g_mask in g_masks:
        h = 0
        for v in range(n_coarse):
            if any(
                not (f_mask & (1 << (v * labels_per_coarse + b)))
                and (g_mask & (1 << (v * labels_per_coarse + b)))
                for b in range(labels_per_coarse)
            ):
                h |= 1 << v
        witnesses.append(h)

    return bad, witnesses


def projected_holds(
    coarse_support: int, bad: int, witnesses: list[int]
) -> bool:
    return not (coarse_support & bad) and all(
        coarse_support & h for h in witnesses
    )


def exhaustive_holds(
    coarse_support: int,
    f_mask: int,
    g_masks: list[int],
    k: int,
    r: int,
) -> bool:
    for fine_support in fine_extensions(coarse_support, k, r):
        # f=0 iff the realized fine support avoids every minterm where f=1.
        if fine_support & f_mask:
            continue
        if all(fine_support & g for g in g_masks):
            return True
    return False


def verify_instance(f_mask: int, g_masks: list[int], k: int, r: int) -> None:
    bad, witnesses = direct_projection(f_mask, g_masks, k, r)
    for coarse_support in range(1, 1 << (1 << k)):
        direct = projected_holds(coarse_support, bad, witnesses)
        exhaustive = exhaustive_holds(
            coarse_support, f_mask, g_masks, k, r
        )
        assert direct == exhaustive, (
            k,
            r,
            coarse_support,
            f_mask,
            g_masks,
            bad,
            witnesses,
            direct,
            exhaustive,
        )


def randomized_checks(seed: int = 0) -> None:
    rng = random.Random(seed)

    # These domains are small enough to exhaust every extension repeatedly.
    schedule = [
        (1, 1, 300),
        (2, 1, 200),
        (1, 2, 200),
    ]

    for k, r, trials in schedule:
        fine_cells = 1 << (k + r)
        mask_bound = 1 << fine_cells
        for _ in range(trials):
            f_mask = rng.randrange(mask_bound)
            g_masks = [
                rng.randrange(mask_bound) for _ in range(rng.randrange(5))
            ]
            verify_instance(f_mask, g_masks, k, r)
        print(f"randomized exact checks passed: k={k}, r={r}, trials={trials}")


def edge_cases() -> None:
    # f=0 identically: every fine cell is allowed.
    verify_instance(0, [], 2, 1)

    # f=1 identically: no nonzero coarse support has an extension.
    all_fine = (1 << (1 << (2 + 1))) - 1
    verify_instance(all_fine, [], 2, 1)

    # An inequation whose support lies entirely inside f's forbidden region
    # can never be witnessed.
    verify_instance(0b0001, [0b0001], 1, 1)

    # Two inequations can demand opposite fine labels in the same coarse cell;
    # atomlessness realizes both labels simultaneously when both are allowed.
    # k=0 means one coarse region (the whole BA), r=1 means two fine labels.
    verify_instance(0, [0b01, 0b10], 0, 1)


def main() -> None:
    edge_cases()
    randomized_checks()
    print("ABA direct block QE checker: all tests passed")


if __name__ == "__main__":
    main()

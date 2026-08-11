#!/usr/bin/env python3
"""Constructive effective witness oracle for the countable dyadic interval ABA.

Elements are finite unions of half-open dyadic intervals on [0,1), represented
as bit masks at a common grid depth.  The algebra permits arbitrary refinement,
so it is atomless even though each individual representation is finite.

This script verifies that every compatible target support type can be realized
constructively, and exercises the maximal-allowed support response used by the
safety strategy.
"""

from __future__ import annotations

import random


def refine_mask(mask: int, old_depth: int, new_depth: int) -> int:
    assert new_depth >= old_depth
    factor = 1 << (new_depth - old_depth)
    block = (1 << factor) - 1
    out = 0
    for atom in range(1 << old_depth):
        if (mask >> atom) & 1:
            out |= block << (atom * factor)
    return out


def support_type(masks: list[int], depth: int) -> int:
    """Return the nonzero Venn-cell support of a tuple of BA elements."""
    support = 0
    for atom in range(1 << depth):
        cell = 0
        for i, mask in enumerate(masks):
            cell |= ((mask >> atom) & 1) << i
        support |= 1 << cell
    return support


def restrict_target_support(target: int, k: int, r: int) -> int:
    coarse = 0
    for fine_cell in range(1 << (k + r)):
        if (target >> fine_cell) & 1:
            coarse |= 1 << (fine_cell & ((1 << k) - 1))
    return coarse


def realize_extension(
    old_masks: list[int],
    depth: int,
    r: int,
    target_support: int,
) -> tuple[list[int], int]:
    """Realize a compatible complete support extension by r new BA elements."""
    k = len(old_masks)
    old_support = support_type(old_masks, depth)
    assert restrict_target_support(target_support, k, r) == old_support

    requested: dict[int, list[int]] = {}
    max_choices = 1
    for coarse in range(1 << k):
        if not ((old_support >> coarse) & 1):
            continue
        vals = [
            u
            for u in range(1 << r)
            if (target_support >> (coarse | (u << k))) & 1
        ]
        assert vals
        requested[coarse] = vals
        max_choices = max(max_choices, len(vals))

    extra_depth = (max_choices - 1).bit_length()
    new_depth = depth + extra_depth
    refined_old = [refine_mask(m, depth, new_depth) for m in old_masks]

    atoms_by_cell: dict[int, list[int]] = {c: [] for c in requested}
    for atom in range(1 << new_depth):
        coarse = 0
        for i, mask in enumerate(refined_old):
            coarse |= ((mask >> atom) & 1) << i
        atoms_by_cell[coarse].append(atom)

    new_masks = [0] * r
    for coarse, atoms in atoms_by_cell.items():
        vals = requested[coarse]
        assert len(atoms) >= len(vals)
        for j, atom in enumerate(atoms):
            value = vals[j] if j < len(vals) else vals[0]
            for bit in range(r):
                if (value >> bit) & 1:
                    new_masks[bit] |= 1 << atom

    full = refined_old + new_masks
    assert support_type(full, new_depth) == target_support
    return full, new_depth


def random_compatible_target(
    rng: random.Random, old_support: int, k: int, r: int
) -> int:
    target = 0
    for coarse in range(1 << k):
        if not ((old_support >> coarse) & 1):
            continue
        local = rng.randrange(1, 1 << (1 << r))  # nonempty subset of r-bit values
        for value in range(1 << r):
            if (local >> value) & 1:
                target |= 1 << (coarse | (value << k))
    return target


def maximal_allowed_target(
    old_support: int, k: int, r: int, forbidden_fine_cells: int
) -> int | None:
    """Q_max: activate every allowed fine cell above the observed old type."""
    target = 0
    for coarse in range(1 << k):
        if not ((old_support >> coarse) & 1):
            continue
        local_count = 0
        for value in range(1 << r):
            fine = coarse | (value << k)
            if not ((forbidden_fine_cells >> fine) & 1):
                target |= 1 << fine
                local_count += 1
        if local_count == 0:
            return None
    return target


def self_test(seed: int = 19) -> None:
    rng = random.Random(seed)

    for k in (1, 2, 3):
        for r in (1, 2):
            for depth in (1, 2, 3):
                width = 1 << depth
                for _ in range(100):
                    old = [rng.randrange(1 << width) for _ in range(k)]
                    old_support = support_type(old, depth)

                    target = random_compatible_target(rng, old_support, k, r)
                    full, new_depth = realize_extension(old, depth, r, target)
                    assert support_type(full, new_depth) == target
                    assert new_depth - depth <= r

                    # Exercise the maximal-support strategy target too.
                    fine_cells = 1 << (k + r)
                    forbidden = rng.randrange(1 << fine_cells)
                    qmax = maximal_allowed_target(
                        old_support, k, r, forbidden
                    )
                    if qmax is not None:
                        full2, depth2 = realize_extension(old, depth, r, qmax)
                        assert support_type(full2, depth2) == qmax
                        assert not (qmax & forbidden)


def main() -> None:
    self_test()
    print("dyadic ABA constructive witness checks passed")
    print("  k=1..3 existing coordinates")
    print("  r=1..2 added coordinates")
    print("  initial dyadic depths 1..3")
    print("  100 random extensions per (k,r,depth)")
    print("  maximal-support strategy targets also exercised")


if __name__ == "__main__":
    main()

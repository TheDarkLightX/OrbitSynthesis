#!/usr/bin/env python3
"""Differential checks for the two-phase ABA clause safety solver.

The solver from notes/ABA_SAFETY_BEKIC.md computes:

  1. the forbidden/zero fixed point independently;
  2. the positive fixed point as finite orbits of seed obligations under a
     unary mask transformer L, with False as an absorbing bottom.

We compare it against ordinary whole-clause greatest-fixed-point iteration.
"""

from __future__ import annotations

import random

from aba_safety_clause_game import (
    Clause,
    normalize,
    conjunction,
    pullback,
    existential_project,
    universal_project,
    cpre_clause,
    random_clause,
    preimage_cellmask,
    fiber_masks,
)


def whole_fixed_point(step: Clause, safe: Clause, d: int, e: int) -> Clause:
    w = normalize(Clause(d))
    for _ in range(10000):
        nxt = conjunction(safe, cpre_clause(step, w, d, e))
        if nxt == w:
            return w
        w = nxt
    raise RuntimeError("whole clause fixed point did not converge")


def zero_cpre(step_z: int, winning_z: int, d: int, e: int) -> int:
    full_arity = 2 * d + e
    next_positions = tuple(range(d + e, full_arity))
    partial_positions = tuple(range(d + e))
    state_positions = tuple(range(d))

    full_z = step_z | preimage_cellmask(
        winning_z, full_arity, next_positions
    )

    partial_z = 0
    for p, fiber in enumerate(fiber_masks(full_arity, partial_positions)):
        if fiber & ~full_z == 0:
            partial_z |= 1 << p

    state_z = 0
    for s, fiber in enumerate(fiber_masks(d + e, state_positions)):
        if fiber & partial_z:
            state_z |= 1 << s

    return state_z


def zero_fixed_point(step: Clause, safe: Clause, d: int, e: int) -> int:
    universe = (1 << (1 << d)) - 1
    if step.is_false or safe.is_false:
        return universe

    z = 0
    for _ in range((1 << d) + 2):
        nxt = (safe.forbidden | zero_cpre(step.forbidden, z, d, e)) & universe
        if nxt == z:
            return z
        assert z & ~nxt == 0
        z = nxt

    raise RuntimeError("zero fixed point exceeded lattice-height bound")


def positive_full_to_state(
    fine_mask: int,
    full_forbidden: int,
    d: int,
    e: int,
) -> int:
    """Existential system image followed by universal environment image."""
    full_arity = 2 * d + e
    partial_positions = tuple(range(d + e))
    state_positions = tuple(range(d))

    partial_hit = 0
    for p, fiber in enumerate(fiber_masks(full_arity, partial_positions)):
        if fiber & fine_mask & ~full_forbidden:
            partial_hit |= 1 << p

    state_hit = 0
    for s, fiber in enumerate(fiber_masks(d + e, state_positions)):
        if fiber & ~partial_hit == 0:
            state_hit |= 1 << s

    return state_hit


def obligation_map(g: int, zstar: int, step: Clause, d: int, e: int) -> int:
    full_arity = 2 * d + e
    next_positions = tuple(range(d + e, full_arity))
    full_forbidden = step.forbidden | preimage_cellmask(
        zstar, full_arity, next_positions
    )
    lifted = preimage_cellmask(g, full_arity, next_positions)
    return positive_full_to_state(lifted, full_forbidden, d, e)


def step_seed(h: int, zstar: int, step: Clause, d: int, e: int) -> int:
    full_arity = 2 * d + e
    next_positions = tuple(range(d + e, full_arity))
    full_forbidden = step.forbidden | preimage_cellmask(
        zstar, full_arity, next_positions
    )
    return positive_full_to_state(h, full_forbidden, d, e)


def minimal_family(allowed: int, masks: list[int]) -> tuple[int, ...] | None:
    """Canonical positive antichain; None denotes semantic False."""
    vals: list[int] = []
    for mask in masks:
        mask &= allowed
        if mask == 0:
            return None
        if mask == allowed:
            continue
        vals.append(mask)

    vals = sorted(set(vals), key=lambda x: (x.bit_count(), x))
    out: list[int] = []
    for mask in vals:
        if not any((old & mask) == old for old in out):
            out.append(mask)
    return tuple(sorted(out))


def orbit_solver(step: Clause, safe: Clause, d: int, e: int) -> Clause:
    if step.is_false or safe.is_false:
        return Clause(d, is_false=True)

    zstar = zero_fixed_point(step, safe, d, e)
    universe = (1 << (1 << d)) - 1
    allowed = universe & ~zstar
    if allowed == 0:
        return Clause(d, is_false=True)

    seeds = list(safe.positive)
    seeds.extend(
        step_seed(h, zstar, step, d, e) for h in step.positive
    )
    seed_antichain = minimal_family(allowed, seeds)
    if seed_antichain is None:
        return Clause(d, is_false=True)

    all_masks: list[int] = []
    for seed in seed_antichain:
        current = seed
        seen: set[int] = set()
        while current not in seen:
            seen.add(current)
            current &= allowed
            if current == 0:
                return Clause(d, is_false=True)
            if current != allowed:
                all_masks.append(current)
            current = obligation_map(current, zstar, step, d, e) & allowed

    final_antichain = minimal_family(allowed, all_masks)
    if final_antichain is None:
        return Clause(d, is_false=True)

    return normalize(Clause(d, zstar, final_antichain))


def first_obligation_cycle_length(
    start: int, zstar: int, step: Clause, d: int, e: int
) -> int:
    universe = (1 << (1 << d)) - 1
    allowed = universe & ~zstar
    current = start & allowed
    index: dict[int, int] = {}
    orbit: list[int] = []
    while current not in index:
        index[current] = len(orbit)
        orbit.append(current)
        current = obligation_map(current, zstar, step, d, e) & allowed
    return len(orbit) - index[current]


def run_random_suite(
    rng: random.Random, d: int, e: int, trials: int
) -> int:
    max_cycle = 0
    for _ in range(trials):
        step = random_clause(rng, 2 * d + e, max_positive=5)
        safe = random_clause(rng, d, max_positive=3)

        whole = whole_fixed_point(step, safe, d, e)
        decomposed = orbit_solver(step, safe, d, e)
        assert decomposed == whole

        if not step.is_false and not safe.is_false:
            zstar = zero_fixed_point(step, safe, d, e)
            universe = (1 << (1 << d)) - 1
            allowed = universe & ~zstar
            if allowed:
                candidate = rng.randrange(1 << (1 << d)) & allowed
                if candidate not in (0, allowed):
                    max_cycle = max(
                        max_cycle,
                        first_obligation_cycle_length(
                            candidate, zstar, step, d, e
                        ),
                    )
    return max_cycle


def self_test(seed: int = 20260811) -> None:
    rng = random.Random(seed)

    suites = [
        (1, 1, 2000),
        (1, 2, 1000),
        (2, 1, 1000),
        (2, 2, 500),
        (3, 1, 100),
    ]

    cycle_summary = {}
    for d, e, trials in suites:
        cycle_summary[(d, e)] = run_random_suite(rng, d, e, trials)

    # Monotone obligation maps can nevertheless have nontrivial cycles among
    # incomparable masks.  The random suite is not required to discover one
    # on every run, so pin a deterministic d=1 example observed during
    # falsification: Step forbidden mask 132 swaps the two singleton state
    # obligations under L when z*=0.
    step = normalize(Clause(3, forbidden=132))
    zstar = 0
    assert obligation_map(1, zstar, step, 1, 1) == 2
    assert obligation_map(2, zstar, step, 1, 1) == 1


def main() -> None:
    self_test()
    print("ABA Bekić/orbit safety decomposition checks passed")
    print("  whole-clause fixed point == zero+orbit solver")
    print("  randomized d/e suites up through d=3")
    print("  deterministic nontrivial obligation 2-cycle pinned")


if __name__ == "__main__":
    main()

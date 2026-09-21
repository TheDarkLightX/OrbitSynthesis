#!/usr/bin/env python3
"""Differential oracle for the ABA support-clause safety-game algorithm.

For d=e=1:

- state types: 3;
- (state,input) types: 15;
- (state,input,next) types: 255.

We compare the symbolic clause algorithm

    W_{n+1} = Safe & forall input. exists next. Step & W_n(next)

against explicit complete-type game enumeration on every approximant for
random generated Step/Safe clauses.
"""

from __future__ import annotations

from dataclasses import dataclass
import random


def project_cell(cell: int, positions: tuple[int, ...]) -> int:
    out = 0
    for new_pos, old_pos in enumerate(positions):
        out |= ((cell >> old_pos) & 1) << new_pos
    return out


def preimage_cellmask(target_mask: int, source_arity: int,
                      positions: tuple[int, ...]) -> int:
    out = 0
    for cell in range(1 << source_arity):
        if (target_mask >> project_cell(cell, positions)) & 1:
            out |= 1 << cell
    return out


def fiber_masks(source_arity: int,
                positions: tuple[int, ...]) -> list[int]:
    fibers = [0] * (1 << len(positions))
    for cell in range(1 << source_arity):
        fibers[project_cell(cell, positions)] |= 1 << cell
    return fibers


def project_support(support: int, source_arity: int,
                    positions: tuple[int, ...]) -> int:
    out = 0
    for cell in range(1 << source_arity):
        if (support >> cell) & 1:
            out |= 1 << project_cell(cell, positions)
    return out


@dataclass(frozen=True)
class Clause:
    arity: int
    forbidden: int = 0
    positive: tuple[int, ...] = ()
    is_false: bool = False


def normalize(c: Clause) -> Clause:
    if c.is_false:
        return Clause(c.arity, is_false=True)

    n_cells = 1 << c.arity
    universe = (1 << n_cells) - 1
    forbidden = c.forbidden & universe
    allowed = universe & ~forbidden
    if allowed == 0:
        return Clause(c.arity, is_false=True)

    hs: list[int] = []
    for h in c.positive:
        h &= allowed
        if h == 0:
            return Clause(c.arity, is_false=True)
        if h == allowed:  # implied by nonempty support validity
            continue
        hs.append(h)

    # Inclusion-minimal antichain is the canonical positive family.
    unique = sorted(set(hs), key=lambda x: (x.bit_count(), x))
    minimal: list[int] = []
    for h in unique:
        if not any((g & h) == g for g in minimal):
            minimal.append(h)

    return Clause(c.arity, forbidden, tuple(sorted(minimal)))


def conjunction(a: Clause, b: Clause) -> Clause:
    assert a.arity == b.arity
    if a.is_false or b.is_false:
        return Clause(a.arity, is_false=True)
    return normalize(Clause(
        a.arity,
        a.forbidden | b.forbidden,
        a.positive + b.positive,
    ))


def pullback(c: Clause, source_arity: int,
             positions: tuple[int, ...]) -> Clause:
    if c.is_false:
        return Clause(source_arity, is_false=True)
    return normalize(Clause(
        source_arity,
        preimage_cellmask(c.forbidden, source_arity, positions),
        tuple(preimage_cellmask(h, source_arity, positions)
              for h in c.positive),
    ))


def existential_project(c: Clause,
                        positions: tuple[int, ...]) -> Clause:
    if c.is_false:
        return Clause(len(positions), is_false=True)

    fibers = fiber_masks(c.arity, positions)
    forbidden = 0
    positive = [0] * len(c.positive)

    for coarse, fiber in enumerate(fibers):
        allowed_fiber = fiber & ~c.forbidden
        if allowed_fiber == 0:
            forbidden |= 1 << coarse
        for j, h in enumerate(c.positive):
            if allowed_fiber & h:
                positive[j] |= 1 << coarse

    return normalize(Clause(len(positions), forbidden, tuple(positive)))


def universal_project(c: Clause,
                      positions: tuple[int, ...]) -> Clause:
    if c.is_false:
        return Clause(len(positions), is_false=True)

    fibers = fiber_masks(c.arity, positions)
    forbidden = 0
    positive = [0] * len(c.positive)

    for coarse, fiber in enumerate(fibers):
        if fiber & c.forbidden:
            forbidden |= 1 << coarse
        for j, h in enumerate(c.positive):
            if fiber & ~h == 0:
                positive[j] |= 1 << coarse

    return normalize(Clause(len(positions), forbidden, tuple(positive)))


def holds(c: Clause, support: int) -> bool:
    if c.is_false:
        return False
    return not (support & c.forbidden) and all(
        support & h for h in c.positive
    )


def cpre_clause(step: Clause, winning: Clause,
                d: int = 1, e: int = 1) -> Clause:
    full_arity = 2 * d + e
    next_positions = tuple(range(d + e, full_arity))
    partial_positions = tuple(range(d + e))
    state_positions = tuple(range(d))

    full = conjunction(
        step,
        pullback(winning, full_arity, next_positions),
    )
    after_system = existential_project(full, partial_positions)
    return universal_project(after_system, state_positions)


def all_types(arity: int) -> range:
    n_cells = 1 << arity
    return range(1, 1 << n_cells)


def explicit_cpre(step: Clause, winning_types: set[int],
                  d: int = 1, e: int = 1) -> set[int]:
    """Brute-force type-game semantics, independent of clause projection."""
    full_arity = 2 * d + e
    state_positions = tuple(range(d))
    partial_positions = tuple(range(d + e))
    next_positions = tuple(range(d + e, full_arity))

    partial_by_state: dict[int, list[int]] = {}
    for partial in all_types(d + e):
        state = project_support(partial, d + e, state_positions)
        partial_by_state.setdefault(state, []).append(partial)

    full_by_partial: dict[int, list[int]] = {}
    for full in all_types(full_arity):
        partial = project_support(full, full_arity, partial_positions)
        full_by_partial.setdefault(partial, []).append(full)

    result: set[int] = set()
    for state in all_types(d):
        good = True
        for partial in partial_by_state[state]:
            exists_system_response = any(
                holds(step, full)
                and project_support(full, full_arity, next_positions)
                    in winning_types
                for full in full_by_partial[partial]
            )
            if not exists_system_response:
                good = False
                break
        if good:
            result.add(state)

    return result


def clause_type_set(c: Clause) -> set[int]:
    return {s for s in all_types(c.arity) if holds(c, s)}


def random_clause(rng: random.Random, arity: int,
                  max_positive: int) -> Clause:
    n_cells = 1 << arity
    forbidden = rng.randrange(1 << n_cells)
    positive = tuple(
        rng.randrange(1 << n_cells)
        for _ in range(rng.randrange(max_positive + 1))
    )
    return normalize(Clause(arity, forbidden, positive))


def self_test(seed: int = 42, trials: int = 200) -> None:
    rng = random.Random(seed)

    for _ in range(trials):
        step = random_clause(rng, arity=3, max_positive=3)
        safe = random_clause(rng, arity=1, max_positive=2)

        winning = normalize(Clause(arity=1))  # top
        winning_types = set(all_types(1))

        for _iteration in range(10):
            symbolic_cpre = cpre_clause(step, winning)
            explicit = explicit_cpre(step, winning_types)
            assert clause_type_set(symbolic_cpre) == explicit

            next_winning = conjunction(safe, symbolic_cpre)
            next_types = clause_type_set(safe) & explicit
            assert clause_type_set(next_winning) == next_types

            if next_winning == winning and next_types == winning_types:
                break
            winning, winning_types = next_winning, next_types


def main() -> None:
    self_test()
    print("ABA safety clause-game differential checks passed")
    print("  200 random d=e=1 games")
    print("  3 state types / 15 partial types / 255 full types")
    print("  every CPre and fixed-point approximant compared")


if __name__ == "__main__":
    main()

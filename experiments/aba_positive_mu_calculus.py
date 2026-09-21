#!/usr/bin/env python3
"""Differential checks for the positive ABA fixed-point calculus.

Inside the permanent zero-safe arena, upward support properties are represented
by canonical positive antichains.  This script compares:

- reachability: mu X. Target OR CPre(X)
- Buchi:       nu Z. mu Y. (F AND CPre(Z)) OR CPre(Y)

against explicit complete-type game semantics for d=e=1:

  3 state types, 15 state/input types, 255 full types.

Every fixed-point approximant is compared, not just the final answer.
"""

from __future__ import annotations

import random

from aba_safety_clause_game import (
    Clause,
    normalize,
    conjunction,
    cpre_clause,
    explicit_cpre,
    clause_type_set,
    random_clause,
)
from aba_safety_bekic import zero_fixed_point


def join_same_arena(a: Clause, b: Clause) -> Clause:
    """Semantic OR of two upward clauses sharing the same forbidden arena."""
    if a.is_false:
        return b
    if b.is_false:
        return a
    assert a.arity == b.arity
    assert a.forbidden == b.forbidden

    # Empty positive family = top inside the fixed allowed arena.
    if not a.positive or not b.positive:
        return normalize(Clause(a.arity, forbidden=a.forbidden))

    return normalize(
        Clause(
            a.arity,
            forbidden=a.forbidden,
            positive=tuple(
                h | k for h in a.positive for k in b.positive
            ),
        )
    )


def fixed_arena(step: Clause, safe: Clause, d: int, e: int) -> Clause:
    return normalize(
        Clause(d, forbidden=zero_fixed_point(step, safe, d, e))
    )


def cpre_in_arena(
    step: Clause, arena: Clause, target: Clause, d: int, e: int
) -> Clause:
    return conjunction(arena, cpre_clause(step, target, d, e))


def reachability_symbolic(
    step: Clause,
    arena: Clause,
    target: Clause,
    d: int,
    e: int,
) -> tuple[Clause, list[Clause]]:
    x = Clause(d, is_false=True)
    history: list[Clause] = []

    for _ in range(1000):
        nxt = join_same_arena(
            target,
            cpre_in_arena(step, arena, x, d, e),
        )
        history.append(nxt)
        if nxt == x:
            return x, history
        x = nxt

    raise RuntimeError("reachability fixed point did not converge")


def reachability_explicit(
    step: Clause,
    arena: Clause,
    target: Clause,
    d: int,
    e: int,
) -> tuple[set[int], list[set[int]]]:
    arena_types = clause_type_set(arena)
    target_types = clause_type_set(target)
    x: set[int] = set()
    history: list[set[int]] = []

    for _ in range(1000):
        nxt = target_types | (
            explicit_cpre(step, x, d, e) & arena_types
        )
        history.append(set(nxt))
        if nxt == x:
            return x, history
        x = nxt

    raise RuntimeError("explicit reachability fixed point did not converge")


def buchi_symbolic(
    step: Clause,
    arena: Clause,
    target: Clause,
    d: int,
    e: int,
) -> tuple[Clause, list[Clause], list[list[Clause]]]:
    z = arena
    outer_history: list[Clause] = []
    nested_history: list[list[Clause]] = []

    for _ in range(1000):
        y = Clause(d, is_false=True)
        inner_history: list[Clause] = []

        for _ in range(1000):
            term1 = conjunction(
                target,
                cpre_in_arena(step, arena, z, d, e),
            )
            term2 = cpre_in_arena(step, arena, y, d, e)
            nxt = join_same_arena(term1, term2)
            inner_history.append(nxt)
            if nxt == y:
                y = nxt
                break
            y = nxt
        else:
            raise RuntimeError("inner Buchi fixed point did not converge")

        outer_history.append(y)
        nested_history.append(inner_history)
        if y == z:
            return z, outer_history, nested_history
        z = y

    raise RuntimeError("outer Buchi fixed point did not converge")


def buchi_explicit(
    step: Clause,
    arena: Clause,
    target: Clause,
    d: int,
    e: int,
) -> tuple[set[int], list[set[int]], list[list[set[int]]]]:
    arena_types = clause_type_set(arena)
    target_types = clause_type_set(target)
    z = set(arena_types)
    outer_history: list[set[int]] = []
    nested_history: list[list[set[int]]] = []

    for _ in range(1000):
        y: set[int] = set()
        inner_history: list[set[int]] = []

        for _ in range(1000):
            cp_z = explicit_cpre(step, z, d, e) & arena_types
            cp_y = explicit_cpre(step, y, d, e) & arena_types
            nxt = (target_types & cp_z) | cp_y
            inner_history.append(set(nxt))
            if nxt == y:
                y = nxt
                break
            y = nxt
        else:
            raise RuntimeError("explicit inner Buchi fixed point did not converge")

        outer_history.append(set(y))
        nested_history.append(inner_history)
        if y == z:
            return z, outer_history, nested_history
        z = y

    raise RuntimeError("explicit outer Buchi fixed point did not converge")


def random_upward_target(
    rng: random.Random, arena: Clause, d: int
) -> Clause:
    if arena.is_false:
        return Clause(d, is_false=True)

    n_cells = 1 << d
    positive = tuple(
        rng.randrange(1 << n_cells)
        for _ in range(rng.randrange(4))
    )
    return normalize(
        Clause(d, forbidden=arena.forbidden, positive=positive)
    )


def self_test(seed: int = 20260811, trials: int = 5000) -> None:
    rng = random.Random(seed)
    d = e = 1

    for _ in range(trials):
        step = random_clause(rng, arity=3, max_positive=4)
        safe = random_clause(rng, arity=1, max_positive=2)
        arena = fixed_arena(step, safe, d, e)
        target = random_upward_target(rng, arena, d)

        # Reachability: compare every least-fixed-point approximant.
        sr, sh = reachability_symbolic(step, arena, target, d, e)
        er, eh = reachability_explicit(step, arena, target, d, e)
        assert clause_type_set(sr) == er
        assert len(sh) == len(eh)
        for symbolic, explicit in zip(sh, eh):
            assert clause_type_set(symbolic) == explicit

        # Buchi: compare every outer and every nested inner approximant.
        sb, soh, snh = buchi_symbolic(step, arena, target, d, e)
        eb, eoh, enh = buchi_explicit(step, arena, target, d, e)
        assert clause_type_set(sb) == eb
        assert len(soh) == len(eoh)
        assert len(snh) == len(enh)

        for symbolic, explicit in zip(soh, eoh):
            assert clause_type_set(symbolic) == explicit

        for symbolic_inner, explicit_inner in zip(snh, enh):
            assert len(symbolic_inner) == len(explicit_inner)
            for symbolic, explicit in zip(symbolic_inner, explicit_inner):
                assert clause_type_set(symbolic) == explicit


def main() -> None:
    self_test()
    print("ABA positive fixed-point calculus checks passed")
    print("  5000 random d=e=1 games")
    print("  reachability: every mu approximant compared")
    print("  Buchi: every nu approximant and nested mu approximant compared")
    print("  explicit oracle: 3 / 15 / 255 complete ABA types")


if __name__ == "__main__":
    main()

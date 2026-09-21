#!/usr/bin/env python3
"""Semantic regression suite for the Tau-independent OrbitSynthesis kernel.

The tests are intentionally theorem-shaped:

1. Quackenbush quasi-primal counterexample:
   semi-primal-style local filtering finds `{00,10,11}`, while the exact
   quasi-primal internal-isomorphism solver has no nonempty feasible domain.

2. Three-element discriminator algebra (demi-semi-primal):
   for random equality-pattern/equivariant safety relations, the orbit/stabilizer
   greatest fixed point agrees with the exact full internal-isomorphism solver.

No Tau source, executable, parser, or license is used.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis import FiniteAlgebra, FiniteSafetyGame  # noqa: E402


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def quackenbush_u(x: int) -> int:
    return {0: 1, 1: 0, 2: 1}[x]


def quackenbush_game() -> FiniteSafetyGame:
    algebra = FiniteAlgebra.from_callables(
        (0, 1, 2),
        {
            "discriminator": (3, discriminator),
            "u": (1, quackenbush_u),
        },
    )

    safe = {
        ((0, 0), (0,), (0, 0)),
        ((0, 0), (1,), (0, 1)),
        ((0, 0), (1,), (1, 0)),
        ((0, 0), (2,), (0, 0)),
        ((0, 1), (0,), (0, 1)),
        ((0, 1), (1,), (1, 1)),
        ((1, 0), (0,), (0, 0)),
        ((1, 0), (1,), (1, 0)),
        ((1, 0), (2,), (1, 1)),
        ((1, 1), (0,), (0, 1)),
        ((1, 1), (0,), (1, 0)),
        ((1, 1), (1,), (1, 1)),
        ((1, 1), (2,), (0, 0)),
    }
    return FiniteSafetyGame(algebra, state_arity=2, input_arity=1, safe_relation=safe)


def check_quackenbush_separation() -> None:
    game = quackenbush_game()

    semi = game.solve_semi_primal()
    expected_naive = frozenset({(0, 0), (1, 0), (1, 1)})
    assert semi.winning_states == expected_naive

    maximal_quasi = game.maximal_quasi_primal_domains()
    assert maximal_quasi == (frozenset(),)

    assert game.solve_quasi_primal_from_initial({(0, 0)}) is None

    print("quasi-primal strict-separation regression passed")


def equality_pattern(values: tuple[int, ...]) -> tuple[int, ...]:
    """Canonical equality pattern, e.g. (2,2,0) -> (0,0,1)."""
    labels: dict[int, int] = {}
    nxt = 0
    result: list[int] = []
    for value in values:
        if value not in labels:
            labels[value] = nxt
            nxt += 1
        result.append(labels[value])
    return tuple(result)


def discriminator_algebra() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        (0, 1, 2),
        {"discriminator": (3, discriminator)},
    )


def random_equality_pattern_game(
    rng: random.Random,
    algebra: FiniteAlgebra,
) -> FiniteSafetyGame:
    states = tuple(product(algebra.values, repeat=1))
    inputs = tuple(product(algebra.values, repeat=1))
    triples = [(state, inp, output) for state in states for inp in inputs for output in states]
    patterns = {
        equality_pattern(state + inp + output)
        for state, inp, output in triples
    }
    selected = {pattern for pattern in patterns if rng.random() < 0.5}
    safe = {
        (state, inp, output)
        for state, inp, output in triples
        if equality_pattern(state + inp + output) in selected
    }
    return FiniteSafetyGame(
        algebra,
        state_arity=1,
        input_arity=1,
        safe_relation=safe,
    )


def check_demi_equals_full_groupoid(seed: int = 20260811, trials: int = 30) -> None:
    rng = random.Random(seed)
    algebra = discriminator_algebra()

    # Every nonempty subset is a subalgebra and every carrier permutation is
    # an automorphism in the pure discriminator algebra.
    assert len(algebra.subalgebras()) == 7
    assert len(algebra.automorphisms()) == 6

    for _ in range(trials):
        game = random_equality_pattern_game(rng, algebra)
        demi = game.solve_demi_semi_primal()
        maximal_quasi = game.maximal_quasi_primal_domains()
        assert maximal_quasi == (demi.winning_states,)

        quasi_strategy = game.quasi_primal_strategy_for_domain(
            demi.winning_states
        )
        assert quasi_strategy is not None

    print(
        f"demi-semi-primal orbit/full-groupoid agreement passed: {trials} games"
    )


def check_ordinary_contains_stronger_modes() -> None:
    game = quackenbush_game()
    ordinary = game.solve_ordinary().winning_states
    semi = game.solve_semi_primal().winning_states
    assert semi <= ordinary
    print("controller-semantics monotonicity smoke check passed")


def main() -> None:
    check_quackenbush_separation()
    check_demi_equals_full_groupoid()
    check_ordinary_contains_stronger_modes()
    print("standalone OrbitSynthesis kernel: all semantic smoke tests passed")


if __name__ == "__main__":
    main()

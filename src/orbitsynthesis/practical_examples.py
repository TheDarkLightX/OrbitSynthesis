"""Small deterministic models for the practical clone-synthesis pipeline."""

from __future__ import annotations

from itertools import product

from .finite_algebra import FiniteAlgebra
from .practical import game_to_model
from .safety import FiniteSafetyGame

Q = (0, 1, 2)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def unary_u(x: int) -> int:
    return (1, 0, 1)[x]


def quackenbush_q() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {"d": (3, discriminator), "u": (1, unary_u)},
    )


def discriminator_policy_model() -> dict[str, object]:
    """A positive instance whose exact controller is one `d` node."""

    algebra = quackenbush_q()
    relation = {
        ((state,), (left, right), (discriminator(state, left, right),))
        for state, left, right in product(Q, repeat=3)
    }
    game = FiniteSafetyGame(algebra, 1, 2, relation)
    return game_to_model(
        game,
        game.states,
        name="q-one-discriminator-policy",
    )


def coupling_counterexample_model() -> dict[str, object]:
    """The 13-transition internal-isomorphism coupling separation."""

    algebra = quackenbush_q()
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
    game = FiniteSafetyGame(algebra, 2, 1, safe)
    return game_to_model(
        game,
        ((0, 0),),
        name="q-internal-isomorphism-coupling-counterexample",
    )


def example_model(name: str) -> dict[str, object]:
    if name == "discriminator":
        return discriminator_policy_model()
    if name == "coupling":
        return coupling_counterexample_model()
    raise ValueError(f"unknown practical example {name!r}")

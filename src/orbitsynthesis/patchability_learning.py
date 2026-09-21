"""Counterexample-guided learning of minimum patchability parameter sets.

The learner does not enumerate every nonextendable partial symmetry up front.
It alternates between:

1. a minimum hitting-set candidate for the currently learned edge clutter; and
2. the exact pointed-extension verifier.

A failed verifier call yields a new obstruction edge.  A successful candidate
is globally minimum: every truly patchable set must hit the learned edges, and
the accepted candidate is minimum for those edges.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

from .finite_algebra import FiniteAlgebra, InternalIsomorphism
from .patchability import (
    ExtensionFailure,
    PatchabilityResult,
    first_extension_failure,
)
from .patchability_residual import (
    build_patchability_residual_automaton,
    minimal_clutter,
    shortest_accepting_parameters,
)

Value = Hashable


@dataclass(frozen=True)
class PatchabilityLearningStep:
    """One candidate-verification round and its resulting learned clutter."""

    candidate: frozenset[Value]
    failure: ExtensionFailure | None
    learned_edge: frozenset[Value] | None
    minimal_edges_after: tuple[frozenset[Value], ...]
    residual_state_count_before: int


@dataclass(frozen=True)
class PatchabilityLearningResult:
    """Verifier-certified minimum parameter set and its complete learning trace."""

    solution: PatchabilityResult
    steps: tuple[PatchabilityLearningStep, ...]
    learned_minimal_edges: tuple[frozenset[Value], ...]
    internal_isomorphism_count: int


def _fixed_set(partial: InternalIsomorphism) -> frozenset[Value]:
    mapping = partial.mapping
    return frozenset(
        value
        for value in partial.domain & partial.codomain
        if mapping.get(value) == value
    )


def learn_minimum_patchability_parameters(
    algebra: FiniteAlgebra,
    *,
    nontrivial_only: bool = True,
    max_parameters: int | None = None,
) -> PatchabilityLearningResult:
    """Learn a globally minimum patchability set from verifier counterexamples.

    Each failed candidate fixes every value in the returned partial
    isomorphism's domain, so it misses the edge ``carrier - Fix(phi)``.  Because
    the candidate hits every previously learned edge, this counterexample makes
    strict semantic progress after clutter minimization.
    """

    carrier = tuple(algebra.values)
    carrier_set = frozenset(carrier)
    all_isos = algebra.internal_isomorphisms()
    learned: tuple[frozenset[Value], ...] = ()
    steps: list[PatchabilityLearningStep] = []

    while True:
        automaton = build_patchability_residual_automaton(carrier, learned)
        candidate_tuple = shortest_accepting_parameters(automaton)
        candidate = frozenset(candidate_tuple)

        if max_parameters is not None and len(candidate) > max_parameters:
            raise ValueError(
                "no patchability set can exist within max_parameters: "
                "the learned obstruction lower bound already exceeds it"
            )

        failure = first_extension_failure(
            algebra,
            candidate,
            nontrivial_only=nontrivial_only,
            internal_isomorphisms=all_isos,
        )
        if failure is None:
            steps.append(
                PatchabilityLearningStep(
                    candidate=candidate,
                    failure=None,
                    learned_edge=None,
                    minimal_edges_after=learned,
                    residual_state_count_before=len(automaton.states),
                )
            )
            return PatchabilityLearningResult(
                solution=PatchabilityResult(
                    size=len(candidate),
                    parameters=candidate,
                ),
                steps=tuple(steps),
                learned_minimal_edges=learned,
                internal_isomorphism_count=len(all_isos),
            )

        edge = carrier_set - _fixed_set(failure.isomorphism)
        if not edge:
            raise AssertionError(
                "a nonextendable partial isomorphism cannot fix the whole carrier"
            )
        updated = minimal_clutter(carrier, (*learned, edge))
        if updated == learned:
            raise AssertionError(
                "the verifier repeated an obstruction already implied by the "
                "learned clutter, although the candidate hits every learned edge"
            )

        steps.append(
            PatchabilityLearningStep(
                candidate=candidate,
                failure=failure,
                learned_edge=edge,
                minimal_edges_after=updated,
                residual_state_count_before=len(automaton.states),
            )
        )
        learned = updated

        # Every failed round learns a genuinely new unpointed obstruction.
        if len(steps) > len(all_isos):
            raise AssertionError("finite counterexample learning failed to progress")

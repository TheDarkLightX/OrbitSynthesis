"""Closure-system presentation of future patchability equivalence.

For an inclusion-minimal obstruction clutter H on carrier V, let U_C be the
edges not hit by a named parameter set C.  The canonical maximal raw
representative of C's future-equivalence class is

    P(C) = V - union(U_C).

P is a closure operator.  Its closed sets are anti-isomorphic to the residual
automaton states, and C is patchable exactly when P(C)=V.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable

from .patchability_residual import (
    PatchabilityResidualAutomaton,
    build_patchability_residual_automaton,
)

Value = Hashable


def closure_from_residual_state(
    automaton: PatchabilityResidualAutomaton,
    state: int,
) -> frozenset[Value]:
    """Return the unique largest parameter set with the given future behavior."""

    if state not in automaton.states:
        raise ValueError("unknown residual state")
    unhit_union: set[Value] = set()
    for index, edge in enumerate(automaton.edges):
        if state & (1 << index):
            unhit_union.update(edge)
    return frozenset(value for value in automaton.carrier if value not in unhit_union)


@dataclass(frozen=True)
class PatchabilityClosureSystem:
    """Exact closure lattice dual to one minimal residual automaton."""

    automaton: PatchabilityResidualAutomaton
    closed_states: tuple[frozenset[Value], ...]

    @property
    def carrier(self) -> tuple[Value, ...]:
        return self.automaton.carrier

    @property
    def edges(self) -> tuple[frozenset[Value], ...]:
        return self.automaton.edges

    def closure(self, parameters: Iterable[Value]) -> frozenset[Value]:
        """Canonical maximal representative of a raw parameter set."""

        state = self.automaton.run(parameters)
        return closure_from_residual_state(self.automaton, state)

    def state_of_closed(self, closed: Iterable[Value]) -> int:
        """Translate a certified closed representative back to a residual state."""

        value = frozenset(closed)
        if value not in self.closed_states:
            raise ValueError("parameter set is not closed in this system")
        state = self.automaton.run(value)
        if closure_from_residual_state(self.automaton, state) != value:
            raise AssertionError("closed-state round trip failed")
        return state

    def transition(
        self,
        closed: Iterable[Value],
        parameter: Value,
    ) -> frozenset[Value]:
        """Add one parameter directly on the closed quotient."""

        state = self.state_of_closed(closed)
        successor = self.automaton.transition(state, parameter)
        return closure_from_residual_state(self.automaton, successor)

    def is_patchable(self, parameters: Iterable[Value]) -> bool:
        """Patchability is exactly closure to the full carrier."""

        return self.closure(parameters) == frozenset(self.carrier)


def build_patchability_closure_system(
    carrier: Iterable[Value],
    edges: Iterable[Iterable[Value]],
) -> PatchabilityClosureSystem:
    """Build the canonical future-patchability closure lattice."""

    automaton = build_patchability_residual_automaton(carrier, edges)
    closed_states = tuple(
        closure_from_residual_state(automaton, state)
        for state in automaton.states
    )
    if len(set(closed_states)) != len(closed_states):
        raise AssertionError(
            "distinct minimal residual states must have distinct maximal representatives"
        )
    return PatchabilityClosureSystem(
        automaton=automaton,
        closed_states=closed_states,
    )


def patchability_closure(
    carrier: Iterable[Value],
    edges: Iterable[Iterable[Value]],
    parameters: Iterable[Value],
) -> frozenset[Value]:
    """Convenience wrapper for the canonical patchability closure P(C)."""

    return build_patchability_closure_system(carrier, edges).closure(parameters)

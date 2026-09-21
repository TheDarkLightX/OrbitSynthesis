"""Canonical residual automata for parameter-patchability hypergraphs.

Given the inclusion-minimal obstruction clutter H on a finite carrier V, a
parameter set C is patchable exactly when it hits every edge of H.  The exact
future-behavior state after naming C is the subfamily of edges still unhit.

The resulting automaton is deterministic, commutative, idempotent, and minimal
for the language of parameter sequences that restore patchability.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Hashable, Iterable

Value = Hashable


@dataclass(frozen=True)
class PatchabilityResidualAutomaton:
    """Minimal residual automaton of a finite obstruction clutter.

    ``states`` are bitmasks over ``edges``. A set bit means the obstruction is
    still unhit. ``parameter_classes`` groups carrier values that induce the
    same transition from every state; the matching ``parameter_masks`` record
    which edges one representative hits.
    """

    carrier: tuple[Value, ...]
    edges: tuple[frozenset[Value], ...]
    parameter_classes: tuple[tuple[Value, ...], ...]
    parameter_masks: tuple[int, ...]
    value_masks: tuple[int, ...]
    states: tuple[int, ...]
    transition_state_indices: tuple[tuple[int, ...], ...]
    initial_state: int
    accepting_state: int

    def transition(self, state: int, parameter: Value) -> int:
        """Apply one named parameter to a residual state mask."""

        if state not in self.states:
            raise ValueError("unknown residual state")
        try:
            index = self.carrier.index(parameter)
        except ValueError as error:
            raise ValueError("parameter outside carrier") from error
        return state & ~self.value_masks[index]

    def run(self, parameters: Iterable[Value], *, start: int | None = None) -> int:
        """Apply a finite parameter sequence; order and repetition are harmless."""

        state = self.initial_state if start is None else start
        if state not in self.states:
            raise ValueError("unknown residual state")
        for parameter in parameters:
            state = self.transition(state, parameter)
        return state

    def accepts(self, parameters: Iterable[Value], *, start: int | None = None) -> bool:
        """Whether the supplied extension reaches the patchable state."""

        return self.run(parameters, start=start) == self.accepting_state


def minimal_clutter(
    carrier: Iterable[Value],
    edges: Iterable[Iterable[Value]],
) -> tuple[frozenset[Value], ...]:
    """Validate a finite hypergraph and remove duplicate/redundant supersets."""

    values = tuple(carrier)
    if not values:
        raise ValueError("carrier must be nonempty")
    if len(set(values)) != len(values):
        raise ValueError("carrier values must be distinct")
    position = {value: index for index, value in enumerate(values)}
    carrier_set = frozenset(values)

    normalized: set[frozenset[Value]] = set()
    for raw in edges:
        edge = frozenset(raw)
        if not edge:
            raise ValueError("obstruction edges must be nonempty")
        if not edge <= carrier_set:
            raise ValueError("obstruction edge leaves carrier")
        normalized.add(edge)

    ordered = sorted(
        normalized,
        key=lambda edge: (
            len(edge),
            tuple(sorted(position[value] for value in edge)),
        ),
    )
    minimal: list[frozenset[Value]] = []
    for edge in ordered:
        if not any(old <= edge for old in minimal):
            minimal.append(edge)
    return tuple(minimal)


def incidence_masks(
    carrier: Iterable[Value],
    edges: Iterable[Iterable[Value]],
) -> tuple[int, ...]:
    """Return, in carrier order, the edge-incidence mask of each parameter."""

    values = tuple(carrier)
    clutter = tuple(frozenset(edge) for edge in edges)
    return tuple(
        sum(1 << index for index, edge in enumerate(clutter) if value in edge)
        for value in values
    )


def residual_mask(
    carrier: Iterable[Value],
    edges: Iterable[Iterable[Value]],
    parameters: Iterable[Value],
) -> int:
    """Bitmask of minimal obstruction edges not yet hit by ``parameters``."""

    values = tuple(carrier)
    clutter = minimal_clutter(values, edges)
    chosen = frozenset(parameters)
    if not chosen <= frozenset(values):
        raise ValueError("parameter outside carrier")
    return sum(
        1 << index
        for index, edge in enumerate(clutter)
        if not chosen & edge
    )


def build_patchability_residual_automaton(
    carrier: Iterable[Value],
    edges: Iterable[Iterable[Value]],
) -> PatchabilityResidualAutomaton:
    """Build the canonical minimal residual automaton of a patchability clutter."""

    values = tuple(carrier)
    clutter = minimal_clutter(values, edges)
    masks_by_value = incidence_masks(values, clutter)

    classes_by_mask: dict[int, list[Value]] = {}
    mask_order: list[int] = []
    for value, mask in zip(values, masks_by_value, strict=True):
        if mask not in classes_by_mask:
            classes_by_mask[mask] = []
            mask_order.append(mask)
        classes_by_mask[mask].append(value)

    parameter_classes = tuple(tuple(classes_by_mask[mask]) for mask in mask_order)
    parameter_masks = tuple(mask_order)

    initial = (1 << len(clutter)) - 1
    queue: deque[int] = deque((initial,))
    states: list[int] = [initial]
    seen = {initial}
    while queue:
        state = queue.popleft()
        for mask in parameter_masks:
            successor = state & ~mask
            if successor not in seen:
                seen.add(successor)
                states.append(successor)
                queue.append(successor)

    state_index = {state: index for index, state in enumerate(states)}
    transition_state_indices = tuple(
        tuple(state_index[state & ~mask] for mask in parameter_masks)
        for state in states
    )
    if 0 not in state_index:
        raise AssertionError("naming the whole carrier must hit every nonempty edge")

    return PatchabilityResidualAutomaton(
        carrier=values,
        edges=clutter,
        parameter_classes=parameter_classes,
        parameter_masks=parameter_masks,
        value_masks=masks_by_value,
        states=tuple(states),
        transition_state_indices=transition_state_indices,
        initial_state=initial,
        accepting_state=0,
    )


def distinguishing_extension(
    automaton: PatchabilityResidualAutomaton,
    left: int,
    right: int,
) -> tuple[tuple[Value, ...], bool, bool]:
    """Construct a future parameter set distinguishing two residual states."""

    if left == right:
        raise ValueError("equal states need no distinguishing extension")
    if left not in automaton.states or right not in automaton.states:
        raise ValueError("unknown residual state")

    difference = left & ~right
    swapped = False
    if difference == 0:
        difference = right & ~left
        swapped = True
    edge_index = (difference & -difference).bit_length() - 1
    edge = automaton.edges[edge_index]
    extension = tuple(value for value in automaton.carrier if value not in edge)

    left_accepts = automaton.accepts(extension, start=left)
    right_accepts = automaton.accepts(extension, start=right)
    expected = (True, False) if swapped else (False, True)
    if (left_accepts, right_accepts) != expected:
        raise AssertionError("clutter distinguisher failed")
    return extension, left_accepts, right_accepts


def shortest_state_parameters(
    automaton: PatchabilityResidualAutomaton,
    target: int,
) -> tuple[Value, ...]:
    """Return a carrier-order canonical shortest sequence reaching ``target``."""

    if target not in automaton.states:
        raise ValueError("unknown residual state")
    representatives = tuple(values[0] for values in automaton.parameter_classes)
    queue: deque[int] = deque((automaton.initial_state,))
    path: dict[int, tuple[Value, ...]] = {automaton.initial_state: ()}
    while queue:
        state = queue.popleft()
        if state == target:
            return path[state]
        for value, mask in zip(representatives, automaton.parameter_masks, strict=True):
            successor = state & ~mask
            if successor not in path:
                path[successor] = path[state] + (value,)
                queue.append(successor)
    raise AssertionError("every listed state should be reachable")


def shortest_accepting_parameters(
    automaton: PatchabilityResidualAutomaton,
) -> tuple[Value, ...]:
    """Return a shortest representative parameter sequence reaching acceptance."""

    return shortest_state_parameters(automaton, automaton.accepting_state)

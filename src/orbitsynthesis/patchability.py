"""Exact small-carrier oracles for partial-symmetry patchability.

The routines are structural: they do not assert that an input algebra is
quasi-primal. When quasi-primality is known independently, the extension
property computed here is exactly the demi-semi-primal condition used by
OrbitSynthesis' original-signature term-controller theorems.

The key factorization is:

1. enumerate nonextendable unpointed internal isomorphisms once;
2. turn each one into the hyperedge ``carrier - Fix(phi)``;
3. minimize the edge family to a clutter;
4. solve the resulting parameter problem either by direct combinations or by
   the exact residual automaton over unhit minimal edges.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism
from .patchability_residual import (
    PatchabilityResidualAutomaton,
    build_patchability_residual_automaton,
    shortest_accepting_parameters,
)

Value = Hashable


@dataclass(frozen=True)
class PatchabilityResult:
    """Minimum named set restoring the internal-isomorphism extension property."""

    size: int
    parameters: frozenset[Value]


@dataclass(frozen=True)
class ExtensionFailure:
    """One pointed internal isomorphism with no pointed global extension."""

    parameters: frozenset[Value]
    isomorphism: InternalIsomorphism


@dataclass(frozen=True)
class ObstructionHypergraph:
    """Compressed parameter-killing edges derived from nonextendable isomorphisms."""

    raw_nonextendable_count: int
    distinct_edges: tuple[frozenset[Value], ...]
    minimal_edges: tuple[frozenset[Value], ...]


def _fixes(
    isomorphism: InternalIsomorphism,
    parameters: frozenset[Value],
) -> bool:
    mapping = isomorphism.mapping
    return all(mapping.get(value) == value for value in parameters)


def _eligible_pointed_iso(
    isomorphism: InternalIsomorphism,
    parameters: frozenset[Value],
    *,
    nontrivial_only: bool,
) -> bool:
    if nontrivial_only and len(isomorphism.domain) <= 1:
        return False
    if not parameters <= isomorphism.domain:
        return False
    if not parameters <= isomorphism.codomain:
        return False
    return _fixes(isomorphism, parameters)


def _extends(
    partial: InternalIsomorphism,
    automorphism: InternalIsomorphism,
) -> bool:
    partial_mapping = partial.mapping
    auto_mapping = automorphism.mapping
    return all(auto_mapping[value] == image for value, image in partial_mapping.items())


def _automorphisms(
    algebra: FiniteAlgebra,
    all_isos: Sequence[InternalIsomorphism],
) -> tuple[InternalIsomorphism, ...]:
    carrier = frozenset(algebra.values)
    return tuple(
        iso
        for iso in all_isos
        if iso.domain == carrier and iso.codomain == carrier
    )


def nonextendable_internal_isomorphisms(
    algebra: FiniteAlgebra,
    *,
    nontrivial_only: bool = True,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> tuple[InternalIsomorphism, ...]:
    """Enumerate unpointed internal isomorphisms with no global extension."""

    all_isos = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    automorphisms = _automorphisms(algebra, all_isos)

    return tuple(
        partial
        for partial in all_isos
        if (not nontrivial_only or len(partial.domain) > 1)
        and not any(_extends(partial, automorphism) for automorphism in automorphisms)
    )


def _fixed_set(partial: InternalIsomorphism) -> frozenset[Value]:
    mapping = partial.mapping
    return frozenset(
        value
        for value in partial.domain & partial.codomain
        if mapping.get(value) == value
    )


def _minimal_edges(
    edges: Iterable[frozenset[Value]],
) -> tuple[frozenset[Value], ...]:
    ordered = sorted(set(edges), key=lambda edge: (len(edge), tuple(map(repr, edge))))
    minimal: list[frozenset[Value]] = []
    for edge in ordered:
        if not any(old <= edge for old in minimal):
            minimal.append(edge)
    return tuple(minimal)


def patchability_obstruction_hypergraph(
    algebra: FiniteAlgebra,
    *,
    nontrivial_only: bool = True,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> ObstructionHypergraph:
    """Compile nonextendable internal symmetries to parameter hitting-set edges.

    For a nonextendable ``phi``, naming ``C`` leaves that obstruction eligible
    iff every named value belongs to ``Fix(phi)``. Hence ``C`` kills ``phi``
    exactly when it intersects ``carrier - Fix(phi)``.
    """

    carrier = frozenset(algebra.values)
    nonextendable = nonextendable_internal_isomorphisms(
        algebra,
        nontrivial_only=nontrivial_only,
        internal_isomorphisms=internal_isomorphisms,
    )
    distinct = tuple(
        sorted(
            {carrier - _fixed_set(partial) for partial in nonextendable},
            key=lambda edge: (len(edge), tuple(sorted(map(repr, edge)))),
        )
    )
    if any(not edge for edge in distinct):
        raise AssertionError("a nonextendable internal isomorphism cannot fix the whole carrier")

    return ObstructionHypergraph(
        raw_nonextendable_count=len(nonextendable),
        distinct_edges=distinct,
        minimal_edges=_minimal_edges(distinct),
    )


def patchability_residual_automaton(
    algebra: FiniteAlgebra,
    *,
    nontrivial_only: bool = True,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> PatchabilityResidualAutomaton:
    """Compile one algebra directly to its exact future-patchability automaton."""

    all_isos = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    hypergraph = patchability_obstruction_hypergraph(
        algebra,
        nontrivial_only=nontrivial_only,
        internal_isomorphisms=all_isos,
    )
    return build_patchability_residual_automaton(
        algebra.values,
        hypergraph.minimal_edges,
    )


def hits_all(
    parameters: Iterable[Value],
    edges: Iterable[frozenset[Value]],
) -> bool:
    chosen = frozenset(parameters)
    return all(bool(chosen & edge) for edge in edges)


def first_extension_failure(
    algebra: FiniteAlgebra,
    parameters: Iterable[Value] = (),
    *,
    nontrivial_only: bool = True,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> ExtensionFailure | None:
    """Return one pointed internal isomorphism that has no pointed extension."""

    fixed = frozenset(parameters)
    carrier = frozenset(algebra.values)
    if not fixed <= carrier:
        raise ValueError("parameter outside carrier")

    all_isos = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    automorphisms = tuple(
        iso
        for iso in _automorphisms(algebra, all_isos)
        if _fixes(iso, fixed)
    )

    for partial in all_isos:
        if not _eligible_pointed_iso(
            partial,
            fixed,
            nontrivial_only=nontrivial_only,
        ):
            continue
        if not any(_extends(partial, automorphism) for automorphism in automorphisms):
            return ExtensionFailure(parameters=fixed, isomorphism=partial)

    return None


def has_pointed_extension_property(
    algebra: FiniteAlgebra,
    parameters: Iterable[Value] = (),
    *,
    nontrivial_only: bool = True,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> bool:
    """Whether every eligible pointed internal isomorphism extends globally."""

    return first_extension_failure(
        algebra,
        parameters,
        nontrivial_only=nontrivial_only,
        internal_isomorphisms=internal_isomorphisms,
    ) is None


def parameter_patchability_number(
    algebra: FiniteAlgebra,
    *,
    nontrivial_only: bool = True,
    max_parameters: int | None = None,
) -> PatchabilityResult:
    """Reference minimum search by carrier-subset cardinality."""

    all_isos = algebra.internal_isomorphisms()
    hypergraph = patchability_obstruction_hypergraph(
        algebra,
        nontrivial_only=nontrivial_only,
        internal_isomorphisms=all_isos,
    )
    carrier = tuple(algebra.values)
    limit = len(carrier) if max_parameters is None else min(max_parameters, len(carrier))

    for size in range(limit + 1):
        for chosen in combinations(carrier, size):
            if hits_all(chosen, hypergraph.minimal_edges):
                return PatchabilityResult(
                    size=size,
                    parameters=frozenset(chosen),
                )

    raise ValueError(
        "no hitting parameter set found within max_parameters; increase the search limit"
    )


def parameter_patchability_number_via_residual(
    algebra: FiniteAlgebra,
    *,
    nontrivial_only: bool = True,
    max_parameters: int | None = None,
) -> PatchabilityResult:
    """Find a minimum parameter set by BFS on the minimal residual automaton.

    Equal-incidence carrier values are searched once as one parameter role, and
    future-equivalent partial parameter sets share one residual state.
    """

    automaton = patchability_residual_automaton(
        algebra,
        nontrivial_only=nontrivial_only,
    )
    parameters = shortest_accepting_parameters(automaton)
    if max_parameters is not None and len(parameters) > max_parameters:
        raise ValueError(
            "no hitting parameter set found within max_parameters; increase the search limit"
        )
    return PatchabilityResult(
        size=len(parameters),
        parameters=frozenset(parameters),
    )

"""Principal-equation no-greatest witnesses for quasi-primal algebras.

The generic groupoid-invariant converse in ``greatest_region_boundary`` can be
made equation-defined.  Its unsafe tuples all carry a tagged listing of a
nontrivial source or target subalgebra, so their first two coordinates are
distinct.  Let ``p`` be the first projection and define ``g`` to be ``p`` on
safe tuples and the second projection on unsafe tuples.  Groupoid invariance
makes this branch equivariant; both branches are projections and hence remain
inside the generated subalgebra.  Quasi-primal interpolation therefore makes
``g`` a term, and the safe relation is exactly ``p=g``.

The caller is responsible for the quasi-primality premise.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Hashable, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism
from .greatest_region_boundary import (
    NoGreatestRegionWitness,
    build_no_greatest_region_witness,
    relation_is_internal_groupoid_invariant,
)
from .safety import FiniteSafetyGame

Value = Hashable
State = tuple[Value, ...]
Input = tuple[Value, ...]
Output = tuple[Value, ...]
Transition = tuple[State, Input, Output]


@dataclass(frozen=True)
class PrincipalNoGreatestRegionWitness:
    """One-equation strengthening of the generic converse witness."""

    structural: NoGreatestRegionWitness
    safe_relation: frozenset[Transition]
    first_projection_index: int = 0
    alternate_projection_index: int = 1

    @property
    def state_arity(self) -> int:
        return self.structural.state_arity

    @property
    def left_domain(self) -> frozenset[State]:
        return self.structural.left_domain

    @property
    def right_domain(self) -> frozenset[State]:
        return self.structural.right_domain

    def game(self, algebra: FiniteAlgebra) -> FiniteSafetyGame:
        return FiniteSafetyGame(
            algebra,
            self.state_arity,
            1,
            self.safe_relation,
        )

    def flattened(self) -> frozenset[tuple[Value, ...]]:
        return frozenset(
            state + input_value + output
            for state, input_value, output in self.safe_relation
        )

    def projection_value(self, flattened_transition: Sequence[Value]) -> Value:
        return flattened_transition[self.first_projection_index]

    def separator_value(self, flattened_transition: Sequence[Value]) -> Value:
        flattened = tuple(flattened_transition)
        if flattened in self.flattened():
            return flattened[self.first_projection_index]
        return flattened[self.alternate_projection_index]


@dataclass(frozen=True)
class PrincipalEquationAudit:
    """Finite replay of the strengthened converse and term separator."""

    left_feasible: bool
    right_feasible: bool
    union_feasible: bool
    relation_groupoid_invariant: bool
    exact_equation: bool
    unsafe_tags_distinct: bool
    separator_subalgebra_preserving: bool
    separator_groupoid_equivariant: bool
    rows_checked: int

    @property
    def passes(self) -> bool:
        return (
            self.left_feasible
            and self.right_feasible
            and not self.union_feasible
            and self.relation_groupoid_invariant
            and self.exact_equation
            and self.unsafe_tags_distinct
            and self.separator_subalgebra_preserving
            and self.separator_groupoid_equivariant
        )


def build_principal_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> PrincipalNoGreatestRegionWitness | None:
    """Build a no-greatest witness whose safety relation is one equation."""

    structural = build_no_greatest_region_witness(
        algebra,
        internal_isomorphisms=internal_isomorphisms,
    )
    if structural is None:
        return None

    critical = structural.critical_observation_orbit
    dead = (
        structural.source_dead_observation_orbit
        | structural.target_dead_observation_orbit
    )
    critical_transitions = frozenset(
        transition
        for transition in structural.safe_relation
        if transition[0] + transition[1] in critical
    )

    states = tuple(product(algebra.values, repeat=structural.state_arity))
    inputs = tuple((value,) for value in algebra.values)
    safe: set[Transition] = set(critical_transitions)

    # Outside the critical and dead observation orbits, every output is safe.
    # This broad relation is easier to define by one equality and preserves the
    # same critical coupling and dead-state obstruction.
    for state in states:
        for input_value in inputs:
            observation = state + input_value
            if observation in critical or observation in dead:
                continue
            for output in states:
                safe.add((state, input_value, output))

    return PrincipalNoGreatestRegionWitness(
        structural=structural,
        safe_relation=frozenset(safe),
    )


def audit_principal_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    witness: PrincipalNoGreatestRegionWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> PrincipalEquationAudit:
    """Exhaustively check the equation separator on the finite algebra."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    game = witness.game(algebra)
    left_feasible = game.quasi_primal_domain_feasible(witness.left_domain)
    right_feasible = game.quasi_primal_domain_feasible(witness.right_domain)
    union_feasible = game.quasi_primal_domain_feasible(
        witness.left_domain | witness.right_domain
    )

    safe_flattened = witness.flattened()
    total_arity = 2 * witness.state_arity + 1
    rows = tuple(product(algebra.values, repeat=total_arity))

    exact_equation = True
    unsafe_tags_distinct = True
    subalgebra_preserving = True
    groupoid_equivariant = True

    for flattened in rows:
        projection = witness.projection_value(flattened)
        separator = witness.separator_value(flattened)
        is_safe = flattened in safe_flattened
        if (projection == separator) != is_safe:
            exact_equation = False
        if not is_safe and flattened[0] == flattened[1]:
            unsafe_tags_distinct = False
        if separator not in algebra.generated_subalgebra(flattened):
            subalgebra_preserving = False

        for isomorphism in all_isomorphisms:
            if not isomorphism.applies_to(flattened):
                continue
            mapped = isomorphism.map_tuple(flattened)
            if separator not in isomorphism.domain:
                groupoid_equivariant = False
                continue
            if witness.separator_value(mapped) != isomorphism.map_value(separator):
                groupoid_equivariant = False

    structural_proxy = NoGreatestRegionWitness(
        isomorphism=witness.structural.isomorphism,
        state_arity=witness.state_arity,
        source_state=witness.structural.source_state,
        target_state=witness.structural.target_state,
        source_output_zero=witness.structural.source_output_zero,
        source_output_one=witness.structural.source_output_one,
        target_output_zero=witness.structural.target_output_zero,
        target_output_one=witness.structural.target_output_one,
        critical_input=witness.structural.critical_input,
        source_dead_input=witness.structural.source_dead_input,
        target_dead_input=witness.structural.target_dead_input,
        left_domain=witness.left_domain,
        right_domain=witness.right_domain,
        critical_observation_orbit=witness.structural.critical_observation_orbit,
        source_dead_observation_orbit=(
            witness.structural.source_dead_observation_orbit
        ),
        target_dead_observation_orbit=(
            witness.structural.target_dead_observation_orbit
        ),
        safe_relation=witness.safe_relation,
    )

    return PrincipalEquationAudit(
        left_feasible=left_feasible,
        right_feasible=right_feasible,
        union_feasible=union_feasible,
        relation_groupoid_invariant=relation_is_internal_groupoid_invariant(
            algebra,
            structural_proxy,
            internal_isomorphisms=all_isomorphisms,
        ),
        exact_equation=exact_equation,
        unsafe_tags_distinct=unsafe_tags_distinct,
        separator_subalgebra_preserving=subalgebra_preserving,
        separator_groupoid_equivariant=groupoid_equivariant,
        rows_checked=len(rows),
    )

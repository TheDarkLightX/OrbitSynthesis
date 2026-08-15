"""Generator-compressed converse witnesses for greatest-region safety.

The original generic converse lists every element of the source subalgebra in
its state prefix. That list is stronger than necessary. An internal
isomorphism is determined by its action on any generating tuple, so a minimum
nonempty generating tuple pins the same partial symmetry with state arity
``d(B)+2`` instead of ``|B|+2``.

For the one-equation strengthening, compression removes the globally fixed
pair of unequal prefix coordinates used by the historical separator. The
replacement chooses one alternate projection per unsafe internal-groupoid
orbit. Every unsafe tuple is nonconstant; injective transport preserves the
chosen inequality, and using a constant projection index on each orbit keeps
the separator equivariant.

The caller is responsible for the quasi-primality premise.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import combinations, product
from typing import Hashable, Iterable, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism
from .greatest_region_boundary import (
    NoGreatestRegionAudit,
    NoGreatestRegionWitness,
    audit_no_greatest_region_witness,
    internal_isomorphism_extends,
    relation_is_internal_groupoid_invariant,
)
from .patchability import nonextendable_internal_isomorphisms
from .safety import FiniteSafetyGame

Value = Hashable
State = tuple[Value, ...]
Observation = tuple[Value, ...]
Output = tuple[Value, ...]
Transition = tuple[State, tuple[Value, ...], Output]
FlattenedTransition = tuple[Value, ...]


def _stable(values: Iterable[object]) -> tuple:
    return tuple(sorted(values, key=repr))


def minimum_generating_tuple(
    algebra: FiniteAlgebra,
    subalgebra: Iterable[Value],
) -> tuple[Value, ...]:
    """Return the first minimum-cardinality nonempty generating tuple.

    The ordering is inherited from ``algebra.values``. The standalone kernel
    does not currently define empty-generated subalgebras in signatures with
    nullary operations; this routine therefore minimizes over nonempty tuples.
    That is sufficient here because the obstructing internal isomorphism has a
    nontrivial source subalgebra.
    """

    target = frozenset(subalgebra)
    if not algebra.is_subalgebra(target):
        raise ValueError("minimum_generating_tuple requires a nonempty subalgebra")
    ordered = tuple(value for value in algebra.values if value in target)
    for size in range(1, len(ordered) + 1):
        for chosen in combinations(ordered, size):
            if algebra.generated_subalgebra(chosen) == target:
                return chosen
    raise AssertionError("the full finite subalgebra failed to generate itself")


def generator_minimal_maximal_nonextendable_internal_isomorphism(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> InternalIsomorphism | None:
    """Choose a graph-maximal obstruction with minimum source generating rank."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    nonextendable = tuple(
        nonextendable_internal_isomorphisms(
            algebra,
            nontrivial_only=True,
            internal_isomorphisms=all_isomorphisms,
        )
    )
    maximal = tuple(
        partial
        for partial in nonextendable
        if not any(
            other != partial
            and internal_isomorphism_extends(other, partial)
            for other in nonextendable
        )
    )
    if not maximal:
        return None
    return min(
        maximal,
        key=lambda partial: (
            len(minimum_generating_tuple(algebra, partial.domain)),
            -len(partial.domain),
            repr(_stable(partial.mapping_items)),
        ),
    )


def _groupoid_orbit(
    seed: Sequence[Value],
    internal_isomorphisms: Sequence[InternalIsomorphism],
) -> frozenset[tuple[Value, ...]]:
    reached = {tuple(seed)}
    stack = [tuple(seed)]
    while stack:
        item = stack.pop()
        for isomorphism in internal_isomorphisms:
            if not isomorphism.applies_to(item):
                continue
            mapped = isomorphism.map_tuple(item)
            if mapped not in reached:
                reached.add(mapped)
                stack.append(mapped)
    return frozenset(reached)


def build_generator_compressed_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> NoGreatestRegionWitness | None:
    """Build the generic converse with a minimum source generating tuple."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    partial = generator_minimal_maximal_nonextendable_internal_isomorphism(
        algebra,
        internal_isomorphisms=all_isomorphisms,
    )
    if partial is None:
        return None

    carrier_order = {value: index for index, value in enumerate(algebra.values)}
    source_values = tuple(
        sorted(partial.domain, key=lambda value: carrier_order[value])
    )
    if len(source_values) < 2:
        raise AssertionError("the converse requires a nontrivial source subalgebra")
    first, second = source_values[:2]
    generators = minimum_generating_tuple(algebra, partial.domain)

    source_output_zero = generators + (first, first)
    source_output_one = generators + (first, second)
    source_state = generators + (second, first)

    target_output_zero = partial.map_tuple(source_output_zero)
    target_output_one = partial.map_tuple(source_output_one)
    target_state = partial.map_tuple(source_state)

    source_dead_input = next(
        value for value in algebra.values if value not in partial.domain
    )
    target_dead_input = next(
        value for value in algebra.values if value not in partial.codomain
    )
    critical_input = first
    target_critical_input = partial.map_value(first)

    state_arity = len(source_state)
    source_observation = source_state + (critical_input,)
    target_observation = target_state + (target_critical_input,)

    critical_observations = _groupoid_orbit(
        source_observation,
        all_isomorphisms,
    )
    if target_observation not in critical_observations:
        raise AssertionError(
            "the chosen internal isomorphism did not transport the critical observation"
        )

    source_dead_observations = _groupoid_orbit(
        source_output_one + (source_dead_input,),
        all_isomorphisms,
    )
    target_dead_observations = _groupoid_orbit(
        target_output_zero + (target_dead_input,),
        all_isomorphisms,
    )
    dead_observations = source_dead_observations | target_dead_observations
    if critical_observations & dead_observations:
        raise AssertionError(
            "critical and dead observation orbits unexpectedly intersect"
        )

    critical_transitions: set[FlattenedTransition] = set()
    for output in (source_output_zero, source_output_one):
        critical_transitions.update(
            _groupoid_orbit(
                source_observation + output,
                all_isomorphisms,
            )
        )

    states = tuple(product(algebra.values, repeat=state_arity))
    safe: set[Transition] = set()
    for state in states:
        for input_value in algebra.values:
            observation = state + (input_value,)
            if observation in dead_observations:
                continue
            if observation in critical_observations:
                continue
            safe.add((state, (input_value,), state))

    for flattened in critical_transitions:
        state = tuple(flattened[:state_arity])
        input_value = (flattened[state_arity],)
        output = tuple(flattened[state_arity + 1 :])
        safe.add((state, input_value, output))

    left_domain = frozenset((source_state, source_output_zero))
    right_domain = frozenset((target_state, target_output_one))
    protected_states = left_domain | right_domain
    if any(
        observation[:state_arity] in protected_states
        for observation in dead_observations
    ):
        raise AssertionError(
            "a dead orbit reached a state needed by a one-sided winning domain"
        )

    return NoGreatestRegionWitness(
        isomorphism=partial,
        state_arity=state_arity,
        source_state=source_state,
        target_state=target_state,
        source_output_zero=source_output_zero,
        source_output_one=source_output_one,
        target_output_zero=target_output_zero,
        target_output_one=target_output_one,
        critical_input=critical_input,
        source_dead_input=source_dead_input,
        target_dead_input=target_dead_input,
        left_domain=left_domain,
        right_domain=right_domain,
        critical_observation_orbit=critical_observations,
        source_dead_observation_orbit=source_dead_observations,
        target_dead_observation_orbit=target_dead_observations,
        safe_relation=frozenset(safe),
    )


@dataclass(frozen=True)
class GeneratorCompressionAudit:
    """Structural replay of the generator-compressed converse."""

    structural_audit: NoGreatestRegionAudit
    generator_prefix: tuple[Value, ...]
    generator_prefix_is_minimum: bool
    generator_prefix_generates_source: bool
    target_prefix_is_transport: bool
    state_arity_matches: bool
    baseline_listing_arity: int

    @property
    def strictly_compressed(self) -> bool:
        return self.state_arity < self.baseline_listing_arity

    @property
    def state_arity(self) -> int:
        return len(self.generator_prefix) + 2

    @property
    def passes(self) -> bool:
        return (
            self.structural_audit.passes
            and self.generator_prefix_is_minimum
            and self.generator_prefix_generates_source
            and self.target_prefix_is_transport
            and self.state_arity_matches
        )


def audit_generator_compressed_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    witness: NoGreatestRegionWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> GeneratorCompressionAudit:
    """Verify the compressed prefix and replay the generic converse."""

    generators = witness.source_state[:-2]
    minimum = minimum_generating_tuple(algebra, witness.isomorphism.domain)
    return GeneratorCompressionAudit(
        structural_audit=audit_no_greatest_region_witness(
            algebra,
            witness,
            internal_isomorphisms=internal_isomorphisms,
        ),
        generator_prefix=generators,
        generator_prefix_is_minimum=(generators == minimum),
        generator_prefix_generates_source=(
            algebra.generated_subalgebra(generators)
            == witness.isomorphism.domain
        ),
        target_prefix_is_transport=(
            witness.target_state[:-2]
            == witness.isomorphism.map_tuple(generators)
        ),
        state_arity_matches=(witness.state_arity == len(generators) + 2),
        baseline_listing_arity=len(witness.isomorphism.domain) + 2,
    )


@dataclass(frozen=True)
class GeneratorCompressedPrincipalWitness:
    """One-equation witness with an orbitwise projection separator."""

    structural: NoGreatestRegionWitness
    safe_relation: frozenset[Transition]
    projection_index: int
    unsafe_projection_items: tuple[tuple[FlattenedTransition, int], ...]

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

    @cached_property
    def flattened(self) -> frozenset[FlattenedTransition]:
        return frozenset(
            state + input_value + output
            for state, input_value, output in self.safe_relation
        )

    @cached_property
    def unsafe_projection_map(self) -> dict[FlattenedTransition, int]:
        return dict(self.unsafe_projection_items)

    def separator_projection_index(
        self,
        flattened_transition: Sequence[Value],
    ) -> int:
        flattened = tuple(flattened_transition)
        if flattened in self.flattened:
            return self.projection_index
        try:
            return self.unsafe_projection_map[flattened]
        except KeyError as error:
            raise ValueError(
                "flattened tuple lies outside the principal certificate"
            ) from error

    def projection_value(self, flattened_transition: Sequence[Value]) -> Value:
        return flattened_transition[self.projection_index]

    def separator_value(self, flattened_transition: Sequence[Value]) -> Value:
        flattened = tuple(flattened_transition)
        return flattened[self.separator_projection_index(flattened)]


def build_generator_compressed_principal_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> GeneratorCompressedPrincipalWitness | None:
    """Build the compressed converse as one equation ``p=g``.

    The separator uses the first generator coordinate on safe tuples. On each
    unsafe internal-groupoid orbit it uses the least coordinate projection that
    differs from that first coordinate. No unsafe tuple is constant: critical
    observations contain distinct tags, while dead observations contain either
    distinct tags or an input outside the tagged subalgebra.
    """

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    structural = build_generator_compressed_no_greatest_region_witness(
        algebra,
        internal_isomorphisms=all_isomorphisms,
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
    safe: set[Transition] = set(critical_transitions)
    for state in states:
        for input_value in algebra.values:
            observation = state + (input_value,)
            if observation in critical or observation in dead:
                continue
            for output in states:
                safe.add((state, (input_value,), output))

    safe_relation = frozenset(safe)
    safe_flattened = frozenset(
        state + input_value + output
        for state, input_value, output in safe_relation
    )
    total_arity = 2 * structural.state_arity + 1
    all_rows = frozenset(product(algebra.values, repeat=total_arity))
    unsafe = all_rows - safe_flattened

    projection_index = 0
    projection_by_row: dict[FlattenedTransition, int] = {}
    while len(projection_by_row) < len(unsafe):
        seed = min(unsafe - set(projection_by_row), key=repr)
        orbit = _groupoid_orbit(seed, all_isomorphisms)
        if not orbit <= unsafe:
            raise AssertionError(
                "an unsafe groupoid orbit crossed into the safe relation"
            )
        alternate = next(
            (
                index
                for index, value in enumerate(seed)
                if value != seed[projection_index]
            ),
            None,
        )
        if alternate is None:
            raise AssertionError(
                "the compressed converse produced a constant unsafe tuple"
            )
        for row in orbit:
            if row[alternate] == row[projection_index]:
                raise AssertionError(
                    "injective transport lost the separating projection"
                )
            projection_by_row[row] = alternate

    return GeneratorCompressedPrincipalWitness(
        structural=structural,
        safe_relation=safe_relation,
        projection_index=projection_index,
        unsafe_projection_items=tuple(
            sorted(projection_by_row.items(), key=lambda item: repr(item[0]))
        ),
    )


@dataclass(frozen=True)
class GeneratorCompressedPrincipalAudit:
    """Exhaustive finite audit of the orbitwise separator."""

    left_feasible: bool
    right_feasible: bool
    union_feasible: bool
    relation_groupoid_invariant: bool
    projection_map_total: bool
    projection_orbit_invariant: bool
    exact_equation: bool
    unsafe_projection_distinct: bool
    separator_subalgebra_preserving: bool
    separator_groupoid_equivariant: bool
    rows_checked: int
    unsafe_rows: int
    unsafe_orbits: int
    single_global_alternate_exists: bool

    @property
    def passes(self) -> bool:
        return (
            self.left_feasible
            and self.right_feasible
            and not self.union_feasible
            and self.relation_groupoid_invariant
            and self.projection_map_total
            and self.projection_orbit_invariant
            and self.exact_equation
            and self.unsafe_projection_distinct
            and self.separator_subalgebra_preserving
            and self.separator_groupoid_equivariant
        )


def audit_generator_compressed_principal_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    witness: GeneratorCompressedPrincipalWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> GeneratorCompressedPrincipalAudit:
    """Replay the one-equation separator and both winning sides."""

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

    total_arity = 2 * witness.state_arity + 1
    rows = tuple(product(algebra.values, repeat=total_arity))
    safe_flattened = witness.flattened
    unsafe = frozenset(rows) - safe_flattened
    projection_map = witness.unsafe_projection_map

    projection_map_total = set(projection_map) == set(unsafe)
    exact_equation = True
    unsafe_projection_distinct = True
    subalgebra_preserving = True
    groupoid_equivariant = True
    projection_orbit_invariant = True
    seen_unsafe: set[FlattenedTransition] = set()
    unsafe_orbits = 0

    for row in rows:
        safe = row in safe_flattened
        separator = witness.separator_value(row)
        projection = witness.projection_value(row)
        if (projection == separator) != safe:
            exact_equation = False
        if not safe:
            index = projection_map.get(row)
            if index is None or row[index] == row[witness.projection_index]:
                unsafe_projection_distinct = False
        if separator not in algebra.generated_subalgebra(row):
            subalgebra_preserving = False

        for isomorphism in all_isomorphisms:
            if not isomorphism.applies_to(row):
                continue
            mapped = isomorphism.map_tuple(row)
            mapped_safe = mapped in safe_flattened
            if mapped_safe != safe:
                projection_orbit_invariant = False
            if not safe and projection_map.get(mapped) != projection_map.get(row):
                projection_orbit_invariant = False
            if separator not in isomorphism.domain:
                groupoid_equivariant = False
                continue
            if witness.separator_value(mapped) != isomorphism.map_value(separator):
                groupoid_equivariant = False

    for seed in sorted(unsafe, key=repr):
        if seed in seen_unsafe:
            continue
        component = _groupoid_orbit(seed, all_isomorphisms)
        seen_unsafe.update(component)
        unsafe_orbits += 1

    single_global_alternate_exists = any(
        all(row[index] != row[witness.projection_index] for row in unsafe)
        for index in range(total_arity)
        if index != witness.projection_index
    )

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

    return GeneratorCompressedPrincipalAudit(
        left_feasible=left_feasible,
        right_feasible=right_feasible,
        union_feasible=union_feasible,
        relation_groupoid_invariant=relation_is_internal_groupoid_invariant(
            algebra,
            structural_proxy,
            internal_isomorphisms=all_isomorphisms,
        ),
        projection_map_total=projection_map_total,
        projection_orbit_invariant=projection_orbit_invariant,
        exact_equation=exact_equation,
        unsafe_projection_distinct=unsafe_projection_distinct,
        separator_subalgebra_preserving=subalgebra_preserving,
        separator_groupoid_equivariant=groupoid_equivariant,
        rows_checked=len(rows),
        unsafe_rows=len(unsafe),
        unsafe_orbits=unsafe_orbits,
        single_global_alternate_exists=single_global_alternate_exists,
    )

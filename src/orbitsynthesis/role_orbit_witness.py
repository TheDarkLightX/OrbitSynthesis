"""Role-orbit compressed greatest-region converse witnesses.

The generator-compressed construction uses one common generating tuple and two
explicit tag coordinates. A sharper invariant is available. The three
source-side roles only need to be generating tuples in distinct diagonal
``Aut(B)`` orbits. If ``rho_3(B)`` is the least arity carrying three such
orbits, the generic no-greatest witness has state arity ``rho_3(B)``.

The one-equation separator no longer needs to be a projection. On each unsafe
internal-groupoid orbit it chooses any generated value different from the
first projection and transports that value equivariantly. Path independence
holds because the flattened tuple generates its subalgebra.

The caller is responsible for the quasi-primality premise.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import product
from typing import Hashable, Iterable, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism
from .generator_compressed_witness import minimum_generating_tuple
from .greatest_region_boundary import (
    NoGreatestRegionAudit,
    NoGreatestRegionWitness,
    audit_no_greatest_region_witness,
    internal_isomorphism_extends,
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


def _internal_automorphisms(
    subalgebra: frozenset[Value],
    internal_isomorphisms: Sequence[InternalIsomorphism],
) -> tuple[InternalIsomorphism, ...]:
    return tuple(
        isomorphism
        for isomorphism in internal_isomorphisms
        if isomorphism.domain == subalgebra
        and isomorphism.codomain == subalgebra
    )


def _tuple_orbit(
    values: Sequence[Value],
    automorphisms: Sequence[InternalIsomorphism],
) -> frozenset[tuple[Value, ...]]:
    return frozenset(
        automorphism.map_tuple(values)
        for automorphism in automorphisms
    )


def generating_tuple_orbit_representatives(
    algebra: FiniteAlgebra,
    subalgebra: Iterable[Value],
    arity: int,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> tuple[tuple[Value, ...], ...]:
    """Return canonical representatives of generating tuples modulo Aut(B)."""

    target = frozenset(subalgebra)
    if arity <= 0:
        raise ValueError("generating-tuple arity must be positive")
    if not algebra.is_subalgebra(target):
        raise ValueError("target must be a nonempty subalgebra")

    isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    automorphisms = _internal_automorphisms(target, isomorphisms)
    ordered = tuple(value for value in algebra.values if value in target)
    generating = tuple(
        values
        for values in product(ordered, repeat=arity)
        if algebra.generated_subalgebra(values) == target
    )

    seen: set[tuple[Value, ...]] = set()
    representatives: list[tuple[Value, ...]] = []
    for values in generating:
        if values in seen:
            continue
        orbit = _tuple_orbit(values, automorphisms)
        seen.update(orbit)
        representatives.append(min(orbit, key=repr))
    return tuple(sorted(representatives, key=repr))


@dataclass(frozen=True)
class ThreeRoleOrbitBasis:
    """Three orbit-separated tuples that individually generate one subalgebra."""

    subalgebra: frozenset[Value]
    arity: int
    critical_state: State
    left_output: Output
    right_output: Output
    orbit_representatives: tuple[tuple[Value, ...], ...]


def three_role_orbit_basis(
    algebra: FiniteAlgebra,
    subalgebra: Iterable[Value],
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
    max_arity: int | None = None,
) -> ThreeRoleOrbitBasis:
    """Compute the least arity with three generating-tuple automorphism orbits.

    The common-generator-plus-two-tags construction proves the search succeeds
    by ``d(B)+2``. The first three canonical orbit representatives are used as
    the critical state and the two source-side critical outputs.
    """

    target = frozenset(subalgebra)
    if not algebra.is_subalgebra(target) or len(target) < 2:
        raise ValueError("three-role compression requires a nontrivial subalgebra")
    isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    universal_upper = len(minimum_generating_tuple(algebra, target)) + 2
    upper = universal_upper if max_arity is None else max_arity
    if upper <= 0:
        raise ValueError("max_arity must be positive")

    for arity in range(1, upper + 1):
        representatives = generating_tuple_orbit_representatives(
            algebra,
            target,
            arity,
            internal_isomorphisms=isomorphisms,
        )
        if len(representatives) >= 3:
            return ThreeRoleOrbitBasis(
                subalgebra=target,
                arity=arity,
                critical_state=representatives[0],
                left_output=representatives[1],
                right_output=representatives[2],
                orbit_representatives=representatives,
            )
    raise ValueError(
        "no three-role orbit basis found within max_arity="
        f"{upper}; the universal d(B)+2 bound was not searched completely"
    )


@dataclass(frozen=True)
class RoleOrbitObstruction:
    isomorphism: InternalIsomorphism
    basis: ThreeRoleOrbitBasis


def role_orbit_minimal_maximal_nonextendable_internal_isomorphism(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> RoleOrbitObstruction | None:
    """Choose a graph-maximal obstruction of minimum three-role orbit rank."""

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

    candidates = tuple(
        RoleOrbitObstruction(
            isomorphism=partial,
            basis=three_role_orbit_basis(
                algebra,
                partial.domain,
                internal_isomorphisms=all_isomorphisms,
            ),
        )
        for partial in maximal
    )
    return min(
        candidates,
        key=lambda candidate: (
            candidate.basis.arity,
            -len(candidate.isomorphism.domain),
            repr(_stable(candidate.isomorphism.mapping_items)),
        ),
    )


def _groupoid_orbit(
    seed: Sequence[Value],
    internal_isomorphisms: Sequence[InternalIsomorphism],
) -> frozenset[tuple[Value, ...]]:
    reached = {tuple(seed)}
    stack = [tuple(seed)]
    while stack:
        values = stack.pop()
        for isomorphism in internal_isomorphisms:
            if not isomorphism.applies_to(values):
                continue
            target = isomorphism.map_tuple(values)
            if target not in reached:
                reached.add(target)
                stack.append(target)
    return frozenset(reached)


def build_role_orbit_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> NoGreatestRegionWitness | None:
    """Build the generic converse at minimum three-role orbit rank."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    obstruction = role_orbit_minimal_maximal_nonextendable_internal_isomorphism(
        algebra,
        internal_isomorphisms=all_isomorphisms,
    )
    if obstruction is None:
        return None

    partial = obstruction.isomorphism
    basis = obstruction.basis
    source_state = basis.critical_state
    source_output_zero = basis.left_output
    source_output_one = basis.right_output
    target_state = partial.map_tuple(source_state)
    target_output_zero = partial.map_tuple(source_output_zero)
    target_output_one = partial.map_tuple(source_output_one)

    carrier_order = {value: index for index, value in enumerate(algebra.values)}
    source_values = tuple(
        sorted(partial.domain, key=lambda value: carrier_order[value])
    )
    critical_input = source_values[0]
    target_critical_input = partial.map_value(critical_input)
    source_dead_input = next(
        value for value in algebra.values if value not in partial.domain
    )
    target_dead_input = next(
        value for value in algebra.values if value not in partial.codomain
    )

    state_arity = basis.arity
    source_observation = source_state + (critical_input,)
    target_observation = target_state + (target_critical_input,)
    critical_observations = _groupoid_orbit(
        source_observation,
        all_isomorphisms,
    )
    if target_observation not in critical_observations:
        raise AssertionError("the obstruction did not transport the critical observation")

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
        raise AssertionError("critical and dead observation orbits intersect")

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
            if observation in critical_observations or observation in dead_observations:
                continue
            safe.add((state, (input_value,), state))
    for flattened in critical_transitions:
        safe.add(
            (
                tuple(flattened[:state_arity]),
                (flattened[state_arity],),
                tuple(flattened[state_arity + 1 :]),
            )
        )

    left_domain = frozenset((source_state, source_output_zero))
    right_domain = frozenset((target_state, target_output_one))
    if any(
        observation[:state_arity] in left_domain | right_domain
        for observation in dead_observations
    ):
        raise AssertionError("a dead orbit reached a protected one-sided state")

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
class RoleOrbitCompressionAudit:
    structural_audit: NoGreatestRegionAudit
    role_rank: int
    generating_orbit_counts: tuple[int, ...]
    roles_generate_source: bool
    roles_pairwise_orbit_separated: bool
    rank_is_minimal: bool
    generator_tag_upper_bound: int

    @property
    def strictly_better_than_generator_tags(self) -> bool:
        return self.role_rank < self.generator_tag_upper_bound

    @property
    def passes(self) -> bool:
        return (
            self.structural_audit.passes
            and self.roles_generate_source
            and self.roles_pairwise_orbit_separated
            and self.rank_is_minimal
            and self.role_rank <= self.generator_tag_upper_bound
        )


def audit_role_orbit_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    witness: NoGreatestRegionWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> RoleOrbitCompressionAudit:
    """Replay the converse and the exact role-orbit rank certificate."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    roles = (
        witness.source_state,
        witness.source_output_zero,
        witness.source_output_one,
    )
    source = witness.isomorphism.domain
    automorphisms = _internal_automorphisms(source, all_isomorphisms)
    role_orbits = tuple(_tuple_orbit(role, automorphisms) for role in roles)
    counts = tuple(
        len(
            generating_tuple_orbit_representatives(
                algebra,
                source,
                arity,
                internal_isomorphisms=all_isomorphisms,
            )
        )
        for arity in range(1, witness.state_arity + 1)
    )
    upper = len(minimum_generating_tuple(algebra, source)) + 2
    return RoleOrbitCompressionAudit(
        structural_audit=audit_no_greatest_region_witness(
            algebra,
            witness,
            internal_isomorphisms=all_isomorphisms,
        ),
        role_rank=witness.state_arity,
        generating_orbit_counts=counts,
        roles_generate_source=all(
            algebra.generated_subalgebra(role) == source
            for role in roles
        ),
        roles_pairwise_orbit_separated=all(
            roles[right] not in role_orbits[left]
            for left in range(len(roles))
            for right in range(left + 1, len(roles))
        ),
        rank_is_minimal=(
            counts[-1] >= 3
            and all(count < 3 for count in counts[:-1])
        ),
        generator_tag_upper_bound=upper,
    )


@dataclass(frozen=True)
class RoleOrbitPrincipalWitness:
    """One-equation role-orbit witness with orbitwise generated separators."""

    structural: NoGreatestRegionWitness
    safe_relation: frozenset[Transition]
    projection_index: int
    unsafe_separator_items: tuple[tuple[FlattenedTransition, Value], ...]

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
    def unsafe_separator_map(self) -> dict[FlattenedTransition, Value]:
        return dict(self.unsafe_separator_items)

    def projection_value(self, flattened: Sequence[Value]) -> Value:
        return flattened[self.projection_index]

    def separator_value(self, flattened: Sequence[Value]) -> Value:
        row = tuple(flattened)
        if row in self.flattened:
            return row[self.projection_index]
        try:
            return self.unsafe_separator_map[row]
        except KeyError as error:
            raise ValueError("row lies outside the principal separator certificate") from error


def _separator_assignment_for_orbit(
    algebra: FiniteAlgebra,
    seed: FlattenedTransition,
    unsafe: frozenset[FlattenedTransition],
    internal_isomorphisms: Sequence[InternalIsomorphism],
    projection_index: int,
) -> dict[FlattenedTransition, Value]:
    component = _groupoid_orbit(seed, internal_isomorphisms)
    if not component <= unsafe:
        raise AssertionError("an unsafe groupoid orbit crossed the safe relation")

    candidates = tuple(
        value
        for value in _stable(algebra.generated_subalgebra(seed))
        if value != seed[projection_index]
    )
    for candidate in candidates:
        assignment: dict[FlattenedTransition, Value] = {seed: candidate}
        queue = [seed]
        inconsistent = False
        while queue and not inconsistent:
            source = queue.pop()
            source_value = assignment[source]
            for isomorphism in internal_isomorphisms:
                if not isomorphism.applies_to(source):
                    continue
                target = isomorphism.map_tuple(source)
                if target not in component:
                    continue
                if source_value not in isomorphism.domain:
                    inconsistent = True
                    break
                target_value = isomorphism.map_value(source_value)
                if target_value == target[projection_index]:
                    inconsistent = True
                    break
                previous = assignment.get(target)
                if previous is not None and previous != target_value:
                    inconsistent = True
                    break
                if previous is None:
                    assignment[target] = target_value
                    queue.append(target)
        if not inconsistent and set(assignment) == set(component):
            return assignment
    raise AssertionError("unsafe orbit has no equivariant generated separator value")


def build_role_orbit_principal_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> RoleOrbitPrincipalWitness | None:
    """Build the minimum-role-rank converse as one equation ``p=g``."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    structural = build_role_orbit_no_greatest_region_witness(
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
    separator: dict[FlattenedTransition, Value] = {}
    while len(separator) < len(unsafe):
        seed = min(unsafe - set(separator), key=repr)
        separator.update(
            _separator_assignment_for_orbit(
                algebra,
                seed,
                unsafe,
                all_isomorphisms,
                projection_index,
            )
        )

    return RoleOrbitPrincipalWitness(
        structural=structural,
        safe_relation=safe_relation,
        projection_index=projection_index,
        unsafe_separator_items=tuple(
            sorted(separator.items(), key=lambda item: repr(item[0]))
        ),
    )


@dataclass(frozen=True)
class RoleOrbitPrincipalAudit:
    compression_audit: RoleOrbitCompressionAudit
    structural_audit: NoGreatestRegionAudit
    exact_equation: bool
    separator_subalgebra_preserving: bool
    separator_groupoid_equivariant: bool
    unsafe_separator_distinct: bool
    rows_checked: int
    unsafe_rows: int
    unsafe_groupoid_orbits: int

    @property
    def passes(self) -> bool:
        return (
            self.compression_audit.passes
            and self.structural_audit.passes
            and self.exact_equation
            and self.separator_subalgebra_preserving
            and self.separator_groupoid_equivariant
            and self.unsafe_separator_distinct
        )


def audit_role_orbit_principal_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    witness: RoleOrbitPrincipalWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> RoleOrbitPrincipalAudit:
    """Exhaustively replay the role rank and one-equation separator."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    proxy = NoGreatestRegionWitness(
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
    structural_audit = audit_no_greatest_region_witness(
        algebra,
        proxy,
        internal_isomorphisms=all_isomorphisms,
    )
    compression_audit = audit_role_orbit_no_greatest_region_witness(
        algebra,
        witness.structural,
        internal_isomorphisms=all_isomorphisms,
    )

    safe = witness.flattened
    total_arity = 2 * witness.state_arity + 1
    rows = tuple(product(algebra.values, repeat=total_arity))
    exact = True
    subalgebra = True
    equivariant = True
    distinct = True
    unsafe_rows = 0
    unsafe_orbit_representatives: set[FlattenedTransition] = set()
    seen_unsafe: set[FlattenedTransition] = set()

    for row in rows:
        is_safe = row in safe
        projection = witness.projection_value(row)
        separator = witness.separator_value(row)
        if (projection == separator) != is_safe:
            exact = False
        if separator not in algebra.generated_subalgebra(row):
            subalgebra = False
        if not is_safe:
            unsafe_rows += 1
            if separator == projection:
                distinct = False
            if row not in seen_unsafe:
                component = _groupoid_orbit(row, all_isomorphisms)
                seen_unsafe.update(component)
                unsafe_orbit_representatives.add(min(component, key=repr))

        for isomorphism in all_isomorphisms:
            if not isomorphism.applies_to(row):
                continue
            mapped = isomorphism.map_tuple(row)
            if separator not in isomorphism.domain:
                equivariant = False
                continue
            if witness.separator_value(mapped) != isomorphism.map_value(separator):
                equivariant = False

    return RoleOrbitPrincipalAudit(
        compression_audit=compression_audit,
        structural_audit=structural_audit,
        exact_equation=exact,
        separator_subalgebra_preserving=subalgebra,
        separator_groupoid_equivariant=equivariant,
        unsafe_separator_distinct=distinct,
        rows_checked=len(rows),
        unsafe_rows=unsafe_rows,
        unsafe_groupoid_orbits=len(unsafe_orbit_representatives),
    )

"""Greatest-region boundary for shared-term safety over quasi-primal algebras.

For a finite quasi-primal algebra, demi-semi-primality is the positive
patchability condition: every internal isomorphism extends globally, so the
orbit/stabilizer predecessor has one greatest term-winning fixed point.

This module implements the converse obstruction for the broader and exact
category of internal-isomorphism-invariant finite safety relations.  Given one
nonextendable internal isomorphism, it constructs two term-winning domains
with no term-winning common upper bound.

The caller is responsible for the quasi-primality premise.  The construction
is exact and useful as a falsification oracle on any small finite algebra.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Hashable, Iterable, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism
from .patchability import nonextendable_internal_isomorphisms
from .safety import FiniteSafetyGame

Value = Hashable
State = tuple[Value, ...]
Observation = tuple[Value, ...]
Output = tuple[Value, ...]
Transition = tuple[State, tuple[Value, ...], Output]


def _stable(values: Iterable[object]) -> tuple:
    return tuple(sorted(values, key=repr))


def internal_isomorphism_extends(
    larger: InternalIsomorphism,
    smaller: InternalIsomorphism,
) -> bool:
    """Whether ``larger`` contains the graph of ``smaller``."""

    if not smaller.domain <= larger.domain:
        return False
    if not smaller.codomain <= larger.codomain:
        return False
    larger_mapping = larger.mapping
    return all(
        larger_mapping.get(value) == image
        for value, image in smaller.mapping_items
    )


def maximal_nonextendable_internal_isomorphism(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> InternalIsomorphism | None:
    """Choose a graph-maximal nonextendable nontrivial internal isomorphism."""

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


@dataclass(frozen=True)
class NoGreatestRegionWitness:
    """A generic converse witness extracted from one partial symmetry."""

    isomorphism: InternalIsomorphism
    state_arity: int
    source_state: State
    target_state: State
    source_output_zero: Output
    source_output_one: Output
    target_output_zero: Output
    target_output_one: Output
    critical_input: Value
    source_dead_input: Value
    target_dead_input: Value
    left_domain: frozenset[State]
    right_domain: frozenset[State]
    critical_observation_orbit: frozenset[Observation]
    source_dead_observation_orbit: frozenset[Observation]
    target_dead_observation_orbit: frozenset[Observation]
    safe_relation: frozenset[Transition]

    def game(self, algebra: FiniteAlgebra) -> FiniteSafetyGame:
        return FiniteSafetyGame(
            algebra=algebra,
            state_arity=self.state_arity,
            input_arity=1,
            safe_relation=self.safe_relation,
        )


@dataclass(frozen=True)
class NoGreatestRegionAudit:
    """Executable verification of the structural converse certificate."""

    left_feasible: bool
    right_feasible: bool
    union_feasible: bool
    groupoid_invariant: bool
    source_dead: bool
    target_dead: bool
    exact_source_outputs: bool
    exact_target_outputs: bool

    @property
    def passes(self) -> bool:
        return (
            self.left_feasible
            and self.right_feasible
            and not self.union_feasible
            and self.groupoid_invariant
            and self.source_dead
            and self.target_dead
            and self.exact_source_outputs
            and self.exact_target_outputs
        )


def build_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> NoGreatestRegionWitness | None:
    """Construct the universal two-domain obstruction from nonextendability.

    Returns ``None`` exactly when every nontrivial internal isomorphism extends
    to a global automorphism, as detected by exhaustive finite enumeration.

    The relation is closed under every internal isomorphism.  It is not claimed
    here to be definable by one equation for every quasi-primal algebra; that
    principal-equation strengthening is a separate frontier.
    """

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    partial = maximal_nonextendable_internal_isomorphism(
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

    # Listing every source element pins any isomorphism on the whole source.
    # The final two coordinates make the three distinguished source states
    # pairwise impossible to identify by an internal isomorphism.
    generators = source_values
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
        raise AssertionError("the chosen internal isomorphism did not transport the critical observation")

    source_dead_seed = source_output_one + (source_dead_input,)
    target_dead_seed = target_output_zero + (target_dead_input,)
    source_dead_observations = _groupoid_orbit(
        source_dead_seed,
        all_isomorphisms,
    )
    target_dead_observations = _groupoid_orbit(
        target_dead_seed,
        all_isomorphisms,
    )
    dead_observations = source_dead_observations | target_dead_observations

    if critical_observations & dead_observations:
        raise AssertionError("critical and dead observation orbits unexpectedly intersect")

    critical_transitions: set[tuple[Value, ...]] = set()
    for output in (source_output_zero, source_output_one):
        critical_transitions.update(
            _groupoid_orbit(
                source_observation + output,
                all_isomorphisms,
            )
        )

    states = tuple(product(algebra.values, repeat=state_arity))
    inputs = tuple((value,) for value in algebra.values)
    safe: set[Transition] = set()

    for state in states:
        for input_value in inputs:
            observation = state + input_value
            if observation in dead_observations:
                continue
            if observation in critical_observations:
                continue
            safe.add((state, input_value, state))

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
        raise AssertionError("a dead orbit reached a state needed by a one-sided winning domain")

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


def relation_is_internal_groupoid_invariant(
    algebra: FiniteAlgebra,
    witness: NoGreatestRegionWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> bool:
    """Check closure of the safe relation under every internal isomorphism."""

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    flattened = {
        state + input_value + output
        for state, input_value, output in witness.safe_relation
    }
    for transition in tuple(flattened):
        for isomorphism in all_isomorphisms:
            if isomorphism.applies_to(transition):
                if isomorphism.map_tuple(transition) not in flattened:
                    return False
    return True


def _safe_outputs(
    witness: NoGreatestRegionWitness,
    state: State,
    input_value: Value,
) -> frozenset[Output]:
    return frozenset(
        output
        for source, input_tuple, output in witness.safe_relation
        if source == state and input_tuple == (input_value,)
    )


def audit_no_greatest_region_witness(
    algebra: FiniteAlgebra,
    witness: NoGreatestRegionWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> NoGreatestRegionAudit:
    """Replay the two winning sides, their incompatible union, and invariance."""

    game = witness.game(algebra)
    left_feasible = game.quasi_primal_domain_feasible(witness.left_domain)
    right_feasible = game.quasi_primal_domain_feasible(witness.right_domain)
    union_feasible = game.quasi_primal_domain_feasible(
        witness.left_domain | witness.right_domain
    )

    target_input = witness.isomorphism.map_value(witness.critical_input)
    exact_source_outputs = _safe_outputs(
        witness,
        witness.source_state,
        witness.critical_input,
    ) == frozenset(
        (witness.source_output_zero, witness.source_output_one)
    )
    exact_target_outputs = _safe_outputs(
        witness,
        witness.target_state,
        target_input,
    ) == frozenset(
        (witness.target_output_zero, witness.target_output_one)
    )

    source_dead = not _safe_outputs(
        witness,
        witness.source_output_one,
        witness.source_dead_input,
    )
    target_dead = not _safe_outputs(
        witness,
        witness.target_output_zero,
        witness.target_dead_input,
    )

    return NoGreatestRegionAudit(
        left_feasible=left_feasible,
        right_feasible=right_feasible,
        union_feasible=union_feasible,
        groupoid_invariant=relation_is_internal_groupoid_invariant(
            algebra,
            witness,
            internal_isomorphisms=internal_isomorphisms,
        ),
        source_dead=source_dead,
        target_dead=target_dead,
        exact_source_outputs=exact_source_outputs,
        exact_target_outputs=exact_target_outputs,
    )

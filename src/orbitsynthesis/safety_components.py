"""Component certificates for fixed-domain quasi-primal safety synthesis.

``FiniteSafetyGame.quasi_primal_strategy_for_domain`` decides one fixed domain
but returns only a table or ``None``.  This module exposes the same exact
internal-groupoid decomposition as a proof-carrying backend: success returns a
total compatible strategy table; failure returns one component and a
candidate-by-candidate reason.

The caller is responsible for the quasi-primality premise.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Hashable, Iterable, Sequence

from .finite_algebra import InternalIsomorphism
from .safety import FiniteSafetyGame, Observation, Output, State

Value = Hashable


@dataclass(frozen=True)
class StrategyCandidateRejection:
    """First load-bearing reason one representative output failed."""

    candidate: Output
    reason: str
    source_observation: Observation | None = None
    target_observation: Observation | None = None
    forced_output: Output | None = None


@dataclass(frozen=True)
class StrategyComponentObstruction:
    """One internal-groupoid component with no compatible output choice."""

    representative: Observation
    observations: tuple[Observation, ...]
    locally_empty_observations: tuple[Observation, ...]
    candidate_rejections: tuple[StrategyCandidateRejection, ...]


@dataclass(frozen=True)
class QuasiPrimalDomainResult:
    """Fixed-domain strategy table or reusable component nogood."""

    feasible: bool
    strategy_items: tuple[tuple[Observation, Output], ...] = ()
    obstruction: StrategyComponentObstruction | None = None

    @property
    def strategy(self) -> dict[Observation, Output]:
        return dict(self.strategy_items)


def _stable(values):
    return tuple(sorted(values, key=repr))


def _edges(
    game: FiniteSafetyGame,
    internal_isomorphisms: Sequence[InternalIsomorphism],
) -> dict[Observation, tuple[tuple[Observation, InternalIsomorphism], ...]]:
    result: dict[Observation, list[tuple[Observation, InternalIsomorphism]]] = {
        observation: [] for observation in game.observations
    }
    arity = game.state_arity + game.input_arity
    for isomorphism in internal_isomorphisms:
        for observation in product(tuple(isomorphism.domain), repeat=arity):
            target = isomorphism.map_tuple(observation)
            result[observation].append((target, isomorphism))
    return {
        observation: tuple(outgoing)
        for observation, outgoing in result.items()
    }


def _components(
    observations: Sequence[Observation],
    edges: dict[Observation, tuple[tuple[Observation, InternalIsomorphism], ...]],
) -> tuple[tuple[Observation, ...], ...]:
    neighbors: dict[Observation, set[Observation]] = {
        observation: set() for observation in observations
    }
    for source, outgoing in edges.items():
        for target, _ in outgoing:
            neighbors[source].add(target)
            neighbors[target].add(source)

    seen: set[Observation] = set()
    result = []
    for representative in observations:
        if representative in seen:
            continue
        component: set[Observation] = set()
        stack = [representative]
        while stack:
            observation = stack.pop()
            if observation in component:
                continue
            component.add(observation)
            stack.extend(neighbors[observation] - component)
        seen.update(component)
        result.append(_stable(component))
    return tuple(result)


def _local_domains(
    game: FiniteSafetyGame,
    winning: frozenset[State],
) -> dict[Observation, frozenset[Output]]:
    domains = {}
    for observation in game.observations:
        state, input_value = game.split_observation(observation)
        generated = game.algebra.generated_subalgebra(observation)
        allowed = {
            output
            for output in game.outputs
            if all(value in generated for value in output)
        }
        if state in winning:
            allowed = {
                output
                for output in allowed
                if output in winning
                and game.is_safe(state, input_value, output)
            }
        domains[observation] = frozenset(allowed)
    return domains


def quasi_primal_domain_result(
    game: FiniteSafetyGame,
    winning_states: Iterable[State],
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> QuasiPrimalDomainResult:
    """Solve one fixed quasi-primal domain with an explicit failure core."""

    winning = frozenset(winning_states)
    isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else game.algebra.internal_isomorphisms()
    )
    domains = _local_domains(game, winning)
    edges = _edges(game, isomorphisms)
    components = _components(game.observations, edges)
    assignment: dict[Observation, Output] = {}

    for component in components:
        representative = component[0]
        empty = tuple(
            observation
            for observation in component
            if not domains[observation]
        )
        if empty:
            return QuasiPrimalDomainResult(
                feasible=False,
                obstruction=StrategyComponentObstruction(
                    representative=representative,
                    observations=component,
                    locally_empty_observations=empty,
                    candidate_rejections=(),
                ),
            )

        rejections: list[StrategyCandidateRejection] = []
        selected: dict[Observation, Output] | None = None

        for candidate in _stable(domains[representative]):
            local: dict[Observation, Output] = {representative: candidate}
            queue = [representative]
            rejection: StrategyCandidateRejection | None = None

            while queue and rejection is None:
                source = queue.pop()
                source_output = local[source]
                for target, isomorphism in edges[source]:
                    if not all(value in isomorphism.domain for value in source_output):
                        rejection = StrategyCandidateRejection(
                            candidate=candidate,
                            reason="output left internal-isomorphism domain",
                            source_observation=source,
                            target_observation=target,
                            forced_output=source_output,
                        )
                        break

                    target_output = isomorphism.map_tuple(source_output)
                    if target_output not in domains[target]:
                        rejection = StrategyCandidateRejection(
                            candidate=candidate,
                            reason="transported output violates target local domain",
                            source_observation=source,
                            target_observation=target,
                            forced_output=target_output,
                        )
                        break

                    previous = local.get(target)
                    if previous is not None:
                        if previous != target_output:
                            rejection = StrategyCandidateRejection(
                                candidate=candidate,
                                reason="inconsistent internal-isomorphism cycle",
                                source_observation=source,
                                target_observation=target,
                                forced_output=target_output,
                            )
                            break
                        continue
                    local[target] = target_output
                    queue.append(target)

            if rejection is None and set(local) != set(component):
                rejection = StrategyCandidateRejection(
                    candidate=candidate,
                    reason="directed propagation did not cover component",
                )

            if rejection is None:
                selected = local
                break
            rejections.append(rejection)

        if selected is None:
            return QuasiPrimalDomainResult(
                feasible=False,
                obstruction=StrategyComponentObstruction(
                    representative=representative,
                    observations=component,
                    locally_empty_observations=(),
                    candidate_rejections=tuple(rejections),
                ),
            )
        assignment.update(selected)

    return QuasiPrimalDomainResult(
        feasible=True,
        strategy_items=tuple(
            sorted(assignment.items(), key=lambda item: repr(item[0]))
        ),
    )


def verify_quasi_primal_domain_result(
    game: FiniteSafetyGame,
    winning_states: Iterable[State],
    result: QuasiPrimalDomainResult,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> bool:
    """Verify a successful total table without trusting the solver search."""

    if not result.feasible:
        return result.obstruction is not None

    winning = frozenset(winning_states)
    strategy = result.strategy
    if set(strategy) != set(game.observations):
        return False

    for observation, output in strategy.items():
        state, input_value = game.split_observation(observation)
        generated = game.algebra.generated_subalgebra(observation)
        if not all(value in generated for value in output):
            return False
        if state in winning:
            if output not in winning or not game.is_safe(state, input_value, output):
                return False

    isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else game.algebra.internal_isomorphisms()
    )
    for observation, output in strategy.items():
        for isomorphism in isomorphisms:
            if not isomorphism.applies_to(observation):
                continue
            if not all(value in isomorphism.domain for value in output):
                return False
            target = isomorphism.map_tuple(observation)
            if strategy[target] != isomorphism.map_tuple(output):
                return False
    return True

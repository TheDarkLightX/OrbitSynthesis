"""Reference and minimum pointed-class kernels for fixed-core synthesis."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Any, Hashable, Iterable, Mapping, Sequence
from .parameter_closure import (
    _carrier_index, eligible_core_isomorphisms, generated_at_observation, parameter_core,
)
Value = Hashable
State = tuple[Value, ...]
Output = tuple[Value, ...]
Observation = tuple[Value, ...]

@dataclass(frozen=True)
class PointedClass:
    """One class of observations under core-fixing pointed isomorphism."""

    representative: Observation
    observations: tuple[Observation, ...]
    generated_subalgebra: frozenset[Value]
    # For each observation, a complete map from representative generated
    # subalgebra values to the target generated subalgebra values.
    transport_items: tuple[tuple[Observation, tuple[tuple[Value, Value], ...]], ...]

    @property
    def transports(self) -> dict[Observation, dict[Value, Value]]:
        return {
            observation: dict(items)
            for observation, items in self.transport_items
        }

def _allowed_outputs(
    game: Any,
    core: frozenset[Value],
    winning: frozenset[State],
) -> dict[Observation, frozenset[Output]] | None:
    domains: dict[Observation, frozenset[Output]] = {}
    for observation in game.observations:
        state, input_value = game.split_observation(observation)
        generated = generated_at_observation(game.algebra, core, observation)
        allowed = {
            output
            for output in game.outputs
            if all(value in generated for value in output)
        }
        if state in winning:
            allowed = {
                output
                for output in allowed
                if output in winning and game.is_safe(state, input_value, output)
            }
        if not allowed:
            return None
        domains[observation] = frozenset(allowed)
    return domains

def parameterized_strategy_reference(
    game: Any,
    core: Iterable[Value],
    winning_states: Iterable[State],
    *,
    internal_isomorphisms: Sequence[Any] | None = None,
) -> dict[Observation, Output] | None:
    """Raw exact reference solver using all core-fixing isomorphism edges."""

    raw_core = frozenset(core)
    fixed = parameter_core(game.algebra, raw_core)
    if raw_core != fixed:
        raise ValueError("pass a closed parameter core, not a raw parameter set")
    winning = frozenset(winning_states)
    domains = _allowed_outputs(game, fixed, winning)
    if domains is None:
        return None

    isomorphisms = eligible_core_isomorphisms(
        game.algebra,
        fixed,
        internal_isomorphisms=internal_isomorphisms,
    )
    observation_set = set(game.observations)
    arity = game.state_arity + game.input_arity
    edges: dict[Observation, list[tuple[Observation, Any]]] = {
        observation: [] for observation in game.observations
    }
    for isomorphism in isomorphisms:
        domain_values = tuple(isomorphism.domain)
        for source in product(domain_values, repeat=arity):
            if source not in observation_set:
                continue
            target = isomorphism.map_tuple(source)
            if target not in observation_set:
                raise AssertionError("internal isomorphism left the observation space")
            edges[source].append((target, isomorphism))

    neighbors: dict[Observation, set[Observation]] = {
        observation: set() for observation in game.observations
    }
    for source, outgoing in edges.items():
        for target, _isomorphism in outgoing:
            neighbors[source].add(target)
            neighbors[target].add(source)

    assignment: dict[Observation, Output] = {}
    seen: set[Observation] = set()
    output_order = tuple(game.outputs)

    for representative in game.observations:
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

        solved: dict[Observation, Output] | None = None
        for candidate in output_order:
            if candidate not in domains[representative]:
                continue
            local: dict[Observation, Output] = {representative: candidate}
            queue = [representative]
            inconsistent = False
            while queue and not inconsistent:
                source = queue.pop()
                source_output = local[source]
                for target, isomorphism in edges[source]:
                    if not all(value in isomorphism.domain for value in source_output):
                        inconsistent = True
                        break
                    target_output = isomorphism.map_tuple(source_output)
                    if target_output not in domains[target]:
                        inconsistent = True
                        break
                    prior = local.get(target)
                    if prior is not None:
                        if prior != target_output:
                            inconsistent = True
                            break
                    else:
                        local[target] = target_output
                        queue.append(target)
            if not inconsistent and set(local) == component:
                solved = local
                break

        if solved is None:
            return None
        assignment.update(solved)

    if set(assignment) != observation_set:
        raise AssertionError("reference solver did not construct a total table")
    return assignment

def _mapping_key(mapping: Mapping[Value, Value], carrier: Sequence[Value]) -> tuple[tuple[int, int], ...]:
    index = _carrier_index(carrier)
    return tuple(
        (index[source], index[target])
        for source, target in sorted(mapping.items(), key=lambda item: index[item[0]])
    )

def pointed_classes(
    game: Any,
    core: Iterable[Value],
    *,
    internal_isomorphisms: Sequence[Any] | None = None,
) -> tuple[PointedClass, ...]:
    """Construct the minimum observation quotient and unique transports."""

    raw_core = frozenset(core)
    fixed = parameter_core(game.algebra, raw_core)
    if raw_core != fixed:
        raise ValueError("pass a closed parameter core")
    carrier = tuple(game.algebra.values)
    observations = tuple(game.observations)
    observation_set = set(observations)
    generated = {
        observation: generated_at_observation(game.algebra, fixed, observation)
        for observation in observations
    }
    isomorphisms = eligible_core_isomorphisms(
        game.algebra,
        fixed,
        internal_isomorphisms=internal_isomorphisms,
    )

    adjacency: dict[Observation, set[Observation]] = {
        observation: set() for observation in observations
    }
    exact_transports: dict[tuple[Observation, Observation], list[dict[Value, Value]]] = {}

    for source in observations:
        source_generated = generated[source]
        for isomorphism in isomorphisms:
            if isomorphism.domain != source_generated:
                continue
            target = isomorphism.map_tuple(source)
            if target not in observation_set:
                continue
            if isomorphism.codomain != generated[target]:
                continue
            adjacency[source].add(target)
            adjacency[target].add(source)
            exact_transports.setdefault((source, target), []).append(isomorphism.mapping)

    result: list[PointedClass] = []
    seen: set[Observation] = set()
    for representative in observations:
        if representative in seen:
            continue
        component: set[Observation] = set()
        stack = [representative]
        while stack:
            source = stack.pop()
            if source in component:
                continue
            component.add(source)
            stack.extend(adjacency[source] - component)
        seen.update(component)
        ordered_component = tuple(obs for obs in observations if obs in component)

        transport_rows: list[tuple[Observation, tuple[tuple[Value, Value], ...]]] = []
        for target in ordered_component:
            candidates = exact_transports.get((representative, target), [])
            unique: dict[tuple[tuple[int, int], ...], dict[Value, Value]] = {}
            for mapping in candidates:
                unique[_mapping_key(mapping, carrier)] = mapping
            if len(unique) != 1:
                raise AssertionError(
                    "pointed transport must exist uniquely; "
                    f"representative={representative!r}, target={target!r}, "
                    f"candidate_count={len(unique)}"
                )
            mapping = next(iter(unique.values()))
            items = tuple((value, mapping[value]) for value in carrier if value in mapping)
            transport_rows.append((target, items))

        result.append(
            PointedClass(
                representative=representative,
                observations=ordered_component,
                generated_subalgebra=generated[representative],
                transport_items=tuple(transport_rows),
            )
        )
    return tuple(result)

def parameterized_strategy_pointed(
    game: Any,
    core: Iterable[Value],
    winning_states: Iterable[State],
    *,
    internal_isomorphisms: Sequence[Any] | None = None,
) -> dict[Observation, Output] | None:
    """Minimum seed solver: one vector seed per pointed observation class."""

    raw_core = frozenset(core)
    fixed = parameter_core(game.algebra, raw_core)
    if raw_core != fixed:
        raise ValueError("pass a closed parameter core")
    winning = frozenset(winning_states)
    domains = _allowed_outputs(game, fixed, winning)
    if domains is None:
        return None
    classes = pointed_classes(
        game,
        fixed,
        internal_isomorphisms=internal_isomorphisms,
    )
    carrier_order = tuple(game.algebra.values)
    assignment: dict[Observation, Output] = {}

    for pointed in classes:
        seed_values = tuple(
            value for value in carrier_order if value in pointed.generated_subalgebra
        )
        transports = pointed.transports
        chosen: dict[Observation, Output] | None = None
        for seed in product(seed_values, repeat=game.state_arity):
            local: dict[Observation, Output] = {}
            valid = True
            for observation in pointed.observations:
                mapping = transports[observation]
                output = tuple(mapping[value] for value in seed)
                if output not in domains[observation]:
                    valid = False
                    break
                local[observation] = output
            if valid:
                chosen = local
                break
        if chosen is None:
            return None
        assignment.update(chosen)

    if set(assignment) != set(game.observations):
        raise AssertionError("pointed solver did not construct a total table")
    return assignment

class CompiledParameterizedKernel:
    """Precomputed exact solver for repeated domains under one closed core.

    The expensive algebraic data are frozen once:

    * core-fixing internal isomorphisms;
    * generated subalgebra at each observation;
    * raw reference edges/components;
    * pointed classes, unique transports, and seed vectors.

    Only safety/invariance lists change with the candidate winning domain.
    """

    def __init__(
        self,
        game: Any,
        core: Iterable[Value],
        *,
        internal_isomorphisms: Sequence[Any] | None = None,
    ) -> None:
        self.game = game
        raw_core = frozenset(core)
        self.core = parameter_core(game.algebra, raw_core)
        if self.core != raw_core:
            raise ValueError("pass a closed parameter core")
        self.isomorphisms = eligible_core_isomorphisms(
            game.algebra,
            self.core,
            internal_isomorphisms=internal_isomorphisms,
        )
        self.generated = {
            observation: generated_at_observation(game.algebra, self.core, observation)
            for observation in game.observations
        }
        self.base_domains = {
            observation: frozenset(
                output
                for output in game.outputs
                if all(value in self.generated[observation] for value in output)
            )
            for observation in game.observations
        }
        if any(not domain for domain in self.base_domains.values()):
            raise AssertionError("positive state arity must provide a generated output")

        observation_set = set(game.observations)
        arity = game.state_arity + game.input_arity
        edge_lists: dict[Observation, list[tuple[Observation, Any]]] = {
            observation: [] for observation in game.observations
        }
        neighbors: dict[Observation, set[Observation]] = {
            observation: set() for observation in game.observations
        }
        for isomorphism in self.isomorphisms:
            for source in product(tuple(isomorphism.domain), repeat=arity):
                if source not in observation_set:
                    continue
                target = isomorphism.map_tuple(source)
                edge_lists[source].append((target, isomorphism))
                neighbors[source].add(target)
                neighbors[target].add(source)
        self.reference_edges = {
            observation: tuple(rows) for observation, rows in edge_lists.items()
        }
        components: list[tuple[Observation, ...]] = []
        seen: set[Observation] = set()
        for representative in game.observations:
            if representative in seen:
                continue
            component: set[Observation] = set()
            stack = [representative]
            while stack:
                source = stack.pop()
                if source in component:
                    continue
                component.add(source)
                stack.extend(neighbors[source] - component)
            seen.update(component)
            components.append(tuple(obs for obs in game.observations if obs in component))
        self.reference_components = tuple(components)

        self.pointed_classes = pointed_classes(
            game,
            self.core,
            internal_isomorphisms=self.isomorphisms,
        )
        carrier_order = tuple(game.algebra.values)
        self.seed_vectors = {
            pointed.representative: tuple(
                product(
                    tuple(
                        value
                        for value in carrier_order
                        if value in pointed.generated_subalgebra
                    ),
                    repeat=game.state_arity,
                )
            )
            for pointed in self.pointed_classes
        }
        self.pointed_transports = {
            pointed.representative: pointed.transports
            for pointed in self.pointed_classes
        }

    def domains(self, winning_states: Iterable[State]) -> dict[Observation, frozenset[Output]] | None:
        winning = frozenset(winning_states)
        out: dict[Observation, frozenset[Output]] = {}
        for observation in self.game.observations:
            state, input_value = self.game.split_observation(observation)
            allowed = self.base_domains[observation]
            if state in winning:
                allowed = frozenset(
                    output
                    for output in allowed
                    if output in winning
                    and self.game.is_safe(state, input_value, output)
                )
            if not allowed:
                return None
            out[observation] = allowed
        return out

    def strategy_reference(self, winning_states: Iterable[State]) -> dict[Observation, Output] | None:
        domains = self.domains(winning_states)
        if domains is None:
            return None
        assignment: dict[Observation, Output] = {}
        for component in self.reference_components:
            representative = component[0]
            component_set = set(component)
            solved = None
            for candidate in self.game.outputs:
                if candidate not in domains[representative]:
                    continue
                local = {representative: candidate}
                queue = [representative]
                inconsistent = False
                while queue and not inconsistent:
                    source = queue.pop()
                    source_output = local[source]
                    for target, isomorphism in self.reference_edges[source]:
                        if not all(value in isomorphism.domain for value in source_output):
                            inconsistent = True
                            break
                        target_output = isomorphism.map_tuple(source_output)
                        if target_output not in domains[target]:
                            inconsistent = True
                            break
                        prior = local.get(target)
                        if prior is not None:
                            if prior != target_output:
                                inconsistent = True
                                break
                        else:
                            local[target] = target_output
                            queue.append(target)
                if not inconsistent and set(local) == component_set:
                    solved = local
                    break
            if solved is None:
                return None
            assignment.update(solved)
        return assignment

    def strategy_pointed(self, winning_states: Iterable[State]) -> dict[Observation, Output] | None:
        domains = self.domains(winning_states)
        if domains is None:
            return None
        assignment: dict[Observation, Output] = {}
        for pointed in self.pointed_classes:
            transports = self.pointed_transports[pointed.representative]
            chosen = None
            for seed in self.seed_vectors[pointed.representative]:
                local = {}
                valid = True
                for observation in pointed.observations:
                    mapping = transports[observation]
                    output = tuple(mapping[value] for value in seed)
                    if output not in domains[observation]:
                        valid = False
                        break
                    local[observation] = output
                if valid:
                    chosen = local
                    break
            if chosen is None:
                return None
            assignment.update(chosen)
        return assignment

    def local_feasible(self, winning_states: Iterable[State]) -> bool:
        return self.domains(winning_states) is not None

    def maximal_domains(
        self,
        *,
        solver: str = "pointed",
        exhaustive_state_limit: int = 16,
    ) -> tuple[tuple[frozenset[State], tuple[tuple[Observation, Output], ...]], ...]:
        if len(self.game.states) > exhaustive_state_limit:
            raise ValueError("state limit exceeded")
        if solver == "pointed":
            solve = self.strategy_pointed
        elif solver == "reference":
            solve = self.strategy_reference
        else:
            raise ValueError("solver must be 'pointed' or 'reference'")
        states = tuple(self.game.states)
        feasible = []
        for mask in range(1 << len(states)):
            domain = frozenset(
                states[index]
                for index in range(len(states))
                if mask & (1 << index)
            )
            strategy = solve(domain)
            if strategy is not None:
                feasible.append((domain, strategy))
        return tuple(
            (
                domain,
                tuple((obs, strategy[obs]) for obs in self.game.observations),
            )
            for domain, strategy in feasible
            if not any(domain < other for other, _ in feasible)
        )

def parameterized_strategy_for_allowed_parameters(
    game: Any,
    allowed_parameters: Iterable[Value],
    winning_states: Iterable[State],
    *,
    solver: str = "pointed",
    internal_isomorphisms: Sequence[Any] | None = None,
) -> dict[Observation, Output] | None:
    """Solve using a raw set of named parameters via its exact closure.

    This is the public ``allowed_parameters`` entry point.  Distinct raw sets
    with the same definable-constant core compile to the same kernel semantics.
    """

    core = parameter_core(game.algebra, allowed_parameters)
    kernel = CompiledParameterizedKernel(
        game,
        core,
        internal_isomorphisms=internal_isomorphisms,
    )
    if solver == "pointed":
        return kernel.strategy_pointed(winning_states)
    if solver == "reference":
        return kernel.strategy_reference(winning_states)
    raise ValueError("solver must be 'pointed' or 'reference'")


def maximal_domains_for_allowed_parameters(
    game: Any,
    allowed_parameters: Iterable[Value],
    *,
    solver: str = "pointed",
    exhaustive_state_limit: int = 16,
    internal_isomorphisms: Sequence[Any] | None = None,
) -> tuple[
    tuple[frozenset[State], tuple[tuple[Observation, Output], ...]], ...
]:
    """Enumerate maximal domains under a raw allowed-parameter set."""

    core = parameter_core(game.algebra, allowed_parameters)
    kernel = CompiledParameterizedKernel(
        game,
        core,
        internal_isomorphisms=internal_isomorphisms,
    )
    return kernel.maximal_domains(
        solver=solver,
        exhaustive_state_limit=exhaustive_state_limit,
    )


def naive_local_domain_feasible(
    game: Any,
    core: Iterable[Value],
    winning_states: Iterable[State],
) -> bool:
    """Deliberately unsound candidate that ignores cross-observation transport."""

    fixed = parameter_core(game.algebra, core)
    winning = frozenset(winning_states)
    domains = _allowed_outputs(game, fixed, winning)
    return domains is not None

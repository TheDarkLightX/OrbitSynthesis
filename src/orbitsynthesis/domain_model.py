"""CNF/MaxSAT model for quasi-primal shared-term winning domains.

For each internal-groupoid component of observations, one representative output
determines a total compatible output table on that component.  Once this table
is fixed, domain constraints have only two forms:

- a state is forbidden because the forced transition is unsafe; or
- including a source state forces inclusion of the selected successor state.

A domain is term-winning exactly when every component selects at least one
candidate rule whose forbidden states are absent and whose closure implications
hold.  This module compiles that statement to ordinary CNF and weighted partial
MaxSAT without depending on an external solver.

The caller is responsible for the quasi-primality premise.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Hashable, Iterable, Mapping, Sequence

from .finite_algebra import InternalIsomorphism
from .safety import FiniteSafetyGame

Value = Hashable
State = tuple[Value, ...]
Input = tuple[Value, ...]
Output = tuple[Value, ...]
Observation = tuple[Value, ...]


def _stable(values):
    return tuple(sorted(values, key=repr))


@dataclass(frozen=True)
class ComponentCandidateRule:
    """One compatible component table and its induced domain constraints."""

    representative_output: Output
    assignment_items: tuple[tuple[Observation, Output], ...]
    forbidden_states: frozenset[State]
    closure_edges: frozenset[tuple[State, State]]

    @property
    def assignment(self) -> dict[Observation, Output]:
        return dict(self.assignment_items)

    def accepts(self, domain: frozenset[State]) -> bool:
        return not (self.forbidden_states & domain) and all(
            source not in domain or target in domain
            for source, target in self.closure_edges
        )


@dataclass(frozen=True)
class ComponentRuleSet:
    representative: Observation
    observations: tuple[Observation, ...]
    candidates: tuple[ComponentCandidateRule, ...]


@dataclass(frozen=True)
class CompiledDomainWitness:
    domain: frozenset[State]
    component_choices: tuple[int, ...]
    strategy_items: tuple[tuple[Observation, Output], ...]

    @property
    def strategy(self) -> dict[Observation, Output]:
        return dict(self.strategy_items)


@dataclass(frozen=True)
class CompiledDomainFailure:
    domain: frozenset[State]
    component_index: int
    representative: Observation
    forbidden_hits: tuple[tuple[int, tuple[State, ...]], ...]
    missing_closure_edges: tuple[
        tuple[int, tuple[tuple[State, State], ...]], ...
    ]


@dataclass(frozen=True)
class CNFEncoding:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]
    state_variables: tuple[tuple[State, int], ...]
    candidate_variables: tuple[tuple[int, int, int], ...]

    def dimacs(self) -> str:
        lines = [f"p cnf {self.variable_count} {len(self.clauses)}"]
        lines.extend(" ".join(map(str, clause)) + " 0" for clause in self.clauses)
        return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class WeightedCNFEncoding:
    variable_count: int
    hard_clauses: tuple[tuple[int, ...], ...]
    # The first entry is a signed literal.  Positive state weight emits x_s;
    # negative state weight emits not x_s.  Maximizing satisfied soft weight is
    # therefore the original signed objective plus a fixed offset.
    soft_state_units: tuple[tuple[int, int], ...]
    top_weight: int

    def wdimacs(self) -> str:
        clause_count = len(self.hard_clauses) + len(self.soft_state_units)
        lines = [
            f"p wcnf {self.variable_count} {clause_count} {self.top_weight}"
        ]
        lines.extend(
            f"{self.top_weight} " + " ".join(map(str, clause)) + " 0"
            for clause in self.hard_clauses
        )
        lines.extend(
            f"{weight} {literal} 0"
            for literal, weight in self.soft_state_units
        )
        return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class QuasiPrimalDomainModel:
    states: tuple[State, ...]
    observations: tuple[Observation, ...]
    components: tuple[ComponentRuleSet, ...]

    def solve_domain(
        self,
        domain: Iterable[State],
    ) -> CompiledDomainWitness | CompiledDomainFailure:
        chosen_domain = frozenset(domain)
        strategy: dict[Observation, Output] = {}
        choices: list[int] = []

        for component_index, component in enumerate(self.components):
            selected_index = None
            for candidate_index, candidate in enumerate(component.candidates):
                if candidate.accepts(chosen_domain):
                    selected_index = candidate_index
                    strategy.update(candidate.assignment)
                    choices.append(candidate_index)
                    break
            if selected_index is not None:
                continue

            forbidden_hits = []
            missing_edges = []
            for candidate_index, candidate in enumerate(component.candidates):
                hits = _stable(candidate.forbidden_states & chosen_domain)
                missing = tuple(
                    sorted(
                        (
                            (source, target)
                            for source, target in candidate.closure_edges
                            if source in chosen_domain and target not in chosen_domain
                        ),
                        key=repr,
                    )
                )
                forbidden_hits.append((candidate_index, hits))
                missing_edges.append((candidate_index, missing))
            return CompiledDomainFailure(
                domain=chosen_domain,
                component_index=component_index,
                representative=component.representative,
                forbidden_hits=tuple(forbidden_hits),
                missing_closure_edges=tuple(missing_edges),
            )

        return CompiledDomainWitness(
            domain=chosen_domain,
            component_choices=tuple(choices),
            strategy_items=tuple(sorted(strategy.items(), key=lambda item: repr(item[0]))),
        )

    def domain_feasible(self, domain: Iterable[State]) -> bool:
        return isinstance(self.solve_domain(domain), CompiledDomainWitness)

    def maximal_domains(
        self,
        *,
        exhaustive_state_limit: int = 20,
    ) -> tuple[frozenset[State], ...]:
        if len(self.states) > exhaustive_state_limit:
            raise ValueError(
                "exact model enumeration disabled above "
                f"{exhaustive_state_limit} states"
            )
        feasible = []
        for mask in range(1 << len(self.states)):
            domain = frozenset(
                state
                for index, state in enumerate(self.states)
                if mask & (1 << index)
            )
            if self.domain_feasible(domain):
                feasible.append(domain)
        return tuple(
            domain
            for domain in feasible
            if not any(domain < other for other in feasible)
        )

    def cnf(
        self,
        *,
        required_states: Iterable[State] = (),
        forbidden_states: Iterable[State] = (),
    ) -> CNFEncoding:
        state_variables = {
            state: index + 1
            for index, state in enumerate(self.states)
        }
        next_variable = len(state_variables) + 1
        candidate_variables: dict[tuple[int, int], int] = {}
        for component_index, component in enumerate(self.components):
            for candidate_index, _ in enumerate(component.candidates):
                candidate_variables[(component_index, candidate_index)] = next_variable
                next_variable += 1

        clauses: list[tuple[int, ...]] = []
        for component_index, component in enumerate(self.components):
            selectors = tuple(
                candidate_variables[(component_index, candidate_index)]
                for candidate_index, _ in enumerate(component.candidates)
            )
            clauses.append(selectors)
            for candidate_index, candidate in enumerate(component.candidates):
                selector = candidate_variables[(component_index, candidate_index)]
                clauses.extend(
                    (-selector, -state_variables[state])
                    for state in candidate.forbidden_states
                )
                clauses.extend(
                    (
                        -selector,
                        -state_variables[source],
                        state_variables[target],
                    )
                    for source, target in candidate.closure_edges
                    if source != target
                )

        required = frozenset(required_states)
        forbidden = frozenset(forbidden_states)
        if required & forbidden:
            raise ValueError("required and forbidden states overlap")
        unknown = (required | forbidden) - set(state_variables)
        if unknown:
            raise ValueError(f"hard state outside model: {min(unknown, key=repr)!r}")
        clauses.extend((state_variables[state],) for state in required)
        clauses.extend((-state_variables[state],) for state in forbidden)

        return CNFEncoding(
            variable_count=next_variable - 1,
            clauses=tuple(clauses),
            state_variables=tuple(state_variables.items()),
            candidate_variables=tuple(
                (component_index, candidate_index, variable)
                for (component_index, candidate_index), variable
                in candidate_variables.items()
            ),
        )

    def weighted_cnf(
        self,
        *,
        required_states: Iterable[State] = (),
        forbidden_states: Iterable[State] = (),
        state_weights: Mapping[State, int] | None = None,
        default_weight: int = 1,
    ) -> WeightedCNFEncoding:
        """Compile signed state utility to weighted partial MaxSAT.

        A positive weight `w(s)` produces the soft unit `(x_s,w(s))`.  A
        negative weight produces `(-x_s,-w(s))`; satisfying that unit rewards
        exclusion.  For every domain `D`, total soft reward equals

        `sum_(w(s)<0) -w(s) + sum_(s in D) w(s)`,

        so maximizing reward is exactly equivalent to maximizing the signed
        state-weight objective.  Zero-weight states produce no soft clause.
        """

        if not isinstance(default_weight, int):
            raise TypeError("default_weight must be an integer")
        supplied = {} if state_weights is None else dict(state_weights)
        unknown = set(supplied) - set(self.states)
        if unknown:
            raise ValueError(f"state weight outside model: {min(unknown, key=repr)!r}")
        if any(not isinstance(weight, int) for weight in supplied.values()):
            raise TypeError("all state weights must be integers")

        encoding = self.cnf(
            required_states=required_states,
            forbidden_states=forbidden_states,
        )
        variable_by_state = dict(encoding.state_variables)
        weights = {
            state: supplied.get(state, default_weight)
            for state in self.states
        }
        soft = tuple(
            (
                variable_by_state[state] if weight > 0 else -variable_by_state[state],
                abs(weight),
            )
            for state, weight in weights.items()
            if weight != 0
        )
        return WeightedCNFEncoding(
            variable_count=encoding.variable_count,
            hard_clauses=encoding.clauses,
            soft_state_units=soft,
            top_weight=sum(weight for _literal, weight in soft) + 1,
        )


def _groupoid_edges(
    game: FiniteSafetyGame,
    internal_isomorphisms: Sequence[InternalIsomorphism],
) -> dict[Observation, tuple[tuple[Observation, InternalIsomorphism], ...]]:
    arity = game.state_arity + game.input_arity
    edges: dict[Observation, list[tuple[Observation, InternalIsomorphism]]] = {
        observation: [] for observation in game.observations
    }
    for isomorphism in internal_isomorphisms:
        for observation in product(tuple(isomorphism.domain), repeat=arity):
            edges[observation].append(
                (isomorphism.map_tuple(observation), isomorphism)
            )
    return {observation: tuple(outgoing) for observation, outgoing in edges.items()}


def _groupoid_components(
    observations: Sequence[Observation],
    edges: dict[Observation, tuple[tuple[Observation, InternalIsomorphism], ...]],
) -> tuple[tuple[Observation, ...], ...]:
    neighbors = {observation: set() for observation in observations}
    for source, outgoing in edges.items():
        for target, _ in outgoing:
            neighbors[source].add(target)
            neighbors[target].add(source)
    seen = set()
    components = []
    for representative in observations:
        if representative in seen:
            continue
        component = set()
        stack = [representative]
        while stack:
            observation = stack.pop()
            if observation in component:
                continue
            component.add(observation)
            stack.extend(neighbors[observation] - component)
        seen.update(component)
        components.append(_stable(component))
    return tuple(components)


def compile_quasi_primal_domain_model(
    game: FiniteSafetyGame,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> QuasiPrimalDomainModel:
    """Compile a finite quasi-primal safety game to candidate closure rules."""

    isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else game.algebra.internal_isomorphisms()
    )
    edges = _groupoid_edges(game, isomorphisms)
    components = _groupoid_components(game.observations, edges)
    compiled_components = []

    for component in components:
        representative = component[0]
        generated = game.algebra.generated_subalgebra(representative)
        representative_outputs = tuple(
            output
            for output in game.outputs
            if all(value in generated for value in output)
        )
        candidates = []
        signatures = set()

        for candidate in _stable(representative_outputs):
            assignment: dict[Observation, Output] = {representative: candidate}
            queue = [representative]
            inconsistent = False
            while queue and not inconsistent:
                source = queue.pop()
                source_output = assignment[source]
                for target, isomorphism in edges[source]:
                    if not all(value in isomorphism.domain for value in source_output):
                        inconsistent = True
                        break
                    target_output = isomorphism.map_tuple(source_output)
                    previous = assignment.get(target)
                    if previous is not None:
                        if previous != target_output:
                            inconsistent = True
                            break
                        continue
                    assignment[target] = target_output
                    queue.append(target)
            if inconsistent or set(assignment) != set(component):
                continue

            forbidden = set()
            closure = set()
            for observation, output in assignment.items():
                state, input_value = game.split_observation(observation)
                if (state, input_value, output) not in game.safe_relation:
                    forbidden.add(state)
                elif state != output:
                    closure.add((state, output))

            signature = (frozenset(forbidden), frozenset(closure))
            if signature in signatures:
                continue
            signatures.add(signature)
            candidates.append(
                ComponentCandidateRule(
                    representative_output=candidate,
                    assignment_items=tuple(
                        sorted(assignment.items(), key=lambda item: repr(item[0]))
                    ),
                    forbidden_states=signature[0],
                    closure_edges=signature[1],
                )
            )

        if not candidates:
            raise ValueError(
                "no structurally compatible candidate for component "
                f"{representative!r}; quasi-primal premise or groupoid data is invalid"
            )
        compiled_components.append(
            ComponentRuleSet(
                representative=representative,
                observations=component,
                candidates=tuple(candidates),
            )
        )

    return QuasiPrimalDomainModel(
        states=game.states,
        observations=game.observations,
        components=tuple(compiled_components),
    )

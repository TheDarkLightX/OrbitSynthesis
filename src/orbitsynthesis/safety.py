"""Tau-independent finite-algebra safety synthesis kernel.

Implemented controller semantics:

- unrestricted finite positional strategies;
- semi-primal original-signature term mode via generated-subalgebra filtering;
- demi-semi-primal term mode via global automorphism orbits/stabilizers;
- quasi-primal term-table feasibility via the full internal-isomorphism groupoid.

The mathematical assumptions behind each mode live in the corresponding notes
under ``notes/``.  This module does not attempt to infer whether an arbitrary
input algebra belongs to one of those classes; the caller chooses the semantic
mode only when its algebraic hypotheses are justified.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Hashable, Iterable, Mapping, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism

Value = Hashable
State = tuple[Value, ...]
Input = tuple[Value, ...]
Output = tuple[Value, ...]
Observation = tuple[Value, ...]
Transition = tuple[State, Input, Output]


@dataclass(frozen=True)
class SafetySolution:
    """A solved finite safety game under one controller semantic class."""

    mode: str
    winning_states: frozenset[State]
    strategy_items: tuple[tuple[Observation, Output], ...]

    @property
    def strategy(self) -> dict[Observation, Output]:
        return dict(self.strategy_items)


class FiniteSafetyGame:
    """A perfect-information finite safety game over a finite algebra carrier."""

    def __init__(
        self,
        algebra: FiniteAlgebra,
        state_arity: int,
        input_arity: int,
        safe_relation: Iterable[Transition],
    ) -> None:
        if state_arity <= 0:
            raise ValueError("state_arity must be positive")
        if input_arity < 0:
            raise ValueError("input_arity cannot be negative")

        self.algebra = algebra
        self.state_arity = state_arity
        self.input_arity = input_arity
        self.states: tuple[State, ...] = tuple(
            product(algebra.values, repeat=state_arity)
        )
        self.inputs: tuple[Input, ...] = tuple(
            product(algebra.values, repeat=input_arity)
        )
        self.outputs = self.states
        self.safe_relation = frozenset(safe_relation)

        allowed_states = set(self.states)
        allowed_inputs = set(self.inputs)
        for state, input_value, output in self.safe_relation:
            if state not in allowed_states:
                raise ValueError(f"safe relation contains unknown state {state!r}")
            if input_value not in allowed_inputs:
                raise ValueError(
                    f"safe relation contains unknown input {input_value!r}"
                )
            if output not in allowed_states:
                raise ValueError(f"safe relation contains unknown output {output!r}")

        self.observations: tuple[Observation, ...] = tuple(
            state + input_value
            for state in self.states
            for input_value in self.inputs
        )

    def is_safe(self, state: State, input_value: Input, output: Output) -> bool:
        return (state, input_value, output) in self.safe_relation

    def split_observation(self, observation: Observation) -> tuple[State, Input]:
        return (
            observation[: self.state_arity],
            observation[self.state_arity :],
        )

    # ------------------------------------------------------------------
    # Ordinary finite positional synthesis
    # ------------------------------------------------------------------

    def ordinary_predecessor(self, target: Iterable[State]) -> frozenset[State]:
        target_set = frozenset(target)
        return frozenset(
            state
            for state in self.states
            if all(
                any(
                    output in target_set
                    and self.is_safe(state, input_value, output)
                    for output in self.outputs
                )
                for input_value in self.inputs
            )
        )

    def greatest_fixed_point(self, predecessor) -> tuple[frozenset[State], tuple[frozenset[State], ...]]:
        current = frozenset(self.states)
        trajectory = [current]
        while True:
            nxt = frozenset(predecessor(current))
            trajectory.append(nxt)
            if nxt == current:
                return current, tuple(trajectory)
            current = nxt

    def _first_output(
        self,
        state: State,
        input_value: Input,
        target: frozenset[State],
        predicate,
    ) -> Output:
        for output in self.outputs:
            if (
                output in target
                and self.is_safe(state, input_value, output)
                and predicate(output)
            ):
                return output
        raise ValueError(
            f"no admissible output for winning observation {(state, input_value)!r}"
        )

    def ordinary_strategy(
        self, winning_states: Iterable[State]
    ) -> dict[Observation, Output]:
        winning = frozenset(winning_states)
        result: dict[Observation, Output] = {}
        for state in winning:
            for input_value in self.inputs:
                result[state + input_value] = self._first_output(
                    state,
                    input_value,
                    winning,
                    lambda _output: True,
                )
        return result

    def solve_ordinary(self) -> SafetySolution:
        winning, _ = self.greatest_fixed_point(self.ordinary_predecessor)
        strategy = self.ordinary_strategy(winning)
        return SafetySolution(
            mode="ordinary",
            winning_states=winning,
            strategy_items=tuple(strategy.items()),
        )

    # ------------------------------------------------------------------
    # Semi-primal term synthesis
    # ------------------------------------------------------------------

    def semi_primal_predecessor(
        self, target: Iterable[State]
    ) -> frozenset[State]:
        target_set = frozenset(target)
        result: set[State] = set()
        for state in self.states:
            state_wins = True
            for input_value in self.inputs:
                generated = self.algebra.generated_subalgebra(state + input_value)
                if not any(
                    output in target_set
                    and self.is_safe(state, input_value, output)
                    and all(value in generated for value in output)
                    for output in self.outputs
                ):
                    state_wins = False
                    break
            if state_wins:
                result.add(state)
        return frozenset(result)

    def semi_primal_strategy(
        self, winning_states: Iterable[State]
    ) -> dict[Observation, Output]:
        winning = frozenset(winning_states)
        result: dict[Observation, Output] = {}
        for state in winning:
            for input_value in self.inputs:
                generated = self.algebra.generated_subalgebra(state + input_value)
                result[state + input_value] = self._first_output(
                    state,
                    input_value,
                    winning,
                    lambda output, generated=generated: all(
                        value in generated for value in output
                    ),
                )
        return result

    def solve_semi_primal(self) -> SafetySolution:
        winning, _ = self.greatest_fixed_point(self.semi_primal_predecessor)
        strategy = self.semi_primal_strategy(winning)
        return SafetySolution(
            mode="semi_primal",
            winning_states=winning,
            strategy_items=tuple(strategy.items()),
        )

    # ------------------------------------------------------------------
    # Demi-semi-primal automorphism-orbit synthesis
    # ------------------------------------------------------------------

    @staticmethod
    def _map_tuple(
        automorphism: InternalIsomorphism,
        values: Sequence[Value],
    ) -> tuple[Value, ...]:
        return automorphism.map_tuple(values)

    def _observation_stabilizer(
        self,
        observation: Observation,
        automorphisms: Sequence[InternalIsomorphism],
    ) -> tuple[InternalIsomorphism, ...]:
        return tuple(
            automorphism
            for automorphism in automorphisms
            if self._map_tuple(automorphism, observation) == observation
        )

    def demi_semi_primal_predecessor(
        self, target: Iterable[State]
    ) -> frozenset[State]:
        target_set = frozenset(target)
        automorphisms = self.algebra.automorphisms()
        result: set[State] = set()

        for state in self.states:
            state_wins = True
            for input_value in self.inputs:
                observation = state + input_value
                generated = self.algebra.generated_subalgebra(observation)
                stabilizer = self._observation_stabilizer(
                    observation, automorphisms
                )

                good = False
                for output in self.outputs:
                    if output not in target_set:
                        continue
                    if not self.is_safe(state, input_value, output):
                        continue
                    if not all(value in generated for value in output):
                        continue
                    if not all(
                        self._map_tuple(automorphism, output) == output
                        for automorphism in stabilizer
                    ):
                        continue
                    good = True
                    break

                if not good:
                    state_wins = False
                    break

            if state_wins:
                result.add(state)

        return frozenset(result)

    def demi_semi_primal_strategy(
        self, winning_states: Iterable[State]
    ) -> dict[Observation, Output]:
        """Construct an orbitwise winning table on winning observations."""

        winning = frozenset(winning_states)
        automorphisms = self.algebra.automorphisms()
        result: dict[Observation, Output] = {}
        processed: set[Observation] = set()

        for observation in self.observations:
            state, input_value = self.split_observation(observation)
            if state not in winning or observation in processed:
                continue

            orbit = {
                self._map_tuple(automorphism, observation)
                for automorphism in automorphisms
            }
            stabilizer = self._observation_stabilizer(
                observation, automorphisms
            )
            generated = self.algebra.generated_subalgebra(observation)

            representative_output: Output | None = None
            for output in self.outputs:
                if output not in winning:
                    continue
                if not self.is_safe(state, input_value, output):
                    continue
                if not all(value in generated for value in output):
                    continue
                if not all(
                    self._map_tuple(automorphism, output) == output
                    for automorphism in stabilizer
                ):
                    continue
                representative_output = output
                break

            if representative_output is None:
                raise ValueError(
                    f"winning set is not demi-semi-primal closed at {observation!r}"
                )

            for automorphism in automorphisms:
                mapped_observation = self._map_tuple(
                    automorphism, observation
                )
                if mapped_observation not in orbit:
                    continue
                mapped_state, _ = self.split_observation(mapped_observation)
                if mapped_state not in winning:
                    raise ValueError("winning set is not automorphism invariant")
                mapped_output = self._map_tuple(
                    automorphism, representative_output
                )
                if mapped_observation in result:
                    if result[mapped_observation] != mapped_output:
                        raise ValueError("stabilizer consistency failure")
                else:
                    result[mapped_observation] = mapped_output

            processed.update(orbit)

        return result

    def solve_demi_semi_primal(self) -> SafetySolution:
        winning, _ = self.greatest_fixed_point(
            self.demi_semi_primal_predecessor
        )
        strategy = self.demi_semi_primal_strategy(winning)
        return SafetySolution(
            mode="demi_semi_primal",
            winning_states=winning,
            strategy_items=tuple(strategy.items()),
        )

    # ------------------------------------------------------------------
    # Quasi-primal internal-isomorphism strategy-table constraints
    # ------------------------------------------------------------------

    def _internal_isomorphism_edges(
        self,
    ) -> dict[Observation, tuple[tuple[Observation, InternalIsomorphism], ...]]:
        edges: dict[Observation, list[tuple[Observation, InternalIsomorphism]]] = {
            observation: [] for observation in self.observations
        }
        arity = self.state_arity + self.input_arity
        for isomorphism in self.algebra.internal_isomorphisms():
            domain_values = tuple(isomorphism.domain)
            for observation in product(domain_values, repeat=arity):
                mapped = isomorphism.map_tuple(observation)
                edges[observation].append((mapped, isomorphism))
        return {
            observation: tuple(outgoing)
            for observation, outgoing in edges.items()
        }

    def quasi_primal_strategy_for_domain(
        self,
        winning_states: Iterable[State],
    ) -> dict[Observation, Output] | None:
        """Solve the exact quasi-primal positional term-table CSP for one W.

        The internal-isomorphism constraints are bijective equations.  For a
        fixed winning domain W they decompose into connected components: choose
        one candidate output at a representative observation and propagate it
        through every internal isomorphism, rejecting inconsistent cycles or
        observations whose local safety/invariance domain is violated.

        Returns a TOTAL clone-compatible table when feasible, otherwise None.
        """

        winning = frozenset(winning_states)
        domains: dict[Observation, frozenset[Output]] = {}

        for observation in self.observations:
            state, input_value = self.split_observation(observation)
            generated = self.algebra.generated_subalgebra(observation)
            allowed = {
                output
                for output in self.outputs
                if all(value in generated for value in output)
            }
            if state in winning:
                allowed = {
                    output
                    for output in allowed
                    if output in winning
                    and self.is_safe(state, input_value, output)
                }
            if not allowed:
                return None
            domains[observation] = frozenset(allowed)

        edges = self._internal_isomorphism_edges()

        # Build undirected component adjacency.  Inverses are present among all
        # internal isomorphisms, but explicit reverse adjacency makes the
        # component computation independent of enumeration order.
        neighbors: dict[Observation, set[Observation]] = {
            observation: set() for observation in self.observations
        }
        for source, outgoing in edges.items():
            for target, _ in outgoing:
                neighbors[source].add(target)
                neighbors[target].add(source)

        assignment: dict[Observation, Output] = {}
        seen: set[Observation] = set()

        for representative in self.observations:
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

            component_assignment: dict[Observation, Output] | None = None

            for candidate in domains[representative]:
                local: dict[Observation, Output] = {representative: candidate}
                queue = [representative]
                inconsistent = False

                while queue and not inconsistent:
                    source = queue.pop()
                    source_output = local[source]
                    for target, isomorphism in edges[source]:
                        # Since source lies in the isomorphism domain and the
                        # local output lies in Sg(source), source_output must be
                        # inside that same domain subalgebra.
                        if not all(
                            value in isomorphism.domain
                            for value in source_output
                        ):
                            inconsistent = True
                            break

                        target_output = isomorphism.map_tuple(source_output)
                        if target_output not in domains[target]:
                            inconsistent = True
                            break

                        if target in local:
                            if local[target] != target_output:
                                inconsistent = True
                                break
                        else:
                            local[target] = target_output
                            queue.append(target)

                if not inconsistent and set(local) == component:
                    component_assignment = local
                    break

            if component_assignment is None:
                return None
            assignment.update(component_assignment)

        return assignment

    def quasi_primal_domain_feasible(
        self, winning_states: Iterable[State]
    ) -> bool:
        return self.quasi_primal_strategy_for_domain(winning_states) is not None

    def maximal_quasi_primal_domains(
        self,
        exhaustive_state_limit: int = 16,
    ) -> tuple[frozenset[State], ...]:
        """Enumerate inclusion-maximal term-controllable invariant domains.

        A quasi-primal game need not have one union-closed/greatest winning
        domain, because distinct safe tables can be globally incompatible under
        clone constraints.  This exact exponential routine is therefore a
        calibration/reference solver, not the intended large-game algorithm.
        """

        if len(self.states) > exhaustive_state_limit:
            raise ValueError(
                "exact quasi-primal domain enumeration is disabled above "
                f"{exhaustive_state_limit} states"
            )

        feasible: list[frozenset[State]] = []
        state_list = list(self.states)
        for mask in range(1 << len(state_list)):
            domain = frozenset(
                state_list[index]
                for index in range(len(state_list))
                if mask & (1 << index)
            )
            if self.quasi_primal_domain_feasible(domain):
                feasible.append(domain)

        return tuple(
            domain
            for domain in feasible
            if not any(domain < other for other in feasible)
        )

    def solve_quasi_primal_from_initial(
        self,
        initial_states: Iterable[State],
        exhaustive_state_limit: int = 16,
    ) -> SafetySolution | None:
        """Find one maximal feasible quasi-primal domain containing initials."""

        required = frozenset(initial_states)
        candidates = [
            domain
            for domain in self.maximal_quasi_primal_domains(
                exhaustive_state_limit=exhaustive_state_limit
            )
            if required <= domain
        ]
        if not candidates:
            return None

        # Deterministic reference choice: prefer maximum cardinality, then the
        # order in which exhaustive enumeration discovered the maximal domains.
        winning = max(candidates, key=len)
        strategy = self.quasi_primal_strategy_for_domain(winning)
        if strategy is None:
            raise AssertionError("feasible maximal domain lost its strategy")

        return SafetySolution(
            mode="quasi_primal",
            winning_states=winning,
            strategy_items=tuple(strategy.items()),
        )

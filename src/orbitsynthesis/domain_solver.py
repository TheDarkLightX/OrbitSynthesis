"""Solver-neutral decoding and exact small-instance optimization.

The domain model emits DIMACS CNF/WCNF but deliberately has no dependency on a
particular SAT package.  This module provides the stable interoperability
boundary:

- parse the conventional ``v ... 0`` model lines used by SAT/MaxSAT tools;
- verify every hard clause;
- recover the selected winning domain and one component rule per groupoid
  component;
- reconstruct a complete compatible controller table; and
- provide a bounded exhaustive optimizer as a reference oracle.

External processes are intentionally not launched here.  Deployment code may
choose Open-WBO, MaxHS, RC2, or another solver while preserving the same model
certificate and verifier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Mapping

from .domain_model import (
    CNFEncoding,
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
)

Value = Hashable
State = tuple[Value, ...]
Observation = tuple[Value, ...]
Output = tuple[Value, ...]


@dataclass(frozen=True)
class ParsedBooleanModel:
    """A checked partial/complete DIMACS assignment."""

    true_variables: frozenset[int]
    false_variables: frozenset[int]

    def value(self, variable: int) -> bool:
        return variable in self.true_variables


@dataclass(frozen=True)
class WeightedDomainOptimum:
    """Exact bounded reference optimum."""

    total_weight: int
    witness: CompiledDomainWitness


def parse_dimacs_model(text: str) -> tuple[int, ...]:
    """Parse model literals from conventional SAT/MaxSAT output.

    Lines beginning with ``v`` are concatenated.  The terminating zero is
    ignored.  Bare integer-only lines are also accepted for lightweight
    adapters.  Status/objective/comment lines are ignored.
    """

    literals: list[int] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("c", "s", "o")):
            continue
        tokens = line.split()
        if tokens[0].lower() == "v":
            tokens = tokens[1:]
        elif not all(token.lstrip("-").isdigit() for token in tokens):
            continue
        for token in tokens:
            literal = int(token)
            if literal == 0:
                continue
            literals.append(literal)
    return tuple(literals)


def normalize_boolean_model(
    variable_count: int,
    literals: Iterable[int],
) -> ParsedBooleanModel:
    """Validate variable ranges and contradictory literals."""

    true_variables: set[int] = set()
    false_variables: set[int] = set()
    for literal in literals:
        variable = abs(int(literal))
        if not 1 <= variable <= variable_count:
            raise ValueError(f"model variable outside 1..{variable_count}: {literal}")
        if literal > 0:
            if variable in false_variables:
                raise ValueError(f"contradictory model literal for variable {variable}")
            true_variables.add(variable)
        else:
            if variable in true_variables:
                raise ValueError(f"contradictory model literal for variable {variable}")
            false_variables.add(variable)
    return ParsedBooleanModel(
        true_variables=frozenset(true_variables),
        false_variables=frozenset(false_variables),
    )


def clause_satisfied(
    clause: Iterable[int],
    assignment: ParsedBooleanModel,
) -> bool:
    """Evaluate one clause, treating unspecified variables as false."""

    return any(
        assignment.value(abs(literal)) == (literal > 0)
        for literal in clause
    )


def decode_cnf_model(
    model: QuasiPrimalDomainModel,
    encoding: CNFEncoding,
    literals: Iterable[int],
) -> CompiledDomainWitness:
    """Verify a CNF model and reconstruct its domain/controller certificate."""

    assignment = normalize_boolean_model(encoding.variable_count, literals)
    failed_clause = next(
        (
            clause
            for clause in encoding.clauses
            if not clause_satisfied(clause, assignment)
        ),
        None,
    )
    if failed_clause is not None:
        raise ValueError(f"assignment violates hard clause {failed_clause!r}")

    domain = frozenset(
        state
        for state, variable in encoding.state_variables
        if assignment.value(variable)
    )
    candidate_variables = {
        (component_index, candidate_index): variable
        for component_index, candidate_index, variable
        in encoding.candidate_variables
    }

    choices: list[int] = []
    strategy: dict[Observation, Output] = {}
    for component_index, component in enumerate(model.components):
        selected = tuple(
            candidate_index
            for candidate_index, candidate in enumerate(component.candidates)
            if assignment.value(
                candidate_variables[(component_index, candidate_index)]
            )
        )
        if not selected:
            raise ValueError(
                f"component {component_index} has no selected candidate"
            )
        if any(
            not component.candidates[candidate_index].accepts(domain)
            for candidate_index in selected
        ):
            raise ValueError(
                f"component {component_index} selects a rule incompatible with the domain"
            )
        chosen = selected[0]
        choices.append(chosen)
        strategy.update(component.candidates[chosen].assignment)

    return CompiledDomainWitness(
        domain=domain,
        component_choices=tuple(choices),
        strategy_items=tuple(sorted(strategy.items(), key=lambda item: repr(item[0]))),
    )


def literals_for_witness(
    model: QuasiPrimalDomainModel,
    encoding: CNFEncoding,
    witness: CompiledDomainWitness,
) -> tuple[int, ...]:
    """Produce one complete DIMACS assignment for a compiled witness."""

    true_variables = {
        variable
        for state, variable in encoding.state_variables
        if state in witness.domain
    }
    candidate_variables = {
        (component_index, candidate_index): variable
        for component_index, candidate_index, variable
        in encoding.candidate_variables
    }
    if len(witness.component_choices) != len(model.components):
        raise ValueError("witness has the wrong number of component choices")
    for component_index, candidate_index in enumerate(witness.component_choices):
        true_variables.add(
            candidate_variables[(component_index, candidate_index)]
        )
    return tuple(
        variable if variable in true_variables else -variable
        for variable in range(1, encoding.variable_count + 1)
    )


def maximum_weight_domain_exhaustive(
    model: QuasiPrimalDomainModel,
    *,
    required_states: Iterable[State] = (),
    state_weights: Mapping[State, int] | None = None,
    exhaustive_state_limit: int = 20,
) -> WeightedDomainOptimum | None:
    """Exact reference optimizer for tests and small standalone instances."""

    if len(model.states) > exhaustive_state_limit:
        raise ValueError(
            "exhaustive weighted optimization disabled above "
            f"{exhaustive_state_limit} states"
        )
    required = frozenset(required_states)
    carrier = frozenset(model.states)
    if not required <= carrier:
        raise ValueError("required state outside the model")
    weights = {
        state: (
            state_weights[state]
            if state_weights is not None and state in state_weights
            else 1
        )
        for state in model.states
    }
    if any(weight <= 0 for weight in weights.values()):
        raise ValueError("state weights must be positive integers")

    best: WeightedDomainOptimum | None = None
    for mask in range(1 << len(model.states)):
        domain = frozenset(
            state
            for index, state in enumerate(model.states)
            if mask & (1 << index)
        )
        if not required <= domain:
            continue
        solution = model.solve_domain(domain)
        if not isinstance(solution, CompiledDomainWitness):
            continue
        total = sum(weights[state] for state in domain)
        candidate = WeightedDomainOptimum(total_weight=total, witness=solution)
        if best is None:
            best = candidate
            continue
        if total > best.total_weight:
            best = candidate
            continue
        if total == best.total_weight and repr(sorted(domain)) < repr(
            sorted(best.witness.domain)
        ):
            best = candidate
    return best

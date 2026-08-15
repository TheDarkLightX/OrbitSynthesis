"""Exact lazy conflict learning for weighted quasi-primal domain search.

The eager domain model can emit every component-rule selector and all of its
CNF clauses at once. This module provides the complementary lazy architecture:

1. an outer state-assignment oracle proposes the best domain not excluded by
   previously learned state-only clauses;
2. the exact component model either returns a controller witness or one
   ``CompiledDomainFailure``;
3. the failure is minimized to a sound state-literal conflict core; and
4. the negated core is learned before the next proposal.

The candidate oracle implemented here is exhaustive and deliberately bounded.
It is a deterministic reference implementation for tests and small standalone
instances. A production implementation can replace that oracle with an
incremental SAT/MaxSAT backend while keeping the same conflict-core and
certificate interface.

The caller is responsible for the quasi-primality premise used when the domain
model was compiled.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Mapping

from .domain_model import (
    CompiledDomainFailure,
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
)
from .domain_nogood import (
    DomainConflictCore,
    minimize_domain_failure,
    verify_domain_conflict_core_against_model,
)
from .domain_solver import WeightedDomainOptimum

Value = Hashable
State = tuple[Value, ...]


@dataclass(frozen=True)
class LearnedDomainSearchStats:
    """Deterministic accounting for one lazy optimization run."""

    oracle_rounds: int
    component_model_checks: int
    learned_core_count: int
    learned_literal_count: int
    state_assignments_scanned: int
    state_assignments_rejected_by_hard_constraints: int
    state_assignments_rejected_by_learned_cores: int


@dataclass(frozen=True)
class LearnedDomainSearchResult:
    """Optimal controller/domain certificate or an exact infeasibility result."""

    optimum: WeightedDomainOptimum | None
    conflict_cores: tuple[DomainConflictCore, ...]
    blocking_clauses: tuple[tuple[int, ...], ...]
    stats: LearnedDomainSearchStats


@dataclass(frozen=True)
class _CandidateScan:
    domain: frozenset[State] | None
    total_weight: int | None
    scanned: int
    hard_rejected: int
    learned_rejected: int


def _weights(
    states: tuple[State, ...],
    state_weights: Mapping[State, int] | None,
) -> dict[State, int]:
    result = {
        state: (
            state_weights[state]
            if state_weights is not None and state in state_weights
            else 1
        )
        for state in states
    }
    unknown = (
        set(state_weights) - set(states)
        if state_weights is not None
        else set()
    )
    if unknown:
        raise ValueError(
            f"state weight supplied outside the model: {unknown!r}"
        )
    if any(
        not isinstance(weight, int) or weight <= 0
        for weight in result.values()
    ):
        raise ValueError("state weights must be positive integers")
    return result


def _better_candidate(
    domain: frozenset[State],
    total_weight: int,
    current_domain: frozenset[State] | None,
    current_weight: int | None,
) -> bool:
    if current_domain is None or current_weight is None:
        return True
    if total_weight != current_weight:
        return total_weight > current_weight
    # Match the deterministic tie convention used by the bounded exhaustive
    # optimizer. State values are intentionally ordered through repr because
    # the finite-algebra API permits arbitrary hashable carrier values.
    return repr(sorted(domain, key=repr)) < repr(
        sorted(current_domain, key=repr)
    )


def _best_unblocked_domain(
    states: tuple[State, ...],
    weights: Mapping[State, int],
    required: frozenset[State],
    forbidden: frozenset[State],
    cores: tuple[DomainConflictCore, ...],
) -> _CandidateScan:
    best_domain: frozenset[State] | None = None
    best_weight: int | None = None
    scanned = hard_rejected = learned_rejected = 0

    for mask in range(1 << len(states)):
        scanned += 1
        domain = frozenset(
            state
            for index, state in enumerate(states)
            if mask & (1 << index)
        )
        if not required <= domain or forbidden & domain:
            hard_rejected += 1
            continue
        if any(core.holds(domain) for core in cores):
            learned_rejected += 1
            continue
        total = sum(weights[state] for state in domain)
        if _better_candidate(domain, total, best_domain, best_weight):
            best_domain = domain
            best_weight = total

    return _CandidateScan(
        domain=best_domain,
        total_weight=best_weight,
        scanned=scanned,
        hard_rejected=hard_rejected,
        learned_rejected=learned_rejected,
    )


def maximum_weight_domain_with_learning(
    model: QuasiPrimalDomainModel,
    *,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    state_weights: Mapping[State, int] | None = None,
    exhaustive_state_limit: int = 20,
    max_rounds: int | None = None,
) -> LearnedDomainSearchResult:
    """Find an exact maximum-weight domain by lazy component conflict learning.

    Every learned core is replayed against the compiled component model before
    it can prune another state assignment. Because each verified core blocks
    only domains for which that component has no acceptable candidate,
    learning never removes a feasible domain. Therefore the first feasible
    proposal from the exact best-unblocked state oracle is globally optimal.

    ``max_rounds`` is a fail-closed resource guard. Exceeding it raises rather
    than returning an unproved optimum.
    """

    states = tuple(model.states)
    if len(states) > exhaustive_state_limit:
        raise ValueError(
            "lazy reference optimization disabled above "
            f"{exhaustive_state_limit} states"
        )

    carrier = frozenset(states)
    required = frozenset(required_states)
    forbidden = frozenset(forbidden_states)
    if not required <= carrier or not forbidden <= carrier:
        raise ValueError("required or forbidden state outside the model")
    if required & forbidden:
        raise ValueError("required and forbidden states overlap")
    weights = _weights(states, state_weights)

    state_variables = dict(model.cnf().state_variables)
    cores: list[DomainConflictCore] = []
    clauses: list[tuple[int, ...]] = []
    core_signatures: set[tuple[tuple[State, bool], ...]] = set()
    rounds = model_checks = 0
    scanned = hard_rejected = learned_rejected = 0

    while True:
        if max_rounds is not None and rounds >= max_rounds:
            raise RuntimeError(
                f"lazy domain search exceeded max_rounds={max_rounds}"
            )
        scan = _best_unblocked_domain(
            states,
            weights,
            required,
            forbidden,
            tuple(cores),
        )
        rounds += 1
        scanned += scan.scanned
        hard_rejected += scan.hard_rejected
        learned_rejected += scan.learned_rejected

        if scan.domain is None:
            return LearnedDomainSearchResult(
                optimum=None,
                conflict_cores=tuple(cores),
                blocking_clauses=tuple(clauses),
                stats=LearnedDomainSearchStats(
                    oracle_rounds=rounds,
                    component_model_checks=model_checks,
                    learned_core_count=len(cores),
                    learned_literal_count=sum(
                        len(core.literals) for core in cores
                    ),
                    state_assignments_scanned=scanned,
                    state_assignments_rejected_by_hard_constraints=(
                        hard_rejected
                    ),
                    state_assignments_rejected_by_learned_cores=(
                        learned_rejected
                    ),
                ),
            )

        model_checks += 1
        solution = model.solve_domain(scan.domain)
        if isinstance(solution, CompiledDomainWitness):
            if scan.total_weight is None:
                raise AssertionError("candidate scan lost its objective")
            return LearnedDomainSearchResult(
                optimum=WeightedDomainOptimum(
                    total_weight=scan.total_weight,
                    witness=solution,
                ),
                conflict_cores=tuple(cores),
                blocking_clauses=tuple(clauses),
                stats=LearnedDomainSearchStats(
                    oracle_rounds=rounds,
                    component_model_checks=model_checks,
                    learned_core_count=len(cores),
                    learned_literal_count=sum(
                        len(core.literals) for core in cores
                    ),
                    state_assignments_scanned=scanned,
                    state_assignments_rejected_by_hard_constraints=(
                        hard_rejected
                    ),
                    state_assignments_rejected_by_learned_cores=(
                        learned_rejected
                    ),
                ),
            )
        if not isinstance(solution, CompiledDomainFailure):
            raise AssertionError("domain model returned an unknown result type")

        core = minimize_domain_failure(solution)
        if not core.holds(scan.domain):
            raise AssertionError(
                "learned core does not block its source domain"
            )
        if not verify_domain_conflict_core_against_model(
            model,
            solution,
            core,
            require_minimal=True,
        ):
            raise AssertionError(
                "learned core failed compiled-model replay"
            )

        signature = tuple(
            (literal.state, literal.included)
            for literal in core.literals
        )
        if signature in core_signatures:
            # A repeated complete assignment would already have been rejected
            # by the earlier identical core. Treat repetition as a bug rather
            # than risking a nonterminating learning loop.
            raise AssertionError(
                "duplicate learned core did not block proposal"
            )
        core_signatures.add(signature)
        cores.append(core)
        clause = core.blocking_clause(state_variables)
        if not clause:
            raise AssertionError(
                "empty learned clause would prove global failure"
            )
        clauses.append(clause)

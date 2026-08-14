"""Learn reusable state-literal nogoods from failed component rules.

A ``CompiledDomainFailure`` records, for every candidate rule of one groupoid
component, the conditions violated by the current domain:

- an included forbidden state; or
- an included source whose selected successor is excluded.

Each violation is a small conjunction of signed state literals. Selecting one
violation per candidate and taking their union gives a conflict core whose
conjunction still makes the whole component impossible. Negating that core
produces a sound CNF blocking clause for incremental SAT/MaxSAT search.

The deterministic deletion pass returns a subset-minimal literal core. It is
not claimed to minimize cardinality globally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Mapping

from .domain_model import (
    CompiledDomainFailure,
    QuasiPrimalDomainModel,
)

Value = Hashable
State = tuple[Value, ...]


@dataclass(frozen=True)
class SignedStateLiteral:
    """One state-membership value from the failing domain assignment."""

    state: State
    included: bool

    def holds(self, domain: frozenset[State]) -> bool:
        return (self.state in domain) == self.included


@dataclass(frozen=True)
class CandidateConflictWitness:
    """One violated rule condition retained for a component candidate."""

    candidate_index: int
    condition: tuple[SignedStateLiteral, ...]


@dataclass(frozen=True)
class DomainConflictCore:
    """A subset-minimal conjunction implying one component is impossible."""

    component_index: int
    representative: tuple[Value, ...]
    literals: tuple[SignedStateLiteral, ...]
    candidate_witnesses: tuple[CandidateConflictWitness, ...]

    def holds(self, domain: frozenset[State]) -> bool:
        return all(literal.holds(domain) for literal in self.literals)

    def blocking_clause(self, state_variables: Mapping[State, int]) -> tuple[int, ...]:
        """Negate the core into a CNF clause over state variables."""

        clause = []
        for literal in self.literals:
            if literal.state not in state_variables:
                raise ValueError(
                    f"state missing from CNF variable map: {literal.state!r}"
                )
            variable = state_variables[literal.state]
            clause.append(-variable if literal.included else variable)
        return tuple(clause)


def _literal_key(literal: SignedStateLiteral) -> tuple[str, int]:
    return repr(literal.state), 0 if literal.included else 1


def _condition_key(
    condition: frozenset[SignedStateLiteral],
) -> tuple[int, tuple[tuple[str, int], ...]]:
    return len(condition), tuple(
        sorted((_literal_key(item) for item in condition))
    )


def candidate_violation_conditions(
    failure: CompiledDomainFailure,
) -> dict[int, tuple[frozenset[SignedStateLiteral], ...]]:
    """Translate all recorded rule failures to signed-literal conjunctions."""

    conditions: dict[int, set[frozenset[SignedStateLiteral]]] = {}
    for candidate_index, states in failure.forbidden_hits:
        bucket = conditions.setdefault(candidate_index, set())
        bucket.update(
            frozenset((SignedStateLiteral(state=state, included=True),))
            for state in states
        )
    for candidate_index, edges in failure.missing_closure_edges:
        bucket = conditions.setdefault(candidate_index, set())
        bucket.update(
            frozenset(
                (
                    SignedStateLiteral(state=source, included=True),
                    SignedStateLiteral(state=target, included=False),
                )
            )
            for source, target in edges
        )
    return {
        candidate_index: tuple(sorted(bucket, key=_condition_key))
        for candidate_index, bucket in conditions.items()
    }


def _covers_every_candidate(
    conditions: dict[int, tuple[frozenset[SignedStateLiteral], ...]],
    literals: frozenset[SignedStateLiteral],
) -> bool:
    return all(
        any(condition <= literals for condition in candidate_conditions)
        for candidate_conditions in conditions.values()
    )


def minimize_domain_failure(
    failure: CompiledDomainFailure,
) -> DomainConflictCore:
    """Build a deterministic subset-minimal conflict core.

    The initial core takes the shortest lexicographically first violation for
    each candidate. A deletion pass then removes every literal whose absence
    still leaves at least one complete violation for every candidate.
    """

    conditions = candidate_violation_conditions(failure)
    if not conditions:
        raise ValueError(
            "compiled domain failure contains no candidate violations"
        )
    if any(not candidate_conditions for candidate_conditions in conditions.values()):
        raise ValueError("one failed candidate has no recorded violation")

    core = frozenset(
        literal
        for candidate_conditions in conditions.values()
        for literal in candidate_conditions[0]
    )
    if not _covers_every_candidate(conditions, core):
        raise AssertionError(
            "initial conflict core does not cover every candidate"
        )

    for literal in sorted(core, key=_literal_key, reverse=True):
        reduced = core - {literal}
        if _covers_every_candidate(conditions, reduced):
            core = reduced

    witnesses = []
    for candidate_index in sorted(conditions):
        condition = next(
            condition
            for condition in conditions[candidate_index]
            if condition <= core
        )
        witnesses.append(
            CandidateConflictWitness(
                candidate_index=candidate_index,
                condition=tuple(sorted(condition, key=_literal_key)),
            )
        )

    result = DomainConflictCore(
        component_index=failure.component_index,
        representative=failure.representative,
        literals=tuple(sorted(core, key=_literal_key)),
        candidate_witnesses=tuple(witnesses),
    )
    if not verify_domain_conflict_core(
        failure,
        result,
        require_minimal=True,
    ):
        raise AssertionError("constructed conflict core did not verify")
    return result


def verify_domain_conflict_core(
    failure: CompiledDomainFailure,
    core: DomainConflictCore,
    *,
    require_minimal: bool = False,
) -> bool:
    """Check soundness and optionally subset-minimality from the raw failure."""

    if core.component_index != failure.component_index:
        return False
    if core.representative != failure.representative:
        return False
    literal_set = frozenset(core.literals)
    if len(literal_set) != len(core.literals):
        return False
    if not all(literal.holds(failure.domain) for literal in core.literals):
        return False

    conditions = candidate_violation_conditions(failure)
    if not conditions or not _covers_every_candidate(conditions, literal_set):
        return False
    witnesses = {
        witness.candidate_index: witness
        for witness in core.candidate_witnesses
    }
    if set(witnesses) != set(conditions):
        return False
    for candidate_index, witness in witnesses.items():
        condition = frozenset(witness.condition)
        if (
            condition not in conditions[candidate_index]
            or not condition <= literal_set
        ):
            return False

    if require_minimal:
        for literal in literal_set:
            if _covers_every_candidate(
                conditions,
                literal_set - {literal},
            ):
                return False
    return True


def verify_domain_conflict_core_against_model(
    model: QuasiPrimalDomainModel,
    failure: CompiledDomainFailure,
    core: DomainConflictCore,
    *,
    require_minimal: bool = False,
) -> bool:
    """Replay the raw failure from the model before trusting its learned core.

    This is the stronger proof-carrying boundary. It prevents a malformed or
    stale ``CompiledDomainFailure`` from manufacturing a clause that is only
    self-consistent with its own recorded fields. The deterministic model must
    reproduce the complete failure object for the same domain, after which the
    ordinary conflict verifier checks the core.
    """

    replay = model.solve_domain(failure.domain)
    if replay != failure:
        return False
    return verify_domain_conflict_core(
        failure,
        core,
        require_minimal=require_minimal,
    )

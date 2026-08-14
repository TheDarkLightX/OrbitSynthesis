"""Independent authorities for external OrbitSynthesis optimization results.

External SAT, MaxSAT, and MILP engines are useful search oracles, but an
optimal model is not by itself a proof that no better controller exists.  This
module records small, replayable authorities that can strengthen a verified
model certificate:

* a bounded exhaustive search over a restricted state carrier; or
* a closed-form structural theorem supplying the complete optimum family.

Every authority is bound to a deterministic fingerprint of the complete
internal-groupoid component model and of its objective/hard-state problem.
A solver result is promoted only after its domain, signed utility, and
controller witness replay against that exact model.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
import hashlib
import json
from typing import Hashable, Iterable, Mapping

from .domain_model import (
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
)
from .external_optimization import ExternalOptimizationResult

Value = Hashable
State = tuple[Value, ...]


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=repr,
    ).encode("utf-8")


def _stable_domains(
    domains: Iterable[frozenset[State]],
    state_order: tuple[State, ...],
) -> tuple[frozenset[State], ...]:
    unique = set(domains)
    return tuple(
        sorted(
            unique,
            key=lambda domain: tuple(
                int(state in domain) for state in state_order
            ),
            reverse=True,
        )
    )


@lru_cache(maxsize=32)
def domain_model_sha256(model: QuasiPrimalDomainModel) -> str:
    """Hash all states, observations, components, rules, and assignments."""

    payload = {
        "states": [list(state) for state in model.states],
        "observations": [list(observation) for observation in model.observations],
        "components": [
            {
                "representative": list(component.representative),
                "observations": [
                    list(observation) for observation in component.observations
                ],
                "candidates": [
                    {
                        "representative_output": list(
                            candidate.representative_output
                        ),
                        "assignment": [
                            {
                                "observation": list(observation),
                                "output": list(output),
                            }
                            for observation, output in candidate.assignment_items
                        ],
                        "forbidden_states": [
                            list(state)
                            for state in sorted(
                                candidate.forbidden_states,
                                key=repr,
                            )
                        ],
                        "closure_edges": [
                            {
                                "source": list(source),
                                "target": list(target),
                            }
                            for source, target in sorted(
                                candidate.closure_edges,
                                key=repr,
                            )
                        ],
                    }
                    for candidate in component.candidates
                ],
            }
            for component in model.components
        ],
    }
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _objective_problem_sha256(
    model: QuasiPrimalDomainModel,
    *,
    state_weights: Mapping[State, int] | None,
    default_weight: int,
    required_states: Iterable[State],
    forbidden_states: Iterable[State],
    tag: str,
) -> str:
    supplied = {} if state_weights is None else dict(state_weights)
    required = frozenset(required_states)
    forbidden = frozenset(forbidden_states)
    payload = {
        "tag": tag,
        "model_sha256": domain_model_sha256(model),
        "weights": [
            supplied.get(state, default_weight)
            for state in model.states
        ],
        "required": [
            list(state)
            for state in model.states
            if state in required
        ],
        "forbidden": [
            list(state)
            for state in model.states
            if state in forbidden
        ],
    }
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


@dataclass(frozen=True)
class ObjectiveAuthority:
    """A model-bound certificate for one primary signed-utility optimum.

    ``optimum_score=None`` means the authority exhaustively established
    infeasibility.  Otherwise ``optimum_domains`` is the complete set of
    primary-score maximizers known to this authority.  Secondary cardinality
    or mask tie-breaking is intentionally not imported into the external
    MaxSAT trust boundary.
    """

    name: str
    model_sha256: str
    problem_sha256: str
    state_order: tuple[State, ...]
    optimum_score: int | None
    optimum_domains: tuple[frozenset[State], ...]
    assignments_checked: int
    feasible_domains_checked: int
    evidence_items: tuple[tuple[str, object], ...] = ()

    @property
    def evidence(self) -> dict[str, object]:
        return dict(self.evidence_items)

    @property
    def semantic_sha256(self) -> str:
        payload = {
            "name": self.name,
            "model_sha256": self.model_sha256,
            "problem_sha256": self.problem_sha256,
            "state_order": [list(state) for state in self.state_order],
            "optimum_score": self.optimum_score,
            "optimum_domains": [
                [list(state) for state in self.state_order if state in domain]
                for domain in self.optimum_domains
            ],
            "assignments_checked": self.assignments_checked,
            "feasible_domains_checked": self.feasible_domains_checked,
            "evidence": self.evidence,
        }
        return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def closed_form_objective_authority(
    *,
    name: str,
    model: QuasiPrimalDomainModel,
    optimum_score: int,
    optimum_domains: Iterable[frozenset[State]],
    state_weights: Mapping[State, int] | None,
    default_weight: int = 0,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    evidence: Mapping[str, object] | None = None,
) -> ObjectiveAuthority:
    """Record a structural theorem's explicitly enumerated optimum family."""

    order = tuple(model.states)
    domains = _stable_domains(optimum_domains, order)
    if not domains:
        raise ValueError("a finite optimum score needs at least one domain")
    carrier = frozenset(order)
    if any(not domain <= carrier for domain in domains):
        raise ValueError("closed-form optimum domain leaves the state carrier")
    model_hash = domain_model_sha256(model)
    problem_hash = _objective_problem_sha256(
        model,
        state_weights=state_weights,
        default_weight=default_weight,
        required_states=required_states,
        forbidden_states=forbidden_states,
        tag=name,
    )
    return ObjectiveAuthority(
        name=name,
        model_sha256=model_hash,
        problem_sha256=problem_hash,
        state_order=order,
        optimum_score=optimum_score,
        optimum_domains=domains,
        assignments_checked=0,
        feasible_domains_checked=len(domains),
        evidence_items=tuple(sorted((evidence or {}).items())),
    )


def bounded_domain_objective_authority(
    model: QuasiPrimalDomainModel,
    *,
    allowed_states: Iterable[State],
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    state_weights: Mapping[State, int] | None = None,
    default_weight: int = 0,
    max_free_states: int = 20,
    name: str = "bounded_domain_enumeration",
) -> ObjectiveAuthority:
    """Exhaust every domain inside a small allowed carrier.

    States outside ``allowed_states`` are fixed absent.  Required and forbidden
    states are fixed before enumeration, so the exponential parameter is only
    the remaining free part of the allowed carrier.  Every feasible domain is
    replayed through the exact component model.
    """

    if not isinstance(default_weight, int):
        raise TypeError("default_weight must be an integer")
    order = tuple(model.states)
    carrier = frozenset(order)
    allowed = frozenset(allowed_states)
    required = frozenset(required_states)
    forbidden = frozenset(forbidden_states) | (carrier - allowed)
    if not allowed <= carrier:
        raise ValueError("allowed state outside model")
    if not required <= allowed:
        raise ValueError("required state is not allowed")
    if required & forbidden:
        raise ValueError("required and forbidden states overlap")

    supplied = {} if state_weights is None else dict(state_weights)
    unknown = set(supplied) - carrier
    if unknown:
        raise ValueError(
            f"state weight outside model: {min(unknown, key=repr)!r}"
        )
    if any(not isinstance(weight, int) for weight in supplied.values()):
        raise TypeError("all state weights must be integers")

    free = tuple(
        state
        for state in order
        if state in allowed and state not in required and state not in forbidden
    )
    if len(free) > max_free_states:
        raise ValueError(
            "bounded authority disabled above "
            f"{max_free_states} free states; received {len(free)}"
        )

    best_score: int | None = None
    best_domains: list[frozenset[State]] = []
    feasible_count = 0
    assignments_checked = 1 << len(free)
    for mask in range(assignments_checked):
        domain = frozenset(
            set(required)
            | {
                state
                for index, state in enumerate(free)
                if mask & (1 << index)
            }
        )
        solution = model.solve_domain(domain)
        if not isinstance(solution, CompiledDomainWitness):
            continue
        feasible_count += 1
        score = sum(
            supplied.get(state, default_weight)
            for state in domain
        )
        if best_score is None or score > best_score:
            best_score = score
            best_domains = [domain]
        elif score == best_score:
            best_domains.append(domain)

    model_hash = domain_model_sha256(model)
    problem_hash = _objective_problem_sha256(
        model,
        state_weights=supplied,
        default_weight=default_weight,
        required_states=required,
        forbidden_states=forbidden,
        tag=name,
    )
    return ObjectiveAuthority(
        name=name,
        model_sha256=model_hash,
        problem_sha256=problem_hash,
        state_order=order,
        optimum_score=best_score,
        optimum_domains=_stable_domains(best_domains, order),
        assignments_checked=assignments_checked,
        feasible_domains_checked=feasible_count,
        evidence_items=(
            ("allowed_state_count", len(allowed)),
            ("free_state_count", len(free)),
            ("required_state_count", len(required)),
            ("fixed_forbidden_state_count", len(forbidden)),
        ),
    )


def _witness_matches_model(
    model: QuasiPrimalDomainModel,
    witness: CompiledDomainWitness,
) -> bool:
    if len(witness.component_choices) != len(model.components):
        return False
    strategy = {}
    for component, candidate_index in zip(
        model.components,
        witness.component_choices,
        strict=True,
    ):
        if not 0 <= candidate_index < len(component.candidates):
            return False
        candidate = component.candidates[candidate_index]
        if not candidate.accepts(witness.domain):
            return False
        strategy.update(candidate.assignment)
    return (
        set(strategy) == set(model.observations)
        and tuple(sorted(strategy.items(), key=lambda item: repr(item[0])))
        == witness.strategy_items
    )


def certify_external_result(
    result: ExternalOptimizationResult,
    authority: ObjectiveAuthority,
    *,
    model: QuasiPrimalDomainModel,
) -> ExternalOptimizationResult:
    """Promote an external result only after exact model/authority agreement."""

    current_model_hash = domain_model_sha256(model)
    if current_model_hash != authority.model_sha256:
        raise ValueError("authority is bound to a different component model")

    metadata = result.metadata
    metadata["authority_sha256"] = authority.semantic_sha256
    metadata["authority_model_sha256"] = authority.model_sha256
    metadata["authority_problem_sha256"] = authority.problem_sha256
    metadata["authority_assignments_checked"] = authority.assignments_checked

    if authority.optimum_score is None:
        if result.status != "infeasible":
            raise ValueError(
                "authority established infeasibility but backend returned "
                f"{result.status!r}"
            )
        return replace(
            result,
            optimality_authority=authority.name,
            metadata_items=tuple(sorted(metadata.items())),
        )

    if result.status != "optimal":
        raise ValueError(
            f"finite optimum authority requires optimal status, got {result.status!r}"
        )
    if not result.certificate_verified or result.witness is None:
        raise ValueError("backend returned no verified controller certificate")
    if not _witness_matches_model(model, result.witness):
        raise ValueError("backend controller witness does not replay on authority model")
    if result.signed_utility != authority.optimum_score:
        raise ValueError(
            "backend utility disagrees with authority: "
            f"{result.signed_utility}!={authority.optimum_score}"
        )
    if result.witness.domain not in authority.optimum_domains:
        raise ValueError("backend domain is not in the authority optimum family")
    return replace(
        result,
        optimality_authority=authority.name,
        metadata_items=tuple(sorted(metadata.items())),
    )

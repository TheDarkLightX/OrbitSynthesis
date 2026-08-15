"""Portable state-only optimality and infeasibility certificates.

An external MaxSAT or MILP model proves that one controller/domain is feasible,
but an ``OPTIMUM FOUND`` line is not itself a checkable proof that no better
controller exists.  This module supplies a backend-independent exact proof
object over the compiled internal-groupoid domain model.

The certificate is a finite binary search tree over state-membership bits.
Every leaf is justified in one of two ways:

* one groupoid component has no candidate rule compatible with the partial
  state assignment; or
* the exact optimistic signed-utility bound is at most the claimed optimum.

For an infeasibility certificate, bound leaves are forbidden and every branch
must end in a component conflict.  Verification checks the complete tree,
recomputes every conflict and bound, and replays a feasible optimum domain.
It does not rerun the optimizer that produced the original answer.

Certificates may be exponential in the worst case.  They are intended as a
proof-carrying fallback, a calibration authority, and a foundation for future
compressed proof traces—not as a polynomial-time optimization claim.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Hashable, Iterable, Mapping

from .domain_model import (
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
)
from .external_optimization import ExternalOptimizationResult
from .optimization_authority import domain_model_sha256

Value = Hashable
State = tuple[Value, ...]
_SCHEMA = "orbit-synthesis/state-search-optimality/v1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=repr,
    ).encode("utf-8")


def _mask(states: tuple[State, ...], selected: Iterable[State]) -> int:
    index = {state: position for position, state in enumerate(states)}
    chosen = frozenset(selected)
    unknown = chosen - set(index)
    if unknown:
        raise ValueError(f"state outside model: {min(unknown, key=repr)!r}")
    result = 0
    for state in chosen:
        result |= 1 << index[state]
    return result


def _weight_tuple(
    states: tuple[State, ...],
    state_weights: Mapping[State, int] | None,
    default_weight: int,
) -> tuple[int, ...]:
    if not isinstance(default_weight, int):
        raise TypeError("default_weight must be an integer")
    supplied = {} if state_weights is None else dict(state_weights)
    unknown = set(supplied) - set(states)
    if unknown:
        raise ValueError(f"state weight outside model: {min(unknown, key=repr)!r}")
    if any(not isinstance(weight, int) for weight in supplied.values()):
        raise TypeError("all state weights must be integers")
    return tuple(supplied.get(state, default_weight) for state in states)


def _score(mask: int, weights: tuple[int, ...]) -> int:
    total = 0
    remaining = mask
    while remaining:
        low = remaining & -remaining
        total += weights[low.bit_length() - 1]
        remaining ^= low
    return total


def _problem_sha256(
    model_hash: str,
    weights: tuple[int, ...],
    required_mask: int,
    forbidden_mask: int,
) -> str:
    return hashlib.sha256(
        _canonical_bytes(
            {
                "schema": _SCHEMA,
                "model_sha256": model_hash,
                "weights": list(weights),
                "required_mask": required_mask,
                "forbidden_mask": forbidden_mask,
            }
        )
    ).hexdigest()


@dataclass(frozen=True)
class StateSearchProofNode:
    """One node in a state-membership proof tree."""

    kind: str
    state_index: int | None = None
    include_child: int | None = None
    exclude_child: int | None = None
    component_index: int | None = None
    upper_bound: int | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "state_index": self.state_index,
            "include_child": self.include_child,
            "exclude_child": self.exclude_child,
            "component_index": self.component_index,
            "upper_bound": self.upper_bound,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "StateSearchProofNode":
        return cls(
            kind=str(payload["kind"]),
            state_index=(
                None
                if payload.get("state_index") is None
                else int(payload["state_index"])
            ),
            include_child=(
                None
                if payload.get("include_child") is None
                else int(payload["include_child"])
            ),
            exclude_child=(
                None
                if payload.get("exclude_child") is None
                else int(payload["exclude_child"])
            ),
            component_index=(
                None
                if payload.get("component_index") is None
                else int(payload["component_index"])
            ),
            upper_bound=(
                None
                if payload.get("upper_bound") is None
                else int(payload["upper_bound"])
            ),
        )


@dataclass(frozen=True)
class StateSearchCertificate:
    """A model-bound proof of one primary optimum or of infeasibility."""

    model_sha256: str
    problem_sha256: str
    state_count: int
    weights: tuple[int, ...]
    required_mask: int
    forbidden_mask: int
    target_score: int | None
    target_domain_mask: int | None
    root: int
    nodes: tuple[StateSearchProofNode, ...]

    @property
    def claim(self) -> str:
        return "infeasible" if self.target_score is None else "optimal"

    @property
    def statistics(self) -> dict[str, int]:
        return {
            "nodes": len(self.nodes),
            "branches": sum(node.kind == "branch" for node in self.nodes),
            "conflict_leaves": sum(node.kind == "conflict" for node in self.nodes),
            "bound_leaves": sum(node.kind == "bound" for node in self.nodes),
        }

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _SCHEMA,
            "model_sha256": self.model_sha256,
            "problem_sha256": self.problem_sha256,
            "state_count": self.state_count,
            "weights": list(self.weights),
            "required_mask": self.required_mask,
            "forbidden_mask": self.forbidden_mask,
            "target_score": self.target_score,
            "target_domain_mask": self.target_domain_mask,
            "root": self.root,
            "nodes": [node.as_dict() for node in self.nodes],
        }

    @property
    def semantic_sha256(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.semantic_payload())).hexdigest()

    def as_dict(self) -> dict[str, object]:
        payload = self.semantic_payload()
        payload["semantic_sha256"] = self.semantic_sha256
        payload["statistics"] = self.statistics
        return payload

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, sort_keys=True) + "\n"

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "StateSearchCertificate":
        if payload.get("schema") != _SCHEMA:
            raise ValueError("unsupported state-search certificate schema")
        nodes_payload = payload.get("nodes")
        if not isinstance(nodes_payload, list):
            raise TypeError("certificate nodes must be a list")
        certificate = cls(
            model_sha256=str(payload["model_sha256"]),
            problem_sha256=str(payload["problem_sha256"]),
            state_count=int(payload["state_count"]),
            weights=tuple(int(value) for value in payload["weights"]),  # type: ignore[index]
            required_mask=int(payload["required_mask"]),
            forbidden_mask=int(payload["forbidden_mask"]),
            target_score=(
                None
                if payload.get("target_score") is None
                else int(payload["target_score"])
            ),
            target_domain_mask=(
                None
                if payload.get("target_domain_mask") is None
                else int(payload["target_domain_mask"])
            ),
            root=int(payload["root"]),
            nodes=tuple(
                StateSearchProofNode.from_dict(node)  # type: ignore[arg-type]
                for node in nodes_payload
            ),
        )
        recorded = payload.get("semantic_sha256")
        if recorded is not None and str(recorded) != certificate.semantic_sha256:
            raise ValueError("state-search certificate semantic hash mismatch")
        return certificate

    @classmethod
    def from_json(cls, text: str) -> "StateSearchCertificate":
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise TypeError("certificate JSON must contain one object")
        return cls.from_dict(payload)


@dataclass(frozen=True)
class _CompiledCandidate:
    forbidden_mask: int
    closure_edges: tuple[tuple[int, int], ...]


def _compile_candidates(
    model: QuasiPrimalDomainModel,
) -> tuple[tuple[_CompiledCandidate, ...], ...]:
    index = {state: position for position, state in enumerate(model.states)}
    components = []
    for component in model.components:
        candidates = []
        for candidate in component.candidates:
            forbidden = 0
            for state in candidate.forbidden_states:
                forbidden |= 1 << index[state]
            edges = tuple(
                (1 << index[source], 1 << index[target])
                for source, target in candidate.closure_edges
            )
            candidates.append(
                _CompiledCandidate(
                    forbidden_mask=forbidden,
                    closure_edges=edges,
                )
            )
        components.append(tuple(candidates))
    return tuple(components)


def _candidate_viable(
    candidate: _CompiledCandidate,
    included: int,
    excluded: int,
) -> bool:
    if candidate.forbidden_mask & included:
        return False
    return all(
        not (included & source_bit) or not (excluded & target_bit)
        for source_bit, target_bit in candidate.closure_edges
    )


def _conflicting_component(
    components: tuple[tuple[_CompiledCandidate, ...], ...],
    included: int,
    excluded: int,
) -> int | None:
    for component_index, component in enumerate(components):
        if not any(
            _candidate_viable(candidate, included, excluded)
            for candidate in component
        ):
            return component_index
    return None


def _upper_bound(
    included: int,
    excluded: int,
    all_mask: int,
    weights: tuple[int, ...],
) -> int:
    total = _score(included, weights)
    undecided = all_mask & ~(included | excluded)
    remaining = undecided
    while remaining:
        low = remaining & -remaining
        weight = weights[low.bit_length() - 1]
        if weight > 0:
            total += weight
        remaining ^= low
    return total


def _state_impacts(
    state_count: int,
    components: tuple[tuple[_CompiledCandidate, ...], ...],
) -> tuple[int, ...]:
    impacts = [0] * state_count
    for component in components:
        for candidate in component:
            remaining = candidate.forbidden_mask
            while remaining:
                low = remaining & -remaining
                impacts[low.bit_length() - 1] += 4
                remaining ^= low
            for source_bit, target_bit in candidate.closure_edges:
                impacts[source_bit.bit_length() - 1] += 1
                impacts[target_bit.bit_length() - 1] += 1
    return tuple(impacts)


def _witness_replays(
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


def generate_state_search_certificate(
    model: QuasiPrimalDomainModel,
    *,
    target_domain: Iterable[State] | None,
    state_weights: Mapping[State, int] | None = None,
    default_weight: int = 1,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    max_nodes: int = 1_000_000,
) -> StateSearchCertificate:
    """Generate an exact primary-optimum or infeasibility proof tree.

    ``target_domain=None`` requests an infeasibility certificate.  Otherwise
    the target must replay as a feasible component-domain witness, and the tree
    proves that no feasible domain has larger signed utility.
    """

    if max_nodes < 1:
        raise ValueError("max_nodes must be positive")
    states = tuple(model.states)
    state_count = len(states)
    all_mask = (1 << state_count) - 1
    weights = _weight_tuple(states, state_weights, default_weight)
    required_mask = _mask(states, required_states)
    forbidden_mask = _mask(states, forbidden_states)
    if required_mask & forbidden_mask:
        raise ValueError("required and forbidden states overlap")

    target_mask: int | None
    target_score: int | None
    if target_domain is None:
        target_mask = None
        target_score = None
    else:
        target = frozenset(target_domain)
        target_mask = _mask(states, target)
        if required_mask & ~target_mask or forbidden_mask & target_mask:
            raise ValueError("target domain violates hard state constraints")
        target_witness = model.solve_domain(target)
        if not isinstance(target_witness, CompiledDomainWitness):
            raise ValueError("target domain is not clone-compatible")
        target_score = _score(target_mask, weights)

    components = _compile_candidates(model)
    impacts = _state_impacts(state_count, components)
    nodes: list[StateSearchProofNode | None] = []

    def choose_state(included: int, excluded: int) -> int:
        undecided = all_mask & ~(included | excluded)
        return max(
            (
                index
                for index in range(state_count)
                if undecided & (1 << index)
            ),
            key=lambda index: (
                impacts[index],
                abs(weights[index]),
                weights[index],
                -index,
            ),
        )

    def build(included: int, excluded: int) -> int:
        if len(nodes) >= max_nodes:
            raise ValueError(
                "state-search certificate exceeded max_nodes="
                f"{max_nodes}"
            )
        conflict = _conflicting_component(components, included, excluded)
        if conflict is not None:
            index = len(nodes)
            nodes.append(
                StateSearchProofNode(
                    kind="conflict",
                    component_index=conflict,
                )
            )
            return index

        upper = _upper_bound(included, excluded, all_mask, weights)
        if target_score is not None and upper <= target_score:
            index = len(nodes)
            nodes.append(
                StateSearchProofNode(
                    kind="bound",
                    upper_bound=upper,
                )
            )
            return index

        if (included | excluded) == all_mask:
            score = _score(included, weights)
            if target_score is None:
                raise ValueError(
                    "infeasibility claim is false; found feasible domain "
                    f"with score {score}"
                )
            raise ValueError(
                "target is not optimal; found feasible domain with score "
                f"{score}>{target_score}"
            )

        state_index = choose_state(included, excluded)
        bit = 1 << state_index
        node_index = len(nodes)
        nodes.append(None)
        include_child = build(included | bit, excluded)
        exclude_child = build(included, excluded | bit)
        nodes[node_index] = StateSearchProofNode(
            kind="branch",
            state_index=state_index,
            include_child=include_child,
            exclude_child=exclude_child,
        )
        return node_index

    root = build(required_mask, forbidden_mask)
    completed = tuple(node for node in nodes if node is not None)
    if len(completed) != len(nodes):
        raise AssertionError("incomplete state-search proof tree")
    model_hash = domain_model_sha256(model)
    return StateSearchCertificate(
        model_sha256=model_hash,
        problem_sha256=_problem_sha256(
            model_hash,
            weights,
            required_mask,
            forbidden_mask,
        ),
        state_count=state_count,
        weights=weights,
        required_mask=required_mask,
        forbidden_mask=forbidden_mask,
        target_score=target_score,
        target_domain_mask=target_mask,
        root=root,
        nodes=completed,
    )


def verify_state_search_certificate(
    model: QuasiPrimalDomainModel,
    certificate: StateSearchCertificate,
) -> bool:
    """Verify a certificate without rerunning its generating optimizer."""

    try:
        state_count = len(model.states)
        all_mask = (1 << state_count) - 1
        if certificate.state_count != state_count:
            return False
        if len(certificate.weights) != state_count:
            return False
        if certificate.required_mask & certificate.forbidden_mask:
            return False
        if (certificate.required_mask | certificate.forbidden_mask) & ~all_mask:
            return False
        model_hash = domain_model_sha256(model)
        if certificate.model_sha256 != model_hash:
            return False
        if certificate.problem_sha256 != _problem_sha256(
            model_hash,
            certificate.weights,
            certificate.required_mask,
            certificate.forbidden_mask,
        ):
            return False
        if not certificate.nodes or not 0 <= certificate.root < len(certificate.nodes):
            return False

        if certificate.target_score is None:
            if certificate.target_domain_mask is not None:
                return False
        else:
            target_mask = certificate.target_domain_mask
            if target_mask is None or target_mask & ~all_mask:
                return False
            if certificate.required_mask & ~target_mask:
                return False
            if certificate.forbidden_mask & target_mask:
                return False
            if _score(target_mask, certificate.weights) != certificate.target_score:
                return False
            target_domain = frozenset(
                state
                for index, state in enumerate(model.states)
                if target_mask & (1 << index)
            )
            target_witness = model.solve_domain(target_domain)
            if not isinstance(target_witness, CompiledDomainWitness):
                return False

        components = _compile_candidates(model)
        seen: set[int] = set()
        stack = [
            (
                certificate.root,
                certificate.required_mask,
                certificate.forbidden_mask,
            )
        ]
        while stack:
            node_index, included, excluded = stack.pop()
            if node_index in seen:
                return False
            if not 0 <= node_index < len(certificate.nodes):
                return False
            seen.add(node_index)
            if included & excluded or (included | excluded) & ~all_mask:
                return False
            node = certificate.nodes[node_index]
            conflict = _conflicting_component(components, included, excluded)

            if node.kind == "conflict":
                if any(
                    value is not None
                    for value in (
                        node.state_index,
                        node.include_child,
                        node.exclude_child,
                        node.upper_bound,
                    )
                ):
                    return False
                if node.component_index is None:
                    return False
                if not 0 <= node.component_index < len(components):
                    return False
                if any(
                    _candidate_viable(candidate, included, excluded)
                    for candidate in components[node.component_index]
                ):
                    return False
                continue

            if node.kind == "bound":
                if certificate.target_score is None:
                    return False
                if any(
                    value is not None
                    for value in (
                        node.state_index,
                        node.include_child,
                        node.exclude_child,
                        node.component_index,
                    )
                ):
                    return False
                upper = _upper_bound(
                    included,
                    excluded,
                    all_mask,
                    certificate.weights,
                )
                if node.upper_bound != upper or upper > certificate.target_score:
                    return False
                continue

            if node.kind != "branch":
                return False
            if conflict is not None:
                return False
            if certificate.target_score is not None:
                upper = _upper_bound(
                    included,
                    excluded,
                    all_mask,
                    certificate.weights,
                )
                if upper <= certificate.target_score:
                    return False
            if any(
                value is not None
                for value in (node.component_index, node.upper_bound)
            ):
                return False
            if node.state_index is None:
                return False
            if not 0 <= node.state_index < state_count:
                return False
            bit = 1 << node.state_index
            if (included | excluded) & bit:
                return False
            if node.include_child is None or node.exclude_child is None:
                return False
            stack.append((node.exclude_child, included, excluded | bit))
            stack.append((node.include_child, included | bit, excluded))

        return len(seen) == len(certificate.nodes)
    except (KeyError, TypeError, ValueError):
        return False


def certify_external_result_with_state_search(
    result: ExternalOptimizationResult,
    certificate: StateSearchCertificate,
    *,
    model: QuasiPrimalDomainModel,
) -> ExternalOptimizationResult:
    """Promote a backend result using a verified state-search proof tree."""

    if not verify_state_search_certificate(model, certificate):
        raise ValueError("invalid state-search optimality certificate")
    metadata = result.metadata
    metadata.update(
        {
            "state_search_certificate_sha256": certificate.semantic_sha256,
            "state_search_nodes": len(certificate.nodes),
            "state_search_problem_sha256": certificate.problem_sha256,
        }
    )

    if certificate.target_score is None:
        if result.status != "infeasible":
            raise ValueError(
                "state-search certificate proves infeasibility but backend "
                f"returned {result.status!r}"
            )
        return replace(
            result,
            optimality_authority="state_search_infeasibility",
            metadata_items=tuple(sorted(metadata.items())),
        )

    if result.status != "optimal":
        raise ValueError(
            f"state-search optimum requires optimal status, got {result.status!r}"
        )
    if not result.certificate_verified or result.witness is None:
        raise ValueError("backend returned no verified controller witness")
    if not _witness_replays(model, result.witness):
        raise ValueError("backend controller witness does not replay on model")
    result_mask = _mask(model.states, result.witness.domain)
    if certificate.required_mask & ~result_mask:
        raise ValueError("backend optimum omits a required state")
    if certificate.forbidden_mask & result_mask:
        raise ValueError("backend optimum contains a forbidden state")
    utility = _score(result_mask, certificate.weights)
    if utility != certificate.target_score:
        raise ValueError(
            "backend utility disagrees with state-search certificate: "
            f"{utility}!={certificate.target_score}"
        )
    if result.signed_utility != utility:
        raise ValueError("backend signed utility does not match its domain")
    return replace(
        result,
        optimality_authority="state_search_certificate",
        metadata_items=tuple(sorted(metadata.items())),
    )

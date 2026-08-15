"""Portable proof bundles for finite clone-constrained safety synthesis.

A bundle contains the canonical input problem, the compiled-model fingerprint,
one complete controller witness when feasible, and an independently checkable
state-search certificate for optimality or infeasibility.

Optimization backends are untrusted search oracles. Bundle verification
rebuilds the finite algebra, safety game, and internal-groupoid component model;
replays the controller; recomputes the signed objective; and verifies the
state-search proof tree.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from .domain_model import (
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
    compile_quasi_primal_domain_model,
)
from .domain_optimization import optimize_weighted_domain
from .external_optimization import (
    ExternalOptimizationError,
    solve_weighted_cnf_highs,
)
from .optimization_authority import domain_model_sha256
from .pointed_kernel import CompiledParameterizedKernel
from .problem_io import FiniteSafetyProblem, State
from .state_optimality_certificate import (
    StateSearchCertificate,
    generate_state_search_certificate,
    verify_state_search_certificate,
)

_SCHEMA = "orbit-synthesis/proof-bundle/v1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _state_rows(states: Iterable[State]) -> list[list[object]]:
    return [list(state) for state in sorted(states, key=repr)]


def _parse_row(
    value: object,
    *,
    length: int,
    carrier: frozenset[object],
    field: str,
) -> tuple[object, ...]:
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{field} must be a row of length {length}")
    if any(
        isinstance(item, bool) or not isinstance(item, (int, str))
        for item in value
    ):
        raise TypeError(f"{field} must contain only JSON integers or strings")
    row = tuple(value)
    if not set(row) <= carrier:
        raise ValueError(f"{field} contains a value outside the carrier")
    return row


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


def _signed_score(
    states: tuple[State, ...],
    domain: frozenset[State],
    weights: Mapping[State, int],
    default_weight: int,
) -> int:
    return sum(
        weights.get(state, default_weight)
        for state in states
        if state in domain
    )


def _problem_certificate_binding(
    problem: FiniteSafetyProblem,
    model: QuasiPrimalDomainModel,
    certificate: StateSearchCertificate,
) -> bool:
    expected_weights = tuple(
        problem.state_weights.get(state, problem.default_weight)
        for state in model.states
    )
    state_index = {state: index for index, state in enumerate(model.states)}
    required_mask = sum(
        1 << state_index[state] for state in problem.required_states
    )
    forbidden_mask = sum(
        1 << state_index[state] for state in problem.forbidden_states
    )
    return (
        certificate.weights == expected_weights
        and certificate.required_mask == required_mask
        and certificate.forbidden_mask == forbidden_mask
    )


@dataclass(frozen=True)
class ProofBundle:
    """One portable synthesis result and its proof-carrying evidence."""

    problem: FiniteSafetyProblem
    problem_sha256: str
    component_model_sha256: str
    status: str
    backend: str
    domain: frozenset[State] | None
    signed_utility: int | None
    component_choices: tuple[int, ...]
    strategy_items: tuple[tuple[tuple[object, ...], State], ...]
    backend_semantic_sha256: str | None
    optimality_certificate: StateSearchCertificate
    metadata_items: tuple[tuple[str, object], ...] = ()

    @property
    def metadata(self) -> dict[str, object]:
        return dict(self.metadata_items)

    @property
    def strategy(self) -> dict[tuple[object, ...], State]:
        return dict(self.strategy_items)

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _SCHEMA,
            "problem": self.problem.semantic_payload(),
            "problem_sha256": self.problem_sha256,
            "component_model_sha256": self.component_model_sha256,
            "result": {
                "status": self.status,
                "backend": self.backend,
                "domain": (
                    None if self.domain is None else _state_rows(self.domain)
                ),
                "signed_utility": self.signed_utility,
                "component_choices": list(self.component_choices),
                "strategy": [
                    {
                        "observation": list(observation),
                        "output": list(output),
                    }
                    for observation, output in self.strategy_items
                ],
                "backend_semantic_sha256": self.backend_semantic_sha256,
            },
            "optimality_certificate": self.optimality_certificate.as_dict(),
            "metadata": self.metadata,
        }

    @property
    def manifest_sha256(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.semantic_payload())).hexdigest()

    def as_dict(self) -> dict[str, object]:
        payload = self.semantic_payload()
        payload["manifest_sha256"] = self.manifest_sha256
        return payload

    def to_json(self) -> str:
        return json.dumps(
            self.as_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n"

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ProofBundle":
        if payload.get("schema") != _SCHEMA:
            raise ValueError("unsupported proof-bundle schema")
        problem_payload = payload.get("problem")
        if not isinstance(problem_payload, Mapping):
            raise TypeError("bundle problem must be a JSON object")
        problem = FiniteSafetyProblem.from_dict(problem_payload)

        result = payload.get("result")
        if not isinstance(result, Mapping):
            raise TypeError("bundle result must be a JSON object")
        status = result.get("status")
        backend = result.get("backend")
        if status not in {"optimal", "infeasible"}:
            raise ValueError("bundle result status must be optimal or infeasible")
        if not isinstance(backend, str) or not backend:
            raise ValueError("bundle backend must be a nonempty string")

        carrier = frozenset(problem.algebra.values)
        domain_payload = result.get("domain")
        if domain_payload is None:
            domain = None
        else:
            if not isinstance(domain_payload, list):
                raise TypeError("bundle result domain must be a list or null")
            parsed = [
                _parse_row(
                    row,
                    length=problem.state_arity,
                    carrier=carrier,
                    field="bundle result domain",
                )
                for row in domain_payload
            ]
            if len(set(parsed)) != len(parsed):
                raise ValueError("bundle result domain contains duplicates")
            domain = frozenset(parsed)

        utility = result.get("signed_utility")
        if utility is not None and (
            isinstance(utility, bool) or not isinstance(utility, int)
        ):
            raise TypeError("bundle signed utility must be an integer or null")

        choices_payload = result.get("component_choices", [])
        if not isinstance(choices_payload, list):
            raise TypeError("component_choices must be a JSON list")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in choices_payload
        ):
            raise TypeError(
                "component_choices must contain nonnegative integers"
            )
        choices = tuple(choices_payload)

        strategy_payload = result.get("strategy", [])
        if not isinstance(strategy_payload, list):
            raise TypeError("strategy must be a JSON list")
        strategy = []
        observation_arity = problem.state_arity + problem.input_arity
        seen_observations = set()
        for index, row in enumerate(strategy_payload):
            if not isinstance(row, Mapping):
                raise TypeError(f"strategy row {index} must be a JSON object")
            observation = _parse_row(
                row.get("observation"),
                length=observation_arity,
                carrier=carrier,
                field=f"strategy row {index}.observation",
            )
            output = _parse_row(
                row.get("output"),
                length=problem.state_arity,
                carrier=carrier,
                field=f"strategy row {index}.output",
            )
            if observation in seen_observations:
                raise ValueError("strategy contains a duplicate observation")
            seen_observations.add(observation)
            strategy.append((observation, output))

        certificate_payload = payload.get("optimality_certificate")
        if not isinstance(certificate_payload, Mapping):
            raise TypeError("optimality_certificate must be a JSON object")
        certificate = StateSearchCertificate.from_dict(certificate_payload)

        metadata = payload.get("metadata", {})
        if not isinstance(metadata, Mapping):
            raise TypeError("bundle metadata must be a JSON object")

        backend_hash = result.get("backend_semantic_sha256")
        if backend_hash is not None and not isinstance(backend_hash, str):
            raise TypeError("backend semantic hash must be a string or null")

        bundle = cls(
            problem=problem,
            problem_sha256=str(payload["problem_sha256"]),
            component_model_sha256=str(payload["component_model_sha256"]),
            status=str(status),
            backend=backend,
            domain=domain,
            signed_utility=utility,
            component_choices=choices,
            strategy_items=tuple(
                sorted(strategy, key=lambda item: repr(item[0]))
            ),
            backend_semantic_sha256=backend_hash,
            optimality_certificate=certificate,
            metadata_items=tuple(sorted(metadata.items())),
        )
        recorded_manifest = payload.get("manifest_sha256")
        if (
            recorded_manifest is not None
            and str(recorded_manifest) != bundle.manifest_sha256
        ):
            raise ValueError("proof-bundle manifest hash mismatch")
        return bundle

    @classmethod
    def from_json(cls, text: str) -> "ProofBundle":
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise TypeError("proof-bundle JSON must contain one object")
        return cls.from_dict(payload)

    @classmethod
    def load(cls, path: str | Path) -> "ProofBundle":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def write(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")


def _native_result(
    problem: FiniteSafetyProblem,
    model: QuasiPrimalDomainModel,
) -> tuple[
    str,
    frozenset[State] | None,
    int | None,
    CompiledDomainWitness | None,
    str | None,
    dict[str, object],
]:
    game = problem.game()
    kernel = CompiledParameterizedKernel(
        game,
        frozenset(),
        internal_isomorphisms=problem.algebra.internal_isomorphisms(),
    )
    try:
        result = optimize_weighted_domain(
            kernel,
            state_weights=problem.state_weights,
            default_weight=problem.default_weight,
            required_states=problem.required_states,
            forbidden_states=problem.forbidden_states,
        )
    except ValueError as error:
        if "no feasible clone-compatible domain exists" not in str(error):
            raise
        return (
            "infeasible",
            None,
            None,
            None,
            None,
            {"native_status": "infeasible"},
        )

    witness = model.solve_domain(result.domain)
    if not isinstance(witness, CompiledDomainWitness):
        raise AssertionError("native optimum failed component-model replay")
    utility = _signed_score(
        model.states,
        result.domain,
        problem.state_weights,
        problem.default_weight,
    )
    if utility != result.objective.score:
        raise AssertionError("native objective disagrees with domain utility")
    return (
        "optimal",
        result.domain,
        utility,
        witness,
        result.semantic_sha256,
        {
            "native_search_nodes": result.stats.nodes,
            "native_conflict_prunes": result.stats.conflict_prunes,
            "native_bound_prunes": result.stats.bound_prunes,
            "native_trace_sha256": result.trace_sha256,
        },
    )


def _highs_result(
    problem: FiniteSafetyProblem,
    model: QuasiPrimalDomainModel,
) -> tuple[
    str,
    frozenset[State] | None,
    int | None,
    CompiledDomainWitness | None,
    str | None,
    dict[str, object],
]:
    cnf = model.cnf(
        required_states=problem.required_states,
        forbidden_states=problem.forbidden_states,
    )
    wcnf = model.weighted_cnf(
        required_states=problem.required_states,
        forbidden_states=problem.forbidden_states,
        state_weights=problem.state_weights,
        default_weight=problem.default_weight,
    )
    result = solve_weighted_cnf_highs(
        model,
        cnf,
        wcnf,
        state_weights=problem.state_weights,
        default_weight=problem.default_weight,
    )
    if result.status == "infeasible":
        return (
            "infeasible",
            None,
            None,
            None,
            result.semantic_sha256,
            {
                "cnf_variables": cnf.variable_count,
                "hard_clauses": len(cnf.clauses),
                "soft_clauses": len(wcnf.soft_state_units),
            },
        )
    if (
        result.status != "optimal"
        or not result.certificate_verified
        or result.witness is None
        or result.signed_utility is None
    ):
        raise ExternalOptimizationError(
            "HiGHS returned no verified optimal controller"
        )
    return (
        "optimal",
        result.witness.domain,
        result.signed_utility,
        result.witness,
        result.semantic_sha256,
        {
            "cnf_variables": cnf.variable_count,
            "hard_clauses": len(cnf.clauses),
            "soft_clauses": len(wcnf.soft_state_units),
            "backend_unsatisfied_cost": result.unsatisfied_cost,
        },
    )


def synthesize_proof_bundle(
    problem: FiniteSafetyProblem,
    *,
    backend: str = "auto",
    certificate_max_nodes: int = 1_000_000,
) -> ProofBundle:
    """Synthesize one controller and attach an exact finite proof."""

    if not problem.quasi_primal_premise:
        raise ValueError("the quasi-primal premise was not acknowledged")
    game = problem.game()
    model = compile_quasi_primal_domain_model(game)
    selected_backend = backend
    if backend == "auto":
        selected_backend = "native" if len(model.states) <= 18 else "highs"
    if selected_backend == "native":
        result = _native_result(problem, model)
    elif selected_backend == "highs":
        result = _highs_result(problem, model)
    else:
        raise ValueError("backend must be 'auto', 'native', or 'highs'")

    status, domain, utility, witness, backend_hash, metadata = result
    certificate = generate_state_search_certificate(
        model,
        target_domain=domain,
        state_weights=problem.state_weights,
        default_weight=problem.default_weight,
        required_states=problem.required_states,
        forbidden_states=problem.forbidden_states,
        max_nodes=certificate_max_nodes,
    )
    if not verify_state_search_certificate(model, certificate):
        raise AssertionError("generated optimality certificate failed replay")

    if status == "optimal":
        if witness is None or domain is None or utility is None:
            raise AssertionError("optimal result lacked its controller witness")
        if certificate.target_score != utility:
            raise AssertionError("certificate score disagrees with optimizer")
        component_choices = witness.component_choices
        strategy_items = witness.strategy_items
    else:
        if witness is not None or domain is not None or utility is not None:
            raise AssertionError("infeasible result carried a controller")
        if certificate.claim != "infeasible":
            raise AssertionError("infeasible result received an optimum proof")
        component_choices = ()
        strategy_items = ()

    bundle = ProofBundle(
        problem=problem,
        problem_sha256=problem.semantic_sha256,
        component_model_sha256=domain_model_sha256(model),
        status=status,
        backend=selected_backend,
        domain=domain,
        signed_utility=utility,
        component_choices=component_choices,
        strategy_items=strategy_items,
        backend_semantic_sha256=backend_hash,
        optimality_certificate=certificate,
        metadata_items=tuple(sorted(metadata.items())),
    )
    if not verify_proof_bundle(bundle):
        raise AssertionError("generated proof bundle failed immediate verification")
    return bundle


def verify_proof_bundle(bundle: ProofBundle) -> bool:
    """Rebuild and independently replay a complete proof bundle."""

    try:
        problem = bundle.problem
        if bundle.problem_sha256 != problem.semantic_sha256:
            return False
        game = problem.game()
        model = compile_quasi_primal_domain_model(game)
        if bundle.component_model_sha256 != domain_model_sha256(model):
            return False
        if not _problem_certificate_binding(
            problem,
            model,
            bundle.optimality_certificate,
        ):
            return False
        if not verify_state_search_certificate(
            model,
            bundle.optimality_certificate,
        ):
            return False

        if bundle.status == "infeasible":
            return (
                bundle.domain is None
                and bundle.signed_utility is None
                and not bundle.component_choices
                and not bundle.strategy_items
                and bundle.optimality_certificate.claim == "infeasible"
            )

        if bundle.status != "optimal" or bundle.domain is None:
            return False
        if bundle.signed_utility is None:
            return False
        witness = CompiledDomainWitness(
            domain=bundle.domain,
            component_choices=bundle.component_choices,
            strategy_items=bundle.strategy_items,
        )
        if not _witness_replays(model, witness):
            return False
        score = _signed_score(
            model.states,
            bundle.domain,
            problem.state_weights,
            problem.default_weight,
        )
        if score != bundle.signed_utility:
            return False
        certificate = bundle.optimality_certificate
        if certificate.claim != "optimal":
            return False
        if certificate.target_score != score:
            return False
        target_mask = 0
        state_index = {state: index for index, state in enumerate(model.states)}
        for state in bundle.domain:
            target_mask |= 1 << state_index[state]
        return certificate.target_domain_mask == target_mask
    except (KeyError, TypeError, ValueError):
        return False

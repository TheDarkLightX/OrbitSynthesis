#!/usr/bin/env python3
"""Focused adversarial checks for portable bundle/objective binding."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import compile_quasi_primal_domain_model
from orbitsynthesis.problem_io import FiniteSafetyProblem
from orbitsynthesis.proof_bundle import (
    ProofBundle,
    synthesize_proof_bundle,
    verify_proof_bundle,
)
from orbitsynthesis.proof_bundle_io import strict_proof_bundle_from_dict
from orbitsynthesis.state_optimality_certificate import (
    verify_state_search_certificate,
)


def rejected(callable_) -> bool:
    try:
        callable_()
    except (TypeError, ValueError):
        return True
    return False


def certificate_problem_hash(
    model_hash: str,
    weights: tuple[int, ...],
    required_mask: int,
    forbidden_mask: int,
) -> str:
    payload = {
        "schema": "orbit-synthesis/state-search-optimality/v1",
        "model_sha256": model_hash,
        "weights": list(weights),
        "required_mask": required_mask,
        "forbidden_mask": forbidden_mask,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def valid_alternate_certificate(
    certificate,
    *,
    weights=None,
    required_mask=None,
    forbidden_mask=None,
):
    new_weights = certificate.weights if weights is None else tuple(weights)
    new_required = (
        certificate.required_mask
        if required_mask is None
        else int(required_mask)
    )
    new_forbidden = (
        certificate.forbidden_mask
        if forbidden_mask is None
        else int(forbidden_mask)
    )
    return replace(
        certificate,
        weights=new_weights,
        required_mask=new_required,
        forbidden_mask=new_forbidden,
        problem_sha256=certificate_problem_hash(
            certificate.model_sha256,
            new_weights,
            new_required,
            new_forbidden,
        ),
    )


def main() -> int:
    problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/discriminator_policy.json"
    )
    bundle = synthesize_proof_bundle(problem, backend="native")
    model = compile_quasi_primal_domain_model(problem.game())
    certificate = bundle.optimality_certificate

    # This is a genuinely valid optimum certificate for a different objective:
    # weights (2,0,1) still give the full domain score and root bound 3.
    changed_weights = valid_alternate_certificate(
        certificate,
        weights=(2, 0, 1),
    )
    if not verify_state_search_certificate(model, changed_weights):
        raise RuntimeError("alternate-weight certificate was not independently valid")
    weight_bound = not verify_proof_bundle(
        replace(bundle, optimality_certificate=changed_weights)
    )

    # Requiring state zero is also a valid proof problem, but it is not the
    # original bundle problem and therefore must not be accepted as authority.
    changed_required = valid_alternate_certificate(
        certificate,
        required_mask=1,
    )
    if not verify_state_search_certificate(model, changed_required):
        raise RuntimeError("alternate-required certificate was not valid")
    required_bound = not verify_proof_bundle(
        replace(bundle, optimality_certificate=changed_required)
    )

    infeasible_problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/coupled_required_infeasible.json"
    )
    infeasible_bundle = synthesize_proof_bundle(
        infeasible_problem,
        backend="native",
    )
    infeasible_model = compile_quasi_primal_domain_model(
        infeasible_problem.game()
    )
    infeasible_certificate = infeasible_bundle.optimality_certificate

    # Both stronger variants remain valid infeasibility certificates because
    # the required binary component is already contradictory. They do not,
    # however, prove the exact original hard-state problem.
    stronger_required = valid_alternate_certificate(
        infeasible_certificate,
        required_mask=7,
    )
    if not verify_state_search_certificate(
        infeasible_model,
        stronger_required,
    ):
        raise RuntimeError("stronger-required infeasibility proof was not valid")
    required_infeasible_bound = not verify_proof_bundle(
        replace(
            infeasible_bundle,
            optimality_certificate=stronger_required,
        )
    )

    extra_forbidden = valid_alternate_certificate(
        infeasible_certificate,
        forbidden_mask=4,
    )
    if not verify_state_search_certificate(
        infeasible_model,
        extra_forbidden,
    ):
        raise RuntimeError("extra-forbidden infeasibility proof was not valid")
    forbidden_bound = not verify_proof_bundle(
        replace(
            infeasible_bundle,
            optimality_certificate=extra_forbidden,
        )
    )

    bool_domain_payload = bundle.as_dict()
    bool_domain_payload["result"]["domain"][1][0] = True
    bool_domain = rejected(
        lambda: strict_proof_bundle_from_dict(bool_domain_payload)
    )

    bool_choice_payload = bundle.as_dict()
    bool_choice_payload["result"]["component_choices"][0] = True
    bool_choice = rejected(
        lambda: strict_proof_bundle_from_dict(bool_choice_payload)
    )

    string_choice_payload = bundle.as_dict()
    string_choice_payload["result"]["component_choices"][0] = "0"
    string_choice = rejected(
        lambda: strict_proof_bundle_from_dict(string_choice_payload)
    )

    missing_manifest_payload = bundle.as_dict()
    missing_manifest_payload.pop("manifest_sha256")
    missing_manifest = rejected(
        lambda: strict_proof_bundle_from_dict(missing_manifest_payload)
    )

    extra_bundle_payload = bundle.as_dict()
    extra_bundle_payload["ignored"] = "must fail closed"
    extra_bundle = rejected(
        lambda: strict_proof_bundle_from_dict(extra_bundle_payload)
    )

    extra_result_payload = bundle.as_dict()
    extra_result_payload["result"]["ignored"] = 1
    extra_result = rejected(
        lambda: strict_proof_bundle_from_dict(extra_result_payload)
    )

    missing_certificate_hash = bundle.as_dict()
    missing_certificate_hash["optimality_certificate"].pop("semantic_sha256")
    missing_certificate = rejected(
        lambda: strict_proof_bundle_from_dict(missing_certificate_hash)
    )

    premise_payload = problem.semantic_payload()
    premise_payload["semantics"]["quasi_primal_premise_acknowledged"] = False
    premise = rejected(lambda: FiniteSafetyProblem.from_dict(premise_payload))

    duplicate_payload = problem.semantic_payload()
    duplicate_payload["game"]["safe_relation"]["transitions"].append(
        duplicate_payload["game"]["safe_relation"]["transitions"][0]
    )
    duplicate = rejected(lambda: FiniteSafetyProblem.from_dict(duplicate_payload))

    extra_problem_payload = problem.semantic_payload()
    extra_problem_payload["ignored"] = "must fail closed"
    extra_problem = rejected(
        lambda: FiniteSafetyProblem.from_dict(extra_problem_payload)
    )

    results = {
        "valid_alternate_weight_certificate_rejected": weight_bound,
        "valid_alternate_required_certificate_rejected": required_bound,
        "valid_stronger_infeasibility_certificate_rejected": (
            required_infeasible_bound
        ),
        "valid_extra_forbidden_certificate_rejected": forbidden_bound,
        "boolean_domain_rejected": bool_domain,
        "boolean_component_choice_rejected": bool_choice,
        "string_component_choice_rejected": string_choice,
        "missing_manifest_rejected": missing_manifest,
        "unknown_bundle_key_rejected": extra_bundle,
        "unknown_result_key_rejected": extra_result,
        "missing_certificate_hash_rejected": missing_certificate,
        "unacknowledged_premise_rejected": premise,
        "duplicate_transition_rejected": duplicate,
        "unknown_problem_key_rejected": extra_problem,
    }
    if not all(results.values()):
        raise RuntimeError("one bundle-binding mutation was accepted")
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Adversarial gate for model-bound external optimum authorities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import (
    CompiledDomainWitness,
    ComponentCandidateRule,
    ComponentRuleSet,
    QuasiPrimalDomainModel,
)
from orbitsynthesis.external_optimization import ExternalOptimizationResult
from orbitsynthesis.optimization_authority import (
    bounded_domain_objective_authority,
    certify_external_result,
    closed_form_objective_authority,
    domain_model_sha256,
)


def candidate(output, observations, forbidden=()):
    return ComponentCandidateRule(
        representative_output=output,
        assignment_items=tuple((observation, output) for observation in observations),
        forbidden_states=frozenset(forbidden),
        closure_edges=frozenset(),
    )


def model_a():
    states = ((0,), (1,))
    observations = states
    return QuasiPrimalDomainModel(
        states=states,
        observations=observations,
        components=(
            ComponentRuleSet(
                representative=(0,),
                observations=observations,
                candidates=(
                    candidate((0,), observations, ((1,),)),
                    candidate((1,), observations, ((0,),)),
                ),
            ),
        ),
    )


def model_b():
    states = ((0,), (1,))
    observations = states
    return QuasiPrimalDomainModel(
        states=states,
        observations=observations,
        components=(
            ComponentRuleSet(
                representative=(0,),
                observations=observations,
                candidates=(candidate((0,), observations),),
            ),
        ),
    )


def model_c_infeasible_at_zero():
    states = ((0,), (1,))
    observations = states
    return QuasiPrimalDomainModel(
        states=states,
        observations=observations,
        components=(
            ComponentRuleSet(
                representative=(0,),
                observations=observations,
                candidates=(candidate((1,), observations, ((0,),)),),
            ),
        ),
    )


def optimal_result(model, witness, score):
    return ExternalOptimizationResult(
        backend="adversarial-test",
        status="optimal",
        certificate_verified=True,
        optimality_authority="backend_status",
        witness=witness,
        model_literals=(),
        soft_reward=score,
        unsatisfied_cost=0,
        reported_cost=0,
        signed_utility=score,
        wall_seconds=0.0,
    )


def infeasible_result():
    return ExternalOptimizationResult(
        backend="adversarial-test",
        status="infeasible",
        certificate_verified=False,
        optimality_authority="backend_status",
        witness=None,
        model_literals=(),
        soft_reward=None,
        unsatisfied_cost=None,
        reported_cost=None,
        signed_utility=None,
        wall_seconds=0.0,
    )


def main():
    a = model_a()
    b = model_b()
    c = model_c_infeasible_at_zero()
    weights = {(0,): 5, (1,): 3}
    witness = a.solve_domain({(0,)})
    if not isinstance(witness, CompiledDomainWitness):
        raise AssertionError("model A lost its expected witness")
    authority = closed_form_objective_authority(
        name="binding_test",
        model=a,
        optimum_score=5,
        optimum_domains=(frozenset({(0,)}),),
        state_weights=weights,
        default_weight=0,
    )
    promoted = certify_external_result(
        optimal_result(a, witness, 5),
        authority,
        model=a,
    )
    if promoted.optimality_authority != "binding_test":
        raise AssertionError("valid authority was not promoted")

    wrong_model_rejected = False
    try:
        certify_external_result(
            optimal_result(a, witness, 5),
            authority,
            model=b,
        )
    except ValueError:
        wrong_model_rejected = True
    if not wrong_model_rejected:
        raise AssertionError("authority was accepted on a different model")

    forged = CompiledDomainWitness(
        domain=frozenset({(0,)}),
        component_choices=(1,),
        strategy_items=tuple(
            sorted(
                candidate((1,), a.observations, ((0,),)).assignment_items,
                key=lambda item: repr(item[0]),
            )
        ),
    )
    forged_witness_rejected = False
    try:
        certify_external_result(
            optimal_result(a, forged, 5),
            authority,
            model=a,
        )
    except ValueError:
        forged_witness_rejected = True
    if not forged_witness_rejected:
        raise AssertionError("forged component choice was accepted")

    infeasible_authority = bounded_domain_objective_authority(
        c,
        allowed_states=((0,),),
        required_states=((0,),),
        state_weights={},
        default_weight=0,
        max_free_states=0,
        name="bounded_binding_infeasible",
    )
    if infeasible_authority.optimum_score is not None:
        raise AssertionError("infeasible authority found a domain")
    promoted_infeasible = certify_external_result(
        infeasible_result(),
        infeasible_authority,
        model=c,
    )
    if promoted_infeasible.optimality_authority != "bounded_binding_infeasible":
        raise AssertionError("valid infeasibility authority was not promoted")

    wrong_infeasible_model_rejected = False
    try:
        certify_external_result(
            infeasible_result(),
            infeasible_authority,
            model=a,
        )
    except ValueError:
        wrong_infeasible_model_rejected = True
    if not wrong_infeasible_model_rejected:
        raise AssertionError("infeasibility authority crossed model boundary")

    changed_objective = closed_form_objective_authority(
        name="binding_test",
        model=a,
        optimum_score=7,
        optimum_domains=(frozenset({(0,)}),),
        state_weights={(0,): 7, (1,): 3},
        default_weight=0,
    )
    if changed_objective.problem_sha256 == authority.problem_sha256:
        raise AssertionError("objective mutation did not change problem hash")

    result = {
        "schema": "orbit-synthesis/authority-binding/v1",
        "model_hashes_distinct": len({
            domain_model_sha256(a),
            domain_model_sha256(b),
            domain_model_sha256(c),
        }) == 3,
        "wrong_model_rejected": wrong_model_rejected,
        "forged_witness_rejected": forged_witness_rejected,
        "wrong_infeasible_model_rejected": wrong_infeasible_model_rejected,
        "objective_hash_changed": (
            changed_objective.problem_sha256 != authority.problem_sha256
        ),
        "promoted_authority": promoted.optimality_authority,
        "promoted_infeasible_authority": (
            promoted_infeasible.optimality_authority
        ),
    }
    if not all(
        result[key]
        for key in (
            "model_hashes_distinct",
            "wrong_model_rejected",
            "forged_witness_rejected",
            "wrong_infeasible_model_rejected",
            "objective_hash_changed",
        )
    ):
        raise AssertionError("authority mutation gate failed")
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

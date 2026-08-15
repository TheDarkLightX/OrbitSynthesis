#!/usr/bin/env python3
"""Exact gate for portable state-search optimality certificates."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.external_optimization import solve_weighted_cnf_highs
from orbitsynthesis.optimization_authority import bounded_domain_objective_authority
from orbitsynthesis.state_optimality_certificate import (
    StateSearchCertificate,
    certify_external_result_with_state_search,
    generate_state_search_certificate,
    verify_state_search_certificate,
)
from orbitsynthesis.structural_benchmarks import (
    build_exact_antichain_family,
    build_principal_backend_family,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def domain_json(domain):
    return [list(state) for state in sorted(domain, key=repr)]


def certificate_summary(certificate: StateSearchCertificate) -> dict[str, object]:
    return {
        "claim": certificate.claim,
        "target_score": certificate.target_score,
        "statistics": certificate.statistics,
        "semantic_sha256": certificate.semantic_sha256,
        "json_bytes": len(certificate.to_json().encode()),
    }


def antichain_case() -> tuple[dict[str, object], StateSearchCertificate, object]:
    family = build_exact_antichain_family(3)
    model = family.component_model()
    weights = family.preferred_weights()
    certificate = generate_state_search_certificate(
        model,
        target_domain=family.preferred_domain,
        state_weights=weights,
        default_weight=0,
        max_nodes=200_000,
    )
    require(verify_state_search_certificate(model, certificate), "antichain proof")
    roundtrip = StateSearchCertificate.from_json(certificate.to_json())
    require(roundtrip == certificate, "antichain JSON roundtrip")

    cnf = model.cnf()
    wcnf = model.weighted_cnf(
        state_weights=weights,
        default_weight=0,
    )
    raw = solve_weighted_cnf_highs(
        model,
        cnf,
        wcnf,
        state_weights=weights,
        default_weight=0,
    )
    promoted = certify_external_result_with_state_search(
        raw,
        certificate,
        model=model,
    )
    require(
        promoted.optimality_authority == "state_search_certificate",
        "antichain optimum was not promoted",
    )
    require(promoted.witness is not None, "antichain backend lost witness")
    require(
        promoted.signed_utility == family.preferred_score(),
        "antichain backend score",
    )
    return (
        {
            "states": len(model.states),
            "components": len(model.components),
            "candidate_rules": sum(
                len(component.candidates) for component in model.components
            ),
            "closed_form_maxima": family.expected_maximal_count,
            "preferred_score": family.preferred_score(),
            "preferred_domain": domain_json(family.preferred_domain),
            "certificate": certificate_summary(certificate),
            "backend": {
                "status": promoted.status,
                "certificate_verified": promoted.certificate_verified,
                "optimality_authority": promoted.optimality_authority,
                "domain": domain_json(promoted.witness.domain),
                "signed_utility": promoted.signed_utility,
            },
        },
        certificate,
        model,
    )


def principal_cases() -> tuple[
    dict[str, object],
    StateSearchCertificate,
    StateSearchCertificate,
    object,
]:
    family = build_principal_backend_family()
    model = family.model
    allowed = family.restricted_union
    outside = frozenset(model.states) - allowed
    weights = {
        state: 1 << index
        for index, state in enumerate(sorted(allowed, key=repr))
    }
    authority = bounded_domain_objective_authority(
        model,
        allowed_states=allowed,
        state_weights=weights,
        default_weight=0,
        max_free_states=20,
        name="principal_certificate_calibration",
    )
    require(authority.optimum_score == 13, "principal optimum score")
    require(len(authority.optimum_domains) == 1, "principal optimum uniqueness")
    target = authority.optimum_domains[0]

    optimum_certificate = generate_state_search_certificate(
        model,
        target_domain=target,
        state_weights=weights,
        default_weight=0,
        forbidden_states=outside,
        max_nodes=100_000,
    )
    require(
        verify_state_search_certificate(model, optimum_certificate),
        "principal optimum proof",
    )
    require(
        StateSearchCertificate.from_json(optimum_certificate.to_json())
        == optimum_certificate,
        "principal optimum JSON roundtrip",
    )

    cnf = model.cnf(forbidden_states=outside)
    wcnf = model.weighted_cnf(
        forbidden_states=outside,
        state_weights=weights,
        default_weight=0,
    )
    optimum_backend = certify_external_result_with_state_search(
        solve_weighted_cnf_highs(
            model,
            cnf,
            wcnf,
            state_weights=weights,
            default_weight=0,
        ),
        optimum_certificate,
        model=model,
    )

    infeasible_certificate = generate_state_search_certificate(
        model,
        target_domain=None,
        state_weights={},
        default_weight=0,
        required_states=allowed,
        forbidden_states=outside,
        max_nodes=10_000,
    )
    require(
        verify_state_search_certificate(model, infeasible_certificate),
        "principal infeasibility proof",
    )
    forced_cnf = model.cnf(
        required_states=allowed,
        forbidden_states=outside,
    )
    forced_wcnf = model.weighted_cnf(
        required_states=allowed,
        forbidden_states=outside,
        state_weights={},
        default_weight=0,
    )
    infeasible_backend = certify_external_result_with_state_search(
        solve_weighted_cnf_highs(
            model,
            forced_cnf,
            forced_wcnf,
            state_weights={},
            default_weight=0,
        ),
        infeasible_certificate,
        model=model,
    )

    require(optimum_backend.witness is not None, "principal backend witness")
    return (
        {
            "states": len(model.states),
            "observations": len(model.observations),
            "components": len(model.components),
            "candidate_rules": sum(
                len(component.candidates) for component in model.components
            ),
            "restricted_union": domain_json(allowed),
            "assignments_checked_by_calibration": authority.assignments_checked,
            "feasible_domains_checked_by_calibration": (
                authority.feasible_domains_checked
            ),
            "optimum": {
                "score": authority.optimum_score,
                "domain": domain_json(target),
                "certificate": certificate_summary(optimum_certificate),
                "backend_authority": optimum_backend.optimality_authority,
            },
            "forced_union": {
                "status": infeasible_backend.status,
                "certificate": certificate_summary(infeasible_certificate),
                "backend_authority": infeasible_backend.optimality_authority,
            },
        },
        optimum_certificate,
        infeasible_certificate,
        model,
    )


def mutation_checks(
    antichain_certificate: StateSearchCertificate,
    antichain_model,
    principal_optimum: StateSearchCertificate,
    principal_infeasible: StateSearchCertificate,
    principal_model,
) -> dict[str, bool]:
    rejected = {}

    bound_index = next(
        index
        for index, node in enumerate(antichain_certificate.nodes)
        if node.kind == "bound"
    )
    nodes = list(antichain_certificate.nodes)
    bound = nodes[bound_index]
    nodes[bound_index] = replace(
        bound,
        upper_bound=(bound.upper_bound or 0) + 1,
    )
    rejected["wrong_bound"] = not verify_state_search_certificate(
        antichain_model,
        replace(antichain_certificate, nodes=tuple(nodes)),
    )

    conflict_index = next(
        index
        for index, node in enumerate(antichain_certificate.nodes)
        if node.kind == "conflict"
    )
    nodes = list(antichain_certificate.nodes)
    nodes[conflict_index] = replace(
        nodes[conflict_index],
        component_index=len(antichain_model.components),
    )
    rejected["bad_component"] = not verify_state_search_certificate(
        antichain_model,
        replace(antichain_certificate, nodes=tuple(nodes)),
    )

    branch_index = next(
        index
        for index, node in enumerate(antichain_certificate.nodes)
        if node.kind == "branch"
    )
    nodes = list(antichain_certificate.nodes)
    nodes[branch_index] = replace(
        nodes[branch_index],
        include_child=branch_index,
    )
    rejected["cyclic_tree"] = not verify_state_search_certificate(
        antichain_model,
        replace(antichain_certificate, nodes=tuple(nodes)),
    )

    rejected["cross_model"] = not verify_state_search_certificate(
        principal_model,
        antichain_certificate,
    )
    rejected["wrong_target_score"] = not verify_state_search_certificate(
        principal_model,
        replace(
            principal_optimum,
            target_score=(principal_optimum.target_score or 0) + 1,
        ),
    )
    rejected["infeasible_with_bound"] = not verify_state_search_certificate(
        principal_model,
        replace(
            principal_infeasible,
            nodes=(
                replace(
                    principal_infeasible.nodes[0],
                    kind="bound",
                    component_index=None,
                    upper_bound=0,
                ),
                *principal_infeasible.nodes[1:],
            ),
        ),
    )
    require(all(rejected.values()), "one certificate mutation was accepted")
    return rejected


def main() -> int:
    antichain, antichain_certificate, antichain_model = antichain_case()
    (
        principal,
        principal_optimum,
        principal_infeasible,
        principal_model,
    ) = principal_cases()
    mutations = mutation_checks(
        antichain_certificate,
        antichain_model,
        principal_optimum,
        principal_infeasible,
        principal_model,
    )
    result = {
        "schema": "orbit-synthesis/state-search-certificate-gate/v1",
        "antichain": antichain,
        "principal": principal,
        "mutations": mutations,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

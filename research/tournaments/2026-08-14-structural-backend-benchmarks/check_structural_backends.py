#!/usr/bin/env python3
"""Exact backend gate on OrbitSynthesis's structural theorem families."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import (
    CompiledDomainFailure,
    CompiledDomainWitness,
)
from orbitsynthesis.domain_optimization import optimize_weighted_domain
from orbitsynthesis.external_optimization import (
    ExternalOptimizationError,
    solve_weighted_cnf_highs,
    solve_weighted_cnf_pysat_rc2,
)
from orbitsynthesis.optimization_authority import (
    bounded_domain_objective_authority,
    certify_external_result,
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


def external_summary(result) -> dict[str, object]:
    return {
        "backend": result.backend,
        "status": result.status,
        "certificate_verified": result.certificate_verified,
        "optimality_authority": result.optimality_authority,
        "domain": (
            domain_json(result.witness.domain)
            if result.witness is not None
            else None
        ),
        "signed_utility": result.signed_utility,
        "unsatisfied_cost": result.unsatisfied_cost,
    }


def exact_backends(
    *,
    model,
    cnf,
    wcnf,
    authority,
    weights,
    require_pysat: bool,
) -> tuple[dict[str, object], bool]:
    highs = certify_external_result(
        solve_weighted_cnf_highs(
            model,
            cnf,
            wcnf,
            state_weights=weights,
            default_weight=0,
        ),
        authority,
        model=model,
    )
    rows = {"highs": external_summary(highs)}
    pysat_available = True
    try:
        pysat = certify_external_result(
            solve_weighted_cnf_pysat_rc2(
                model,
                cnf,
                wcnf,
                state_weights=weights,
                default_weight=0,
            ),
            authority,
            model=model,
        )
    except ExternalOptimizationError as error:
        if "python-sat is required" not in str(error):
            raise
        pysat_available = False
        if require_pysat:
            raise
    else:
        rows["pysat_rc2"] = external_summary(pysat)
    return rows, pysat_available


def antichain_case(state_arity: int, require_pysat: bool) -> dict[str, object]:
    family = build_exact_antichain_family(state_arity)
    model = family.component_model()
    for domain in family.maximal_domains:
        solution = model.solve_domain(domain)
        require(
            isinstance(solution, CompiledDomainWitness),
            "closed-form antichain maximum failed component replay",
        )

    authority = family.objective_authority(model)
    weights = family.preferred_weights()
    require(authority.optimum_score == family.preferred_score(), "authority score")
    require(authority.optimum_domains == (family.preferred_domain,), "authority domain")

    native = None
    if state_arity == 3:
        native = optimize_weighted_domain(
            family.pointed_kernel(),
            state_weights=weights,
            default_weight=0,
        )
        require(native.domain == family.preferred_domain, "native antichain domain")
        require(
            native.objective.score == authority.optimum_score,
            "native antichain score",
        )

    cnf = model.cnf()
    wcnf = model.weighted_cnf(
        state_weights=weights,
        default_weight=0,
    )
    backends, pysat_available = exact_backends(
        model=model,
        cnf=cnf,
        wcnf=wcnf,
        authority=authority,
        weights=weights,
        require_pysat=require_pysat,
    )
    for row in backends.values():
        require(
            row["domain"] == domain_json(family.preferred_domain),
            "external antichain domain",
        )

    return {
        "state_arity": state_arity,
        "states": len(family.game.states),
        "observations": len(family.game.observations),
        "orientation_variables": family.variable_count,
        "closed_form_maxima": family.expected_maximal_count,
        "replayed_maxima": len(family.maximal_domains),
        "maximal_domain_size": family.expected_maximal_size,
        "preferred_score": family.preferred_score(),
        "preferred_domain": domain_json(family.preferred_domain),
        "component_count": len(model.components),
        "candidate_rule_count": sum(
            len(component.candidates) for component in model.components
        ),
        "cnf_variables": cnf.variable_count,
        "hard_clauses": len(cnf.clauses),
        "soft_clauses": len(wcnf.soft_state_units),
        "authority_sha256": authority.semantic_sha256,
        "model_sha256": authority.model_sha256,
        "problem_sha256": authority.problem_sha256,
        "native": (
            {
                "domain": domain_json(native.domain),
                "score": native.objective.score,
                "search_nodes": native.stats.nodes,
                "bound_prunes": native.stats.bound_prunes,
                "conflict_prunes": native.stats.conflict_prunes,
            }
            if native is not None
            else None
        ),
        "backends": backends,
        "pysat_available": pysat_available,
    }


def principal_case(require_pysat: bool) -> dict[str, object]:
    family = build_principal_backend_family()
    model = family.model
    witness = family.witness
    left = model.solve_domain(witness.left_domain)
    right = model.solve_domain(witness.right_domain)
    union = model.solve_domain(family.restricted_union)
    require(isinstance(left, CompiledDomainWitness), "left domain lost")
    require(isinstance(right, CompiledDomainWitness), "right domain lost")
    require(isinstance(union, CompiledDomainFailure), "union became feasible")

    allowed = family.restricted_union
    ordered_allowed = tuple(sorted(allowed, key=repr))
    require(len(ordered_allowed) <= 20, "principal restricted union grew unexpectedly")
    weights = {
        state: 1 << index
        for index, state in enumerate(ordered_allowed)
    }

    weighted_authority = bounded_domain_objective_authority(
        model,
        allowed_states=allowed,
        state_weights=weights,
        default_weight=0,
        max_free_states=20,
        name="bounded_principal_union",
    )
    require(weighted_authority.optimum_score is not None, "restricted optimum missing")
    require(
        len(weighted_authority.optimum_domains) == 1,
        "binary-place objective did not have a unique optimum",
    )
    outside = frozenset(model.states) - allowed
    weighted_cnf = model.cnf(forbidden_states=outside)
    weighted_wcnf = model.weighted_cnf(
        forbidden_states=outside,
        state_weights=weights,
        default_weight=0,
    )
    weighted_backends, weighted_pysat = exact_backends(
        model=model,
        cnf=weighted_cnf,
        wcnf=weighted_wcnf,
        authority=weighted_authority,
        weights=weights,
        require_pysat=require_pysat,
    )

    infeasible_authority = bounded_domain_objective_authority(
        model,
        allowed_states=allowed,
        required_states=allowed,
        state_weights={},
        default_weight=0,
        max_free_states=0,
        name="bounded_principal_union_infeasible",
    )
    require(infeasible_authority.optimum_score is None, "forced union became feasible")
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
    forced_backends, forced_pysat = exact_backends(
        model=model,
        cnf=forced_cnf,
        wcnf=forced_wcnf,
        authority=infeasible_authority,
        weights={},
        require_pysat=require_pysat,
    )

    base_cnf = model.cnf()
    return {
        "states": len(model.states),
        "observations": len(model.observations),
        "component_count": len(model.components),
        "candidate_rule_count": sum(
            len(component.candidates) for component in model.components
        ),
        "base_cnf_variables": base_cnf.variable_count,
        "base_hard_clauses": len(base_cnf.clauses),
        "left_domain": domain_json(witness.left_domain),
        "right_domain": domain_json(witness.right_domain),
        "restricted_union": domain_json(allowed),
        "direct_pattern": {
            "left_feasible": isinstance(left, CompiledDomainWitness),
            "right_feasible": isinstance(right, CompiledDomainWitness),
            "union_feasible": isinstance(union, CompiledDomainWitness),
        },
        "weighted_restriction": {
            "assignments_checked": weighted_authority.assignments_checked,
            "feasible_domains_checked": weighted_authority.feasible_domains_checked,
            "optimum_score": weighted_authority.optimum_score,
            "optimum_domain": domain_json(weighted_authority.optimum_domains[0]),
            "authority_sha256": weighted_authority.semantic_sha256,
            "model_sha256": weighted_authority.model_sha256,
            "problem_sha256": weighted_authority.problem_sha256,
            "backends": weighted_backends,
        },
        "forced_union": {
            "assignments_checked": infeasible_authority.assignments_checked,
            "feasible_domains_checked": infeasible_authority.feasible_domains_checked,
            "authority_sha256": infeasible_authority.semantic_sha256,
            "model_sha256": infeasible_authority.model_sha256,
            "problem_sha256": infeasible_authority.problem_sha256,
            "backends": forced_backends,
        },
        "pysat_available": weighted_pysat and forced_pysat,
    }


def make_receipt(require_pysat: bool) -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/structural-backend-benchmarks/v2",
        "antichain": [
            antichain_case(3, require_pysat),
            antichain_case(4, require_pysat),
        ],
        "principal": principal_case(require_pysat),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-pysat", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = make_receipt(args.require_pysat)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

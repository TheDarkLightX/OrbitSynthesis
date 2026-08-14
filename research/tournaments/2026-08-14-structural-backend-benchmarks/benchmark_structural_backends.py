#!/usr/bin/env python3
"""Diagnostic timing benchmark for exact structural OrbitSynthesis families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

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


def timing_summary(samples):
    ordered = sorted(samples)
    return {
        "runs": len(ordered),
        "min_seconds": ordered[0],
        "median_seconds": statistics.median(ordered),
        "max_seconds": ordered[-1],
    }


def timed(callable_, repeat):
    samples = []
    semantic = None
    for _ in range(repeat):
        started = time.perf_counter()
        result = callable_()
        samples.append(time.perf_counter() - started)
        witness = getattr(result, "witness", None)
        domain = (
            tuple(sorted(witness.domain, key=repr))
            if witness is not None
            else tuple(sorted(getattr(result, "domain", ()), key=repr))
        )
        score = (
            result.objective.score
            if hasattr(result, "objective")
            else getattr(result, "signed_utility", None)
        )
        candidate = (getattr(result, "status", "optimal"), domain, score)
        if semantic is None:
            semantic = candidate
        elif semantic != candidate:
            raise AssertionError("backend semantics changed across repetitions")
    return timing_summary(samples), semantic


def antichain_rows(repeat, require_pysat):
    rows = []
    pysat_available = True
    for state_arity in (3, 4):
        family = build_exact_antichain_family(state_arity)
        model = family.component_model()
        weights = family.preferred_weights()
        authority = family.objective_authority(model)
        cnf = model.cnf()
        wcnf = model.weighted_cnf(
            state_weights=weights,
            default_weight=0,
        )
        backends = {}
        if state_arity == 3:
            native_timing, native_semantic = timed(
                lambda: optimize_weighted_domain(
                    family.pointed_kernel(),
                    state_weights=weights,
                    default_weight=0,
                ),
                repeat,
            )
            backends["native"] = {
                **native_timing,
                "semantic": native_semantic,
            }
        highs_timing, highs_semantic = timed(
            lambda: certify_external_result(
                solve_weighted_cnf_highs(
                    model,
                    cnf,
                    wcnf,
                    state_weights=weights,
                    default_weight=0,
                ),
                authority,
                model=model,
            ),
            repeat,
        )
        backends["highs"] = {
            **highs_timing,
            "semantic": highs_semantic,
        }
        if pysat_available:
            try:
                pysat_timing, pysat_semantic = timed(
                    lambda: certify_external_result(
                        solve_weighted_cnf_pysat_rc2(
                            model,
                            cnf,
                            wcnf,
                            state_weights=weights,
                            default_weight=0,
                        ),
                        authority,
                        model=model,
                    ),
                    repeat,
                )
            except ExternalOptimizationError as error:
                if "python-sat is required" not in str(error):
                    raise
                pysat_available = False
                if require_pysat:
                    raise
            else:
                backends["pysat_rc2"] = {
                    **pysat_timing,
                    "semantic": pysat_semantic,
                }
        rows.append(
            {
                "family": "exact_antichain",
                "state_arity": state_arity,
                "states": len(model.states),
                "components": len(model.components),
                "candidate_rules": sum(
                    len(component.candidates) for component in model.components
                ),
                "variables": cnf.variable_count,
                "hard_clauses": len(cnf.clauses),
                "soft_clauses": len(wcnf.soft_state_units),
                "closed_form_maxima": family.expected_maximal_count,
                "authority_model_sha256": authority.model_sha256,
                "authority_problem_sha256": authority.problem_sha256,
                "backends": backends,
            }
        )
    return rows, pysat_available


def principal_rows(repeat, require_pysat):
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
        name="bounded_principal_union",
    )
    cnf = model.cnf(forbidden_states=outside)
    wcnf = model.weighted_cnf(
        forbidden_states=outside,
        state_weights=weights,
        default_weight=0,
    )
    backends = {}
    highs_timing, highs_semantic = timed(
        lambda: certify_external_result(
            solve_weighted_cnf_highs(
                model,
                cnf,
                wcnf,
                state_weights=weights,
                default_weight=0,
            ),
            authority,
            model=model,
        ),
        repeat,
    )
    backends["highs"] = {
        **highs_timing,
        "semantic": highs_semantic,
    }
    pysat_available = True
    try:
        pysat_timing, pysat_semantic = timed(
            lambda: certify_external_result(
                solve_weighted_cnf_pysat_rc2(
                    model,
                    cnf,
                    wcnf,
                    state_weights=weights,
                    default_weight=0,
                ),
                authority,
                model=model,
            ),
            repeat,
        )
    except ExternalOptimizationError as error:
        if "python-sat is required" not in str(error):
            raise
        pysat_available = False
        if require_pysat:
            raise
    else:
        backends["pysat_rc2"] = {
            **pysat_timing,
            "semantic": pysat_semantic,
        }
    return {
        "family": "principal_one_equation",
        "states": len(model.states),
        "observations": len(model.observations),
        "components": len(model.components),
        "candidate_rules": sum(
            len(component.candidates) for component in model.components
        ),
        "variables": cnf.variable_count,
        "hard_clauses": len(cnf.clauses),
        "soft_clauses": len(wcnf.soft_state_units),
        "restricted_assignments": authority.assignments_checked,
        "authority_model_sha256": authority.model_sha256,
        "authority_problem_sha256": authority.problem_sha256,
        "backends": backends,
    }, pysat_available


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--require-pysat", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.repeat < 1:
        raise SystemExit("repeat must be positive")

    antichain, antichain_pysat = antichain_rows(
        args.repeat,
        args.require_pysat,
    )
    principal, principal_pysat = principal_rows(
        args.repeat,
        args.require_pysat,
    )
    result = {
        "schema": "orbit-synthesis/structural-backend-timing/v2",
        "diagnostic_only": True,
        "python": sys.version,
        "platform": platform.platform(),
        "repeat": args.repeat,
        "pysat_available": antichain_pysat and principal_pysat,
        "rows": [*antichain, principal],
    }
    rendered = json.dumps(result, indent=2, sort_keys=True, default=repr) + "\n"
    if args.out is not None:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

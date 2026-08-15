#!/usr/bin/env python3
"""Exact gate for user-supplied finite-safety proof bundles."""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.external_optimization import ExternalOptimizationError
from orbitsynthesis.problem_io import FiniteSafetyProblem
from orbitsynthesis.proof_bundle import (
    ProofBundle,
    synthesize_proof_bundle,
    verify_proof_bundle,
)
from orbitsynthesis.proof_bundle_io import strict_proof_bundle_from_json


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def domain_json(domain):
    return None if domain is None else [
        list(state) for state in sorted(domain, key=repr)
    ]


def bundle_row(bundle: ProofBundle) -> dict[str, object]:
    return {
        "problem": bundle.problem.name,
        "status": bundle.status,
        "backend": bundle.backend,
        "domain": domain_json(bundle.domain),
        "signed_utility": bundle.signed_utility,
        "strategy_rows": len(bundle.strategy_items),
        "problem_sha256": bundle.problem_sha256,
        "component_model_sha256": bundle.component_model_sha256,
        "manifest_sha256": bundle.manifest_sha256,
        "certificate": {
            "claim": bundle.optimality_certificate.claim,
            "target_score": bundle.optimality_certificate.target_score,
            "semantic_sha256": bundle.optimality_certificate.semantic_sha256,
            "statistics": bundle.optimality_certificate.statistics,
        },
    }


def mutation_checks(bundle: ProofBundle) -> dict[str, bool]:
    rejected = {}
    rejected["problem_hash"] = not verify_proof_bundle(
        replace(bundle, problem_sha256="0" * 64)
    )
    rejected["component_model_hash"] = not verify_proof_bundle(
        replace(bundle, component_model_sha256="1" * 64)
    )
    rejected["target_score"] = not verify_proof_bundle(
        replace(
            bundle,
            optimality_certificate=replace(
                bundle.optimality_certificate,
                target_score=(bundle.optimality_certificate.target_score or 0) + 1,
            ),
        )
    )

    if bundle.status == "optimal":
        require(bundle.strategy_items, "optimal bundle had no strategy")
        first_observation, first_output = bundle.strategy_items[0]
        carrier = tuple(bundle.problem.algebra.values)
        replacement_value = next(
            value for value in carrier if value != first_output[0]
        )
        changed_output = (replacement_value,) + first_output[1:]
        changed_strategy = (
            (first_observation, changed_output),
            *bundle.strategy_items[1:],
        )
        rejected["strategy"] = not verify_proof_bundle(
            replace(bundle, strategy_items=changed_strategy)
        )
        rejected["component_choice"] = not verify_proof_bundle(
            replace(
                bundle,
                component_choices=(10**9, *bundle.component_choices[1:]),
            )
        )
    else:
        rejected["spurious_domain"] = not verify_proof_bundle(
            replace(bundle, domain=frozenset())
        )
        rejected["spurious_strategy"] = not verify_proof_bundle(
            replace(bundle, strategy_items=(((), ()),))
        )

    payload = bundle.as_dict()
    payload["manifest_sha256"] = "f" * 64
    try:
        strict_proof_bundle_from_json(json.dumps(payload))
    except ValueError:
        rejected["manifest"] = True
    else:
        rejected["manifest"] = False

    require(all(rejected.values()), "one proof-bundle mutation was accepted")
    return rejected


def denylist_equivalent(problem: FiniteSafetyProblem) -> FiniteSafetyProblem:
    payload = problem.semantic_payload()
    carrier = tuple(problem.algebra.values)
    universe = {
        (state, input_value, output)
        for state in product(carrier, repeat=problem.state_arity)
        for input_value in product(carrier, repeat=problem.input_arity)
        for output in product(carrier, repeat=problem.state_arity)
    }
    forbidden = sorted(universe - problem.safe_relation, key=repr)
    payload["game"]["safe_relation"] = {
        "mode": "forbidden",
        "transitions": [
            {
                "state": list(state),
                "input": list(input_value),
                "output": list(output),
            }
            for state, input_value, output in reversed(forbidden)
        ],
    }
    payload["algebra"]["operations"] = list(
        reversed(payload["algebra"]["operations"])
    )
    return FiniteSafetyProblem.from_dict(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-highs", action="store_true")
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    optimal_path = ROOT / "examples/proof_bundle/discriminator_policy.json"
    infeasible_path = ROOT / "examples/proof_bundle/coupled_required_infeasible.json"
    optimal_problem = FiniteSafetyProblem.load(optimal_path)
    infeasible_problem = FiniteSafetyProblem.load(infeasible_path)

    require(
        FiniteSafetyProblem.from_json(optimal_problem.to_json()).semantic_sha256
        == optimal_problem.semantic_sha256,
        "optimal problem canonical roundtrip",
    )
    require(
        FiniteSafetyProblem.from_json(infeasible_problem.to_json()).semantic_sha256
        == infeasible_problem.semantic_sha256,
        "infeasible problem canonical roundtrip",
    )
    equivalent = denylist_equivalent(optimal_problem)
    require(
        equivalent.semantic_sha256 == optimal_problem.semantic_sha256,
        "denylist and operation-order canonicalization changed semantics",
    )

    optimal = synthesize_proof_bundle(optimal_problem, backend="native")
    require(verify_proof_bundle(optimal), "optimal bundle replay")
    require(optimal.status == "optimal", "optimal example became infeasible")
    require(optimal.domain == frozenset({(0,), (1,), (2,)}), "optimal domain")
    require(optimal.signed_utility == 3, "optimal utility")
    require(len(optimal.strategy_items) == 27, "optimal strategy totality")
    for observation, output in optimal.strategy_items:
        x, y, z = observation
        expected = z if x == y else x
        require(output == (expected,), "strategy did not implement d")

    infeasible = synthesize_proof_bundle(infeasible_problem, backend="native")
    require(verify_proof_bundle(infeasible), "infeasible bundle replay")
    require(infeasible.status == "infeasible", "coupled example became feasible")
    require(infeasible.optimality_certificate.claim == "infeasible", "claim")

    strict_optimal = strict_proof_bundle_from_json(optimal.to_json())
    strict_infeasible = strict_proof_bundle_from_json(infeasible.to_json())
    require(
        strict_optimal.manifest_sha256 == optimal.manifest_sha256,
        "optimal strict bundle roundtrip",
    )
    require(
        strict_infeasible.manifest_sha256 == infeasible.manifest_sha256,
        "infeasible strict bundle roundtrip",
    )

    highs_row = None
    try:
        highs = synthesize_proof_bundle(optimal_problem, backend="highs")
    except ExternalOptimizationError as error:
        if args.require_highs:
            raise
        highs_row = {"available": False, "reason": type(error).__name__}
    else:
        require(verify_proof_bundle(highs), "HiGHS bundle replay")
        require(highs.domain == optimal.domain, "native/HiGHS domain disagreement")
        require(
            highs.signed_utility == optimal.signed_utility,
            "native/HiGHS utility disagreement",
        )
        highs_row = {
            "available": True,
            "manifest_sha256": highs.manifest_sha256,
            "backend_semantic_sha256": highs.backend_semantic_sha256,
        }

    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        optimal.write(args.out_dir / "optimal.bundle.json")
        infeasible.write(args.out_dir / "infeasible.bundle.json")

    result = {
        "schema": "orbit-synthesis/portable-proof-bundle-gate/v1",
        "canonicalization": {
            "denylist_equivalent": True,
            "operation_order_independent": True,
        },
        "optimal": bundle_row(optimal),
        "infeasible": bundle_row(infeasible),
        "highs": highs_row,
        "mutations": {
            "optimal": mutation_checks(optimal),
            "infeasible": mutation_checks(infeasible),
        },
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

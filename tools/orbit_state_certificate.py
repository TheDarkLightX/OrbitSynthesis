#!/usr/bin/env python3
"""Generate and verify OrbitSynthesis state-search certificates.

The first CLI surface intentionally exposes source-grounded built-in examples.
A later model-serialization layer can extend the same certificate format to
user-supplied compiled component models.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.optimization_authority import bounded_domain_objective_authority
from orbitsynthesis.state_optimality_certificate import (
    StateSearchCertificate,
    generate_state_search_certificate,
    verify_state_search_certificate,
)
from orbitsynthesis.structural_benchmarks import (
    build_exact_antichain_family,
    build_principal_backend_family,
)


def example_problem(name: str):
    if name == "antichain3":
        family = build_exact_antichain_family(3)
        return {
            "model": family.component_model(),
            "target_domain": family.preferred_domain,
            "state_weights": family.preferred_weights(),
            "default_weight": 0,
            "required_states": frozenset(),
            "forbidden_states": frozenset(),
        }

    family = build_principal_backend_family()
    model = family.model
    allowed = family.restricted_union
    outside = frozenset(model.states) - allowed
    if name == "principal-infeasible":
        return {
            "model": model,
            "target_domain": None,
            "state_weights": {},
            "default_weight": 0,
            "required_states": allowed,
            "forbidden_states": outside,
        }
    if name == "principal-optimum":
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
            name="principal_cli_calibration",
        )
        if authority.optimum_score is None or len(authority.optimum_domains) != 1:
            raise RuntimeError("principal example lost its unique optimum")
        return {
            "model": model,
            "target_domain": authority.optimum_domains[0],
            "state_weights": weights,
            "default_weight": 0,
            "required_states": frozenset(),
            "forbidden_states": outside,
        }
    raise ValueError(f"unknown example: {name!r}")


def summary(
    example: str,
    certificate: StateSearchCertificate,
    verified: bool,
) -> dict[str, object]:
    return {
        "example": example,
        "claim": certificate.claim,
        "verified": verified,
        "target_score": certificate.target_score,
        "model_sha256": certificate.model_sha256,
        "problem_sha256": certificate.problem_sha256,
        "certificate_sha256": certificate.semantic_sha256,
        "statistics": certificate.statistics,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument(
        "--example",
        required=True,
        choices=("antichain3", "principal-optimum", "principal-infeasible"),
    )
    generate.add_argument("--out", type=Path, required=True)
    generate.add_argument("--max-nodes", type=int, default=1_000_000)

    verify = subparsers.add_parser("verify")
    verify.add_argument(
        "--example",
        required=True,
        choices=("antichain3", "principal-optimum", "principal-infeasible"),
    )
    verify.add_argument("--input", type=Path, required=True)

    args = parser.parse_args()
    problem = example_problem(args.example)
    model = problem["model"]

    if args.command == "generate":
        certificate = generate_state_search_certificate(
            model,
            target_domain=problem["target_domain"],
            state_weights=problem["state_weights"],
            default_weight=problem["default_weight"],
            required_states=problem["required_states"],
            forbidden_states=problem["forbidden_states"],
            max_nodes=args.max_nodes,
        )
        verified = verify_state_search_certificate(model, certificate)
        if not verified:
            raise RuntimeError("generated certificate failed immediate replay")
        args.out.write_text(certificate.to_json(), encoding="utf-8")
    else:
        certificate = StateSearchCertificate.from_json(
            args.input.read_text(encoding="utf-8")
        )
        verified = verify_state_search_certificate(model, certificate)
        if not verified:
            raise SystemExit("certificate verification failed")

    print(json.dumps(summary(args.example, certificate, verified), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

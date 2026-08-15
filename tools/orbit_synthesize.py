#!/usr/bin/env python3
"""Synthesize and verify portable OrbitSynthesis proof bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.problem_io import FiniteSafetyProblem
from orbitsynthesis.proof_bundle import (
    ProofBundle,
    synthesize_proof_bundle,
    verify_proof_bundle,
)
from orbitsynthesis.proof_bundle_io import load_proof_bundle


def bundle_summary(bundle: ProofBundle, verified: bool) -> dict[str, object]:
    certificate = bundle.optimality_certificate
    return {
        "problem": bundle.problem.name,
        "status": bundle.status,
        "backend": bundle.backend,
        "verified": verified,
        "state_count": len(bundle.problem.game().states),
        "domain_size": None if bundle.domain is None else len(bundle.domain),
        "signed_utility": bundle.signed_utility,
        "strategy_rows": len(bundle.strategy_items),
        "problem_sha256": bundle.problem_sha256,
        "component_model_sha256": bundle.component_model_sha256,
        "certificate_claim": certificate.claim,
        "certificate_sha256": certificate.semantic_sha256,
        "certificate_statistics": certificate.statistics,
        "manifest_sha256": bundle.manifest_sha256,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    canonicalize = subparsers.add_parser(
        "canonicalize",
        help="validate and canonicalize one finite-safety problem",
    )
    canonicalize.add_argument("--input", type=Path, required=True)
    canonicalize.add_argument("--out", type=Path, required=True)

    synthesize = subparsers.add_parser(
        "synthesize",
        help="solve one problem and emit a proof bundle",
    )
    synthesize.add_argument("--input", type=Path, required=True)
    synthesize.add_argument("--out", type=Path, required=True)
    synthesize.add_argument(
        "--backend",
        choices=("auto", "native", "highs"),
        default="auto",
    )
    synthesize.add_argument(
        "--certificate-max-nodes",
        type=int,
        default=1_000_000,
    )

    verify = subparsers.add_parser(
        "verify",
        help="rebuild and verify one portable proof bundle",
    )
    verify.add_argument("--input", type=Path, required=True)

    inspect = subparsers.add_parser(
        "inspect",
        help="show bundle metadata after full verification",
    )
    inspect.add_argument("--input", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "canonicalize":
        problem = FiniteSafetyProblem.load(args.input)
        problem.write(args.out)
        result = {
            "name": problem.name,
            "problem_sha256": problem.semantic_sha256,
            "states": len(problem.game().states),
            "safe_transitions": len(problem.safe_relation),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "synthesize":
        problem = FiniteSafetyProblem.load(args.input)
        bundle = synthesize_proof_bundle(
            problem,
            backend=args.backend,
            certificate_max_nodes=args.certificate_max_nodes,
        )
        bundle.write(args.out)
        verified = verify_proof_bundle(bundle)
        if not verified:
            raise RuntimeError("generated proof bundle failed immediate replay")
        print(json.dumps(bundle_summary(bundle, verified), indent=2, sort_keys=True))
        return 0

    bundle = load_proof_bundle(args.input)
    verified = verify_proof_bundle(bundle)
    if not verified:
        print(
            json.dumps(
                {
                    "verified": False,
                    "manifest_sha256": bundle.manifest_sha256,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(bundle_summary(bundle, True), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

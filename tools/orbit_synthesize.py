#!/usr/bin/env python3
"""Synthesize and verify portable OrbitSynthesis proof bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.executable_bundle import (
    ExecutableProofBundle,
    synthesize_executable_bundle,
    verify_executable_bundle,
)
from orbitsynthesis.original_signature_dag import CompilationLimits
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
        "artifact": "semantic_proof_bundle",
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


def executable_summary(
    bundle: ExecutableProofBundle,
    verified: bool,
) -> dict[str, object]:
    result = bundle_summary(bundle.proof_bundle, verified)
    artifact = bundle.controller_artifact
    result.update(
        {
            "artifact": "executable_proof_bundle",
            "controller_dag_status": artifact.status,
            "controller_dag_reason": artifact.reason,
            "controller_artifact_sha256": artifact.semantic_sha256,
            "controller_dag_nodes": (
                None if artifact.dag is None else len(artifact.dag.nodes)
            ),
            "controller_dag_depth": (
                None
                if artifact.certificate is None
                else artifact.certificate.depth
            ),
            "controller_dag_sha256": (
                None if artifact.dag is None else artifact.dag.semantic_sha256
            ),
            "table_dag_certificate_sha256": (
                None
                if artifact.certificate is None
                else artifact.certificate.semantic_sha256
            ),
            "manifest_sha256": bundle.manifest_sha256,
        }
    )
    return result


def _add_backend_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--backend",
        choices=("auto", "native", "highs"),
        default="auto",
    )
    parser.add_argument(
        "--certificate-max-nodes",
        type=int,
        default=1_000_000,
    )


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
        help="solve one problem and emit a semantic proof bundle",
    )
    synthesize.add_argument("--input", type=Path, required=True)
    synthesize.add_argument("--out", type=Path, required=True)
    _add_backend_arguments(synthesize)

    synthesize_executable = subparsers.add_parser(
        "synthesize-executable",
        help="emit a proof bundle plus an original-signature controller DAG",
    )
    synthesize_executable.add_argument("--input", type=Path, required=True)
    synthesize_executable.add_argument("--out", type=Path, required=True)
    _add_backend_arguments(synthesize_executable)
    synthesize_executable.add_argument(
        "--dag-policy",
        choices=("required", "best_effort", "off"),
        default="required",
    )
    synthesize_executable.add_argument("--dag-max-depth", type=int, default=3)
    synthesize_executable.add_argument(
        "--dag-max-functions", type=int, default=10_000
    )
    synthesize_executable.add_argument(
        "--dag-max-combinations", type=int, default=500_000
    )
    synthesize_executable.add_argument(
        "--dag-max-exploration-nodes", type=int, default=50_000
    )
    synthesize_executable.add_argument(
        "--dag-max-operation-arity", type=int, default=4
    )

    verify = subparsers.add_parser(
        "verify",
        help="rebuild and verify one semantic proof bundle",
    )
    verify.add_argument("--input", type=Path, required=True)

    verify_executable = subparsers.add_parser(
        "verify-executable",
        help="verify semantic synthesis and the original-signature DAG",
    )
    verify_executable.add_argument("--input", type=Path, required=True)

    inspect = subparsers.add_parser(
        "inspect",
        help="show semantic bundle metadata after full verification",
    )
    inspect.add_argument("--input", type=Path, required=True)

    inspect_executable = subparsers.add_parser(
        "inspect-executable",
        help="show executable bundle metadata after full verification",
    )
    inspect_executable.add_argument("--input", type=Path, required=True)

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

    if args.command == "synthesize-executable":
        problem = FiniteSafetyProblem.load(args.input)
        limits = CompilationLimits(
            max_depth=args.dag_max_depth,
            max_semantic_functions=args.dag_max_functions,
            max_combinations=args.dag_max_combinations,
            max_exploration_nodes=args.dag_max_exploration_nodes,
            max_operation_arity=args.dag_max_operation_arity,
        )
        bundle = synthesize_executable_bundle(
            problem,
            backend=args.backend,
            certificate_max_nodes=args.certificate_max_nodes,
            dag_policy=args.dag_policy,
            dag_limits=limits,
        )
        bundle.write(args.out)
        verified = verify_executable_bundle(bundle)
        if not verified:
            raise RuntimeError(
                "generated executable proof bundle failed immediate replay"
            )
        print(json.dumps(executable_summary(bundle, verified), indent=2, sort_keys=True))
        return 0

    if args.command in {"verify-executable", "inspect-executable"}:
        bundle = ExecutableProofBundle.load(args.input)
        verified = verify_executable_bundle(bundle)
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
        print(json.dumps(executable_summary(bundle, True), indent=2, sort_keys=True))
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

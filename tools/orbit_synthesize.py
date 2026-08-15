#!/usr/bin/env python3
"""Synthesize and verify portable OrbitSynthesis proof bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.compiler_portfolio import CompilerPortfolioConfig
from orbitsynthesis.executable_bundle import (
    ExecutableProofBundle,
    synthesize_executable_bundle,
    verify_executable_bundle,
)
from orbitsynthesis.original_signature_dag import CompilationLimits
from orbitsynthesis.portfolio_bundle import (
    PortfolioProofBundle,
    synthesize_portfolio_bundle,
    verify_portfolio_bundle,
)
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


def portfolio_summary(
    bundle: PortfolioProofBundle,
    verified: bool,
) -> dict[str, object]:
    result = bundle_summary(bundle.proof_bundle, verified)
    portfolio = bundle.compiler_portfolio
    selected = portfolio.original_signature
    mdd = portfolio.mdd
    result.update(
        {
            "artifact": "compiler_portfolio_bundle",
            "portfolio_status": portfolio.status,
            "portfolio_policy": portfolio.config.policy,
            "selected_backend": portfolio.selected_backend,
            "selected_kind": portfolio.selected_kind,
            "portfolio_reason": portfolio.reason,
            "portfolio_sha256": portfolio.semantic_sha256,
            "attempts": [attempt.as_dict() for attempt in portfolio.attempts],
            "original_signature_nodes": (
                None if selected is None else len(selected.dag.nodes)
            ),
            "original_signature_depth": (
                None if selected is None else selected.certificate.depth
            ),
            "mdd_nodes": (
                None
                if mdd is None or mdd.diagram is None
                else len(mdd.diagram.nodes)
            ),
            "mdd_terminals": (
                None
                if mdd is None or mdd.diagram is None
                else len(mdd.diagram.terminals)
            ),
            "mdd_depth": (
                None
                if mdd is None or mdd.certificate is None
                else mdd.certificate.depth
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


def _add_exact_limits(parser: argparse.ArgumentParser, prefix: str = "dag") -> None:
    parser.add_argument(f"--{prefix}-max-depth", type=int, default=3)
    parser.add_argument(f"--{prefix}-max-functions", type=int, default=10_000)
    parser.add_argument(
        f"--{prefix}-max-combinations", type=int, default=500_000
    )
    parser.add_argument(
        f"--{prefix}-max-exploration-nodes", type=int, default=50_000
    )
    parser.add_argument(
        f"--{prefix}-max-operation-arity", type=int, default=4
    )


def _limits_from_args(args, prefix: str = "dag") -> CompilationLimits:
    normalized = prefix.replace("-", "_")
    return CompilationLimits(
        max_depth=getattr(args, f"{normalized}_max_depth"),
        max_semantic_functions=getattr(args, f"{normalized}_max_functions"),
        max_combinations=getattr(args, f"{normalized}_max_combinations"),
        max_exploration_nodes=getattr(
            args, f"{normalized}_max_exploration_nodes"
        ),
        max_operation_arity=getattr(
            args, f"{normalized}_max_operation_arity"
        ),
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
    _add_exact_limits(synthesize_executable, "dag")

    synthesize_portfolio = subparsers.add_parser(
        "synthesize-portfolio",
        help="select among exact, fixed-Q structural, MDD, and research tiers",
    )
    synthesize_portfolio.add_argument("--input", type=Path, required=True)
    synthesize_portfolio.add_argument("--out", type=Path, required=True)
    _add_backend_arguments(synthesize_portfolio)
    synthesize_portfolio.add_argument(
        "--portfolio-policy",
        choices=("practical", "original_signature", "mdd_only"),
        default="practical",
    )
    synthesize_portfolio.add_argument("--exact-max-rows", type=int, default=243)
    synthesize_portfolio.add_argument("--mdd-max-rows", type=int, default=250_000)
    synthesize_portfolio.add_argument(
        "--structural-max-candidates", type=int, default=400_000
    )
    synthesize_portfolio.add_argument("--disable-exact", action="store_true")
    synthesize_portfolio.add_argument("--disable-structural", action="store_true")
    synthesize_portfolio.add_argument("--disable-mdd", action="store_true")
    synthesize_portfolio.add_argument(
        "--no-shannon-diagnostic", action="store_true"
    )
    synthesize_portfolio.add_argument(
        "--allow-unsupported", action="store_true"
    )
    _add_exact_limits(synthesize_portfolio, "exact")

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

    verify_portfolio = subparsers.add_parser(
        "verify-portfolio",
        help="verify semantic synthesis and the selected portfolio implementation",
    )
    verify_portfolio.add_argument("--input", type=Path, required=True)

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

    inspect_portfolio = subparsers.add_parser(
        "inspect-portfolio",
        help="show compiler-portfolio metadata after full verification",
    )
    inspect_portfolio.add_argument("--input", type=Path, required=True)

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
        bundle = synthesize_executable_bundle(
            problem,
            backend=args.backend,
            certificate_max_nodes=args.certificate_max_nodes,
            dag_policy=args.dag_policy,
            dag_limits=_limits_from_args(args, "dag"),
        )
        bundle.write(args.out)
        verified = verify_executable_bundle(bundle)
        if not verified:
            raise RuntimeError(
                "generated executable proof bundle failed immediate replay"
            )
        print(json.dumps(executable_summary(bundle, verified), indent=2, sort_keys=True))
        return 0

    if args.command == "synthesize-portfolio":
        problem = FiniteSafetyProblem.load(args.input)
        config = CompilerPortfolioConfig(
            policy=args.portfolio_policy,
            exact_max_rows=args.exact_max_rows,
            mdd_max_rows=args.mdd_max_rows,
            structural_candidate_limit=args.structural_max_candidates,
            enable_exact=not args.disable_exact,
            enable_structural=not args.disable_structural,
            enable_mdd=not args.disable_mdd,
            include_shannon_diagnostic=not args.no_shannon_diagnostic,
            exact_limits=_limits_from_args(args, "exact"),
        )
        bundle = synthesize_portfolio_bundle(
            problem,
            backend=args.backend,
            certificate_max_nodes=args.certificate_max_nodes,
            portfolio_config=config,
            implementation_required=not args.allow_unsupported,
        )
        bundle.write(args.out)
        verified = verify_portfolio_bundle(bundle)
        if not verified:
            raise RuntimeError(
                "generated compiler-portfolio bundle failed immediate replay"
            )
        print(json.dumps(portfolio_summary(bundle, verified), indent=2, sort_keys=True))
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

    if args.command in {"verify-portfolio", "inspect-portfolio"}:
        bundle = PortfolioProofBundle.load(args.input)
        verified = verify_portfolio_bundle(bundle)
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
        print(json.dumps(portfolio_summary(bundle, True), indent=2, sort_keys=True))
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

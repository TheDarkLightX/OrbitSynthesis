#!/usr/bin/env python3
"""Exact calibration gate for the OrbitSynthesis compiler portfolio."""

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

from orbitsynthesis.compiler_portfolio import (
    CompilerPortfolioArtifact,
    CompilerPortfolioConfig,
    compile_portfolio,
    verify_portfolio,
)
from orbitsynthesis.decision_diagram import MDDArtifact
from orbitsynthesis.portfolio_bundle import (
    PortfolioProofBundle,
    synthesize_portfolio_bundle,
    verify_portfolio_bundle,
)
from orbitsynthesis.problem_io import FiniteSafetyProblem
from orbitsynthesis.structural_benchmarks import (
    q_discriminator,
    q_unary,
    quackenbush_q,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def attempt_map(artifact: CompilerPortfolioArtifact):
    return {attempt.backend: attempt for attempt in artifact.attempts}


def bundle_row(bundle: PortfolioProofBundle) -> dict[str, object]:
    portfolio = bundle.compiler_portfolio
    original = portfolio.original_signature
    mdd = portfolio.mdd
    return {
        "status": bundle.proof_bundle.status,
        "selected_backend": portfolio.selected_backend,
        "selected_kind": portfolio.selected_kind,
        "portfolio_sha256": portfolio.semantic_sha256,
        "manifest_sha256": bundle.manifest_sha256,
        "attempt_status": {
            attempt.backend: attempt.status for attempt in portfolio.attempts
        },
        "original_nodes": None if original is None else len(original.dag.nodes),
        "original_depth": (
            None if original is None else original.certificate.depth
        ),
        "mdd_nodes": (
            None if mdd is None or mdd.diagram is None else len(mdd.diagram.nodes)
        ),
        "mdd_terminals": (
            None
            if mdd is None or mdd.diagram is None
            else len(mdd.diagram.terminals)
        ),
        "mdd_depth": (
            None if mdd is None or mdd.certificate is None else mdd.certificate.depth
        ),
    }


def structural_router_case() -> dict[str, object]:
    algebra = quackenbush_q()
    points = tuple(product(algebra.values, repeat=5))
    table = {}
    for point in points:
        inner = q_discriminator(point[2], point[3], point[4])
        outer = q_discriminator(point[0], point[1], inner)
        table[point] = (outer, q_unary(outer))
    config = CompilerPortfolioConfig(
        policy="original_signature",
        exact_max_rows=1,
        enable_exact=False,
        enable_structural=True,
        enable_mdd=False,
        structural_candidate_limit=400_000,
    )
    artifact = compile_portfolio(
        algebra,
        input_arity=5,
        output_arity=2,
        table=table,
        config=config,
    )
    require(artifact.status == "compiled", "nested router did not compile")
    require(
        artifact.selected_backend == "fixed-q-structural-router",
        "nested router selected wrong backend",
    )
    require(artifact.original_signature is not None, "nested router lost DAG")
    require(len(artifact.original_signature.dag.nodes) == 3, "nested router node count")
    require(artifact.original_signature.certificate.depth == 3, "nested router depth")
    require(
        verify_portfolio(
            artifact,
            algebra,
            input_arity=5,
            output_arity=2,
            table=table,
        ),
        "nested router portfolio replay",
    )
    return {
        "rows": len(points),
        "nodes": len(artifact.original_signature.dag.nodes),
        "depth": artifact.original_signature.certificate.depth,
        "portfolio_sha256": artifact.semantic_sha256,
        "attempts": {
            attempt.backend: attempt.as_dict() for attempt in artifact.attempts
        },
    }


def mdd_compression_case() -> dict[str, object]:
    algebra = quackenbush_q()
    points = tuple(product(algebra.values, repeat=6))
    table = {}
    for point in points:
        # A repeated-subcube controller: only x0, x2, and x5 matter.
        value = point[5] if point[0] == point[2] else point[0]
        table[point] = (value,)
    config = CompilerPortfolioConfig(
        policy="mdd_only",
        enable_exact=False,
        enable_structural=False,
        enable_mdd=True,
        mdd_max_rows=10_000,
    )
    artifact = compile_portfolio(
        algebra,
        input_arity=6,
        output_arity=1,
        table=table,
        config=config,
    )
    require(artifact.status == "compiled", "MDD case did not compile")
    require(artifact.selected_backend == "reduced-vector-mdd", "wrong MDD backend")
    require(artifact.mdd is not None and artifact.mdd.diagram is not None, "missing MDD")
    require(len(artifact.mdd.diagram.nodes) < len(points), "MDD did not compress")
    require(
        verify_portfolio(
            artifact,
            algebra,
            input_arity=6,
            output_arity=1,
            table=table,
        ),
        "MDD portfolio replay",
    )
    return {
        "rows": len(points),
        "nodes": len(artifact.mdd.diagram.nodes),
        "terminals": len(artifact.mdd.diagram.terminals),
        "depth": artifact.mdd.certificate.depth if artifact.mdd.certificate else None,
        "variable_order": list(artifact.mdd.diagram.variable_order),
        "portfolio_sha256": artifact.semantic_sha256,
    }


def mutation_checks(bundle: PortfolioProofBundle) -> dict[str, bool]:
    portfolio = bundle.compiler_portfolio
    rejected = {}
    rejected["shannon_selection"] = not verify_portfolio_bundle(
        replace(
            bundle,
            compiler_portfolio=replace(
                portfolio,
                selected_backend="fixed-q-shannon-experimental",
            ),
        )
    )
    selected_attempts = list(portfolio.attempts)
    for index, attempt in enumerate(selected_attempts):
        if attempt.backend == portfolio.selected_backend:
            selected_attempts[index] = replace(attempt, status="diagnostic")
            break
    rejected["selected_attempt_not_compiled"] = not verify_portfolio_bundle(
        replace(
            bundle,
            compiler_portfolio=replace(
                portfolio,
                attempts=tuple(selected_attempts),
            ),
        )
    )
    payload = bundle.as_dict()
    payload["manifest_sha256"] = "0" * 64
    try:
        PortfolioProofBundle.from_dict(payload)
    except ValueError:
        rejected["outer_manifest"] = True
    else:
        rejected["outer_manifest"] = False
    require(all(rejected.values()), "one portfolio mutation survived")
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    optimal_problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/discriminator_policy.json"
    )
    infeasible_problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/coupled_required_infeasible.json"
    )

    default_bundle = synthesize_portfolio_bundle(
        optimal_problem,
        backend="native",
    )
    require(verify_portfolio_bundle(default_bundle), "default portfolio replay")
    require(
        default_bundle.compiler_portfolio.selected_backend
        == "exact-semantic-closure",
        "tiny controller did not prefer exact closure",
    )
    default_attempts = attempt_map(default_bundle.compiler_portfolio)
    require(default_attempts["fixed-q-shannon-experimental"].status == "diagnostic", "missing Shannon diagnostic")
    require(
        default_attempts["fixed-q-shannon-experimental"].metrics["automatic_selection"] is False,
        "Shannon diagnostic became selectable",
    )

    structural_bundle = synthesize_portfolio_bundle(
        optimal_problem,
        backend="native",
        portfolio_config=CompilerPortfolioConfig(
            policy="original_signature",
            enable_exact=False,
            enable_structural=True,
            enable_mdd=False,
        ),
    )
    require(verify_portfolio_bundle(structural_bundle), "structural bundle replay")
    require(
        structural_bundle.compiler_portfolio.selected_backend
        == "fixed-q-structural-router",
        "structural-only bundle selected wrong backend",
    )
    require(
        structural_bundle.compiler_portfolio.original_signature is not None
        and len(
            structural_bundle.compiler_portfolio.original_signature.dag.nodes
        )
        == 1,
        "discriminator structural recognizer did not emit one node",
    )

    mdd_bundle = synthesize_portfolio_bundle(
        optimal_problem,
        backend="native",
        portfolio_config=CompilerPortfolioConfig(
            policy="mdd_only",
            enable_exact=False,
            enable_structural=False,
            enable_mdd=True,
        ),
    )
    require(verify_portfolio_bundle(mdd_bundle), "MDD bundle replay")
    require(
        mdd_bundle.compiler_portfolio.selected_backend == "reduced-vector-mdd",
        "MDD-only bundle selected wrong backend",
    )

    infeasible_bundle = synthesize_portfolio_bundle(
        infeasible_problem,
        backend="native",
    )
    require(verify_portfolio_bundle(infeasible_bundle), "infeasible portfolio replay")
    require(
        infeasible_bundle.compiler_portfolio.status == "not_applicable",
        "infeasible problem retained implementation",
    )

    require(
        PortfolioProofBundle.from_json(default_bundle.to_json()).manifest_sha256
        == default_bundle.manifest_sha256,
        "portfolio JSON roundtrip",
    )

    unsupported = compile_portfolio(
        quackenbush_q(),
        input_arity=1,
        output_arity=1,
        table={(0,): (0,), (1,): (1,), (2,): (2,)},
        config=CompilerPortfolioConfig(
            policy="practical",
            enable_exact=False,
            enable_structural=False,
            enable_mdd=False,
        ),
    )
    require(unsupported.status == "unsupported", "disabled portfolio not unsupported")
    require(
        verify_portfolio(
            unsupported,
            quackenbush_q(),
            input_arity=1,
            output_arity=1,
            table={(0,): (0,), (1,): (1,), (2,): (2,)},
        ),
        "unsupported portfolio envelope",
    )

    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        default_bundle.write(args.out_dir / "default.portfolio.json")
        structural_bundle.write(args.out_dir / "structural.portfolio.json")
        mdd_bundle.write(args.out_dir / "mdd.portfolio.json")
        infeasible_bundle.write(args.out_dir / "infeasible.portfolio.json")

    result = {
        "schema": "orbit-synthesis/compiler-portfolio-gate/v1",
        "default": bundle_row(default_bundle),
        "structural": bundle_row(structural_bundle),
        "mdd": bundle_row(mdd_bundle),
        "infeasible": bundle_row(infeasible_bundle),
        "nested_router": structural_router_case(),
        "mdd_compression": mdd_compression_case(),
        "unsupported": {
            "status": unsupported.status,
            "reason": unsupported.reason,
            "portfolio_sha256": unsupported.semantic_sha256,
        },
        "mutations": mutation_checks(default_bundle),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

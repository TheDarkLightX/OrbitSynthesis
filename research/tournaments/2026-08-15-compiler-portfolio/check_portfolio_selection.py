#!/usr/bin/env python3
"""Consistency checks for deterministic compiler-portfolio selection."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.compiler_portfolio import CompilerPortfolioConfig
from orbitsynthesis.compiler_portfolio_policy import verify_portfolio_selection
from orbitsynthesis.portfolio_bundle import (
    synthesize_portfolio_bundle,
    verify_portfolio_bundle,
)
from orbitsynthesis.problem_io import FiniteSafetyProblem


def main() -> int:
    problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/discriminator_policy.json"
    )
    bundle = synthesize_portfolio_bundle(problem, backend="native")
    portfolio = bundle.compiler_portfolio
    attempts = list(portfolio.attempts)

    exact_index = next(
        index
        for index, attempt in enumerate(attempts)
        if attempt.backend == "exact-semantic-closure"
    )
    shannon_index = next(
        index
        for index, attempt in enumerate(attempts)
        if attempt.backend == "fixed-q-shannon-experimental"
    )

    if portfolio.original_signature is None:
        raise RuntimeError("default portfolio lost its exact implementation")
    lower_tier_selection = replace(
        portfolio,
        selected_backend="fixed-q-structural-router",
        original_signature=replace(
            portfolio.original_signature,
            backend="fixed-q-structural-router",
        ),
    )

    changed_scores = list(attempts)
    exact_score = changed_scores[exact_index].score
    if exact_score is None:
        raise RuntimeError("exact attempt lost its score")
    changed_scores[exact_index] = replace(
        changed_scores[exact_index],
        score=exact_score + 10_000,
    )
    diagnostic_score_change = replace(
        portfolio,
        attempts=tuple(changed_scores),
    )

    unsupported_with_candidate = replace(
        portfolio,
        status="unsupported",
        selected_backend=None,
        selected_kind=None,
        original_signature=None,
        mdd=None,
        reason="inconsistent_unsupported_status",
    )

    research_as_executable = list(attempts)
    research_as_executable[shannon_index] = replace(
        research_as_executable[shannon_index],
        status="compiled",
        implementation_kind="original_signature",
        score=0,
        reason=None,
    )
    research_selection = replace(
        portfolio,
        selected_backend="fixed-q-shannon-experimental",
        selected_kind="original_signature",
        attempts=tuple(research_as_executable),
    )

    duplicate_attempts = replace(
        portfolio,
        attempts=(*portfolio.attempts, portfolio.attempts[0]),
    )

    mdd_policy = synthesize_portfolio_bundle(
        problem,
        backend="native",
        portfolio_config=CompilerPortfolioConfig(
            policy="mdd_only",
            enable_exact=True,
            enable_structural=True,
            enable_mdd=False,
        ),
        implementation_required=False,
    )

    results = {
        "lower_priority_selection_rejected": (
            not verify_portfolio_selection(lower_tier_selection)
            and not verify_portfolio_bundle(
                replace(bundle, compiler_portfolio=lower_tier_selection)
            )
        ),
        "diagnostic_score_does_not_change_tier": (
            verify_portfolio_selection(diagnostic_score_change)
            and verify_portfolio_bundle(
                replace(bundle, compiler_portfolio=diagnostic_score_change)
            )
        ),
        "unsupported_with_eligible_candidate_rejected": (
            not verify_portfolio_selection(unsupported_with_candidate)
            and not verify_portfolio_bundle(
                replace(bundle, compiler_portfolio=unsupported_with_candidate)
            )
        ),
        "research_diagnostic_selection_rejected": (
            not verify_portfolio_selection(research_selection)
            and not verify_portfolio_bundle(
                replace(bundle, compiler_portfolio=research_selection)
            )
        ),
        "duplicate_backend_rejected": (
            not verify_portfolio_selection(duplicate_attempts)
        ),
        "policy_excluded_candidates_allow_unsupported": (
            mdd_policy.compiler_portfolio.status == "unsupported"
            and verify_portfolio_selection(mdd_policy.compiler_portfolio)
            and verify_portfolio_bundle(mdd_policy)
        ),
    }
    if not all(results.values()):
        raise RuntimeError("one portfolio selection consistency check failed")
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

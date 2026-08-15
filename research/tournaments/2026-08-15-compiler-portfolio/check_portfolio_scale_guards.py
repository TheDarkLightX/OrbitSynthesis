#!/usr/bin/env python3
"""Check that explicit-table size routes work to the intended portfolio tier."""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.compiler_portfolio import CompilerPortfolioConfig
from orbitsynthesis.compiler_portfolio_policy import verify_portfolio_selection
from orbitsynthesis.compiler_portfolio_runtime import (
    compile_portfolio_runtime,
    verify_portfolio_runtime,
)
from orbitsynthesis.structural_benchmarks import quackenbush_q


def main() -> int:
    algebra = quackenbush_q()
    input_arity = 8
    points = tuple(product(algebra.values, repeat=input_arity))
    table = {point: (point[0],) for point in points}
    artifact = compile_portfolio_runtime(
        algebra,
        input_arity=input_arity,
        output_arity=1,
        table=table,
        config=CompilerPortfolioConfig(
            policy="practical",
            exact_max_rows=243,
            mdd_max_rows=10_000,
            structural_candidate_limit=400_000,
        ),
    )
    attempts = {attempt.backend: attempt for attempt in artifact.attempts}
    exact = attempts["exact-semantic-closure"]
    structural = attempts["fixed-q-structural-router"]
    mdd = attempts["reduced-vector-mdd"]
    shannon = attempts["fixed-q-shannon-experimental"]

    checks = {
        "rows": len(points),
        "exact_skipped": (
            exact.status == "not_applicable"
            and exact.reason == "above_tiny_table_threshold"
        ),
        "structural_skipped": (
            structural.status == "not_applicable"
            and structural.reason == "above_structural_table_threshold"
            and structural.metrics["row_limit"] == 2_187
        ),
        "mdd_compiled": mdd.status == "compiled",
        "mdd_selected": (
            artifact.selected_backend == "reduced-vector-mdd"
            and artifact.selected_kind == "mdd"
        ),
        "mdd_one_node": (
            artifact.mdd is not None
            and artifact.mdd.diagram is not None
            and len(artifact.mdd.diagram.nodes) == 1
            and len(artifact.mdd.diagram.terminals) == 3
        ),
        "shannon_diagnostic_only": (
            shannon.status == "diagnostic"
            and shannon.metrics["automatic_selection"] is False
        ),
        "selection_verified": verify_portfolio_selection(artifact),
        "implementation_verified": verify_portfolio_runtime(
            artifact,
            algebra,
            input_arity=input_arity,
            output_arity=1,
            table=table,
        ),
    }
    if not all(
        value is True
        for key, value in checks.items()
        if key != "rows"
    ):
        raise RuntimeError("one compiler portfolio scale guard failed")
    print(json.dumps(checks, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

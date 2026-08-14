#!/usr/bin/env python3
"""Diagnostic benchmark for OrbitSynthesis exact optimization backends."""
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_external_optimization import FAMILIES, SyntheticKernel, component_model, scenarios
from orbitsynthesis.domain_optimization import optimize_weighted_domain
from orbitsynthesis.external_optimization import (
    ExternalOptimizationError,
    solve_weighted_cnf_command,
    solve_weighted_cnf_highs,
    solve_weighted_cnf_pysat_rc2,
)


def summary(samples):
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, int(0.95 * len(ordered)) - 1))
    return {
        "runs": len(ordered),
        "min_seconds": ordered[0],
        "median_seconds": statistics.median(ordered),
        "p95_seconds": ordered[index],
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
        if witness is not None:
            domain = tuple(sorted(witness.domain))
        elif hasattr(result, "domain"):
            domain = tuple(sorted(result.domain))
        else:
            domain = None
        if hasattr(result, "objective"):
            score = result.objective.score
        else:
            score = getattr(result, "signed_utility", None)
        candidate = (
            result.status if hasattr(result, "status") else "optimal",
            domain,
            score,
        )
        if semantic is None:
            semantic = candidate
        elif semantic != candidate:
            raise AssertionError("backend result changed across benchmark repeats")
    return summary(samples), semantic


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--require-pysat", action="store_true")
    args = parser.parse_args()
    if args.repeat < 1:
        raise SystemExit("repeat must be positive")

    reference = (
        ROOT
        / "research/tournaments/2026-08-14-external-maxsat-benchmark"
        / "tools/reference_maxsat_solver.py"
    )
    rows = []
    pysat_available = True

    for family, state_count, candidate_data in FAMILIES:
        kernel = SyntheticKernel(state_count, candidate_data)
        model = component_model(state_count, candidate_data)
        # Benchmark one unique-primary and one signed-primary case per family.
        for scenario, weights, required, forbidden in scenarios(state_count)[:2]:
            cnf = model.cnf(
                required_states=required,
                forbidden_states=forbidden,
            )
            wcnf = model.weighted_cnf(
                required_states=required,
                forbidden_states=forbidden,
                state_weights=weights,
                default_weight=0,
            )
            backend_rows = {}

            native_stats, native_semantic = timed(
                lambda: optimize_weighted_domain(
                    kernel,
                    state_weights=weights,
                    required_states=required,
                    forbidden_states=forbidden,
                ),
                args.repeat,
            )
            backend_rows["native"] = {
                **native_stats,
                "semantic": native_semantic,
            }

            highs_stats, highs_semantic = timed(
                lambda: solve_weighted_cnf_highs(
                    model,
                    cnf,
                    wcnf,
                    state_weights=weights,
                    default_weight=0,
                ),
                args.repeat,
            )
            backend_rows["highs"] = {
                **highs_stats,
                "semantic": highs_semantic,
            }

            if wcnf.variable_count <= 18:
                command_stats, command_semantic = timed(
                    lambda: solve_weighted_cnf_command(
                        model,
                        cnf,
                        wcnf,
                        [sys.executable, str(reference), "{wcnf}"],
                        state_weights=weights,
                        default_weight=0,
                    ),
                    args.repeat,
                )
                backend_rows["reference_process"] = {
                    **command_stats,
                    "semantic": command_semantic,
                }

            if pysat_available:
                try:
                    pysat_stats, pysat_semantic = timed(
                        lambda: solve_weighted_cnf_pysat_rc2(
                            model,
                            cnf,
                            wcnf,
                            state_weights=weights,
                            default_weight=0,
                        ),
                        args.repeat,
                    )
                except ExternalOptimizationError as error:
                    if "python-sat is required" not in str(error):
                        raise
                    pysat_available = False
                    if args.require_pysat:
                        raise
                else:
                    backend_rows["pysat_rc2"] = {
                        **pysat_stats,
                        "semantic": pysat_semantic,
                    }

            expected_score = native_semantic[2]
            for backend, data in backend_rows.items():
                semantic = data["semantic"]
                score = semantic[2]
                if score is not None and score != expected_score:
                    raise AssertionError(
                        f"{backend} benchmark changed the primary optimum"
                    )

            rows.append(
                {
                    "family": family,
                    "scenario": scenario,
                    "states": state_count,
                    "variables": wcnf.variable_count,
                    "hard_clauses": len(wcnf.hard_clauses),
                    "soft_clauses": len(wcnf.soft_state_units),
                    "backends": backend_rows,
                }
            )

    result = {
        "schema": "orbit-synthesis/external-optimization-benchmark/v1",
        "diagnostic_only": True,
        "python": sys.version,
        "platform": platform.platform(),
        "repeat": args.repeat,
        "pysat_available": pysat_available,
        "rows": rows,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

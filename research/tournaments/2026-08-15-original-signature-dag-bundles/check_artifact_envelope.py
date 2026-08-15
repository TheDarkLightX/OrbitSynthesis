#!/usr/bin/env python3
"""Focused in-memory envelope mutations for executable proof bundles."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.executable_bundle import (
    synthesize_executable_bundle,
    verify_executable_bundle,
)
from orbitsynthesis.original_signature_dag import CompilationLimits
from orbitsynthesis.problem_io import FiniteSafetyProblem


def main() -> int:
    optimal_problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/discriminator_policy.json"
    )
    infeasible_problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/coupled_required_infeasible.json"
    )
    optimal = synthesize_executable_bundle(
        optimal_problem,
        backend="native",
        dag_policy="required",
        dag_limits=CompilationLimits(max_depth=1),
    )
    infeasible = synthesize_executable_bundle(
        infeasible_problem,
        backend="native",
        dag_policy="required",
    )
    compiled = optimal.controller_artifact
    empty = infeasible.controller_artifact
    if compiled.dag is None or compiled.certificate is None:
        raise RuntimeError("optimal example did not compile")

    results = {
        "infeasible_with_dag": not verify_executable_bundle(
            replace(
                infeasible,
                controller_artifact=replace(empty, dag=compiled.dag),
            )
        ),
        "infeasible_with_certificate": not verify_executable_bundle(
            replace(
                infeasible,
                controller_artifact=replace(
                    empty,
                    certificate=compiled.certificate,
                ),
            )
        ),
        "unsupported_with_executable_data": not verify_executable_bundle(
            replace(
                optimal,
                controller_artifact=replace(
                    compiled,
                    status="unsupported",
                    reason="forged_unsupported",
                ),
            )
        ),
        "optimal_not_applicable": not verify_executable_bundle(
            replace(
                optimal,
                controller_artifact=replace(
                    compiled,
                    status="not_applicable",
                    reason="forged_not_applicable",
                    dag=None,
                    certificate=None,
                ),
            )
        ),
        "wrong_compiler": not verify_executable_bundle(
            replace(
                optimal,
                controller_artifact=replace(
                    compiled,
                    compiler="untrusted-compiler/v0",
                ),
            )
        ),
    }
    if not all(results.values()):
        raise RuntimeError("one executable artifact envelope mutation was accepted")
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

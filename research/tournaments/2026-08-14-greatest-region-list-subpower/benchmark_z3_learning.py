#!/usr/bin/env python3
"""Real-solver benchmark for eager selectors versus lazy conflict learning.

This is a calibration lane, not a production performance claim.  Both paths
use the same installed Z3 Optimize backend and every returned domain is replayed
by the deterministic OrbitSynthesis component model.  The semantic receipt is
separated from wall-clock observations so that timing noise is never promoted
to correctness evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from z3 import Bool, If, Not, Optimize, Or, Sum, is_true, sat
from z3 import get_version_string as z3_version

from orbitsynthesis.domain_model import (
    CompiledDomainWitness,
    QuasiPrimalDomainModel,
    compile_quasi_primal_domain_model,
)
from orbitsynthesis.domain_nogood import (
    DomainConflictCore,
    minimize_domain_failure,
    verify_domain_conflict_core_against_model,
)
from orbitsynthesis.domain_solver import (
    decode_cnf_model,
    maximum_weight_domain_exhaustive,
)
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.principal_greatest_region import (
    build_principal_no_greatest_region_witness,
)
from orbitsynthesis.safety import FiniteSafetyGame

Q = (0, 1, 2)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def qunary(x: int) -> int:
    return (1, 0, 1)[x]


def algebra() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {"d": (3, discriminator), "u": (1, qunary)},
    )


@dataclass(frozen=True)
class SolveResult:
    objective: int
    domain: frozenset[tuple[int, ...]]
    variable_count: int
    hard_clause_count: int
    optimizer_calls: int
    component_checks: int
    learned_cores: tuple[DomainConflictCore, ...]
    elapsed_ns: int


def _sum_terms(terms):
    terms = tuple(terms)
    return Sum(*terms) if terms else 0


def _model_domain(z3_model, state_variables):
    return frozenset(
        state
        for state, variable in state_variables.items()
        if is_true(z3_model.eval(variable, model_completion=True))
    )


def solve_eager(
    model: QuasiPrimalDomainModel,
    weights: dict[tuple[int, ...], int],
) -> SolveResult:
    """Optimize the complete component-selector CNF."""

    encoding = model.cnf()
    variables = {
        index: Bool(f"e_{index}") for index in range(1, encoding.variable_count + 1)
    }
    optimizer = Optimize()
    for clause in encoding.clauses:
        optimizer.add(
            Or(
                *(
                    variables[abs(literal)]
                    if literal > 0
                    else Not(variables[abs(literal)])
                    for literal in clause
                )
            )
        )
    state_variables = {
        state: variables[variable] for state, variable in encoding.state_variables
    }
    optimizer.maximize(
        _sum_terms(
            If(state_variables[state], weights[state], 0) for state in model.states
        )
    )
    started = time.perf_counter_ns()
    status = optimizer.check()
    if status != sat:
        raise RuntimeError(f"eager Z3 optimization returned {status}")
    z3_model = optimizer.model()
    elapsed = time.perf_counter_ns() - started

    literals = tuple(
        variable
        if is_true(z3_model.eval(expression, model_completion=True))
        else -variable
        for variable, expression in variables.items()
    )
    witness = decode_cnf_model(model, encoding, literals)
    objective = sum(weights[state] for state in witness.domain)
    return SolveResult(
        objective=objective,
        domain=witness.domain,
        variable_count=encoding.variable_count,
        hard_clause_count=len(encoding.clauses),
        optimizer_calls=1,
        component_checks=1,
        learned_cores=(),
        elapsed_ns=elapsed,
    )


def _core_clause(core: DomainConflictCore, state_variables):
    return Or(
        *(
            Not(state_variables[literal.state])
            if literal.included
            else state_variables[literal.state]
            for literal in core.literals
        )
    )


def solve_lazy(
    model: QuasiPrimalDomainModel,
    weights: dict[tuple[int, ...], int],
    *,
    max_rounds: int = 10_000,
) -> SolveResult:
    """Optimize state variables and add only model-verified conflict clauses."""

    state_variables = {
        state: Bool(f"l_{index}") for index, state in enumerate(model.states)
    }
    optimizer = Optimize()
    optimizer.maximize(
        _sum_terms(
            If(state_variables[state], weights[state], 0) for state in model.states
        )
    )
    cores: list[DomainConflictCore] = []
    started = time.perf_counter_ns()

    for round_index in range(1, max_rounds + 1):
        status = optimizer.check()
        if status != sat:
            raise RuntimeError(
                "lazy Z3 optimization exhausted all domains without a witness"
            )
        z3_model = optimizer.model()
        domain = _model_domain(z3_model, state_variables)
        solution = model.solve_domain(domain)
        if isinstance(solution, CompiledDomainWitness):
            elapsed = time.perf_counter_ns() - started
            return SolveResult(
                objective=sum(weights[state] for state in domain),
                domain=domain,
                variable_count=len(state_variables),
                hard_clause_count=len(cores),
                optimizer_calls=round_index,
                component_checks=round_index,
                learned_cores=tuple(cores),
                elapsed_ns=elapsed,
            )

        core = minimize_domain_failure(solution)
        if not core.holds(domain):
            raise AssertionError("learned core does not reject its proposal")
        if not verify_domain_conflict_core_against_model(
            model,
            solution,
            core,
            require_minimal=True,
        ):
            raise AssertionError("learned core failed model replay")
        if not core.literals:
            raise AssertionError("empty core is outside this benchmark scope")
        cores.append(core)
        optimizer.add(_core_clause(core, state_variables))

    raise RuntimeError(f"lazy optimization exceeded max_rounds={max_rounds}")


def random_models(
    A: FiniteAlgebra,
    *,
    seed: int = 0x1EA4C,
    relations: int = 24,
):
    rng = random.Random(seed)
    states = tuple((left, right) for left in Q for right in Q)
    rows = []
    for relation_index in range(relations):
        safe = set()
        for state in states:
            mask = rng.randrange(1 << len(states))
            for output_index, output in enumerate(states):
                if mask & (1 << output_index):
                    safe.add((state, (), output))
        game = FiniteSafetyGame(A, 2, 0, safe)
        model = compile_quasi_primal_domain_model(game)
        weights = {state: rng.randrange(1, 10) for state in states}
        rows.append((f"random-{relation_index:02d}", model, weights))
    return tuple(rows)


def principal_model(A: FiniteAlgebra):
    witness = build_principal_no_greatest_region_witness(A)
    if witness is None:
        raise RuntimeError("principal witness construction returned None")
    model = compile_quasi_primal_domain_model(witness.game(A))
    return "principal", model, {state: 1 for state in model.states}


def _semantic_row(name, model, eager, lazy, reference_weight):
    if eager.objective != lazy.objective:
        raise AssertionError(f"{name}: eager/lazy objective mismatch")
    if reference_weight is not None and eager.objective != reference_weight:
        raise AssertionError(f"{name}: solver/reference objective mismatch")
    if not model.domain_feasible(eager.domain):
        raise AssertionError(f"{name}: eager domain failed deterministic replay")
    if not model.domain_feasible(lazy.domain):
        raise AssertionError(f"{name}: lazy domain failed deterministic replay")
    return {
        "name": name,
        "states": len(model.states),
        "components": len(model.components),
        "objective": eager.objective,
        "eager_variables": eager.variable_count,
        "eager_hard_clauses": eager.hard_clause_count,
        "lazy_variables": lazy.variable_count,
        "lazy_optimizer_calls": lazy.optimizer_calls,
        "lazy_learned_clauses": len(lazy.learned_cores),
        "lazy_learned_literals": sum(len(core.literals) for core in lazy.learned_cores),
    }


def benchmark(repeats: int) -> dict[str, object]:
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    A = algebra()
    instances = (*random_models(A), principal_model(A))
    semantic_rows = []
    timing_samples = {
        name: {"eager": [], "lazy": []} for name, _model, _weights in instances
    }

    for repeat in range(repeats):
        for name, model, weights in instances:
            # Alternate order to reduce a systematic warm-cache advantage.
            if repeat % 2:
                lazy = solve_lazy(model, weights)
                eager = solve_eager(model, weights)
            else:
                eager = solve_eager(model, weights)
                lazy = solve_lazy(model, weights)
            timing_samples[name]["eager"].append(eager.elapsed_ns / 1_000_000)
            timing_samples[name]["lazy"].append(lazy.elapsed_ns / 1_000_000)

            if repeat:
                continue
            reference_weight = None
            if len(model.states) <= 20:
                reference = maximum_weight_domain_exhaustive(
                    model,
                    state_weights=weights,
                    exhaustive_state_limit=20,
                )
                if reference is None:
                    raise AssertionError(f"{name}: missing exhaustive optimum")
                reference_weight = reference.total_weight
            semantic_rows.append(
                _semantic_row(
                    name,
                    model,
                    eager,
                    lazy,
                    reference_weight,
                )
            )

    random_rows = [row for row in semantic_rows if row["name"].startswith("random-")]
    principal = next(row for row in semantic_rows if row["name"] == "principal")
    semantic = {
        "schema": "orbit-synthesis/z3-eager-lazy-domain-benchmark/v1",
        "backend": "Z3 Optimize weighted Boolean objectives",
        "random": {
            "instances": len(random_rows),
            "objectives_sum": sum(row["objective"] for row in random_rows),
            "eager_variables_sum": sum(row["eager_variables"] for row in random_rows),
            "eager_hard_clauses_sum": sum(
                row["eager_hard_clauses"] for row in random_rows
            ),
            "lazy_variables_sum": sum(row["lazy_variables"] for row in random_rows),
            "lazy_optimizer_calls_sum": sum(
                row["lazy_optimizer_calls"] for row in random_rows
            ),
            "lazy_learned_clauses_sum": sum(
                row["lazy_learned_clauses"] for row in random_rows
            ),
            "lazy_learned_literals_sum": sum(
                row["lazy_learned_literals"] for row in random_rows
            ),
        },
        "principal": principal,
        "checks": {
            "all_eager_domains_replayed": True,
            "all_lazy_domains_replayed": True,
            "all_random_objectives_match_exhaustive": True,
            "all_learned_cores_model_verified": True,
        },
    }
    canonical = json.dumps(semantic, sort_keys=True, separators=(",", ":"))
    per_instance_timing = {
        name: {
            method: {
                "median_ms": statistics.median(samples),
                "min_ms": min(samples),
                "max_ms": max(samples),
            }
            for method, samples in methods.items()
        }
        for name, methods in timing_samples.items()
    }
    random_names = tuple(name for name in timing_samples if name.startswith("random-"))
    random_totals = {
        method: [
            sum(timing_samples[name][method][repeat] for name in random_names)
            for repeat in range(repeats)
        ]
        for method in ("eager", "lazy")
    }
    timing = {
        "principal": per_instance_timing["principal"],
        "random_24_instance_corpus": {
            method: {
                "median_ms": statistics.median(samples),
                "min_ms": min(samples),
                "max_ms": max(samples),
            }
            for method, samples in random_totals.items()
        },
    }
    return {
        "semantic": semantic,
        "semantic_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "environment": {
            "python": sys.version.split()[0],
            "z3": z3_version(),
            "repeats": repeats,
        },
        "timing_observations_not_correctness_evidence": timing,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--semantic-only",
        action="store_true",
        help="omit environment-specific wall-clock observations",
    )
    args = parser.parse_args()
    result = benchmark(args.repeats)
    if args.semantic_only:
        result = {
            "semantic": result["semantic"],
            "semantic_sha256": result["semantic_sha256"],
            "solver": result["environment"]["z3"],
        }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit solver-neutral SAT/MaxSAT certificate decoding."""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import compile_quasi_primal_domain_model
from orbitsynthesis.domain_solver import (
    decode_cnf_model,
    literals_for_witness,
    maximum_weight_domain_exhaustive,
    normalize_boolean_model,
    parse_dimacs_model,
)
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.principal_greatest_region import (
    build_principal_no_greatest_region_witness,
)
from orbitsynthesis.safety import FiniteSafetyGame

Q = (0, 1, 2)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def qunary(x: int) -> int:
    return (1, 0, 1)[x]


def algebra() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {"d": (3, discriminator), "u": (1, qunary)},
    )


def solver_text(literals: tuple[int, ...], width: int = 11) -> str:
    lines = ["c synthetic solver certificate", "s OPTIMUM FOUND", "o 0"]
    for start in range(0, len(literals), width):
        lines.append(
            "v " + " ".join(map(str, literals[start : start + width])) + " 0"
        )
    return "\n".join(lines) + "\n"


def reference_optimum(game, required, weights):
    best_weight = None
    best_domains = []
    for mask in range(1 << len(game.states)):
        domain = frozenset(
            state
            for index, state in enumerate(game.states)
            if mask & (1 << index)
        )
        if not required <= domain or not game.quasi_primal_domain_feasible(domain):
            continue
        value = sum(weights[state] for state in domain)
        if best_weight is None or value > best_weight:
            best_weight = value
            best_domains = [domain]
        elif value == best_weight:
            best_domains.append(domain)
    return best_weight, tuple(best_domains)


def targeted(A: FiniteAlgebra) -> dict[str, object]:
    game = FiniteSafetyGame(
        A,
        1,
        0,
        {
            ((0,), (), (0,)),
            ((1,), (), (0,)),
            ((2,), (), (2,)),
        },
    )
    model = compile_quasi_primal_domain_model(game)
    required = frozenset(((0,),))
    weights = {(0,): 5, (1,): 3, (2,): 1}
    optimum = maximum_weight_domain_exhaustive(
        model,
        required_states=required,
        state_weights=weights,
        exhaustive_state_limit=3,
    )
    require(optimum is not None, "missing targeted optimum")
    reference_weight, reference_domains = reference_optimum(
        game,
        required,
        weights,
    )
    require(optimum.total_weight == reference_weight, "targeted optimum weight")
    require(optimum.witness.domain in reference_domains, "targeted optimum domain")

    encoding = model.cnf(required_states=required)
    literals = literals_for_witness(model, encoding, optimum.witness)
    parsed = parse_dimacs_model(solver_text(literals))
    decoded = decode_cnf_model(model, encoding, parsed)
    require(decoded.domain == optimum.witness.domain, "targeted decoded domain")
    require(decoded.strategy == optimum.witness.strategy, "targeted decoded strategy")

    contradictory = False
    try:
        normalize_boolean_model(encoding.variable_count, (1, -1))
    except ValueError:
        contradictory = True
    require(contradictory, "contradictory-literal mutation escaped")

    selected_variables = {
        variable
        for component_index, candidate_index, variable
        in encoding.candidate_variables
        if component_index == 0
    }
    broken = tuple(
        -abs(literal)
        if abs(literal) in selected_variables
        else literal
        for literal in literals
    )
    rejected = False
    try:
        decode_cnf_model(model, encoding, broken)
    except ValueError:
        rejected = True
    require(rejected, "missing-component-selector mutation escaped")

    return {
        "optimum_weight": optimum.total_weight,
        "optimum_domain": [list(state) for state in sorted(optimum.witness.domain)],
        "variables": encoding.variable_count,
        "clauses": len(encoding.clauses),
        "literals": len(literals),
        "contradictory_mutation_rejected": contradictory,
        "selector_mutation_rejected": rejected,
    }


def random_weighted_differential(
    A: FiniteAlgebra,
    *,
    seed: int = 0x50A7,
    relations: int = 64,
) -> dict[str, int]:
    rng = random.Random(seed)
    states = tuple((value,) for value in Q)
    inputs = states
    checked = decoded = infeasible_required = 0

    for _ in range(relations):
        safe = set()
        for state in states:
            for input_value in inputs:
                mask = rng.randrange(1 << len(states))
                for index, output in enumerate(states):
                    if mask & (1 << index):
                        safe.add((state, input_value, output))
        game = FiniteSafetyGame(A, 1, 1, safe)
        model = compile_quasi_primal_domain_model(game)
        weights = {state: rng.randrange(1, 8) for state in states}
        required = frozenset(
            state for state in states if rng.randrange(4) == 0
        )

        optimum = maximum_weight_domain_exhaustive(
            model,
            required_states=required,
            state_weights=weights,
            exhaustive_state_limit=3,
        )
        reference_weight, reference_domains = reference_optimum(
            game,
            required,
            weights,
        )
        require((optimum is None) == (reference_weight is None), "feasibility drift")
        if optimum is None:
            infeasible_required += 1
            checked += 1
            continue

        require(optimum.total_weight == reference_weight, "random optimum weight")
        require(optimum.witness.domain in reference_domains, "random optimum domain")
        encoding = model.cnf(required_states=required)
        literals = literals_for_witness(model, encoding, optimum.witness)
        certificate = solver_text(literals, width=rng.randrange(3, 13))
        replay = decode_cnf_model(
            model,
            encoding,
            parse_dimacs_model(certificate),
        )
        require(replay.domain == optimum.witness.domain, "random decoded domain")
        require(replay.strategy == optimum.witness.strategy, "random decoded strategy")
        decoded += 1
        checked += 1

    return {
        "seed": seed,
        "relations": relations,
        "instances": checked,
        "decoded_optima": decoded,
        "infeasible_required_sets": infeasible_required,
    }


def principal_certificate(A: FiniteAlgebra) -> dict[str, int]:
    witness = build_principal_no_greatest_region_witness(A)
    require(witness is not None, "missing principal witness")
    game = witness.game(A)
    model = compile_quasi_primal_domain_model(game)
    encoding = model.cnf(required_states=witness.left_domain)
    solution = model.solve_domain(witness.left_domain)
    require(hasattr(solution, "component_choices"), "principal left domain failed")
    literals = literals_for_witness(model, encoding, solution)
    decoded = decode_cnf_model(model, encoding, parse_dimacs_model(solver_text(literals)))
    require(decoded.domain == witness.left_domain, "principal decoded domain")
    require(decoded.strategy == solution.strategy, "principal decoded strategy")
    return {
        "states": len(model.states),
        "components": len(model.components),
        "candidate_rules": sum(len(component.candidates) for component in model.components),
        "variables": encoding.variable_count,
        "clauses": len(encoding.clauses),
        "literals": len(literals),
    }


def make_receipt() -> dict[str, object]:
    A = algebra()
    result = {
        "schema": "orbit-synthesis/domain-solver-certificate/v1",
        "targeted": targeted(A),
        "random_weighted": random_weighted_differential(A),
        "principal": principal_certificate(A),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    result = make_receipt()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

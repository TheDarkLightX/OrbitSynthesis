#!/usr/bin/env python3
"""Differential audit for compiled quasi-primal domain constraints."""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import (
    CompiledDomainFailure,
    CompiledDomainWitness,
    compile_quasi_primal_domain_model,
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


def clause_satisfied(clause, assignment) -> bool:
    return any(
        assignment[abs(literal)] == (literal > 0)
        for literal in clause
    )


def verify_cnf_witness(model, domain, solution, encoding) -> None:
    require(isinstance(solution, CompiledDomainWitness), "missing model witness")
    state_variables = dict(encoding.state_variables)
    candidate_variables = {
        (component_index, candidate_index): variable
        for component_index, candidate_index, variable
        in encoding.candidate_variables
    }
    assignment = {
        variable: state in domain
        for state, variable in state_variables.items()
    }
    for variable in candidate_variables.values():
        assignment[variable] = False
    for component_index, candidate_index in enumerate(solution.component_choices):
        assignment[candidate_variables[(component_index, candidate_index)]] = True
    require(
        all(clause_satisfied(clause, assignment) for clause in encoding.clauses),
        "compiled witness does not satisfy emitted CNF",
    )


def verify_cnf_failure(model, domain, failure, encoding) -> None:
    require(isinstance(failure, CompiledDomainFailure), "missing model failure")
    state_variables = dict(encoding.state_variables)
    component_candidates = model.components[failure.component_index].candidates
    # With state variables fixed, every candidate selector in the failing
    # component must violate at least one of its hard clauses.
    for candidate in component_candidates:
        violated = bool(candidate.forbidden_states & domain) or any(
            source in domain and target not in domain
            for source, target in candidate.closure_edges
        )
        require(violated, "failing component contains a CNF-satisfying selector")
    require(
        all(state in state_variables for state in domain),
        "domain contains an unknown state",
    )


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
    encoding = model.cnf(required_states=((0,),))
    weighted = model.weighted_cnf(
        required_states=((0,),),
        state_weights={(0,): 5, (1,): 3, (2,): 1},
    )

    rows = []
    for mask in range(1 << len(game.states)):
        domain = frozenset(
            state
            for index, state in enumerate(game.states)
            if mask & (1 << index)
        )
        reference = game.quasi_primal_domain_feasible(domain)
        solution = model.solve_domain(domain)
        require(
            isinstance(solution, CompiledDomainWitness) == reference,
            "targeted compiled model disagrees with reference",
        )
        if reference:
            verify_cnf_witness(model, domain, solution, model.cnf())
        else:
            verify_cnf_failure(model, domain, solution, model.cnf())
        rows.append([mask, reference])

    require(
        model.maximal_domains(exhaustive_state_limit=3)
        == game.maximal_quasi_primal_domains(exhaustive_state_limit=3),
        "targeted maximal-domain mismatch",
    )
    require((dict(encoding.state_variables)[(0,)],) in encoding.clauses, "required unit")
    require(weighted.top_weight == 10, "weighted top drift")
    require(len(weighted.soft_state_units) == 3, "soft-state census")
    require(encoding.dimacs().startswith("p cnf "), "DIMACS header")
    require(weighted.wdimacs().startswith("p wcnf "), "WCNF header")

    return {
        "components": len(model.components),
        "candidate_rules": sum(len(component.candidates) for component in model.components),
        "variables": encoding.variable_count,
        "clauses": len(encoding.clauses),
        "domain_rows": rows,
        "maximal_domains": [
            [list(state) for state in sorted(domain)]
            for domain in model.maximal_domains(exhaustive_state_limit=3)
        ],
        "weighted_top": weighted.top_weight,
    }


def random_differential(
    A: FiniteAlgebra,
    *,
    seed: int = 0xD04A1,
    relations: int = 96,
) -> dict[str, int]:
    rng = random.Random(seed)
    states = tuple((value,) for value in Q)
    inputs = states
    checked = feasible = infeasible = cnf_checks = 0

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
        encoding = model.cnf()

        require(
            model.maximal_domains(exhaustive_state_limit=3)
            == game.maximal_quasi_primal_domains(exhaustive_state_limit=3),
            "random maximal-domain mismatch",
        )

        for mask in range(1 << len(states)):
            domain = frozenset(
                state
                for index, state in enumerate(states)
                if mask & (1 << index)
            )
            reference = game.quasi_primal_domain_feasible(domain)
            solution = model.solve_domain(domain)
            require(
                isinstance(solution, CompiledDomainWitness) == reference,
                "random compiled model disagrees with reference",
            )
            if reference:
                verify_cnf_witness(model, domain, solution, encoding)
                feasible += 1
            else:
                verify_cnf_failure(model, domain, solution, encoding)
                infeasible += 1
            checked += 1
            cnf_checks += 1

    return {
        "seed": seed,
        "relations": relations,
        "domain_instances": checked,
        "cnf_checks": cnf_checks,
        "feasible": feasible,
        "infeasible": infeasible,
    }


def principal_differential(A: FiniteAlgebra) -> dict[str, object]:
    witness = build_principal_no_greatest_region_witness(A)
    require(witness is not None, "missing principal witness")
    game = witness.game(A)
    model = compile_quasi_primal_domain_model(game)
    rows = []
    for label, domain in (
        ("left", witness.left_domain),
        ("right", witness.right_domain),
        ("union", witness.left_domain | witness.right_domain),
    ):
        reference = game.quasi_primal_domain_feasible(domain)
        solution = model.solve_domain(domain)
        require(
            isinstance(solution, CompiledDomainWitness) == reference,
            "principal compiled model mismatch",
        )
        rows.append(
            {
                "label": label,
                "feasible": reference,
                "failing_component": (
                    solution.component_index
                    if isinstance(solution, CompiledDomainFailure)
                    else None
                ),
            }
        )
    require([row["feasible"] for row in rows] == [True, True, False], "pattern")
    return {
        "components": len(model.components),
        "candidate_rules": sum(len(component.candidates) for component in model.components),
        "rows": rows,
    }


def make_receipt() -> dict[str, object]:
    A = algebra()
    result = {
        "schema": "orbit-synthesis/quasi-primal-domain-cnf/v1",
        "targeted": targeted(A),
        "random_differential": random_differential(A),
        "principal_differential": principal_differential(A),
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

#!/usr/bin/env python3
"""Differential audit for learned domain conflict clauses."""

from __future__ import annotations

import hashlib
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
from orbitsynthesis.domain_nogood import (
    SignedStateLiteral,
    minimize_domain_failure,
    verify_domain_conflict_core,
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


def clause_satisfied(clause, domain, state_variables) -> bool:
    state_by_variable = {variable: state for state, variable in state_variables.items()}
    return any(
        (state_by_variable[abs(literal)] in domain) == (literal > 0)
        for literal in clause
    )


def synthetic_shared_literal() -> dict[str, object]:
    s0, s1, s2, shared = ((0,), (1,), (2,), (3,))
    failure = CompiledDomainFailure(
        domain=frozenset((s0, s1, s2, shared)),
        component_index=7,
        representative=("synthetic",),
        forbidden_hits=(
            (0, (s0, shared)),
            (1, (s1, shared)),
            (2, (s2, shared)),
        ),
        missing_closure_edges=((0, ()), (1, ()), (2, ())),
    )
    core = minimize_domain_failure(failure)
    require(
        core.literals == (SignedStateLiteral(shared, True),),
        "shared-literal minimization failed",
    )
    return {
        "candidate_count": len(core.candidate_witnesses),
        "core": [
            {"state": list(literal.state), "included": literal.included}
            for literal in core.literals
        ],
    }


def random_differential(
    A: FiniteAlgebra,
    *,
    seed: int = 0xC0FE,
    relations: int = 96,
) -> dict[str, object]:
    rng = random.Random(seed)
    states = tuple((value,) for value in Q)
    inputs = states
    failures = matching_domains = clauses_checked = 0
    core_sizes = []
    clause_sizes = []

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
        state_variables = dict(model.cnf().state_variables)

        for mask in range(1 << len(states)):
            domain = frozenset(
                state
                for index, state in enumerate(states)
                if mask & (1 << index)
            )
            solution = model.solve_domain(domain)
            if isinstance(solution, CompiledDomainWitness):
                continue
            require(isinstance(solution, CompiledDomainFailure), "failure type")
            core = minimize_domain_failure(solution)
            require(core.holds(domain), "core does not hold on source domain")
            require(
                verify_domain_conflict_core(solution, core, require_minimal=True),
                "core verifier failed",
            )
            clause = core.blocking_clause(state_variables)
            require(
                not clause_satisfied(clause, domain, state_variables),
                "learned clause does not block the source domain",
            )

            component = model.components[solution.component_index]
            for other_mask in range(1 << len(states)):
                other = frozenset(
                    state
                    for index, state in enumerate(states)
                    if other_mask & (1 << index)
                )
                if not core.holds(other):
                    continue
                require(
                    not any(candidate.accepts(other) for candidate in component.candidates),
                    "core permits a candidate in its failing component",
                )
                require(
                    not model.domain_feasible(other),
                    "learned core blocks a globally feasible domain",
                )
                matching_domains += 1

            failures += 1
            clauses_checked += 1
            core_sizes.append(len(core.literals))
            clause_sizes.append(len(clause))

    require(failures > 0, "empty random failure corpus")
    return {
        "seed": seed,
        "relations": relations,
        "failed_domains": failures,
        "matching_domains_checked": matching_domains,
        "clauses_checked": clauses_checked,
        "minimum_core_size": min(core_sizes),
        "maximum_core_size": max(core_sizes),
        "total_core_literals": sum(core_sizes),
        "total_clause_literals": sum(clause_sizes),
    }


def principal_core(A: FiniteAlgebra) -> dict[str, object]:
    witness = build_principal_no_greatest_region_witness(A)
    require(witness is not None, "missing principal witness")
    model = compile_quasi_primal_domain_model(witness.game(A))
    domain = witness.left_domain | witness.right_domain
    failure = model.solve_domain(domain)
    require(isinstance(failure, CompiledDomainFailure), "principal union should fail")
    core = minimize_domain_failure(failure)
    require(core.holds(domain), "principal core")
    require(
        verify_domain_conflict_core(failure, core, require_minimal=True),
        "principal core verification",
    )
    clause = core.blocking_clause(dict(model.cnf().state_variables))
    return {
        "component_index": core.component_index,
        "component_candidates": len(
            model.components[core.component_index].candidates
        ),
        "core_literals": [
            {"state": list(literal.state), "included": literal.included}
            for literal in core.literals
        ],
        "blocking_clause": list(clause),
    }


def make_receipt() -> dict[str, object]:
    A = algebra()
    result = {
        "schema": "orbit-synthesis/domain-conflict-core/v1",
        "synthetic": synthetic_shared_literal(),
        "random_differential": random_differential(A),
        "principal": principal_core(A),
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

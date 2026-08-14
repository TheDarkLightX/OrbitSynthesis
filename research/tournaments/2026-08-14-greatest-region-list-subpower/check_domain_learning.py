#!/usr/bin/env python3
"""Differential audit for lazy conflict-learning domain optimization."""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_learning import maximum_weight_domain_with_learning
from orbitsynthesis.domain_model import (
    ComponentCandidateRule,
    ComponentRuleSet,
    QuasiPrimalDomainModel,
    compile_quasi_primal_domain_model,
)
from orbitsynthesis.domain_solver import maximum_weight_domain_exhaustive
from orbitsynthesis.finite_algebra import FiniteAlgebra
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
    state_by_variable = {
        variable: state for state, variable in state_variables.items()
    }
    return any(
        (state_by_variable[abs(literal)] in domain) == (literal > 0)
        for literal in clause
    )


def synthetic_force_multiplier() -> dict[str, object]:
    """One shared literal removes half of a 12-state search space."""

    states = tuple((index,) for index in range(12))
    blocked = states[0]
    model = QuasiPrimalDomainModel(
        states=states,
        observations=(),
        components=(
            ComponentRuleSet(
                representative=("synthetic",),
                observations=(),
                candidates=(
                    ComponentCandidateRule(
                        representative_output=(),
                        assignment_items=(),
                        forbidden_states=frozenset((blocked,)),
                        closure_edges=frozenset(),
                    ),
                ),
            ),
        ),
    )
    weights = {
        state: (100 if state == blocked else 1)
        for state in states
    }
    reference = maximum_weight_domain_exhaustive(
        model,
        state_weights=weights,
        exhaustive_state_limit=12,
    )
    learned = maximum_weight_domain_with_learning(
        model,
        state_weights=weights,
        exhaustive_state_limit=12,
    )
    require(reference is not None and learned.optimum is not None, "synthetic optimum")
    require(
        learned.optimum.total_weight == reference.total_weight,
        "synthetic weight mismatch",
    )
    require(
        learned.optimum.witness.domain == reference.witness.domain,
        "synthetic domain mismatch",
    )
    require(blocked not in learned.optimum.witness.domain, "blocked state survived")
    require(learned.stats.component_model_checks == 2, "synthetic model-check count")
    require(learned.stats.learned_core_count == 1, "synthetic core count")
    require(
        len(learned.conflict_cores[0].literals) == 1,
        "synthetic core should be one literal",
    )
    require(
        learned.stats.component_model_checks < (1 << len(states)),
        "learning did not reduce expensive model checks",
    )

    guard_rejected = False
    try:
        maximum_weight_domain_with_learning(
            model,
            state_weights=weights,
            exhaustive_state_limit=12,
            max_rounds=1,
        )
    except RuntimeError:
        guard_rejected = True
    require(guard_rejected, "round guard did not fail closed")

    return {
        "states": len(states),
        "reference_domain_checks": 1 << len(states),
        "learned_model_checks": learned.stats.component_model_checks,
        "learned_cores": learned.stats.learned_core_count,
        "learned_literals": learned.stats.learned_literal_count,
        "optimum_weight": learned.optimum.total_weight,
        "optimum_domain_size": len(learned.optimum.witness.domain),
        "max_round_guard_rejected": guard_rejected,
    }


def random_exact_differential(
    A: FiniteAlgebra,
    *,
    seed: int = 0x1EA4C,
    relations: int = 24,
) -> dict[str, object]:
    """Compare lazy learning with complete optimization on nine-state games."""

    rng = random.Random(seed)
    states = tuple(
        (left, right)
        for left in Q
        for right in Q
    )
    learned_checks = reference_checks = learned_cores = learned_literals = 0
    matching_domains_checked = 0
    eager_clauses = learned_clauses = 0
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
        weights = {
            state: rng.randrange(1, 10)
            for state in states
        }

        reference = maximum_weight_domain_exhaustive(
            model,
            state_weights=weights,
            exhaustive_state_limit=9,
        )
        learned = maximum_weight_domain_with_learning(
            model,
            state_weights=weights,
            exhaustive_state_limit=9,
        )
        require(reference is not None and learned.optimum is not None, "random optimum")
        require(
            learned.optimum.total_weight == reference.total_weight,
            "random optimum weight mismatch",
        )
        require(
            learned.optimum.witness.domain == reference.witness.domain,
            "random optimum domain mismatch",
        )

        state_variables = dict(model.cnf().state_variables)
        for core, clause in zip(
            learned.conflict_cores,
            learned.blocking_clauses,
            strict=True,
        ):
            require(
                not clause_satisfied(
                    clause,
                    frozenset(
                        literal.state
                        for literal in core.literals
                        if literal.included
                    ),
                    state_variables,
                ) or any(not literal.included for literal in core.literals),
                "blocking-clause polarity sanity",
            )
            for mask in range(1 << len(states)):
                domain = frozenset(
                    state
                    for index, state in enumerate(states)
                    if mask & (1 << index)
                )
                if not core.holds(domain):
                    continue
                require(
                    not model.domain_feasible(domain),
                    "learned conflict core blocks a feasible domain",
                )
                require(
                    not clause_satisfied(clause, domain, state_variables),
                    "blocking clause does not reject a core-matching domain",
                )
                matching_domains_checked += 1

        reference_checks += 1 << len(states)
        learned_checks += learned.stats.component_model_checks
        learned_cores += learned.stats.learned_core_count
        learned_literals += learned.stats.learned_literal_count
        eager_clauses += len(model.cnf().clauses)
        learned_clauses += len(learned.blocking_clauses)
        rows.append(
            {
                "relation": relation_index,
                "optimum_weight": learned.optimum.total_weight,
                "optimum_domain_size": len(learned.optimum.witness.domain),
                "model_checks": learned.stats.component_model_checks,
                "learned_cores": learned.stats.learned_core_count,
                "eager_hard_clauses": len(model.cnf().clauses),
            }
        )

    require(
        learned_checks < reference_checks,
        "random corpus did not reduce component-model checks",
    )
    require(learned_cores > 0, "random corpus learned no conflicts")
    return {
        "seed": seed,
        "relations": relations,
        "states_per_relation": len(states),
        "reference_component_model_checks": reference_checks,
        "learned_component_model_checks": learned_checks,
        "learned_core_count": learned_cores,
        "learned_literal_count": learned_literals,
        "matching_domains_checked": matching_domains_checked,
        "eager_hard_clause_total": eager_clauses,
        "lazy_learned_clause_total": learned_clauses,
        "rows": rows,
    }


def validation_mutations() -> dict[str, bool]:
    A = algebra()
    game = FiniteSafetyGame(A, 1, 0, {((0,), (), (0,))})
    model = compile_quasi_primal_domain_model(game)

    overlap_rejected = False
    try:
        maximum_weight_domain_with_learning(
            model,
            required_states=((0,),),
            forbidden_states=((0,),),
            exhaustive_state_limit=3,
        )
    except ValueError:
        overlap_rejected = True

    unknown_weight_rejected = False
    try:
        maximum_weight_domain_with_learning(
            model,
            state_weights={(99,): 1},
            exhaustive_state_limit=3,
        )
    except ValueError:
        unknown_weight_rejected = True

    nonpositive_weight_rejected = False
    try:
        maximum_weight_domain_with_learning(
            model,
            state_weights={(0,): 0},
            exhaustive_state_limit=3,
        )
    except ValueError:
        nonpositive_weight_rejected = True

    require(overlap_rejected, "required/forbidden overlap escaped")
    require(unknown_weight_rejected, "unknown weight escaped")
    require(nonpositive_weight_rejected, "nonpositive weight escaped")
    return {
        "overlap_rejected": overlap_rejected,
        "unknown_weight_rejected": unknown_weight_rejected,
        "nonpositive_weight_rejected": nonpositive_weight_rejected,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/lazy-domain-conflict-learning/v1",
        "synthetic": synthetic_force_multiplier(),
        "random_exact": random_exact_differential(algebra()),
        "mutations": validation_mutations(),
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

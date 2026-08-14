#!/usr/bin/env python3
"""Differential and mutation audit for exact weighted domain optimization."""

from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path

from orbitsynthesis.domain_api import CompiledParameterizedKernel
from orbitsynthesis.domain_model import compile_quasi_primal_domain_model
from orbitsynthesis.domain_optimization import (
    WeightedBitsetDomainOptimizer,
    WeightedObjective,
    verify_weighted_domain_result,
)
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.safety import FiniteSafetyGame

ROOT = Path(__file__).resolve().parents[3]
SCENARIOS = (
    ("unit", (1, 1, 1), 0, 0),
    ("skew", (3, -2, 1), 0, 0),
    ("negative", (-3, 5, 0), 0, 0),
    ("zero", (0, 0, 0), 0, 0),
    ("require-zero", (2, 1, -4), 1, 0),
    ("forbid-two", (1, 4, 9), 0, 4),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def q_algebra() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        (0, 1, 2),
        {
            "d": (3, lambda x, y, z: z if x == y else x),
            "u": (1, lambda x: (1, 0, 1)[x]),
        },
    )


def unary_game(algebra: FiniteAlgebra, relation_mask: int) -> FiniteSafetyGame:
    transitions = []
    for source in range(3):
        for target in range(3):
            bit = 1 << (3 * source + target)
            if relation_mask & bit:
                transitions.append(((source,), (), (target,)))
    return FiniteSafetyGame(algebra, 1, 0, transitions)


def objective(mask: int, weights: tuple[int, ...]) -> WeightedObjective:
    return WeightedObjective(
        score=sum(weight for index, weight in enumerate(weights) if mask & (1 << index)),
        cardinality=mask.bit_count(),
        mask=mask,
    )


def brute_force(
    engine: WeightedBitsetDomainOptimizer,
    weights: tuple[int, ...],
    required: int,
    forbidden: int,
) -> WeightedObjective | None:
    best = None
    for mask in range(1 << engine.n):
        if required & ~mask or forbidden & mask:
            continue
        if not engine.is_feasible_mask(mask):
            continue
        row = objective(mask, weights)
        if best is None or row > best:
            best = row
    return best


def validate_wcnf(
    model,
    game: FiniteSafetyGame,
    weights: tuple[int, ...],
    required_states,
    forbidden_states,
    expected: WeightedObjective | None,
) -> None:
    mapping = {state: weights[index] for index, state in enumerate(game.states)}
    encoding = model.weighted_cnf(
        required_states=required_states,
        forbidden_states=forbidden_states,
        state_weights=mapping,
        default_weight=0,
    )
    variable_by_state = dict(model.cnf().state_variables)
    expected_soft = tuple(
        (
            variable_by_state[state] if weight > 0 else -variable_by_state[state],
            abs(weight),
        )
        for state, weight in mapping.items()
        if weight != 0
    )
    require(encoding.soft_state_units == expected_soft, "signed WCNF units drift")
    require(
        encoding.top_weight == sum(weight for _literal, weight in expected_soft) + 1,
        "WCNF top weight drift",
    )
    hard = set(encoding.hard_clauses)
    require(
        all((variable_by_state[state],) in hard for state in required_states),
        "required WCNF unit missing",
    )
    require(
        all((-variable_by_state[state],) in hard for state in forbidden_states),
        "forbidden WCNF unit missing",
    )
    require(encoding.wdimacs().startswith("p wcnf "), "WCNF header drift")

    if expected is None:
        return
    negative_offset = sum(-weight for weight in weights if weight < 0)
    reward = negative_offset + expected.score
    best_reward = None
    for mask in range(1 << len(game.states)):
        domain = frozenset(
            state
            for index, state in enumerate(game.states)
            if mask & (1 << index)
        )
        if not frozenset(required_states) <= domain:
            continue
        if frozenset(forbidden_states) & domain:
            continue
        if not model.domain_feasible(domain):
            continue
        current = sum(
            soft_weight
            for literal, soft_weight in expected_soft
            if (
                literal > 0
                and mask & (1 << (literal - 1))
            ) or (
                literal < 0
                and not mask & (1 << ((-literal) - 1))
            )
        )
        if best_reward is None or current > best_reward:
            best_reward = current
    require(best_reward == reward, "WCNF reward is not the signed optimum")


def unary_corpus() -> dict[str, object]:
    algebra = q_algebra()
    isomorphisms = algebra.internal_isomorphisms()
    digest_rows = []
    feasible_instances = 0
    infeasible_instances = 0
    verified_instances = 0
    total_search_nodes = 0
    total_bound_prunes = 0
    total_conflict_prunes = 0
    domain_model_masks = 0
    wcnf_instances = 0

    for relation_mask in range(1 << 9):
        game = unary_game(algebra, relation_mask)
        kernel = CompiledParameterizedKernel(
            game,
            frozenset(),
            internal_isomorphisms=isomorphisms,
        )
        model = compile_quasi_primal_domain_model(
            game,
            internal_isomorphisms=isomorphisms,
        )
        engine_for_model = WeightedBitsetDomainOptimizer(kernel)
        for mask in range(1 << len(game.states)):
            domain = frozenset(
                state
                for index, state in enumerate(game.states)
                if mask & (1 << index)
            )
            require(
                model.domain_feasible(domain) == engine_for_model.is_feasible_mask(mask),
                "component model and pointed rules disagree",
            )
            domain_model_masks += 1

        for label, weights, required, forbidden in SCENARIOS:
            engine = WeightedBitsetDomainOptimizer(kernel)
            required_states = tuple(
                game.states[index] for index in range(3) if required & (1 << index)
            )
            forbidden_states = tuple(
                game.states[index] for index in range(3) if forbidden & (1 << index)
            )
            expected = brute_force(engine, weights, required, forbidden)
            validate_wcnf(
                model,
                game,
                weights,
                required_states,
                forbidden_states,
                expected,
            )
            wcnf_instances += 1
            try:
                result = engine.optimize(
                    state_weights={state: weights[index] for index, state in enumerate(game.states)},
                    default_weight=0,
                    required_states=required_states,
                    forbidden_states=forbidden_states,
                )
            except ValueError:
                require(expected is None, "optimizer rejected a feasible unary instance")
                digest_rows.append([relation_mask, label, None])
                infeasible_instances += 1
                continue

            require(expected is not None, "optimizer accepted an infeasible unary instance")
            require(result.objective == expected, "weighted objective mismatch")
            require(
                verify_weighted_domain_result(
                    kernel,
                    result,
                    state_weights={
                        state: weights[index] for index, state in enumerate(game.states)
                    },
                    default_weight=0,
                    required_states=required_states,
                    forbidden_states=forbidden_states,
                    exhaustive_state_limit=3,
                ),
                "weighted certificate verification failed",
            )
            digest_rows.append(
                [
                    relation_mask,
                    label,
                    [
                        result.objective.score,
                        result.objective.cardinality,
                        result.objective.mask,
                    ],
                ]
            )
            feasible_instances += 1
            verified_instances += 1
            total_search_nodes += result.stats.nodes
            total_bound_prunes += result.stats.bound_prunes
            total_conflict_prunes += result.stats.conflict_prunes

    rendered = json.dumps(digest_rows, separators=(",", ":"))
    return {
        "relations": 1 << 9,
        "scenarios": len(SCENARIOS),
        "instances": len(digest_rows),
        "feasible_instances": feasible_instances,
        "infeasible_instances": infeasible_instances,
        "verified_instances": verified_instances,
        "domain_model_masks": domain_model_masks,
        "wcnf_instances": wcnf_instances,
        "total_search_nodes": total_search_nodes,
        "total_bound_prunes": total_bound_prunes,
        "total_conflict_prunes": total_conflict_prunes,
        "corpus_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
    }


def preference_audit() -> dict[str, object]:
    algebra = q_algebra()
    game = unary_game(algebra, (1 << 9) - 1)
    kernel = CompiledParameterizedKernel(
        game,
        frozenset(),
        internal_isomorphisms=algebra.internal_isomorphisms(),
    )
    preferences = {
        ((0,), (1,)): 5,
        ((1,), (0,)): 5,
        ((2,), (2,)): 3,
    }
    result = WeightedBitsetDomainOptimizer(kernel).optimize(
        state_weights={state: 1 for state in game.states},
        action_preferences=preferences,
    )
    require(result.domain == frozenset(game.states), "preference test lost a state")
    require(result.action_preference_score == 13, "action preference optimum drift")
    require(
        result.strategy == {(0,): (1,), (1,): (0,), (2,): (2,)},
        "action-preferred term table drift",
    )

    mutated = dict(result.strategy)
    mutated[(2,)] = (1,)
    mutated_score = sum(preferences.get(item, 0) for item in mutated.items())
    require(mutated_score < result.action_preference_score, "strategy mutation ineffective")
    return {
        "domain_mask": result.objective.mask,
        "action_preference_score": result.action_preference_score,
        "strategy": [
            [list(observation), list(output)]
            for observation, output in result.strategy_items
        ],
        "mutation_score": mutated_score,
        "semantic_sha256": result.semantic_sha256,
    }


def nine_state_pruning() -> dict[str, object]:
    algebra = q_algebra()
    states = tuple(product(algebra.values, repeat=2))
    game = FiniteSafetyGame(
        algebra,
        2,
        0,
        ((state, (), state) for state in states),
    )
    kernel = CompiledParameterizedKernel(
        game,
        frozenset(),
        internal_isomorphisms=algebra.internal_isomorphisms(),
    )
    result = WeightedBitsetDomainOptimizer(kernel).optimize(
        state_weights={state: 1 for state in states}
    )
    require(result.domain == frozenset(states), "identity game did not keep every state")
    require(result.objective.score == 9, "identity game score drift")
    require(result.stats.nodes < (1 << len(states)), "branch-and-bound did not beat enumeration")
    require(
        verify_weighted_domain_result(
            kernel,
            result,
            state_weights={state: 1 for state in states},
            exhaustive_state_limit=9,
        ),
        "nine-state optimality verification failed",
    )
    return {
        "states": len(states),
        "exhaustive_masks": 1 << len(states),
        "search_nodes": result.stats.nodes,
        "bound_prunes": result.stats.bound_prunes,
        "conflict_prunes": result.stats.conflict_prunes,
        "trace_sha256": result.trace_sha256,
    }


def input_validation() -> dict[str, object]:
    algebra = q_algebra()
    game = unary_game(algebra, (1 << 9) - 1)
    kernel = CompiledParameterizedKernel(
        game,
        frozenset(),
        internal_isomorphisms=algebra.internal_isomorphisms(),
    )
    engine = WeightedBitsetDomainOptimizer(kernel)
    rejected = []
    for label, kwargs in (
        ("unknown-state", {"state_weights": {(9,): 1}}),
        ("noninteger-weight", {"state_weights": {(0,): 1.5}}),
        ("required-forbidden-overlap", {
            "required_states": ((0,),),
            "forbidden_states": ((0,),),
        }),
    ):
        try:
            engine.optimize(**kwargs)
        except (TypeError, ValueError):
            rejected.append(label)
    require(len(rejected) == 3, "input validation mutation escaped")
    return {"rejected": rejected}


def main() -> None:
    result = {
        "schema": "orbit-synthesis/weighted-domain-optimizer-primary/v1",
        "unary_corpus": unary_corpus(),
        "preference": preference_audit(),
        "nine_state_pruning": nine_state_pruning(),
        "input_validation": input_validation(),
        "source_sha256": {
            "domain_optimization.py": hashlib.sha256(
                (ROOT / "src/orbitsynthesis/domain_optimization.py").read_bytes()
            ).hexdigest(),
            "domain_model.py": hashlib.sha256(
                (ROOT / "src/orbitsynthesis/domain_model.py").read_bytes()
            ).hexdigest(),
        },
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

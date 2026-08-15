#!/usr/bin/env python3
"""Differential audit for the practical fixed-domain component backend."""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.principal_greatest_region import (
    build_principal_no_greatest_region_witness,
)
from orbitsynthesis.safety import FiniteSafetyGame
from orbitsynthesis.safety_components import (
    quasi_primal_domain_result,
    verify_quasi_primal_domain_result,
)

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


def targeted_obstruction(A: FiniteAlgebra) -> dict[str, object]:
    game = FiniteSafetyGame(
        A,
        state_arity=1,
        input_arity=0,
        safe_relation={
            ((0,), (), (0,)),
            ((1,), (), (0,)),
            ((2,), (), (2,)),
        },
    )
    impossible = frozenset(((0,), (1,)))
    result = quasi_primal_domain_result(game, impossible)
    require(not result.feasible, "targeted coupled domain escaped")
    require(result.obstruction is not None, "missing component obstruction")
    require(
        any(
            rejection.reason
            == "transported output violates target local domain"
            for rejection in result.obstruction.candidate_rejections
        ),
        "obstruction missed the complement-coupled target failure",
    )

    feasible = frozenset(((0,),))
    success = quasi_primal_domain_result(game, feasible)
    require(success.feasible, "one-sided domain should be feasible")
    require(
        verify_quasi_primal_domain_result(game, feasible, success),
        "one-sided strategy certificate failed",
    )

    return {
        "impossible_domain": [list(state) for state in sorted(impossible)],
        "component_size": len(result.obstruction.observations),
        "candidate_rejections": [
            {
                "candidate": list(rejection.candidate),
                "reason": rejection.reason,
                "source": (
                    list(rejection.source_observation)
                    if rejection.source_observation is not None
                    else None
                ),
                "target": (
                    list(rejection.target_observation)
                    if rejection.target_observation is not None
                    else None
                ),
                "forced_output": (
                    list(rejection.forced_output)
                    if rejection.forced_output is not None
                    else None
                ),
            }
            for rejection in result.obstruction.candidate_rejections
        ],
        "one_sided_strategy": [
            [list(observation), list(output)]
            for observation, output in success.strategy_items
        ],
    }


def random_differential(
    A: FiniteAlgebra,
    *,
    seed: int = 0xC0A5E,
    relations: int = 96,
) -> dict[str, int]:
    rng = random.Random(seed)
    checked = feasible = infeasible = 0
    states = tuple((value,) for value in Q)
    inputs = tuple((value,) for value in Q)

    for _ in range(relations):
        safe = set()
        for state in states:
            for input_value in inputs:
                mask = rng.randrange(1 << len(states))
                for index, output in enumerate(states):
                    if mask & (1 << index):
                        safe.add((state, input_value, output))
        game = FiniteSafetyGame(A, 1, 1, safe)

        for mask in range(1 << len(states)):
            domain = frozenset(
                state
                for index, state in enumerate(states)
                if mask & (1 << index)
            )
            reference = game.quasi_primal_strategy_for_domain(domain)
            result = quasi_primal_domain_result(game, domain)
            require(
                result.feasible == (reference is not None),
                "component backend disagrees with reference solver",
            )
            if result.feasible:
                require(
                    verify_quasi_primal_domain_result(game, domain, result),
                    "returned strategy did not verify",
                )
                feasible += 1
            else:
                require(result.obstruction is not None, "failure lacks nogood")
                infeasible += 1
            checked += 1

    return {
        "seed": seed,
        "relations": relations,
        "domain_instances": checked,
        "feasible": feasible,
        "infeasible": infeasible,
    }


def principal_differential(A: FiniteAlgebra) -> dict[str, object]:
    witness = build_principal_no_greatest_region_witness(A)
    require(witness is not None, "missing principal Q witness")
    game = witness.game(A)
    rows = []
    for label, domain in (
        ("left", witness.left_domain),
        ("right", witness.right_domain),
        ("union", witness.left_domain | witness.right_domain),
    ):
        reference = game.quasi_primal_strategy_for_domain(domain)
        result = quasi_primal_domain_result(game, domain)
        require(result.feasible == (reference is not None), "principal differential")
        if result.feasible:
            require(
                verify_quasi_primal_domain_result(game, domain, result),
                "principal strategy failed verification",
            )
        else:
            require(result.obstruction is not None, "principal union lacks core")
        rows.append(
            {
                "label": label,
                "domain_size": len(domain),
                "feasible": result.feasible,
                "obstruction_component_size": (
                    len(result.obstruction.observations)
                    if result.obstruction is not None
                    else 0
                ),
            }
        )
    require([row["feasible"] for row in rows] == [True, True, False], "principal pattern")
    return {"rows": rows}


def make_receipt() -> dict[str, object]:
    A = algebra()
    result = {
        "schema": "orbit-synthesis/quasi-primal-component-backend/v1",
        "targeted": targeted_obstruction(A),
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

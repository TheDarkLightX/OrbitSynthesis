#!/usr/bin/env python3
"""Differential gate for native, HiGHS, command, and PySAT optimization."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import (
    ComponentCandidateRule,
    ComponentRuleSet,
    QuasiPrimalDomainModel,
)
from orbitsynthesis.domain_optimization import optimize_weighted_domain
from orbitsynthesis.external_optimization import (
    ExternalOptimizationError,
    parse_maxsat_output,
    solve_weighted_cnf_command,
    solve_weighted_cnf_highs,
    solve_weighted_cnf_pysat_rc2,
)

State = tuple[int, ...]
Observation = tuple[int, ...]
Output = tuple[int, ...]


@dataclass(frozen=True)
class SyntheticPointedClass:
    representative: Observation
    observations: tuple[Observation, ...]


class SyntheticGame:
    def __init__(
        self,
        state_count: int,
        candidates: tuple[tuple[int, frozenset[int]], ...],
    ) -> None:
        self.states = tuple((index,) for index in range(state_count))
        self.observations = self.states
        self.outputs = self.states
        self._forbidden = {
            target: frozenset((source,) for source in forbidden)
            for target, forbidden in candidates
        }

    @staticmethod
    def split_observation(observation: Observation):
        return observation, ()

    def is_safe(self, state: State, _input, output: Output) -> bool:
        return state not in self._forbidden[output[0]]


class SyntheticKernel:
    def __init__(
        self,
        state_count: int,
        candidates: tuple[tuple[int, frozenset[int]], ...],
    ) -> None:
        self.game = SyntheticGame(state_count, candidates)
        representative = self.game.observations[0]
        pointed = SyntheticPointedClass(
            representative=representative,
            observations=self.game.observations,
        )
        self.pointed_classes = (pointed,)
        identity = {index: index for index in range(state_count)}
        self.pointed_transports = {
            representative: {
                observation: identity
                for observation in self.game.observations
            }
        }
        self.seed_vectors = {
            representative: tuple((target,) for target, _forbidden in candidates)
        }


def component_model(
    state_count: int,
    candidates: tuple[tuple[int, frozenset[int]], ...],
) -> QuasiPrimalDomainModel:
    states = tuple((index,) for index in range(state_count))
    observations = states
    rules = []
    for target, forbidden_indices in candidates:
        forbidden = frozenset((index,) for index in forbidden_indices)
        assignment = tuple((observation, (target,)) for observation in observations)
        closure = frozenset(
            (source, (target,))
            for source in states
            if source not in forbidden and source != (target,)
        )
        rules.append(
            ComponentCandidateRule(
                representative_output=(target,),
                assignment_items=assignment,
                forbidden_states=forbidden,
                closure_edges=closure,
            )
        )
    return QuasiPrimalDomainModel(
        states=states,
        observations=observations,
        components=(
            ComponentRuleSet(
                representative=observations[0],
                observations=observations,
                candidates=tuple(rules),
            ),
        ),
    )


FAMILIES = (
    ("split2", 2, ((0, frozenset({1})), (1, frozenset({0})))),
    (
        "choice4",
        4,
        (
            (0, frozenset({2, 3})),
            (1, frozenset({0})),
            (3, frozenset({1, 2})),
        ),
    ),
    (
        "cycle6",
        6,
        (
            (0, frozenset({3, 4, 5})),
            (2, frozenset({0, 5})),
            (4, frozenset({1, 2})),
        ),
    ),
    (
        "pruning9",
        9,
        (
            (0, frozenset({4, 5, 6, 7, 8})),
            (2, frozenset({0, 6, 7})),
            (5, frozenset({1, 2, 8})),
            (8, frozenset({0, 3, 4})),
        ),
    ),
)


def scenarios(state_count: int):
    states = tuple((index,) for index in range(state_count))
    return (
        (
            "unique",
            {state: 1 << index for index, state in enumerate(states)},
            frozenset(),
            frozenset(),
        ),
        (
            "signed",
            {
                state: ((index + 2) if index % 2 == 0 else -(index + 1))
                for index, state in enumerate(states)
            },
            frozenset(),
            frozenset(),
        ),
        (
            "required",
            {state: index + 1 for index, state in enumerate(states)},
            frozenset({states[0]}),
            frozenset(),
        ),
        (
            "forbidden",
            {state: 2 * index + 1 for index, state in enumerate(states)},
            frozenset(),
            frozenset({states[-1]}),
        ),
        (
            "zero",
            {state: 0 for state in states},
            frozenset(),
            frozenset(),
        ),
    )


def objective(mask: int, states: tuple[State, ...], weights: dict[State, int]):
    score = sum(
        weights[state]
        for index, state in enumerate(states)
        if mask & (1 << index)
    )
    return score, mask.bit_count(), mask


def exhaustive_optimum(
    model: QuasiPrimalDomainModel,
    weights: dict[State, int],
    required: frozenset[State],
    forbidden: frozenset[State],
):
    best = None
    for mask in range(1 << len(model.states)):
        domain = frozenset(
            state
            for index, state in enumerate(model.states)
            if mask & (1 << index)
        )
        if not required <= domain or forbidden & domain:
            continue
        if not model.domain_feasible(domain):
            continue
        candidate = objective(mask, model.states, weights)
        if best is None or candidate > best[0]:
            best = candidate, domain
    return best


def checked_domain(result):
    if result.status == "infeasible":
        return None
    if not result.certificate_verified or result.witness is None:
        raise AssertionError("backend returned an unchecked feasible result")
    return result.witness.domain


def run_corpus(require_pysat: bool) -> dict[str, object]:
    reference_process = (
        ROOT
        / "research/tournaments/2026-08-14-external-maxsat-benchmark"
        / "tools/reference_maxsat_solver.py"
    )
    rows = []
    highs_cases = command_cases = pysat_cases = 0
    pysat_available = True

    for family_name, state_count, candidate_data in FAMILIES:
        kernel = SyntheticKernel(state_count, candidate_data)
        model = component_model(state_count, candidate_data)
        for scenario_name, weights, required, forbidden in scenarios(state_count):
            expected = exhaustive_optimum(model, weights, required, forbidden)
            try:
                native = optimize_weighted_domain(
                    kernel,
                    state_weights=weights,
                    required_states=required,
                    forbidden_states=forbidden,
                )
            except ValueError:
                native = None

            if expected is None:
                if native is not None:
                    raise AssertionError("native optimizer found an impossible domain")
            else:
                if native is None:
                    raise AssertionError("native optimizer missed a feasible domain")
                if (
                    native.objective.score,
                    native.objective.cardinality,
                    native.objective.mask,
                ) != expected[0]:
                    raise AssertionError("native optimizer disagrees with exhaustive optimum")
                if native.domain != expected[1]:
                    raise AssertionError("native optimizer returned the wrong domain")

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
            highs = solve_weighted_cnf_highs(
                model,
                cnf,
                wcnf,
                state_weights=weights,
                default_weight=0,
            )
            highs_cases += 1
            highs_domain = checked_domain(highs)
            if expected is None:
                if highs_domain is not None:
                    raise AssertionError("HiGHS found an impossible domain")
            elif highs.signed_utility != expected[0][0]:
                raise AssertionError("HiGHS returned a non-optimal signed utility")

            command_domain = None
            if wcnf.variable_count <= 18:
                command = solve_weighted_cnf_command(
                    model,
                    cnf,
                    wcnf,
                    [sys.executable, str(reference_process), "{wcnf}"],
                    state_weights=weights,
                    default_weight=0,
                )
                command_cases += 1
                command_domain = checked_domain(command)
                if expected is None:
                    if command_domain is not None:
                        raise AssertionError("command backend found an impossible domain")
                elif command.signed_utility != expected[0][0]:
                    raise AssertionError("command backend returned non-optimal utility")

            pysat_domain = None
            if pysat_available:
                try:
                    pysat = solve_weighted_cnf_pysat_rc2(
                        model,
                        cnf,
                        wcnf,
                        state_weights=weights,
                        default_weight=0,
                    )
                except ExternalOptimizationError as error:
                    if "python-sat is required" not in str(error):
                        raise
                    pysat_available = False
                    if require_pysat:
                        raise
                else:
                    pysat_cases += 1
                    pysat_domain = checked_domain(pysat)
                    if expected is None:
                        if pysat_domain is not None:
                            raise AssertionError("PySAT found an impossible domain")
                    elif pysat.signed_utility != expected[0][0]:
                        raise AssertionError("PySAT returned non-optimal utility")

            if scenario_name == "unique" and expected is not None:
                if highs_domain != expected[1]:
                    raise AssertionError("HiGHS unique optimum domain mismatch")
                if command_domain is not None and command_domain != expected[1]:
                    raise AssertionError("command unique optimum domain mismatch")
                if pysat_domain is not None and pysat_domain != expected[1]:
                    raise AssertionError("PySAT unique optimum domain mismatch")

            rows.append(
                (
                    family_name,
                    scenario_name,
                    None if expected is None else expected[0],
                    None if expected is None else tuple(sorted(expected[1])),
                    highs.status,
                    tuple(sorted(highs_domain)) if highs_domain is not None else None,
                    tuple(sorted(command_domain)) if command_domain is not None else None,
                    tuple(sorted(pysat_domain)) if pysat_domain is not None else None,
                )
            )

    semantic = hashlib.sha256(repr(tuple(rows)).encode()).hexdigest()
    return {
        "families": len(FAMILIES),
        "scenarios": sum(
            len(scenarios(state_count))
            for _name, state_count, _data in FAMILIES
        ),
        "highs_cases": highs_cases,
        "command_cases": command_cases,
        "pysat_cases": pysat_cases,
        "pysat_available": pysat_available,
        "semantic_sha256": semantic,
        "rows": rows,
    }


def mutation_audit() -> dict[str, object]:
    state_count = 2
    candidate_data = FAMILIES[0][2]
    model = component_model(state_count, candidate_data)
    weights = {(0,): 5, (1,): 3}
    cnf = model.cnf()
    wcnf = model.weighted_cnf(state_weights=weights, default_weight=0)
    reference_process = (
        ROOT
        / "research/tournaments/2026-08-14-external-maxsat-benchmark"
        / "tools/reference_maxsat_solver.py"
    )
    correct = solve_weighted_cnf_command(
        model,
        cnf,
        wcnf,
        [sys.executable, str(reference_process), "{wcnf}"],
        state_weights=weights,
        default_weight=0,
    )
    model_text = " ".join(map(str, correct.model_literals))
    rejected = []
    cases = (
        (
            "wrong_cost",
            f"print('o 999\\ns OPTIMUM FOUND\\nv {model_text} 0')",
        ),
        (
            "non_optimal_status",
            f"print('o {correct.unsatisfied_cost}\\ns SATISFIABLE\\nv {model_text} 0')",
        ),
        ("missing_model", "print('o 0\\ns OPTIMUM FOUND')"),
    )
    for label, code in cases:
        try:
            solve_weighted_cnf_command(
                model,
                cnf,
                wcnf,
                [sys.executable, "-c", code, "{wcnf}"],
                state_weights=weights,
                default_weight=0,
            )
        except ExternalOptimizationError:
            rejected.append(label)
        else:
            raise AssertionError(f"mutation was accepted: {label}")

    try:
        solve_weighted_cnf_command(
            model,
            cnf,
            wcnf,
            [
                sys.executable,
                "-c",
                "import time; time.sleep(1)",
                "{wcnf}",
            ],
            timeout=0.01,
            state_weights=weights,
            default_weight=0,
        )
    except ExternalOptimizationError:
        rejected.append("timeout")
    else:
        raise AssertionError("timeout mutation was accepted")

    too_large = model.weighted_cnf(
        state_weights={(0,): 1 << 53, (1,): 0},
        default_weight=0,
    )
    try:
        solve_weighted_cnf_highs(
            model,
            model.cnf(),
            too_large,
            state_weights={(0,): 1 << 53, (1,): 0},
            default_weight=0,
        )
    except ExternalOptimizationError:
        rejected.append("highs_precision_guard")
    else:
        raise AssertionError("HiGHS precision guard did not fire")

    parsed = parse_maxsat_output(
        "c test\no 3\ns OPTIMUM FOUND\nv 1 -2 3 -4 0\n"
    )
    if parsed.status != "optimal" or parsed.reported_cost != 3:
        raise AssertionError("MaxSAT output parser drift")
    return {
        "rejected": rejected,
        "parsed_status": parsed.status,
        "parsed_cost": parsed.reported_cost,
        "parsed_literals": parsed.model_literals,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-pysat", action="store_true")
    args = parser.parse_args()
    result = {
        "schema": "orbit-synthesis/external-optimization-gate/v1",
        "corpus": run_corpus(args.require_pysat),
        "mutations": mutation_audit(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

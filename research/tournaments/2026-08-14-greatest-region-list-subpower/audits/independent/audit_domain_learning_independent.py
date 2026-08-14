#!/usr/bin/env python3
"""No-import reconstruction of state-literal conflict learning."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import json
import random


@dataclass(frozen=True)
class Literal:
    variable: int
    included: bool

    def holds(self, assignment: frozenset[int]) -> bool:
        return (self.variable in assignment) == self.included


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def literal_key(literal: Literal) -> tuple[int, int]:
    return literal.variable, 0 if literal.included else 1


def condition_key(condition: frozenset[Literal]):
    return len(condition), tuple(sorted(map(literal_key, condition)))


def covers_every_candidate(conditions, literals) -> bool:
    return all(
        any(condition <= literals for condition in candidate_conditions)
        for candidate_conditions in conditions.values()
    )


def minimize(conditions) -> frozenset[Literal]:
    core = frozenset(
        literal
        for candidate_conditions in conditions.values()
        for literal in sorted(candidate_conditions, key=condition_key)[0]
    )
    require(covers_every_candidate(conditions, core), "initial coverage")
    for literal in sorted(core, key=literal_key, reverse=True):
        reduced = core - {literal}
        if covers_every_candidate(conditions, reduced):
            core = reduced
    require(covers_every_candidate(conditions, core), "final coverage")
    require(
        all(
            not covers_every_candidate(conditions, core - {literal})
            for literal in core
        ),
        "subset minimality",
    )
    return core


def exhaustive_minimizer() -> dict[str, int]:
    # Every condition is compatible with the same failing assignment: variables
    # 0,1 are included and variables 2,3 are excluded.
    universe = (
        Literal(0, True),
        Literal(1, True),
        Literal(2, False),
        Literal(3, False),
    )
    conditions = tuple(
        frozenset(items)
        for size in (1, 2)
        for items in itertools.combinations(universe, size)
    )
    families = tuple(
        tuple(items)
        for size in (1, 2, 3)
        for items in itertools.combinations(conditions, size)
    )

    checked = assignments_checked = 0
    for left in families:
        for right in families:
            instance = {0: left, 1: right}
            core = minimize(instance)
            for mask in range(1 << 4):
                assignment = frozenset(
                    variable
                    for variable in range(4)
                    if mask & (1 << variable)
                )
                if not all(literal.holds(assignment) for literal in core):
                    continue
                require(
                    covers_every_candidate(
                        instance,
                        frozenset(
                            literal
                            for literal in universe
                            if literal.holds(assignment)
                        ),
                    ),
                    "core-matching assignment escaped a candidate conflict",
                )
                assignments_checked += 1
            checked += 1

    require(checked == 30625, "exhaustive family census")
    return {
        "two_candidate_condition_families": checked,
        "core_matching_assignments": assignments_checked,
    }


def randomized_multicandidate(
    *,
    seed: int = 0xC0A11C7,
    instances: int = 2000,
) -> dict[str, int]:
    rng = random.Random(seed)
    universe = tuple(
        Literal(variable, variable % 2 == 0)
        for variable in range(8)
    )
    all_conditions = tuple(
        frozenset(items)
        for size in (1, 2)
        for items in itertools.combinations(universe, size)
    )
    literal_total = 0
    for _ in range(instances):
        candidate_count = rng.randrange(3, 8)
        conditions = {}
        for candidate in range(candidate_count):
            selected = rng.sample(
                all_conditions,
                rng.randrange(1, min(7, len(all_conditions)) + 1),
            )
            conditions[candidate] = tuple(selected)
        core = minimize(conditions)
        literal_total += len(core)
    return {
        "seed": seed,
        "instances": instances,
        "total_core_literals": literal_total,
    }


def lazy_search_synthetic() -> dict[str, int]:
    # Variable 0 has very high reward but is structurally forbidden.  One
    # learned literal excludes all 2^11 assignments containing it, so the
    # second component check returns the exact optimum.
    weights = {0: 100, **{variable: 1 for variable in range(1, 12)}}
    cores: list[frozenset[Literal]] = []
    checks = rounds = 0

    while True:
        rounds += 1
        best = None
        best_weight = None
        for mask in range(1 << 12):
            assignment = frozenset(
                variable
                for variable in range(12)
                if mask & (1 << variable)
            )
            if any(
                all(literal.holds(assignment) for literal in core)
                for core in cores
            ):
                continue
            total = sum(weights[variable] for variable in assignment)
            if best is None or total > best_weight:
                best = assignment
                best_weight = total
            elif total == best_weight and repr(sorted(assignment)) < repr(sorted(best)):
                best = assignment
        require(best is not None, "synthetic candidate")
        checks += 1
        if 0 not in best:
            require(best_weight == 11, "synthetic optimum")
            break
        conditions = {0: (frozenset((Literal(0, True),)),)}
        core = minimize(conditions)
        require(core not in cores, "duplicate core")
        cores.append(core)

    require(checks == 2, "synthetic model checks")
    require(rounds == 2, "synthetic rounds")
    return {
        "state_assignments": 1 << 12,
        "component_checks": checks,
        "learned_cores": len(cores),
        "optimum_weight": best_weight,
    }


def make_receipt() -> dict[str, object]:
    result = {
        "schema": "orbit-synthesis/domain-learning-independent/v1",
        "exhaustive_minimizer": exhaustive_minimizer(),
        "randomized_multicandidate": randomized_multicandidate(),
        "lazy_synthetic": lazy_search_synthetic(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    print(json.dumps(make_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

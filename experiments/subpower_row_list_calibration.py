#!/usr/bin/env python3
"""Finite calibration for SUBPOWER_ROW_LIST_SYNTHESIS.md.

Algebra: two-element meet-semilattice A=({0,1}; meet), no constants.

For a constrained observation set Z, the generated subpower P_Z is the
closure under coordinatewise meet of the observation-coordinate columns.
The note proves that fixed-domain term safety is equivalent to selecting
output-coordinate vectors from P_Z whose transposed rows lie in the local
allowed lists.

This script:
1. exhausts every k=1,m=1 candidate-domain/list instance (265 total);
2. runs 1,000 deterministic randomized k=2,m=1 instances;
3. compares subpower-row-list feasibility with brute term-controller search.
"""

from __future__ import annotations

from itertools import product
import random

A = (0, 1)


def meet_vec(x: tuple[int, ...], y: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a & b for a, b in zip(x, y))


def generated_subpower(columns: list[tuple[int, ...]]) -> frozenset[tuple[int, ...]]:
    values = set(columns)
    changed = True
    while changed:
        changed = False
        snapshot = tuple(values)
        for x in snapshot:
            for y in snapshot:
                z = meet_vec(x, y)
                if z not in values:
                    values.add(z)
                    changed = True
    return frozenset(values)


def meet_term(mask: int, observation: tuple[int, ...]) -> int:
    """Evaluate conjunction of the nonempty variable subset selected by mask."""
    result = 1
    for index, value in enumerate(observation):
        if mask & (1 << index):
            result &= value
    return result


def subpower_feasible(
    observations: tuple[tuple[int, ...], ...],
    output_arity: int,
    allowed: dict[tuple[int, ...], frozenset[tuple[int, ...]]],
) -> bool:
    if not observations:
        return True

    observation_arity = len(observations[0])
    columns = [
        tuple(observation[index] for observation in observations)
        for index in range(observation_arity)
    ]
    subpower = generated_subpower(columns)

    for output_columns in product(subpower, repeat=output_arity):
        good = True
        for row_index, observation in enumerate(observations):
            row = tuple(column[row_index] for column in output_columns)
            if row not in allowed[observation]:
                good = False
                break
        if good:
            return True
    return False


def brute_term_feasible(
    observations: tuple[tuple[int, ...], ...],
    output_arity: int,
    allowed: dict[tuple[int, ...], frozenset[tuple[int, ...]]],
) -> bool:
    if not observations:
        return True

    observation_arity = len(observations[0])
    term_masks = tuple(range(1, 1 << observation_arity))

    for coordinate_terms in product(term_masks, repeat=output_arity):
        if all(
            tuple(meet_term(mask, observation) for mask in coordinate_terms)
            in allowed[observation]
            for observation in observations
        ):
            return True
    return False


def exhaustive_k1() -> int:
    checked = 0
    states = A
    outputs = tuple((a,) for a in A)

    for domain_mask in range(1 << len(states)):
        W = tuple(a for a in states if domain_mask & (1 << a))
        observations = tuple((state, inp) for state in W for inp in A)

        list_options = []
        seen = set()
        for mask in range(1 << len(outputs)):
            option = frozenset(
                output
                for index, output in enumerate(outputs)
                if mask & (1 << index) and output[0] in W
            )
            if option not in seen:
                seen.add(option)
                list_options.append(option)

        for choices in product(range(len(list_options)), repeat=len(observations)):
            allowed = {
                observation: list_options[index]
                for observation, index in zip(observations, choices)
            }
            left = subpower_feasible(observations, 1, allowed)
            right = brute_term_feasible(observations, 1, allowed)
            assert left == right, (W, allowed, left, right)
            checked += 1

    assert checked == 265
    return checked


def randomized_k2(seed: int = 0, trials: int = 1000) -> int:
    rng = random.Random(seed)
    states = tuple(product(A, repeat=2))

    for trial in range(trials):
        W = tuple(state for state in states if rng.random() < 0.6)
        observations = tuple(state + (inp,) for state in W for inp in A)

        allowed: dict[tuple[int, ...], frozenset[tuple[int, ...]]] = {}
        for observation in observations:
            allowed[observation] = frozenset(
                output for output in W if rng.random() < 0.5
            )

        left = subpower_feasible(observations, 2, allowed)
        right = brute_term_feasible(observations, 2, allowed)
        assert left == right, (trial, W, allowed, left, right)

    return trials


def main() -> None:
    exact = exhaustive_k1()
    random_trials = randomized_k2()
    print("PASS: subpower row-list calibration")
    print(f"exact k=1,m=1 instances: {exact}")
    print(f"deterministic randomized k=2,m=1 instances: {random_trials}")


if __name__ == "__main__":
    main()

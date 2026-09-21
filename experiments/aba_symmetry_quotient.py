#!/usr/bin/env python3
"""Differential checks for the S_d histogram quotient of the ABA cell game.

For small d we compare:

1. the full concrete cell arena with 2^d / 2^(2d) / 2^(3d) cells;
2. the diagonal-coordinate S_d quotient with histogram nodes
       d+1, C(d+3,3), C(d+7,7).

Random Step/Safe masks are generated as unions of full symmetry orbits.
We compare both the zero safety fixed point and invariant positive predecessor
queries exactly.
"""

from __future__ import annotations

import random


def weak_compositions(total: int, parts: int, prefix: tuple[int, ...] = ()):
    if parts == 1:
        yield prefix + (total,)
        return
    for x in range(total + 1):
        yield from weak_compositions(total - x, parts - 1, prefix + (x,))


def pair_histogram(partial: int, d: int) -> tuple[int, ...]:
    hist = [0] * 4
    for j in range(d):
        s = (partial >> j) & 1
        i = (partial >> (d + j)) & 1
        hist[(s << 1) | i] += 1
    return tuple(hist)


def triple_histogram(full: int, d: int) -> tuple[int, ...]:
    hist = [0] * 8
    for j in range(d):
        s = (full >> j) & 1
        i = (full >> (d + j)) & 1
        y = (full >> (2 * d + j)) & 1
        hist[(s << 2) | (i << 1) | y] += 1
    return tuple(hist)


def partial_state_weight(hist: tuple[int, ...]) -> int:
    return sum(((idx >> 1) & 1) * count for idx, count in enumerate(hist))


def full_histogram_marginals(
    hist: tuple[int, ...],
) -> tuple[tuple[int, ...], int, int]:
    partial = [0] * 4
    state_weight = 0
    next_weight = 0
    for idx, count in enumerate(hist):
        s = (idx >> 2) & 1
        i = (idx >> 1) & 1
        y = idx & 1
        partial[(s << 1) | i] += count
        state_weight += s * count
        next_weight += y * count
    return tuple(partial), state_weight, next_weight


def full_zero_fixed_point(
    d: int,
    forbidden_full_orbits: set[tuple[int, ...]],
    forbidden_state_weights: set[int],
) -> set[int]:
    target = set(range(1 << d))
    while True:
        nxt: set[int] = set()
        for state in range(1 << d):
            if state.bit_count() in forbidden_state_weights:
                continue
            good = True
            for inp in range(1 << d):
                exists_response = False
                for out in range(1 << d):
                    full = state | (inp << d) | (out << (2 * d))
                    if triple_histogram(full, d) in forbidden_full_orbits:
                        continue
                    if out in target:
                        exists_response = True
                        break
                if not exists_response:
                    good = False
                    break
            if good:
                nxt.add(state)
        if nxt == target:
            return target
        target = nxt


def quotient_transition_index(
    d: int, forbidden_full_orbits: set[tuple[int, ...]]
) -> dict[tuple[int, ...], set[int]]:
    by_partial: dict[tuple[int, ...], set[int]] = {}
    for full_hist in weak_compositions(d, 8):
        if full_hist in forbidden_full_orbits:
            continue
        partial, _, next_weight = full_histogram_marginals(full_hist)
        by_partial.setdefault(partial, set()).add(next_weight)
    return by_partial


def quotient_zero_fixed_point(
    d: int,
    forbidden_full_orbits: set[tuple[int, ...]],
    forbidden_state_weights: set[int],
) -> set[int]:
    partial_orbits = list(weak_compositions(d, 4))
    by_partial = quotient_transition_index(d, forbidden_full_orbits)

    target = set(range(d + 1))
    while True:
        nxt: set[int] = set()
        for weight in range(d + 1):
            if weight in forbidden_state_weights:
                continue
            good = True
            for partial in partial_orbits:
                if partial_state_weight(partial) != weight:
                    continue
                if not (by_partial.get(partial, set()) & target):
                    good = False
                    break
            if good:
                nxt.add(weight)
        if nxt == target:
            return target
        target = nxt


def full_predecessor(
    d: int,
    forbidden_full_orbits: set[tuple[int, ...]],
    target_weights: set[int],
    zero_safe_weights: set[int],
) -> set[int]:
    result: set[int] = set()
    for state in range(1 << d):
        if state.bit_count() not in zero_safe_weights:
            continue
        good = True
        for inp in range(1 << d):
            exists_response = False
            for out in range(1 << d):
                full = state | (inp << d) | (out << (2 * d))
                if triple_histogram(full, d) in forbidden_full_orbits:
                    continue
                if out.bit_count() not in zero_safe_weights:
                    continue
                if out.bit_count() in target_weights:
                    exists_response = True
                    break
            if not exists_response:
                good = False
                break
        if good:
            result.add(state)
    return result


def quotient_predecessor(
    d: int,
    forbidden_full_orbits: set[tuple[int, ...]],
    target_weights: set[int],
    zero_safe_weights: set[int],
) -> set[int]:
    partial_orbits = list(weak_compositions(d, 4))

    by_partial: dict[tuple[int, ...], set[int]] = {}
    for full_hist in weak_compositions(d, 8):
        if full_hist in forbidden_full_orbits:
            continue
        partial, _, next_weight = full_histogram_marginals(full_hist)
        if next_weight not in zero_safe_weights:
            continue
        by_partial.setdefault(partial, set()).add(next_weight)

    result: set[int] = set()
    for weight in zero_safe_weights:
        good = True
        for partial in partial_orbits:
            if partial_state_weight(partial) != weight:
                continue
            if not (by_partial.get(partial, set()) & target_weights):
                good = False
                break
        if good:
            result.add(weight)
    return result


def self_test(seed: int = 123) -> None:
    rng = random.Random(seed)

    suites = [(1, 100), (2, 200), (3, 150), (4, 60)]
    for d, trials in suites:
        full_orbits = list(weak_compositions(d, 8))

        assert len(list(weak_compositions(d, 4))) == (d + 3) * (d + 2) * (d + 1) // 6
        assert len(full_orbits) == (
            (d + 7) * (d + 6) * (d + 5) * (d + 4)
            * (d + 3) * (d + 2) * (d + 1) // 5040
        )

        for _ in range(trials):
            forbidden_full = {
                hist for hist in full_orbits if rng.random() < 0.25
            }
            forbidden_state = {
                w for w in range(d + 1) if rng.random() < 0.15
            }

            quotient_safe = quotient_zero_fixed_point(
                d, forbidden_full, forbidden_state
            )
            concrete_safe = full_zero_fixed_point(
                d, forbidden_full, forbidden_state
            )

            assert all(
                (state in concrete_safe)
                == (state.bit_count() in quotient_safe)
                for state in range(1 << d)
            )

            target = {
                w for w in quotient_safe if rng.random() < 0.5
            }
            quotient_pre = quotient_predecessor(
                d, forbidden_full, target, quotient_safe
            )
            concrete_pre = full_predecessor(
                d, forbidden_full, target, quotient_safe
            )

            assert all(
                (state in concrete_pre)
                == (state.bit_count() in quotient_pre)
                for state in range(1 << d)
            )


def main() -> None:
    self_test()
    print("ABA S_d symmetry quotient checks passed")
    print("  full concrete arena == histogram quotient for d=1..4")
    print("  zero safety fixed points compared")
    print("  invariant positive predecessor masks compared")


if __name__ == "__main__":
    main()

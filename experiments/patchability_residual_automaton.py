#!/usr/bin/env python3
"""Exhaustive bounded oracle for the patchability residual automaton."""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.patchability_residual import (  # noqa: E402
    build_patchability_residual_automaton,
    distinguishing_extension,
    shortest_accepting_parameters,
)


def all_clutters(n: int):
    edges = tuple(range(1, 1 << n))
    for code in range(1 << len(edges)):
        family = tuple(edges[i] for i in range(len(edges)) if code & (1 << i))
        if all(not ((a & b) == a or (a & b) == b) for a, b in combinations(family, 2)):
            yield family


def check_clutter(n: int, family: tuple[int, ...]) -> tuple[int, int, int]:
    carrier = tuple(range(n))
    edges = tuple(frozenset(i for i in carrier if edge & (1 << i)) for edge in family)
    machine = build_patchability_residual_automaton(carrier, edges)
    residual_to_future = {}
    future_to_residual = {}
    future_checks = 0

    for chosen in range(1 << n):
        residual = tuple(edge for edge in family if not (chosen & edge))
        future = tuple(
            all((chosen | extension) & edge for edge in family)
            for extension in range(1 << n)
        )
        future_checks += len(future)
        assert residual_to_future.setdefault(residual, future) == future
        assert future_to_residual.setdefault(future, residual) == residual

        parameters = tuple(i for i in carrier if chosen & (1 << i))
        state = machine.run(parameters)
        expected = sum(
            1 << index
            for index, edge in enumerate(machine.edges)
            if not any(chosen & (1 << value) for value in edge)
        )
        assert state == expected
        assert machine.accepts(parameters) == all(chosen & edge for edge in family)
        for value in carrier:
            assert machine.transition(state, value) == machine.run((value,), start=state)

    assert len(residual_to_future) == len(machine.states)

    distinguishers = 0
    for left, right in combinations(machine.states, 2):
        _, left_answer, right_answer = distinguishing_extension(machine, left, right)
        assert left_answer != right_answer
        distinguishers += 1

    masks = {
        value: sum(1 << i for i, edge in enumerate(edges) if value in edge)
        for value in carrier
    }
    for left in carrier:
        for right in carrier:
            same = all(
                machine.transition(state, left) == machine.transition(state, right)
                for state in machine.states
            )
            assert same == (masks[left] == masks[right])

    unions = {0}
    for mask in masks.values():
        unions |= {old | mask for old in tuple(unions)}
    assert len(unions) == len(machine.states)

    shortest = shortest_accepting_parameters(machine)
    assert machine.accepts(shortest)
    assert all(
        not machine.accepts(shortest[:i] + shortest[i + 1 :])
        for i in range(len(shortest))
    )
    return len(machine.states), distinguishers, future_checks


def check_nonclutter() -> None:
    raw = (frozenset((0,)), frozenset((0, 1)))
    machine = build_patchability_residual_automaton((0, 1), raw)
    assert machine.edges == (frozenset((0,)),)
    extensions = ((), (0,), (1,), (0, 1))
    empty_answers = tuple(all(set(ext) & edge for edge in raw) for ext in extensions)
    one_answers = tuple(all((set((1,)) | set(ext)) & edge for edge in raw) for ext in extensions)
    assert empty_answers == one_answers


def check_witnesses() -> tuple[int, int, int, int]:
    carrier = tuple(range(6))
    star = build_patchability_residual_automaton(
        carrier,
        ((3, 4, 5), (0, 1, 2, 5), (0, 1, 2, 3, 4)),
    )
    chain = build_patchability_residual_automaton(
        carrier,
        ((0, 1, 2), (0, 3, 4, 5), (1, 2, 3, 4, 5)),
    )
    assert star.parameter_classes == ((0, 1, 2), (3, 4), (5,))
    assert chain.parameter_classes == ((0,), (1, 2), (3, 4, 5))
    assert len(star.states) == len(chain.states) == 5
    assert len(shortest_accepting_parameters(star)) == 2
    assert len(shortest_accepting_parameters(chain)) == 2
    return 3, 5, 3, 5


def main() -> None:
    expected = {1: 2, 2: 5, 3: 19, 4: 167}
    clutter_count = state_count = distinguisher_count = future_count = 0
    for n in range(1, 5):
        local = 0
        for family in all_clutters(n):
            states, distinguishers, futures = check_clutter(n, family)
            local += 1
            clutter_count += 1
            state_count += states
            distinguisher_count += distinguishers
            future_count += futures
        assert local == expected[n]

    check_nonclutter()
    star_roles, star_states, chain_roles, chain_states = check_witnesses()
    print("PASS patchability residual automaton")
    print("clutters exhausted for n=1..4:", clutter_count)
    print("reachable residual states checked:", state_count)
    print("constructive state distinguishers checked:", distinguisher_count)
    print("future-extension answers checked:", future_count)
    print("redundant non-clutter false-split fixture: rejected")
    print("six-element star role classes / minimal states:", star_roles, star_states)
    print("six-element rigid-chain role classes / minimal states:", chain_roles, chain_states)


if __name__ == "__main__":
    main()

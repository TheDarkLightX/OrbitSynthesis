#!/usr/bin/env python3
"""Calibration of QUASIPRIMAL_ORBIT_SELECTOR_EQUATIONS.md.

Use the higher-arity non-demi reactive template over the three-element
Quackenbush quasi-primal algebra. Build the orbitwise conservative operation g
such that the safety relation is exactly the single equation

    first_state_coordinate = g(transition_tuple).

The concrete algebra has only one nontrivial proper internal isomorphism: phi
swaps 0 and 1 on B={0,1}; Aut(Q) is trivial.
"""

from __future__ import annotations

from itertools import product

Q = (0, 1, 2)
B = (0, 1)


def phi(x: int) -> int:
    if x not in B:
        raise ValueError("phi only acts on B")
    return 1 - x


def map_phi(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(phi(value) for value in values)


A_ENUM = (0, 1)
B_ENUM = map_phi(A_ENUM)
CODES = ((0, 0), (0, 1), (1, 0))
A0, A1, A2 = tuple(A_ENUM + code for code in CODES)
B0, B1, B2 = tuple(B_ENUM + map_phi(code) for code in CODES)

SPECIAL_INPUT = (0, 1, 0)
SPECIAL_INPUT_IMAGE = map_phi(SPECIAL_INPUT)
FULL_INPUT = Q

Z_A = A0 + SPECIAL_INPUT
Z_B = B0 + SPECIAL_INPUT_IMAGE

TRANSITION_ARITY = 11  # state 4 + input 3 + output 4
P_COORD = 0


def safety(transition: tuple[int, ...]) -> bool:
    state = transition[:4]
    inp = transition[4:7]
    out = transition[7:]
    observation = state + inp

    if (state == A2 and inp == FULL_INPUT) or (state == B1 and inp == FULL_INPUT):
        return False

    if observation == Z_A:
        return out in {A1, A2}
    if observation == Z_B:
        return out in {B1, B2}
    return True


def orbit_key(transition: tuple[int, ...]) -> tuple[int, ...]:
    """Canonical key for the concrete internal-isomorphism orbit."""
    if all(value in B for value in transition):
        paired = map_phi(transition)
        return min(transition, paired)
    return transition


def build_forbidden_orbit_selectors() -> dict[tuple[int, ...], int]:
    selector: dict[tuple[int, ...], int] = {}

    for transition in product(Q, repeat=TRANSITION_ARITY):
        if safety(transition):
            continue
        key = orbit_key(transition)
        if key in selector:
            continue

        # The theorem's separating-coordinate hypothesis.
        index = next(
            index
            for index in range(1, TRANSITION_ARITY)
            if key[index] != key[P_COORD]
        )
        selector[key] = index

    return selector


def selector_term_function(
    transition: tuple[int, ...],
    selectors: dict[tuple[int, ...], int],
) -> int:
    if safety(transition):
        return transition[P_COORD]
    return transition[selectors[orbit_key(transition)]]


def main() -> None:
    selectors = build_forbidden_orbit_selectors()

    forbidden = 0
    total = 0
    for transition in product(Q, repeat=TRANSITION_ARITY):
        total += 1
        is_safe = safety(transition)
        if not is_safe:
            forbidden += 1
        g_value = selector_term_function(transition, selectors)
        assert is_safe == (transition[P_COORD] == g_value), transition

    # In this concrete Q, preserving B and commuting with phi is the only
    # nontrivial quasi-primal term-table constraint.
    equivariance = 0
    for transition in product(B, repeat=TRANSITION_ARITY):
        paired = map_phi(transition)
        left = selector_term_function(paired, selectors)
        right = phi(selector_term_function(transition, selectors))
        assert left == right, transition
        equivariance += 1

    assert total == 3 ** TRANSITION_ARITY
    assert forbidden == 320
    assert len(selectors) == 306
    assert equivariance == 2 ** TRANSITION_ARITY

    print("PASS: orbit-selector equation calibration")
    print(f"transition tuples checked: {total}")
    print(f"forbidden tuples: {forbidden}")
    print(f"forbidden groupoid orbits/selectors: {len(selectors)}")
    print(f"binary phi-equivariance checks: {equivariance}")
    print("safe(x) iff first_state_coordinate == g(x) on all transitions")


if __name__ == "__main__":
    main()

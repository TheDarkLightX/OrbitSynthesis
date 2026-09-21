#!/usr/bin/env python3
"""Calibration of QUASIPRIMAL_DEMI_RELATIONAL_CHARACTERIZATION.md.

Instantiate the general nonextendable-internal-isomorphism construction on
Quackenbush's three-element quasi-primal algebra

    Q=({0,1,2}; discriminator, u),
    u(0)=1, u(1)=0, u(2)=1.

The proper nontrivial subalgebra B={0,1} has phi swapping 0 and 1;
Aut(Q) is trivial.

The general template uses state arity 4 and input arity 3. This script verifies
internal-isomorphism invariance on every all-B transition tuple and explicitly
checks the two winning term-controller tables.
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

W1 = frozenset({A0, A1})
W2 = frozenset({B0, B2})

STATES = tuple(product(Q, repeat=4))
INPUTS = tuple(product(Q, repeat=3))


def safe(state: tuple[int, ...], inp: tuple[int, ...], out: tuple[int, ...]) -> bool:
    observation = state + inp

    # Aut(Q) is trivial in this concrete calibration, so these are the full
    # global-automorphism dead observation orbits.
    if (state == A2 and inp == FULL_INPUT) or (state == B1 and inp == FULL_INPUT):
        return False

    if observation == Z_A:
        return out in {A1, A2}
    if observation == Z_B:
        return out in {B1, B2}
    return True


def sigma1(state: tuple[int, ...], inp: tuple[int, ...]) -> tuple[int, ...]:
    observation = state + inp
    if observation == Z_A:
        return A1
    if observation == Z_B:
        return B1
    return state


def sigma2(state: tuple[int, ...], inp: tuple[int, ...]) -> tuple[int, ...]:
    observation = state + inp
    if observation == Z_A:
        return A2
    if observation == Z_B:
        return B2
    return state


def check_relation_invariance() -> int:
    checked = 0
    for state in product(B, repeat=4):
        for inp in product(B, repeat=3):
            for out in product(B, repeat=4):
                left = safe(state, inp, out)
                right = safe(map_phi(state), map_phi(inp), map_phi(out))
                assert left == right, (state, inp, out, left, right)
                checked += 1
    assert checked == 2 ** 11
    return checked


def check_controller_term_constraints(controller) -> int:
    checked = 0
    for observation in product(B, repeat=7):
        state = observation[:4]
        inp = observation[4:]
        out = controller(state, inp)
        paired = controller(map_phi(state), map_phi(inp))
        assert all(value in B for value in out)
        assert paired == map_phi(out)
        checked += 1
    return checked


def check_winning(domain, controller) -> int:
    checked = 0
    for state in domain:
        for inp in INPUTS:
            out = controller(state, inp)
            assert out in domain, (state, inp, out, domain)
            assert safe(state, inp, out), (state, inp, out)
            checked += 1
    return checked


def check_no_common_superset_logic() -> None:
    # Any common winning domain contains A0 and B0, so both special
    # observations are active. The only safe source outputs are A1,A2.
    # A Q-term table must transport them to B1,B2 respectively.
    assert safe(A0, SPECIAL_INPUT, A1)
    assert safe(A0, SPECIAL_INPUT, A2)
    assert not safe(A0, SPECIAL_INPUT, B0)
    assert map_phi(A1) == B1
    assert map_phi(A2) == B2

    # Choosing A1 forces inclusion of B1 at the paired active observation;
    # choosing A2 forces inclusion of A2 already at the source. Both are dead.
    assert not any(safe(B1, FULL_INPUT, out) for out in STATES)
    assert not any(safe(A2, FULL_INPUT, out) for out in STATES)


def main() -> None:
    assert map_phi(A0) == B0
    assert map_phi(A1) == B1
    assert map_phi(A2) == B2
    assert map_phi(SPECIAL_INPUT) == SPECIAL_INPUT_IMAGE

    relation_checks = check_relation_invariance()
    controller1_checks = check_controller_term_constraints(sigma1)
    controller2_checks = check_controller_term_constraints(sigma2)
    winning1 = check_winning(W1, sigma1)
    winning2 = check_winning(W2, sigma2)
    check_no_common_superset_logic()

    print("PASS: general non-demi relation-template calibration")
    print(f"all-B transition invariance checks: {relation_checks}")
    print(f"sigma1 all-B equivariance checks: {controller1_checks}")
    print(f"sigma2 all-B equivariance checks: {controller2_checks}")
    print(f"W1 required observations checked: {winning1}")
    print(f"W2 required observations checked: {winning2}")
    print("common-superset obstruction verified symbolically")


if __name__ == "__main__":
    main()

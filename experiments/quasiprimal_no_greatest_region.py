#!/usr/bin/env python3
"""Exact finite witness: quasi-primal term-winning domains need not have a greatest element.

The algebra is Quackenbush's three-element quasi-primal example
Q = ({0,1,2}; d, u), where d is the discriminator and
u(0)=1, u(1)=0, u(2)=1.

We use only the classical term-function characterization:
a total operation is a Q-term iff it preserves every internal isomorphism.
For this Q, the only proper nonempty subalgebra is Q0={0,1}; its
nontrivial internal automorphism phi swaps 0 and 1; Aut(Q) is trivial.

The safety relation is a single equation p=g. We explicitly tabulate g,
check that it preserves Q0 and phi, and hence (by quasi-primality) is a term.
"""

from __future__ import annotations

from itertools import combinations, permutations, product

Q = (0, 1, 2)
Q0 = (0, 1)
STATES = tuple(product(Q, repeat=2))
INPUTS = Q
BINARY_OBS = tuple(product(Q0, repeat=3))
BINARY_STATES = tuple(product(Q0, repeat=2))

W1 = frozenset({(0, 0), (0, 1)})
W2 = frozenset({(1, 1), (0, 1)})
UNION = W1 | W2
DEAD_STATE = (1, 0)
SPECIAL_OBS = {(0, 0, 0), (1, 1, 1)}


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def unary_u(x: int) -> int:
    return {0: 1, 1: 0, 2: 1}[x]


def phi_value(x: int) -> int:
    assert x in Q0
    return 1 - x


def phi_tuple(xs: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(phi_value(x) for x in xs)


def is_subalgebra(subset: frozenset[int]) -> bool:
    if not subset:
        return False
    if any(unary_u(x) not in subset for x in subset):
        return False
    return all(
        discriminator(x, y, z) in subset
        for x in subset
        for y in subset
        for z in subset
    )


def preserves_algebra(perm: tuple[int, ...]) -> bool:
    p = {x: perm[x] for x in Q}
    if any(p[unary_u(x)] != unary_u(p[x]) for x in Q):
        return False
    return all(
        p[discriminator(x, y, z)]
        == discriminator(p[x], p[y], p[z])
        for x in Q
        for y in Q
        for z in Q
    )


def safe(a: tuple[int, int], u: int, v: tuple[int, int]) -> bool:
    # Make state 10 globally losing via the unconstrained observation u=2.
    if a == DEAD_STATE and u == 2:
        return False

    # At complementary binary observations 000 and 111, only binary
    # outputs 01 and 10 are allowed. Outputs containing 2 are harmless
    # here because every Q-term maps Q0^3 back into Q0.
    z = a + (u,)
    if z in SPECIAL_OBS and v in {(0, 0), (1, 1)}:
        return False
    return True


def projection_p(t: tuple[int, int, int, int, int]) -> int:
    return t[0]


def term_g(t: tuple[int, int, int, int, int]) -> int:
    a = (t[0], t[1])
    u = t[2]
    v = (t[3], t[4])
    p = projection_p(t)
    if safe(a, u, v):
        return p
    # All unsafe tuples have p in {0,1}; flipping makes p != g.
    return 1 - p


def exact_term_winning(
    W: frozenset[tuple[int, int]],
) -> tuple[bool, dict[tuple[int, int, int], tuple[int, int]]]:
    """Exact feasibility from the internal-isomorphism characterization.

    On Q0^3, each controller coordinate must stay in Q0 and commute with phi.
    Any observation containing 2 is unconstrained by the proper subalgebra
    and may be filled independently.
    """

    chosen: dict[tuple[int, int, int], tuple[int, int]] = {}

    # Observations containing 2 are independent table entries.
    for a in W:
        for u in INPUTS:
            z = a + (u,)
            if 2 in z:
                candidates = [v for v in W if safe(a, u, v)]
                if not candidates:
                    return False, {}
                chosen[z] = candidates[0]

    # Binary observations occur in phi-pairs. Choose one binary output y;
    # the paired observation is forced to output phi(y).
    seen: set[tuple[int, int, int]] = set()
    for z in BINARY_OBS:
        if z in seen:
            continue
        zp = phi_tuple(z)
        seen.add(z)
        seen.add(zp)

        a, u = z[:2], z[2]
        ap, up = zp[:2], zp[2]

        witness = None
        for y in BINARY_STATES:
            yp = phi_tuple(y)
            if a in W and not (y in W and safe(a, u, y)):
                continue
            if ap in W and not (yp in W and safe(ap, up, yp)):
                continue
            witness = y
            break

        if witness is None:
            return False, {}

        chosen[z] = witness
        chosen[zp] = phi_tuple(witness)

    return True, chosen


def all_domains():
    n = len(STATES)
    for mask in range(1 << n):
        yield frozenset(STATES[i] for i in range(n) if (mask >> i) & 1)


def main() -> None:
    # Directly verify the concrete algebra facts used from Quackenbush's example.
    subalgebras = {
        frozenset(s)
        for r in range(1, len(Q) + 1)
        for s in combinations(Q, r)
        if is_subalgebra(frozenset(s))
    }
    assert subalgebras == {frozenset({0, 1}), frozenset(Q)}

    auts = [perm for perm in permutations(Q) if preserves_algebra(perm)]
    assert auts == [(0, 1, 2)]

    # phi is an automorphism of the proper subalgebra Q0.
    assert unary_u(phi_value(0)) == phi_value(unary_u(0))
    assert unary_u(phi_value(1)) == phi_value(unary_u(1))
    for x, y, z in product(Q0, repeat=3):
        lhs = discriminator(phi_value(x), phi_value(y), phi_value(z))
        rhs = phi_value(discriminator(x, y, z))
        assert lhs == rhs

    # The safety relation is exactly the single equation p=g.
    for t in product(Q, repeat=5):
        a, u, v = (t[0], t[1]), t[2], (t[3], t[4])
        assert (projection_p(t) == term_g(t)) == safe(a, u, v)

    # g preserves the only proper subalgebra and its nontrivial internal iso.
    for t in product(Q0, repeat=5):
        assert term_g(t) in Q0
        assert term_g(phi_tuple(t)) == phi_value(term_g(t))

    ok1, witness1 = exact_term_winning(W1)
    ok2, witness2 = exact_term_winning(W2)
    oku, _ = exact_term_winning(UNION)
    assert ok1 and ok2 and not oku

    assert witness1[(0, 0, 0)] in W1
    assert witness2[(1, 1, 1)] in W2

    # Any common winning superset would have to contain 10 to satisfy the
    # 000 <-> 111 phi-coupling, but 10 is dead at environment input 2.
    winning = []
    for W in all_domains():
        ok, _ = exact_term_winning(W)
        if ok:
            winning.append(W)
            assert DEAD_STATE not in W

    common_supersets = [W for W in winning if W1 <= W and W2 <= W]
    assert common_supersets == []

    maximal = [W for W in winning if not any(W < V for V in winning)]
    expected_maximal = {
        frozenset(set(STATES) - {DEAD_STATE, (1, 1)}),
        frozenset(set(STATES) - {DEAD_STATE, (0, 0)}),
    }
    assert set(maximal) == expected_maximal
    assert len(winning) == 128

    print("PASS quasi-primal no-greatest-region witness")
    print("W1:", sorted(W1))
    print("W2:", sorted(W2))
    print("W1 union W2 term-winning:", oku)
    print("winning domains:", len(winning))
    print("maximal winning domains:", [sorted(W) for W in maximal])
    print("common winning supersets of W1,W2:", len(common_supersets))


if __name__ == "__main__":
    main()

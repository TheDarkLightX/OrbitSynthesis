#!/usr/bin/env python3
"""Exact finite checker for notes/QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md.

The algebra is Quackenbush's Example 9.2:

    Q={0,1,2}
    t(x,y,z)=z if x=y else x
    u(0)=1, u(1)=0, u(2)=1

Its only proper subalgebra is Q0={0,1}; phi swaps 0 and 1 on Q0 and is an
internal automorphism that does not extend to Q.

We verify:

1. algebra/subalgebra/automorphism facts;
2. the 13 safe-transition relation and its phi symmetry;
3. naive generated-subalgebra greatest fixed point = {00,10,11};
4. no nonempty invariant state domain admits a positional strategy preserving
   all internal-isomorphism constraints;
5. the relation is exactly one equation f=g where f,g preserve the required
   subalgebras/internal isomorphisms, so quasi-primality makes them term
   operations under the standard clone characterization.
"""

from __future__ import annotations

from itertools import combinations, permutations, product

Q = (0, 1, 2)
Q0 = frozenset((0, 1))


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    return {0: 1, 1: 0, 2: 1}[x]


def phi(x: int) -> int:
    if x == 0:
        return 1
    if x == 1:
        return 0
    raise ValueError("phi is defined only on Q0")


def is_subalgebra(s: frozenset[int]) -> bool:
    return (
        bool(s)
        and all(u(x) in s for x in s)
        and all(disc(x, y, z) in s for x in s for y in s for z in s)
    )


def subalgebras() -> list[frozenset[int]]:
    out = []
    for r in range(1, len(Q) + 1):
        for xs in combinations(Q, r):
            s = frozenset(xs)
            if is_subalgebra(s):
                out.append(s)
    return out


def automorphisms() -> list[dict[int, int]]:
    out = []
    for values in permutations(Q):
        m = dict(zip(Q, values))
        if not all(m[u(x)] == u(m[x]) for x in Q):
            continue
        if not all(
            m[disc(x, y, z)] == disc(m[x], m[y], m[z])
            for x in Q for y in Q for z in Q
        ):
            continue
        out.append(m)
    return out


STATES = list(product(Q, repeat=2))
INPUTS = list(Q)
OUTPUTS = STATES

SAFE = {
    ((0, 0), 0, (0, 0)),
    ((0, 0), 1, (0, 1)),
    ((0, 0), 1, (1, 0)),
    ((0, 0), 2, (0, 0)),
    ((0, 1), 0, (0, 1)),
    ((0, 1), 1, (1, 1)),
    ((1, 0), 0, (0, 0)),
    ((1, 0), 1, (1, 0)),
    ((1, 0), 2, (1, 1)),
    ((1, 1), 0, (0, 1)),
    ((1, 1), 0, (1, 0)),
    ((1, 1), 1, (1, 1)),
    ((1, 1), 2, (0, 0)),
}


def generated_subalgebra(values: tuple[int, ...]) -> frozenset[int]:
    return Q0 if all(v in Q0 for v in values) else frozenset(Q)


def local_options(w: set[tuple[int, int]], state: tuple[int, int], inp: int):
    g = generated_subalgebra(state + (inp,))
    return [
        out for out in OUTPUTS
        if out in w
        and (state, inp, out) in SAFE
        and all(v in g for v in out)
    ]


def naive_pre(w: set[tuple[int, int]]) -> set[tuple[int, int]]:
    return {
        state
        for state in STATES
        if all(local_options(w, state, inp) for inp in INPUTS)
    }


def naive_fixed_point() -> set[tuple[int, int]]:
    w = set(STATES)
    while True:
        nxt = naive_pre(w)
        if nxt == w:
            return w
        w = nxt


def phi_tuple(z: tuple[int, ...]) -> tuple[int, ...]:
    assert all(v in Q0 for v in z)
    return tuple(phi(v) for v in z)


def phi_output(out: tuple[int, int]) -> tuple[int, int]:
    assert all(v in Q0 for v in out)
    return phi(out[0]), phi(out[1])


def q0_observation_orbits():
    observations = list(product((0, 1), repeat=3))
    seen: set[tuple[int, int, int]] = set()
    orbits = []
    for z in observations:
        if z in seen:
            continue
        z2 = phi_tuple(z)
        seen.add(z)
        seen.add(z2)
        orbits.append((z, z2))
    return orbits


def term_strategy_domain_feasible(w: set[tuple[int, int]]) -> bool:
    """Exact finite quasi-primal table feasibility for this Q.

    The internal-isomorphism constraints are:

    - observations entirely in Q0 must output in Q0^2;
    - paired Q0 observations z and phi(z) have outputs related by phi;
    - observations involving 2 have no nontrivial cross-observation constraint
      because the only generated subalgebra is Q and Aut(Q) is trivial.

    Safety/invariance is imposed only on states in w; the term table is total,
    so values at nonwinning observations can always be completed consistently.
    """

    # Observations involving 2 are independent once their state is winning.
    for state in w:
        for inp in INPUTS:
            z = state + (inp,)
            if all(v in Q0 for v in z):
                continue
            if not local_options(w, state, inp):
                return False

    # Q0 observations come in phi-pairs.
    for z, z2 in q0_observation_orbits():
        s1, i1 = (z[0], z[1]), z[2]
        s2, i2 = (z2[0], z2[1]), z2[2]
        win1, win2 = s1 in w, s2 in w

        if win1 and win2:
            opts1 = local_options(w, s1, i1)
            opts2 = set(local_options(w, s2, i2))
            if not any(phi_output(out) in opts2 for out in opts1):
                return False
        elif win1:
            if not local_options(w, s1, i1):
                return False
        elif win2:
            if not local_options(w, s2, i2):
                return False

    return True


def all_term_strategy_domains():
    feasible = []
    for mask in range(1 << len(STATES)):
        w = {
            STATES[i]
            for i in range(len(STATES))
            if mask & (1 << i)
        }
        if term_strategy_domain_feasible(w):
            feasible.append(w)
    return feasible


def flatten_transition(t):
    state, inp, out = t
    return state + (inp,) + out


SAFE_FLAT = {flatten_transition(t) for t in SAFE}
ALL5 = list(product(Q, repeat=5))


def f(z: tuple[int, ...]) -> int:
    return z[0]


def g(z: tuple[int, ...]) -> int:
    fv = f(z)
    if z in SAFE_FLAT:
        return fv
    if all(v in Q0 for v in z):
        return phi(fv)
    # Any distinct Q-value is allowed once the input tuple generates Q.
    return (fv + 1) % 3


def preserves_required_quasiprimal_structure(h) -> bool:
    # Identity internal isomorphism on Q0 -> preserve the subalgebra Q0.
    if not all(
        h(z) in Q0
        for z in product((0, 1), repeat=5)
    ):
        return False

    # Nontrivial internal automorphism phi of Q0.
    if not all(
        h(phi_tuple(z)) == phi(h(z))
        for z in product((0, 1), repeat=5)
    ):
        return False

    # On Q itself the only automorphism is the identity, checked separately.
    return True


def check_algebra() -> None:
    assert subalgebras() == [Q0, frozenset(Q)]
    autos = automorphisms()
    assert autos == [{0: 0, 1: 1, 2: 2}]

    # phi is an automorphism of Q0.
    assert all(phi(u(x)) == u(phi(x)) for x in Q0)
    assert all(
        phi(disc(x, y, z)) == disc(phi(x), phi(y), phi(z))
        for x in Q0 for y in Q0 for z in Q0
    )

    # It cannot extend: Q's only automorphism is identity.
    assert not any(auto[0] == 1 and auto[1] == 0 for auto in autos)


def check_safe_relation_symmetry() -> None:
    assert len(SAFE) == 13
    assert all(
        (z in SAFE_FLAT) == (phi_tuple(z) in SAFE_FLAT)
        for z in product((0, 1), repeat=5)
    )


def check_naive_vs_term() -> None:
    naive = naive_fixed_point()
    assert naive == {(0, 0), (1, 0), (1, 1)}

    # The critical phi-paired observations.
    z = ((0, 0), 1)
    zp = ((1, 1), 0)
    assert local_options(naive, *z) == [(1, 0)]
    assert local_options(naive, *zp) == [(1, 0)]
    assert phi_output((1, 0)) == (0, 1)
    assert (0, 1) not in naive

    feasible = all_term_strategy_domains()
    assert feasible == [set()]


def check_equation_definition() -> None:
    # Equation f=g defines exactly the safe relation.
    assert all(
        (f(z) == g(z)) == (z in SAFE_FLAT)
        for z in ALL5
    )

    # f is a projection; g satisfies the finite preservation conditions in
    # Pixley's quasi-primal clone characterization for this Q.
    assert preserves_required_quasiprimal_structure(f)
    assert preserves_required_quasiprimal_structure(g)


def main() -> None:
    check_algebra()
    check_safe_relation_symmetry()
    check_naive_vs_term()
    check_equation_definition()
    print("Quackenbush Q subalgebras: Q0 and Q only")
    print("Aut(Q): identity only; phi is internal on Q0 and nonextendable")
    print("naive generated-subalgebra fixed point: {(0,0),(1,0),(1,1)}")
    print("exact quasi-primal term-controllable nonempty domains: none")
    print("13-transition safe relation is exactly equation f=g")
    print("quasi-primal coupling counterexample: all checks passed")


if __name__ == "__main__":
    main()

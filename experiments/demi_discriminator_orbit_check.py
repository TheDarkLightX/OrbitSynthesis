#!/usr/bin/env python3
"""Finite calibration for the demi-semi-primal orbit predecessor.

Algebra: the pure ternary discriminator on D={0,1,2}.
Every nonempty subset is a subalgebra and Aut(D)=S3. Its term operations
are exactly conservative S3-equivariant operations.

Checks:
1. Exhaust every S3-invariant one-state safety relation (32 total).
2. Sample 200 S3-invariant two-state safety relations and compare the
   orbit/local predecessor against all 24^2=576 ternary term controllers.

This is finite verification of the derived theorem, not a universal proof.
"""

from __future__ import annotations

from itertools import product
import random

D = (0, 1, 2)


def equality_pattern(xs: tuple[int, ...]) -> tuple[int, ...]:
    names: dict[int, int] = {}
    nxt = 0
    out = []
    for x in xs:
        if x not in names:
            names[x] = nxt
            nxt += 1
        out.append(names[x])
    return tuple(out)


def binary_term(choice: int):
    def f(x: int, y: int) -> int:
        if x == y:
            return x
        return x if choice == 0 else y
    return f


def ternary_term(c_xy: int, c_xz: int, c_yz: int, c_distinct: int):
    def f(x: int, y: int, z: int) -> int:
        if x == y == z:
            return x
        if x == y:
            return x if c_xy == 0 else z
        if x == z:
            return x if c_xz == 0 else y
        if y == z:
            return y if c_yz == 0 else x
        return (x, y, z)[c_distinct]
    return f


BINARY_TERMS = tuple(binary_term(c) for c in range(2))
TERNARY_TERMS = tuple(
    ternary_term(a, b, c, d)
    for a in range(2)
    for b in range(2)
    for c in range(2)
    for d in range(3)
)
assert len(TERNARY_TERMS) == 24


def orbit_predecessor_gfp(k: int, m: int, safe):
    """DPre for pure discriminator D.

    Sg(observation) is exactly the set of values occurring in the observation.
    For |D|=3, the stabilizer-fixed restriction contributes nothing beyond
    this generated-subalgebra condition.
    """
    states = tuple(product(D, repeat=k))
    inputs = tuple(product(D, repeat=m))
    W = set(states)
    rounds = 0
    while True:
        W2 = set()
        for a in states:
            good = True
            for u in inputs:
                generated = set(a + u)
                candidates = [
                    v for v in W
                    if all(x in generated for x in v) and safe(a, u, v)
                ]
                if not candidates:
                    good = False
                    break
            if good:
                W2.add(a)
        if W2 == W:
            return frozenset(W), rounds
        W = W2
        rounds += 1


def fixed_controller_win(k: int, m: int, safe, sigma):
    states = tuple(product(D, repeat=k))
    inputs = tuple(product(D, repeat=m))
    W = set(states)
    while True:
        W2 = set()
        for a in states:
            good = True
            for u in inputs:
                v = sigma(a, u)
                if v not in W or not safe(a, u, v):
                    good = False
                    break
            if good:
                W2.add(a)
        if W2 == W:
            return frozenset(W)
        W = W2


def check_one_state_exhaustive() -> None:
    # Transition tuple has arity 3: state, input, next.
    patterns = sorted({equality_pattern(t) for t in product(D, repeat=3)})
    assert len(patterns) == 5

    for mask in range(1 << len(patterns)):
        allowed = {
            patterns[i] for i in range(len(patterns))
            if (mask >> i) & 1
        }

        def safe(a, u, v, allowed=allowed):
            return equality_pattern(a + u + v) in allowed

        orbit_win, _ = orbit_predecessor_gfp(1, 1, safe)
        exact_regions = []
        for f in BINARY_TERMS:
            def sigma(a, u, f=f):
                return (f(a[0], u[0]),)
            exact_regions.append(fixed_controller_win(1, 1, safe, sigma))

        union_exact = frozenset().union(*exact_regions)
        assert orbit_win == union_exact
        if orbit_win:
            assert orbit_win in exact_regions


def check_two_state_random(samples: int = 200, seed: int = 20260811) -> dict:
    # Transition tuple has arity 5: two state, one input, two next.
    patterns = sorted({equality_pattern(t) for t in product(D, repeat=5)})
    assert len(patterns) == 41

    controllers = []
    for f1 in TERNARY_TERMS:
        for f2 in TERNARY_TERMS:
            def sigma(a, u, f1=f1, f2=f2):
                z = (a[0], a[1], u[0])
                return (f1(*z), f2(*z))
            controllers.append(sigma)
    assert len(controllers) == 576

    rng = random.Random(seed)
    size_hist: dict[int, int] = {}
    max_rounds = 0

    for trial in range(samples):
        allowed = {p for p in patterns if rng.getrandbits(1)}

        def safe(a, u, v, allowed=allowed):
            return equality_pattern(a + u + v) in allowed

        orbit_win, rounds = orbit_predecessor_gfp(2, 1, safe)
        max_rounds = max(max_rounds, rounds)

        union_exact = frozenset()
        exact_match = not orbit_win
        for sigma in controllers:
            region = fixed_controller_win(2, 1, safe, sigma)
            union_exact = union_exact.union(region)
            if region == orbit_win:
                exact_match = True

        assert orbit_win == union_exact, (
            "orbit predecessor disagrees with global term-controller search",
            trial,
            orbit_win,
            union_exact,
        )
        assert exact_match, (
            "no single term controller realizes the predicted greatest region",
            trial,
            orbit_win,
        )
        size_hist[len(orbit_win)] = size_hist.get(len(orbit_win), 0) + 1

    return {
        "samples": samples,
        "controllers_per_sample": len(controllers),
        "size_histogram": size_hist,
        "max_fixpoint_rounds": max_rounds,
    }


def main() -> None:
    check_one_state_exhaustive()
    stats = check_two_state_random()
    print("PASS demi-semi-primal discriminator calibration")
    print("one-state invariant relations exhausted: 32")
    print("two-state random invariant relations:", stats["samples"])
    print("term controllers checked per two-state relation:", stats["controllers_per_sample"])
    print("winning-region size histogram:", stats["size_histogram"])
    print("max orbit-predecessor rounds:", stats["max_fixpoint_rounds"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact calibration of SMP -> term-constrained safety synthesis.

For the two-element meet-semilattice A=({0,1}; meet), n=3, enumerate all
3^8=6561 partial functions f:T subseteq A^3 -> A.  The n-ary term
operations are exactly the nonempty conjunctions of variables (7 tables).

For every partial f we compare:

1. SMP/interpolation: does some term operation extend f?
2. Safety synthesis: on state space A^3, full invariant W=A^3, no inputs,
   require next_state[0]=f(state) whenever state is in dom(f), and require
   all three controller coordinates to be term operations.

The two answers must agree for every partial f.  This is a finite
calibration of the general reduction, not its proof.
"""

from __future__ import annotations

from itertools import product

A = (0, 1)
N = 3
STATES = tuple(product(A, repeat=N))
TERM_MASKS = tuple(range(1, 1 << N))


def meet_term(mask: int, z: tuple[int, ...]) -> int:
    out = 1
    for i, value in enumerate(z):
        if (mask >> i) & 1:
            out &= value
    return out


TERM_TABLE = {
    mask: tuple(meet_term(mask, z) for z in STATES)
    for mask in TERM_MASKS
}
assert len(set(TERM_TABLE.values())) == 7


def smp_extendible(partial: tuple[int, ...]) -> bool:
    """-1 means undefined; 0/1 are prescribed values."""
    return any(
        all(want == -1 or TERM_TABLE[mask][i] == want
            for i, want in enumerate(partial))
        for mask in TERM_MASKS
    )


def game_winning(partial: tuple[int, ...]) -> bool:
    """Brute-force all 7^3 term-controller tuples."""
    for controller in product(TERM_MASKS, repeat=N):
        good = True
        for i, _state in enumerate(STATES):
            next_state = tuple(TERM_TABLE[mask][i] for mask in controller)
            want = partial[i]
            if want != -1 and next_state[0] != want:
                good = False
                break
        if good:
            return True
    return False


def main() -> None:
    total = 0
    extendible = 0
    for partial in product((-1, 0, 1), repeat=len(STATES)):
        smp = smp_extendible(partial)
        game = game_winning(partial)
        assert smp == game, (partial, smp, game)
        total += 1
        extendible += int(smp)

    print("PASS SMP -> term-safety calibration")
    print("algebra: two-element meet-semilattice")
    print("observation/state arity:", N)
    print("term operations checked:", len(TERM_MASKS))
    print("partial functions exhausted:", total)
    print("extendible / winning instances:", extendible)


if __name__ == "__main__":
    main()

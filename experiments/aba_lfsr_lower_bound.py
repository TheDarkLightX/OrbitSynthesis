#!/usr/bin/env python3
"""Executable small-d validation of the LFSR lower-bound family.

For each d, search a feedback mask whose d-bit shift-register map has one
cycle on all 2^d-1 nonzero cell labels.  Compile the deterministic transition
into the exact ABA support-clause cell game and verify:

- zero-safe arena is all cells;
- one singleton Safe obligation produces exactly 2^d-1 strict fixed-point
  strengthenings;
- final canonical positive family is every nonzero singleton.

The search is only a small-d executable witness.  The all-d theorem uses the
classical existence of primitive degree-d polynomials over GF(2).
"""

from __future__ import annotations

from aba_safety_clause_game import Clause, normalize, conjunction, cpre_clause


def parity(x: int) -> int:
    return x.bit_count() & 1


def lfsr_next(x: int, d: int, taps: int) -> int:
    feedback = parity(x & taps)
    return (x >> 1) | (feedback << (d - 1))


def nonzero_cycle_length(d: int, taps: int, start: int = 1) -> int:
    x = start
    seen: dict[int, int] = {}
    while x not in seen:
        if x == 0:
            return 0
        seen[x] = len(seen)
        x = lfsr_next(x, d, taps)
    if x != start:
        return 0
    return len(seen)


def find_maximal_taps(d: int) -> int:
    target = (1 << d) - 1
    # Constant term must be nonzero for an invertible companion recurrence,
    # hence bit 0 should participate.  Searching all masks is tiny here.
    for taps in range(1, 1 << d, 2):
        if nonzero_cycle_length(d, taps) == target:
            return taps
    raise RuntimeError(f"no maximal taps found for d={d}")


def deterministic_step_clause(d: int, taps: int) -> Clause:
    """One forbidden mask representing y = LFSR(x) at cell level."""
    n = 1 << d
    forbidden = 0
    for x in range(n):
        expected = lfsr_next(x, d, taps)
        for y in range(n):
            if y != expected:
                full_cell = x | (y << d)
                forbidden |= 1 << full_cell
    return normalize(Clause(2 * d, forbidden=forbidden))


def iterate_family(d: int, taps: int) -> tuple[int, Clause]:
    step = deterministic_step_clause(d, taps)
    seed_cell = 1  # nonzero, therefore on the maximal cycle
    safe = normalize(Clause(d, positive=(1 << seed_cell,)))

    w = normalize(Clause(d))  # top
    strict = 0
    for _ in range((1 << d) + 2):
        nxt = conjunction(safe, cpre_clause(step, w, d=d, e=0))
        if nxt == w:
            return strict, w
        strict += 1
        w = nxt
    raise RuntimeError("fixed point exceeded expected bound")


def self_test() -> None:
    for d in range(2, 6):
        taps = find_maximal_taps(d)
        assert lfsr_next(0, d, taps) == 0
        assert nonzero_cycle_length(d, taps) == (1 << d) - 1

        strict, winning = iterate_family(d, taps)
        expected = tuple(1 << v for v in range(1, 1 << d))

        assert not winning.is_false
        assert winning.forbidden == 0
        assert winning.positive == expected
        assert strict == (1 << d) - 1


def main() -> None:
    self_test()
    print("ABA LFSR compact lower-bound checks passed")
    for d in range(2, 6):
        taps = find_maximal_taps(d)
        strict, _ = iterate_family(d, taps)
        print(
            f"  d={d}: taps=0b{taps:0{d}b}, "
            f"nonzero orbit/fixed-point strict steps={strict}"
        )


if __name__ == "__main__":
    main()

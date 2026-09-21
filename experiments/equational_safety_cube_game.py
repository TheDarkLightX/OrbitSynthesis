#!/usr/bin/env python3
"""Bounded exact checks for notes/EQUATIONAL_SAFETY_CUBE_GAME.md.

The explicit side works over complete support types of a Boolean algebra with:

- one current-state BA variable s;
- one environment BA variable x;
- one controller/next-state BA variable y.

There are 3 nonempty supports for s, 15 for (s,x), and 255 for (s,x,y).
For random Boolean transition truth tables F and every principal target region
W_A, compare the explicit controllable predecessor with the predicted finite
2-state Boolean-cube predecessor.
"""

from __future__ import annotations

from itertools import product
import random


def extensions(base_support: int, base_dims: int, extra_dims: int):
    """Enumerate all nonempty fine supports projecting to base_support."""
    n_base_cells = 1 << base_dims
    refinements = 1 << extra_dims
    active = [a for a in range(n_base_cells) if base_support & (1 << a)]

    for local_masks in product(range(1, 1 << refinements), repeat=len(active)):
        fine = 0
        for a, local in zip(active, local_masks):
            for extra in range(refinements):
                if local & (1 << extra):
                    fine |= 1 << (a | (extra << base_dims))
        yield fine


def projection(mask: int, total_dims: int, keep_positions: list[int]) -> int:
    out = 0
    for cell in range(1 << total_dims):
        if not (mask & (1 << cell)):
            continue
        projected = 0
        for j, pos in enumerate(keep_positions):
            if cell & (1 << pos):
                projected |= 1 << j
        out |= 1 << projected
    return out


def principal_region(a_mask: int) -> set[int]:
    """All nonempty state supports contained in the Boolean cell set A."""
    return {support for support in range(1, 4) if not (support & ~a_mask)}


def explicit_cpre(f_mask: int, target_supports: set[int]) -> set[int]:
    """Exact BA support-game CPre for k=p=1."""
    winning: set[int] = set()

    for state_support in range(1, 4):
        all_inputs_work = True

        # Environment chooses any complete (s,x) support extending s.
        for sx_support in extensions(state_support, base_dims=1, extra_dims=1):
            some_output_works = False

            # Controller chooses any complete (s,x,y) support extending (s,x).
            for sxy_support in extensions(sx_support, base_dims=2, extra_dims=1):
                # F=0 iff the realized support avoids every truth-table cell
                # on which F evaluates to 1.
                if sxy_support & f_mask:
                    continue

                y_support = projection(sxy_support, total_dims=3, keep_positions=[2])
                if y_support in target_supports:
                    some_output_works = True
                    break

            if not some_output_works:
                all_inputs_work = False
                break

        if all_inputs_work:
            winning.add(state_support)

    return winning


def cube_pre(f_mask: int, a_mask: int) -> int:
    """Finite two-state Boolean-cube predecessor for k=p=1."""
    result = 0
    for a in range(2):
        good = True
        for u in range(2):
            if not any(
                (a_mask & (1 << v))
                and not (f_mask & (1 << (a | (u << 1) | (v << 2))))
                for v in range(2)
            ):
                good = False
                break
        if good:
            result |= 1 << a
    return result


def verify_one_step(f_mask: int) -> None:
    for a_mask in range(4):
        explicit = explicit_cpre(f_mask, principal_region(a_mask))
        predicted_a = cube_pre(f_mask, a_mask)
        predicted = principal_region(predicted_a)
        assert explicit == predicted, (
            f_mask,
            a_mask,
            explicit,
            predicted_a,
            predicted,
        )


def verify_fixed_point(f_mask: int) -> None:
    a_mask = 0b11
    explicit_region = principal_region(a_mask)

    # The descending chain has at most two strict cell removals here, but run
    # extra rounds to assert stable agreement.
    for _ in range(6):
        next_explicit = explicit_cpre(f_mask, explicit_region)
        next_a = cube_pre(f_mask, a_mask)
        assert next_explicit == principal_region(next_a)
        explicit_region = next_explicit
        a_mask = next_a


def exhaustive_all_transition_tables() -> None:
    # With one s, one x, one y bit, F has 8 Boolean truth-table cells, hence
    # exactly 256 possible transition terms up to Boolean equivalence. Check all.
    for f_mask in range(256):
        verify_one_step(f_mask)
        verify_fixed_point(f_mask)
    print("all 256 transition truth tables passed exact support-game validation")


def randomized_smoke(seed: int = 9) -> None:
    # Redundant after the exhaustive 256-case sweep, retained as a convenient
    # deterministic smoke entry if this script is later generalized.
    rng = random.Random(seed)
    for _ in range(50):
        f_mask = rng.randrange(256)
        verify_one_step(f_mask)


def main() -> None:
    exhaustive_all_transition_tables()
    randomized_smoke()
    print("equational safety cube-game checker: all tests passed")


if __name__ == "__main__":
    main()

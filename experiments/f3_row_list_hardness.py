#!/usr/bin/env python3
"""Finite calibration for F3_ROW_LIST_REACTIVE_HARDNESS.md.

Checks the reduction from positive 1-in-3-SAT to:
1. row-list term interpolation over A=(F3;+,-,0); and
2. sparse input-free fixed-domain term safety over the same fixed algebra.

The theorem proof is in the note. This script is an exact small-instance
cross-check, including full linear-controller enumeration for n=3.
"""

from __future__ import annotations

from itertools import combinations, product
import random

F3 = (0, 1, 2)


def dot(alpha: tuple[int, ...], x: tuple[int, ...]) -> int:
    return sum(a * b for a, b in zip(alpha, x)) % 3


def positive_1in3_sat(n: int, clauses: tuple[tuple[int, int, int], ...]) -> bool:
    return any(
        all(sum(bits[i] for i in clause) == 1 for clause in clauses)
        for bits in product((0, 1), repeat=n)
    )


def row_list_feasible(n: int, clauses: tuple[tuple[int, int, int], ...]) -> bool:
    for alpha in product(F3, repeat=n):
        if any(value not in (0, 1) for value in alpha):
            continue
        if all(sum(alpha[i] for i in clause) % 3 == 1 for clause in clauses):
            return True
    return False


def basis(n: int, index: int) -> tuple[int, ...]:
    return tuple(1 if i == index else 0 for i in range(n))


def clause_vector(n: int, clause: tuple[int, int, int]) -> tuple[int, ...]:
    chosen = set(clause)
    return tuple(1 if i in chosen else 0 for i in range(n))


def q_state(n: int, value: int) -> tuple[int, ...]:
    return (value,) + (0,) * (n - 1)


def sparse_game(
    n: int,
    clauses: tuple[tuple[int, int, int], ...],
) -> tuple[
    frozenset[tuple[int, ...]],
    dict[tuple[int, ...], frozenset[tuple[int, ...]]],
]:
    q0 = q_state(n, 0)
    q1 = q_state(n, 1)
    q2 = q_state(n, 2)

    variable_states = {basis(n, i) for i in range(n)}
    clause_states = {clause_vector(n, clause) for clause in clauses}
    W = frozenset(variable_states | clause_states | {q0, q2})

    allowed: dict[tuple[int, ...], frozenset[tuple[int, ...]]] = {}
    for state in W:
        if state in clause_states:
            allowed[state] = frozenset({q1})
        elif state in variable_states:
            allowed[state] = frozenset({q0, q1})
        elif state == q0:
            allowed[state] = frozenset({q0})
        elif state == q2:
            allowed[state] = frozenset({q0, q2})
        else:  # pragma: no cover - W has no other state class
            raise AssertionError(state)

    return W, allowed


def constructed_controller_wins(
    n: int,
    clauses: tuple[tuple[int, int, int], ...],
    alpha: tuple[int, ...],
) -> bool:
    W, allowed = sparse_game(n, clauses)
    for state in W:
        output = (dot(alpha, state),) + (0,) * (n - 1)
        if output not in allowed[state]:
            return False
    return True


def sparse_game_feasible_via_first_row(
    n: int,
    clauses: tuple[tuple[int, int, int], ...],
) -> bool:
    # The note proves necessity from the first matrix row and sufficiency by
    # setting all remaining rows to zero.
    return any(
        constructed_controller_wins(n, clauses, alpha)
        for alpha in product(F3, repeat=n)
    )


def mat_vec(matrix: tuple[tuple[int, ...], ...], x: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(dot(row, x) for row in matrix)


def full_matrix_game_feasible_n3(
    clauses: tuple[tuple[int, int, int], ...],
) -> bool:
    n = 3
    W, allowed = sparse_game(n, clauses)
    rows = tuple(product(F3, repeat=n))
    for matrix_rows in product(rows, repeat=n):
        matrix = tuple(matrix_rows)
        if all(mat_vec(matrix, state) in allowed[state] for state in W):
            return True
    return False


def exhaustive_formula_subsets() -> int:
    checked = 0
    for n in (3, 4, 5):
        possible = tuple(combinations(range(n), 3))
        for mask in range(1 << len(possible)):
            clauses = tuple(
                possible[index]
                for index in range(len(possible))
                if mask & (1 << index)
            )
            sat = positive_1in3_sat(n, clauses)
            rlti = row_list_feasible(n, clauses)
            game = sparse_game_feasible_via_first_row(n, clauses)
            assert sat == rlti == game, (n, clauses, sat, rlti, game)

            if n == 3:
                full = full_matrix_game_feasible_n3(clauses)
                assert full == sat, (clauses, full, sat)

            checked += 1

    assert checked == 1042
    return checked


def randomized_larger(seed: int = 0, trials: int = 500) -> int:
    rng = random.Random(seed)
    n = 6
    possible = tuple(combinations(range(n), 3))

    for trial in range(trials):
        clauses = tuple(clause for clause in possible if rng.random() < 0.45)
        sat = positive_1in3_sat(n, clauses)
        rlti = row_list_feasible(n, clauses)
        game = sparse_game_feasible_via_first_row(n, clauses)
        assert sat == rlti == game, (trial, clauses, sat, rlti, game)

    return trials


def main() -> None:
    exact = exhaustive_formula_subsets()
    randomized = randomized_larger()
    print("PASS: F3 row-list/reactive hardness calibration")
    print(f"exhaustive positive-1-in-3 formula subsets checked: {exact}")
    print(f"larger deterministic randomized formulas checked: {randomized}")
    print("n=3 full 3^9 linear-controller matrices checked for both formula subsets")


if __name__ == "__main__":
    main()

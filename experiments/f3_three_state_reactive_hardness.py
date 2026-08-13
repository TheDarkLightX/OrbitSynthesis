#!/usr/bin/env python3
"""Exact calibration for F3_THREE_STATE_REACTIVE_HARDNESS.md.

For graph G on n vertices, dangerous environment inputs are e_i-e_j for edges.
A term controller is beta*s + alpha dot u over F3. At current state s=0,
safety requires nonzero output on every dangerous input, exactly proper
3-coloring.

Exhaust all labelled simple graphs on n<=5.
"""

from __future__ import annotations

from itertools import combinations, product

F3 = (0, 1, 2)


def graph_3colorable(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    return any(
        all(colors[i] != colors[j] for i, j in edges)
        for colors in product(F3, repeat=n)
    )


def controller_exists(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    # beta does not affect the dangerous observations because the current
    # state there is 0. Still enumerate it to mirror the complete term form.
    for beta in F3:
        del beta
        for alpha in product(F3, repeat=n):
            if all((alpha[i] - alpha[j]) % 3 != 0 for i, j in edges):
                return True
    return False


def main() -> None:
    checked = 0
    by_n: dict[int, int] = {}

    for n in range(1, 6):
        possible_edges = tuple(combinations(range(n), 2))
        count = 0
        for mask in range(1 << len(possible_edges)):
            edges = tuple(
                possible_edges[index]
                for index in range(len(possible_edges))
                if mask & (1 << index)
            )
            left = graph_3colorable(n, edges)
            right = controller_exists(n, edges)
            assert left == right, (n, edges, left, right)
            count += 1
            checked += 1
        by_n[n] = count

    assert checked == 1099
    assert by_n == {1: 1, 2: 2, 3: 8, 4: 64, 5: 1024}

    print("PASS: three-state F3 reactive hardness calibration")
    print(f"labelled graphs checked: {checked}")
    for n in sorted(by_n):
        print(f"n={n}: {by_n[n]} graphs")


if __name__ == "__main__":
    main()

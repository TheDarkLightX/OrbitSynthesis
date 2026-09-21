#!/usr/bin/env python3
"""Exact calibration for F3_NONZERO_ROW_HARDNESS.md.

For a graph G on n labelled vertices, associate alpha_i in F3 to vertex i.
For every edge {i,j}, require alpha_i-alpha_j != 0.
This is exactly proper 3-colorability.

Exhaust all labelled simple graphs on n=1,...,5.
"""

from __future__ import annotations

from itertools import combinations, product

F3 = (0, 1, 2)


def graph_3colorable(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    return any(
        all(colors[i] != colors[j] for i, j in edges)
        for colors in product(F3, repeat=n)
    )


def nonzero_row_feasible(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    # An n-ary term over (F3;+,-,0) is alpha dot x.
    # Edge row e_i-e_j evaluates to alpha_i-alpha_j.
    return any(
        all((alpha[i] - alpha[j]) % 3 in (1, 2) for i, j in edges)
        for alpha in product(F3, repeat=n)
    )


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
            right = nonzero_row_feasible(n, edges)
            assert left == right, (n, edges, left, right)
            checked += 1
            count += 1
        by_n[n] = count

    assert by_n == {1: 1, 2: 2, 3: 8, 4: 64, 5: 1024}
    assert checked == 1099

    print("PASS: graph coloring = F3 nonzero row interpolation")
    print(f"labelled graphs checked: {checked}")
    for n in sorted(by_n):
        print(f"n={n}: {by_n[n]} graphs")


if __name__ == "__main__":
    main()

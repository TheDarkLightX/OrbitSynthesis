#!/usr/bin/env python3
"""Exhaustive bounded validation of alternating-block ABA clause QE.

We generate prenex sentences

    Q0 x0 Q1 x1 ... Q(k-1) x(k-1) . C

where C is one conjunction of a zero-equation support mask Z and q
nonzero/disequation support masks G_j.  The support universe at the matrix has
2^k Venn cells.

Two evaluators are compared:

1. direct semantic recursion through every realizable ABA type extension;
2. repeated closed-form support projection from
   notes/ABA_ALTERNATING_CLAUSE_QE.md.

The exhaustive semantic evaluator is intentionally independent of the closed
form and is used only for small k.
"""

from __future__ import annotations

import itertools
import random


def clause_holds(support: int, forbidden: int, positive_sets: list[int]) -> bool:
    return not (support & forbidden) and all(support & g for g in positive_sets)


def one_variable_extensions(coarse_support: int, n_coarse_cells: int):
    """All ABA support extensions after adding one new (last) variable."""
    active = [i for i in range(n_coarse_cells) if coarse_support & (1 << i)]
    for choices in itertools.product((1, 2, 3), repeat=len(active)):
        fine = 0
        for coarse_cell, choice in zip(active, choices):
            if choice & 1:
                fine |= 1 << (2 * coarse_cell)
            if choice & 2:
                fine |= 1 << (2 * coarse_cell + 1)
        yield fine


def semantic_sentence_value(
    quantifiers: tuple[str, ...], forbidden: int, positive_sets: list[int]
) -> bool:
    """Evaluate the prenex sentence by explicit support-extension recursion."""
    k = len(quantifiers)

    def rec(depth: int, support: int) -> bool:
        if depth == k:
            return clause_holds(support, forbidden, positive_sets)

        n_coarse = 1 << depth
        vals = (
            rec(depth + 1, fine)
            for fine in one_variable_extensions(support, n_coarse)
        )
        if quantifiers[depth] == "E":
            return any(vals)
        if quantifiers[depth] == "A":
            return all(vals)
        raise ValueError(quantifiers[depth])

    # T_0 has one mandatory support cell: the universe 1 is nonzero.
    return rec(0, 1)


def project_exists(forbidden: int, positive_sets: list[int], n_coarse: int):
    new_z = 0
    new_g = [0 for _ in positive_sets]

    for v in range(n_coarse):
        fiber = (1 << (2 * v)) | (1 << (2 * v + 1))

        # Every refinement forbidden -> coarse cell must be zero.
        if (fiber & ~forbidden) == 0:
            new_z |= 1 << v

        allowed_fiber = fiber & ~forbidden
        for j, g in enumerate(positive_sets):
            if allowed_fiber & g:
                new_g[j] |= 1 << v

    return new_z, new_g


def project_forall(forbidden: int, positive_sets: list[int], n_coarse: int):
    new_z = 0
    new_g = [0 for _ in positive_sets]

    for v in range(n_coarse):
        fiber = (1 << (2 * v)) | (1 << (2 * v + 1))

        # Some refinement violates the zero equation -> active coarse cell
        # cannot satisfy the equation universally.
        if fiber & forbidden:
            new_z |= 1 << v

        # Every refinement hits G_j iff the entire fiber lies inside G_j.
        for j, g in enumerate(positive_sets):
            if (fiber & ~g) == 0:
                new_g[j] |= 1 << v

    return new_z, new_g


def projected_sentence_value(
    quantifiers: tuple[str, ...], forbidden: int, positive_sets: list[int]
) -> bool:
    k = len(quantifiers)
    z = forbidden
    gs = list(positive_sets)

    # Eliminate innermost variable first.  The support indexing makes the
    # innermost/latest variable the low bit, so each projection groups pairs.
    for current_k in range(k, 0, -1):
        q = quantifiers[current_k - 1]
        n_coarse = 1 << (current_k - 1)
        if q == "E":
            z, gs = project_exists(z, gs, n_coarse)
        elif q == "A":
            z, gs = project_forall(z, gs, n_coarse)
        else:
            raise ValueError(q)

    return clause_holds(1, z, gs)


def self_test(seed: int = 11) -> None:
    rng = random.Random(seed)

    # Exhaust every quantifier pattern for k<=3 and many random clauses.
    for k in range(1, 4):
        width = 1 << k
        for quantifiers in itertools.product(("E", "A"), repeat=k):
            for _ in range(80):
                forbidden = rng.randrange(1 << width)
                q = rng.randrange(4)
                positive_sets = [rng.randrange(1 << width) for _ in range(q)]

                semantic = semantic_sentence_value(
                    quantifiers, forbidden, positive_sets
                )
                projected = projected_sentence_value(
                    quantifiers, forbidden, positive_sets
                )
                assert semantic == projected, (
                    k,
                    quantifiers,
                    forbidden,
                    positive_sets,
                    semantic,
                    projected,
                )


def main() -> None:
    self_test()
    print("alternating ABA clause-QE exhaustive checks passed")
    print("  all E/A quantifier patterns for k=1,2,3")
    print("  80 randomized clauses per prefix")
    print("  0..3 disequation obligations")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Meta-check for F3_ROW_LIST_DICHOTOMY.md.

Enumerate all 127 nonempty languages of nonempty subsets of F3 and check the
claimed combinatorial partition. Also verify the field-scaling normalizations
used in the two NP-hardness cases.
"""

from __future__ import annotations

from itertools import combinations

F3 = (0, 1, 2)
NONEMPTY_LISTS = tuple(
    frozenset(values)
    for size in range(1, 4)
    for values in combinations(F3, size)
)


def scale(value: int, subset: frozenset[int]) -> frozenset[int]:
    return frozenset((value * x) % 3 for x in subset)


def classify(language: tuple[frozenset[int], ...]) -> str:
    has_doubleton = any(len(row_list) == 2 for row_list in language)
    if not has_doubleton:
        return "P1-linear"
    if all(0 in row_list for row_list in language):
        return "P2-zero"
    return "H-hard"


def main() -> None:
    assert len(NONEMPTY_LISTS) == 7

    counts = {"P1-linear": 0, "P2-zero": 0, "H-hard": 0}
    for mask in range(1, 1 << len(NONEMPTY_LISTS)):
        language = tuple(
            NONEMPTY_LISTS[index]
            for index in range(len(NONEMPTY_LISTS))
            if mask & (1 << index)
        )
        counts[classify(language)] += 1

    assert counts == {"P1-linear": 15, "P2-zero": 12, "H-hard": 100}

    # Variable-row normalization in hard case B:
    # t(a e_i) in {0,a} iff alpha_i in {0,1}.
    for a in (1, 2):
        assert {
            alpha for alpha in F3 if (a * alpha) % 3 in {0, a}
        } == {0, 1}

    # Clause-row normalization:
    # b*s=b iff s=1 for nonzero b.
    for b in (1, 2):
        assert {
            total for total in F3 if (b * total) % 3 == b
        } == {1}

    # Nonzero list is invariant under nonzero scaling.
    for a in (1, 2):
        assert scale(a, frozenset({1, 2})) == frozenset({1, 2})

    print("PASS: F3 fixed row-list language partition")
    print(counts)
    print("hardness scaling identities verified for both nonzero field elements")


if __name__ == "__main__":
    main()

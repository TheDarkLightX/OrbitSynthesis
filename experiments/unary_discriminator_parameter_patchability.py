#!/usr/bin/env python3
"""Exact finite campaign for QUASIPRIMAL_PARAMETER_PATCHABILITY.md.

Algebras are (D_n; discriminator, u) for every unary map u:D_n->D_n.
Since the discriminator is conservative, subalgebras are exactly the nonempty
u-invariant subsets. Internal isomorphisms are bijections commuting with u;
global automorphisms are permutations commuting with u.

By default the script exhausts n=4,5. Pass ``--include-six`` for the complete
6^6=46,656 map campaign; on the development machine this is intentionally the
expensive mode.
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations, permutations, product


def invariant_subsets(n: int, u: tuple[int, ...], constant_mask: int) -> tuple[int, ...]:
    out: list[int] = []
    for mask in range(1, 1 << n):
        if constant_mask & ~mask:
            continue
        if mask.bit_count() <= 1:
            continue
        if all(not (mask >> x & 1) or (mask >> u[x] & 1) for x in range(n)):
            out.append(mask)
    return tuple(out)


def automorphisms(
    n: int,
    u: tuple[int, ...],
    constant_mask: int,
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        p
        for p in permutations(range(n))
        if all(not (constant_mask >> c & 1) or p[c] == c for c in range(n))
        and all(p[u[x]] == u[p[x]] for x in range(n))
    )


def pointed_demi(
    n: int,
    u: tuple[int, ...],
    constants: tuple[int, ...],
) -> bool:
    constant_mask = sum(1 << c for c in constants)
    subalgebras = invariant_subsets(n, u, constant_mask)
    auts = automorphisms(n, u, constant_mask)

    restrictions: dict[int, set[tuple[int, ...]]] = {}
    by_size: dict[int, list[int]] = {}
    for source_mask in subalgebras:
        source = tuple(i for i in range(n) if source_mask >> i & 1)
        restrictions[source_mask] = {
            tuple(g[x] for x in source)
            for g in auts
        }
        by_size.setdefault(len(source), []).append(source_mask)

    for source_mask in subalgebras:
        source = tuple(i for i in range(n) if source_mask >> i & 1)
        source_index = {x: i for i, x in enumerate(source)}

        for target_mask in by_size[len(source)]:
            target = tuple(i for i in range(n) if target_mask >> i & 1)
            for image in permutations(target):
                if any(image[source_index[c]] != c for c in constants):
                    continue

                phi = dict(zip(source, image))
                if not all(phi[u[x]] == u[phi[x]] for x in source):
                    continue

                if tuple(image) not in restrictions[source_mask]:
                    return False

    return True


def patchability_number(n: int, u: tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    for size in range(n + 1):
        for constants in combinations(range(n), size):
            if pointed_demi(n, u, constants):
                return size, constants
    raise AssertionError("naming the whole carrier must be sufficient")


def classify_all(n: int) -> Counter[int]:
    counts: Counter[int] = Counter()
    for u in product(range(n), repeat=n):
        value, _ = patchability_number(n, u)
        counts[value] += 1
    return counts


def first_pi2_witness() -> tuple[int, ...]:
    n = 6
    for u in product(range(n), repeat=n):
        value, constants = patchability_number(n, u)
        if value == 2:
            assert u == (0, 0, 0, 3, 3, 5)
            assert constants == (0, 3)
            return u
    raise AssertionError("expected six-element witness")


def check_star_family_symbolically(max_components: int = 8) -> None:
    """Check the combinatorial parameters of the proved star family.

    We do not enumerate automorphisms of the larger carriers here. The note
    contains the proof that m pairwise-distinct rooted-star components require
    exactly m-1 anchors. This check only guards construction/count arithmetic.
    """

    for m in range(1, max_components + 1):
        component_sizes = tuple(range(1, m + 1))
        carrier_size = sum(component_sizes)
        expected = m * (m + 1) // 2
        assert carrier_size == expected
        assert len(set(component_sizes)) == m
        assert m - 1 <= carrier_size


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--include-six",
        action="store_true",
        help="also exhaust all 46,656 unary maps on six points",
    )
    args = parser.parse_args()

    expected = {
        4: Counter({0: 100, 1: 156}),
        5: Counter({0: 575, 1: 2550}),
    }

    for n in (4, 5):
        counts = classify_all(n)
        assert counts == expected[n]
        print(f"n={n}: {dict(sorted(counts.items()))}")

    if args.include_six:
        counts6 = classify_all(6)
        expected6 = Counter({0: 5526, 1: 38790, 2: 2340})
        assert counts6 == expected6
        print(f"n=6: {dict(sorted(counts6.items()))}")
        witness = first_pi2_witness()
        print(f"first pi=2 witness: {witness}")

    check_star_family_symbolically()
    print("PASS: unary discriminator parameter-patchability campaign")


if __name__ == "__main__":
    main()

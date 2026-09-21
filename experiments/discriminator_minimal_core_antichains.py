#!/usr/bin/env python3
"""Exact binary minimal-core-antichain classification for the 3-element discriminator."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path

Q = (0, 1, 2)
ROWS = tuple(product(Q, repeat=2))
ROW_INDEX = {row: index for index, row in enumerate(ROWS)}
CORES = tuple(
    frozenset(Q[index] for index in range(len(Q)) if mask & (1 << index))
    for mask in range(1 << len(Q))
)
NONEMPTY_SUBALGEBRAS = tuple(core for core in CORES if core)
PERMUTATIONS = tuple(permutations(Q))


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def internal_isomorphisms(core: frozenset[int]):
    result = []
    for source in NONEMPTY_SUBALGEBRAS:
        if not core <= source:
            continue
        source_order = tuple(sorted(source))
        for target in NONEMPTY_SUBALGEBRAS:
            if len(source) != len(target) or not core <= target:
                continue
            for image in permutations(sorted(target)):
                mapping = dict(zip(source_order, image, strict=True))
                if any(mapping[value] != value for value in core):
                    continue
                if all(
                    mapping[discriminator(x, y, z)]
                    == discriminator(mapping[x], mapping[y], mapping[z])
                    for x, y, z in product(source_order, repeat=3)
                ):
                    result.append((source, mapping))
    return tuple(result)


CONSTRAINTS = {
    core: tuple(
        (
            ROW_INDEX[row],
            ROW_INDEX[tuple(mapping[value] for value in row)],
            source,
            tuple(mapping.get(value, -1) for value in Q),
        )
        for source, mapping in internal_isomorphisms(core)
        for row in product(sorted(source), repeat=2)
    )
    for core in CORES
}


def preserves(core: frozenset[int], table: tuple[int, ...]) -> bool:
    return all(
        table[source_index] in source
        and table[target_index] == mapping[table[source_index]]
        for source_index, target_index, source, mapping in CONSTRAINTS[core]
    )


def family_key(family) -> tuple[tuple[int, ...], ...]:
    return tuple(
        sorted(
            (tuple(sorted(core)) for core in family),
            key=lambda values: (len(values), values),
        )
    )


def minimal_cores(table: tuple[int, ...]) -> tuple[frozenset[int], ...]:
    feasible = tuple(core for core in CORES if preserves(core, table))
    return tuple(
        core
        for core in feasible
        if not any(other < core for other in feasible)
    )


def all_antichains():
    for size in range(len(CORES) + 1):
        for family in combinations(CORES, size):
            if all(
                not (left < right or right < left)
                for index, left in enumerate(family)
                for right in family[index + 1 :]
            ):
                yield family


def permute_core(core: frozenset[int], permutation: tuple[int, ...]) -> frozenset[int]:
    return frozenset(permutation[value] for value in core)


def orbit_representative(key: tuple[tuple[int, ...], ...]):
    family = tuple(frozenset(values) for values in key)
    orbit = tuple(
        family_key(permute_core(core, permutation) for core in family)
        for permutation in PERMUTATIONS
    )
    return min(orbit, key=repr)


def matrix(table: tuple[int, ...]) -> list[list[int]]:
    return [list(table[offset : offset + len(Q)]) for offset in range(0, len(table), len(Q))]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-root", type=Path)
    args = parser.parse_args()

    frequencies: Counter[tuple[tuple[int, ...], ...]] = Counter()
    examples: dict[tuple[tuple[int, ...], ...], tuple[int, ...]] = {}
    singleton_clone_tables = {value: set() for value in Q}
    parameter_free_tables = set()

    for table in product(Q, repeat=len(ROWS)):
        key = family_key(minimal_cores(table))
        frequencies[key] += 1
        examples.setdefault(key, table)
        if preserves(frozenset(), table):
            parameter_free_tables.add(table)
        for value in Q:
            if preserves(frozenset({value}), table):
                singleton_clone_tables[value].add(table)

    all_nonempty = {
        family_key(family)
        for family in all_antichains()
        if family
    }
    realized = set(frequencies)
    missing = tuple(sorted(all_nonempty - realized, key=repr))
    expected_missing = {
        ((0,), (1,)),
        ((0,), (2,)),
        ((1,), (2,)),
        ((0,), (1,), (2,)),
    }
    assert set(missing) == expected_missing
    assert len(realized) == 15
    assert len(all_nonempty) == 19

    # The key structural obstruction: two distinct singleton languages overlap
    # exactly in the parameter-free term clone.
    singleton_intersections = {}
    for left, right in combinations(Q, 2):
        intersection = singleton_clone_tables[left] & singleton_clone_tables[right]
        assert intersection == parameter_free_tables
        singleton_intersections[f"{left},{right}"] = len(intersection)
    assert len(parameter_free_tables) == 2

    orbit_members: dict[tuple[tuple[int, ...], ...], set[tuple[tuple[int, ...], ...]]] = defaultdict(set)
    for key in all_nonempty:
        orbit_members[orbit_representative(key)].add(key)
    realized_orbits = {
        representative
        for representative, members in orbit_members.items()
        if members & realized
    }
    missing_orbits = {
        representative
        for representative, members in orbit_members.items()
        if members <= set(missing)
    }
    assert len(orbit_members) == 9
    assert len(realized_orbits) == 7
    assert missing_orbits == {
        ((0,), (1,)),
        ((0,), (1,), (2,)),
    }

    orbit_rows = []
    for representative, members in sorted(orbit_members.items(), key=lambda item: repr(item[0])):
        realized_members = members & realized
        orbit_rows.append(
            {
                "representative": [list(values) for values in representative],
                "orbit_size": len(members),
                "realized": bool(realized_members),
                "table_count": sum(frequencies[key] for key in realized_members),
                "example_matrix": (
                    matrix(examples[min(realized_members, key=repr)])
                    if realized_members
                    else None
                ),
            }
        )

    exact_family_rows = [
        {
            "minimal_cores": [list(values) for values in key],
            "count": count,
            "example_matrix": matrix(examples[key]),
        }
        for key, count in sorted(frequencies.items(), key=lambda item: repr(item[0]))
    ]

    semantic = {
        "schema": "orbit-synthesis/discriminator-minimal-core-antichains/v1",
        "carrier_size": 3,
        "arity": 2,
        "table_count": 3**9,
        "nonempty_antichain_count": len(all_nonempty),
        "realized_antichain_count": len(realized),
        "missing_antichains": [[list(values) for values in key] for key in missing],
        "symmetry_orbit_count": len(orbit_members),
        "realized_orbit_count": len(realized_orbits),
        "missing_orbit_representatives": [
            [list(values) for values in key]
            for key in sorted(missing_orbits, key=repr)
        ],
        "singleton_clone_pair_intersections": singleton_intersections,
        "parameter_free_binary_table_count": len(parameter_free_tables),
        "orbit_rows": orbit_rows,
        "exact_family_rows": exact_family_rows,
        "candidate_statuses": {
            "all_nonempty_antichains_realizable": "FAILED",
            "multiple_minimal_cores_impossible": "FAILED",
            "no_two_distinct_singletons": "DERIVED_AND_EXHAUSTIVELY_CHECKED",
            "seven_of_nine_symmetry_types_realizable": "TESTED_ONLY",
        },
    }
    semantic["semantic_sha256"] = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    if args.out_root:
        args.out_root.mkdir(parents=True, exist_ok=True)
        (args.out_root / "summary.json").write_text(
            json.dumps(semantic, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(semantic, sort_keys=True))


if __name__ == "__main__":
    main()

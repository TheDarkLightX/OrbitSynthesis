#!/usr/bin/env python3
"""Construct and exhaustively validate pure-discriminator minimal-core families."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.discriminator_core_family import (
    all_subsets,
    family_size_distribution,
    foreign_output_core,
    is_pairwise_cover_antichain,
    minimal_parameter_cores,
    pairwise_cover_families,
    realizable_family_count,
    realize_minimal_core_family,
)


def all_antichains(size: int):
    carrier = tuple(range(size))
    cores = all_subsets(carrier)
    result = []
    for mask in range(1, 1 << len(cores)):
        family = tuple(
            core for index, core in enumerate(cores) if mask & (1 << index)
        )
        if not any(
            left < right or right < left
            for left, right in combinations(family, 2)
        ):
            result.append(family)
    return tuple(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exact-max-carrier", type=int, default=6)
    parser.add_argument("--out-root", type=Path)
    args = parser.parse_args()
    if args.exact_max_carrier < 2:
        raise ValueError("exact-max-carrier must be at least two")

    enumeration = {}
    for size in range(1, min(args.exact_max_carrier, 4) + 1):
        antichains = all_antichains(size)
        cover = tuple(
            family for family in antichains
            if is_pairwise_cover_antichain(tuple(range(size)), family)
        )
        expected = 2 if size == 1 else realizable_family_count(size)
        assert len(cover) == expected
        enumeration[str(size)] = {
            "nonempty_antichains": len(antichains),
            "pairwise_cover_antichains": len(cover),
        }

    exact_families = 0
    exact_core_queries = 0
    family_mismatches = []
    foreign_core_mismatches = []
    per_size = {}
    for size in range(2, args.exact_max_carrier + 1):
        carrier = tuple(range(size))
        families = pairwise_cover_families(carrier)
        assert len(set(families)) == len(families)
        assert len(families) == realizable_family_count(size)
        observed_distribution = {}
        for family in families:
            observed_distribution[len(family)] = (
                observed_distribution.get(len(family), 0) + 1
            )
            realization = realize_minimal_core_family(carrier, family)
            minimal = minimal_parameter_cores(carrier, realization.table)
            exact_families += 1
            exact_core_queries += 1 << size
            if set(minimal) != set(realization.family):
                family_mismatches.append((size, realization.family, minimal))
            if foreign_output_core(carrier, realization.table) != realization.common_core:
                foreign_core_mismatches.append((size, realization.family))
        expected_distribution = family_size_distribution(size)
        assert observed_distribution == expected_distribution
        per_size[str(size)] = {
            "realizable_families": len(families),
            "family_size_distribution": {
                str(key): value for key, value in expected_distribution.items()
            },
        }

    singleton_carrier = (0,)
    singleton_empty = realize_minimal_core_family(singleton_carrier, (frozenset(),))
    assert minimal_parameter_cores(singleton_carrier, singleton_empty.table) == (
        frozenset(),
    )
    singleton_full_rejected = False
    try:
        realize_minimal_core_family(singleton_carrier, (frozenset({0}),))
    except ValueError:
        singleton_full_rejected = True
    assert singleton_full_rejected

    assert not family_mismatches
    assert not foreign_core_mismatches
    semantic = {
        "exact_max_carrier": args.exact_max_carrier,
        "exact_family_count": exact_families,
        "exact_core_membership_queries": exact_core_queries,
        "family_mismatch_count": len(family_mismatches),
        "foreign_core_mismatch_count": len(foreign_core_mismatches),
        "singleton_full_core_rejected": singleton_full_rejected,
        "enumerated_antichains": enumeration,
        "per_carrier": per_size,
        "count_sequence_1_through_8": {
            str(size): realizable_family_count(size)
            for size in range(1, 9)
        },
    }
    receipt = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    report = {
        "schema": "orbit-synthesis/zag-discriminator-core-family-realizability/v1",
        "candidate_statuses": {
            "pairwise_cover_is_sufficient_for_carrier_at_least_two": "TESTED_ONLY",
            "binary_arity_is_insufficient": "FAILED",
            "one_element_full_core_is_realizable": "FAILED",
            "count_formula": "TESTED_ONLY",
        },
        **semantic,
        "semantic_sha256": receipt,
    }
    if args.out_root:
        args.out_root.mkdir(parents=True, exist_ok=True)
        (args.out_root / "summary.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()

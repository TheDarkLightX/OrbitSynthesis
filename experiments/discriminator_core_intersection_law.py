#!/usr/bin/env python3
"""Exact ZAG campaign for the pure-discriminator core-intersection law."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from discriminator_core_census import d3_census
from orbitsynthesis.discriminator_core import (
    core_intersection_collapses,
    cover_intersection_witness,
    incomparable_cover_profile,
    is_parameter_polynomial_table,
)
from orbitsynthesis.discriminator_orbits import (
    cover_orbit_product_count,
    enumerate_polynomial_tables,
    subsets,
    transposition_graph_connected,
)


def pair_campaign(max_carrier: int):
    counts = Counter()
    profiles: set[tuple[int, int, int]] = set()
    for m in range(2, max_carrier + 1):
        carrier = tuple(range(m))
        for left in subsets(m):
            for right in subsets(m):
                counts["pairs"] += 1
                collapse = core_intersection_collapses(carrier, left, right)
                counts["graph_mismatches"] += int(
                    collapse != transposition_graph_connected(m, left, right)
                )
                if collapse:
                    counts["collapse"] += 1
                    continue
                counts["covers"] += 1
                profile = incomparable_cover_profile(carrier, left, right)
                profiles.add((len(profile.meet), len(profile.left_only), len(profile.right_only)))
                witness = cover_intersection_witness(carrier, left, right)
                counts["witness_failures"] += int(
                    not is_parameter_polynomial_table(carrier, left, 2, witness)
                )
                counts["witness_failures"] += int(
                    not is_parameter_polynomial_table(carrier, right, 2, witness)
                )
                counts["witness_failures"] += int(
                    is_parameter_polynomial_table(carrier, left & right, 2, witness)
                )
    count_failures = 0
    for e, x, y in profiles:
        profile = incomparable_cover_profile(
            tuple(range(e + x + y)),
            frozenset(range(e + x)),
            frozenset(range(e)) | frozenset(range(e + x, e + x + y)),
        )
        count_failures += int(
            cover_orbit_product_count(e, x, y) != profile.binary_operation_count
        )
    return counts, profiles, count_failures


def exact_table_checks(max_carrier: int) -> dict[str, int]:
    checks = {}
    for m in range(3, min(max_carrier, 7) + 1):
        base = enumerate_polynomial_tables(m, 2, frozenset())
        singles = {
            a: enumerate_polynomial_tables(m, 2, frozenset({a}))
            for a in range(m)
        }
        assert all(singles[a] & singles[b] == base for a, b in combinations(range(m), 2))
        checks[f"D{m}_singleton_pair_intersection"] = len(base)
    return checks


def exceptional_counts() -> dict[str, int]:
    d4_left = enumerate_polynomial_tables(4, 2, frozenset({0, 1}))
    d4_overlap = enumerate_polynomial_tables(4, 2, frozenset({1, 2}))
    d4_meet = enumerate_polynomial_tables(4, 2, frozenset({1}))
    assert d4_left & d4_overlap == d4_meet
    d4_cover = d4_left & enumerate_polynomial_tables(4, 2, frozenset({2, 3}))
    d4_empty = enumerate_polynomial_tables(4, 2, frozenset())
    d3_cover = (
        enumerate_polynomial_tables(3, 2, frozenset({0, 1}))
        & enumerate_polynomial_tables(3, 2, frozenset({0, 2}))
    )
    d3_meet = enumerate_polynomial_tables(3, 2, frozenset({0}))
    assert len(d4_cover) == 16 and len(d3_cover) == 576
    return {
        "D4_noncover_intersection": len(d4_meet),
        "D4_disjoint_cover_intersection": len(d4_cover),
        "D4_disjoint_cover_extra_over_meet": len(d4_cover - d4_empty),
        "D3_cover_intersection": len(d3_cover),
        "D3_cover_extra_over_meet": len(d3_cover - d3_meet),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-carrier", type=int, default=8)
    parser.add_argument("--out-root", type=Path)
    args = parser.parse_args()
    if args.max_carrier < 4:
        raise ValueError("max-carrier must be at least four")

    counts, profiles, formula_failures = pair_campaign(args.max_carrier)
    assert counts["graph_mismatches"] == 0
    assert counts["witness_failures"] == 0
    assert formula_failures == 0
    semantic = {
        "pair_count": counts["pairs"],
        "collapse_pair_count": counts["collapse"],
        "incomparable_cover_pair_count": counts["covers"],
        "graph_mismatches": counts["graph_mismatches"],
        "witness_failures": counts["witness_failures"],
        "count_formula_failures": formula_failures,
        "cover_profile_count": len(profiles),
        "exact_checks": exact_table_checks(args.max_carrier),
        **exceptional_counts(),
        "D3_census": d3_census(),
        "maximum_minimal_family_bound_at_max_carrier": args.max_carrier,
    }
    receipt = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    report = {
        "schema": "orbit-synthesis/zag-discriminator-core-intersection/v1",
        "candidate_statuses": {
            "collapse_for_every_core_pair": "FAILED",
            "collapse_except_incomparable_full_covers": "TESTED_ONLY",
            "cover_block_intersection_count": "TESTED_ONLY",
            "minimum_core_multiplicity_exceeds_carrier": "FAILED",
            "all_pairwise_cover_families_are_realizable": "UNDER_TEST",
        },
        **semantic,
        "semantic_sha256": receipt,
    }
    if args.out_root:
        args.out_root.mkdir(parents=True, exist_ok=True)
        (args.out_root / "summary.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()

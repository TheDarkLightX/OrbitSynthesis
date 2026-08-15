#!/usr/bin/env python3
"""Exact three-element audit for role-orbit converse compression."""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import compile_quasi_primal_domain_model
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.generator_compressed_witness import (
    build_generator_compressed_principal_no_greatest_region_witness,
)
from orbitsynthesis.role_orbit_witness import (
    audit_role_orbit_principal_no_greatest_region_witness,
    build_role_orbit_principal_no_greatest_region_witness,
)

Q = (0, 1, 2)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def algebra_for(table: tuple[int, int, int] | None) -> FiniteAlgebra:
    operations = {"d": (3, discriminator)}
    if table is not None:
        operations["u"] = (1, lambda value, table=table: table[value])
    return FiniteAlgebra.from_callables(Q, operations)


def model_census(witness, algebra: FiniteAlgebra) -> dict[str, int]:
    model = compile_quasi_primal_domain_model(witness.game(algebra))
    encoding = model.cnf()
    return {
        "states": len(model.states),
        "observations": len(model.observations),
        "components": len(model.components),
        "candidate_rules": sum(
            len(component.candidates) for component in model.components
        ),
        "variables": encoding.variable_count,
        "hard_clauses": len(encoding.clauses),
    }


def add_census(total: Counter, row: dict[str, int]) -> None:
    for key, value in row.items():
        total[key] += value


def make_receipt() -> dict[str, object]:
    require(
        build_role_orbit_principal_no_greatest_region_witness(
            algebra_for(None)
        ) is None,
        "pure discriminator should be the demi-semi-primal negative control",
    )

    counts = Counter()
    classifications = []
    flattened_rows = 0
    strict = 0
    generator_total: Counter = Counter()
    role_total: Counter = Counter()
    q_checkpoint = None

    for table in itertools.product(Q, repeat=3):
        algebra = algebra_for(table)
        isomorphisms = algebra.internal_isomorphisms()
        witness = build_role_orbit_principal_no_greatest_region_witness(
            algebra,
            internal_isomorphisms=isomorphisms,
        )
        if witness is None:
            counts["demi"] += 1
            classifications.append([list(table), True, None])
            continue

        audit = audit_role_orbit_principal_no_greatest_region_witness(
            algebra,
            witness,
            internal_isomorphisms=isomorphisms,
        )
        require(audit.passes, "role-orbit principal audit failed")
        counts["non_demi"] += 1
        counts[f"rank_{audit.compression_audit.role_rank}"] += 1
        flattened_rows += audit.rows_checked

        generator = build_generator_compressed_principal_no_greatest_region_witness(
            algebra,
            internal_isomorphisms=isomorphisms,
        )
        require(generator is not None, "generator-tag baseline disappeared")
        generator_model = model_census(generator, algebra)
        role_model = model_census(witness, algebra)
        add_census(generator_total, generator_model)
        add_census(role_total, role_model)

        upper = audit.compression_audit.generator_tag_upper_bound
        role_rank = audit.compression_audit.role_rank
        if role_rank < upper:
            strict += 1
        classifications.append(
            [
                list(table),
                False,
                role_rank,
                upper,
                list(audit.compression_audit.generating_orbit_counts),
                role_model["candidate_rules"],
            ]
        )

        if table == (1, 0, 1):
            q_checkpoint = {
                "role_rank": role_rank,
                "generator_tag_upper_bound": upper,
                "generating_orbit_counts": list(
                    audit.compression_audit.generating_orbit_counts
                ),
                "available_rank_three_orbits": len(
                    witness.structural.source_state
                    and __import__(
                        "orbitsynthesis.role_orbit_witness",
                        fromlist=["generating_tuple_orbit_representatives"],
                    ).generating_tuple_orbit_representatives(
                        algebra,
                        witness.structural.isomorphism.domain,
                        role_rank,
                        internal_isomorphisms=isomorphisms,
                    )
                ),
                "roles": [
                    list(witness.structural.source_state),
                    list(witness.structural.source_output_zero),
                    list(witness.structural.source_output_one),
                ],
                "principal_rows": audit.rows_checked,
                "unsafe_rows": audit.unsafe_rows,
                "unsafe_groupoid_orbits": audit.unsafe_groupoid_orbits,
                "safe_rows": audit.rows_checked - audit.unsafe_rows,
                "domain_model": role_model,
            }

    require((counts["demi"], counts["non_demi"]) == (15, 12), "extension census")
    require(counts["rank_3"] == 12, "role-rank distribution")
    require(strict == 6, "strict generator-tag improvement count")
    require(flattened_rows == 26244, "flattened row census")
    require(q_checkpoint is not None, "missing Quackenbush-Q checkpoint")

    expected_generator = {
        "states": 648,
        "observations": 1944,
        "components": 1800,
        "candidate_rules": 101436,
        "variables": 102084,
        "hard_clauses": 103062,
    }
    expected_role = {
        "states": 324,
        "observations": 972,
        "components": 876,
        "candidate_rules": 19392,
        "variables": 19716,
        "hard_clauses": 20010,
    }
    require(dict(generator_total) == expected_generator, "generator model census")
    require(dict(role_total) == expected_role, "role-orbit model census")

    result = {
        "schema": "orbit-synthesis/role-orbit-rank-converse/v1",
        "theorem": (
            "a graph-maximal nonextendable internal isomorphism yields a "
            "one-equation no-greatest witness at its three-role orbit rank"
        ),
        "demi": counts["demi"],
        "non_demi": counts["non_demi"],
        "role_rank_distribution": {"3": counts["rank_3"]},
        "strict_improvements_over_generator_tags": strict,
        "flattened_rows_checked": flattened_rows,
        "generator_compressed_flattened_rows": 131220,
        "full_listing_flattened_rows": 236196,
        "aggregate_domain_models": {
            "generator_tags": expected_generator,
            "role_orbits": expected_role,
        },
        "classifications": classifications,
        "quackenbush_q": q_checkpoint,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    result = make_receipt()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

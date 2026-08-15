#!/usr/bin/env python3
"""Primary audit for the generator-compressed greatest-region converse."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.domain_model import compile_quasi_primal_domain_model
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.generator_compressed_witness import (
    audit_generator_compressed_no_greatest_region_witness,
    audit_generator_compressed_principal_no_greatest_region_witness,
    build_generator_compressed_no_greatest_region_witness,
    build_generator_compressed_principal_no_greatest_region_witness,
)
from orbitsynthesis.greatest_region_boundary import (
    build_no_greatest_region_witness,
)
from orbitsynthesis.principal_greatest_region import (
    build_principal_no_greatest_region_witness,
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


def model_census(model) -> dict[str, int]:
    encoding = model.cnf()
    return {
        "states": len(model.states),
        "observations": len(model.observations),
        "components": len(model.components),
        "candidate_rules": sum(
            len(component.candidates) for component in model.components
        ),
        "variables": encoding.variable_count,
        "clauses": len(encoding.clauses),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_receipt() -> dict[str, object]:
    pure = algebra_for(None)
    require(
        build_generator_compressed_no_greatest_region_witness(pure) is None,
        "pure discriminator should satisfy the extension property",
    )
    require(
        build_generator_compressed_principal_no_greatest_region_witness(pure)
        is None,
        "pure discriminator should have no principal converse witness",
    )

    counts: Counter[int] = Counter()
    classifications = []
    demi = non_demi = strict_reductions = 0
    flattened_rows = baseline_flattened_rows = 0
    q_checkpoint = None

    for table in itertools.product(Q, repeat=3):
        algebra = algebra_for(table)
        isomorphisms = algebra.internal_isomorphisms()
        baseline = build_no_greatest_region_witness(
            algebra,
            internal_isomorphisms=isomorphisms,
        )
        compressed = build_generator_compressed_no_greatest_region_witness(
            algebra,
            internal_isomorphisms=isomorphisms,
        )
        principal = (
            build_generator_compressed_principal_no_greatest_region_witness(
                algebra,
                internal_isomorphisms=isomorphisms,
            )
        )

        if baseline is None:
            require(compressed is None and principal is None, "classification drift")
            demi += 1
            classifications.append([list(table), True, None])
            continue

        require(compressed is not None and principal is not None, "missing witness")
        non_demi += 1
        structural_audit = audit_generator_compressed_no_greatest_region_witness(
            algebra,
            compressed,
            internal_isomorphisms=isomorphisms,
        )
        principal_audit = (
            audit_generator_compressed_principal_no_greatest_region_witness(
                algebra,
                principal,
                internal_isomorphisms=isomorphisms,
            )
        )
        require(structural_audit.passes, "compressed structural audit failed")
        require(principal_audit.passes, "compressed principal audit failed")
        require(
            compressed.state_arity <= baseline.state_arity,
            "generator compression increased state arity",
        )

        counts[compressed.state_arity] += 1
        strict_reductions += int(compressed.state_arity < baseline.state_arity)
        flattened_rows += principal_audit.rows_checked
        baseline_flattened_rows += len(Q) ** (2 * baseline.state_arity + 1)
        classifications.append(
            [
                list(table),
                False,
                compressed.state_arity,
                list(structural_audit.generator_prefix),
            ]
        )

        if table == (1, 0, 1):
            baseline_principal = build_principal_no_greatest_region_witness(
                algebra,
                internal_isomorphisms=isomorphisms,
            )
            require(baseline_principal is not None, "missing baseline Q witness")
            compressed_model = compile_quasi_primal_domain_model(
                principal.game(algebra),
                internal_isomorphisms=isomorphisms,
            )
            baseline_model = compile_quasi_primal_domain_model(
                baseline_principal.game(algebra),
                internal_isomorphisms=isomorphisms,
            )
            compressed_census = model_census(compressed_model)
            baseline_census = model_census(baseline_model)
            require(
                compressed_census
                == {
                    "states": 27,
                    "observations": 81,
                    "components": 73,
                    "candidate_rules": 1762,
                    "variables": 1789,
                    "clauses": 1817,
                },
                "compressed Q model census drift",
            )
            require(
                baseline_census
                == {
                    "states": 81,
                    "observations": 243,
                    "components": 227,
                    "candidate_rules": 17174,
                    "variables": 17255,
                    "clauses": 17405,
                },
                "baseline Q model census drift",
            )
            require(
                not principal_audit.single_global_alternate_exists,
                "Q unexpectedly admits one global alternate projection",
            )
            q_checkpoint = {
                "generator_prefix": list(structural_audit.generator_prefix),
                "state_arity": compressed.state_arity,
                "baseline_state_arity": baseline.state_arity,
                "principal_rows": principal_audit.rows_checked,
                "principal_safe_transitions": len(principal.safe_relation),
                "principal_unsafe_rows": principal_audit.unsafe_rows,
                "unsafe_groupoid_orbits": principal_audit.unsafe_orbits,
                "single_global_alternate_exists": (
                    principal_audit.single_global_alternate_exists
                ),
                "compressed_model": compressed_census,
                "baseline_model": baseline_census,
            }

    require((demi, non_demi) == (15, 12), "extension-property census drift")
    require(dict(counts) == {3: 6, 4: 6}, "compressed arity distribution drift")
    require(strict_reductions == 6, "strict compression census drift")
    require(flattened_rows == 131220, "compressed flattened-row census drift")
    require(
        baseline_flattened_rows == 236196,
        "baseline flattened-row census drift",
    )
    require(q_checkpoint is not None, "missing Quackenbush-Q checkpoint")

    source_paths = {
        "generator_compressed_witness.py": (
            ROOT / "src/orbitsynthesis/generator_compressed_witness.py"
        ),
        "check_generator_compression.py": Path(__file__).resolve(),
    }
    result = {
        "schema": "orbit-synthesis/generator-compressed-converse/v1",
        "theorem": (
            "a graph-maximal nonextendable internal isomorphism with source "
            "generating rank d yields a one-equation no-greatest witness of "
            "state arity d+2"
        ),
        "demi": demi,
        "non_demi": non_demi,
        "arity_distribution": {str(key): value for key, value in sorted(counts.items())},
        "strict_arity_reductions": strict_reductions,
        "flattened_rows_checked": flattened_rows,
        "baseline_flattened_rows": baseline_flattened_rows,
        "classifications": classifications,
        "quackenbush_q": q_checkpoint,
        "source_sha256": {
            label: sha256(path) for label, path in source_paths.items()
        },
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

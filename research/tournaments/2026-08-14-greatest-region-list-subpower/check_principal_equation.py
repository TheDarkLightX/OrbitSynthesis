#!/usr/bin/env python3
"""Exhaust the one-equation greatest-region converse on 3-element expansions."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.principal_greatest_region import (
    audit_principal_no_greatest_region_witness,
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


def make_receipt() -> dict[str, object]:
    require(
        build_principal_no_greatest_region_witness(algebra_for(None)) is None,
        "pure discriminator should be the extendable negative control",
    )

    classifications = []
    demi = non_demi = 0
    rows_checked = 0
    q_checkpoint = None

    for table in itertools.product(Q, repeat=3):
        algebra = algebra_for(table)
        isomorphisms = algebra.internal_isomorphisms()
        witness = build_principal_no_greatest_region_witness(
            algebra,
            internal_isomorphisms=isomorphisms,
        )
        if witness is None:
            demi += 1
            classifications.append([list(table), True])
            continue

        audit = audit_principal_no_greatest_region_witness(
            algebra,
            witness,
            internal_isomorphisms=isomorphisms,
        )
        require(audit.passes, "principal-equation converse failed")
        non_demi += 1
        rows_checked += audit.rows_checked
        classifications.append([list(table), False])

        if table == (1, 0, 1):
            # Effective mutation: replacing the unsafe branch by the first
            # projection makes p=g on an actually unsafe transition.
            unsafe = next(
                row
                for row in itertools.product(
                    algebra.values,
                    repeat=2 * witness.state_arity + 1,
                )
                if row not in witness.flattened
            )
            require(unsafe[0] != unsafe[1], "unsafe tag collision")
            mutated_separator = unsafe[0]
            require(
                witness.projection_value(unsafe) == mutated_separator,
                "equation mutation did not accept the unsafe tuple",
            )
            q_checkpoint = {
                "state_arity": witness.state_arity,
                "safe_transition_count": len(witness.safe_relation),
                "rows_checked": audit.rows_checked,
                "left_feasible": audit.left_feasible,
                "right_feasible": audit.right_feasible,
                "union_feasible": audit.union_feasible,
                "exact_equation": audit.exact_equation,
                "separator_subalgebra_preserving": (
                    audit.separator_subalgebra_preserving
                ),
                "separator_groupoid_equivariant": (
                    audit.separator_groupoid_equivariant
                ),
                "mutation_unsafe_tuple": list(unsafe),
            }

    require((demi, non_demi) == (15, 12), "extension census drift")
    require(q_checkpoint is not None, "missing Quackenbush-Q checkpoint")

    result = {
        "schema": "orbit-synthesis/principal-greatest-region/v1",
        "theorem": (
            "demi-semi-primal iff every one-equation shared-term safety "
            "instance has a greatest winning domain"
        ),
        "demi_semi_primal_count": demi,
        "non_demi_semi_primal_count": non_demi,
        "flattened_rows_checked": rows_checked,
        "classifications": classifications,
        "quackenbush_q": q_checkpoint,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    output = None
    arguments = iter(sys.argv[1:])
    for argument in arguments:
        if argument == "--out":
            output = Path(next(arguments))
        else:
            raise SystemExit(argument)
    result = make_receipt()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if output is not None:
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent fail-closed audit of the order-pair integrated compiler bridge."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from fractions import Fraction
from itertools import product
from pathlib import Path

from compiler_bridge_model import (
    DAG,
    Q,
    binary_depth_upper,
    binary_node_upper,
    build_order_pair_vector,
    clog2,
    compile_integrated_small,
    compiler_parameters,
    nonbinary_depth_upper,
    nonbinary_node_upper,
    order_pair_vector_nodes,
    require,
    total_depth_upper,
    total_node_upper,
)


def expected_pair(
    target: tuple[int, ...],
    physical: tuple[int, ...],
    root_negative: bool,
) -> tuple[int, int]:
    equal = target == physical
    gain = False
    if not equal:
        for target_digit, physical_digit in zip(target, physical, strict=True):
            if target_digit != physical_digit:
                gain = target_digit == 1 and physical_digit == 2
                break
    loss = not equal and not gain
    negative = root_negative ^ bool(sum(digit == 1 for digit in physical) & 1)
    return (int(gain), int(equal or gain)) if negative else (int(loss), int(gain))


def check_order_pair_component() -> dict[str, object]:
    semantic_checks = 0
    rows = []
    for width in range(1, 6):
        words = tuple(product(Q, repeat=width))
        for root_negative in (False, True):
            dag = DAG(width)
            anchor = dag.var(("A",))
            one = dag.unary(anchor)
            zero = dag.unary(one)
            outputs = build_order_pair_vector(
                dag,
                dag.variables,
                anchor=anchor,
                zero=zero,
                root_negative=root_negative,
            )
            roots = [root for pair in outputs.values() for root in pair]
            actual_nodes = len(dag.reachable(roots))
            actual_depth = max(dag.depth(root) for root in roots)
            require(
                actual_nodes == order_pair_vector_nodes(width, root_negative),
                f"order-pair node recurrence drift at width={width}",
            )
            require(
                actual_depth <= 3 + clog2(width),
                f"order-pair depth drift at width={width}",
            )
            for target in words:
                for physical, pair in outputs.items():
                    actual = tuple(
                        dag.evaluate(root, target, extra_inputs={anchor: 2})
                        for root in pair
                    )
                    require(
                        actual == expected_pair(target, physical, root_negative),
                        "order-pair semantic mismatch",
                    )
                    semantic_checks += 1
            rows.append(
                {
                    "width": width,
                    "root": "negative" if root_negative else "positive",
                    "nodes": actual_nodes,
                    "depth": actual_depth,
                }
            )
    return {"semantic_checks": semantic_checks, "exact_rows": rows}


def all_arity_two_selectors():
    binary_representatives = ((0, 0), (0, 1))
    nonbinary = tuple(point for point in product(Q, repeat=2) if 2 in point)
    for choices in product(range(2), repeat=2 + len(nonbinary)):
        selector: dict[tuple[int, ...], int] = {}
        for representative, index in zip(
            binary_representatives, choices[:2], strict=True
        ):
            complement = tuple(1 - value for value in representative)
            selector[representative] = index
            selector[complement] = index
        for point, index in zip(nonbinary, choices[2:], strict=True):
            selector[point] = index
        yield selector


def random_selector(arity: int, seed: int) -> dict[tuple[int, ...], int]:
    rng = random.Random(seed)
    selector: dict[tuple[int, ...], int] = {}
    for point in product(Q, repeat=arity):
        if all(value in (0, 1) for value in point):
            complement = tuple(1 - value for value in point)
            if complement in selector:
                selector[point] = selector[complement]
            else:
                index = rng.randrange(arity)
                selector[point] = index
                selector[complement] = index
        else:
            selector[point] = rng.randrange(arity)
    return selector


def check_integrated_semantics() -> dict[str, object]:
    selector_tables = 0
    row_checks = 0
    maximum_nodes = 0
    maximum_depth = 0

    for selector in all_arity_two_selectors():
        dag, build = compile_integrated_small(2, selector, local_width=1)
        for point in product(Q, repeat=2):
            require(
                dag.evaluate(build.root, point) == point[selector[point]],
                "arity-two integrated semantic mismatch",
            )
            row_checks += 1
        selector_tables += 1
        maximum_nodes = max(maximum_nodes, len(dag.reachable([build.root])))
        maximum_depth = max(maximum_depth, dag.depth(build.root))

    for seed in range(32):
        selector = random_selector(3, seed)
        dag, build = compile_integrated_small(3, selector, local_width=1)
        for point in product(Q, repeat=3):
            require(
                dag.evaluate(build.root, point) == point[selector[point]],
                "arity-three integrated semantic mismatch",
            )
            row_checks += 1
        selector_tables += 1
        maximum_nodes = max(maximum_nodes, len(dag.reachable([build.root])))
        maximum_depth = max(maximum_depth, dag.depth(build.root))

    return {
        "selector_tables": selector_tables,
        "row_checks": row_checks,
        "maximum_materialized_nodes": maximum_nodes,
        "maximum_materialized_depth": maximum_depth,
        "arities": [2, 3],
    }


def check_large_arity_ledger() -> dict[str, object]:
    checks = 0
    worst_total = (Fraction(0), 0)
    worst_nonbinary = (Fraction(0), 0)
    minimum_depth_slack = None
    stronger_constant = True

    for arity in range(64, 16385):
        ell, headroom, local, local_width, prefix, prefix_width = (
            compiler_parameters(arity)
        )
        local_vector = order_pair_vector_nodes(local_width, False)
        prefix_vector = order_pair_vector_nodes(prefix_width, False)
        require(2 * local_vector <= 5 * local - 1, "local vector bound")
        require(2 * prefix_vector <= 5 * prefix - 1, "prefix vector bound")
        require(local <= headroom < 3 * local, "local power bracketing")
        require(local * prefix == 3**arity, "local/prefix product")
        require(8 * ell <= arity, "log reserve bound")
        require(16 * headroom >= 13 * arity, "headroom lower bound")
        require(48 * local > 13 * arity, "local assignment lower bound")

        nonbinary = nonbinary_node_upper(arity)
        binary = binary_node_upper(arity)
        total = nonbinary + binary
        require(total * arity < 34 * 3**arity, "34-constant theorem")
        require(
            total_depth_upper(arity) <= arity + 4 * clog2(arity) + 9,
            "depth theorem",
        )
        require(
            nonbinary_depth_upper(arity) <= arity + 4 * clog2(arity) + 9,
            "nonbinary depth theorem",
        )
        require(
            binary_depth_upper(arity) + 2 <= arity + 4 * clog2(arity) + 9,
            "binary depth theorem",
        )

        total_ratio = Fraction(total * arity, 3**arity)
        nonbinary_ratio = Fraction(nonbinary * arity, 3**arity)
        if total_ratio > worst_total[0]:
            worst_total = (total_ratio, arity)
        if nonbinary_ratio > worst_nonbinary[0]:
            worst_nonbinary = (nonbinary_ratio, arity)
        slack = arity + 4 * clog2(arity) + 9 - total_depth_upper(arity)
        minimum_depth_slack = slack if minimum_depth_slack is None else min(
            minimum_depth_slack, slack
        )
        stronger_constant &= total * arity < 16 * 3**arity
        checks += 14

    return {
        "arities": [64, 16384],
        "checks": checks,
        "proved_constant": "<34*3^r/r",
        "depth": "<=r+4*ceil(log2 r)+9",
        "worst_total_arity": worst_total[1],
        "worst_total_decimal": format(float(worst_total[0]), ".15f"),
        "worst_nonbinary_arity": worst_nonbinary[1],
        "worst_nonbinary_decimal": format(float(worst_nonbinary[0]), ".15f"),
        "minimum_depth_slack": minimum_depth_slack,
        "bounded_stronger_constant_16": stronger_constant,
    }


def check_mutations() -> dict[str, object]:
    # Recompiling the prefix vector for every physical branch changes a shared
    # O(P) object into an O(P^2) object.
    arity = 64
    _, _, local, local_width, prefix, prefix_width = compiler_parameters(arity)
    duplicated_prefix_vector = (
        (3 * local - 1) * 3**local
        + order_pair_vector_nodes(local_width, False)
        + (3 * prefix - 1)
        + order_pair_vector_nodes(prefix_width, False) * prefix
        + 4 * arity
        + 3
        + binary_node_upper(arity)
    )
    require(
        duplicated_prefix_vector * arity > 34 * 3**arity,
        "prefix-vector duplication mutation did not break the theorem",
    )

    # Serializing the two Boolean planes repeats the entire routing dependency.
    serial_depth = 2 * (local_width + 1 + prefix_width + 1) + 3 * clog2(arity) + 9
    require(
        serial_depth > arity + 4 * clog2(arity) + 9,
        "serialized-plane mutation did not break the depth target",
    )

    # Removing complement invariance must be rejected before construction.
    bad_selector = {point: 0 for point in product(Q, repeat=2)}
    bad_selector[(1, 1)] = 1
    rejected = False
    try:
        compile_integrated_small(2, bad_selector, local_width=1)
    except AssertionError:
        rejected = True
    require(rejected, "non-equivariant binary selector was accepted")

    return {
        "duplicated_prefix_vector": {
            "witness_arity": arity,
            "normalized_decimal": format(
                float(Fraction(duplicated_prefix_vector * arity, 3**arity)),
                ".6e",
            ),
        },
        "serialized_planes": {
            "witness_arity": arity,
            "depth": serial_depth,
            "target": arity + 4 * clog2(arity) + 9,
        },
        "non_equivariant_selector_rejected": rejected,
    }


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "orbit-synthesis/order-pair-integrated-compiler/v1",
        "status": "fresh-room explicit construction and deterministic audit",
        "order_pair_component": check_order_pair_component(),
        "integrated_semantics": check_integrated_semantics(),
        "large_arity_ledger": check_large_arity_ledger(),
        "mutations": check_mutations(),
        "claim_boundary": (
            "This independently reconstructs one explicit shared d/u DAG from a "
            "compatible selector table and proves the stated 34 size constant and "
            "coefficient-one depth ledger. It is not the byte-exact local "
            "01ddf456 packet, a novelty opinion, FTO analysis, or a proof of "
            "finite-width optimality."
        ),
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(encoded).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_receipt(), sort_keys=True, indent=2) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

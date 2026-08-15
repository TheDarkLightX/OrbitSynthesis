"""Two-stage residual selector using shared order-pair vectors."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping

from compiler_bridge_model import (
    DAG,
    Q,
    Word,
    balanced_anchor,
    binary_node_upper,
    build_binary_reference,
    build_order_pair_vector,
    build_signed_router,
    ceil_log3,
    clog2,
    encode_bits,
    floor_log3,
    order_pair_vector_nodes,
    require,
    validate_selector,
)


@dataclass(frozen=True)
class HierarchicalBuild:
    root: int
    anchor: int
    binary: int
    nonbinary: int
    local_width: int
    bottom_width: int
    top_width: int
    local_library_size: int


def controls_from_pairs(
    pairs: Mapping[Word, tuple[int, int]],
) -> dict[tuple[int, Word], int]:
    return {
        (slot, physical): pair[slot]
        for physical, pair in pairs.items()
        for slot in (0, 1)
    }


def compile_hierarchical_small(
    arity: int,
    selector: Mapping[Word, int],
    *,
    local_width: int = 1,
) -> tuple[DAG, HierarchicalBuild]:
    """Materialize the complete two-stage compiler for bounded testing."""

    validate_selector(arity, selector)
    require(1 <= local_width < arity, "nontrivial split required")
    residual_width = arity - local_width
    require(residual_width >= 2, "two-stage residual requires width at least two")
    bottom_width = residual_width // 2
    top_width = residual_width - bottom_width

    dag = DAG(arity)
    anchor = balanced_anchor(dag, dag.variables)
    one = dag.unary(anchor)
    zero = dag.unary(one)

    local_variables = dag.variables[:local_width]
    bottom_variables = dag.variables[
        local_width : local_width + bottom_width
    ]
    top_variables = dag.variables[local_width + bottom_width :]
    local_words = tuple(product(Q, repeat=local_width))
    bottom_words = tuple(product(Q, repeat=bottom_width))
    top_words = tuple(product(Q, repeat=top_width))

    local_controls = controls_from_pairs(
        build_order_pair_vector(
            dag,
            local_variables,
            anchor=anchor,
            zero=zero,
            root_negative=False,
        )
    )
    library: dict[tuple[int, ...], tuple[int, int]] = {}
    for table in product(Q, repeat=len(local_words)):
        high_payloads = {
            physical: one if encode_bits(value)[0] else zero
            for physical, value in zip(local_words, table, strict=True)
        }
        low_payloads = {
            physical: one if encode_bits(value)[1] else zero
            for physical, value in zip(local_words, table, strict=True)
        }
        library[table] = (
            build_signed_router(
                dag,
                local_width,
                root_negative=False,
                branches=high_payloads,
                controls=local_controls,
            ),
            build_signed_router(
                dag,
                local_width,
                root_negative=False,
                branches=low_payloads,
                controls=local_controls,
            ),
        )

    bottom_controls = controls_from_pairs(
        build_order_pair_vector(
            dag,
            bottom_variables,
            anchor=anchor,
            zero=zero,
            root_negative=False,
        )
    )
    bottom_roots: dict[Word, tuple[int, int]] = {}
    for top in top_words:
        high_branches: dict[Word, int] = {}
        low_branches: dict[Word, int] = {}
        for bottom in bottom_words:
            table = tuple(
                (local + bottom + top)[selector[local + bottom + top]]
                for local in local_words
            )
            high_branches[bottom], low_branches[bottom] = library[table]
        bottom_roots[top] = (
            build_signed_router(
                dag,
                bottom_width,
                root_negative=False,
                branches=high_branches,
                controls=bottom_controls,
            ),
            build_signed_router(
                dag,
                bottom_width,
                root_negative=False,
                branches=low_branches,
                controls=bottom_controls,
            ),
        )

    top_controls = controls_from_pairs(
        build_order_pair_vector(
            dag,
            top_variables,
            anchor=anchor,
            zero=zero,
            root_negative=False,
        )
    )
    high = build_signed_router(
        dag,
        top_width,
        root_negative=False,
        branches={top: roots[0] for top, roots in bottom_roots.items()},
        controls=top_controls,
    )
    low = build_signed_router(
        dag,
        top_width,
        root_negative=False,
        branches={top: roots[1] for top, roots in bottom_roots.items()},
        controls=top_controls,
    )
    nonbinary = dag.disc(dag.disc(high, one, anchor), zero, low)
    binary = build_binary_reference(dag, selector)
    root = dag.disc(
        dag.disc(zero, anchor, binary),
        dag.disc(zero, anchor, nonbinary),
        nonbinary,
    )
    return dag, HierarchicalBuild(
        root=root,
        anchor=anchor,
        binary=binary,
        nonbinary=nonbinary,
        local_width=local_width,
        bottom_width=bottom_width,
        top_width=top_width,
        local_library_size=len(library),
    )


def adaptive_parameters(
    arity: int,
) -> tuple[int, int, int, int, int, int, int]:
    ell = ceil_log3(arity * arity)
    headroom = arity + 1 - ell
    local_width = floor_log3(headroom)
    local_assignments = 3**local_width
    residual_width = arity - local_width
    bottom_width = residual_width // 2
    top_width = residual_width - bottom_width
    return (
        ell,
        headroom,
        local_assignments,
        local_width,
        residual_width,
        bottom_width,
        top_width,
    )


def residual_nodes(width: int) -> int:
    """Two-stage two-plane residual selector with two shared vectors."""

    require(width >= 2, "two-stage residual requires width at least two")
    bottom_width = width // 2
    top_width = width - bottom_width
    bottom_capacity = 3**bottom_width
    top_capacity = 3**top_width
    return (
        top_capacity * (3 * bottom_capacity - 1)
        + order_pair_vector_nodes(bottom_width, False)
        + (3 * top_capacity - 1)
        + order_pair_vector_nodes(top_width, False)
    )


def total_node_upper(arity: int) -> int:
    _, _, local, local_width, residual_width, _, _ = adaptive_parameters(arity)
    return (
        (3 * local - 1) * 3**local
        + order_pair_vector_nodes(local_width, False)
        + residual_nodes(residual_width)
        + 4 * arity
        + 3
        + binary_node_upper(arity)
    )


def total_depth_upper(arity: int) -> int:
    _, _, _, local_width, _, bottom_width, top_width = adaptive_parameters(arity)
    anchor_depth = 3 * clog2(arity)
    local_output = (
        anchor_depth
        + 3
        + clog2(local_width)
        + local_width
        + 1
    )
    bottom_output = (
        max(
            local_output,
            anchor_depth + 3 + clog2(bottom_width),
        )
        + bottom_width
        + 1
    )
    top_output = (
        max(
            bottom_output,
            anchor_depth + 3 + clog2(top_width),
        )
        + top_width
        + 1
    )
    return top_output + 4

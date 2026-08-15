"""Hierarchical residual compiler with a recursively shared local library."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
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
    floor_log3,
    order_pair_vector_nodes,
    require,
    validate_selector,
)
from hierarchical_compiler_model import controls_from_pairs, residual_nodes


@dataclass(frozen=True)
class RecursiveBuild:
    root: int
    anchor: int
    binary: int
    nonbinary: int
    local_width: int
    bottom_width: int
    top_width: int
    local_library_size: int


def build_recursive_library(
    dag: DAG,
    variables: tuple[int, ...],
    *,
    anchor: int,
    zero: int,
    one: int,
) -> dict[tuple[int, ...], tuple[int, int]]:
    """Generate every Q-valued table as a shared pair of Boolean-plane roots."""

    if not variables:
        return {
            (0,): (zero, zero),
            (1,): (zero, one),
            (2,): (one, zero),
        }

    selector = variables[0]
    child_library = build_recursive_library(
        dag,
        variables[1:],
        anchor=anchor,
        zero=zero,
        one=one,
    )
    controls = controls_from_pairs(
        build_order_pair_vector(
            dag,
            (selector,),
            anchor=anchor,
            zero=zero,
            root_negative=False,
        )
    )

    outputs: dict[tuple[int, ...], tuple[int, int]] = {}
    children = tuple(child_library.items())
    for (table0, roots0), (table1, roots1), (table2, roots2) in product(
        children,
        repeat=3,
    ):
        table = table0 + table1 + table2
        outputs[table] = (
            build_signed_router(
                dag,
                1,
                root_negative=False,
                branches={
                    (0,): roots0[0],
                    (1,): roots1[0],
                    (2,): roots2[0],
                },
                controls=controls,
            ),
            build_signed_router(
                dag,
                1,
                root_negative=False,
                branches={
                    (0,): roots0[1],
                    (1,): roots1[1],
                    (2,): roots2[1],
                },
                controls=controls,
            ),
        )
    return outputs


def compile_recursive_small(
    arity: int,
    selector: Mapping[Word, int],
    *,
    local_width: int = 1,
) -> tuple[DAG, RecursiveBuild]:
    """Materialize the full recursive-library/two-stage compiler."""

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

    library = build_recursive_library(
        dag,
        local_variables,
        anchor=anchor,
        zero=zero,
        one=one,
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
    return dag, RecursiveBuild(
        root=root,
        anchor=anchor,
        binary=binary,
        nonbinary=nonbinary,
        local_width=local_width,
        bottom_width=bottom_width,
        top_width=top_width,
        local_library_size=len(library),
    )


@lru_cache(maxsize=None)
def recursive_library_nodes(width: int) -> int:
    """Eight skeleton nodes per table plus one width-one vector per level."""

    return 8 * sum(3 ** (3**level) for level in range(1, width + 1)) + 6 * width


def parameters(
    arity: int,
) -> tuple[int, int, int, int, int, int, int]:
    ell = ceil_log3(arity)
    headroom = arity - ell
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


def total_node_upper(arity: int) -> int:
    _, _, _, local_width, residual_width, _, _ = parameters(arity)
    return (
        recursive_library_nodes(local_width)
        + residual_nodes(residual_width)
        + 4 * arity
        + 3
        + binary_node_upper(arity)
    )


def total_depth_upper(arity: int) -> int:
    _, _, _, local_width, _, bottom_width, top_width = parameters(arity)
    anchor_depth = 3 * clog2(arity)
    local_output = anchor_depth + 2 * local_width + 3
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

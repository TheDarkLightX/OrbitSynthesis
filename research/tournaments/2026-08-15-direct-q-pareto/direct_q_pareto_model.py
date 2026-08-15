"""Direct-Q local/bottom selectors with one signed outer routing stage."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[3]
BASE = (
    ROOT
    / "research/tournaments/2026-08-13-program-vector-optimization"
    / "audits/compiler_bridge_reconstruction"
)
sys.path.insert(0, str(BASE))

from compiler_bridge_model import (  # noqa: E402
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


@dataclass(frozen=True)
class ParetoBuild:
    root: int
    anchor: int
    binary: int
    nonbinary: int
    local_width: int
    direct_width: int
    signed_width: int
    local_library_size: int


def mux_q(
    dag: DAG,
    selector: int,
    branch0: int,
    branch1: int,
    branch2: int,
    *,
    zero: int,
    one: int,
    two: int,
) -> int:
    """Five-node exact selector for arbitrary Q-valued payloads."""

    gated0 = dag.disc(zero, selector, branch0)
    gated1 = dag.disc(one, selector, branch1)
    gated2 = dag.disc(selector, two, branch2)
    tail = dag.disc(gated1, one, gated2)
    return dag.disc(gated0, zero, tail)


def encode_q(
    dag: DAG,
    value: int,
    *,
    zero: int,
    one: int,
    two: int,
) -> tuple[int, int]:
    """One node per rail: 0->10, 1->01, 2->00."""

    first = dag.disc(zero, value, one)
    second = dag.disc(value, two, zero)
    return first, second


def decode_q(dag: DAG, first: int, second: int, *, two: int) -> int:
    """One-node inverse on the three legal codes."""

    return dag.disc(second, first, two)


def controls_from_pairs(
    pairs: Mapping[Word, tuple[int, int]],
) -> dict[tuple[int, Word], int]:
    return {
        (slot, physical): pair[slot]
        for physical, pair in pairs.items()
        for slot in (0, 1)
    }


def build_direct_library(
    dag: DAG,
    variables: tuple[int, ...],
    *,
    zero: int,
    one: int,
    two: int,
) -> dict[tuple[int, ...], int]:
    """All Q-valued tables, recursively shared as native Q roots."""

    if not variables:
        return {(0,): zero, (1,): one, (2,): two}

    selector = variables[0]
    children = tuple(
        build_direct_library(
            dag,
            variables[1:],
            zero=zero,
            one=one,
            two=two,
        ).items()
    )
    outputs: dict[tuple[int, ...], int] = {}
    for (table0, root0), (table1, root1), (table2, root2) in product(
        children,
        repeat=3,
    ):
        outputs[table0 + table1 + table2] = mux_q(
            dag,
            selector,
            root0,
            root1,
            root2,
            zero=zero,
            one=one,
            two=two,
        )
    return outputs


def direct_select(
    dag: DAG,
    variables: tuple[int, ...],
    branches: Mapping[Word, int],
    *,
    zero: int,
    one: int,
    two: int,
) -> int:
    """Balanced-by-coordinate direct Q selector using five nodes per tree node."""

    width = len(variables)
    require(
        set(branches) == set(product(Q, repeat=width)),
        "direct-selector branch domain drift",
    )
    if width == 0:
        return branches[()]

    children = []
    for digit in Q:
        child_branches = {
            word[1:]: root
            for word, root in branches.items()
            if word[0] == digit
        }
        children.append(
            direct_select(
                dag,
                variables[1:],
                child_branches,
                zero=zero,
                one=one,
                two=two,
            )
        )
    return mux_q(
        dag,
        variables[0],
        children[0],
        children[1],
        children[2],
        zero=zero,
        one=one,
        two=two,
    )


def compile_pareto_small(
    arity: int,
    selector: Mapping[Word, int],
    *,
    local_width: int,
    direct_width: int,
) -> tuple[DAG, ParetoBuild]:
    """Materialize the complete direct-Q/signed-outer compiler."""

    validate_selector(arity, selector)
    require(local_width >= 1, "positive local width required")
    require(direct_width >= 1, "positive direct width required")
    signed_width = arity - local_width - direct_width
    require(signed_width >= 1, "positive signed outer width required")

    dag = DAG(arity)
    anchor = balanced_anchor(dag, dag.variables)
    one = dag.unary(anchor)
    zero = dag.unary(one)

    local_variables = dag.variables[:local_width]
    direct_variables = dag.variables[
        local_width : local_width + direct_width
    ]
    signed_variables = dag.variables[local_width + direct_width :]
    local_words = tuple(product(Q, repeat=local_width))
    direct_words = tuple(product(Q, repeat=direct_width))
    signed_words = tuple(product(Q, repeat=signed_width))

    library = build_direct_library(
        dag,
        local_variables,
        zero=zero,
        one=one,
        two=anchor,
    )

    bottom_roots: dict[Word, int] = {}
    for signed in signed_words:
        branches: dict[Word, int] = {}
        for direct in direct_words:
            table = tuple(
                (local + direct + signed)[selector[local + direct + signed]]
                for local in local_words
            )
            branches[direct] = library[table]
        bottom_roots[signed] = direct_select(
            dag,
            direct_variables,
            branches,
            zero=zero,
            one=one,
            two=anchor,
        )

    encoded = {
        signed: encode_q(
            dag,
            root,
            zero=zero,
            one=one,
            two=anchor,
        )
        for signed, root in bottom_roots.items()
    }
    controls = controls_from_pairs(
        build_order_pair_vector(
            dag,
            signed_variables,
            anchor=anchor,
            zero=zero,
            root_negative=False,
        )
    )
    first = build_signed_router(
        dag,
        signed_width,
        root_negative=False,
        branches={word: roots[0] for word, roots in encoded.items()},
        controls=controls,
    )
    second = build_signed_router(
        dag,
        signed_width,
        root_negative=False,
        branches={word: roots[1] for word, roots in encoded.items()},
        controls=controls,
    )
    nonbinary = decode_q(dag, first, second, two=anchor)

    binary = build_binary_reference(dag, selector)
    root = dag.disc(
        dag.disc(zero, anchor, binary),
        dag.disc(zero, anchor, nonbinary),
        nonbinary,
    )
    return dag, ParetoBuild(
        root=root,
        anchor=anchor,
        binary=binary,
        nonbinary=nonbinary,
        local_width=local_width,
        direct_width=direct_width,
        signed_width=signed_width,
        local_library_size=len(library),
    )


@lru_cache(maxsize=None)
def direct_library_nodes(width: int) -> int:
    return 5 * sum(3 ** (3**level) for level in range(1, width + 1))


def parameters(
    arity: int,
) -> tuple[int, int, int, int, int, int, int, int, int]:
    ell = ceil_log3(arity)
    headroom = arity + 1 - ell
    local_width = floor_log3(headroom)
    local_assignments = 3**local_width
    direct_width = local_width + 1
    signed_width = arity - local_width - direct_width
    direct_capacity = 3**direct_width
    signed_capacity = 3**signed_width
    prefix_capacity = direct_capacity * signed_capacity
    return (
        ell,
        headroom,
        local_assignments,
        local_width,
        direct_width,
        signed_width,
        direct_capacity,
        signed_capacity,
        prefix_capacity,
    )


def residual_nodes(arity: int) -> int:
    (
        _,
        _,
        _,
        _,
        direct_width,
        signed_width,
        direct_capacity,
        signed_capacity,
        prefix_capacity,
    ) = parameters(arity)
    bottom = 5 * signed_capacity * ((direct_capacity - 1) // 2)
    encoders = 2 * signed_capacity
    top_skeletons = 3 * signed_capacity - 1
    return (
        bottom
        + encoders
        + top_skeletons
        + order_pair_vector_nodes(signed_width, False)
    )


def total_node_upper(arity: int) -> int:
    _, _, _, local_width, _, _, _, _, _ = parameters(arity)
    return (
        direct_library_nodes(local_width)
        + residual_nodes(arity)
        + 4 * arity
        + 2
        + binary_node_upper(arity)
    )


def total_depth_upper(arity: int) -> int:
    (
        _,
        _,
        _,
        local_width,
        direct_width,
        signed_width,
        _,
        _,
        _,
    ) = parameters(arity)
    address_depth = 3 * clog2(arity)
    local_output = address_depth + 2 + 3 * local_width
    direct_output = local_output + 3 * direct_width
    encoded_output = direct_output + 1
    signed_controls = address_depth + 3 + clog2(signed_width)
    signed_output = max(encoded_output, signed_controls) + signed_width + 1
    return signed_output + 3  # one decoder and two glue levels

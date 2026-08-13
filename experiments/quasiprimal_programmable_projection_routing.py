#!/usr/bin/env python3
"""Audit programmable projection routing for conservative Quackenbush-Q terms.

This is a fail-closed checker for the candidate depth bound

    (3 * log_6(3)) * r + O(r / log r)

in the same parameter-free original-signature shared-DAG model used by the
fixed-Q term-complexity draft.  The checker validates the fixed six-way
ternary and seven-way complement-relative Boolean gadgets, materializes the
composed compiler on bounded selector tables, checks the exact recurrences,
and exercises mutations.  Its PASS is bounded evidence, not a proof of the
generic asymptotic theorem or of novelty.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from functools import cache
from itertools import product
from pathlib import Path
from typing import Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.quasiprimal_orbit_term_compiler import (  # noqa: E402
    compatible_tables,
    random_compatible_table,
)
from orbitsynthesis.orbit_term_compile import (  # noqa: E402
    Disc,
    Expr,
    Q,
    UnaryU,
    Var,
    complement,
    distinct_node_count,
    evaluate,
    expression_depth,
    normal_selector,
)
from orbitsynthesis.orbit_term_compile_local import (  # noqa: E402
    balanced_absorbing_two,
    shallow_ternary_selector,
)


R6_PROGRAMS = (
    (1, 2, 1, 1, 2, 1, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2, 0, 1),
    (0, 0, 1, 1, 1, 2, 1, 1, 2, 2, 0, 2, 1, 0, 1, 2, 1, 2),
    (1, 2, 1, 1, 0, 2, 0, 0, 2, 2, 2, 2, 2, 1, 2, 2, 0, 0),
    (2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 1, 2, 0, 2, 2, 0, 0, 1),
    (2, 0, 0, 2, 0, 2, 2, 1, 0, 1, 1, 0, 2, 1, 2, 2, 1, 2),
    (1, 2, 1, 1, 0, 2, 0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 1),
)

R7_PROGRAMS = (
    (0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1),
    (0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0),
    (1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1),
    (0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0),
    (0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0),
    (0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1),
    (0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def operation_depth(expr: Expr) -> int:
    return expression_depth(expr) - 1


def value_names(anchor: Expr) -> tuple[Expr, Expr, Expr]:
    one = UnaryU(anchor)
    zero = UnaryU(one)
    return zero, one, anchor


def r6_router(controls: Sequence[Expr], branches: Sequence[Expr]) -> Expr:
    require(len(controls) == 18, "R6 requires 18 controls")
    require(len(branches) == 6, "R6 requires six branches")
    (
        c13, c14, c16, c18, c19, c20, c22, c24, c25,
        c27, c28, c30, c31, c32, c34, c36, c37, c38,
    ) = controls
    b0, b1, b2, b3, b4, b5 = branches
    return Disc(
        Disc(
            Disc(c13, c14, b1),
            Disc(c16, b4, c18),
            Disc(c19, c20, b3),
        ),
        Disc(
            Disc(c22, b4, c24),
            Disc(c25, b4, c27),
            Disc(c28, b0, c30),
        ),
        Disc(
            Disc(c31, c32, b5),
            Disc(c34, b0, c36),
            Disc(c37, c38, b2),
        ),
    )


def r7_router(controls: Sequence[Expr], branches: Sequence[Expr]) -> Expr:
    require(len(controls) == 16, "R7 requires 16 controls")
    require(len(branches) == 7, "R7 requires seven branches")
    (
        c13, c14, c16, c18, c20, c21, c22, c24,
        c26, c27, c28, c30, c31, c32, c34, c36,
    ) = controls
    b0, b1, b2, b3, b4, b5, b6 = branches
    return Disc(
        Disc(
            Disc(c13, c14, b0),
            Disc(c16, b5, c18),
            Disc(b4, c20, c21),
        ),
        Disc(
            Disc(c22, b1, c24),
            Disc(b3, c26, c27),
            Disc(c28, b0, c30),
        ),
        Disc(
            Disc(c31, c32, b2),
            Disc(c34, b2, c36),
            b6,
        ),
    )


def program_terms(
    program: Sequence[int],
    names: Sequence[Expr],
) -> tuple[Expr, ...]:
    require(all(0 <= digit < len(names) for digit in program), "bad program digit")
    return tuple(names[digit] for digit in program)


def primitive_checks() -> dict[str, object]:
    r6_skeleton_controls = tuple(Var(index) for index in range(18))
    r6_skeleton_branches = tuple(Var(index) for index in range(18, 24))
    r6_skeleton = r6_router(r6_skeleton_controls, r6_skeleton_branches)
    require(operation_depth(r6_skeleton) == 3, "R6 dependency depth drift")
    require(
        distinct_node_count(r6_skeleton) - 24 == 13,
        "R6 discriminator census drift",
    )
    r7_skeleton_controls = tuple(Var(index) for index in range(16))
    r7_skeleton_branches = tuple(Var(index) for index in range(16, 23))
    r7_skeleton = r7_router(r7_skeleton_controls, r7_skeleton_branches)
    require(operation_depth(r7_skeleton) == 3, "R7 dependency depth drift")
    require(
        distinct_node_count(r7_skeleton) - 23 == 12,
        "R7 discriminator census drift",
    )

    anchor = Var(0)
    zero, one, two = value_names(anchor)
    q_names = (zero, one, two)
    r6_branches = tuple(Var(index) for index in range(1, 7))

    r6_checked = 0
    for target, program in enumerate(R6_PROGRAMS):
        term = r6_router(program_terms(program, q_names), r6_branches)
        for branches in product(Q, repeat=6):
            require(
                evaluate(term, (2, *branches)) == branches[target],
                f"R6 failed for target {target}, branches {branches}",
            )
            r6_checked += 1

    mutated_r6 = list(R6_PROGRAMS[0])
    mutated_r6[0] = 2
    mutated_r6_term = r6_router(program_terms(mutated_r6, q_names), r6_branches)
    r6_mutation_mismatches = sum(
        evaluate(mutated_r6_term, (2, *branches)) != branches[0]
        for branches in product(Q, repeat=6)
    )
    require(r6_mutation_mismatches > 0, "effective R6 mutation survived")

    x0 = Var(0)
    x0_flip = UnaryU(x0)
    bit_names = (x0, x0_flip)
    r7_branches = tuple(Var(index) for index in range(1, 8))
    r7_checked = 0
    r7_complement_checked = 0
    for target, program in enumerate(R7_PROGRAMS):
        term = r7_router(program_terms(program, bit_names), r7_branches)
        for branches in product((0, 1), repeat=7):
            require(
                evaluate(term, (0, *branches)) == branches[target],
                f"R7 failed for target {target}, branches {branches}",
            )
            r7_checked += 1
            flipped = tuple(1 - value for value in branches)
            require(
                evaluate(term, (1, *flipped)) == flipped[target],
                f"R7 complement-relative failure for target {target}",
            )
            r7_complement_checked += 1

    mutated_r7 = list(R7_PROGRAMS[0])
    mutated_r7[1] = 1
    mutated_r7_term = r7_router(program_terms(mutated_r7, bit_names), r7_branches)
    r7_mutation_mismatches = sum(
        evaluate(mutated_r7_term, (0, *branches)) != branches[0]
        for branches in product((0, 1), repeat=7)
    )
    require(r7_mutation_mismatches > 0, "effective R7 mutation survived")

    # If global Boolean constants were free, the fixed programs would still
    # select the requested branch.  The failure is therefore input legality,
    # not finite gadget semantics: parameter-free Q-terms have no global 0/1
    # names on the binary cube.  The compiler gate below rejects that model
    # explicitly and uses x0/u(x0) instead.
    absolute_controls = tuple(Var(index) for index in range(8, 24))
    absolute_term = r7_router(absolute_controls, r7_branches)
    absolute_mismatches = 0
    for target, program in enumerate(R7_PROGRAMS):
        for branches in product((0, 1), repeat=7):
            flipped = tuple(1 - value for value in branches)
            # Program bits are absolute constants here, so unlike x0/u(x0)
            # they do not complement when the branch orientation flips.
            arguments = (1, *flipped, *program)
            if evaluate(absolute_term, arguments) != flipped[target]:
                absolute_mismatches += 1
    require(absolute_mismatches == 0, "fixed-program projection semantics drift")

    primitive_semantics = {
        "r6_discriminator_nodes": 13,
        "r6_dependency_depth": 3,
        "r6_checks": r6_checked,
        "r6_mutation_mismatches": r6_mutation_mismatches,
        "r7_discriminator_nodes": 12,
        "r7_dependency_depth": 3,
        "r7_checks": r7_checked,
        "r7_complement_checks": r7_complement_checked,
        "r7_mutation_mismatches": r7_mutation_mismatches,
        "free_absolute_controls_would_project": absolute_mismatches == 0,
    }
    primitive_semantics["semantic_sha256"] = hashlib.sha256(
        json.dumps(primitive_semantics, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return primitive_semantics


Shape = int | tuple["Shape", ...]


def ceil_log(base: int, value: int) -> int:
    require(base >= 2 and value >= 1, "invalid ceil-log arguments")
    exponent = 0
    power = 1
    while power < value:
        power *= base
        exponent += 1
    return exponent


def balanced_shape(count: int, fanout: int, offset: int = 0) -> Shape:
    require(count >= 1, "balanced tree requires a leaf")
    require(fanout >= 2, "balanced tree fanout must be at least two")
    if count == 1:
        return offset
    child_count = min(fanout, count)
    quotient, remainder = divmod(count, child_count)
    sizes = tuple(quotient + (index < remainder) for index in range(child_count))
    children = []
    cursor = offset
    for size in sizes:
        children.append(balanced_shape(size, fanout, cursor))
        cursor += size
    return tuple(children)


def shape_height(shape: Shape) -> int:
    if isinstance(shape, int):
        return 0
    return 1 + max(shape_height(child) for child in shape)


def shape_internal_count(shape: Shape) -> int:
    if isinstance(shape, int):
        return 0
    return 1 + sum(shape_internal_count(child) for child in shape)


def shape_leaf_count(shape: Shape) -> int:
    if isinstance(shape, int):
        return 1
    return sum(shape_leaf_count(child) for child in shape)


def shape_digits(shape: Shape, leaf_count: int) -> tuple[tuple[int, ...], ...]:
    digits: list[dict[int, int]] = []

    def visit(node: Shape, depth: int) -> None:
        if isinstance(node, int):
            return
        while len(digits) <= depth:
            digits.append({})
        for digit, child in enumerate(node):
            def mark_leaves(subtree: Shape) -> None:
                if isinstance(subtree, int):
                    digits[depth][subtree] = digit
                else:
                    for grandchild in subtree:
                        mark_leaves(grandchild)
            mark_leaves(child)
            visit(child, depth + 1)

    visit(shape, 0)
    return tuple(
        tuple(level.get(index, 0) for index in range(leaf_count))
        for level in digits
    )


def compile_ternary_control(
    positions: tuple[int, ...],
    table: Mapping[tuple[int, ...], int],
    variables: tuple[Expr, ...],
    names: tuple[Expr, Expr, Expr],
) -> Expr:
    require(set(table) == set(product(Q, repeat=len(positions))), "bad ternary control table")

    def build(offset: int, prefix: tuple[int, ...]) -> Expr:
        if offset == len(positions):
            return names[table[prefix]]
        branches = tuple(build(offset + 1, prefix + (value,)) for value in Q)
        return shallow_ternary_selector(
            variables[positions[offset]], *names, *branches
        )

    return build(0, ())


def compile_relative_binary_control(
    positions: tuple[int, ...],
    table: Mapping[tuple[int, ...], int],
    variables: tuple[Expr, ...],
    bit_names: tuple[Expr, Expr],
) -> Expr:
    assignments = set(product((0, 1), repeat=len(positions)))
    require(set(table) == assignments, "bad relative-binary control table")

    def build(offset: int, prefix: tuple[int, ...]) -> Expr:
        if offset == len(positions):
            return bit_names[table[prefix]]
        return normal_selector(
            variables[positions[offset]],
            variables[0],
            build(offset + 1, prefix + (0,)),
            build(offset + 1, prefix + (1,)),
        )

    return build(0, ())


def prepare_controls(
    assignments: tuple[tuple[int, ...], ...],
    positions: tuple[int, ...],
    fanout: int,
    programs: tuple[tuple[int, ...], ...],
    compiler: Callable[[tuple[int, ...], Mapping[tuple[int, ...], int]], Expr],
) -> tuple[Shape, tuple[tuple[Expr, ...], ...]]:
    require(len(programs) == fanout, "program count does not match fanout")
    shape = balanced_shape(len(assignments), fanout)
    require(shape_height(shape) <= ceil_log(fanout, len(assignments)), "balanced height drift")
    require(shape_internal_count(shape) <= len(assignments) - 1, "balanced node bound drift")
    digit_levels = shape_digits(shape, len(assignments))
    controls = []
    for digits in digit_levels:
        level_controls = []
        for slot in range(len(programs[0])):
            table = {
                assignment: programs[digits[index]][slot]
                for index, assignment in enumerate(assignments)
            }
            level_controls.append(compiler(positions, table))
        controls.append(tuple(level_controls))
    return shape, tuple(controls)


def materialize_route(
    shape: Shape,
    leaf_terms: Sequence[Expr],
    controls: tuple[tuple[Expr, ...], ...],
    fanout: int,
    router: Callable[[Sequence[Expr], Sequence[Expr]], Expr],
    depth: int = 0,
) -> Expr:
    if isinstance(shape, int):
        return leaf_terms[shape]
    branches = [
        materialize_route(child, leaf_terms, controls, fanout, router, depth + 1)
        for child in shape
    ]
    while len(branches) < fanout:
        branches.append(branches[-1])
    return router(controls[depth], tuple(branches))


def partition_chunks(positions: tuple[int, ...], width: int) -> tuple[tuple[int, ...], ...]:
    require(width >= 1, "chunk width must be positive")
    return tuple(positions[start : start + width] for start in range(0, len(positions), width))


def candidate_parameters(arity: int) -> dict[str, object]:
    require(arity >= 2, "candidate parameters start at arity two")
    ratio = 3**arity // arity
    h = 0
    power = 1
    while power * 3 <= ratio:
        power *= 3
        h += 1
    h = max(1, h)
    block_assignments = 1
    block_positions = 0
    while block_assignments * 3 <= h:
        block_assignments *= 3
        block_positions += 1
    g3 = max(1, ceil_log(3, arity))
    g2 = max(1, ceil_log(2, arity))
    ternary_chunks = partition_chunks(tuple(range(block_positions, arity)), g3)
    binary_chunks = partition_chunks(tuple(range(1, arity)), g2)
    l6 = ceil_log(6, block_assignments) + sum(
        ceil_log(6, 3 ** len(chunk)) for chunk in ternary_chunks
    )
    l7 = sum(ceil_log(7, 2 ** len(chunk)) for chunk in binary_chunks)
    return {
        "H": h,
        "block_positions": block_positions,
        "M": block_assignments,
        "P": 3 ** (arity - block_positions),
        "g3": g3,
        "g2": g2,
        "ternary_chunks": ternary_chunks,
        "binary_chunks": binary_chunks,
        "L6": l6,
        "L7": l7,
    }


def certified_size_bound(
    arity: int,
    *,
    include_controls: bool = True,
    per_level_sharing: bool = True,
    balanced_codes: bool = True,
) -> int:
    require(include_controls, "control preprocessing omitted from size accounting")
    require(per_level_sharing, "per-node controls do not certify the claimed size")
    require(balanced_codes, "sparse full-code accounting substituted for balanced tries")
    parameters = candidate_parameters(arity)
    m = int(parameters["M"])
    p = int(parameters["P"])
    g3 = int(parameters["g3"])
    g2 = int(parameters["g2"])
    l6 = int(parameters["L6"])
    l7 = int(parameters["L7"])
    return (
        26 * 3**m
        + 13 * (p - 1)
        + 12 * (2 ** (arity - 1) - 1)
        + 63 * l6 * (3**g3 - 1)
        + 48 * l7 * (2**g2 - 1)
        + 4 * arity
        + 6
    )


def certified_depth_bound(arity: int, *, include_binary: bool = True) -> int:
    require(include_binary, "all-binary branch omitted from depth maximum")
    parameters = candidate_parameters(arity)
    anchor_depth = 3 * ceil_log(2, arity)
    nonbinary = (
        anchor_depth
        + 2
        + 3 * int(parameters["g3"])
        + 3 * int(parameters["L6"])
    )
    binary = 1 + 2 * int(parameters["g2"]) + 3 * int(parameters["L7"])
    return max(nonbinary, binary, anchor_depth + 2) + 2


def compile_programmable_selector(
    arity: int,
    selector_indices: Mapping[tuple[int, ...], int],
    *,
    relative_binary_controls: bool = True,
) -> Expr:
    require(arity >= 1, "arity must be positive")
    require(
        relative_binary_controls,
        "absolute Boolean program constants are illegal in the parameter-free model",
    )
    points = tuple(product(Q, repeat=arity))
    require(set(selector_indices) == set(points), "selector table is not total")
    require(
        all(0 <= index < arity for index in selector_indices.values()),
        "selector index outside arity",
    )
    for point in product((0, 1), repeat=arity):
        require(
            selector_indices[point] == selector_indices[complement(point)],
            "binary selector table is not complement-invariant",
        )
    variables = tuple(Var(index) for index in range(arity))
    if arity == 1:
        return variables[0]

    anchor = balanced_absorbing_two(variables)
    names = value_names(anchor)
    bit_names = (variables[0], UnaryU(variables[0]))
    parameters = candidate_parameters(arity)
    block_count = int(parameters["block_positions"])
    block_positions = tuple(range(block_count))
    prefix_chunks = tuple(parameters["ternary_chunks"])
    binary_chunks = tuple(parameters["binary_chunks"])

    def ternary_compiler(
        positions: tuple[int, ...], table: Mapping[tuple[int, ...], int]
    ) -> Expr:
        return compile_ternary_control(positions, table, variables, names)

    block_assignments = tuple(product(Q, repeat=block_count))
    if block_count == 0:
        library: dict[tuple[int, ...], Expr] = {
            (0,): names[0],
            (1,): names[1],
            (2,): names[2],
        }
    else:
        block_shape, block_controls = prepare_controls(
            block_assignments,
            block_positions,
            6,
            R6_PROGRAMS,
            ternary_compiler,
        )

        def build_library(node: Shape, depth: int = 0) -> dict[tuple[int, ...], Expr]:
            if isinstance(node, int):
                return {(0,): names[0], (1,): names[1], (2,): names[2]}
            child_libraries = tuple(build_library(child, depth + 1) for child in node)
            result: dict[tuple[int, ...], Expr] = {}
            for choices in product(*(tuple(library.items()) for library in child_libraries)):
                word = tuple(value for child_word, _ in choices for value in child_word)
                branches = [term for _, term in choices]
                while len(branches) < 6:
                    branches.append(branches[-1])
                result[word] = r6_router(block_controls[depth], tuple(branches))
            require(
                len(result) == 3 ** shape_leaf_count(node),
                "six-way function-library census drift",
            )
            return result

        library = build_library(block_shape)

    prefix_control_packets = []
    for chunk in prefix_chunks:
        assignments = tuple(product(Q, repeat=len(chunk)))
        prefix_control_packets.append(
            prepare_controls(assignments, chunk, 6, R6_PROGRAMS, ternary_compiler)
        )

    values: list[int | None] = [None] * arity

    def select_prefix(chunk_index: int) -> Expr:
        if chunk_index == len(prefix_chunks):
            output_vector = []
            for block_point in block_assignments:
                for position, value in zip(block_positions, block_point, strict=True):
                    values[position] = value
                point = tuple(int(value) for value in values)
                output_vector.append(point[selector_indices[point]])
            return library[tuple(output_vector)]
        chunk = prefix_chunks[chunk_index]
        assignments = tuple(product(Q, repeat=len(chunk)))
        leaves = []
        for assignment in assignments:
            for position, value in zip(chunk, assignment, strict=True):
                values[position] = value
            leaves.append(select_prefix(chunk_index + 1))
        for position in chunk:
            values[position] = None
        shape, controls = prefix_control_packets[chunk_index]
        return materialize_route(shape, leaves, controls, 6, r6_router)

    nonbinary = select_prefix(0)

    def binary_compiler(
        positions: tuple[int, ...], table: Mapping[tuple[int, ...], int]
    ) -> Expr:
        return compile_relative_binary_control(positions, table, variables, bit_names)

    binary_control_packets = []
    for chunk in binary_chunks:
        assignments = tuple(product((0, 1), repeat=len(chunk)))
        binary_control_packets.append(
            prepare_controls(assignments, chunk, 7, R7_PROGRAMS, binary_compiler)
        )

    representative = [0] * arity

    def select_binary(chunk_index: int) -> Expr:
        if chunk_index == len(binary_chunks):
            point = tuple(representative)
            return variables[selector_indices[point]]
        chunk = binary_chunks[chunk_index]
        assignments = tuple(product((0, 1), repeat=len(chunk)))
        leaves = []
        for assignment in assignments:
            for position, value in zip(chunk, assignment, strict=True):
                representative[position] = value
            leaves.append(select_binary(chunk_index + 1))
        shape, controls = binary_control_packets[chunk_index]
        return materialize_route(shape, leaves, controls, 7, r7_router)

    binary = select_binary(0)
    return normal_selector(names[0], anchor, binary, nonbinary)


def verify_compiler(
    arity: int,
    table: Mapping[tuple[int, ...], int],
) -> dict[str, int]:
    term = compile_programmable_selector(arity, table)
    checked = 0
    for point in product(Q, repeat=arity):
        require(
            evaluate(term, point) == point[table[point]],
            f"programmable compiler mismatch at arity {arity}, point {point}",
        )
        checked += 1
    operation_nodes = distinct_node_count(term) - arity
    depth = operation_depth(term)
    if arity >= 2:
        require(operation_nodes <= certified_size_bound(arity), "finite size bound failed")
        require(depth <= certified_depth_bound(arity), "finite depth bound failed")
    return {
        "tuples_checked": checked,
        "operation_nodes": operation_nodes,
        "operation_depth": depth,
    }


@cache
def library_router_count(points: int) -> int:
    require(points >= 1, "library point count must be positive")
    if points == 1:
        return 0
    shape = balanced_shape(points, 6)
    return 13 * 3**points + sum(
        library_router_count(shape_leaf_count(child)) for child in shape
    )


def recurrence_checks() -> dict[str, object]:
    for points in range(1, 129):
        require(
            library_router_count(points) <= 26 * 3**points,
            f"library recurrence failed at {points}",
        )

    structural_rows = []
    coefficient = 3 * math.log(3, 6)
    for arity in (16, 32, 64, 128, 256, 512, 1024, 4096):
        parameters = candidate_parameters(arity)
        depth = certified_depth_bound(arity)
        structural_rows.append(
            {
                "arity": arity,
                "M": parameters["M"],
                "L6": parameters["L6"],
                "L7": parameters["L7"],
                "depth_bound": depth,
                "depth_per_arity": depth / arity,
            }
        )

    # Mutation gates for the proof-accounting contract.
    mutations = {}
    for name, kwargs in (
        ("omitted_controls", {"include_controls": False}),
        ("per_node_controls", {"per_level_sharing": False}),
        ("sparse_full_code", {"balanced_codes": False}),
    ):
        rejected = False
        try:
            certified_size_bound(16, **kwargs)
        except RuntimeError:
            rejected = True
        require(rejected, f"{name} accounting mutation survived")
        mutations[f"{name}_rejected"] = rejected

    binary_omission_rejected = False
    try:
        certified_depth_bound(16, include_binary=False)
    except RuntimeError:
        binary_omission_rejected = True
    require(binary_omission_rejected, "binary-depth omission mutation survived")
    mutations["binary_depth_omission_rejected"] = binary_omission_rejected

    absolute_controls_rejected = False
    try:
        compile_programmable_selector(
            2,
            next(iter(compatible_tables(2))),
            relative_binary_controls=False,
        )
    except RuntimeError:
        absolute_controls_rejected = True
    require(absolute_controls_rejected, "illegal absolute-control model survived")
    mutations["absolute_binary_controls_rejected"] = absolute_controls_rejected

    sparse_count = (6 ** ceil_log(6, 7) - 1) // 5
    balanced_count = shape_internal_count(balanced_shape(7, 6))
    require(balanced_count <= 6 and sparse_count > balanced_count, "sparse-code sentinel drift")
    mutations["sparse_router_count"] = sparse_count
    mutations["balanced_router_count"] = balanced_count

    return {
        "library_recurrence_points_checked": 128,
        "candidate_coefficient": coefficient,
        "structural_rows": structural_rows,
        "mutation_checks": mutations,
    }


def compiler_checks() -> dict[str, object]:
    rows = []
    total_tables = 0
    total_tuples = 0

    arity_one = {point: 0 for point in product(Q, repeat=1)}
    result = verify_compiler(1, arity_one)
    rows.append({"arity": 1, "tables": 1, **result})
    total_tables += 1
    total_tuples += result["tuples_checked"]

    arity_two_rows = []
    for table in compatible_tables(2):
        arity_two_rows.append(verify_compiler(2, table))
    require(len(arity_two_rows) == 128, "arity-two compatible-table census drift")
    rows.append(
        {
            "arity": 2,
            "tables": 128,
            "tuples_checked": sum(row["tuples_checked"] for row in arity_two_rows),
            "max_operation_nodes": max(row["operation_nodes"] for row in arity_two_rows),
            "max_operation_depth": max(row["operation_depth"] for row in arity_two_rows),
        }
    )
    total_tables += 128
    total_tuples += rows[-1]["tuples_checked"]

    for arity, seeds in ((3, (3101, 3102, 3103, 3104)), (4, (4101, 4102, 4103)), (5, (5101, 5102))):
        checks = [verify_compiler(arity, random_compatible_table(arity, seed)) for seed in seeds]
        rows.append(
            {
                "arity": arity,
                "tables": len(checks),
                "tuples_checked": sum(row["tuples_checked"] for row in checks),
                "max_operation_nodes": max(row["operation_nodes"] for row in checks),
                "max_operation_depth": max(row["operation_depth"] for row in checks),
            }
        )
        total_tables += len(checks)
        total_tuples += rows[-1]["tuples_checked"]

    invalid = random_compatible_table(3, 9917)
    binary_point = next(iter(product((0, 1), repeat=3)))
    partner = complement(binary_point)
    invalid[binary_point] = 0
    invalid[partner] = 1
    invalid_rejected = False
    try:
        compile_programmable_selector(3, invalid)
    except RuntimeError:
        invalid_rejected = True
    require(invalid_rejected, "non-complement-invariant table mutation survived")

    return {
        "rows": rows,
        "total_tables_checked": total_tables,
        "total_tuple_evaluations": total_tuples,
        "noncomplement_table_mutation_rejected": invalid_rejected,
    }


def main() -> None:
    summary = {
        "schema": "orbit-synthesis/quasiprimal-programmable-projection-routing/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "model": "parameter-free original-signature shared DAG; operation nodes; variables depth zero",
        "primitive_checks": primitive_checks(),
        "compiler_checks": compiler_checks(),
        "recurrence_checks": recurrence_checks(),
        "claim_boundary": (
            "The deterministic checks validate the displayed gadgets, bounded composed "
            "compiler instances, mutations, and recurrence arithmetic. The generic "
            "O(3^r/r) same-DAG size and (3 log_6 3)r+O(r/log r) depth theorem remains "
            "a manuscript proof under independent review. This receipt is not novelty, "
            "optimality, practical-performance, patent, FTO, or Tau-capability evidence."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal programmable projection routing")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

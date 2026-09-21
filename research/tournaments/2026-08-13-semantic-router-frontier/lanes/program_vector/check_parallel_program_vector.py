#!/usr/bin/env python3
"""Certify the parallel program-vector construction for signed d routers.

The checker is self-contained.  It does not import the frozen strong-family
author or audit.  Acceptance is owned by explicit requirements, concrete
truth tables, a direct ternary ROBDD, exact integer ledgers, and mutations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections.abc import Iterable
from decimal import Decimal, getcontext
from functools import cache
from itertools import product
from pathlib import Path
from typing import Literal


Bit = Literal[0, 1]
Mode = Literal["projection", "constant"]
CONTROL = 0
C_PARAMETER = 4
MIN_COMPILER_ARITY = 64
ROOT = Path(__file__).resolve().parents[5]
STATE = ROOT / "research/tournaments/2026-08-13-semantic-router-frontier/STATE.md"
STRONG_SOURCE = (
    ROOT
    / "research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/check_strong_router_family.py"
)
STRONG_SUMMARY = STRONG_SOURCE.with_name("summary.json")
STRONG_WITNESS = STRONG_SOURCE.with_name("r27_witness.json")
STRONG_REPORT = STRONG_SOURCE.with_name("REPORT.md")
VARIABLE_AUDIT = (
    ROOT
    / "research/tournaments/2026-08-13-semantic-router-frontier/audits/variable_compiler/REPORT.md"
)

FROZEN_HASHES = {
    STATE: "5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133",
    STRONG_SOURCE: "07fb1d8d322e57a7af666bae5b699c072805ff1d15eef1f1e7c2d87208729ef8",
    STRONG_SUMMARY: "6042127fd9f214e63bc38aa8e6367d1db7580c24b2b2e7a3aeba16625279aff0",
    STRONG_WITNESS: "6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65",
    STRONG_REPORT: "5ed37d98357eb03a2f6ded9f741c9fb52d8f5ad821585c81be544f201945f8c6",
    VARIABLE_AUDIT: "174a8fdf32e47fcce650298df5554a9f7c101fc67cc7be4ab4d2acb14bc5c661",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def unary_u(x: int) -> int:
    require(x in (0, 1, 2), "u input left Q")
    return (1, 0, 1)[x]


def words(width: int) -> tuple[tuple[int, ...], ...]:
    require(width >= 0, "negative word width")
    return tuple(product((0, 1, 2), repeat=width))


def first_mismatch_state(
    target: tuple[int, ...], physical: tuple[int, ...]
) -> tuple[int, int]:
    require(len(target) == len(physical), "word width mismatch")
    for target_digit, physical_digit in zip(target, physical, strict=True):
        if target_digit != physical_digit:
            return 0, int(target_digit == 1 and physical_digit == 2)
    return 1, 0


def cell_sign(root_sign: int, physical: tuple[int, ...]) -> int:
    require(root_sign in (0, 1), "invalid root sign")
    return root_sign ^ (sum(digit == 1 for digit in physical) & 1)


def expected_pair(
    root_sign: int,
    physical: tuple[int, ...],
    target: tuple[int, ...] | None,
    mode: Mode,
    constant: int = 0,
) -> tuple[int, int]:
    sign = cell_sign(root_sign, physical)
    if mode == "constant":
        require(constant in (0, 1), "invalid constant mode")
        return (1 - constant, constant) if sign == 0 else (constant, constant)
    require(target is not None, "projection target missing")
    equal, good = first_mismatch_state(target, physical)
    active = equal | good
    return (1 - active, good) if sign == 0 else (good, active)


class TermDAG:
    """Hash-consed original-signature d/u DAG with named input terminals."""

    def __init__(self) -> None:
        self.records: list[tuple[object, ...]] = []
        self.unique: dict[tuple[object, ...], int] = {}
        self.depths: list[int] = []

    def _intern(self, record: tuple[object, ...], depth: int) -> int:
        found = self.unique.get(record)
        if found is not None:
            return found
        result = len(self.records)
        self.records.append(record)
        self.depths.append(depth)
        self.unique[record] = result
        return result

    def terminal(self, name: str) -> int:
        return self._intern(("terminal", name), 0)

    def u(self, child: int) -> int:
        return self._intern(("u", child), self.depths[child] + 1)

    def d(self, left: int, middle: int, right: int) -> int:
        return self._intern(
            ("d", left, middle, right),
            max(self.depths[left], self.depths[middle], self.depths[right]) + 1,
        )

    @property
    def operation_count(self) -> int:
        return sum(record[0] != "terminal" for record in self.records)

    def evaluate_many(self, roots: Iterable[int], environment: dict[str, int]) -> tuple[int, ...]:
        memo: dict[int, int] = {}

        def visit(node: int) -> int:
            if node in memo:
                return memo[node]
            record = self.records[node]
            if record[0] == "terminal":
                name = str(record[1])
                require(name in environment, f"missing terminal {name}")
                result = environment[name]
            elif record[0] == "u":
                result = unary_u(visit(int(record[1])))
            else:
                require(record[0] == "d", "unknown operation")
                result = discriminator(
                    visit(int(record[1])), visit(int(record[2])), visit(int(record[3]))
                )
            memo[node] = result
            return result

        return tuple(visit(root) for root in roots)

    def dependencies(self, roots: Iterable[int]) -> frozenset[str]:
        memo: dict[int, frozenset[str]] = {}

        def visit(node: int) -> frozenset[str]:
            if node in memo:
                return memo[node]
            record = self.records[node]
            if record[0] == "terminal":
                result = frozenset((str(record[1]),))
            elif record[0] == "u":
                result = visit(int(record[1]))
            else:
                result = (
                    visit(int(record[1]))
                    | visit(int(record[2]))
                    | visit(int(record[3]))
                )
            memo[node] = result
            return result

        answer: frozenset[str] = frozenset()
        for root in roots:
            answer |= visit(root)
        return answer


def boolean_and(dag: TermDAG, left: int, right: int, one: int) -> int:
    # d(x,1,y)=x and y on Boolean inputs.
    return dag.d(left, one, right)


def boolean_or(dag: TermDAG, left: int, right: int, zero: int) -> int:
    # d(x,0,y)=x or y on Boolean inputs.
    return dag.d(left, zero, right)


def digit_states(
    dag: TermDAG, digit: int, zero: int, one: int, two: int
) -> dict[tuple[int, ...], tuple[int, int]]:
    # Exact Q-valued equality indicators.  All outputs are Boolean.
    equal_zero = dag.u(dag.d(digit, two, one))
    equal_one = dag.d(digit, two, zero)
    equal_two = dag.u(dag.d(digit, zero, one))
    return {
        (0,): (equal_zero, zero),
        (1,): (equal_one, zero),
        (2,): (equal_two, equal_one),
    }


def balanced_states(
    dag: TermDAG,
    digits: tuple[int, ...],
    zero: int,
    one: int,
    two: int,
) -> dict[tuple[int, ...], tuple[int, int]]:
    if not digits:
        return {(): (one, zero)}
    if len(digits) == 1:
        return digit_states(dag, digits[0], zero, one, two)
    split = len(digits) // 2
    left = balanced_states(dag, digits[:split], zero, one, two)
    right = balanced_states(dag, digits[split:], zero, one, two)
    result: dict[tuple[int, ...], tuple[int, int]] = {}
    for left_word, (equal_left, good_left) in left.items():
        for right_word, (equal_right, good_right) in right.items():
            equal = boolean_and(dag, equal_left, equal_right, one)
            guarded_good_right = boolean_and(dag, equal_left, good_right, one)
            good = boolean_or(dag, good_left, guarded_good_right, zero)
            result[left_word + right_word] = (equal, good)
    return result


def build_program_vector(
    width: int,
    root_sign: int,
    mode: Mode = "projection",
    constant: int = 0,
) -> tuple[TermDAG, dict[tuple[int, ...], tuple[int, int]], tuple[int, ...]]:
    dag = TermDAG()
    anchor = dag.terminal("A")
    one = dag.u(anchor)
    zero = dag.u(one)
    two = anchor
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    pairs: dict[tuple[int, ...], tuple[int, int]] = {}
    if mode == "constant":
        require(constant in (0, 1), "bad vector constant")
        for physical in words(width):
            sign = cell_sign(root_sign, physical)
            if sign == 0:
                pairs[physical] = (one if constant == 0 else zero, zero if constant == 0 else one)
            else:
                pairs[physical] = (zero if constant == 0 else one, zero if constant == 0 else one)
        return dag, pairs, digits

    if width == 0:
        pairs[()] = (zero, zero) if root_sign == 0 else (zero, one)
        return dag, pairs, digits
    states = balanced_states(dag, digits, zero, one, two)
    for physical, (equal, good) in states.items():
        active = boolean_or(dag, equal, good, zero)
        if cell_sign(root_sign, physical) == 0:
            pairs[physical] = (dag.u(active), good)
        else:
            pairs[physical] = (good, active)
    return dag, pairs, digits


def evaluate_program(
    dag: TermDAG,
    pairs: dict[tuple[int, ...], tuple[int, int]],
    target: tuple[int, ...],
    anchor: int = 2,
) -> tuple[int, ...]:
    roots = tuple(root for physical in words(len(target)) for root in pairs[physical])
    environment = {"A": anchor, **{f"t{index}": value for index, value in enumerate(target)}}
    return dag.evaluate_many(roots, environment)


def router_labels(width: int, root_sign: int) -> tuple[int, ...]:
    labels: list[int] = []
    for branch, physical in enumerate(words(width), start=1):
        sign = cell_sign(root_sign, physical)
        labels.extend((branch, CONTROL, CONTROL) if sign == 0 else (CONTROL, branch, CONTROL))
    return tuple(labels)


def concrete_router(labels: tuple[int, ...], program: tuple[int, ...], values: tuple[int, ...]) -> int:
    require(labels.count(CONTROL) == len(program), "program width mismatch")
    iterator = iter(program)
    layer = [next(iterator) if label == CONTROL else values[label - 1] for label in labels]
    while len(layer) > 1:
        require(len(layer) % 3 == 0, "malformed router layer")
        layer = [
            discriminator(layer[index], layer[index + 1], layer[index + 2])
            for index in range(0, len(layer), 3)
        ]
    return layer[0]


class DirectTernaryROBDD:
    """Canonical ROBDD using d itself as the primitive apply operation."""

    def __init__(self) -> None:
        self.nodes: list[tuple[int, int, int] | None] = [None, None]
        self.unique: dict[tuple[int, int, int], int] = {}
        self.cache: dict[tuple[int, int, int], int] = {}

    def make(self, variable: int, low: int, high: int) -> int:
        if low == high:
            return low
        key = (variable, low, high)
        if key not in self.unique:
            self.unique[key] = len(self.nodes)
            self.nodes.append(key)
        return self.unique[key]

    def variable(self, index: int) -> int:
        return self.make(index, 0, 1)

    def top(self, node: int) -> int:
        record = self.nodes[node]
        return record[0] if record is not None else 10**9

    def cofactor(self, node: int, variable: int, bit: int) -> int:
        record = self.nodes[node]
        if record is None or record[0] != variable:
            return node
        return record[1 + bit]

    def apply_d(self, x: int, y: int, z: int) -> int:
        key = (x, y, z)
        if key in self.cache:
            return self.cache[key]
        if x < 2 and y < 2 and z < 2:
            result = discriminator(x, y, z)
        else:
            variable = min(self.top(x), self.top(y), self.top(z))
            result = self.make(
                variable,
                self.apply_d(
                    self.cofactor(x, variable, 0),
                    self.cofactor(y, variable, 0),
                    self.cofactor(z, variable, 0),
                ),
                self.apply_d(
                    self.cofactor(x, variable, 1),
                    self.cofactor(y, variable, 1),
                    self.cofactor(z, variable, 1),
                ),
            )
        self.cache[key] = result
        return result

    def evaluate_router(
        self,
        labels: tuple[int, ...],
        program: tuple[int, ...],
        variables: tuple[int, ...],
    ) -> int:
        iterator = iter(program)
        layer = [next(iterator) if label == CONTROL else variables[label - 1] for label in labels]
        while len(layer) > 1:
            layer = [
                self.apply_d(layer[index], layer[index + 1], layer[index + 2])
                for index in range(0, len(layer), 3)
            ]
        return layer[0]


@cache
def state_node_upper(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 5
    left = width // 2
    right = width - left
    return state_node_upper(left) + state_node_upper(right) + 3 * 3**width


def vector_node_upper(width: int) -> int:
    if width == 0:
        return 0
    capacity = 3**width
    positive_cells = (capacity + 1) // 2
    return state_node_upper(width) + capacity + positive_cells


def ceil_log(base: int, value: int) -> int:
    require(base >= 2 and value >= 1, "bad ceil-log input")
    power = 1
    exponent = 0
    while power < value:
        power *= base
        exponent += 1
    return exponent


def floor_power_three(value: int) -> tuple[int, int]:
    require(value >= 1, "bad floor-power input")
    exponent = 0
    power = 1
    while power * 3 <= value:
        power *= 3
        exponent += 1
    return exponent, power


def vector_depth_above_anchor(width: int) -> int:
    # Even the width-zero base program uses zero=u(u(A)) and one=u(A).
    return 2 if width == 0 else 6 + 2 * ceil_log(2, width)


def vector_checks() -> dict[str, object]:
    rows = []
    semantic_pair_checks = 0
    dependency_checks = 0
    for width in range(0, 9):
        capacity = 3**width
        for root_sign in (0, 1):
            dag, pairs, _ = build_program_vector(width, root_sign)
            generated_nodes = dag.operation_count - 2  # shared one=u(A), zero=u(one)
            upper = vector_node_upper(width)
            require(generated_nodes <= upper, "vector syntax count exceeded recurrence")
            require(upper <= 7 * capacity, "linear vector bound failed")
            pair_depth = max(dag.depths[root] for pair in pairs.values() for root in pair)
            require(
                pair_depth <= vector_depth_above_anchor(width),
                "balanced vector depth bound failed",
            )
            dependencies = dag.dependencies(root for pair in pairs.values() for root in pair)
            require(
                dependencies <= frozenset(("A", *(f"t{index}" for index in range(width)))),
                "program vector acquired a payload dependency",
            )
            dependency_checks += 1

            if width <= 6:
                for target in words(width):
                    program = evaluate_program(dag, pairs, target)
                    for index, physical in enumerate(words(width)):
                        expected = expected_pair(root_sign, physical, target, "projection")
                        require(
                            program[2 * index : 2 * index + 2] == expected,
                            f"program pair mismatch at {width}:{root_sign}:{target}:{physical}",
                        )
                        semantic_pair_checks += 1
                for constant in (0, 1):
                    constant_dag, constant_pairs, _ = build_program_vector(
                        width, root_sign, "constant", constant
                    )
                    require(constant_dag.operation_count == 2, "constant vector created hidden operations")
                    program = evaluate_program(constant_dag, constant_pairs, (0,) * width)
                    for index, physical in enumerate(words(width)):
                        require(
                            program[2 * index : 2 * index + 2]
                            == expected_pair(root_sign, physical, None, "constant", constant),
                            "constant pair mismatch",
                        )
                        semantic_pair_checks += 1

            rows.append(
                {
                    "width": width,
                    "root_sign": "P" if root_sign == 0 else "N",
                    "capacity": capacity,
                    "generated_operation_nodes_excluding_shared_names": generated_nodes,
                    "certified_node_upper": upper,
                    "program_depth_above_raw_anchor": pair_depth,
                    "certified_depth_upper": vector_depth_above_anchor(width),
                }
            )
    return {
        "rows": rows,
        "semantic_pair_checks": semantic_pair_checks,
        "dependency_checks": dependency_checks,
    }


def router_checks() -> dict[str, object]:
    concrete_checks = 0
    bdd_checks = 0
    last_bdd_nodes = 0
    for width in range(0, 5):
        capacity = 3**width
        variables_bdd = DirectTernaryROBDD()
        variables = tuple(variables_bdd.variable(index) for index in range(capacity))
        for root_sign in (0, 1):
            labels = router_labels(width, root_sign)
            dag, pairs, _ = build_program_vector(width, root_sign)
            for target_index, target in enumerate(words(width)):
                program = evaluate_program(dag, pairs, target)
                root = variables_bdd.evaluate_router(labels, program, variables)
                expected = (
                    variables[target_index]
                    if root_sign == 0
                    else variables_bdd.make(target_index, 1, 0)
                )
                require(root == expected, "ROBDD projection/complement mismatch")
                bdd_checks += 1
                if width <= 2:
                    for valuation in product((0, 1), repeat=capacity):
                        expected_value = valuation[target_index] ^ root_sign
                        require(
                            concrete_router(labels, program, valuation) == expected_value,
                            "concrete projection/complement mismatch",
                        )
                        concrete_checks += 1
            for constant in (0, 1):
                const_dag, const_pairs, _ = build_program_vector(
                    width, root_sign, "constant", constant
                )
                program = evaluate_program(const_dag, const_pairs, (0,) * width)
                root = variables_bdd.evaluate_router(labels, program, variables)
                require(root == constant, "ROBDD constant mode mismatch")
                bdd_checks += 1
                if width <= 2:
                    for valuation in product((0, 1), repeat=capacity):
                        require(
                            concrete_router(labels, program, valuation) == constant,
                            "concrete constant mode mismatch",
                        )
                        concrete_checks += 1
        last_bdd_nodes = len(variables_bdd.nodes)

    # Padding: repeat the last live branch in every unused slot.  Programs only
    # request live target words, so padding must be unreachable.
    padding_checks = 0
    for width in range(1, 5):
        capacity = 3**width
        live = capacity - 1
        bdd = DirectTernaryROBDD()
        variables = tuple(bdd.variable(index) for index in range(live))
        for root_sign in (0, 1):
            raw_labels = router_labels(width, root_sign)
            labels = tuple(live if label == capacity else label for label in raw_labels)
            dag, pairs, _ = build_program_vector(width, root_sign)
            for target_index, target in enumerate(words(width)[:live]):
                program = evaluate_program(dag, pairs, target)
                root = bdd.evaluate_router(labels, program, variables)
                expected = variables[target_index] if root_sign == 0 else bdd.make(target_index, 1, 0)
                require(root == expected, "repeated-last padding changed live projection")
                padding_checks += 1
    return {
        "concrete_router_checks_through_width_two": concrete_checks,
        "direct_ternary_robdd_mode_checks_through_width_four": bdd_checks,
        "last_robdd_node_count": last_bdd_nodes,
        "padding_robdd_checks": padding_checks,
    }


def residual_first_widths(total: int, width: int) -> tuple[int, ...]:
    require(total >= 0 and width >= 1, "bad chunk dimensions")
    if total == 0:
        return ()
    remainder = total % width
    return ((remainder,) if remainder else ()) + (width,) * (total // width)


def prefix_instances(widths: tuple[int, ...], alphabet: int) -> tuple[int, int]:
    product_so_far = 1
    instances = 0
    for width in widths:
        instances += product_so_far
        product_so_far *= alphabet**width
    return instances, product_so_far


def compiler_parameters(arity: int) -> dict[str, int]:
    require(arity >= MIN_COMPILER_ARITY, "compiler arity below audited regime")
    reserve = C_PARAMETER + ceil_log(3, arity * arity)
    h_budget = arity - reserve
    require(h_budget >= 1, "empty local budget")
    block_coordinates, block_assignments = floor_power_three(h_budget)
    prefix_coordinates = arity - block_coordinates
    prefix_assignments = 3**prefix_coordinates

    local_library_nodes = (3 * block_assignments - 1) * 3**block_assignments
    local_program_nodes = vector_node_upper(block_coordinates)
    prefix_router_nodes = 3 * prefix_assignments - 1
    prefix_program_nodes = vector_node_upper(prefix_coordinates)
    anchor_nodes = 4 * (arity - 1)
    names_decoder_glue = 2 + 2 + 3
    nonbinary_nodes = (
        local_library_nodes
        + local_program_nodes
        + prefix_router_nodes
        + prefix_program_nodes
        + anchor_nodes
        + names_decoder_glue
    )

    anchor_depth = 3 * ceil_log(2, arity)
    local_control_depth = anchor_depth + vector_depth_above_anchor(block_coordinates)
    local_plane_depth = max(anchor_depth + 2, local_control_depth) + block_coordinates + 1
    prefix_control_depth = anchor_depth + vector_depth_above_anchor(prefix_coordinates)
    prefix_plane_depth = max(local_plane_depth, prefix_control_depth) + prefix_coordinates + 1
    nonbinary_depth_with_decoder_glue = prefix_plane_depth + 2 + 2

    # Retained, independently audited binary schedule: a square-root signed
    # router, residual-first binary chunks, relative controls x0/u(x0).
    binary_k = math.isqrt(arity)
    binary_capacity = 3**binary_k
    binary_router_depth = binary_k + 1
    binary_router_nodes_each = (3 * binary_capacity - 1) // 2
    binary_width = binary_capacity.bit_length() - 1
    binary_widths = residual_first_widths(arity - 1, binary_width)
    binary_instances, binary_assignments = prefix_instances(binary_widths, 2)
    require(binary_assignments == 2 ** (arity - 1), "binary address product drift")
    binary_nodes = (
        binary_router_nodes_each * binary_instances
        + sum(6 * binary_capacity * (2**width - 1) for width in binary_widths)
        + 4 * arity
        + 10
    )
    binary_depth = (
        binary_router_depth * len(binary_widths)
        + 2 * binary_width
        + anchor_depth
        + 8
    )
    return {
        "arity": arity,
        "reserve": reserve,
        "H": h_budget,
        "block_coordinates": block_coordinates,
        "M": block_assignments,
        "prefix_coordinates": prefix_coordinates,
        "P": prefix_assignments,
        "local_library_nodes": local_library_nodes,
        "local_program_nodes": local_program_nodes,
        "prefix_router_nodes": prefix_router_nodes,
        "prefix_program_nodes": prefix_program_nodes,
        "nonbinary_nodes": nonbinary_nodes,
        "nonbinary_depth": nonbinary_depth_with_decoder_glue,
        "binary_k": binary_k,
        "binary_capacity": binary_capacity,
        "binary_width": binary_width,
        "binary_levels": len(binary_widths),
        "binary_nodes": binary_nodes,
        "binary_depth": binary_depth,
    }


def decimal_ratio(numerator: int, denominator: int) -> str:
    getcontext().prec = 16
    return format(Decimal(numerator) / Decimal(denominator), ".12f")


def compiler_checks() -> dict[str, object]:
    selected_arities = (64, 90, 93, 94, 128, 256, 338, 339, 512, 900, 1024, 2048, 4096)
    selected = []
    max_ratio_numerator = 0
    max_ratio_denominator = 1
    max_ratio_arity = 0
    exact_rows = 0
    binary_below_r_from = None
    for arity in range(MIN_COMPILER_ARITY, 4097):
        row = compiler_parameters(arity)
        target_denominator = 3**arity
        require(2 * row["H"] >= arity, "H lost the r/2 lower bound")
        require(row["M"] <= row["H"] < 3 * row["M"], "largest-power choice drift")
        require(
            81 * row["M"] * 3 ** row["M"] * arity <= target_denominator,
            "local library reserve inequality failed",
        )
        require(
            row["nonbinary_nodes"] * arity <= 62 * target_denominator,
            "nonbinary size constant failed",
        )
        require(
            row["binary_nodes"] * arity <= target_denominator,
            "retained binary size ceased to be lower order",
        )
        require(
            row["nonbinary_depth"]
            <= arity + 5 * ceil_log(2, arity) + 12,
            "nonbinary logarithmic depth bound failed",
        )
        if arity >= 339:
            require(row["binary_depth"] < arity, "binary depth no longer below r")
            if binary_below_r_from is None:
                binary_below_r_from = arity
        numerator = row["nonbinary_nodes"] * arity
        if numerator * max_ratio_denominator > max_ratio_numerator * target_denominator:
            max_ratio_numerator = numerator
            max_ratio_denominator = target_denominator
            max_ratio_arity = arity
        if arity in selected_arities:
            selected.append(
                {
                    "arity": arity,
                    "H": row["H"],
                    "block_coordinates": row["block_coordinates"],
                    "M": row["M"],
                    "prefix_coordinates": row["prefix_coordinates"],
                    "nonbinary_size_over_3r_over_r": decimal_ratio(numerator, target_denominator),
                    "nonbinary_depth": row["nonbinary_depth"],
                    "certified_depth_bound": arity + 5 * ceil_log(2, arity) + 12,
                    "binary_depth": row["binary_depth"],
                }
            )
        exact_rows += 1

    # Analytic tail gate for binary depth.  For k=floor(sqrt r)>=30,
    # floor(log2(3^k)) >= floor(3k/2), <2k, and ceil(log2 r)<=k.
    # The displayed polynomial proves the conservative binary bound is <r.
    analytic_binary_k = 30
    require(
        analytic_binary_k**3
        - 27 * analytic_binary_k**2
        - 19 * analytic_binary_k
        + 9
        > 0,
        "binary analytic threshold failed",
    )

    # Exact base witnesses for the analytic size tail.  For r>=64, Q<N,
    # router cost is below 12N, and each displayed normalized contribution is
    # below 1/4, 6/r^2, and 1/4 respectively.  The square-boundary inequality
    # controls q^2=3^(2*floor(sqrt(r))).
    analytic_size_r = 64
    analytic_size_k = math.isqrt(analytic_size_r)
    require(
        3**analytic_size_k < 2 ** (analytic_size_r - 1),
        "binary Q<N base witness failed",
    )
    require(
        24 * analytic_size_r * 2**analytic_size_r < 3**analytic_size_r,
        "binary router quarter-unit witness failed",
    )
    require(24 < analytic_size_r**2, "binary control quarter-unit witness failed")
    require(
        3 ** (analytic_size_k**2 - 2 * analytic_size_k) >= analytic_size_k**8,
        "binary square-boundary exponent witness failed",
    )
    require(
        4 * (4 * analytic_size_r + 10) * analytic_size_r < 3**analytic_size_r,
        "binary fixed-overhead quarter-unit witness failed",
    )
    require(
        (11 * analytic_size_r + 7) * analytic_size_r < 3**analytic_size_r,
        "nonbinary lower-order unit witness failed",
    )

    # Killer mutation: reserving only one log_3(r) loses the M factor in the
    # local library.  At this exact arity it already exceeds the entire 62-unit
    # size allowance used above.
    bad_arity = 6574
    bad_h = bad_arity - (C_PARAMETER + ceil_log(3, bad_arity))
    _, bad_m = floor_power_three(bad_h)
    bad_local = (3 * bad_m - 1) * 3**bad_m
    require(bad_m == 6561, "single-log mutation target drift")
    require(
        bad_local * bad_arity > 62 * 3**bad_arity,
        "single-log reserve mutation unexpectedly survived",
    )

    # Naively compiling q controls one at a time for width w costs Omega(qw).
    # At the giant prefix this has an unbounded factor over 3^r/r.
    naive_arity = 512
    naive = compiler_parameters(naive_arity)
    naive_vector_nodes = naive["P"] * naive["prefix_coordinates"]
    require(
        naive_vector_nodes * naive_arity > 100 * 3**naive_arity,
        "sequential program-vector mutation unexpectedly stayed order optimal",
    )

    return {
        "C": C_PARAMETER,
        "arities_checked": exact_rows,
        "arity_range": [MIN_COMPILER_ARITY, 4096],
        "selected_rows": selected,
        "maximum_checked_nonbinary_normalized_size": {
            "arity": max_ratio_arity,
            "ratio": decimal_ratio(max_ratio_numerator, max_ratio_denominator),
        },
        "analytic_nonbinary_size_bound": "nonbinary_nodes <= 62*3^r/r for r>=64",
        "analytic_nonbinary_depth_bound": "nonbinary_depth <= r+5*ceil(log_2 r)+12",
        "binary_below_r_from_checked_arity": binary_below_r_from,
        "binary_tail_proof_threshold": "k=floor(sqrt(r))>=30, hence r>=900",
        "analytic_size_base_witness": {
            "arity": analytic_size_r,
            "Q_less_than_N": True,
            "router_normalized_below_one_quarter": True,
            "controls_normalized_below_6_over_r_squared": True,
            "fixed_overhead_normalized_below_one_quarter": True,
            "nonbinary_lower_order_normalized_below_one": True,
        },
        "single_log_reserve_mutation": {
            "arity": bad_arity,
            "H": bad_h,
            "M": bad_m,
            "verdict": "REJECTED_LOCAL_LIBRARY_EXCEEDS_62_TIMES_TARGET",
        },
        "sequential_vector_mutation": {
            "arity": naive_arity,
            "verdict": "REJECTED_PREFIX_PROGRAM_COST_EXCEEDS_100_TIMES_TARGET",
        },
    }


def falsifier_checks() -> dict[str, object]:
    # Truth tables of the exact Boolean primitives used in the composition.
    primitive_rows = 0
    for left, right in product((0, 1), repeat=2):
        require(discriminator(left, 1, right) == (left & right), "AND formula failed")
        require(discriminator(left, 0, right) == (left | right), "OR formula failed")
        require(unary_u(left) == 1 - left, "NOT formula failed")
        primitive_rows += 1

    # Minimal counterexample to dropping the E_A guard in G_AB.
    target = (0, 1)
    physical = (1, 2)
    equal, good = first_mismatch_state(target, physical)
    wrong_good = int(target[1] == 1 and physical[1] == 2)
    require((equal, good, wrong_good) == (0, 0, 1), "G guard counterexample drift")

    # Swapping the positive and negative base program destroys P1 projection.
    swapped_outputs = tuple(discriminator(x, 0, 1) for x in (0, 1))
    require(swapped_outputs == (1, 1), "sign-swap counterexample drift")

    # Absolute names from A are legal only on A=2.  Re-evaluate a width-one
    # vector with a binary anchor and demand a concrete mismatch.
    dag, pairs, _ = build_program_vector(1, 0)
    expected = evaluate_program(dag, pairs, (0,), anchor=2)
    illegal = evaluate_program(dag, pairs, (0,), anchor=0)
    require(expected != illegal, "binary absolute-name mutation unexpectedly survived")

    return {
        "boolean_primitive_rows": primitive_rows,
        "unguarded_G_counterexample": {
            "target": list(target),
            "physical": list(physical),
            "correct_E_G": [equal, good],
            "wrong_G": wrong_good,
        },
        "swapped_sign_counterexample": {
            "term": "P1 with N1 projection pair (0,1)",
            "outputs_at_x_0_1": list(swapped_outputs),
        },
        "binary_absolute_constants_rejected": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path, expected in FROZEN_HASHES.items():
        require(sha256_path(path) == expected, f"frozen input drift: {path}")

    vector = vector_checks()
    routers = router_checks()
    compiler = compiler_checks()
    falsifiers = falsifier_checks()
    payload: dict[str, object] = {
        "schema": "orbit-synthesis/parallel-program-vector/v1",
        "status": "PASS_EXACT_VECTOR_CONDITIONAL_COMPILER",
        "frozen_inputs": {str(path.relative_to(ROOT)): digest for path, digest in FROZEN_HASHES.items()},
        "theorem": {
            "state": "E_p=[t=p], G_p=[the first mismatch has (t_j,p_j)=(1,2)]",
            "composition": "E_AB=E_A and E_B; G_AB=G_A or (E_A and G_B)",
            "positive_cell_pair": "(not(E or G), G)",
            "negative_cell_pair": "(G, E or G)",
            "constant_positive_pair": "(1-c,c)",
            "constant_negative_pair": "(c,c)",
            "size": "at most 7*3^w d/u nodes beyond the two shared anchor names",
            "depth": "at most 6+2*ceil(log_2 w) above the raw anchor and address digits",
        },
        "vector_checks": vector,
        "router_checks": routers,
        "compiler_checks": compiler,
        "falsifier_checks": falsifiers,
        "original_signature_boundary": (
            "On the nonbinary branch A=2 legally supplies one=u(A), zero=u(u(A)), "
            "and two=A. Equality indicators, AND, OR, and NOT are explicit d/u terms. "
            "On the binary branch these are not absolute constants; the compiler retains "
            "the separately audited complement-relative x0/u(x0) construction."
        ),
        "compiler_boundary": (
            "The program-vector theorem and its giant nonbinary local/prefix ledger are "
            "proved here. The full parameter-free compiler still composes frozen anchor, "
            "selector-table, binary-branch, decoder, and glue lemmas; it is not a new "
            "standalone semantic characterization of conservative Q terms."
        ),
        "claim_boundary": (
            "Research-only. No novelty, optimality beyond the displayed construction, "
            "practical speedup, unshared-formula bound, Lean proof, patent/FTO, license, "
            "Tau, or publication claim follows."
        ),
    }
    payload["semantic_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("PASS parallel program-vector compiler")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

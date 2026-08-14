#!/usr/bin/env python3
"""Independent audit of Boolean-rail program-vector constructions.

This file imports no candidate implementation.  It reconstructs the direct
Kuhn rails, the native-scan bad/gain/not-bad construction, and a conservative
zero-gain-reuse refinement in the original {d,u} signature.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import deque
from functools import cache
from pathlib import Path
from typing import Iterable, Sequence


STATE_SHA256 = "6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6"
KUHN_SHA256 = "3b02d4cd842e7b8b252a38b3cdcb4fb2fc6044cf04f72b0b0250709a6cda2785"
NATIVE_SHA256 = "a41114a8f7bf21bd34d32b9fcc4b46e4558110de1aeb76817a071168c6d501e0"
OPTIMAL_SHA256 = "02da40907d0495fbbc5e4d2a9420952c2676ece1229ed0fffbb22c757dda2b16"
SCHEMA = "orbit.program-vector.referee.boolean-rails.v1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def d(x: int, y: int, z: int) -> int:
    require(x in (0, 1, 2) and y in (0, 1, 2) and z in (0, 1, 2), "d outside Q")
    return z if x == y else x


def u(x: int) -> int:
    require(x in (0, 1, 2), "u outside Q")
    return (1, 0, 1)[x]


@cache
def words(width: int) -> tuple[tuple[int, ...], ...]:
    require(width >= 0, "negative width")
    return tuple(itertools.product((0, 1, 2), repeat=width))


def parity(word: Sequence[int]) -> int:
    return sum(digit == 1 for digit in word) & 1


def negative_cell(root_negative: bool, physical: Sequence[int]) -> bool:
    return bool(root_negative) ^ bool(parity(physical))


def direct_triple(target: Sequence[int], physical: Sequence[int]) -> tuple[int, int, int]:
    """Return (bad/zero-mode, gain/one-mode, not-bad)."""
    require(len(target) == len(physical), "word-width mismatch")
    for requested, placed in zip(target, physical, strict=True):
        if requested != placed:
            gain = int(requested == 1 and placed == 2)
            bad = 1 - gain
            return bad, gain, 1 - bad
    return 0, 0, 1


def expected_pair(
    root_negative: bool, target: Sequence[int], physical: Sequence[int]
) -> tuple[int, int]:
    bad, gain, not_bad = direct_triple(target, physical)
    return (gain, not_bad) if negative_cell(root_negative, physical) else (bad, gain)


class DAG:
    """Purely syntactic hash-consed scalar term DAG."""

    def __init__(self) -> None:
        self.nodes: list[tuple[object, ...]] = []
        self.depth: list[int] = []
        self.unique: dict[tuple[object, ...], int] = {}

    def _intern(self, node: tuple[object, ...], depth: int) -> int:
        old = self.unique.get(node)
        if old is not None:
            return old
        result = len(self.nodes)
        self.nodes.append(node)
        self.depth.append(depth)
        self.unique[node] = result
        return result

    def terminal(self, name: str) -> int:
        return self._intern(("var", name), 0)

    def unary(self, child: int) -> int:
        return self._intern(("u", child), self.depth[child] + 1)

    def discr(self, left: int, middle: int, right: int) -> int:
        return self._intern(
            ("d", left, middle, right),
            max(self.depth[left], self.depth[middle], self.depth[right]) + 1,
        )

    @property
    def operation_count(self) -> int:
        return sum(node[0] != "var" for node in self.nodes)

    def reachable(self, roots: Iterable[int]) -> frozenset[int]:
        seen: set[int] = set()
        stack = list(roots)
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            node = self.nodes[node_id]
            if node[0] == "u":
                stack.append(int(node[1]))
            elif node[0] == "d":
                stack.extend((int(node[1]), int(node[2]), int(node[3])))
        return frozenset(seen)

    def reachable_operation_count(self, roots: Iterable[int]) -> int:
        return sum(self.nodes[node][0] != "var" for node in self.reachable(roots))

    def dependencies(self, roots: Iterable[int]) -> frozenset[str]:
        return frozenset(
            str(self.nodes[node][1])
            for node in self.reachable(roots)
            if self.nodes[node][0] == "var"
        )

    def evaluate(self, roots: Iterable[int], environment: dict[str, int]) -> tuple[int, ...]:
        values = [0] * len(self.nodes)
        for node_id, node in enumerate(self.nodes):
            if node[0] == "var":
                values[node_id] = environment[str(node[1])]
            elif node[0] == "u":
                values[node_id] = u(values[int(node[1])])
            else:
                require(node[0] == "d", "unknown DAG node")
                values[node_id] = d(
                    values[int(node[1])], values[int(node[2])], values[int(node[3])]
                )
        return tuple(values[root] for root in roots)


def add_names(dag: DAG) -> tuple[int, int, int]:
    two = dag.terminal("A")
    one = dag.unary(two)
    zero = dag.unary(one)
    return two, one, zero


PairMap = dict[tuple[int, ...], tuple[int, int]]
BGMap = dict[tuple[int, ...], tuple[int, int]]
BGNMap = dict[tuple[int, ...], tuple[int, int, int]]


def digit_bgn(dag: DAG, digit: int, two: int, one: int, zero: int) -> BGNMap:
    bad_zero = dag.discr(digit, two, one)       # (0,1,1)
    bad_two = dag.unary(bad_zero)               # (1,0,0)
    gain_two = dag.discr(digit, two, zero)       # (0,1,0)
    bad_one = dag.discr(one, digit, zero)        # (1,0,1)
    return {
        (0,): (bad_zero, zero, bad_two),
        (1,): (bad_one, zero, gain_two),
        (2,): (bad_two, gain_two, bad_zero),
    }


def build_bg(
    dag: DAG,
    digits: tuple[int, ...],
    two: int,
    one: int,
    zero: int,
    reuse_zero_gain: bool,
) -> BGMap:
    require(digits, "empty BG block")
    if len(digits) == 1:
        return {
            physical: (bad, gain)
            for physical, (bad, gain, _not_bad) in digit_bgn(
                dag, digits[0], two, one, zero
            ).items()
        }
    left_width = (len(digits) + 1) // 2
    left = build_bg(dag, digits[:left_width], two, one, zero, reuse_zero_gain)
    right = build_bg(dag, digits[left_width:], two, one, zero, reuse_zero_gain)
    result: BGMap = {}
    for p_left, (bad_left, gain_left) in left.items():
        for p_right, (bad_right, gain_right) in right.items():
            bad = dag.discr(bad_left, gain_left, bad_right)
            gain = (
                gain_left
                if reuse_zero_gain and gain_right == zero
                else dag.discr(gain_left, bad_left, gain_right)
            )
            result[p_left + p_right] = bad, gain
    return result


def build_bgn(
    dag: DAG,
    digits: tuple[int, ...],
    two: int,
    one: int,
    zero: int,
    reuse_zero_gain: bool,
) -> BGNMap:
    require(digits, "empty BGN block")
    if len(digits) == 1:
        return digit_bgn(dag, digits[0], two, one, zero)
    left_width = (len(digits) + 1) // 2
    left = build_bg(dag, digits[:left_width], two, one, zero, reuse_zero_gain)
    right = build_bgn(dag, digits[left_width:], two, one, zero, reuse_zero_gain)
    result: BGNMap = {}
    for p_left, (bad_left, gain_left) in left.items():
        for p_right, (bad_right, gain_right, not_bad_right) in right.items():
            bad = dag.discr(bad_left, gain_left, bad_right)
            gain = (
                gain_left
                if reuse_zero_gain and gain_right == zero
                else dag.discr(gain_left, bad_left, gain_right)
            )
            not_bad = dag.discr(gain_left, bad_left, not_bad_right)
            result[p_left + p_right] = bad, gain, not_bad
    return result


def build_native_vector(width: int, root_negative: bool, reuse_zero_gain: bool) -> tuple[DAG, PairMap]:
    require(width >= 1, "native projection width must be positive")
    dag = DAG()
    two, one, zero = add_names(dag)
    digits = tuple(dag.terminal(f"t{i}") for i in range(width))
    if width == 1:
        states = digit_bgn(dag, digits[0], two, one, zero)
        return dag, {
            physical: ((gain, not_bad) if negative_cell(root_negative, physical) else (bad, gain))
            for physical, (bad, gain, not_bad) in states.items()
        }
    left_width = (width + 1) // 2
    left = build_bg(dag, digits[:left_width], two, one, zero, reuse_zero_gain)
    right = build_bgn(dag, digits[left_width:], two, one, zero, reuse_zero_gain)
    pairs: PairMap = {}
    for p_left, (bad_left, gain_left) in left.items():
        for p_right, (bad_right, gain_right, not_bad_right) in right.items():
            physical = p_left + p_right
            gain = (
                gain_left
                if reuse_zero_gain and gain_right == zero
                else dag.discr(gain_left, bad_left, gain_right)
            )
            if negative_cell(root_negative, physical):
                pairs[physical] = gain, dag.discr(gain_left, bad_left, not_bad_right)
            else:
                pairs[physical] = dag.discr(bad_left, gain_left, bad_right), gain
    return dag, pairs


def build_direct_rail_block(
    dag: DAG, digits: tuple[int, ...], two: int, one: int, zero: int
) -> BGMap:
    require(digits, "empty direct-rail block")
    if len(digits) == 1:
        x = digits[0]
        bad_zero = dag.discr(x, two, one)
        bad_one = dag.discr(one, x, zero)
        bad_two = dag.discr(zero, x, one)
        gain_two = dag.discr(x, two, zero)
        return {
            (0,): (bad_zero, zero),
            (1,): (bad_one, zero),
            (2,): (bad_two, gain_two),
        }
    split = len(digits) // 2
    left = build_direct_rail_block(dag, digits[:split], two, one, zero)
    right = build_direct_rail_block(dag, digits[split:], two, one, zero)
    result: BGMap = {}
    for p_left, (bad_left, gain_left) in left.items():
        for p_right, (bad_right, gain_right) in right.items():
            bad = dag.discr(bad_left, gain_left, bad_right)
            gain = (
                gain_left
                if gain_right == zero
                else dag.discr(gain_left, bad_left, gain_right)
            )
            result[p_left + p_right] = bad, gain
    return result


def build_direct_rail_vector(width: int, root_negative: bool) -> tuple[DAG, PairMap]:
    dag = DAG()
    two, one, zero = add_names(dag)
    if width == 0:
        return dag, {(): (zero, one) if root_negative else (zero, zero)}
    digits = tuple(dag.terminal(f"t{i}") for i in range(width))
    rails = build_direct_rail_block(dag, digits, two, one, zero)
    return dag, {
        physical: ((gain, dag.unary(bad)) if negative_cell(root_negative, physical) else (bad, gain))
        for physical, (bad, gain) in rails.items()
    }


def roots_of(pairs: PairMap) -> tuple[int, ...]:
    return tuple(root for physical in sorted(pairs) for root in pairs[physical])


def evaluate_and_collect_functions(
    dag: DAG, pairs: PairMap, width: int, root_negative: bool
) -> tuple[int, int]:
    roots = roots_of(pairs)
    columns = [[] for _ in roots]
    for target in words(width):
        environment = {"A": 2, **{f"t{i}": value for i, value in enumerate(target)}}
        values = dag.evaluate(roots, environment)
        for index, physical in enumerate(sorted(pairs)):
            actual = values[2 * index : 2 * index + 2]
            require(actual == expected_pair(root_negative, target, physical), "control mismatch")
        for column, value in zip(columns, values, strict=True):
            column.append(value)
    functions = tuple(tuple(column) for column in columns)
    return len(set(functions)), len(set(roots))


@cache
def direct_rail_count(width: int) -> int:
    require(width >= 1, "direct rail count width")
    if width == 1:
        return 4
    left = width // 2
    right = width - left
    q_left = 3**left
    q_right = 3**right
    return (
        direct_rail_count(left)
        + direct_rail_count(right)
        + 3**width
        + q_left * (q_right - 1) // 2
    )


def direct_vector_count(width: int, root_negative: bool) -> int:
    if width == 0:
        return 2
    q = 3**width
    negatives = (q + (1 if root_negative else -1)) // 2
    return 2 + direct_rail_count(width) + negatives


@cache
def bg_count(width: int, reuse_zero_gain: bool) -> int:
    require(width >= 1, "BG count width")
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    q = 3**width
    q_left = 3**left
    gain_nodes = (q - q_left) // 2 if reuse_zero_gain else 2 * q // 3
    return bg_count(left, reuse_zero_gain) + bg_count(right, reuse_zero_gain) + q + gain_nodes


@cache
def bgn_count(width: int, reuse_zero_gain: bool) -> int:
    require(width >= 1, "BGN count width")
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    q = 3**width
    q_left = 3**left
    gain_nodes = (q - q_left) // 2 if reuse_zero_gain else 2 * q // 3
    # q bad nodes, gain_nodes gain nodes, and q-q/3 new not-bad nodes.
    return (
        bg_count(left, reuse_zero_gain)
        + bgn_count(right, reuse_zero_gain)
        + q
        + gain_nodes
        + q
        - q // 3
    )


def native_vector_count(width: int, root_negative: bool, reuse_zero_gain: bool) -> int:
    require(width >= 1, "native vector count width")
    if width == 1:
        return 5 + int(root_negative)
    left = (width + 1) // 2
    right = width // 2
    q = 3**width
    q_left = 3**left
    gain_nodes = (q - q_left) // 2 if reuse_zero_gain else 2 * q // 3
    overlap = (q // 3 + (1 if not root_negative else -1)) // 2
    return (
        2
        + bg_count(left, reuse_zero_gain)
        + bgn_count(right, reuse_zero_gain)
        + gain_nodes
        + q
        - overlap
    )


def distinct_control_count(width: int, root_negative: bool) -> int:
    require(width >= 1, "distinct control count width")
    q = 3**width
    return 4 * q // 3 + int(root_negative)


def structural_checks(max_width: int, semantic_width: int) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    semantic_checks = 0
    for width in range(1, max_width + 1):
        q = 3**width
        for reuse in (False, True):
            label = "uncanonicalized_native_reference" if not reuse else "current_native_scan"

            bg_dag = DAG()
            two, one, zero = add_names(bg_dag)
            digits = tuple(bg_dag.terminal(f"t{i}") for i in range(width))
            bg = build_bg(bg_dag, digits, two, one, zero, reuse)
            bad_roots = {value[0] for value in bg.values()}
            gain_roots = {value[1] for value in bg.values()}
            expected_gain_roots = (q + 1) // 2 if reuse else 2 * q // 3
            require(bg_dag.operation_count - 2 == bg_count(width, reuse), "BG recurrence mismatch")
            require(len(bad_roots) == q, "BG bad roots not injective")
            require(len(gain_roots) == expected_gain_roots, "BG gain-root census mismatch")

            bgn_dag = DAG()
            two, one, zero = add_names(bgn_dag)
            digits = tuple(bgn_dag.terminal(f"t{i}") for i in range(width))
            bgn = build_bgn(bgn_dag, digits, two, one, zero, reuse)
            bad_roots = {value[0] for value in bgn.values()}
            gain_roots = {value[1] for value in bgn.values()}
            not_bad_roots = {value[2] for value in bgn.values()}
            require(bgn_dag.operation_count - 2 == bgn_count(width, reuse), "BGN recurrence mismatch")
            require(len(bad_roots) == q, "BGN bad roots not injective")
            require(len(gain_roots) == expected_gain_roots, "BGN gain-root census mismatch")
            require(len(not_bad_roots) == q, "BGN not-bad roots not injective")
            require(len(gain_roots & not_bad_roots) == q // 3, "gain/not-bad overlap mismatch")
            for prefix in words(width - 1):
                require(
                    bgn[prefix + (1,)][2] == bgn[prefix + (2,)][1],
                    "not_bad(a1)=gain(a2) sharing failed",
                )
            if reuse:
                for physical, (_bad, gain, _not_bad) in bgn.items():
                    require((gain == zero) == (2 not in physical), "canonical zero-gain root failed")

            for root_negative in (False, True):
                dag, pairs = build_native_vector(width, root_negative, reuse)
                roots = roots_of(pairs)
                reachable = dag.reachable_operation_count(roots)
                require(reachable == native_vector_count(width, root_negative, reuse), "native exact count mismatch")
                require(reachable <= 3 * q, "native 3q bound failed")
                require(
                    dag.dependencies(roots) == frozenset({"A", *(f"t{i}" for i in range(width))}),
                    "native dependency mismatch",
                )
                depth = max(dag.depth[root] for root in roots)
                require(depth <= 3 + (width - 1).bit_length(), "native depth mismatch")
                distinct_functions = None
                distinct_root_ids = len(set(roots))
                if reuse:
                    require(
                        distinct_root_ids == distinct_control_count(width, root_negative),
                        "current native output roots are not exactly function-canonical",
                    )
                if width <= semantic_width:
                    distinct_functions, distinct_root_ids = evaluate_and_collect_functions(
                        dag, pairs, width, root_negative
                    )
                    require(
                        distinct_functions == distinct_control_count(width, root_negative),
                        "distinct output-function formula failed",
                    )
                    semantic_checks += 2 * q * q
                rows.append(
                    {
                        "construction": label,
                        "width": width,
                        "root_sign": "N" if root_negative else "P",
                        "q": q,
                        "reachable_operation_nodes": reachable,
                        "allocated_operation_nodes": dag.operation_count,
                        "exact_recurrence_count": native_vector_count(width, root_negative, reuse),
                        "distinct_output_functions": distinct_functions,
                        "distinct_output_root_ids": distinct_root_ids,
                        "depth": depth,
                    }
                )

        for root_negative in (False, True):
            dag, pairs = build_direct_rail_vector(width, root_negative)
            roots = roots_of(pairs)
            reachable = dag.reachable_operation_count(roots)
            require(reachable == direct_vector_count(width, root_negative), "direct-rail exact count mismatch")
            require(reachable <= 3 * q, "direct-rail 3q bound failed")
            depth = max(dag.depth[root] for root in roots)
            require(depth <= 4 + (width - 1).bit_length(), "direct-rail depth mismatch")
            distinct_functions = None
            distinct_root_ids = len(set(roots))
            if width <= semantic_width:
                distinct_functions, distinct_root_ids = evaluate_and_collect_functions(
                    dag, pairs, width, root_negative
                )
                require(
                    distinct_functions == distinct_control_count(width, root_negative),
                    "direct distinct-output formula failed",
                )
                semantic_checks += 2 * q * q
            rows.append(
                {
                    "construction": "kuhn_direct_rails",
                    "width": width,
                    "root_sign": "N" if root_negative else "P",
                    "q": q,
                    "reachable_operation_nodes": reachable,
                    "allocated_operation_nodes": dag.operation_count,
                    "exact_recurrence_count": direct_vector_count(width, root_negative),
                    "distinct_output_functions": distinct_functions,
                    "distinct_output_root_ids": distinct_root_ids,
                    "depth": depth,
                }
            )
    return {"rows": rows, "semantic_scalar_comparisons": semantic_checks}


def constant_checks(max_width: int) -> int:
    checks = 0
    for width in range(max_width + 1):
        for root_negative in (False, True):
            for constant in (0, 1):
                dag = DAG()
                _two, one, zero = add_names(dag)
                pairs: PairMap = {}
                for physical in words(width):
                    if negative_cell(root_negative, physical):
                        pairs[physical] = (constant and one or zero, constant and one or zero)
                    else:
                        pairs[physical] = (zero if constant else one, one if constant else zero)
                require(dag.operation_count == 2, "constant names not charged")
                values = dag.evaluate(roots_of(pairs), {"A": 2})
                for index, physical in enumerate(sorted(pairs)):
                    expected = (
                        (constant, constant)
                        if negative_cell(root_negative, physical)
                        else (1 - constant, constant)
                    )
                    require(values[2 * index : 2 * index + 2] == expected, "constant pair failed")
                    checks += 1
    return checks


def semantic_output_census(max_width: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for width in range(1, max_width + 1):
        valuations = words(width)
        q = len(valuations)
        gains = {
            physical: tuple(direct_triple(target, physical)[1] for target in valuations)
            for physical in valuations
        }
        bads = {
            physical: tuple(direct_triple(target, physical)[0] for target in valuations)
            for physical in valuations
        }
        not_bads = {
            physical: tuple(1 - value for value in bads[physical])
            for physical in valuations
        }
        require(len(set(bads.values())) == q, "bad family not injective")
        require(len(set(not_bads.values())) == q, "not-bad family not injective")
        require(len(set(gains.values())) == (q + 1) // 2, "gain family count failed")
        for prefix in words(width - 1):
            require(
                not_bads[prefix + (1,)] == gains[prefix + (2,)],
                "semantic not_bad(a1)=gain(a2) failed",
            )
        for root_negative in (False, True):
            mixed = {
                physical: (
                    not_bads[physical]
                    if negative_cell(root_negative, physical)
                    else bads[physical]
                )
                for physical in valuations
            }
            gain_set = set(gains.values())
            mixed_set = set(mixed.values())
            overlap = len(gain_set & mixed_set)
            expected_overlap = (q // 3 + (1 if not root_negative else -1)) // 2
            require(len(mixed_set) == q, "mixed bad/not-bad family not injective")
            require(overlap == expected_overlap, "gain/mixed overlap count failed")
            distinct = len(gain_set | mixed_set)
            require(distinct == distinct_control_count(width, root_negative), "control union count failed")
            raw_inputs = {tuple(2 for _ in valuations)} | {
                tuple(target[index] for target in valuations) for index in range(width)
            }
            require(not (gain_set | mixed_set) & raw_inputs, "control equals a free raw input")
            rows.append(
                {
                    "width": width,
                    "root_sign": "N" if root_negative else "P",
                    "q": q,
                    "gain_functions": len(gain_set),
                    "mixed_functions": len(mixed_set),
                    "overlap": overlap,
                    "distinct_controls": distinct,
                    "scalar_gate_lower_bound": distinct,
                }
            )
    return rows


def exact_width_one_minimum(root_negative: bool) -> int:
    universe = tuple(itertools.product((0, 1, 2), repeat=3))
    position = {function: index for index, function in enumerate(universe)}
    initial = ((2, 2, 2), (0, 1, 2))
    target_columns = [[] for _ in range(6)]
    for target in words(1):
        for index, physical in enumerate(words(1)):
            pair = expected_pair(root_negative, target, physical)
            target_columns[2 * index].append(pair[0])
            target_columns[2 * index + 1].append(pair[1])
    initial_mask = sum(1 << position[value] for value in initial)
    target_mask = 0
    for column in target_columns:
        target_mask |= 1 << position[tuple(column)]
    queue = deque(((initial_mask, 0),))
    seen = {initial_mask}
    while queue:
        mask, distance = queue.popleft()
        if not target_mask & ~mask:
            return distance
        available = [index for index in range(27) if mask >> index & 1]
        candidates: set[int] = set()
        for source in available:
            candidates.add(position[tuple(u(value) for value in universe[source])])
        for x in available:
            for y in available:
                for z in available:
                    candidates.add(
                        position[
                            tuple(
                                d(a, b, c)
                                for a, b, c in zip(
                                    universe[x], universe[y], universe[z], strict=True
                                )
                            )
                        ]
                    )
        for result in candidates:
            if mask >> result & 1:
                continue
            next_mask = mask | 1 << result
            if next_mask not in seen:
                seen.add(next_mask)
                queue.append((next_mask, distance + 1))
    raise RuntimeError("width-one semantic BFS exhausted")


def arithmetic_checks(max_width: int) -> dict[str, object]:
    maxima = {
        "kuhn_direct_rails": (0, 0, 1),
        "uncanonicalized_native_reference": (0, 0, 1),
        "current_native_scan": (0, 0, 1),
    }
    for width in range(1, max_width + 1):
        q = 3**width
        require(3 * direct_rail_count(width) <= 7 * q, "direct rail 7q/3 bound failed")
        require(3 * bg_count(width, True) <= 7 * q, "current BG 7q/3 bound failed")
        require(9 * bgn_count(width, True) <= 26 * q, "current BGN 26q/9 bound failed")
        for root_negative in (False, True):
            direct = direct_vector_count(width, root_negative)
            native = native_vector_count(width, root_negative, False)
            refined = native_vector_count(width, root_negative, True)
            require(direct <= 3 * q, "all-width direct 3q bound failed")
            require(3 * native <= 8 * q, "all-width uncanonicalized native 8q/3 bound failed")
            require(3 * refined <= 7 * q, "all-width current native 7q/3 bound failed")
            require(
                3 * refined <= 4 * q + 15 * 3 ** ((width + 1) // 2),
                "current native 4q/3 envelope failed",
            )
            for label, value in (
                ("kuhn_direct_rails", direct),
                ("uncanonicalized_native_reference", native),
                ("current_native_scan", refined),
            ):
                old_width, old_num, old_den = maxima[label]
                if value * old_den > old_num * q:
                    maxima[label] = (width, value, q)
    return {
        "checked_widths": max_width,
        "maximum_ratios": {
            label: {
                "width": value[0],
                "numerator": value[1],
                "denominator": value[2],
                "decimal": f"{value[1] / value[2]:.12f}",
            }
            for label, value in maxima.items()
        },
        "exact_recurrences": {
            "kuhn": "R1=4; Rw=Ra+Rb+q+3^a(3^b-1)/2; S=2+R+(q+/-1)/2",
            "uncanonicalized_native_reference": "B1=C1=4; B=Ba+Bb+5q/3; C=Ba+Cb+7q/3; V=2+Ba+Cb+3q/2+/-1/2",
            "current_native_scan": "B=Ba+Bb+q+(q-3^a)/2; C=Ba+Cb+5q/3+(q-3^a)/2; V=2+Ba+Cb+4q/3-3^a/2+/-1/2",
        },
        "component_bounds": {
            "current_BG": "B(w)<=7*3^w/3",
            "current_BGN": "C(w)<=26*3^w/9",
            "current_vector_uniform": "V(w)<=7*3^w/3",
            "current_vector_envelope": "3V(w)<=4*3^w+15*3^ceil(w/2)",
        },
        "asymptotics": {
            "kuhn_direct_rails": "(2+o(1))q",
            "uncanonicalized_native_reference": "(3/2+o(1))q",
            "current_native_scan": "(4/3+o(1))q",
        },
    }


def mutation_checks() -> dict[str, object]:
    # Serial state composition cannot always drop the right gain rail.
    left = (0, 0)   # equal: (bad,gain)
    right = (0, 1)  # gain
    correct_gain = d(left[1], left[0], right[1])
    mutated_gain = left[1]
    require((correct_gain, mutated_gain) == (1, 0), "always-reuse mutation inert")

    flat_sign = None
    for root_negative in (False, True):
        for target in words(1):
            for physical in words(1):
                bad, gain, _not_bad = direct_triple(target, physical)
                actual = (bad, gain)
                expected = expected_pair(root_negative, target, physical)
                if actual != expected:
                    flat_sign = {
                        "root_sign": "N" if root_negative else "P",
                        "target": list(target),
                        "physical": list(physical),
                        "expected": list(expected),
                        "positive_pair_used": list(actual),
                    }
                    break
            if flat_sign is not None:
                break
        if flat_sign is not None:
            break
    require(flat_sign is not None, "flat-sign mutation survived")

    dag, pairs = build_native_vector(1, False, True)
    roots = roots_of(pairs)
    anchor_bad = None
    for anchor in (0, 1):
        values = dag.evaluate(roots, {"A": anchor, "t0": 0})
        expected = tuple(
            value
            for physical in words(1)
            for value in expected_pair(False, (0,), physical)
        )
        if values != expected:
            anchor_bad = {"anchor": anchor, "target": [0], "expected": list(expected), "actual": list(values)}
            break
    require(anchor_bad is not None, "binary-anchor mutation survived")

    false_overlap = {
        "target": [0],
        "not_bad_physical_0": direct_triple((0,), (0,))[2],
        "gain_physical_2": direct_triple((0,), (2,))[1],
    }
    require(
        false_overlap["not_bad_physical_0"] != false_overlap["gain_physical_2"],
        "false overlap mutation inert",
    )
    return {
        "always_reuse_right_gain": {
            "left_state": list(left),
            "right_state": list(right),
            "correct_gain": correct_gain,
            "mutated_gain": mutated_gain,
        },
        "ignore_cell_sign": flat_sign,
        "drop_A_equals_2_scope": anchor_bad,
        "share_not_bad_a0_with_gain_a2": false_overlap,
        "count_distinct_outputs_as_a_complete_circuit": {
            "width": 1,
            "P_distinct_outputs": 4,
            "P_exact_minimum_gates": exact_width_one_minimum(False),
            "N_distinct_outputs": 5,
            "N_exact_minimum_gates": exact_width_one_minimum(True),
        },
    }


def freeze_inputs() -> dict[str, str]:
    here = Path(__file__).resolve()
    tournament = here.parents[3]
    paths = {
        "STATE.md": tournament / "STATE.md",
        "check_lower_bound.py": tournament / "lanes/lower_bound/check_lower_bound.py",
        "check_native_scan.py": tournament / "lanes/native_scan/check_native_scan.py",
        "check_optimal_scan.py": tournament / "lanes/native_scan/check_optimal_scan.py",
    }
    expected = {
        "STATE.md": STATE_SHA256,
        "check_lower_bound.py": KUHN_SHA256,
        "check_native_scan.py": NATIVE_SHA256,
        "check_optimal_scan.py": OPTIMAL_SHA256,
    }
    result = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    require(result == expected, "frozen candidate hash drift")
    return result


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def run(structural_width: int, semantic_width: int, arithmetic_width: int) -> dict[str, object]:
    require(1 <= semantic_width <= structural_width <= 10, "invalid replay widths")
    require(arithmetic_width >= structural_width, "arithmetic width too small")
    frozen = freeze_inputs()
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS_KUHN__PASS_NATIVE_CURRENT_4_OVER_3",
        "frozen": frozen,
        "structural": structural_checks(structural_width, semantic_width),
        "constants": {
            "checks": constant_checks(semantic_width),
            "operation_nodes_upper_bound": 2,
            "scope": "A=2",
        },
        "output_lower_bound": {
            "rows": semantic_output_census(min(semantic_width, 5)),
            "all_width": {
                "P": "4q/3 distinct noninput Boolean controls",
                "N": "4q/3+1 distinct noninput Boolean controls",
                "scope": "address-only scalar {d,u} DAG with raw terminals A=2,t0,...; output counting only",
            },
        },
        "arithmetic": arithmetic_checks(arithmetic_width),
        "mutations": mutation_checks(),
        "verdicts": {
            "kuhn_direct_rails": "VALID: <=3q and (2+o(1))q, depth <=4+ceil(log2 w)",
            "scalar_output_lower_bound": "VALID IN DECLARED ADDRESS-ONLY SCALAR GRAMMAR; global D+1 is not established",
            "uncanonicalized_native_actual_counts": "GENUINE: exact recurrence gives (3/2+o(1))q, not a semantics/counting artifact",
            "current_native_scan": "VALID STRONGER CONSTRUCTION: zero-gain and N_(a1)=G_(a2) reuse give (4/3+o(1))q with unchanged depth",
        },
        "nonclaims": [
            "No global circuit minimum beyond the scalar distinct-output lower bound.",
            "No lower-order optimality, bounded-fanout, or formula-size theorem.",
            "No binary-anchor absolute-name theorem.",
            "No integrated compiler, novelty, prior-art, patent, FTO, license, or performance conclusion.",
        ],
    }
    result["semantic_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structural-width", type=int, default=9)
    parser.add_argument("--semantic-width", type=int, default=6)
    parser.add_argument("--arithmetic-width", type=int, default=4096)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.structural_width, args.semantic_width, args.arithmetic_width)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(result["semantic_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

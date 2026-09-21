#!/usr/bin/env python3
"""Exact checker for the native bad/gain signed program-vector construction.

The checker is deliberately self-contained: it imports neither the frozen
program-vector implementation nor any author/audit helper.  It checks direct
first-mismatch semantics, constant modes, original-signature DAG accounting,
depth, analytic recurrences, and effective mutations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from functools import cache
from itertools import product
from pathlib import Path
from typing import Iterable, Literal


Bit = Literal[0, 1]
Mode = Literal["projection", "constant"]
ROOT = Path(__file__).resolve().parents[5]
STATE = ROOT / "research/tournaments/2026-08-13-program-vector-optimization/STATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


def unary(x: int) -> int:
    require(x in (0, 1, 2), "u input outside Q")
    return (1, 0, 1)[x]


@cache
def words(width: int) -> tuple[tuple[int, ...], ...]:
    require(width >= 0, "negative width")
    return tuple(product((0, 1, 2), repeat=width))


def ceil_log2(value: int) -> int:
    require(value >= 1, "ceil_log2 requires a positive integer")
    return (value - 1).bit_length()


def cell_sign(root_sign: int, physical: tuple[int, ...]) -> int:
    require(root_sign in (0, 1), "invalid root sign")
    return root_sign ^ (sum(digit == 1 for digit in physical) & 1)


def direct_state(
    target: tuple[int, ...], physical: tuple[int, ...]
) -> tuple[int, int, int]:
    """Return the one-hot (bad, gain, not-bad) first-mismatch state."""
    require(len(target) == len(physical), "word width mismatch")
    for target_digit, physical_digit in zip(target, physical, strict=True):
        if target_digit != physical_digit:
            gain = int(target_digit == 1 and physical_digit == 2)
            bad = 1 - gain
            return bad, gain, 1 - bad
    return 0, 0, 1


def expected_pair(
    root_sign: int,
    physical: tuple[int, ...],
    target: tuple[int, ...] | None,
    mode: Mode,
    constant: int = 0,
) -> tuple[int, int]:
    sign = cell_sign(root_sign, physical)
    if mode == "constant":
        require(constant in (0, 1), "invalid constant")
        return (1 - constant, constant) if sign == 0 else (constant, constant)
    require(target is not None, "projection target missing")
    bad, gain, not_bad = direct_state(target, physical)
    return (bad, gain) if sign == 0 else (gain, not_bad)


class TermDAG:
    """Hash-consed constant-free original-signature d/u DAG."""

    def __init__(self) -> None:
        self.records: list[tuple[object, ...]] = []
        self.depths: list[int] = []
        self.unique: dict[tuple[object, ...], int] = {}

    def _intern(self, record: tuple[object, ...], depth: int) -> int:
        previous = self.unique.get(record)
        if previous is not None:
            return previous
        node = len(self.records)
        self.records.append(record)
        self.depths.append(depth)
        self.unique[record] = node
        return node

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

    def reachable_operation_count(self, roots: Iterable[int]) -> int:
        return sum(
            self.records[node][0] != "terminal" for node in self.reachable(roots)
        )

    def reachable(self, roots: Iterable[int]) -> frozenset[int]:
        seen: set[int] = set()

        def visit(node: int) -> None:
            if node in seen:
                return
            seen.add(node)
            record = self.records[node]
            if record[0] == "u":
                visit(int(record[1]))
            elif record[0] == "d":
                visit(int(record[1]))
                visit(int(record[2]))
                visit(int(record[3]))

        for root in roots:
            visit(root)
        return frozenset(seen)

    def dependencies(self, roots: Iterable[int]) -> frozenset[str]:
        reachable = self.reachable(roots)
        return frozenset(
            str(self.records[node][1])
            for node in reachable
            if self.records[node][0] == "terminal"
        )

    def evaluate_many(
        self, roots: Iterable[int], environment: dict[str, int]
    ) -> tuple[int, ...]:
        memo: dict[int, int] = {}

        def visit(node: int) -> int:
            cached = memo.get(node)
            if cached is not None:
                return cached
            record = self.records[node]
            if record[0] == "terminal":
                name = str(record[1])
                require(name in environment, f"missing terminal {name}")
                value = environment[name]
            elif record[0] == "u":
                value = unary(visit(int(record[1])))
            else:
                require(record[0] == "d", "unknown node kind")
                value = disc(
                    visit(int(record[1])),
                    visit(int(record[2])),
                    visit(int(record[3])),
                )
            memo[node] = value
            return value

        return tuple(visit(root) for root in roots)


BG = tuple[int, int]
BGN = tuple[int, int, int]


def digit_bgn(
    dag: TermDAG, digit: int, zero: int, one: int, two: int, mutation: str = ""
) -> dict[tuple[int, ...], BGN]:
    # bad_0=[t!=0], bad_2=[t=0], gain_2=[t=1], bad_1=[t!=1].
    bad_zero = dag.d(digit, two, one)
    bad_two = dag.u(bad_zero)
    gain_two = dag.d(digit, two, zero)
    bad_one = dag.d(one, digit, one if mutation == "bad_one" else zero)
    return {
        (0,): (bad_zero, zero, bad_two),
        (1,): (bad_one, zero, gain_two),
        (2,): (bad_two, gain_two, bad_zero),
    }


def balanced_bg(
    dag: TermDAG,
    digits: tuple[int, ...],
    zero: int,
    one: int,
    two: int,
    mutation: str = "",
) -> dict[tuple[int, ...], BG]:
    require(digits, "empty BG segment")
    if len(digits) == 1:
        return {
            word: (bad, gain)
            for word, (bad, gain, _not_bad) in digit_bgn(
                dag, digits[0], zero, one, two, mutation
            ).items()
        }
    left_width = (len(digits) + 1) // 2
    left = balanced_bg(dag, digits[:left_width], zero, one, two, mutation)
    right = balanced_bg(dag, digits[left_width:], zero, one, two, mutation)
    result: dict[tuple[int, ...], BG] = {}
    for left_word, (bad_left, gain_left) in left.items():
        for right_word, (bad_right, gain_right) in right.items():
            if mutation == "bad_compose":
                bad = dag.d(gain_left, bad_left, bad_right)
            else:
                bad = dag.d(bad_left, gain_left, bad_right)
            if mutation == "gain_compose":
                gain = dag.d(gain_left, zero, gain_right)
            elif gain_right == zero:
                # A suffix whose gain rail is identically zero cannot create
                # a good first mismatch.  Reuse the prefix rail verbatim;
                # this canonicalizes the entire trailing-{0,1} class.
                gain = gain_left
            else:
                gain = dag.d(gain_left, bad_left, gain_right)
            result[left_word + right_word] = (bad, gain)
    return result


def balanced_bgn(
    dag: TermDAG,
    digits: tuple[int, ...],
    zero: int,
    one: int,
    two: int,
    mutation: str = "",
) -> dict[tuple[int, ...], BGN]:
    require(digits, "empty BGN segment")
    if len(digits) == 1:
        return digit_bgn(dag, digits[0], zero, one, two, mutation)
    left_width = (len(digits) + 1) // 2
    left = balanced_bg(dag, digits[:left_width], zero, one, two, mutation)
    right = balanced_bgn(dag, digits[left_width:], zero, one, two, mutation)
    partial: dict[
        tuple[int, ...], tuple[int, int, int, int, int]
    ] = {}
    for left_word, (bad_left, gain_left) in left.items():
        for right_word, (bad_right, gain_right, not_bad_right) in right.items():
            bad = dag.d(bad_left, gain_left, bad_right)
            if gain_right == zero:
                gain = gain_left
            else:
                gain = dag.d(gain_left, bad_left, gain_right)
            partial[left_word + right_word] = (
                bad,
                gain,
                gain_left,
                bad_left,
                not_bad_right,
            )
    result: dict[tuple[int, ...], BGN] = {}
    for physical, (bad, gain, gain_left, bad_left, not_bad_right) in partial.items():
        if physical[-1] == 1 and mutation != "not_bad_compose":
            # Exact all-segment sibling law N_(a1)=O_(a2).
            not_bad = partial[physical[:-1] + (2,)][1]
        else:
            not_bad = dag.d(
                gain_left,
                bad_left,
                bad if mutation == "not_bad_compose" else not_bad_right,
            )
        result[physical] = (bad, gain, not_bad)
    return result


def build_projection_vector(
    width: int, root_sign: int, mutation: str = ""
) -> tuple[TermDAG, dict[tuple[int, ...], tuple[int, int]], tuple[int, ...]]:
    require(width >= 1, "projection vector requires positive width")
    dag = TermDAG()
    anchor = dag.terminal("A")
    one = dag.u(anchor)
    zero = dag.u(one)
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))

    if width == 1:
        states = digit_bgn(dag, digits[0], zero, one, anchor, mutation)
        pairs: dict[tuple[int, ...], tuple[int, int]] = {}
        for physical, (bad, gain, not_bad) in states.items():
            sign = root_sign if mutation == "flat_sign" else cell_sign(root_sign, physical)
            pairs[physical] = (bad, gain) if sign == 0 else (gain, not_bad)
        return dag, pairs, digits

    left_width = (width + 1) // 2
    left = balanced_bg(dag, digits[:left_width], zero, one, anchor, mutation)
    right = balanced_bgn(dag, digits[left_width:], zero, one, anchor, mutation)
    pairs = {}
    gains: dict[tuple[int, ...], int] = {}
    for left_word, (bad_left, gain_left) in left.items():
        for right_word, (bad_right, gain_right, not_bad_right) in right.items():
            physical = left_word + right_word
            if gain_right == zero and mutation != "gain_compose":
                gain = gain_left
            elif mutation == "gain_compose":
                gain = dag.d(gain_left, zero, gain_right)
            else:
                gain = dag.d(gain_left, bad_left, gain_right)
            gains[physical] = gain

    for left_word, (bad_left, gain_left) in left.items():
        for right_word, (bad_right, _gain_right, not_bad_right) in right.items():
            physical = left_word + right_word
            gain = gains[physical]
            sign = root_sign if mutation == "flat_sign" else cell_sign(root_sign, physical)
            if sign == 0:
                selected = dag.d(bad_left, gain_left, bad_right)
                pairs[physical] = (selected, gain)
            elif physical[-1] == 1 and mutation != "not_bad_final":
                # Exact global identity N_(a1)=G_(a2).  Naming the already
                # materialized sibling rail removes every genuine overlap in
                # the requested scalar-output family.
                selected = gains[physical[:-1] + (2,)]
                pairs[physical] = (gain, selected)
            else:
                selected = dag.d(
                    gain_left,
                    bad_left,
                    bad_right if mutation == "not_bad_final" else not_bad_right,
                )
                pairs[physical] = (gain, selected)
    return dag, pairs, digits


def build_constant_vector(
    width: int, root_sign: int, constant: int
) -> tuple[TermDAG, dict[tuple[int, ...], tuple[int, int]]]:
    require(width >= 0, "negative constant width")
    require(constant in (0, 1), "invalid constant")
    dag = TermDAG()
    anchor = dag.terminal("A")
    one = dag.u(anchor)
    zero = dag.u(one)
    pairs: dict[tuple[int, ...], tuple[int, int]] = {}
    for physical in words(width):
        sign = cell_sign(root_sign, physical)
        if sign == 0:
            pairs[physical] = (one, zero) if constant == 0 else (zero, one)
        else:
            pairs[physical] = (zero, zero) if constant == 0 else (one, one)
    return dag, pairs


def flatten_roots(
    pairs: dict[tuple[int, ...], tuple[int, int]], width: int
) -> tuple[int, ...]:
    return tuple(root for physical in words(width) for root in pairs[physical])


def evaluate_pairs(
    dag: TermDAG,
    pairs: dict[tuple[int, ...], tuple[int, int]],
    target: tuple[int, ...],
    anchor: int = 2,
) -> tuple[tuple[int, int], ...]:
    roots = flatten_roots(pairs, len(target))
    environment = {"A": anchor, **{f"t{i}": digit for i, digit in enumerate(target)}}
    values = dag.evaluate_many(roots, environment)
    return tuple((values[2 * i], values[2 * i + 1]) for i in range(len(words(len(target)))))


@cache
def bg_merge_bound(width: int) -> int:
    """BG nodes, including four digit-specific base nodes per leaf."""
    require(width >= 1, "BG merge bound width")
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    return bg_merge_bound(left) + bg_merge_bound(right) + 2 * 3**width


@cache
def bgn_merge_bound(width: int) -> int:
    """BGN nodes, including four digit-specific base nodes per leaf."""
    require(width >= 1, "BGN merge bound width")
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    return bg_merge_bound(left) + bgn_merge_bound(right) + 3 * 3**width


@cache
def vector_bound(width: int) -> int:
    require(width >= 1, "vector bound width")
    if width == 1:
        return 6
    left = (width + 1) // 2
    right = width // 2
    # Two anchor names are globally shared.  Each address digit has its own
    # four-node base and is charged inside the two disjoint segment bounds.
    return 2 + bg_merge_bound(left) + bgn_merge_bound(right) + 2 * 3**width


def first_counterexample(mutation: str, max_width: int = 4) -> dict[str, object] | None:
    for width in range(1, max_width + 1):
        for root_sign in (0, 1):
            dag, pairs, _digits = build_projection_vector(width, root_sign, mutation)
            for target in words(width):
                actual = evaluate_pairs(dag, pairs, target)
                for index, physical in enumerate(words(width)):
                    expected = expected_pair(root_sign, physical, target, "projection")
                    if actual[index] != expected:
                        return {
                            "width": width,
                            "root_sign": root_sign,
                            "target": list(target),
                            "physical": list(physical),
                            "expected": list(expected),
                            "actual": list(actual[index]),
                        }
    return None


def semantic_checks(max_width: int) -> tuple[list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    comparisons = 0
    for width in range(1, max_width + 1):
        q = 3**width
        for root_sign in (0, 1):
            dag, pairs, _digits = build_projection_vector(width, root_sign)
            roots = flatten_roots(pairs, width)
            require(
                dag.dependencies(roots) == frozenset({"A", *(f"t{i}" for i in range(width))}),
                f"projection dependency mismatch at width {width}",
            )
            reachable_operations = dag.reachable_operation_count(roots)
            require(reachable_operations <= dag.operation_count, "reachable count exceeds allocation")
            require(reachable_operations <= vector_bound(width), "analytic node bound violated")
            require(4 * vector_bound(width) <= 13 * q, "13q/4 universal bound violated")
            max_depth = max(dag.depths[root] for root in roots)
            require(max_depth <= 3 + ceil_log2(width), "depth bound violated")
            for target in words(width):
                actual = evaluate_pairs(dag, pairs, target)
                for index, physical in enumerate(words(width)):
                    expected = expected_pair(root_sign, physical, target, "projection")
                    require(actual[index] == expected, "projection semantic mismatch")
                    require(actual[index][0] in (0, 1) and actual[index][1] in (0, 1), "nonbit output")
                    comparisons += 1
            rows.append(
                {
                    "width": width,
                    "q": q,
                    "root_sign": root_sign,
                    "operation_nodes": reachable_operations,
                    "allocated_operation_nodes": dag.operation_count,
                    "recurrence_bound": vector_bound(width),
                    "uniform_13q_over_4_numerator_slack": 13 * q - 4 * vector_bound(width),
                    "depth": max_depth,
                    "depth_bound": 3 + ceil_log2(width),
                }
            )
    return rows, comparisons


def constant_checks(max_width: int) -> int:
    comparisons = 0
    for width in range(0, max_width + 1):
        for root_sign in (0, 1):
            for constant in (0, 1):
                dag, pairs = build_constant_vector(width, root_sign, constant)
                roots = flatten_roots(pairs, width)
                require(dag.operation_count == 2, "constant vector must use exactly two names")
                values = dag.evaluate_many(roots, {"A": 2})
                for index, physical in enumerate(words(width)):
                    actual = (values[2 * index], values[2 * index + 1])
                    expected = expected_pair(root_sign, physical, None, "constant", constant)
                    require(actual == expected, "constant semantic mismatch")
                    comparisons += 1
    return comparisons


def arithmetic_checks(max_width: int = 4096) -> dict[str, object]:
    min_bg_slack: int | None = None
    min_bgn_slack: int | None = None
    min_vector_slack: int | None = None
    max_ratio_width = 0
    max_ratio_numerator = 0
    max_ratio_denominator = 1
    for width in range(1, max_width + 1):
        q = 3**width
        bg_slack = 13 * q - 4 * bg_merge_bound(width)
        bgn_slack = 17 * q - 4 * bgn_merge_bound(width)
        vector_slack = 13 * q - 4 * vector_bound(width)
        require(bg_slack >= 0, "BG universal arithmetic bound failed")
        require(bgn_slack >= 0, "BGN universal arithmetic bound failed")
        require(vector_slack >= 0, "vector universal arithmetic bound failed")
        min_bg_slack = bg_slack if min_bg_slack is None else min(min_bg_slack, bg_slack)
        min_bgn_slack = bgn_slack if min_bgn_slack is None else min(min_bgn_slack, bgn_slack)
        min_vector_slack = (
            vector_slack if min_vector_slack is None else min(min_vector_slack, vector_slack)
        )
        candidate_numerator = vector_bound(width)
        candidate_denominator = q
        if candidate_numerator * max_ratio_denominator > max_ratio_numerator * candidate_denominator:
            max_ratio_width = width
            max_ratio_numerator = candidate_numerator
            max_ratio_denominator = candidate_denominator
    return {
        "checked_widths": max_width,
        "min_bg_13q_over_4_scaled_slack": min_bg_slack,
        "min_bgn_17q_over_4_scaled_slack": min_bgn_slack,
        "min_vector_13q_over_4_scaled_slack": min_vector_slack,
        "max_vector_bound_ratio": {
            "width": max_ratio_width,
            "numerator": max_ratio_numerator,
            "denominator": max_ratio_denominator,
            "decimal": f"{max_ratio_numerator / max_ratio_denominator:.12f}",
        },
        "asymptotic_statement": "vector_bound(w)=2*3^w+O(3^ceil(w/2))",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=6)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    require(1 <= args.max_width <= 7, "max-width outside exact replay budget")

    semantic_rows, projection_comparisons = semantic_checks(args.max_width)
    constant_comparisons = constant_checks(args.max_width)
    mutations = {}
    for mutation in (
        "bad_one",
        "bad_compose",
        "gain_compose",
        "not_bad_compose",
        "not_bad_final",
        "flat_sign",
    ):
        counterexample = first_counterexample(mutation)
        require(counterexample is not None, f"ineffective mutation: {mutation}")
        mutations[mutation] = counterexample

    # The A=2 premise is load-bearing.
    dag, pairs, _digits = build_projection_vector(1, 0)
    anchor_mutation_actual = evaluate_pairs(dag, pairs, (0,), anchor=1)
    anchor_mutation_expected = tuple(
        expected_pair(0, physical, (0,), "projection") for physical in words(1)
    )
    require(anchor_mutation_actual != anchor_mutation_expected, "A=1 mutation survived")

    payload: dict[str, object] = {
        "schema": "orbit-synthesis/native-bad-gain-program-vector/v1",
        "status": "PASS",
        "claim": {
            "q": "3^w",
            "uniform_size": "operation_nodes <= 13q/4 < 4q, including two anchor names",
            "asymptotic_size": "operation_nodes = 2q+O(3^ceil(w/2))",
            "depth": "operation_depth <= 3+ceil(log2 w)",
            "scope": "A=2 nonbinary branch; all projection and Boolean constant modes; both root signs",
        },
        "state_sha256": sha256_path(STATE),
        "source_sha256": sha256_path(Path(__file__)),
        "exact": {
            "max_width": args.max_width,
            "projection_comparisons": projection_comparisons,
            "constant_comparisons": constant_comparisons,
            "rows": semantic_rows,
        },
        "arithmetic": arithmetic_checks(),
        "mutations": mutations,
        "anchor_mutation": {
            "anchor": 1,
            "target": [0],
            "expected": [list(pair) for pair in anchor_mutation_expected],
            "actual": [list(pair) for pair in anchor_mutation_actual],
        },
        "nonclaims": [
            "No global optimality or lower bound below the construction.",
            "No novelty or freedom-to-operate conclusion.",
            "No binary-cube absolute-control theorem.",
            "No integrated all-arity compiler promotion.",
            "No ordinary formula-size or bounded-fanout claim.",
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["semantic_sha256"] = sha256_bytes(canonical)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()

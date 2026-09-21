#!/usr/bin/env python3
"""Check the recursive strong Boolean discriminator-router family.

The construction is discovery evidence for a manuscript proof.  It builds
positive and negative signed routers directly in the original discriminator
syntax, proves bounded members by canonical ROBDDs, freezes the depth-four
R27 witness, checks effective mutations, and audits variable-depth compiler
arithmetic.  The square-root schedule yields `r+O(sqrt(r))` depth at
`O(3^r/r)` size; a logarithmic schedule is retained as a calibration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from functools import cache
from itertools import product
from pathlib import Path
from typing import Literal


Kind = Literal["P", "N"]
Mode = tuple[Literal["const", "proj"], int]
CONTROL = -1
SOURCE_PATH = Path(__file__).resolve()
STATE_PATH = SOURCE_PATH.parents[2] / "STATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def disc(left: int, middle: int, right: int) -> int:
    return right if left == middle else left


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def router_capacity(depth: int) -> int:
    require(depth >= 1, "router depth must be positive")
    return 3 ** (depth - 1)


def child_kinds(kind: Kind) -> tuple[Kind, Kind, Kind]:
    return ("P", "N", "P") if kind == "P" else ("N", "P", "N")


@cache
def layout(kind: Kind, depth: int) -> tuple[int, ...]:
    """Full leaf labels: nonnegative branch index, or CONTROL."""

    require(depth >= 1, "layout depth must be positive")
    if depth == 1:
        return (0, CONTROL, CONTROL) if kind == "P" else (CONTROL, 0, CONTROL)
    child_capacity = router_capacity(depth - 1)
    result: list[int] = []
    for child_index, child_kind in enumerate(child_kinds(kind)):
        offset = child_index * child_capacity
        result.extend(
            CONTROL if label == CONTROL else offset + label
            for label in layout(child_kind, depth - 1)
        )
    return tuple(result)


@cache
def full_program(kind: Kind, depth: int, mode: Mode) -> tuple[int | None, ...]:
    """Values on controls and None on branch leaves for one requested mode."""

    tag, value = mode
    capacity = router_capacity(depth)
    require(tag == "const" and value in (0, 1) or tag == "proj" and 0 <= value < capacity, "bad mode")
    if depth == 1:
        if kind == "P":
            return {
                ("proj", 0): (None, 0, 0),
                ("const", 0): (None, 1, 0),
                ("const", 1): (None, 0, 1),
            }[mode]
        return {
            ("proj", 0): (0, None, 1),
            ("const", 0): (0, None, 0),
            ("const", 1): (1, None, 1),
        }[mode]

    children = child_kinds(kind)
    if tag == "const":
        child_modes: tuple[Mode, Mode, Mode] = (mode, mode, mode)
    else:
        child_capacity = router_capacity(depth - 1)
        group, local_target = divmod(value, child_capacity)
        if group == 0:
            child_modes = (("proj", local_target), ("const", 0), ("const", 0))
        elif group == 1:
            child_modes = (("const", 0), ("proj", local_target), ("const", 1))
        else:
            child_modes = (("const", 0), ("const", 0), ("proj", local_target))
    return tuple(
        leaf
        for child_kind, child_mode in zip(children, child_modes, strict=True)
        for leaf in full_program(child_kind, depth - 1, child_mode)
    )


def compact_program(kind: Kind, depth: int, mode: Mode) -> tuple[int, ...]:
    leaves = full_program(kind, depth, mode)
    result = tuple(int(leaves[index]) for index, label in enumerate(layout(kind, depth)) if label == CONTROL)
    require(len(result) == 2 * router_capacity(depth), "control-count drift")
    return result


def evaluate(kind: Kind, depth: int, program: tuple[int, ...], values: tuple[int, ...]) -> int:
    labels = layout(kind, depth)
    require(len(values) == router_capacity(depth), "branch valuation width drift")
    iterator = iter(program)
    layer = [next(iterator) if label == CONTROL else values[label] for label in labels]
    for _ in range(depth):
        layer = [disc(*layer[index : index + 3]) for index in range(0, len(layer), 3)]
    require(len(layer) == 1, "router did not reduce to a root")
    return layer[0]


def middle_parity(position: int, depth: int) -> int:
    parity = 0
    for power in reversed(range(depth)):
        digit, position = divmod(position, 3**power)
        parity ^= digit == 1
    return int(parity)


class BDD:
    """Small canonical reduced ordered BDD implementation."""

    def __init__(self) -> None:
        self.nodes: list[tuple[int, int, int] | None] = [None, None]
        self.unique: dict[tuple[int, int, int], int] = {}
        self.apply_cache: dict[tuple[str, int, int], int] = {}
        self.not_cache: dict[int, int] = {0: 1, 1: 0}

    def mk(self, variable: int, low: int, high: int) -> int:
        if low == high:
            return low
        key = (variable, low, high)
        if key not in self.unique:
            self.unique[key] = len(self.nodes)
            self.nodes.append(key)
        return self.unique[key]

    def variable(self, index: int) -> int:
        return self.mk(index, 0, 1)

    def negate(self, node: int) -> int:
        if node in self.not_cache:
            return self.not_cache[node]
        record = self.nodes[node]
        require(record is not None, "missing BDD node")
        variable, low, high = record
        result = self.mk(variable, self.negate(low), self.negate(high))
        self.not_cache[node] = result
        self.not_cache[result] = node
        return result

    def apply(self, operation: Literal["and", "or"], left: int, right: int) -> int:
        if operation == "and":
            if left == 0 or right == 0:
                return 0
            if left == 1:
                return right
            if right == 1 or left == right:
                return left
        else:
            if left == 1 or right == 1:
                return 1
            if left == 0:
                return right
            if right == 0 or left == right:
                return left
        if left > right:
            left, right = right, left
        key = (operation, left, right)
        if key in self.apply_cache:
            return self.apply_cache[key]
        left_record = self.nodes[left]
        right_record = self.nodes[right]
        require(left_record is not None and right_record is not None, "terminal reduction failed")
        variable = min(left_record[0], right_record[0])
        left_low, left_high = left_record[1:] if left_record[0] == variable else (left, left)
        right_low, right_high = right_record[1:] if right_record[0] == variable else (right, right)
        result = self.mk(
            variable,
            self.apply(operation, left_low, right_low),
            self.apply(operation, left_high, right_high),
        )
        self.apply_cache[key] = result
        return result

    def discriminator(self, left: int, middle: int, right: int) -> int:
        # d(x,y,z)=majority(x,not y,z).
        not_middle = self.negate(middle)
        return self.apply(
            "or",
            self.apply("or", self.apply("and", left, not_middle), self.apply("and", left, right)),
            self.apply("and", not_middle, right),
        )


def bdd_root(
    bdd: BDD,
    kind: Kind,
    depth: int,
    program: tuple[int, ...],
    variables: tuple[int, ...],
) -> int:
    iterator = iter(program)
    layer = [next(iterator) if label == CONTROL else variables[label] for label in layout(kind, depth)]
    for _ in range(depth):
        layer = [bdd.discriminator(*layer[index : index + 3]) for index in range(0, len(layer), 3)]
    return layer[0]


def finite_family_checks(max_bdd_depth: int = 6, mutation_depth: int = 4) -> dict[str, object]:
    rows = []
    mutation_rows = []
    direct_checks = 0
    require(1 <= mutation_depth <= max_bdd_depth, "bad mutation depth")
    for depth in range(1, max_bdd_depth + 1):
        capacity = router_capacity(depth)
        expected_leaves = 3**depth
        for kind in ("P", "N"):
            labels = layout(kind, depth)
            require(len(labels) == expected_leaves, "leaf-count drift")
            require(
                sorted(label for label in labels if label != CONTROL) == list(range(capacity)),
                "branch labels drift",
            )
            expected_parity = 0 if kind == "P" else 1
            require(
                all(
                    middle_parity(position, depth) == expected_parity
                    for position, label in enumerate(labels)
                    if label != CONTROL
                ),
                "signed branch polarity drift",
            )

            bdd = BDD()
            variables = tuple(bdd.variable(index) for index in range(capacity))
            for constant in (0, 1):
                root = bdd_root(
                    bdd,
                    kind,
                    depth,
                    compact_program(kind, depth, ("const", constant)),
                    variables,
                )
                require(root == constant, f"BDD constant mode failed at {kind}{depth}:{constant}")

            for target in range(capacity):
                program = compact_program(kind, depth, ("proj", target))
                root = bdd_root(bdd, kind, depth, program, variables)
                expected = variables[target] if kind == "P" else bdd.negate(variables[target])
                require(root == expected, f"BDD projection failed at {kind}{depth}:{target}")
                if kind == "P" and depth == mutation_depth:
                    corpus = (
                        ((0,) * capacity, (1,) * capacity)
                        + tuple(
                            tuple(int(index == one) for index in range(capacity))
                            for one in range(capacity)
                        )
                        + tuple(
                            tuple(int(index != zero) for index in range(capacity))
                            for zero in range(capacity)
                        )
                    )
                    effective = None
                    for slot in range(len(program)):
                        mutated = program[:slot] + (1 - program[slot],) + program[slot + 1 :]
                        if bdd_root(bdd, kind, depth, mutated, variables) == expected:
                            continue
                        witnesses = tuple(
                            values
                            for values in corpus
                            if evaluate(kind, depth, mutated, values) != values[target]
                        )
                        if witnesses:
                            effective = (slot, witnesses[0])
                            break
                    require(effective is not None, f"no effective mutation for P{depth}:{target}")
                    slot, counterexample = effective
                    mutation_rows.append(
                        {
                            "target": target,
                            "slot": slot,
                            "counterexample_ones": [
                                index for index, value in enumerate(counterexample) if value
                            ],
                            "verdict": "not_equivalent",
                        }
                    )

            if depth <= 3:
                for values in product((0, 1), repeat=capacity):
                    for constant in (0, 1):
                        require(
                            evaluate(
                                kind,
                                depth,
                                compact_program(kind, depth, ("const", constant)),
                                values,
                            )
                            == constant,
                            f"direct constant mode failed at {kind}{depth}:{values}",
                        )
                        direct_checks += 1
                    for target in range(capacity):
                        expected_value = values[target] if kind == "P" else 1 - values[target]
                        require(
                            evaluate(
                                kind,
                                depth,
                                compact_program(kind, depth, ("proj", target)),
                                values,
                            )
                            == expected_value,
                            f"direct projection failed at {kind}{depth}:{target}:{values}",
                        )
                        direct_checks += 1

            rows.append(
                {
                    "kind": kind,
                    "depth": depth,
                    "capacity": capacity,
                    "branch_leaves": capacity,
                    "control_leaves": 2 * capacity,
                    "discriminator_nodes": (3**depth - 1) // 2,
                    "bdd_nodes_after_all_modes": len(bdd.nodes),
                }
            )

    # Exhaust the two representation bridges on the recursive R9 member.
    bridge_depth = 3
    bridge_capacity = router_capacity(bridge_depth)
    codes = ((0, 0), (0, 1), (1, 0))
    complement_checks = 0
    q_plane_checks = 0
    for target in range(bridge_capacity):
        program = compact_program("P", bridge_depth, ("proj", target))
        for relative_values in product((0, 1), repeat=bridge_capacity):
            for orientation in (0, 1):
                physical_values = tuple(value ^ orientation for value in relative_values)
                physical_program = tuple(bit ^ orientation for bit in program)
                require(
                    evaluate("P", bridge_depth, physical_program, physical_values)
                    == physical_values[target],
                    f"relative-complement bridge failed at {target}:{orientation}",
                )
                complement_checks += 1
        for values in product((0, 1, 2), repeat=bridge_capacity):
            high = tuple(codes[value][0] for value in values)
            low = tuple(codes[value][1] for value in values)
            routed_high = evaluate("P", bridge_depth, program, high)
            routed_low = evaluate("P", bridge_depth, program, low)
            decoded = disc(disc(routed_high, 1, 2), 0, routed_low)
            require(decoded == values[target], f"two-plane Q bridge failed at {target}:{values}")
            q_plane_checks += 1

    return {
        "rows": rows,
        "direct_boolean_checks_through_depth_three": direct_checks,
        "r27_effective_mutations": mutation_rows,
        "r9_complement_relative_checks": complement_checks,
        "r9_q_plane_checks": q_plane_checks,
    }


def floor_log(base: int, value: int) -> int:
    require(base >= 2 and value >= 1, "bad floor-log arguments")
    exponent = 0
    power = 1
    while power * base <= value:
        power *= base
        exponent += 1
    return exponent


def ceil_log(base: int, value: int) -> int:
    exponent = floor_log(base, value)
    return exponent if base**exponent == value else exponent + 1


def ceil_div(left: int, right: int) -> int:
    return (left + right - 1) // right


def chunk_widths(total: int, width: int) -> tuple[int, ...]:
    """Partition with the short residual first, a size-critical order."""

    require(total >= 0 and width >= 1, "bad chunk arguments")
    if total == 0:
        return ()
    remainder = total % width
    result = ((remainder,) if remainder else ()) + (width,) * (total // width)
    require(sum(result) == total, "chunk-width sum drift")
    require(all(chunk == width for chunk in result[1:] if remainder), "full chunk drift")
    require(not remainder or result[0] == remainder, "residual chunk is not first")
    return result


def prefix_instances(widths: tuple[int, ...], alphabet: int) -> tuple[int, int]:
    product_so_far = 1
    instances = 0
    for width in widths:
        instances += product_so_far
        product_so_far *= alphabet**width
    return instances, product_so_far


def compiler_parameters(
    arity: int,
    policy: Literal["logarithmic", "square_root"] = "logarithmic",
) -> dict[str, int | float | str]:
    require(arity >= 27, "variable family audit starts at arity 27")
    if policy == "logarithmic":
        k = floor_log(3, arity)
    else:
        require(policy == "square_root", "unknown compiler policy")
        k = math.isqrt(arity)
    depth = k + 1
    capacity = 3**k
    router_nodes = (3**depth - 1) // 2
    ratio = 3**arity // (arity * capacity)
    local_cap = floor_log(3, ratio)
    require(local_cap >= 1, "empty local-code cap")
    block_coordinates = floor_log(3, local_cap)
    block_assignments = 3**block_coordinates
    prefix_coordinates = arity - block_coordinates

    local_widths = chunk_widths(block_coordinates, k)
    prefix_widths = chunk_widths(prefix_coordinates, k)
    local_levels = len(local_widths)
    prefix_levels = len(prefix_widths)
    route_levels = local_levels + prefix_levels
    prefix_router_instances, prefix_assignments = prefix_instances(prefix_widths, 3)
    require(prefix_assignments == 3**prefix_coordinates, "prefix product drift")

    require(local_levels == 1, "local block unexpectedly needs more than one router")
    require(block_assignments <= capacity, "local assignment set exceeds router capacity")

    # The one-level encoded library uses two R_h copies for each of its 3^M
    # Boolean-plane code pairs.
    library_upper = 2 * router_nodes * 3**block_assignments
    prefix_router_nodes = 2 * router_nodes * prefix_router_instances

    # Each ternary control table is compiled by a seven-d-node selector tree.
    def ternary_control_nodes(width: int) -> int:
        return 7 * (3**width - 1) // 2

    local_control_nodes = sum(
        2 * capacity * ternary_control_nodes(width) for width in local_widths
    )
    prefix_control_nodes = sum(
        2 * capacity * ternary_control_nodes(width) for width in prefix_widths
    )

    binary_width = max(1, floor_log(2, capacity))
    binary_widths = chunk_widths(arity - 1, binary_width)
    require(
        not ((arity - 1) % binary_width)
        or binary_widths[0] == (arity - 1) % binary_width,
        "binary residual chunk is not first",
    )
    binary_router_instances, binary_assignments = prefix_instances(binary_widths, 2)
    require(binary_assignments == 2 ** (arity - 1), "binary product drift")
    binary_router_nodes = router_nodes * binary_router_instances
    binary_control_nodes = sum(
        2 * capacity * 3 * (2**width - 1) for width in binary_widths
    )

    polynomial_and_glue = 4 * arity + 64
    size_upper = (
        library_upper
        + prefix_router_nodes
        + local_control_nodes
        + prefix_control_nodes
        + binary_router_nodes
        + binary_control_nodes
        + polynomial_and_glue
    )
    route_depth = depth * route_levels
    anchor_depth = 3 * ceil_log(2, arity)
    control_depth = anchor_depth + 2 + 3 * max((0, *local_widths, *prefix_widths))
    nonbinary_depth_upper = route_depth + control_depth + 8
    binary_depth_upper = depth * len(binary_widths) + 2 * binary_width + 8
    depth_upper = max(nonbinary_depth_upper, binary_depth_upper)

    if policy == "logarithmic":
        require(capacity <= arity < 3 * capacity, "capacity scale drift")
    else:
        require(k * k <= arity < (k + 1) * (k + 1), "square-root scale drift")
    require(capacity * 3**block_assignments * arity <= 3**arity, "library budget failed")
    require(prefix_router_instances * (capacity - 1) <= prefix_assignments + capacity, "prefix instance rate failed")
    require(route_levels <= ceil_div(arity, k) + 1, "route-level ceiling failed")

    return {
        "policy": policy,
        "arity": arity,
        "router_depth": depth,
        "chunk_width": k,
        "capacity": capacity,
        "router_nodes": router_nodes,
        "control_leaves": 2 * capacity,
        "local_cap": local_cap,
        "block_coordinates": block_coordinates,
        "block_assignments": block_assignments,
        "prefix_assignments": prefix_assignments,
        "route_levels": route_levels,
        "size_upper_log3": math.log(size_upper, 3),
        "target_size_log3": arity - math.log(arity, 3),
        "depth_upper": depth_upper,
        "depth_per_arity": depth_upper / arity,
        "routing_coefficient": depth / k,
    }


def compiler_checks() -> dict[str, object]:
    policies = {}
    selected_arities = (27, 32, 64, 128, 256, 512, 1024)
    all_rows = {}
    for policy in ("logarithmic", "square_root"):
        rows = [compiler_parameters(arity, policy) for arity in range(27, 1025)]
        all_rows[policy] = rows
        require(
            all(
                row["routing_coefficient"] == 1 + 1 / int(row["chunk_width"])
                for row in rows
            ),
            f"{policy} coefficient formula drift",
        )
        policies[policy] = {
            "arities_checked": len(rows),
            "selected_rows": [rows[arity - 27] for arity in selected_arities],
        }

    # Exact counterexample to putting a short residual last.  At r=512 under
    # the square-root policy, k=22, q=3^22, b=5, and the prefix has 507
    # coordinates = 1 + 23*22.  Residual-first makes the q-ary router-instance
    # census satisfy (q-1)I=P+q-4.  Residual-last instead gives
    # (q-1)I_wrong=q^24-1>P+q, introducing the forbidden factor q/3.
    mutation_arity = 512
    mutation_row = compiler_parameters(mutation_arity, "square_root")
    mutation_k = int(mutation_row["chunk_width"])
    mutation_q = int(mutation_row["capacity"])
    mutation_prefix_coordinates = mutation_arity - int(mutation_row["block_coordinates"])
    correct_widths = chunk_widths(mutation_prefix_coordinates, mutation_k)
    require(correct_widths == (1,) + (22,) * 23, "r=512 residual-first shape drift")
    wrong_widths = correct_widths[1:] + correct_widths[:1]
    correct_instances, mutation_p = prefix_instances(correct_widths, 3)
    wrong_instances, wrong_p = prefix_instances(wrong_widths, 3)
    require(mutation_p == wrong_p == 3**mutation_prefix_coordinates, "schedule product drift")
    correct_lhs = (mutation_q - 1) * correct_instances
    wrong_lhs = (mutation_q - 1) * wrong_instances
    threshold = mutation_p + mutation_q
    require(correct_lhs == threshold - 4, "residual-first exact identity drift")
    require(wrong_lhs == mutation_q**24 - 1, "residual-last exact identity drift")
    require(wrong_lhs > threshold, "residual-last size mutation unexpectedly survived")

    return {
        "policies": policies,
        "depth_policy_comparison": [
            {
                "arity": arity,
                "logarithmic_depth_upper": all_rows["logarithmic"][arity - 27][
                    "depth_upper"
                ],
                "square_root_depth_upper": all_rows["square_root"][arity - 27][
                    "depth_upper"
                ],
            }
            for arity in selected_arities
        ],
        "residual_first_lemma": (
            "For prefix widths (s,k,...,k), a=3^s and q=3^k: "
            "(q-1)I=P+q-a-1<=P+q. The same product-first argument is used "
            "for the binary branch."
        ),
        "residual_last_mutation_r512": {
            "k": mutation_k,
            "q": mutation_q,
            "prefix_coordinates": mutation_prefix_coordinates,
            "correct_widths": list(correct_widths),
            "wrong_widths": list(wrong_widths),
            "correct_identity": "(q-1)*I=P+q-4",
            "wrong_identity": "(q-1)*I_wrong=q^24-1>P+q",
            "wrong_excess": str(wrong_lhs - threshold),
            "verdict": "REJECTED",
        },
        "fixed_depth_rows": [
            {
                "depth": depth,
                "capacity": router_capacity(depth),
                "coefficient": depth / (depth - 1),
            }
            for depth in range(2, 9)
        ],
        "asymptotic_depth_logarithmic_policy": "r+O(r/log r)",
        "asymptotic_depth_square_root_policy": "r+O(sqrt(r))",
        "asymptotic_size": "O(3^r/r)",
        "fixed_depth_coefficient": "h/(h-1)",
        "control_bound": (
            "each of 2q slots has a full width-k ternary selector with at most "
            "7*(3^k-1)/2 nodes and 3k depth, shared once per level; q<=r for "
            "the logarithmic policy, while (r/k)q^2=o(3^r/r) for k=floor(sqrt(r))"
        ),
        "square_root_analytic_ledger": {
            "parameters": (
                "k=floor(sqrt(r)), h=k+1, q=3^k; H=floor(log_3(floor(3^r/(r*q)))); "
                "M=3^floor(log_3(H)), b=log_3(M), P=3^(r-b)"
            ),
            "local_library": "2*((3^h-1)/2)*3^M < 3*q*3^M <= 3*3^r/r",
            "prefix_routers": "instances <= 1+P/(q-1), hence paired router nodes O(P+q)=O(3^r/r)",
            "shared_controls": "O((r/k)*q^2)=O(sqrt(r)*3^(2*sqrt(r)))=o(3^r/r)",
            "depth": "(k+1)*(1+ceil((r-b)/k))+O(k+log r)=r+O(sqrt(r))",
            "binary": "relative-control depth log_3(2)*r+O(sqrt(r)); size O(2^r+(r/k)*q^2)",
        },
    }


def falsifier_checks() -> dict[str, object]:
    # Freeze the STATE erratum: d is not ordinary monotone majority.
    require(disc(0, 0, 1) == 1, "discriminator truth table drift")
    require(sum((0, 0, 1)) < 2, "ordinary-majority counterexample drift")
    require(
        disc(0, 1, 0) == 0 and disc(1, 0, 0) == 1 and disc(1, 1, 0) == 0,
        "naive two-extreme counterexample drift",
    )

    complement_checks = 0
    for left, middle, right in product((0, 1), repeat=3):
        require(
            disc(1 - left, 1 - middle, 1 - right)
            == 1 - disc(left, middle, right),
            "complement equivariance drift",
        )
        complement_checks += 1

    padding_checks = 0
    for depth in range(2, 7):
        capacity = router_capacity(depth)
        used = capacity - 1
        for target in range(used):
            for phase in (0, 1):
                live = tuple((index + phase) % 2 for index in range(used))
                padded = live + (live[-1],)
                require(
                    evaluate("P", depth, compact_program("P", depth, ("proj", target)), padded)
                    == live[target],
                    f"padding drift at depth {depth}:{target}",
                )
                padding_checks += 1
    return {
        "ordinary_majority_refuted_by": "d(0,0,1)=1 while majority(0,0,1)=0",
        "naive_extreme_lemma_counterexample": "F=d(x0,x1,0): F(0,1)=0, F(1,0)=1, F(1,1)=0",
        "complement_equivariance_checks": complement_checks,
        "repeated_last_branch_padding_checks": padding_checks,
    }


def r27_witness() -> dict[str, object]:
    depth = 4
    labels = layout("P", depth)
    programs = tuple(
        compact_program("P", depth, ("proj", target))
        for target in range(router_capacity(depth))
    )
    payload: dict[str, object] = {
        "schema": "orbit-synthesis/strong-discriminator-r27/v1",
        "depth": depth,
        "capacity": router_capacity(depth),
        "labels": [0 if label == CONTROL else label + 1 for label in labels],
        "control_positions": [index for index, label in enumerate(labels) if label == CONTROL],
        "branch_positions": [index for index, label in enumerate(labels) if label != CONTROL],
        "programs": [list(program) for program in programs],
        "discriminator_nodes": (3**depth - 1) // 2,
        "claim": "each frozen program makes the full depth-4 d tree the requested Boolean projection",
        "generator_source_sha256": sha256_path(SOURCE_PATH),
        "frozen_state_sha256": sha256_path(STATE_PATH),
    }
    payload["semantic_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    parser.add_argument("--witness-out")
    args = parser.parse_args()
    lane = "research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused"
    checker = f"{lane}/check_strong_router_family.py"
    summary: dict[str, object] = {
        "schema": "orbit-synthesis/strong-discriminator-router-family/v1",
        "provenance": {
            "source_sha256": sha256_path(SOURCE_PATH),
            "state_sha256": sha256_path(STATE_PATH),
            "normal_command": (
                f"python3 {checker} --out {lane}/summary.json "
                f"--witness-out {lane}/r27_witness.json"
            ),
            "optimized_command": (
                f"python3 -O {checker} --out /tmp/strong_router_summary_opt.json "
                "--witness-out /tmp/strong_router_r27_opt.json"
            ),
            "required_equality": (
                "normal and optimized summary bytes equal; normal and optimized "
                "R27 witness bytes equal"
            ),
        },
        "family": {
            "P_base": "d(x,c0,c1)",
            "N_base": "d(c0,x,c1)",
            "P_step": "d(P,N,P)",
            "N_step": "d(N,P,N)",
            "capacity_at_depth_h": "3^(h-1)",
            "control_leaves": "2*3^(h-1)",
            "discriminator_nodes": "(3^h-1)/2",
        },
        "finite_family_checks": finite_family_checks(),
        "r27_witness": r27_witness(),
        "compiler_checks": compiler_checks(),
        "falsifier_checks": falsifier_checks(),
        "claim_boundary": (
            "Exact recursive programs, canonical BDD checks through depth six, R27 "
            "mutations, exhaustive R9 representation lifts, and bounded variable-depth "
            "recurrence arithmetic. The all-arity "
            "r+O(sqrt(r)), O(3^r/r) result is a manuscript proof pending independent "
            "audit/formalization and prior-art review. No novelty, optimality beyond the "
            "leading coefficient, patent, FTO, practical-performance, or Tau claim follows."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS recursive strong discriminator-router family")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    if args.witness_out:
        Path(args.witness_out).write_text(json.dumps(r27_witness(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

"""Independent referee checker for the gain/loss program-vector candidate.

This file imports no OrbitSynthesis implementation.  It reconstructs the
three-element algebra, a hash-consed constant-free d/u DAG, the gain/loss
segment law, all physical control roots, constant modes, cost/depth ledgers,
mutations, and a small scoped synthesis check from first principles.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA = "orbit.program-vector-optimization.gain-loss-referee.v1"

SUBJECT_HASHES = {
    "research/tournaments/2026-08-13-program-vector-optimization/STATE.md":
        "6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6",
    "research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean":
        "c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd",
    "research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean":
        "ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2",
    "notes/QUASIPRIMAL_CONSERVATIVE_TERM_PARALLEL_PROGRAM_DEPTH.md":
        "570d4ef5468eb802689bfc139f28fd1f26250ec94dfeeacaa6d9c4fd30e25165",
    "paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md":
        "dddeb98c31805a4a68cf7c2767e61469c252aa1710a5a56d621e13787a2dc2e4",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def d(x: int, y: int, z: int) -> int:
    require(x in (0, 1, 2) and y in (0, 1, 2) and z in (0, 1, 2), "d outside Q")
    return z if x == y else x


def u(x: int) -> int:
    require(x in (0, 1, 2), "u outside Q")
    return (1, 0, 1)[x]


def words(width: int) -> Iterable[tuple[int, ...]]:
    return itertools.product((0, 1, 2), repeat=width)


def ceil_log2(value: int) -> int:
    require(value >= 1, "ceil_log2 domain")
    return (value - 1).bit_length()


def cell_negative(root_negative: bool, physical: Sequence[int]) -> bool:
    middle_odd = sum(digit == 1 for digit in physical) % 2 == 1
    return root_negative != middle_odd


def first_mismatch_loss_gain(
    target: Sequence[int], physical: Sequence[int]
) -> tuple[int, int]:
    require(len(target) == len(physical), "address width mismatch")
    for requested, placed in zip(target, physical):
        if requested != placed:
            gain = int(requested == 1 and placed == 2)
            return 1 - gain, gain
    return 0, 0


def compose_loss_gain(
    left: tuple[int, int], right: tuple[int, int]
) -> tuple[int, int]:
    loss_a, gain_a = left
    loss_b, gain_b = right
    return d(loss_a, gain_a, loss_b), d(gain_a, loss_a, gain_b)


def projection_pair(
    root_negative: bool,
    physical: Sequence[int],
    state: tuple[int, int],
) -> tuple[int, int]:
    loss, gain = state
    if cell_negative(root_negative, physical):
        return gain, u(loss)
    return loss, gain


def constant_pair(root_negative: bool, physical: Sequence[int], constant: int) -> tuple[int, int]:
    require(constant in (0, 1), "constant mode outside Boolean planes")
    if cell_negative(root_negative, physical):
        return constant, constant
    return 1 - constant, constant


@dataclass(frozen=True)
class Node:
    op: str
    args: tuple[int, ...]
    label: str = ""


class SignatureDAG:
    """Hash-consed original-signature DAG with named variable terminals."""

    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.terminals: dict[str, int] = {}
        self.unique: dict[Node, int] = {}
        self.depths: list[int] = []
        self.dependencies: list[frozenset[str]] = []

    def terminal(self, label: str) -> int:
        if label in self.terminals:
            return self.terminals[label]
        node_id = len(self.nodes)
        self.nodes.append(Node("var", (), label))
        self.terminals[label] = node_id
        self.depths.append(0)
        self.dependencies.append(frozenset((label,)))
        return node_id

    def operation(self, op: str, *args: int) -> int:
        require(op in ("u", "d"), "operation outside d/u")
        require((op == "u" and len(args) == 1) or (op == "d" and len(args) == 3), "bad arity")
        node = Node(op, tuple(args))
        old = self.unique.get(node)
        if old is not None:
            return old
        node_id = len(self.nodes)
        self.nodes.append(node)
        self.unique[node] = node_id
        self.depths.append(1 + max(self.depths[arg] for arg in args))
        dependencies: set[str] = set()
        for arg in args:
            dependencies.update(self.dependencies[arg])
        self.dependencies.append(frozenset(dependencies))
        return node_id

    def unary(self, child: int) -> int:
        return self.operation("u", child)

    def disc(self, left: int, middle: int, right: int) -> int:
        return self.operation("d", left, middle, right)

    def evaluate(self, roots: Sequence[int], assignment: dict[str, int]) -> tuple[int, ...]:
        values = [0] * len(self.nodes)
        for node_id, node in enumerate(self.nodes):
            if node.op == "var":
                values[node_id] = assignment[node.label]
            elif node.op == "u":
                values[node_id] = u(values[node.args[0]])
            else:
                values[node_id] = d(*(values[arg] for arg in node.args))
        return tuple(values[root] for root in roots)

    def reachable_operations(self, roots: Sequence[int]) -> int:
        seen: set[int] = set()
        stack = list(roots)
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            stack.extend(self.nodes[node_id].args)
        return sum(self.nodes[node_id].op != "var" for node_id in seen)

    def maximum_depth(self, roots: Sequence[int]) -> int:
        return max((self.depths[root] for root in roots), default=0)


def build_names(dag: SignatureDAG) -> tuple[int, int, int]:
    two = dag.terminal("A")
    one = dag.unary(two)
    zero = dag.unary(one)
    return two, one, zero


def build_gain_loss_block(
    dag: SignatureDAG,
    digits: tuple[int, ...],
    two: int,
    one: int,
    zero: int,
) -> list[tuple[tuple[int, ...], int, int]]:
    width = len(digits)
    require(width >= 1, "empty block must use the width-zero specialization")
    if width == 1:
        x = digits[0]
        loss_zero_branch = dag.disc(x, two, one)  # [0,1,1]
        loss_middle_branch = dag.unary(x)  # [1,0,1]
        loss_two_branch = dag.unary(loss_zero_branch)  # [1,0,0]
        gain_two_branch = dag.disc(x, two, zero)  # [0,1,0]
        return [
            ((0,), loss_zero_branch, zero),
            ((1,), loss_middle_branch, zero),
            ((2,), loss_two_branch, gain_two_branch),
        ]

    left_width = width // 2
    left = build_gain_loss_block(dag, digits[:left_width], two, one, zero)
    right = build_gain_loss_block(dag, digits[left_width:], two, one, zero)
    result: list[tuple[tuple[int, ...], int, int]] = []
    for p_left, loss_a, gain_a in left:
        for p_right, loss_b, gain_b in right:
            loss = dag.disc(loss_a, gain_a, loss_b)
            gain = dag.disc(gain_a, loss_a, gain_b)
            result.append((p_left + p_right, loss, gain))
    return result


def materialize_projection(
    width: int, root_negative: bool
) -> tuple[SignatureDAG, dict[tuple[int, ...], tuple[int, int]]]:
    dag = SignatureDAG()
    two, one, zero = build_names(dag)
    if width == 0:
        return dag, {(): (zero, one) if root_negative else (zero, zero)}
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    states = build_gain_loss_block(dag, digits, two, one, zero)
    pairs: dict[tuple[int, ...], tuple[int, int]] = {}
    for physical, loss, gain in states:
        if cell_negative(root_negative, physical):
            pairs[physical] = gain, dag.unary(loss)
        else:
            pairs[physical] = loss, gain
    return dag, pairs


def materialize_constant(
    width: int, root_negative: bool, constant: int
) -> tuple[SignatureDAG, dict[tuple[int, ...], tuple[int, int]]]:
    dag = SignatureDAG()
    _, one, zero = build_names(dag)
    bit = (zero, one)
    pairs: dict[tuple[int, ...], tuple[int, int]] = {}
    for physical in words(width):
        if cell_negative(root_negative, physical):
            pairs[physical] = bit[constant], bit[constant]
        else:
            pairs[physical] = bit[1 - constant], bit[constant]
    return dag, pairs


def build_native_block(
    dag: SignatureDAG,
    digits: tuple[int, ...],
    two: int,
    one: int,
    zero: int,
) -> list[tuple[tuple[int, ...], int]]:
    """Build states encoded as loss=0, gain=1, equal=2."""

    width = len(digits)
    require(width >= 1, "empty native block must use width-zero specialization")
    if width == 1:
        x = digits[0]
        state_zero_branch = dag.disc(zero, x, two)  # [2,0,0]
        not_x = dag.unary(x)
        state_middle_branch = dag.disc(zero, not_x, two)  # [0,2,0]
        state_two_branch = x  # [0,1,2]
        return [
            ((0,), state_zero_branch),
            ((1,), state_middle_branch),
            ((2,), state_two_branch),
        ]

    left_width = width // 2
    left = build_native_block(dag, digits[:left_width], two, one, zero)
    right = build_native_block(dag, digits[left_width:], two, one, zero)
    result: list[tuple[tuple[int, ...], int]] = []
    for p_left, state_a in left:
        for p_right, state_b in right:
            # Equal=2 is the identity; either mismatch state absorbs on the left.
            result.append((p_left + p_right, dag.disc(state_a, two, state_b)))
    return result


def materialize_native_projection(
    width: int, root_negative: bool
) -> tuple[SignatureDAG, dict[tuple[int, ...], tuple[int, int]]]:
    dag = SignatureDAG()
    two, one, zero = build_names(dag)
    if width == 0:
        return dag, {(): (zero, one) if root_negative else (zero, zero)}
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    states = build_native_block(dag, digits, two, one, zero)
    pairs: dict[tuple[int, ...], tuple[int, int]] = {}
    for physical, state in states:
        gain = dag.disc(state, two, zero)  # indicator of state=1
        if cell_negative(root_negative, physical):
            not_loss = dag.disc(state, two, one)  # [0,1,1]
            pairs[physical] = gain, not_loss
        else:
            loss = dag.disc(zero, state, one)  # indicator of state=0
            pairs[physical] = loss, gain
    return dag, pairs


def state_nodes(width: int, cache: dict[int, int] | None = None) -> int:
    if cache is None:
        cache = {}
    if width in cache:
        return cache[width]
    if width == 0:
        value = 0
    elif width == 1:
        value = 4
    else:
        left = width // 2
        value = state_nodes(left, cache) + state_nodes(width - left, cache) + 2 * 3**width
    cache[width] = value
    return value


def native_state_nodes(width: int, cache: dict[int, int] | None = None) -> int:
    if cache is None:
        cache = {}
    if width in cache:
        return cache[width]
    if width == 0:
        value = 0
    elif width == 1:
        value = 3
    else:
        left = width // 2
        value = (
            native_state_nodes(left, cache)
            + native_state_nodes(width - left, cache)
            + 3**width
        )
    cache[width] = value
    return value


def negative_cells(root_negative: bool, width: int) -> int:
    q = 3**width
    return (q + 1) // 2 if root_negative else (q - 1) // 2


def analytic_nodes(root_negative: bool, width: int) -> int:
    if width == 0:
        return 2
    return 2 + state_nodes(width) + negative_cells(root_negative, width)


def native_analytic_nodes(width: int) -> int:
    if width == 0:
        return 2
    return 2 + native_state_nodes(width) + 2 * 3**width


def depth_bound(width: int) -> int:
    return 2 if width == 0 else 4 + ceil_log2(width)


def semantic_and_dag_checks() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    pair_checks = 0
    payload_checks = 0
    constant_pair_checks = 0
    maximum_materialized_width = 9
    for width in range(maximum_materialized_width + 1):
        q = 3**width
        for root_negative in (False, True):
            dag, pairs = materialize_projection(width, root_negative)
            physicals = sorted(pairs)
            roots = tuple(root for physical in physicals for root in pairs[physical])
            actual_nodes = dag.reachable_operations(roots)
            actual_depth = dag.maximum_depth(roots)
            require(actual_nodes <= analytic_nodes(root_negative, width), "hash-consed DAG exceeded analytic count")
            require(27 * analytic_nodes(root_negative, width) <= 100 * q, "100q/27 gain/loss bound failed")
            require(analytic_nodes(root_negative, width) <= 4 * q, "4q bound failed")
            require(actual_depth <= depth_bound(width), "logarithmic depth bound failed")
            allowed = frozenset(("A", *(f"t{i}" for i in range(width))))
            require(all(dag.dependencies[root] <= allowed for root in roots), "payload dependency entered vector")

            if width <= 5:
                for target in words(width):
                    assignment = {"A": 2, **{f"t{i}": digit for i, digit in enumerate(target)}}
                    values = dag.evaluate(roots, assignment)
                    for position, physical in enumerate(physicals):
                        state = first_mismatch_loss_gain(target, physical)
                        expected = projection_pair(root_negative, physical, state)
                        observed = values[2 * position : 2 * position + 2]
                        require(observed == expected, "projection pair mismatch")
                        pair_checks += 1
                        negative = cell_negative(root_negative, physical)
                        for payload in (0, 1):
                            output = d(payload, *observed) if not negative else d(observed[0], payload, observed[1])
                            if state == (0, 0):
                                expected_output = 1 - payload if negative else payload
                            else:
                                expected_output = state[1]
                            require(output == expected_output, "base-cell payload semantics mismatch")
                            payload_checks += 1

                for constant in (0, 1):
                    const_dag, const_pairs = materialize_constant(width, root_negative, constant)
                    const_physicals = sorted(const_pairs)
                    const_roots = tuple(root for physical in const_physicals for root in const_pairs[physical])
                    const_values = const_dag.evaluate(const_roots, {"A": 2})
                    require(const_dag.reachable_operations(const_roots) <= 2, "constant mode exceeded shared names")
                    require(const_dag.maximum_depth(const_roots) <= 2, "constant mode depth exceeded names")
                    for position, physical in enumerate(const_physicals):
                        expected = constant_pair(root_negative, physical, constant)
                        observed = const_values[2 * position : 2 * position + 2]
                        require(observed == expected, "constant pair mismatch")
                        constant_pair_checks += 1

            rows.append(
                {
                    "width": width,
                    "root_sign": "N" if root_negative else "P",
                    "q": q,
                    "actual_reachable_operation_nodes": actual_nodes,
                    "analytic_nodes_including_names_and_complements": analytic_nodes(root_negative, width),
                    "hundred_q_over_27_numerator_bound": 100 * q,
                    "four_q_bound": 4 * q,
                    "actual_depth": actual_depth,
                    "depth_bound": depth_bound(width),
                }
            )

    recurrence_checks = 0
    for width in range(1, 513):
        q = 3**width
        require(9 * state_nodes(width) <= 28 * q, "28q/9 state bound failed")
        for root_negative in (False, True):
            require(27 * analytic_nodes(root_negative, width) <= 100 * q, "all-width 100q/27 inequality failed")
            require(analytic_nodes(root_negative, width) <= 4 * q, "all-width 4q inequality failed")
        recurrence_checks += 1

    # The names are deliberately not absolute outside A=2.
    anchor_mutations = []
    for anchor in (0, 1):
        names = (anchor, u(anchor), u(u(anchor)))
        require(names != (2, 1, 0), "binary anchor accidentally supplied absolute names")
        anchor_mutations.append({"A": anchor, "two_one_zero_attempt": list(names)})

    return {
        "materialized_widths": [0, maximum_materialized_width],
        "rows": rows,
        "projection_pair_checks_through_width_five": pair_checks,
        "base_cell_payload_checks_through_width_five": payload_checks,
        "constant_pair_checks_through_width_five": constant_pair_checks,
        "recurrence_widths_checked": recurrence_checks,
        "binary_anchor_name_mutation": anchor_mutations,
    }


def native_semantic_and_dag_checks() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    pair_checks = 0
    payload_checks = 0
    maximum_materialized_width = 9
    for width in range(maximum_materialized_width + 1):
        q = 3**width
        for root_negative in (False, True):
            dag, pairs = materialize_native_projection(width, root_negative)
            physicals = sorted(pairs)
            roots = tuple(root for physical in physicals for root in pairs[physical])
            actual_nodes = dag.reachable_operations(roots)
            actual_depth = dag.maximum_depth(roots)
            require(actual_nodes <= native_analytic_nodes(width), "native DAG exceeded analytic count")
            require(native_analytic_nodes(width) <= 4 * q, "native 4q bound failed")
            require(actual_depth <= depth_bound(width), "native logarithmic depth bound failed")
            allowed = frozenset(("A", *(f"t{i}" for i in range(width))))
            require(all(dag.dependencies[root] <= allowed for root in roots), "payload entered native vector")

            if width <= 5:
                for target in words(width):
                    assignment = {"A": 2, **{f"t{i}": digit for i, digit in enumerate(target)}}
                    values = dag.evaluate(roots, assignment)
                    for position, physical in enumerate(physicals):
                        state = first_mismatch_loss_gain(target, physical)
                        expected = projection_pair(root_negative, physical, state)
                        observed = values[2 * position : 2 * position + 2]
                        require(observed == expected, "native projection pair mismatch")
                        pair_checks += 1
                        negative = cell_negative(root_negative, physical)
                        for payload in (0, 1):
                            output = d(payload, *observed) if not negative else d(observed[0], payload, observed[1])
                            if state == (0, 0):
                                expected_output = 1 - payload if negative else payload
                            else:
                                expected_output = state[1]
                            require(output == expected_output, "native base-cell semantics mismatch")
                            payload_checks += 1

            rows.append(
                {
                    "width": width,
                    "root_sign": "N" if root_negative else "P",
                    "q": q,
                    "actual_reachable_operation_nodes": actual_nodes,
                    "analytic_nodes_including_names_and_extraction": native_analytic_nodes(width),
                    "four_q_bound": 4 * q,
                    "actual_depth": actual_depth,
                    "depth_bound": depth_bound(width),
                }
            )

    recurrence_checks = 0
    for width in range(1, 513):
        q = 3**width
        require(native_state_nodes(width) <= 2 * q - 3, "native 2q-3 state bound failed")
        require(native_analytic_nodes(width) <= 4 * q - 1, "native 4q-1 bound failed")
        recurrence_checks += 1
    return {
        "encoding": {"loss": 0, "gain": 1, "equal": 2},
        "state_composition": "d(SA,A,SB)",
        "positive_extraction": ["d(zero,S,one)", "d(S,A,zero)"],
        "negative_extraction": ["d(S,A,zero)", "d(S,A,one)"],
        "materialized_widths": [0, maximum_materialized_width],
        "rows": rows,
        "projection_pair_checks_through_width_five": pair_checks,
        "base_cell_payload_checks_through_width_five": payload_checks,
        "recurrence_widths_checked": recurrence_checks,
    }


def recursively_compose(
    target: tuple[int, ...],
    physical: tuple[int, ...],
    mutant: str | None = None,
) -> tuple[int, int]:
    width = len(target)
    require(width == len(physical) and width >= 1, "recursive state domain")
    if width == 1:
        state = first_mismatch_loss_gain(target, physical)
        if mutant == "drop_p2_loss" and physical == (2,) and target == (0,):
            return 0, state[1]
        return state
    split = width // 2
    left = recursively_compose(target[:split], physical[:split], mutant)
    right = recursively_compose(target[split:], physical[split:], mutant)
    loss, gain = compose_loss_gain(left, right)
    if mutant == "unguarded_gain":
        gain = left[1] | right[1]
    elif mutant == "reuse_loss_as_gain":
        gain = loss
    return loss, gain


def first_mutation_witness(kind: str) -> dict[str, object]:
    for width in range(1, 5):
        for root_negative in (False, True):
            for target in words(width):
                for physical in words(width):
                    expected_state = first_mismatch_loss_gain(target, physical)
                    if kind in ("unguarded_gain", "reuse_loss_as_gain", "drop_p2_loss"):
                        observed_state = recursively_compose(target, physical, kind)
                        if observed_state != expected_state:
                            return {
                                "width": width,
                                "root_sign": "N" if root_negative else "P",
                                "target": list(target),
                                "physical": list(physical),
                                "expected_state": list(expected_state),
                                "mutated_state": list(observed_state),
                            }
                    elif kind == "omit_negative_loss_complement":
                        if not cell_negative(root_negative, physical):
                            continue
                        loss, gain = expected_state
                        expected_pair = projection_pair(root_negative, physical, expected_state)
                        mutated_pair = (gain, loss)
                        if mutated_pair != expected_pair:
                            return {
                                "width": width,
                                "root_sign": "N" if root_negative else "P",
                                "target": list(target),
                                "physical": list(physical),
                                "expected_pair": list(expected_pair),
                                "mutated_pair": list(mutated_pair),
                            }
    raise RuntimeError(f"mutation was inert: {kind}")


def scoped_one_operation_composition_check() -> dict[str, object]:
    """Exclude one-new-node composition for the declared gain/loss interface.

    The result is deliberately scoped: inputs are the four raw Boolean signals
    LA,GA,LB,GB plus named Q constants; one u/d node may be added; both outputs
    must be roots among those inputs/constants and that one new node.
    """

    states = ((0, 0), (1, 0), (0, 1))
    rows = tuple((left, right) for left in states for right in states)
    atoms: dict[str, tuple[int, ...]] = {
        "LA": tuple(left[0] for left, _ in rows),
        "GA": tuple(left[1] for left, _ in rows),
        "LB": tuple(right[0] for _, right in rows),
        "GB": tuple(right[1] for _, right in rows),
        "zero": (0,) * len(rows),
        "one": (1,) * len(rows),
        "two": (2,) * len(rows),
    }
    target_loss = tuple(compose_loss_gain(left, right)[0] for left, right in rows)
    target_gain = tuple(compose_loss_gain(left, right)[1] for left, right in rows)
    one_node_functions: set[tuple[int, ...]] = set()
    atom_values = tuple(atoms.values())
    for value in atom_values:
        one_node_functions.add(tuple(u(x) for x in value))
    for left, middle, right in itertools.product(atom_values, repeat=3):
        one_node_functions.add(tuple(d(x, y, z) for x, y, z in zip(left, middle, right)))
    raw = set(atom_values)
    one_node_pair_exists = any(
        target_loss in raw | {new_value} and target_gain in raw | {new_value}
        for new_value in one_node_functions
    )
    require(not one_node_pair_exists, "unexpected one-node gain/loss pair composition")
    require(
        tuple(d(a[0], a[1], b[0]) for a, b in rows) == target_loss,
        "two-node loss formula failed",
    )
    require(
        tuple(d(a[1], a[0], b[1]) for a, b in rows) == target_gain,
        "two-node gain formula failed",
    )
    return {
        "input_state_rows": len(rows),
        "one_node_functions_examined": len(one_node_functions),
        "one_new_node_pair_exists": one_node_pair_exists,
        "scope": "raw LA,GA,LB,GB and named 0,1,2; one added u/d node",
        "two_node_witness": ["d(LA,GA,LB)", "d(GA,LA,GB)"],
    }


UnaryFunction = tuple[int, int, int]


def unary_apply_u(function: UnaryFunction) -> UnaryFunction:
    return tuple(u(value) for value in function)  # type: ignore[return-value]


def unary_apply_d(
    left: UnaryFunction, middle: UnaryFunction, right: UnaryFunction
) -> UnaryFunction:
    return tuple(d(x, y, z) for x, y, z in zip(left, middle, right))  # type: ignore[return-value]


def minimum_unary_pair_nodes(
    target_a: UnaryFunction, target_b: UnaryFunction, maximum: int = 4
) -> int | None:
    initial = frozenset(
        {
            (0, 1, 2),
            (0, 0, 0),
            (1, 1, 1),
            (2, 2, 2),
        }
    )
    if target_a in initial and target_b in initial:
        return 0
    queue: deque[tuple[frozenset[UnaryFunction], int]] = deque(((initial, 0),))
    seen = {initial}
    while queue:
        available, cost = queue.popleft()
        if cost >= maximum:
            continue
        functions = tuple(available)
        candidates = {unary_apply_u(function) for function in functions}
        candidates.update(
            unary_apply_d(left, middle, right)
            for left, middle, right in itertools.product(functions, repeat=3)
        )
        for candidate in candidates - available:
            extended = available | {candidate}
            if target_a in extended and target_b in extended:
                return cost + 1
            if extended not in seen:
                seen.add(extended)
                queue.append((extended, cost + 1))
    return None


def native_ternary_checks() -> dict[str, object]:
    """Check the one-d native state law and expose final-extraction costs."""

    results = []
    modes = ("E", "L", "G")
    for codes in itertools.permutations((0, 1, 2)):
        encoding = dict(zip(modes, codes))
        equal_code = encoding["E"]
        for left_mode, right_mode in itertools.product(modes, repeat=2):
            expected_mode = right_mode if left_mode == "E" else left_mode
            observed = d(encoding[left_mode], equal_code, encoding[right_mode])
            require(observed == encoding[expected_mode], "native one-d composition failed")

        inverse = {code: mode for mode, code in encoding.items()}
        positive_a: UnaryFunction = tuple(int(inverse[value] == "L") for value in (0, 1, 2))  # type: ignore[assignment]
        positive_b: UnaryFunction = tuple(int(inverse[value] == "G") for value in (0, 1, 2))  # type: ignore[assignment]
        negative_a = positive_b
        negative_b: UnaryFunction = tuple(int(inverse[value] != "L") for value in (0, 1, 2))  # type: ignore[assignment]
        positive_cost = minimum_unary_pair_nodes(positive_a, positive_b)
        negative_cost = minimum_unary_pair_nodes(negative_a, negative_b)
        require(positive_cost is not None and negative_cost is not None, "native extraction search incomplete")
        results.append(
            {
                "encoding": encoding,
                "composition_nodes": 1,
                "minimum_positive_pair_extraction_nodes": positive_cost,
                "minimum_negative_pair_extraction_nodes": negative_cost,
            }
        )
    return {
        "encodings_checked": len(results),
        "rows": results,
        "qualification": "extraction minima are per state root with named constants; cross-branch sharing not lower-bounded",
    }


def recursively_compose_native(
    target: tuple[int, ...],
    physical: tuple[int, ...],
    mutant: str | None = None,
) -> int:
    width = len(target)
    require(width == len(physical) and width >= 1, "native recursive domain")
    if width == 1:
        loss, gain = first_mismatch_loss_gain(target, physical)
        if mutant == "raw_middle_branch" and physical == (1,):
            return target[0]
        return 0 if loss else (1 if gain else 2)
    split = width // 2
    left = recursively_compose_native(target[:split], physical[:split], mutant)
    right = recursively_compose_native(target[split:], physical[split:], mutant)
    equal_code = 1 if mutant == "wrong_equal_code" else 2
    return d(left, equal_code, right)


def first_native_mutation_witness(kind: str) -> dict[str, object]:
    for width in range(1, 5):
        for root_negative in (False, True):
            for target in words(width):
                for physical in words(width):
                    loss, gain = first_mismatch_loss_gain(target, physical)
                    expected_state = 0 if loss else (1 if gain else 2)
                    if kind in ("raw_middle_branch", "wrong_equal_code"):
                        observed_state = recursively_compose_native(target, physical, kind)
                        if observed_state != expected_state:
                            return {
                                "width": width,
                                "root_sign": "N" if root_negative else "P",
                                "target": list(target),
                                "physical": list(physical),
                                "expected_state": expected_state,
                                "mutated_state": observed_state,
                            }
                    elif kind == "state_as_control_pair":
                        observed_pair = (expected_state, u(expected_state))
                        expected_pair = projection_pair(root_negative, physical, (loss, gain))
                        if observed_pair != expected_pair:
                            return {
                                "width": width,
                                "root_sign": "N" if root_negative else "P",
                                "target": list(target),
                                "physical": list(physical),
                                "expected_pair": list(expected_pair),
                                "mutated_pair": list(observed_pair),
                            }
    raise RuntimeError(f"native mutation was inert: {kind}")


def mutation_checks() -> dict[str, object]:
    return {
        "gain_loss": {
            kind: first_mutation_witness(kind)
            for kind in (
                "drop_p2_loss",
                "unguarded_gain",
                "reuse_loss_as_gain",
                "omit_negative_loss_complement",
            )
        },
        "native": {
            kind: first_native_mutation_witness(kind)
            for kind in (
                "raw_middle_branch",
                "wrong_equal_code",
                "state_as_control_pair",
            )
        },
    }


def find_repo_root(script_path: Path) -> Path:
    for candidate in script_path.resolve().parents:
        if (candidate / "research/tournaments/2026-08-13-program-vector-optimization/STATE.md").is_file():
            return candidate
    raise RuntimeError("repository root not found")


def freeze_subject(repo: Path) -> dict[str, str]:
    observed = {}
    for relative, expected in SUBJECT_HASHES.items():
        path = repo / relative
        require(path.is_file(), f"missing subject: {relative}")
        digest = sha256_bytes(path.read_bytes())
        require(digest == expected, f"subject hash drift: {relative}")
        observed[relative] = digest
    return observed


def run(script_path: Path) -> dict[str, object]:
    repo = find_repo_root(script_path)
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "EXACT_NATIVE_AND_GAIN_LOSS_4Q_VECTOR_PASS",
        "checker_sha256": sha256_bytes(script_path.read_bytes()),
        "frozen_subjects": freeze_subject(repo),
        "algebra": {
            "carrier": [0, 1, 2],
            "composition": {
                "loss": "d(LA,GA,LB)",
                "gain": "d(GA,LA,GB)",
            },
            "positive_pair": ["L", "G"],
            "negative_pair": ["G", "u(L)"],
        },
        "gain_loss_dag_and_semantics": semantic_and_dag_checks(),
        "native_dag_and_semantics": native_semantic_and_dag_checks(),
        "scoped_one_operation_check": scoped_one_operation_composition_check(),
        "native_ternary": native_ternary_checks(),
        "mutations": mutation_checks(),
        "scope": {
            "proved_by_construction_and_integer_induction": [
                "all 2*3^w projection controls for every w and either root sign",
                "both constant modes",
                "constant-free d/u syntax under A=2 names",
                "4q shared-operation-node upper bound including names and final complements",
                "stronger 27*size <= 100q gain/loss upper bound",
                "4+ceil(log_2 w) projection depth above raw A/address inputs",
            ],
            "not_claimed": [
                "global optimality or a lower bound outside the scoped one-node interface grammar",
                "ordinary formula or bounded-fanout cost",
                "binary-branch controls",
                "integrated compiler constants or manuscript promotion",
                "novelty, practicality, patent scope, or freedom to operate",
            ],
        },
    }
    result["semantic_sha256"] = sha256_bytes(canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    script_path = Path(__file__)
    result = run(script_path)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(result["semantic_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

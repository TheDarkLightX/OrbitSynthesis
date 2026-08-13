"""Independent, no-author-import audit of the parallel program-vector lane.

The executable deliberately rebuilds the algebra, recursive P/N semantics,
hash-consed original-signature DAG, ROBDD replay, and compiler arithmetic from
first principles.  It imports only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "orbit.semantic-router.program-vector-independent-audit.v1"
MIN_R = 64
MAX_R = 16_384
RESERVE_C = 4

SUBJECT_HASHES = {
    "STATE.md": "5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133",
    "lanes/fused/check_strong_router_family.py": "07fb1d8d322e57a7af666bae5b699c072805ff1d15eef1f1e7c2d87208729ef8",
    "lanes/fused/summary.json": "6042127fd9f214e63bc38aa8e6367d1db7580c24b2b2e7a3aeba16625279aff0",
    "lanes/fused/r27_witness.json": "6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65",
    "lanes/fused/REPORT.md": "5ed37d98357eb03a2f6ded9f741c9fb52d8f5ad821585c81be544f201945f8c6",
    "audits/variable_compiler/REPORT.md": "174a8fdf32e47fcce650298df5554a9f7c101fc67cc7be4ab4d2acb14bc5c661",
    "lanes/program_vector/REPORT.md": "d4a4a6e8c512b915c35129b7158da5a841456c26acc569e677fda8a965f30834",
    "lanes/program_vector/check_parallel_program_vector.py": "2ba586a1ef97822aebbbcf692d29cd5bd3f8bbc8e785ddce43aff2180df3c350",
    "lanes/program_vector/manifest.json": "9d470da6b6f5559bc7e5b461255ce6d3bc3bfab10025d6ab48a99f41a34c694e",
    "lanes/program_vector/receipt.json": "c9e8b1ad9c57f4ef55ea458b2573f20578a137a6c7b5fb1a66707bb7ee68b632",
    "lanes/program_vector/receipt_optimized.json": "c9e8b1ad9c57f4ef55ea458b2573f20578a137a6c7b5fb1a66707bb7ee68b632",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def d(x: int, y: int, z: int) -> int:
    require(x in (0, 1, 2) and y in (0, 1, 2) and z in (0, 1, 2), "d outside Q")
    return z if x == y else x


def u(x: int) -> int:
    require(x in (0, 1, 2), "u outside Q")
    return (1, 0, 1)[x]


def words(width: int) -> Iterator[tuple[int, ...]]:
    return itertools.product((0, 1, 2), repeat=width)


def word_at(index: int, width: int) -> tuple[int, ...]:
    require(0 <= index < 3**width, "ternary word index out of range")
    out = [0] * width
    for position in range(width - 1, -1, -1):
        out[position] = index % 3
        index //= 3
    return tuple(out)


def cell_positive(root_negative: bool, physical: Sequence[int]) -> bool:
    return root_negative == (sum(digit == 1 for digit in physical) % 2 == 1)


def first_mismatch_state(
    target: Sequence[int], physical: Sequence[int]
) -> tuple[int, int]:
    require(len(target) == len(physical), "word length mismatch")
    for requested, placed in zip(target, physical):
        if requested != placed:
            return 0, int(requested == 1 and placed == 2)
    return 1, 0


TRANSITION = {
    0: ("project", "zero", "zero"),
    1: ("zero", "project", "one"),
    2: ("zero", "zero", "project"),
}


def recursive_mode_table(target: tuple[int, ...]) -> dict[tuple[int, ...], str]:
    """Expand the stated P/N child programs without using E/G."""
    if not target:
        return {(): "project"}
    suffix = recursive_mode_table(target[1:])
    table: dict[tuple[int, ...], str] = {}
    for physical_digit, mode in enumerate(TRANSITION[target[0]]):
        if mode == "project":
            for tail, tail_mode in suffix.items():
                table[(physical_digit, *tail)] = tail_mode
        else:
            for tail in words(len(target) - 1):
                table[(physical_digit, *tail)] = mode
    return table


def mode_pair(positive: bool, mode: str) -> tuple[int, int]:
    if positive:
        return {
            "project": (0, 0),
            "zero": (1, 0),
            "one": (0, 1),
        }[mode]
    return {
        "project": (0, 1),
        "zero": (0, 0),
        "one": (1, 1),
    }[mode]


def law_pair(root_negative: bool, target: Sequence[int], physical: Sequence[int]) -> tuple[int, int]:
    equal, good = first_mismatch_state(target, physical)
    active = equal | good
    if cell_positive(root_negative, physical):
        return 1 - active, good
    return good, active


def constant_pair(root_negative: bool, physical: Sequence[int], constant: int) -> tuple[int, int]:
    require(constant in (0, 1), "non-Boolean constant mode")
    if cell_positive(root_negative, physical):
        return 1 - constant, constant
    return constant, constant


def eval_bottom(positive: bool, payload: int, pair: tuple[int, int]) -> int:
    return d(payload, pair[0], pair[1]) if positive else d(pair[0], payload, pair[1])


def compose_state(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    e_left, g_left = left
    e_right, g_right = right
    return e_left & e_right, g_left | (e_left & g_right)


def semantic_checks() -> dict[str, object]:
    primitive_rows = 0
    for x, y, z in itertools.product((0, 1, 2), repeat=3):
        require(d(x, y, z) == (z if x == y else x), "discriminator definition drift")
        primitive_rows += 1
    require(tuple(u(x) for x in (0, 1, 2)) == (1, 0, 1), "unary operation drift")

    # The anchor-derived names and all original-signature Boolean connectives.
    two = 2
    one = u(two)
    zero = u(one)
    require((two, one, zero) == (2, 1, 0), "A=2 names are wrong")
    delta_rows = 0
    for x in (0, 1, 2):
        delta0 = u(d(x, two, one))
        delta1 = d(x, two, zero)
        delta2 = u(d(x, zero, one))
        require((delta0, delta1, delta2) == tuple(int(x == j) for j in range(3)), "delta formula failed")
        delta_rows += 1
    connective_rows = 0
    for x, y in itertools.product((0, 1), repeat=2):
        require(d(x, one, y) == (x & y), "AND realization failed")
        require(d(x, zero, y) == (x | y), "OR realization failed")
        require(u(x) == 1 - x, "NOT realization failed")
        connective_rows += 1

    # The two planes stay encoded through both routing stages.  This exact
    # two-node decoder is therefore needed only at the final root.
    decoder_rows = 0
    for value, (high, low) in enumerate(((0, 0), (0, 1), (1, 0))):
        decoded = d(d(high, one, two), zero, low)
        require(decoded == value, "two-plane decoder failed")
        decoder_rows += 1

    # Associativity is checked on all Boolean pairs, including the otherwise
    # unreachable state (E,G)=(1,1), so the algebraic law has no hidden domain.
    associative_rows = 0
    boolean_states = tuple(itertools.product((0, 1), repeat=2))
    for a, b, c in itertools.product(boolean_states, repeat=3):
        require(compose_state(compose_state(a, b), c) == compose_state(a, compose_state(b, c)), "segment law not associative")
        associative_rows += 1

    pair_checks = 0
    disjoint_checks = 0
    composition_checks = 0
    for width in range(7):
        for target in words(width):
            recursive = recursive_mode_table(target)
            for physical in words(width):
                state = first_mismatch_state(target, physical)
                expected_mode = "project" if state[0] else ("one" if state[1] else "zero")
                require(recursive[physical] == expected_mode, "recursive mode and first mismatch disagree")
                require(not (state[0] and state[1]), "E/G disjointness failed")
                disjoint_checks += 1
                for split in range(width + 1):
                    left = first_mismatch_state(target[:split], physical[:split])
                    right = first_mismatch_state(target[split:], physical[split:])
                    require(compose_state(left, right) == state, "segment composition failed")
                    composition_checks += 1
                for root_negative in (False, True):
                    positive = cell_positive(root_negative, physical)
                    pair = law_pair(root_negative, target, physical)
                    require(pair == mode_pair(positive, expected_mode), "E/G pair formula failed")
                    for payload in (0, 1):
                        value = eval_bottom(positive, payload, pair)
                        expected = payload if expected_mode == "project" else int(expected_mode == "one")
                        if not positive and expected_mode == "project":
                            expected = 1 - payload
                        require(value == expected, "bottom P/N cell semantics failed")
                        pair_checks += 1
                    for constant in (0, 1):
                        const_program = constant_pair(root_negative, physical, constant)
                        for payload in (0, 1):
                            require(eval_bottom(positive, payload, const_program) == constant, "constant pair failed")
                            pair_checks += 1

    # A concrete unguarded-right-block counterexample.
    target = (0, 1)
    physical = (1, 2)
    left = first_mismatch_state(target[:1], physical[:1])
    right = first_mismatch_state(target[1:], physical[1:])
    correct = compose_state(left, right)[1]
    unguarded = left[1] | right[1]
    require((correct, unguarded) == (0, 1), "unguarded-G mutation did not fail")

    # Absolute names are not stable on a binary anchor.
    binary_name_rows = []
    for anchor in (0, 1):
        names = (anchor, u(anchor), u(u(anchor)))
        binary_name_rows.append({"anchor": anchor, "two_one_zero_attempt": list(names)})
        require(names != (2, 1, 0), "binary anchor accidentally supplied absolute names")

    return {
        "primitive_d_rows": primitive_rows,
        "delta_rows": delta_rows,
        "boolean_connective_rows": connective_rows,
        "two_plane_decoder_rows": decoder_rows,
        "two_plane_decoder_d_nodes": 2,
        "associativity_rows": associative_rows,
        "first_mismatch_disjoint_rows": disjoint_checks,
        "segment_composition_rows": composition_checks,
        "pair_and_constant_evaluations": pair_checks,
        "unguarded_G_witness": {
            "target": list(target),
            "physical": list(physical),
            "correct_G": correct,
            "unguarded_G": unguarded,
        },
        "binary_absolute_name_mutation": binary_name_rows,
    }


@dataclass(frozen=True)
class Node:
    op: str
    args: tuple[int, ...]


class SignatureDAG:
    """Hash-consed d/u circuit with named input terminals."""

    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.unique: dict[Node, int] = {}
        self.terminal_ids: dict[str, int] = {}
        self.depth: list[int] = []
        self.dependencies: list[frozenset[str]] = []

    def terminal(self, name: str) -> int:
        if name in self.terminal_ids:
            return self.terminal_ids[name]
        node_id = len(self.nodes)
        node = Node("var", ())
        self.nodes.append(node)
        self.terminal_ids[name] = node_id
        self.depth.append(0)
        self.dependencies.append(frozenset((name,)))
        return node_id

    def operation(self, op: str, *args: int) -> int:
        require(op in ("u", "d"), "operation outside original signature")
        require((op == "u" and len(args) == 1) or (op == "d" and len(args) == 3), "bad arity")
        node = Node(op, tuple(args))
        existing = self.unique.get(node)
        if existing is not None:
            return existing
        node_id = len(self.nodes)
        self.nodes.append(node)
        self.unique[node] = node_id
        self.depth.append(1 + max(self.depth[arg] for arg in args))
        deps: set[str] = set()
        for arg in args:
            deps.update(self.dependencies[arg])
        self.dependencies.append(frozenset(deps))
        return node_id

    def unary(self, x: int) -> int:
        return self.operation("u", x)

    def discr(self, x: int, y: int, z: int) -> int:
        return self.operation("d", x, y, z)

    @property
    def operation_count(self) -> int:
        return len(self.unique)

    def evaluate(self, roots: Sequence[int], assignment: dict[str, int]) -> tuple[int, ...]:
        terminal_name = {node_id: name for name, node_id in self.terminal_ids.items()}
        values: list[int] = [0] * len(self.nodes)
        for node_id, node in enumerate(self.nodes):
            if node.op == "var":
                values[node_id] = assignment[terminal_name[node_id]]
            elif node.op == "u":
                values[node_id] = u(values[node.args[0]])
            else:
                values[node_id] = d(*(values[arg] for arg in node.args))
        return tuple(values[root] for root in roots)

    def expanded_forest_operations(self, roots: Sequence[int]) -> int:
        sizes = [0] * len(self.nodes)
        for node_id, node in enumerate(self.nodes):
            if node.op != "var":
                sizes[node_id] = 1 + sum(sizes[arg] for arg in node.args)
        return sum(sizes[root] for root in roots)

    def maximum_fanout(self, roots: Sequence[int]) -> int:
        references = [0] * len(self.nodes)
        for node in self.nodes:
            for arg in node.args:
                references[arg] += 1
        for root in roots:
            references[root] += 1
        return max(references, default=0)


def build_names(dag: SignatureDAG) -> tuple[int, int, int]:
    two = dag.terminal("A")
    one = dag.unary(two)
    zero = dag.unary(one)
    return two, one, zero


def boolean_and(dag: SignatureDAG, one: int, x: int, y: int) -> int:
    return dag.discr(x, one, y)


def boolean_or(dag: SignatureDAG, zero: int, x: int, y: int) -> int:
    return dag.discr(x, zero, y)


def build_state_block(
    dag: SignatureDAG,
    digits: tuple[int, ...],
    two: int,
    one: int,
    zero: int,
) -> list[tuple[tuple[int, ...], int, int]]:
    width = len(digits)
    require(width >= 1, "empty state block")
    if width == 1:
        x = digits[0]
        delta0 = dag.unary(dag.discr(x, two, one))
        delta1 = dag.discr(x, two, zero)
        delta2 = dag.unary(dag.discr(x, zero, one))
        return [((0,), delta0, zero), ((1,), delta1, zero), ((2,), delta2, delta1)]
    left_width = width // 2
    left = build_state_block(dag, digits[:left_width], two, one, zero)
    right = build_state_block(dag, digits[left_width:], two, one, zero)
    out: list[tuple[tuple[int, ...], int, int]] = []
    for p_left, e_left, g_left in left:
        for p_right, e_right, g_right in right:
            equal = boolean_and(dag, one, e_left, e_right)
            guarded = boolean_and(dag, one, e_left, g_right)
            good = boolean_or(dag, zero, g_left, guarded)
            out.append((p_left + p_right, equal, good))
    return out


def materialize_vector(width: int, root_negative: bool) -> tuple[SignatureDAG, dict[tuple[int, ...], tuple[int, int]], dict[str, int]]:
    dag = SignatureDAG()
    two, one, zero = build_names(dag)
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    names_count = dag.operation_count
    pairs: dict[tuple[int, ...], tuple[int, int]] = {}
    state_start = dag.operation_count
    if width == 0:
        pairs[()] = (zero, zero) if not root_negative else (zero, one)
    else:
        states = build_state_block(dag, digits, two, one, zero)
        state_end = dag.operation_count
        for physical, equal, good in states:
            active = boolean_or(dag, zero, equal, good)
            if cell_positive(root_negative, physical):
                pairs[physical] = dag.unary(active), good
            else:
                pairs[physical] = good, active
    state_end = locals().get("state_end", state_start)
    counters = {
        "shared_name_nodes": names_count,
        "state_nodes": state_end - state_start,
        "final_pair_nodes": dag.operation_count - state_end,
    }
    return dag, pairs, counters


def state_recurrence(width: int, cache: dict[int, int] | None = None) -> int:
    if cache is None:
        cache = {}
    if width in cache:
        return cache[width]
    if width == 0:
        value = 0
    elif width == 1:
        value = 5
    else:
        left = width // 2
        value = state_recurrence(left, cache) + state_recurrence(width - left, cache) + 3 * 3**width
    cache[width] = value
    return value


def vector_logic_upper(width: int) -> int:
    if width == 0:
        return 0
    q = 3**width
    return state_recurrence(width) + q + (q + 1) // 2


def ceil_log2(value: int) -> int:
    require(value >= 1, "ceil_log2 domain")
    return (value - 1).bit_length()


def vector_depth_upper(width: int) -> int:
    return 2 if width == 0 else 6 + 2 * ceil_log2(width)


def dag_checks() -> dict[str, object]:
    rows = []
    value_checks = 0
    max_width = 9
    for width in range(max_width + 1):
        q = 3**width
        for root_negative in (False, True):
            dag, pairs, counters = materialize_vector(width, root_negative)
            roots = tuple(node for physical in sorted(pairs) for node in pairs[physical])
            logic_nodes = dag.operation_count - counters["shared_name_nodes"]
            upper = vector_logic_upper(width)
            require(counters["shared_name_nodes"] == 2, "name nodes not shared exactly once")
            require(logic_nodes <= upper, "materialized DAG exceeded recurrence")
            require(upper <= 7 * q, "7q logic upper failed")
            # The stronger total bound, including both shared names, follows
            # from slack; check it exactly rather than silently excluding them.
            require(dag.operation_count <= 7 * q, "7q total operation bound failed")
            output_depth = max(dag.depth[root] for root in roots)
            require(output_depth <= vector_depth_upper(width), "vector depth upper failed")
            allowed = frozenset(("A", *(f"t{i}" for i in range(width))))
            require(all(dag.dependencies[root] <= allowed for root in roots), "payload dependency entered vector")

            if width <= 5:
                for target in words(width):
                    assignment = {"A": 2, **{f"t{i}": digit for i, digit in enumerate(target)}}
                    values = dag.evaluate(roots, assignment)
                    for position, physical in enumerate(sorted(pairs)):
                        require(values[2 * position : 2 * position + 2] == law_pair(root_negative, target, physical), "DAG pair evaluation failed")
                        value_checks += 1

            rows.append(
                {
                    "width": width,
                    "root_sign": "N" if root_negative else "P",
                    "q": q,
                    "operation_nodes_including_names": dag.operation_count,
                    "operation_nodes_excluding_names": logic_nodes,
                    "state_recurrence_upper": state_recurrence(width),
                    "vector_logic_upper": upper,
                    "depth": output_depth,
                    "depth_upper": vector_depth_upper(width),
                    "maximum_fanout": dag.maximum_fanout(roots),
                    "unshared_formula_forest_operations": dag.expanded_forest_operations(roots),
                    **counters,
                }
            )

    recurrence_rows = 0
    for width in range(1, 513):
        q = 3**width
        require(state_recurrence(width) <= 5 * q, "state recurrence induction bound failed")
        require(vector_logic_upper(width) <= 7 * q, "vector recurrence bound failed")
        require(vector_logic_upper(width) + 2 <= 7 * q, "7q total including shared names failed")
        recurrence_rows += 1

    return {
        "materialized_widths": [0, max_width],
        "rows": rows,
        "exact_pair_value_checks_through_width_five": value_checks,
        "recurrence_widths_checked": recurrence_rows,
        "interpretation": "same hash-consed DAG with unrestricted fanout; not an unshared formula bound",
    }


class ROBDD:
    """Small canonical ROBDD whose ternary apply calls d at terminals."""

    def __init__(self) -> None:
        self.nodes: list[tuple[int, int, int]] = [(-1, 0, 0), (-1, 1, 1)]
        self.unique: dict[tuple[int, int, int], int] = {}
        self.apply_cache: dict[tuple[int, int, int], int] = {}

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

    def cofactor(self, node: int, variable: int, value: int) -> int:
        if node < 2:
            return node
        top, low, high = self.nodes[node]
        return (low, high)[value] if top == variable else node

    def apply_d(self, x: int, y: int, z: int) -> int:
        key = (x, y, z)
        if key in self.apply_cache:
            return self.apply_cache[key]
        if x < 2 and y < 2 and z < 2:
            out = d(x, y, z)
        else:
            variables = [self.nodes[node][0] for node in (x, y, z) if node >= 2]
            variable = min(variables)
            low = self.apply_d(*(self.cofactor(node, variable, 0) for node in (x, y, z)))
            high = self.apply_d(*(self.cofactor(node, variable, 1) for node in (x, y, z)))
            out = self.make(variable, low, high)
        self.apply_cache[key] = out
        return out

    def complement(self, node: int) -> int:
        return self.apply_d(0, node, 1)


def eval_router_bdd(
    manager: ROBDD,
    width: int,
    root_negative: bool,
    leaves: Sequence[int],
    target: tuple[int, ...] | None,
    constant: int | None = None,
) -> int:
    require(len(leaves) == 3**width, "wrong physical leaf count")
    require((target is None) != (constant is None), "choose target or constant mode")

    def recurse(prefix: tuple[int, ...], negative: bool) -> int:
        depth = len(prefix)
        if depth == width:
            index = 0
            for digit in prefix:
                index = 3 * index + digit
            positive = not negative
            pair = constant_pair(root_negative, prefix, int(constant)) if target is None else law_pair(root_negative, target, prefix)
            payload = leaves[index]
            return manager.apply_d(payload, pair[0], pair[1]) if positive else manager.apply_d(pair[0], payload, pair[1])
        children = tuple(recurse((*prefix, digit), negative ^ (digit == 1)) for digit in (0, 1, 2))
        return manager.apply_d(*children)

    return recurse((), root_negative)


def router_and_padding_checks() -> dict[str, object]:
    mode_checks = 0
    constant_checks = 0
    last_nodes = 0
    for width in range(5):
        q = 3**width
        manager = ROBDD()
        leaves = tuple(manager.variable(index) for index in range(q))
        for root_negative in (False, True):
            for target_index in range(q):
                target = word_at(target_index, width)
                root = eval_router_bdd(manager, width, root_negative, leaves, target)
                expected = manager.complement(leaves[target_index]) if root_negative else leaves[target_index]
                require(root == expected, "full P/N router projection failed")
                mode_checks += 1
            for constant in (0, 1):
                root = eval_router_bdd(manager, width, root_negative, leaves, None, constant)
                require(root == constant, "full P/N router constant failed")
                constant_checks += 1
        last_nodes = len(manager.nodes)

    # Every live count is tested, not only q-1.  Unused slots duplicate the
    # last live branch, and only live physical targets are requested.
    padding_checks = 0
    for width in range(1, 5):
        q = 3**width
        manager = ROBDD()
        all_live_variables = tuple(manager.variable(index) for index in range(q))
        for live_count in range(1, q + 1):
            leaves = tuple(all_live_variables[min(index, live_count - 1)] for index in range(q))
            for root_negative in (False, True):
                for target_index in range(live_count):
                    root = eval_router_bdd(manager, width, root_negative, leaves, word_at(target_index, width))
                    expected = manager.complement(all_live_variables[target_index]) if root_negative else all_live_variables[target_index]
                    require(root == expected, "duplicate-last padding changed a live target")
                    padding_checks += 1

    return {
        "projection_or_complement_checks_through_width_four": mode_checks,
        "constant_mode_checks_through_width_four": constant_checks,
        "all_live_count_padding_checks_through_width_four": padding_checks,
        "last_mode_robdd_nodes": last_nodes,
    }


def ceil_log3(value: int) -> int:
    require(value >= 1, "ceil_log3 domain")
    power = 1
    exponent = 0
    while power < value:
        power *= 3
        exponent += 1
    return exponent


def floor_power3(value: int) -> tuple[int, int]:
    require(value >= 1, "floor_power3 domain")
    exponent = 0
    power = 1
    while 3 * power <= value:
        power *= 3
        exponent += 1
    return exponent, power


def residual_first(total: int, width: int) -> tuple[int, ...]:
    require(total >= 0 and width >= 1, "bad chunk dimensions")
    if total == 0:
        return ()
    remainder = total % width
    return ((remainder,) if remainder else ()) + (width,) * (total // width)


def prefix_instance_count(widths: Sequence[int]) -> tuple[int, int]:
    instances = 0
    assignments = 1
    for width in widths:
        instances += assignments
        assignments *= 2**width
    return instances, assignments


def compiler_ledger(r: int) -> dict[str, int]:
    require(r >= MIN_R, "compiler regime begins at r=64")
    reserve = RESERVE_C + ceil_log3(r * r)
    h = r - reserve
    b, m = floor_power3(h)
    prefix_coordinates = r - b
    p = 3**prefix_coordinates

    local_router_nodes = (3 * m - 1) * 3**m
    local_program_nodes = vector_logic_upper(b)
    prefix_router_nodes = 3 * p - 1
    prefix_program_nodes = vector_logic_upper(prefix_coordinates)
    anchor_nodes = 4 * (r - 1)
    shared_names = 2
    final_decoder = 2
    final_glue = 3
    nonbinary_nodes = (
        local_router_nodes
        + local_program_nodes
        + prefix_router_nodes
        + prefix_program_nodes
        + anchor_nodes
        + shared_names
        + final_decoder
        + final_glue
    )

    anchor_depth = 3 * ceil_log2(r)
    local_control_depth = anchor_depth + vector_depth_upper(b)
    local_plane_depth = max(anchor_depth + 2, local_control_depth) + b + 1
    prefix_control_depth = anchor_depth + vector_depth_upper(prefix_coordinates)
    prefix_plane_depth = max(local_plane_depth, prefix_control_depth) + prefix_coordinates + 1
    nonbinary_depth = prefix_plane_depth + 2 + 2

    k = math.isqrt(r)
    q = 3**k
    binary_width = q.bit_length() - 1
    widths = residual_first(r - 1, binary_width)
    instances, assignments = prefix_instance_count(widths)
    require(assignments == 2 ** (r - 1), "binary prefix product drift")
    binary_router_nodes = ((3 * q - 1) // 2) * instances
    binary_control_nodes = sum(6 * q * (2**width - 1) for width in widths)
    binary_fixed_nodes = 4 * r + 10
    binary_nodes = binary_router_nodes + binary_control_nodes + binary_fixed_nodes
    binary_depth = (k + 1) * len(widths) + 2 * binary_width + anchor_depth + 8

    return {
        "r": r,
        "reserve": reserve,
        "H": h,
        "b": b,
        "M": m,
        "prefix_coordinates": prefix_coordinates,
        "P": p,
        "local_table_count": 3**m,
        "local_router_nodes_two_planes": local_router_nodes,
        "local_program_nodes_shared": local_program_nodes,
        "prefix_router_nodes_two_planes": prefix_router_nodes,
        "prefix_program_nodes_shared": prefix_program_nodes,
        "anchor_nodes": anchor_nodes,
        "shared_names": shared_names,
        "final_decoder_nodes_once": final_decoder,
        "final_glue_nodes": final_glue,
        "nonbinary_nodes": nonbinary_nodes,
        "nonbinary_depth": nonbinary_depth,
        "binary_k": k,
        "binary_q": q,
        "binary_logical_width": binary_width,
        "binary_levels": len(widths),
        "binary_router_nodes": binary_router_nodes,
        "binary_control_nodes": binary_control_nodes,
        "binary_fixed_nodes": binary_fixed_nodes,
        "binary_nodes": binary_nodes,
        "binary_depth": binary_depth,
    }


def ratio_decimal(numerator: int, denominator: int, places: int = 12) -> str:
    require(denominator > 0 and numerator >= 0, "bad ratio")
    scale = 10**places
    rounded = (numerator * scale + denominator // 2) // denominator
    whole, fraction = divmod(rounded, scale)
    return f"{whole}.{fraction:0{places}d}"


def compiler_checks() -> dict[str, object]:
    selected_r = (64, 90, 93, 94, 128, 256, 338, 339, 512, 900, 1024, 4096, 6574, 8192, MAX_R)
    selected: list[dict[str, object]] = []
    maximum = (0, 1, 0)  # numerator, denominator, r
    binary_below_r_from: int | None = None
    jump_checks = 0
    for r in range(MIN_R, MAX_R + 1):
        row = compiler_ledger(r)
        target = 3**r
        require(row["H"] >= r // 2, "H<r/2")
        require(3 * row["M"] > row["H"] and row["M"] <= row["H"], "floor power bracket failed")
        require(6 * row["M"] > r, "M<=r/6")
        require(row["nonbinary_nodes"] * r <= 62 * target, "nonbinary 62-unit bound failed")
        require(row["binary_nodes"] * r <= target, "binary one-unit bound failed")
        require(row["nonbinary_depth"] <= r + 5 * ceil_log2(r) + 12, "nonbinary depth bound failed")
        binary_q = row["binary_q"]
        binary_Q = 2 ** row["binary_logical_width"]
        binary_N = 2 ** (r - 1)
        require(binary_Q <= binary_q < 2 * binary_Q, "binary floor-log bracket failed")
        require(binary_Q < binary_N, "binary Q<N failed")
        require(row["binary_router_nodes"] < 6 * 2**r, "binary router analytic envelope failed")
        require(row["binary_control_nodes"] < 6 * r * binary_q**2, "binary control analytic envelope failed")
        if r >= 339:
            require(row["binary_depth"] < r, "binary depth coefficient bound failed")
            if binary_below_r_from is None:
                binary_below_r_from = r
        numerator = row["nonbinary_nodes"] * r
        if numerator * maximum[1] > maximum[0] * target:
            maximum = (numerator, target, r)
        if r in selected_r:
            selected.append(
                {
                    "r": r,
                    "reserve": row["reserve"],
                    "H": row["H"],
                    "b": row["b"],
                    "M": row["M"],
                    "prefix_coordinates": row["prefix_coordinates"],
                    "nonbinary_normalized": ratio_decimal(numerator, target),
                    "nonbinary_depth": row["nonbinary_depth"],
                    "binary_normalized": ratio_decimal(row["binary_nodes"] * r, target),
                    "binary_depth": row["binary_depth"],
                }
            )
        if r > MIN_R:
            previous = compiler_ledger(r - 1)
            if previous["M"] != row["M"] or previous["reserve"] != row["reserve"]:
                jump_checks += 1

    require(binary_below_r_from == 339, "binary <r threshold drift")

    # Exact symbolic inequalities behind the 62+1 ledger.
    analytic_rows = 0
    for r in range(MIN_R, MAX_R + 1):
        row = compiler_ledger(r)
        target = 3**r
        m = row["M"]
        require(81 * m * 3**m * r <= target, "two-log local reserve inequality failed")
        require((11 * r + 7) * r < target, "lower-order unit failed")
        require(10 * row["P"] * r < 60 * target, "prefix 60-unit inequality failed")
        analytic_rows += 1

    # Load-bearing mutations.
    sequential_r = 512
    sequential = compiler_ledger(sequential_r)
    q_prefix = sequential["P"]
    w_prefix = sequential["prefix_coordinates"]
    sequential_cost = q_prefix * w_prefix
    require(sequential_cost * sequential_r > 100 * 3**sequential_r, "q*w mutation did not exceed 100 units")

    single_r = 6574
    single_h = single_r - (RESERVE_C + ceil_log3(single_r))
    _, single_m = floor_power3(single_h)
    single_local = (3 * single_m - 1) * 3**single_m
    require(single_m == 6561, "single-log witness M drift")
    require(single_local * single_r > 62 * 3**single_r, "single-log mutation did not exceed 62 units")

    # Ceiling-to-next-power is not an innocent rounding change: find its first
    # audited arity where M>H and record the failed budget invariant.
    ceiling_witness = None
    for r in range(MIN_R, 4097):
        h = r - (RESERVE_C + ceil_log3(r * r))
        b, floor_m = floor_power3(h)
        ceil_m = floor_m if floor_m == h else 3 ** (b + 1)
        if ceil_m > h:
            ceiling_witness = {"r": r, "H": h, "floor_M": floor_m, "ceiling_M": ceil_m}
            break
    require(ceiling_witness is not None, "rounding mutation witness missing")

    # A decoder per local table is intentionally absent.  Its exact extra cost
    # is recorded to make the one-decoder ledger falsifiable.
    decoder_probe = compiler_ledger(93)
    repeated_decoder_extra = 2 * decoder_probe["local_table_count"] - 2
    require(decoder_probe["final_decoder_nodes_once"] == 2, "decoder was not charged exactly once")
    require(repeated_decoder_extra > 0, "repeated decoder mutation inert")

    # The tail polynomial claimed by the conservative binary proof.
    tail_values = []
    for k in (30, 31, 40, 64, 128):
        polynomial = k**3 - 27 * k**2 - 19 * k + 9
        require(polynomial > 0, "binary tail polynomial failed")
        tail_values.append({"k": k, "polynomial": polynomial})
    tail_increment_at_30 = 3 * 30**2 - 51 * 30 - 45
    require(tail_increment_at_30 > 0, "tail polynomial is not increasing from k=30")

    analytic_r = 64
    analytic_k = math.isqrt(analytic_r)
    analytic_size_witnesses = {
        "r": analytic_r,
        "Q_less_than_N": 3**analytic_k < 2 ** (analytic_r - 1),
        "router_quarter_unit": 24 * analytic_r * 2**analytic_r < 3**analytic_r,
        "control_quarter_unit": 24 < analytic_r**2,
        "square_boundary": 3 ** (analytic_k**2 - 2 * analytic_k) >= analytic_k**8,
        "fixed_quarter_unit": 4 * (4 * analytic_r + 10) * analytic_r < 3**analytic_r,
        "lower_order_unit": (11 * analytic_r + 7) * analytic_r < 3**analytic_r,
        "lower_order_ratio_decreases": 22 * analytic_r**2 - 8 * analytic_r - 18 > 0,
    }
    require(all(value for key, value in analytic_size_witnesses.items() if key != "r"), "analytic base witness failed")

    # Giant schedule is deliberately not asserted for the finite tail.
    small_valid = []
    for r in range(1, MIN_R):
        reserve = RESERVE_C + ceil_log3(r * r)
        small_valid.append(r - reserve >= 1)

    return {
        "exact_arity_interval": [MIN_R, MAX_R],
        "arity_count": MAX_R - MIN_R + 1,
        "selected_rows": selected,
        "maximum_nonbinary_normalized": {
            "r": maximum[2],
            "decimal": ratio_decimal(maximum[0], maximum[1]),
        },
        "power_or_reserve_jump_checks": jump_checks,
        "analytic_inequality_rows": analytic_rows,
        "binary_depth_below_r_from": binary_below_r_from,
        "binary_tail_polynomial": tail_values,
        "binary_tail_polynomial_increment_at_30": tail_increment_at_30,
        "analytic_size_base_witnesses": analytic_size_witnesses,
        "mutations": {
            "sequential_q_times_w": {
                "r": sequential_r,
                "q": q_prefix,
                "w": w_prefix,
                "cost_times_r_gt_100_times_3r": True,
            },
            "single_log_reserve": {
                "r": single_r,
                "M": single_m,
                "local_alone_gt_62_times_3r_over_r": True,
            },
            "ceil_power_rounding": ceiling_witness,
            "decoder_per_local_table_at_r93_extra_nodes": repeated_decoder_extra,
        },
        "small_arity_scope": {
            "r_1_through_63_with_nonempty_budget": sum(small_valid),
            "giant_schedule_claimed": False,
            "fallback_is_a_named_frozen_compiler_premise": True,
        },
    }


def physical_binary_control_checks() -> dict[str, object]:
    # Logical relative bit p is physically x0 for p=0 and u(x0) for p=1.
    # Check orientation, dependence, and simultaneous complement equivariance.
    rows = 0
    for orientation, logical_bit in itertools.product((0, 1), repeat=2):
        physical = orientation if logical_bit == 0 else u(orientation)
        require(physical == (orientation ^ logical_bit), "relative binary control realization failed")
        rows += 1
    equivariance_rows = 0
    for x, y, z in itertools.product((0, 1), repeat=3):
        require(u(d(x, y, z)) == d(u(x), u(y), u(z)), "binary complement equivariance failed")
        equivariance_rows += 1
    # A relative logical 0 has two different physical wires.  This explicitly
    # refutes any payload-independent interpretation of the binary branch.
    require((0, 1) == tuple(orientation for orientation in (0, 1)), "binary payload witness drift")
    return {
        "relative_control_rows": rows,
        "complement_equivariance_rows": equivariance_rows,
        "logical_zero_physical_values_by_orientation": [0, 1],
        "qualification": "logical programs are address-only; physical wires depend on payload orientation x0",
    }


def freeze_subject(base: Path) -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in SUBJECT_HASHES.items():
        path = base / relative
        require(path.is_file(), f"missing frozen subject: {relative}")
        digest = sha256_bytes(path.read_bytes())
        require(digest == expected, f"frozen subject hash drift: {relative}")
        observed[relative] = digest
    return observed


def find_tournament_root(script_path: Path) -> Path:
    # .../semantic-router-frontier/audits/program_vector/audit_program_vector.py
    return script_path.resolve().parents[2]


def run_audit(script_path: Path) -> dict[str, object]:
    tournament = find_tournament_root(script_path)
    frozen = freeze_subject(tournament)
    semantics = semantic_checks()
    dag = dag_checks()
    routers = router_and_padding_checks()
    compiler = compiler_checks()
    binary = physical_binary_control_checks()
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "EXACT_PROGRAM_VECTOR_PASS__CONDITIONAL_COMPILER_LEDGER_PASS",
        "frozen_subject": frozen,
        "semantics": semantics,
        "shared_dag": dag,
        "router_and_padding": routers,
        "compiler": compiler,
        "binary_relative_branch": binary,
        "scope": {
            "exact": [
                "E/G first-mismatch law and recursive P/N program equivalence",
                "associative guarded segment composition",
                "original-signature A=2 formulas",
                "same-DAG 7q size and logarithmic control depth",
                "projection, complement, constants, and duplicate-last padding",
                "integer compiler ledger on the stated interval",
            ],
            "conditional": [
                "end-to-end compiler composition uses frozen anchor, decoder, glue, selector-library, and finite-tail premises",
                "binary branch size/depth ledger uses the frozen complement-relative schedule",
            ],
            "not_claimed": [
                "ordinary formula size",
                "bounded fanout",
                "nullary constants in the original signature",
                "novelty or prior-art clearance",
                "patent freedom to operate or copyright clearance",
                "unsigned Tau license rights",
                "Lean verification, practicality, publication readiness, or optimal constants",
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
    result = run_audit(script_path)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(result["semantic_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

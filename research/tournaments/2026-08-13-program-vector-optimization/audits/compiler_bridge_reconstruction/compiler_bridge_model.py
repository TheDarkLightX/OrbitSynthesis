"""Fresh-room explicit bridge from the order-pair vector to the fixed-Q compiler.

This module deliberately does not import the author/compiler implementation. It
constructs one hash-consed original-signature DAG for bounded selector tables and
provides the exact integer ledgers used by the generic proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import ceil, isqrt
from typing import Iterable, Mapping, Sequence

Q = (0, 1, 2)
Word = tuple[int, ...]


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    return (1, 0, 1)[x]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@dataclass(frozen=True)
class Node:
    op: str
    args: tuple[int, ...]


class DAG:
    """Hash-consed DAG over variables, unary ``u``, and discriminator ``d``."""

    def __init__(self, arity: int) -> None:
        require(arity >= 1, "positive arity required")
        self.arity = arity
        self.nodes: list[Node] = []
        self.index: dict[Node, int] = {}
        self.inputs: dict[tuple[object, ...], int] = {}
        self.variables = tuple(self.var(("x", i)) for i in range(arity))

    def var(self, key: tuple[object, ...]) -> int:
        if key not in self.inputs:
            self.inputs[key] = -(len(self.inputs) + 1)
        return self.inputs[key]

    def intern(self, op: str, *args: int) -> int:
        node = Node(op, tuple(args))
        old = self.index.get(node)
        if old is not None:
            return old
        ref = len(self.nodes)
        self.nodes.append(node)
        self.index[node] = ref
        return ref

    def unary(self, child: int) -> int:
        return self.intern("u", child)

    def disc(self, left: int, middle: int, right: int) -> int:
        return self.intern("d", left, middle, right)

    def evaluate(
        self,
        root: int,
        arguments: Sequence[int],
        *,
        extra_inputs: Mapping[int, int] | None = None,
    ) -> int:
        require(len(arguments) == self.arity, "argument arity mismatch")
        input_values = {
            self.variables[index]: value for index, value in enumerate(arguments)
        }
        if extra_inputs is not None:
            input_values.update(extra_inputs)
        memo: dict[int, int] = {}

        def go(ref: int) -> int:
            if ref < 0:
                return input_values[ref]
            old = memo.get(ref)
            if old is not None:
                return old
            node = self.nodes[ref]
            if node.op == "u":
                value = u(go(node.args[0]))
            elif node.op == "d":
                value = d(*(go(arg) for arg in node.args))
            else:  # pragma: no cover
                raise AssertionError(node.op)
            memo[ref] = value
            return value

        return go(root)

    @lru_cache(maxsize=None)
    def depth(self, ref: int) -> int:
        if ref < 0:
            return 0
        return 1 + max(self.depth(arg) for arg in self.nodes[ref].args)

    def reachable(self, roots: Iterable[int]) -> set[int]:
        seen: set[int] = set()

        def visit(ref: int) -> None:
            if ref < 0 or ref in seen:
                return
            seen.add(ref)
            for arg in self.nodes[ref].args:
                visit(arg)

        for root in roots:
            visit(root)
        return seen


def normal_selector(dag: DAG, x: int, y: int, equal: int, different: int) -> int:
    """Return ``equal`` iff ``x=y`` using three discriminator nodes."""

    return dag.disc(
        dag.disc(x, y, equal),
        dag.disc(x, y, different),
        different,
    )


def absorbing_two(dag: DAG, left: int, right: int) -> int:
    """Return 2 iff either argument is 2; otherwise return ``left``."""

    left_u = dag.unary(left)
    left_u2 = dag.unary(left_u)
    return dag.disc(left, left_u2, dag.disc(right, left_u, left))


def balanced_anchor(dag: DAG, roots: tuple[int, ...]) -> int:
    require(bool(roots), "nonempty anchor fold required")
    if len(roots) == 1:
        return roots[0]
    split = len(roots) // 2
    return absorbing_two(
        dag,
        balanced_anchor(dag, roots[:split]),
        balanced_anchor(dag, roots[split:]),
    )


def parity(word: Word) -> int:
    return sum(digit == 1 for digit in word) & 1


def build_summary_package(
    dag: DAG,
    variables: tuple[int, ...],
    *,
    anchor: int,
    zero: int,
) -> dict[Word, tuple[int, int]]:
    """All order-pair summaries ``(L,G)`` for the given target variables."""

    width = len(variables)
    require(width >= 1, "positive vector width required")
    if width == 1:
        x = variables[0]
        not_one = dag.unary(x)
        gain_two = dag.unary(not_one)
        loss_two = dag.disc(zero, x, not_one)
        loss_zero = dag.disc(x, anchor, not_one)
        return {
            (0,): (loss_zero, zero),
            (1,): (not_one, zero),
            (2,): (loss_two, gain_two),
        }

    split = width // 2
    left = build_summary_package(
        dag, variables[:split], anchor=anchor, zero=zero
    )
    right = build_summary_package(
        dag, variables[split:], anchor=anchor, zero=zero
    )
    outputs: dict[Word, tuple[int, int]] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (right_loss, right_gain) in right.items():
            loss = dag.disc(left_loss, left_gain, right_loss)
            gain = (
                left_gain
                if right_gain == zero
                else dag.disc(left_gain, left_loss, right_gain)
            )
            outputs[left_word + right_word] = (loss, gain)
    return outputs


def build_partial_upper(
    dag: DAG,
    package: Mapping[Word, tuple[int, int]],
    variables: tuple[int, ...],
    *,
    anchor: int,
    zero: int,
) -> dict[Word, int]:
    """Build ``H=not L`` for words ending 0 or 2; ending 1 reuses sibling G."""

    width = len(variables)
    if width == 1:
        return {
            (0,): package[(2,)][0],
            (2,): package[(0,)][0],
        }

    split = width // 2
    left_variables = variables[:split]
    right_variables = variables[split:]
    left = build_summary_package(
        dag, left_variables, anchor=anchor, zero=zero
    )
    right = build_summary_package(
        dag, right_variables, anchor=anchor, zero=zero
    )
    right_upper = build_partial_upper(
        dag,
        right,
        right_variables,
        anchor=anchor,
        zero=zero,
    )

    def upper(word: Word) -> int:
        if word[-1] == 1:
            return right[word[:-1] + (2,)][1]
        return right_upper[word]

    outputs: dict[Word, int] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word in right:
            if right_word[-1] == 1:
                continue
            outputs[left_word + right_word] = dag.disc(
                left_gain, left_loss, upper(right_word)
            )
    return outputs


def build_order_pair_vector(
    dag: DAG,
    variables: tuple[int, ...],
    *,
    anchor: int,
    zero: int,
    root_negative: bool = False,
) -> dict[Word, tuple[int, int]]:
    """Exact sign-aware ordered pair for every physical branch word."""

    width = len(variables)
    require(width >= 1, "positive vector width required")
    package = build_summary_package(dag, variables, anchor=anchor, zero=zero)

    if width == 1:
        upper = build_partial_upper(
            dag, package, variables, anchor=anchor, zero=zero
        )
        outputs: dict[Word, tuple[int, int]] = {}
        for physical, (loss, gain) in package.items():
            negative = root_negative ^ bool(parity(physical))
            high = (
                package[physical[:-1] + (2,)][1]
                if physical[-1] == 1
                else upper[physical]
            )
            outputs[physical] = (gain, high) if negative else (loss, gain)
        return outputs

    split = width // 2
    left_variables = variables[:split]
    right_variables = variables[split:]
    left = build_summary_package(
        dag, left_variables, anchor=anchor, zero=zero
    )
    right = build_summary_package(
        dag, right_variables, anchor=anchor, zero=zero
    )
    right_upper = build_partial_upper(
        dag,
        right,
        right_variables,
        anchor=anchor,
        zero=zero,
    )

    root_gain: dict[Word, int] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (_, right_gain) in right.items():
            root_gain[left_word + right_word] = (
                left_gain
                if right_gain == zero
                else dag.disc(left_gain, left_loss, right_gain)
            )

    def upper(word: Word) -> int:
        if word[-1] == 1:
            return right[word[:-1] + (2,)][1]
        return right_upper[word]

    outputs: dict[Word, tuple[int, int]] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (right_loss, _) in right.items():
            physical = left_word + right_word
            gain = root_gain[physical]
            negative = root_negative ^ bool(parity(physical))
            if not negative:
                outputs[physical] = (
                    dag.disc(left_loss, left_gain, right_loss),
                    gain,
                )
            elif physical[-1] == 1:
                outputs[physical] = (
                    gain,
                    root_gain[physical[:-1] + (2,)],
                )
            else:
                outputs[physical] = (
                    gain,
                    dag.disc(left_gain, left_loss, upper(right_word)),
                )
    return outputs


def build_signed_router(
    dag: DAG,
    width: int,
    *,
    root_negative: bool,
    branches: Mapping[Word, int],
    controls: Mapping[tuple[int, Word], int],
) -> int:
    """Frozen strong signed router skeleton with supplied payload/control roots."""

    require(set(branches) == set(product(Q, repeat=width)), "branch domain drift")
    require(
        set(controls)
        == {
            (slot, word)
            for word in product(Q, repeat=width)
            for slot in (0, 1)
        },
        "control domain drift",
    )

    def recurse(
        current_width: int,
        negative: bool,
        local_branches: Mapping[Word, int],
        local_controls: Mapping[tuple[int, Word], int],
    ) -> int:
        if current_width == 0:
            payload = local_branches[()]
            first = local_controls[(0, ())]
            second = local_controls[(1, ())]
            return (
                dag.disc(first, payload, second)
                if negative
                else dag.disc(payload, first, second)
            )

        children = []
        for digit in Q:
            child_branches = {
                word[1:]: root
                for word, root in local_branches.items()
                if word[0] == digit
            }
            child_controls = {
                (slot, word[1:]): root
                for (slot, word), root in local_controls.items()
                if word[0] == digit
            }
            children.append(
                recurse(
                    current_width - 1,
                    negative ^ (digit == 1),
                    child_branches,
                    child_controls,
                )
            )
        return dag.disc(children[0], children[1], children[2])

    return recurse(width, root_negative, branches, controls)


def encode_bits(value: int) -> tuple[int, int]:
    return ((0, 0), (0, 1), (1, 0))[value]


def complement(point: Word) -> Word:
    require(all(value in (0, 1) for value in point), "binary point required")
    return tuple(1 - value for value in point)


def validate_selector(arity: int, selector: Mapping[Word, int]) -> None:
    points = set(product(Q, repeat=arity))
    require(set(selector) == points, "selector table is not total")
    require(
        all(0 <= index < arity for index in selector.values()),
        "selector index out of range",
    )
    for point in product((0, 1), repeat=arity):
        require(
            selector[point] == selector[complement(point)],
            "binary selector is not complement-invariant",
        )


def build_binary_reference(
    dag: DAG,
    selector: Mapping[Word, int],
) -> int:
    """Bounded semantic reference; the generic theorem uses the signed binary lane."""

    def recurse(position: int, representative: list[int]) -> int:
        if position == dag.arity:
            return dag.variables[selector[tuple(representative)]]
        return normal_selector(
            dag,
            dag.variables[position],
            dag.variables[0],
            recurse(position + 1, representative + [0]),
            recurse(position + 1, representative + [1]),
        )

    return recurse(1, [0])


@dataclass(frozen=True)
class IntegratedBuild:
    root: int
    anchor: int
    binary: int
    nonbinary: int
    local_width: int
    local_library_size: int


def compile_integrated_small(
    arity: int,
    selector: Mapping[Word, int],
    *,
    local_width: int = 1,
) -> tuple[DAG, IntegratedBuild]:
    """Materialize one complete compiler DAG for bounded differential testing."""

    validate_selector(arity, selector)
    require(1 <= local_width < arity, "nontrivial local/prefix split required")

    dag = DAG(arity)
    anchor = balanced_anchor(dag, dag.variables)
    one = dag.unary(anchor)
    zero = dag.unary(one)

    local_variables = dag.variables[:local_width]
    prefix_variables = dag.variables[local_width:]
    local_words = tuple(product(Q, repeat=local_width))
    prefix_words = tuple(product(Q, repeat=arity - local_width))

    local_pairs = build_order_pair_vector(
        dag,
        local_variables,
        anchor=anchor,
        zero=zero,
        root_negative=False,
    )
    local_controls = {
        (slot, physical): pair[slot]
        for physical, pair in local_pairs.items()
        for slot in (0, 1)
    }

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

    prefix_pairs = build_order_pair_vector(
        dag,
        prefix_variables,
        anchor=anchor,
        zero=zero,
        root_negative=False,
    )
    prefix_controls = {
        (slot, physical): pair[slot]
        for physical, pair in prefix_pairs.items()
        for slot in (0, 1)
    }

    high_branches: dict[Word, int] = {}
    low_branches: dict[Word, int] = {}
    for prefix in prefix_words:
        local_table = tuple(
            (local + prefix)[selector[local + prefix]] for local in local_words
        )
        high_root, low_root = library[local_table]
        high_branches[prefix] = high_root
        low_branches[prefix] = low_root

    high = build_signed_router(
        dag,
        arity - local_width,
        root_negative=False,
        branches=high_branches,
        controls=prefix_controls,
    )
    low = build_signed_router(
        dag,
        arity - local_width,
        root_negative=False,
        branches=low_branches,
        controls=prefix_controls,
    )
    nonbinary = dag.disc(dag.disc(high, one, anchor), zero, low)

    binary = build_binary_reference(dag, selector)
    root = dag.disc(
        dag.disc(zero, anchor, binary),
        dag.disc(zero, anchor, nonbinary),
        nonbinary,
    )
    return dag, IntegratedBuild(
        root=root,
        anchor=anchor,
        binary=binary,
        nonbinary=nonbinary,
        local_width=local_width,
        local_library_size=len(library),
    )


def ceil_log3(value: int) -> int:
    exponent = 0
    power = 1
    while power < value:
        power *= 3
        exponent += 1
    return exponent


def floor_log3(value: int) -> int:
    require(value >= 1, "positive logarithm argument required")
    exponent = 0
    power = 1
    while 3 * power <= value:
        power *= 3
        exponent += 1
    return exponent


def clog2(value: int) -> int:
    return 0 if value <= 1 else (value - 1).bit_length()


@lru_cache(maxsize=None)
def summary_nodes(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 4
    left = width // 2
    right = (width + 1) // 2
    return (
        summary_nodes(left)
        + summary_nodes(right)
        + 3**width
        + 3**left * ((3**right - 1) // 2)
    )


@lru_cache(maxsize=None)
def partial_upper_nodes(width: int) -> int:
    if width <= 1:
        return 0
    return partial_upper_nodes((width + 1) // 2) + 2 * 3 ** (width - 1)


def reusable_count(width: int, root_negative: bool) -> int:
    require(width >= 1, "positive width required")
    even = (3 ** (width - 1) + 1) // 2
    odd = (3 ** (width - 1) - 1) // 2
    return odd if root_negative else even


def order_pair_vector_nodes(width: int, root_negative: bool = False) -> int:
    if width == 0:
        return 2
    if width == 1:
        return 6
    return (
        2
        + summary_nodes(width)
        + partial_upper_nodes((width + 1) // 2)
        - reusable_count(width, root_negative)
    )


def compiler_parameters(arity: int) -> tuple[int, int, int, int, int, int]:
    require(arity >= 64, "large-arity ledger starts at 64")
    ell = ceil_log3(arity * arity)
    reserve = 4 + ell
    headroom = arity - reserve
    local_width = floor_log3(headroom)
    local_assignments = 3**local_width
    prefix_width = arity - local_width
    prefix_assignments = 3**prefix_width
    return (
        ell,
        headroom,
        local_assignments,
        local_width,
        prefix_assignments,
        prefix_width,
    )


def nonbinary_node_upper(arity: int) -> int:
    _, _, local, local_width, prefix, prefix_width = compiler_parameters(arity)
    return (
        (3 * local - 1) * 3**local
        + order_pair_vector_nodes(local_width, False)
        + (3 * prefix - 1)
        + order_pair_vector_nodes(prefix_width, False)
        + 4 * arity
        + 3
    )


def binary_chunk_width(arity: int) -> int:
    """Explicit finite-depth choice; square-root schedule from arity 339 on."""

    if arity >= 339:
        return isqrt(arity)
    candidates = range(1, 33)
    return min(
        candidates,
        key=lambda width: (binary_depth_for_width(arity, width), width),
    )


def binary_depth_for_width(arity: int, width: int) -> int:
    address_bits = (3**width).bit_length() - 1
    require(address_bits >= 1, "positive binary chunk capacity required")
    levels = ceil((arity - 1) / address_bits)
    return (
        (width + 1) * levels
        + 2 * address_bits
        + 3 * clog2(arity)
        + 8
    )


def binary_depth_upper(arity: int) -> int:
    return binary_depth_for_width(arity, binary_chunk_width(arity))


def binary_node_upper(arity: int) -> int:
    width = binary_chunk_width(arity)
    router_capacity = 3**width
    padded_capacity = 2 ** (router_capacity.bit_length() - 1)
    binary_rows = 2 ** (arity - 1)
    return (
        6 * (binary_rows + padded_capacity)
        + 6 * arity * router_capacity * router_capacity
        + 4 * arity
        + 10
    )


def total_node_upper(arity: int) -> int:
    return nonbinary_node_upper(arity) + binary_node_upper(arity)


def nonbinary_depth_upper(arity: int) -> int:
    _, _, _, local_width, _, prefix_width = compiler_parameters(arity)
    anchor_depth = 3 * clog2(arity)
    local_controls = anchor_depth + 3 + clog2(local_width)
    local_output = local_controls + local_width + 1
    prefix_controls = anchor_depth + 3 + clog2(prefix_width)
    prefix_output = max(local_output, prefix_controls) + prefix_width + 1
    return prefix_output + 4  # one decoder (2) and final glue (2)


def total_depth_upper(arity: int) -> int:
    return max(nonbinary_depth_upper(arity), binary_depth_upper(arity) + 2)

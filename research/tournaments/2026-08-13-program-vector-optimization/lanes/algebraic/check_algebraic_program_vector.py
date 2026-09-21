#!/usr/bin/env python3
"""Independent checker for algebraic signed-router program vectors.

This file imports no Orbit implementation.  It constructs original-signature
``d/u`` DAGs, evaluates every generated control on bounded complete domains,
replays full routers with a direct ROBDD, and checks the all-width arithmetic
used by REPORT.md.  Search results never own acceptance: explicit semantic
requirements below do.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from functools import cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
STATE = (
    ROOT
    / "research/tournaments/2026-08-13-program-vector-optimization/STATE.md"
)
STATE_SHA256 = "6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6"

EQUAL = 0
LOSS = 1
GAIN = 2


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(x: int, y: int, z: int) -> int:
    require(x in (0, 1, 2) and y in (0, 1, 2) and z in (0, 1, 2), "d left Q")
    return z if x == y else x


def u(x: int) -> int:
    require(x in (0, 1, 2), "u left Q")
    return (1, 0, 1)[x]


def words(width: int) -> tuple[tuple[int, ...], ...]:
    require(width >= 0, "negative width")
    return tuple(itertools.product((0, 1, 2), repeat=width))


def first_mode(target: tuple[int, ...], physical: tuple[int, ...]) -> int:
    require(len(target) == len(physical), "word-width mismatch")
    for target_digit, physical_digit in zip(target, physical, strict=True):
        if target_digit != physical_digit:
            return GAIN if (target_digit, physical_digit) == (1, 2) else LOSS
    return EQUAL


def mode_product(left: int, right: int) -> int:
    require(left in (EQUAL, LOSS, GAIN) and right in (EQUAL, LOSS, GAIN), "bad mode")
    return right if left == EQUAL else left


def positive_code(mode: int) -> tuple[int, int]:
    return {
        EQUAL: (0, 0),
        LOSS: (1, 0),
        GAIN: (0, 1),
    }[mode]


def negative_code(mode: int) -> tuple[int, int]:
    return {
        EQUAL: (0, 1),
        LOSS: (0, 0),
        GAIN: (1, 1),
    }[mode]


def cell_sign(root_sign: int, physical: tuple[int, ...]) -> int:
    require(root_sign in (0, 1), "bad root sign")
    return root_sign ^ (sum(digit == 1 for digit in physical) & 1)


def expected_pair(
    root_sign: int,
    physical: tuple[int, ...],
    target: tuple[int, ...] | None,
    constant: int | None = None,
) -> tuple[int, int]:
    sign = cell_sign(root_sign, physical)
    if constant is not None:
        require(constant in (0, 1), "bad constant")
        return (1 - constant, constant) if sign == 0 else (constant, constant)
    require(target is not None, "projection target missing")
    mode = first_mode(target, physical)
    return positive_code(mode) if sign == 0 else negative_code(mode)


class DAG:
    """Hash-consed original-signature DAG with named variable terminals."""

    def __init__(self) -> None:
        self.records: list[tuple[object, ...]] = []
        self.depths: list[int] = []
        self.unique: dict[tuple[object, ...], int] = {}

    def _intern(self, record: tuple[object, ...], depth: int) -> int:
        found = self.unique.get(record)
        if found is not None:
            return found
        node = len(self.records)
        self.records.append(record)
        self.depths.append(depth)
        self.unique[record] = node
        return node

    def terminal(self, name: str) -> int:
        return self._intern(("terminal", name), 0)

    def unary(self, child: int) -> int:
        return self._intern(("u", child), self.depths[child] + 1)

    def discriminator(self, left: int, middle: int, right: int) -> int:
        return self._intern(
            ("d", left, middle, right),
            max(self.depths[left], self.depths[middle], self.depths[right]) + 1,
        )

    @property
    def operation_count(self) -> int:
        return sum(record[0] != "terminal" for record in self.records)

    def evaluate(self, roots: tuple[int, ...], environment: dict[str, int]) -> tuple[int, ...]:
        memo: dict[int, int] = {}

        def visit(node: int) -> int:
            if node in memo:
                return memo[node]
            record = self.records[node]
            if record[0] == "terminal":
                name = str(record[1])
                require(name in environment, f"missing terminal {name}")
                value = environment[name]
            elif record[0] == "u":
                value = u(visit(int(record[1])))
            else:
                require(record[0] == "d", "unknown record")
                value = d(
                    visit(int(record[1])),
                    visit(int(record[2])),
                    visit(int(record[3])),
                )
            memo[node] = value
            return value

        return tuple(visit(root) for root in roots)

    def dependencies(self, roots: tuple[int, ...]) -> frozenset[str]:
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

        result: frozenset[str] = frozenset()
        for root in roots:
            result |= visit(root)
        return result


def names(dag: DAG) -> tuple[int, int, int]:
    two = dag.terminal("A")
    one = dag.unary(two)
    zero = dag.unary(one)
    return zero, one, two


def pair_digit_states(
    dag: DAG, digit: int, zero: int, one: int, two: int
) -> dict[tuple[int, ...], tuple[int, int]]:
    # The four nonconstant Boolean functions are two complement pairs.
    loss_for_zero = dag.discriminator(digit, two, one)  # [0,1,1]
    loss_for_one = dag.unary(digit)                     # [1,0,1]
    loss_for_two = dag.unary(loss_for_zero)             # [1,0,0]
    gain_for_two = dag.unary(loss_for_one)              # [0,1,0]
    return {
        (0,): (loss_for_zero, zero),
        (1,): (loss_for_one, zero),
        (2,): (loss_for_two, gain_for_two),
    }


def balanced_pair_states(
    dag: DAG,
    digits: tuple[int, ...],
    zero: int,
    one: int,
    two: int,
) -> dict[tuple[int, ...], tuple[int, int]]:
    if not digits:
        return {(): (zero, zero)}
    if len(digits) == 1:
        return pair_digit_states(dag, digits[0], zero, one, two)
    split = len(digits) // 2
    left = balanced_pair_states(dag, digits[:split], zero, one, two)
    right = balanced_pair_states(dag, digits[split:], zero, one, two)
    result: dict[tuple[int, ...], tuple[int, int]] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (right_loss, right_gain) in right.items():
            # For one-hot (loss,gain), equality is (0,0).  If the left pair
            # is equal, d returns the right coordinate; otherwise it returns
            # the left absorbing coordinate.
            loss = dag.discriminator(left_loss, left_gain, right_loss)
            gain = dag.discriminator(left_gain, left_loss, right_gain)
            result[left_word + right_word] = (loss, gain)
    return result


def balanced_shared_rail_states(
    dag: DAG,
    digits: tuple[int, ...],
    zero: int,
    one: int,
    two: int,
) -> dict[tuple[int, ...], tuple[int, int]]:
    """Gain/loss states with the identically-zero right gain rail elided.

    The longer half is put on the left.  This is semantically immaterial, but
    it maximizes the number of omitted right-zero gain merges at odd widths.
    """
    if not digits:
        return {(): (zero, zero)}
    if len(digits) == 1:
        return pair_digit_states(dag, digits[0], zero, one, two)
    split = (len(digits) + 1) // 2
    left = balanced_shared_rail_states(dag, digits[:split], zero, one, two)
    right = balanced_shared_rail_states(dag, digits[split:], zero, one, two)
    result: dict[tuple[int, ...], tuple[int, int]] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (right_loss, right_gain) in right.items():
            loss = dag.discriminator(left_loss, left_gain, right_loss)
            # For disjoint Boolean rails, d(G,L,0)=G.  Moreover, different
            # physical right words can point to the same gain root; structural
            # hash-consing then shares the nonzero merge too.
            gain = (
                left_gain
                if right_gain == zero
                else dag.discriminator(left_gain, left_loss, right_gain)
            )
            result[left_word + right_word] = (loss, gain)
    return result


def balanced_extended_rail_states(
    dag: DAG,
    digits: tuple[int, ...],
    zero: int,
    one: int,
    two: int,
) -> dict[tuple[int, ...], tuple[int, int, int]]:
    """Build (loss,gain,not-loss), recursively reusing sibling gain rails."""
    require(digits, "empty extended rail block")
    if len(digits) == 1:
        pair = pair_digit_states(dag, digits[0], zero, one, two)
        loss_zero, _ = pair[(0,)]
        loss_one, _ = pair[(1,)]
        loss_two, gain_two = pair[(2,)]
        return {
            (0,): (loss_zero, zero, loss_two),
            (1,): (loss_one, zero, gain_two),
            (2,): (loss_two, gain_two, loss_zero),
        }
    split = (len(digits) + 1) // 2
    left = balanced_shared_rail_states(dag, digits[:split], zero, one, two)
    right = balanced_extended_rail_states(
        dag, digits[split:], zero, one, two
    )
    partial: dict[
        tuple[int, ...], tuple[int, int, int, int, int]
    ] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (right_loss, right_gain, right_not_loss) in right.items():
            loss = dag.discriminator(left_loss, left_gain, right_loss)
            gain = (
                left_gain
                if right_gain == zero
                else dag.discriminator(left_gain, left_loss, right_gain)
            )
            partial[left_word + right_word] = (
                loss,
                gain,
                left_loss,
                left_gain,
                right_not_loss,
            )
    result: dict[tuple[int, ...], tuple[int, int, int]] = {}
    for physical, (loss, gain, left_loss, left_gain, right_not_loss) in partial.items():
        if physical[-1] == 1:
            not_loss = partial[physical[:-1] + (2,)][1]
        else:
            not_loss = dag.discriminator(
                left_gain, left_loss, right_not_loss
            )
        result[physical] = (loss, gain, not_loss)
    return result


def finish_pair_vector(
    dag: DAG,
    states: dict[tuple[int, ...], tuple[int, int]],
    root_sign: int,
) -> dict[tuple[int, ...], tuple[int, int]]:
    outputs: dict[tuple[int, ...], tuple[int, int]] = {}
    for physical, (loss, gain) in states.items():
        outputs[physical] = (
            (loss, gain)
            if cell_sign(root_sign, physical) == 0
            else (gain, dag.unary(loss))
        )
    return outputs


def build_pair_vector(
    width: int,
    root_sign: int,
    constant: int | None = None,
) -> tuple[DAG, dict[tuple[int, ...], tuple[int, int]], tuple[int, ...]]:
    require(width >= 0 and root_sign in (0, 1), "bad vector request")
    dag = DAG()
    zero, one, two = names(dag)
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    outputs: dict[tuple[int, ...], tuple[int, int]] = {}
    if constant is not None:
        require(constant in (0, 1), "bad vector constant")
        for physical in words(width):
            if cell_sign(root_sign, physical) == 0:
                outputs[physical] = (one, zero) if constant == 0 else (zero, one)
            else:
                outputs[physical] = (zero, zero) if constant == 0 else (one, one)
        return dag, outputs, digits

    # The empty address has one equality cell and needs no state machinery.
    if width == 0:
        outputs[()] = (zero, zero) if root_sign == 0 else (zero, one)
        return dag, outputs, digits

    states = balanced_pair_states(dag, digits, zero, one, two)
    outputs = finish_pair_vector(dag, states, root_sign)
    return dag, outputs, digits


def build_shared_rail_vector(
    width: int,
    root_sign: int,
    constant: int | None = None,
) -> tuple[DAG, dict[tuple[int, ...], tuple[int, int]], tuple[int, ...]]:
    require(width >= 0 and root_sign in (0, 1), "bad rail-vector request")
    dag = DAG()
    zero, one, two = names(dag)
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    if constant is not None:
        require(constant in (0, 1), "bad rail-vector constant")
        outputs: dict[tuple[int, ...], tuple[int, int]] = {}
        for physical in words(width):
            if cell_sign(root_sign, physical) == 0:
                outputs[physical] = (one, zero) if constant == 0 else (zero, one)
            else:
                outputs[physical] = (zero, zero) if constant == 0 else (one, one)
        return dag, outputs, digits
    if width == 0:
        outputs = {(): (zero, zero) if root_sign == 0 else (zero, one)}
        return dag, outputs, digits
    states = balanced_shared_rail_states(dag, digits, zero, one, two)
    return dag, finish_pair_vector(dag, states, root_sign), digits


def build_terminal_mixed_vector(
    width: int,
    root_sign: int,
    constant: int | None = None,
) -> tuple[DAG, dict[tuple[int, ...], tuple[int, int]], tuple[int, ...]]:
    """Build only the sign-selected loss/not-loss rail at the top merge."""
    require(width >= 0 and root_sign in (0, 1), "bad terminal-mixed request")
    dag = DAG()
    zero, one, two = names(dag)
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    if constant is not None:
        require(constant in (0, 1), "bad terminal-mixed constant")
        outputs: dict[tuple[int, ...], tuple[int, int]] = {}
        for physical in words(width):
            if cell_sign(root_sign, physical) == 0:
                outputs[physical] = (one, zero) if constant == 0 else (zero, one)
            else:
                outputs[physical] = (zero, zero) if constant == 0 else (one, one)
        return dag, outputs, digits
    if width == 0:
        return (
            dag,
            {(): (zero, zero) if root_sign == 0 else (zero, one)},
            digits,
        )
    if width == 1:
        digit = digits[0]
        loss_zero = dag.discriminator(digit, two, one)
        loss_two = dag.discriminator(zero, digit, one)
        gain_two = dag.discriminator(digit, two, zero)
        if root_sign == 0:
            outputs = {
                (0,): (loss_zero, zero),
                (1,): (zero, gain_two),
                (2,): (loss_two, gain_two),
            }
        else:
            loss_one = dag.unary(digit)
            outputs = {
                (0,): (zero, loss_two),
                (1,): (loss_one, zero),
                (2,): (gain_two, loss_zero),
            }
        return dag, outputs, digits

    split = (width + 1) // 2
    left = balanced_shared_rail_states(dag, digits[:split], zero, one, two)
    right = balanced_shared_rail_states(dag, digits[split:], zero, one, two)

    # not L_(a1) = G_(a2).  Reuse that rail explicitly; for the remaining
    # right words a single u node gives not-loss.
    right_not_loss: dict[tuple[int, ...], int] = {}
    for physical, (loss, _gain) in right.items():
        if physical[-1] == 1:
            alternate = physical[:-1] + (2,)
            right_not_loss[physical] = right[alternate][1]
        else:
            right_not_loss[physical] = dag.unary(loss)

    outputs = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (right_loss, right_gain) in right.items():
            physical = left_word + right_word
            gain = (
                left_gain
                if right_gain == zero
                else dag.discriminator(left_gain, left_loss, right_gain)
            )
            if cell_sign(root_sign, physical) == 0:
                mixed = dag.discriminator(left_loss, left_gain, right_loss)
                outputs[physical] = (mixed, gain)
            else:
                mixed = dag.discriminator(
                    left_gain, left_loss, right_not_loss[right_word]
                )
                outputs[physical] = (gain, mixed)
    return dag, outputs, digits


def build_recursive_terminal_vector(
    width: int,
    root_sign: int,
    constant: int | None = None,
) -> tuple[DAG, dict[tuple[int, ...], tuple[int, int]], tuple[int, ...]]:
    """Terminal mixed rails with recursively co-produced not-loss suffixes."""
    require(width >= 0 and root_sign in (0, 1), "bad recursive-terminal request")
    if width <= 1 or constant is not None:
        return build_terminal_mixed_vector(width, root_sign, constant)

    dag = DAG()
    zero, one, two = names(dag)
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    split = (width + 1) // 2
    left = balanced_shared_rail_states(dag, digits[:split], zero, one, two)
    right = balanced_extended_rail_states(dag, digits[split:], zero, one, two)

    gains: dict[tuple[int, ...], int] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (_right_loss, right_gain, _right_not_loss) in right.items():
            gains[left_word + right_word] = (
                left_gain
                if right_gain == zero
                else dag.discriminator(left_gain, left_loss, right_gain)
            )

    outputs: dict[tuple[int, ...], tuple[int, int]] = {}
    for left_word, (left_loss, left_gain) in left.items():
        for right_word, (right_loss, _right_gain, right_not_loss) in right.items():
            physical = left_word + right_word
            gain = gains[physical]
            if cell_sign(root_sign, physical) == 0:
                mixed = dag.discriminator(left_loss, left_gain, right_loss)
                outputs[physical] = (mixed, gain)
            elif physical[-1] == 1:
                mixed = gains[physical[:-1] + (2,)]
                outputs[physical] = (gain, mixed)
            else:
                mixed = dag.discriminator(left_gain, left_loss, right_not_loss)
                outputs[physical] = (gain, mixed)
    return dag, outputs, digits


def ternary_digit_states(
    dag: DAG, digit: int, zero: int, one: int, two: int
) -> dict[tuple[int, ...], int]:
    del one
    state_zero = dag.discriminator(zero, digit, two)  # [E,Z,Z] = [2,0,0]
    not_digit = dag.unary(digit)
    state_one = dag.discriminator(zero, not_digit, two)  # [Z,E,Z]
    return {(0,): state_zero, (1,): state_one, (2,): digit}


def balanced_ternary_states(
    dag: DAG,
    digits: tuple[int, ...],
    zero: int,
    one: int,
    two: int,
) -> dict[tuple[int, ...], int]:
    if not digits:
        return {(): two}
    if len(digits) == 1:
        return ternary_digit_states(dag, digits[0], zero, one, two)
    split = len(digits) // 2
    left = balanced_ternary_states(dag, digits[:split], zero, one, two)
    right = balanced_ternary_states(dag, digits[split:], zero, one, two)
    return {
        left_word + right_word: dag.discriminator(left_state, two, right_state)
        for left_word, left_state in left.items()
        for right_word, right_state in right.items()
    }


def build_ternary_vector(
    width: int, root_sign: int
) -> tuple[DAG, dict[tuple[int, ...], tuple[int, int]], tuple[int, ...]]:
    require(width >= 0 and root_sign in (0, 1), "bad ternary vector request")
    dag = DAG()
    zero, one, two = names(dag)
    digits = tuple(dag.terminal(f"t{index}") for index in range(width))
    if width == 0:
        outputs = {(): (zero, zero) if root_sign == 0 else (zero, one)}
        return dag, outputs, digits
    states = balanced_ternary_states(dag, digits, zero, one, two)
    outputs: dict[tuple[int, ...], tuple[int, int]] = {}
    for physical, state in states.items():
        gain = dag.discriminator(state, two, zero)  # state==1
        if cell_sign(root_sign, physical) == 0:
            loss = dag.discriminator(zero, state, one)  # state==0
            outputs[physical] = (loss, gain)
        else:
            not_loss = dag.discriminator(state, two, one)  # state!=0
            outputs[physical] = (gain, not_loss)
    return dag, outputs, digits


def roots_for(
    outputs: dict[tuple[int, ...], tuple[int, int]], width: int
) -> tuple[int, ...]:
    return tuple(root for physical in words(width) for root in outputs[physical])


def evaluate_vector(
    dag: DAG,
    outputs: dict[tuple[int, ...], tuple[int, int]],
    target: tuple[int, ...],
    anchor: int = 2,
) -> tuple[int, ...]:
    environment = {"A": anchor}
    environment.update({f"t{index}": value for index, value in enumerate(target)})
    return dag.evaluate(roots_for(outputs, len(target)), environment)


def ceil_log_two(value: int) -> int:
    require(value >= 1, "bad log input")
    exponent = 0
    power = 1
    while power < value:
        power *= 2
        exponent += 1
    return exponent


@cache
def pair_state_exact(width: int) -> int:
    """Exact hash-consed pair-state operation count, excluding the names."""
    if width == 0:
        return 0
    if width == 1:
        return 4
    left = width // 2
    # All q loss roots are distinct.  Gain roots identify exactly the physical
    # words differing only by a final 0/1, leaving 2q/3 distinct roots.
    return (
        pair_state_exact(left)
        + pair_state_exact(width - left)
        + 5 * 3 ** (width - 1)
    )


def pair_vector_exact(width: int, root_sign: int) -> int:
    if width == 0:
        return 2
    capacity = 3**width
    negative_cells = (capacity - 1) // 2 if root_sign == 0 else (capacity + 1) // 2
    # At width one, exactly one requested u(loss) is already the leaf-state
    # gain/loss complement.  At larger widths all final complements are new.
    final_complements = negative_cells - int(width == 1)
    return 2 + pair_state_exact(width) + final_complements


@cache
def shared_rail_state_exact(width: int) -> int:
    """Exact structural rail-node recurrence, excluding the two names."""
    if width == 0:
        return 0
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    left_capacity = 3**left
    right_capacity = 3**right
    # Every loss merge is structurally distinct.  Right gain rails have zero
    # plus exactly (3^right-1)/2 distinct nonzero roots.
    return (
        shared_rail_state_exact(left)
        + shared_rail_state_exact(right)
        + left_capacity * right_capacity
        + left_capacity * (right_capacity - 1) // 2
    )


def shared_rail_vector_ledger(width: int, root_sign: int) -> int:
    """Conservative final ledger, exact except for one width-one collision."""
    if width == 0:
        return 2
    capacity = 3**width
    negative_cells = (capacity - 1) // 2 if root_sign == 0 else (capacity + 1) // 2
    return 2 + shared_rail_state_exact(width) + negative_cells


def shared_rail_vector_exact(width: int, root_sign: int) -> int:
    return shared_rail_vector_ledger(width, root_sign) - int(width == 1)


def right_not_loss_extra(width: int) -> int:
    require(width >= 1, "right not-loss width")
    return 1 if width == 1 else 2 * 3 ** (width - 1)


def terminal_mixed_vector_exact(width: int, root_sign: int) -> int:
    require(width >= 0 and root_sign in (0, 1), "terminal-mixed count request")
    if width == 0:
        return 2
    if width == 1:
        return 5 + root_sign
    left = (width + 1) // 2
    right = width // 2
    left_capacity = 3**left
    right_capacity = 3**right
    capacity = left_capacity * right_capacity
    gain_nodes = left_capacity * (right_capacity - 1) // 2
    overlap = (3 ** (width - 1) + (1 if root_sign == 0 else -1)) // 2
    return (
        2
        + shared_rail_state_exact(left)
        + shared_rail_state_exact(right)
        + right_not_loss_extra(right)
        + capacity
        + gain_nodes
        - overlap
    )


@cache
def extended_rail_state_exact(width: int) -> int:
    require(width >= 1, "extended rail count width")
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    left_capacity = 3**left
    right_capacity = 3**right
    capacity = left_capacity * right_capacity
    return (
        shared_rail_state_exact(left)
        + extended_rail_state_exact(right)
        + 2 * capacity
        - 3 ** (width - 1)
        + left_capacity * (right_capacity - 1) // 2
    )


def recursive_terminal_vector_exact(width: int, root_sign: int) -> int:
    require(width >= 0 and root_sign in (0, 1), "recursive-terminal count")
    if width <= 1:
        return terminal_mixed_vector_exact(width, root_sign)
    left = (width + 1) // 2
    right = width // 2
    left_capacity = 3**left
    right_capacity = 3**right
    capacity = left_capacity * right_capacity
    gain_nodes = left_capacity * (right_capacity - 1) // 2
    overlap = (3 ** (width - 1) + (1 if root_sign == 0 else -1)) // 2
    return (
        2
        + shared_rail_state_exact(left)
        + extended_rail_state_exact(right)
        + gain_nodes
        + capacity
        - overlap
    )


@cache
def ternary_state_upper(width: int) -> int:
    if width == 0:
        return 0
    if width == 1:
        return 3
    left = width // 2
    return ternary_state_upper(left) + ternary_state_upper(width - left) + 3**width


def ternary_vector_upper(width: int) -> int:
    return 2 if width == 0 else 2 + ternary_state_upper(width) + 2 * 3**width


def vector_depth_upper(width: int) -> int:
    return 2 if width == 0 else 4 + ceil_log_two(width)


def recursive_terminal_depth_upper(width: int) -> int:
    return 2 if width == 0 else 3 + ceil_log_two(width)


def algebra_checks() -> dict[str, object]:
    state_encoding = {EQUAL: 2, LOSS: 0, GAIN: 1}
    ternary_rows = 0
    for left, right in itertools.product((EQUAL, LOSS, GAIN), repeat=2):
        expected = state_encoding[mode_product(left, right)]
        actual = d(state_encoding[left], 2, state_encoding[right])
        require(actual == expected, "one-d ternary composition failed")
        ternary_rows += 1
    ternary_associativity = 0
    for a, b, c in itertools.product((EQUAL, LOSS, GAIN), repeat=3):
        require(
            mode_product(mode_product(a, b), c)
            == mode_product(a, mode_product(b, c)),
            "mode product is not associative",
        )
        ternary_associativity += 1

    pair_rows = 0
    pair_associativity = 0
    for left, right in itertools.product((EQUAL, LOSS, GAIN), repeat=2):
        left_loss, left_gain = positive_code(left)
        right_loss, right_gain = positive_code(right)
        actual = (
            d(left_loss, left_gain, right_loss),
            d(left_gain, left_loss, right_gain),
        )
        require(actual == positive_code(mode_product(left, right)), "two-d pair failed")
        pair_rows += 1
    for a, b, c in itertools.product((EQUAL, LOSS, GAIN), repeat=3):
        def pair_mul(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
            return (d(x[0], x[1], y[0]), d(x[1], x[0], y[1]))

        require(
            pair_mul(pair_mul(positive_code(a), positive_code(b)), positive_code(c))
            == pair_mul(positive_code(a), pair_mul(positive_code(b), positive_code(c))),
            "pair operation is not associative",
        )
        pair_associativity += 1

    zero_gain_elision_rows = 0
    for left, right in itertools.product((EQUAL, LOSS, GAIN), repeat=2):
        left_loss, left_gain = positive_code(left)
        _right_loss, right_gain = positive_code(right)
        if right_gain == 0:
            require(
                d(left_gain, left_loss, 0) == left_gain,
                "right-zero gain elision failed",
            )
            zero_gain_elision_rows += 1

    # Exact declared-grammar search.  A code qualifies when each composition
    # coordinate is one d-node over the four input bits and 0/1.
    bit_pairs = tuple(itertools.product((0, 1), repeat=2))
    leaf_names = ("a0", "a1", "b0", "b1", "zero", "one")
    composable_codes: list[tuple[tuple[int, int], ...]] = []
    for code_tuple in itertools.permutations(bit_pairs, 3):
        code = dict(zip((EQUAL, LOSS, GAIN), code_tuple, strict=True))
        rows: list[tuple[dict[str, int], tuple[int, int]]] = []
        for left, right in itertools.product((EQUAL, LOSS, GAIN), repeat=2):
            environment = dict(
                zip(leaf_names, code[left] + code[right] + (0, 1), strict=True)
            )
            rows.append((environment, code[mode_product(left, right)]))
        coordinate_hits = []
        for coordinate in (0, 1):
            target = tuple(output[coordinate] for _, output in rows)
            hits = 0
            for x, y, z in itertools.product(leaf_names, repeat=3):
                actual = tuple(d(env[x], env[y], env[z]) for env, _ in rows)
                hits += int(actual == target)
            coordinate_hits.append(hits)
        if all(coordinate_hits):
            composable_codes.append(code_tuple)

    require(len(composable_codes) == 4, "two-d code census drift")
    positive_tuple = tuple(positive_code(mode) for mode in (EQUAL, LOSS, GAIN))
    negative_tuple = tuple(negative_code(mode) for mode in (EQUAL, LOSS, GAIN))
    require(positive_tuple in composable_codes, "positive code missing")
    require(negative_tuple not in composable_codes, "negative code unexpectedly two-d")

    # Both positive-code outputs are distinct new truth tables, so a circuit
    # with only one single-output operation cannot expose both.
    rows = tuple(itertools.product((EQUAL, LOSS, GAIN), repeat=2))
    leaf_tables = {
        tuple(positive_code(a)[0] for a, _ in rows),
        tuple(positive_code(a)[1] for a, _ in rows),
        tuple(positive_code(b)[0] for _, b in rows),
        tuple(positive_code(b)[1] for _, b in rows),
        (0,) * len(rows),
        (1,) * len(rows),
    }
    out_loss = tuple(positive_code(mode_product(a, b))[0] for a, b in rows)
    out_gain = tuple(positive_code(mode_product(a, b))[1] for a, b in rows)
    require(out_loss != out_gain, "pair outputs collapsed")
    require(out_loss not in leaf_tables and out_gain not in leaf_tables, "pair output is free")

    # The width-one pair state needs four distinct nonterminal Boolean
    # functions; four operation nodes construct them, hence this base is exact.
    required_leaf_tables = {
        (0, 1, 1),  # loss, physical digit 0
        (1, 0, 1),  # loss, physical digit 1
        (1, 0, 0),  # loss, physical digit 2
        (0, 1, 0),  # gain, physical digit 2
    }
    terminal_tables = {(0, 1, 2), (0, 0, 0), (1, 1, 1), (2, 2, 2)}
    require(required_leaf_tables.isdisjoint(terminal_tables), "leaf function became free")
    require(len(required_leaf_tables) == 4, "leaf outputs collided")

    return {
        "ternary_composition_rows": ternary_rows,
        "ternary_associativity_rows": ternary_associativity,
        "pair_composition_rows": pair_rows,
        "pair_associativity_rows": pair_associativity,
        "right_zero_gain_elision_rows": zero_gain_elision_rows,
        "two_d_composable_injective_bit_codes": len(composable_codes),
        "positive_code_is_two_d_composable": True,
        "negative_code_is_two_d_composable": False,
        "pair_one_operation_impossible_in_declared_grammar": True,
        "width_one_pair_leaf_minimum_operations": 4,
    }


def semantic_vector_checks() -> dict[str, object]:
    semantic_pairs = 0
    constant_pairs = 0
    dependency_checks = 0
    materialized_rows: list[dict[str, object]] = []
    for representation, builder in (
        ("recursive_terminal_rails", build_recursive_terminal_vector),
        ("terminal_mixed_rails", build_terminal_mixed_vector),
        ("shared_gain_loss_rails", build_shared_rail_vector),
        ("gain_loss_pair", build_pair_vector),
        ("native_ternary", build_ternary_vector),
    ):
        for width in range(0, 7):
            capacity = 3**width
            for root_sign in (0, 1):
                dag, outputs, _ = builder(width, root_sign)
                roots = roots_for(outputs, width)
                allowed = frozenset(("A", *(f"t{i}" for i in range(width))))
                require(dag.dependencies(roots) <= allowed, "payload dependency appeared")
                dependency_checks += 1
                require(max(dag.depths[root] for root in roots) <= vector_depth_upper(width), "depth")
                if representation == "recursive_terminal_rails":
                    require(
                        max(dag.depths[root] for root in roots)
                        <= recursive_terminal_depth_upper(width),
                        "recursive-terminal depth",
                    )
                if representation == "recursive_terminal_rails":
                    require(
                        dag.operation_count
                        == recursive_terminal_vector_exact(width, root_sign),
                        "recursive-terminal exact size",
                    )
                elif representation == "terminal_mixed_rails":
                    require(
                        dag.operation_count
                        == terminal_mixed_vector_exact(width, root_sign),
                        "terminal-mixed exact size",
                    )
                elif representation == "shared_gain_loss_rails":
                    require(
                        dag.operation_count == shared_rail_vector_exact(width, root_sign),
                        "shared rail exact size",
                    )
                elif representation == "gain_loss_pair":
                    require(
                        dag.operation_count == pair_vector_exact(width, root_sign),
                        "pair exact size",
                    )
                else:
                    require(
                        dag.operation_count == ternary_vector_upper(width),
                        "ternary exact size",
                    )
                for target in words(width):
                    program = evaluate_vector(dag, outputs, target)
                    require(len(program) == 2 * capacity, "not all controls emitted")
                    for index, physical in enumerate(words(width)):
                        pair = program[2 * index : 2 * index + 2]
                        require(pair == expected_pair(root_sign, physical, target), "pair mismatch")
                        semantic_pairs += 1

                if representation in (
                    "recursive_terminal_rails",
                    "terminal_mixed_rails",
                    "shared_gain_loss_rails",
                    "gain_loss_pair",
                ):
                    for constant in (0, 1):
                        const_dag, const_outputs, _ = build_pair_vector(
                            width, root_sign, constant
                        )
                        require(const_dag.operation_count == 2, "constant mode has hidden logic")
                        program = evaluate_vector(const_dag, const_outputs, (0,) * width)
                        for index, physical in enumerate(words(width)):
                            require(
                                program[2 * index : 2 * index + 2]
                                == expected_pair(root_sign, physical, None, constant),
                                "constant mode mismatch",
                            )
                            constant_pairs += 1

        for width in range(0, 10):
            for root_sign in (0, 1):
                dag, outputs, _ = builder(width, root_sign)
                roots = roots_for(outputs, width)
                materialized_rows.append(
                    {
                        "representation": representation,
                        "width": width,
                        "root": "P" if root_sign == 0 else "N",
                        "capacity": 3**width,
                        "actual_shared_operation_nodes": dag.operation_count,
                        "certified_operation_exact": (
                            recursive_terminal_vector_exact(width, root_sign)
                            if representation == "recursive_terminal_rails"
                            else (
                                terminal_mixed_vector_exact(width, root_sign)
                                if representation == "terminal_mixed_rails"
                                else (
                                    shared_rail_vector_exact(width, root_sign)
                                    if representation == "shared_gain_loss_rails"
                                    else (
                                        pair_vector_exact(width, root_sign)
                                        if representation == "gain_loss_pair"
                                        else ternary_vector_upper(width)
                                    )
                                )
                            )
                        ),
                        "actual_depth": max(dag.depths[root] for root in roots),
                        "certified_depth_upper": (
                            recursive_terminal_depth_upper(width)
                            if representation == "recursive_terminal_rails"
                            else vector_depth_upper(width)
                        ),
                    }
                )
    return {
        "semantic_projection_pairs_through_width_six": semantic_pairs,
        "constant_pairs_through_width_six": constant_pairs,
        "dependency_checks": dependency_checks,
        "materialized_rows": materialized_rows,
    }


def structural_sharing_checks() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for width in range(1, 11):
        capacity = 3**width
        dag = DAG()
        zero, one, two = names(dag)
        digits = tuple(dag.terminal(f"t{index}") for index in range(width))
        states = balanced_shared_rail_states(dag, digits, zero, one, two)
        loss_roots = {pair[0] for pair in states.values()}
        gain_roots = {pair[1] for pair in states.values()}
        require(len(loss_roots) == capacity, "loss-root collision")
        require(len(gain_roots) == (capacity + 1) // 2, "gain-class count drift")
        require(zero in gain_roots, "zero gain class missing")
        require(
            dag.operation_count == 2 + shared_rail_state_exact(width),
            "exact structural rail recurrence drift",
        )
        for root_sign in (0, 1):
            full_dag, outputs, _ = build_shared_rail_vector(width, root_sign)
            require(len(outputs) == capacity, "complete rail-vector output count")
            actual = full_dag.operation_count
            ledger = shared_rail_vector_ledger(width, root_sign)
            exact = shared_rail_vector_exact(width, root_sign)
            require(actual == exact, "exact complete rail-vector count drift")
            mixed_dag, mixed_outputs, _ = build_terminal_mixed_vector(
                width, root_sign
            )
            require(len(mixed_outputs) == capacity, "terminal-mixed output count")
            mixed_exact = terminal_mixed_vector_exact(width, root_sign)
            require(
                mixed_dag.operation_count == mixed_exact,
                "terminal-mixed structural recurrence drift",
            )
            recursive_dag, recursive_outputs, _ = build_recursive_terminal_vector(
                width, root_sign
            )
            require(len(recursive_outputs) == capacity, "recursive-terminal outputs")
            recursive_exact = recursive_terminal_vector_exact(width, root_sign)
            require(
                recursive_dag.operation_count == recursive_exact,
                "recursive-terminal structural recurrence drift",
            )
            rows.append(
                {
                    "width": width,
                    "root": "P" if root_sign == 0 else "N",
                    "capacity": capacity,
                    "distinct_loss_roots": len(loss_roots),
                    "distinct_gain_roots_including_zero": len(gain_roots),
                    "exact_state_operation_nodes_including_names": (
                        2 + shared_rail_state_exact(width)
                    ),
                    "actual_complete_vector_operation_nodes": actual,
                    "exact_complete_vector_formula": exact,
                    "complete_vector_ledger": ledger,
                    "hash_consing_slack": ledger - actual,
                    "terminal_mixed_exact_operation_nodes": mixed_exact,
                    "terminal_mixed_actual_operation_nodes": (
                        mixed_dag.operation_count
                    ),
                    "recursive_terminal_exact_operation_nodes": recursive_exact,
                    "recursive_terminal_actual_operation_nodes": (
                        recursive_dag.operation_count
                    ),
                }
            )
    return {
        "rows": rows,
        "gain_class_formula": "(3^w+1)/2 including the identically-zero rail",
        "nonzero_gain_class_formula": "(3^w-1)/2",
        "classification": (
            "a nonzero gain rail is identified by the physical prefix ending "
            "at its last digit 2; later 0/1 suffixes are irrelevant"
        ),
    }


class ROBDD:
    """Canonical Boolean DAG; d is applied directly, not via majority."""

    def __init__(self) -> None:
        self.nodes: list[tuple[int, int, int] | None] = [None, None]
        self.unique: dict[tuple[int, int, int], int] = {}
        self.memo: dict[tuple[int, int, int], int] = {}

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

    def cofactor(self, node: int, variable: int, value: int) -> int:
        record = self.nodes[node]
        if record is None or record[0] != variable:
            return node
        return record[1 + value]

    def apply_d(self, left: int, middle: int, right: int) -> int:
        key = (left, middle, right)
        if key in self.memo:
            return self.memo[key]
        if left < 2 and middle < 2 and right < 2:
            result = d(left, middle, right)
        else:
            variable = min(self.top(left), self.top(middle), self.top(right))
            result = self.make(
                variable,
                self.apply_d(
                    self.cofactor(left, variable, 0),
                    self.cofactor(middle, variable, 0),
                    self.cofactor(right, variable, 0),
                ),
                self.apply_d(
                    self.cofactor(left, variable, 1),
                    self.cofactor(middle, variable, 1),
                    self.cofactor(right, variable, 1),
                ),
            )
        self.memo[key] = result
        return result


def router_labels(width: int, root_sign: int) -> tuple[int, ...]:
    labels: list[int] = []
    for branch, physical in enumerate(words(width)):
        if cell_sign(root_sign, physical) == 0:
            labels.extend((branch, -1, -1))
        else:
            labels.extend((-1, branch, -1))
    return tuple(labels)


def bdd_router(
    bdd: ROBDD,
    labels: tuple[int, ...],
    program: tuple[int, ...],
    variables: tuple[int, ...],
) -> int:
    iterator = iter(program)
    layer = [next(iterator) if label == -1 else variables[label] for label in labels]
    while len(layer) > 1:
        require(len(layer) % 3 == 0, "router layer malformed")
        layer = [
            bdd.apply_d(layer[index], layer[index + 1], layer[index + 2])
            for index in range(0, len(layer), 3)
        ]
    return layer[0]


def router_checks() -> dict[str, object]:
    mode_checks = 0
    effective_control_mutations = 0
    concrete_checks = 0
    for width in range(0, 5):
        capacity = 3**width
        bdd = ROBDD()
        variables = tuple(bdd.variable(index) for index in range(capacity))
        for root_sign in (0, 1):
            labels = router_labels(width, root_sign)
            dag, outputs, _ = build_recursive_terminal_vector(width, root_sign)
            for target_index, target in enumerate(words(width)):
                program = evaluate_vector(dag, outputs, target)
                root = bdd_router(bdd, labels, program, variables)
                expected = (
                    variables[target_index]
                    if root_sign == 0
                    else bdd.make(target_index, 1, 0)
                )
                require(root == expected, "full-router projection failed")
                mode_checks += 1

                mutation_found = False
                for offset in (2 * target_index, 2 * target_index + 1):
                    mutated = list(program)
                    mutated[offset] ^= 1
                    if bdd_router(bdd, labels, tuple(mutated), variables) != expected:
                        mutation_found = True
                        break
                require(mutation_found, "target-cell mutations were ineffective")
                effective_control_mutations += 1

                if width <= 2:
                    for valuation in itertools.product((0, 1), repeat=capacity):
                        controls = iter(program)
                        layer = [
                            next(controls) if label == -1 else valuation[label]
                            for label in labels
                        ]
                        while len(layer) > 1:
                            layer = [
                                d(layer[index], layer[index + 1], layer[index + 2])
                                for index in range(0, len(layer), 3)
                            ]
                        require(layer[0] == (valuation[target_index] ^ root_sign), "concrete")
                        concrete_checks += 1

            for constant in (0, 1):
                const_dag, const_outputs, _ = build_recursive_terminal_vector(
                    width, root_sign, constant
                )
                program = evaluate_vector(const_dag, const_outputs, (0,) * width)
                require(bdd_router(bdd, labels, program, variables) == constant, "constant")
                mode_checks += 1
    return {
        "direct_robdd_projection_and_constant_checks": mode_checks,
        "effective_target_control_mutations": effective_control_mutations,
        "concrete_router_checks_through_width_two": concrete_checks,
    }


def mutation_checks() -> dict[str, object]:
    state_encoding = {EQUAL: 2, LOSS: 0, GAIN: 1}

    ternary_counterexample = None
    for left, right in itertools.product((EQUAL, LOSS, GAIN), repeat=2):
        expected = state_encoding[mode_product(left, right)]
        mutated = d(state_encoding[left], 1, state_encoding[right])
        if mutated != expected:
            ternary_counterexample = {
                "left_mode": left,
                "right_mode": right,
                "expected_state": expected,
                "mutated_state": mutated,
            }
            break
    require(ternary_counterexample is not None, "wrong-neutral mutation survived")

    gain_counterexample = None
    for left, right in itertools.product((EQUAL, LOSS, GAIN), repeat=2):
        left_loss, left_gain = positive_code(left)
        right_loss, right_gain = positive_code(right)
        expected_gain = positive_code(mode_product(left, right))[1]
        mutated_gain = d(left_gain, 0, right_gain)  # unguarded OR
        if mutated_gain != expected_gain:
            gain_counterexample = {
                "left_mode": left,
                "right_mode": right,
                "expected_gain": expected_gain,
                "mutated_gain": mutated_gain,
            }
            break
    require(gain_counterexample is not None, "unguarded-gain mutation survived")

    complement_counterexample = None
    for mode in (EQUAL, LOSS, GAIN):
        loss, gain = positive_code(mode)
        mutated_negative = (gain, loss)
        if mutated_negative != negative_code(mode):
            complement_counterexample = {
                "mode": mode,
                "expected_negative": negative_code(mode),
                "mutated_negative": mutated_negative,
            }
            break
    require(complement_counterexample is not None, "negative complement mutation survived")

    leaf_counterexample = None
    for target_digit in (0, 1, 2):
        loss_one = u(target_digit)
        expected_gain_two = int(target_digit == 1)
        mutated_gain_two = loss_one
        if mutated_gain_two != expected_gain_two:
            leaf_counterexample = {
                "target_digit": target_digit,
                "expected_gain_for_physical_two": expected_gain_two,
                "mutated_gain": mutated_gain_two,
            }
            break
    require(leaf_counterexample is not None, "leaf-complement mutation survived")

    elision_counterexample = None
    for left, right in itertools.product((EQUAL, LOSS, GAIN), repeat=2):
        left_loss, left_gain = positive_code(left)
        _right_loss, right_gain = positive_code(right)
        correct_gain = positive_code(mode_product(left, right))[1]
        mutated_gain = left_gain  # wrongly elide even a nonzero right rail
        if right_gain == 1 and mutated_gain != correct_gain:
            elision_counterexample = {
                "left_mode": left,
                "right_mode": right,
                "expected_gain": correct_gain,
                "wrongly_reused_left_gain": mutated_gain,
            }
            break
    require(elision_counterexample is not None, "over-elision mutation survived")

    # If the top mixed rail and its equal gain rail are materialized twice,
    # width-two P pays two avoidable scalar nodes and misses the exact count.
    duplicate_cross_rail_counterexample = {
        "width": 2,
        "root": "P",
        "exact_with_cross_rail_reuse": terminal_mixed_vector_exact(2, 0),
        "mutated_without_reuse": terminal_mixed_vector_exact(2, 0) + 2,
    }
    require(
        duplicate_cross_rail_counterexample["exact_with_cross_rail_reuse"] == 21
        and duplicate_cross_rail_counterexample["mutated_without_reuse"] == 23,
        "cross-rail cost mutation drift",
    )

    anchor_counterexample = None
    dag, outputs, _ = build_recursive_terminal_vector(1, 0)
    for target in words(1):
        program = evaluate_vector(dag, outputs, target, anchor=1)
        for index, physical in enumerate(words(1)):
            actual = program[2 * index : 2 * index + 2]
            expected = expected_pair(0, physical, target)
            if actual != expected:
                anchor_counterexample = {
                    "target": target,
                    "physical": physical,
                    "expected": expected,
                    "mutated_anchor_program": actual,
                }
                break
        if anchor_counterexample is not None:
            break
    require(anchor_counterexample is not None, "binary-anchor mutation survived")

    return {
        "wrong_ternary_neutral": ternary_counterexample,
        "unguarded_gain": gain_counterexample,
        "missing_negative_complement": complement_counterexample,
        "missing_leaf_complement": leaf_counterexample,
        "elide_nonzero_right_gain": elision_counterexample,
        "duplicate_cross_rail_outputs": duplicate_cross_rail_counterexample,
        "anchor_not_two": anchor_counterexample,
    }


def output_function_checks() -> dict[str, object]:
    """Independent bounded check of the scalar-output counting lower bound."""
    rows: list[dict[str, object]] = []
    cross_rail_identity_rows = 0
    for width in range(1, 6):
        targets = words(width)
        capacity = 3**width
        for prefix in words(width - 1):
            physical_one = prefix + (1,)
            physical_two = prefix + (2,)
            for target in targets:
                loss_one, _gain_one = positive_code(
                    first_mode(target, physical_one)
                )
                _loss_two, gain_two = positive_code(
                    first_mode(target, physical_two)
                )
                require(1 - loss_one == gain_two, "cross-rail identity failed")
                cross_rail_identity_rows += 1
        raw_inputs = {
            (2,) * capacity,
            *(
                tuple(target[index] for target in targets)
                for index in range(width)
            ),
        }
        for root_sign in (0, 1):
            functions: list[tuple[int, ...]] = []
            for physical in words(width):
                left: list[int] = []
                right: list[int] = []
                for target in targets:
                    pair = expected_pair(root_sign, physical, target)
                    left.append(pair[0])
                    right.append(pair[1])
                functions.extend((tuple(left), tuple(right)))
            distinct = set(functions)
            expected = 4 * capacity // 3 + root_sign
            require(len(distinct) == expected, "distinct-output formula drift")
            require(distinct.isdisjoint(raw_inputs), "a control became a free raw input")
            rows.append(
                {
                    "width": width,
                    "root": "P" if root_sign == 0 else "N",
                    "capacity": capacity,
                    "distinct_noninput_scalar_outputs": len(distinct),
                    "certified_scalar_gate_lower_bound": expected,
                }
            )
    return {
        "bounded_rows": rows,
        "not_loss_a1_equals_gain_a2_rows": cross_rail_identity_rows,
        "all_width_formula": {
            "P": "4q/3",
            "N": "4q/3+1",
            "reason": (
                "q mixed loss/not-loss rails plus (q+1)/2 gain rails, minus "
                "overlap (q/3+1)/2 for P or (q/3-1)/2 for N"
            ),
            "scope": (
                "scalar original-signature shared DAG with raw A,t inputs; "
                "output-count lower bound, not global optimality"
            ),
        },
    }


def arithmetic_checks() -> dict[str, object]:
    rows = []
    for width in range(0, 513):
        capacity = 3**width
        recursive_p = recursive_terminal_vector_exact(width, 0)
        recursive_n = recursive_terminal_vector_exact(width, 1)
        terminal_p = terminal_mixed_vector_exact(width, 0)
        terminal_n = terminal_mixed_vector_exact(width, 1)
        rail_p = shared_rail_vector_ledger(width, 0)
        rail_n = shared_rail_vector_ledger(width, 1)
        pair_p = pair_vector_exact(width, 0)
        pair_n = pair_vector_exact(width, 1)
        ternary = ternary_vector_upper(width)
        require(pair_p <= 4 * capacity and pair_n <= 4 * capacity, "4q pair bound")
        require(ternary <= 4 * capacity, "4q ternary bound")
        error_scale = 3 ** ((width + 1) // 2)
        require(
            3 * recursive_p <= 4 * capacity + 15 * error_scale,
            "recursive-terminal P envelope",
        )
        require(
            3 * recursive_n <= 4 * capacity + 15 * error_scale,
            "recursive-terminal N envelope",
        )
        require(3 * recursive_p <= 7 * capacity, "7q/3 recursive P")
        require(3 * recursive_n <= 7 * capacity, "7q/3 recursive N")
        require(3 * terminal_p <= 7 * capacity, "7q/3 terminal-mixed P")
        require(9 * terminal_n <= 22 * capacity, "22q/9 terminal-mixed N")
        if width >= 1:
            require(9 * pair_p <= 29 * capacity, "29q/9 P bound")
            require(3 * pair_n <= 10 * capacity, "10q/3 N bound")
        if width >= 2:
            require(rail_p <= 3 * capacity, "3q shared-rail P bound")
            require(rail_n <= 3 * capacity, "3q shared-rail N bound")
        if width <= 16:
            rows.append(
                {
                    "width": width,
                    "capacity": capacity,
                    "recursive_terminal_P_exact": recursive_p,
                    "recursive_terminal_N_exact": recursive_n,
                    "terminal_mixed_P_exact": terminal_p,
                    "terminal_mixed_N_exact": terminal_n,
                    "shared_rail_P_ledger": rail_p,
                    "shared_rail_N_ledger": rail_n,
                    "pair_P_upper": pair_p,
                    "pair_N_upper": pair_n,
                    "ternary_upper": ternary,
                    "depth_upper": vector_depth_upper(width),
                }
            )
    require(pair_vector_exact(2, 0) * 9 == 29 * 3**2, "P sharp width drift")
    require(pair_vector_exact(3, 0) * 9 == 29 * 3**3, "P sharp width drift")
    require(pair_vector_exact(2, 1) * 3 == 10 * 3**2, "N sharp width drift")
    require(shared_rail_vector_ledger(2, 1) == 3 * 3**2, "3q sharp width drift")
    require(terminal_mixed_vector_exact(2, 0) * 3 == 7 * 3**2, "7q/3 sharp")
    require(terminal_mixed_vector_exact(2, 1) * 9 == 22 * 3**2, "22q/9 sharp")
    return {
        "all_width_arithmetic_checked_through": 512,
        "recursive_terminal_depth_bound": (
            "2 if w=0 else 3+ceil(log2(w))"
        ),
        "recursive_terminal_envelope": (
            "3S<=4q+15*3^ceil(w/2), hence S=(4/3+o(1))q"
        ),
        "recursive_terminal_uniform_bound": "7q/3 for either root sign",
        "terminal_mixed_P_uniform_bound": "7q/3",
        "terminal_mixed_N_uniform_bound": "22q/9",
        "terminal_mixed_asymptotic": "(4/3+o(1))q",
        "shared_rail_uniform_bound": "3q",
        "shared_rail_asymptotic": "(2+o(1))q",
        "shared_rail_state_recurrence": (
            "R(1)=4; R(w)=R(ceil(w/2))+R(floor(w/2))+"
            "3^w+3^ceil(w/2)*(3^floor(w/2)-1)/2"
        ),
        "pair_P_bound": "29q/9",
        "pair_N_bound": "10q/3",
        "uniform_pair_bound": "10q/3",
        "pair_asymptotic": "(13/6+o(1))q",
        "native_ternary_bound": "4q",
        "balanced_depth_bound": "2 if w=0 else 4+ceil(log2(w))",
        "finite_rows": rows,
    }


def main() -> None:
    require(sha256_path(STATE) == STATE_SHA256, "frozen STATE hash drift")
    semantic = {
        "algebra": algebra_checks(),
        "arithmetic": arithmetic_checks(),
        "mutations": mutation_checks(),
        "output_functions": output_function_checks(),
        "routers": router_checks(),
        "sharing": structural_sharing_checks(),
        "vectors": semantic_vector_checks(),
    }
    canonical = json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "checker_sha256": sha256_path(Path(__file__)),
        "schema": "orbit.program_vector_optimization.algebraic.v1",
        "semantic": semantic,
        "semantic_sha256": hashlib.sha256(canonical).hexdigest(),
        "state_sha256": STATE_SHA256,
        "status": "PASS",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

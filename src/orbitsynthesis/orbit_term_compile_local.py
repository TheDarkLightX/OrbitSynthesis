"""Lupanov-style local-coding compiler for conservative Quackenbush-Q tables.

The construction is parameter-free globally.  On the branch where ``x_a=2``
is the first nonbinary coordinate, ``u(u(x_a))``, ``u(x_a)``, and ``x_a``
dynamically supply 0, 1, and 2.  A small block of the remaining coordinates is
used as a local code: all functions on that block are generated along a ternary
Gray path, and a decision DAG on the other coordinates selects the required
block function.

This module materializes the construction for bounded experiments.  It exposes
the original Gray-path schedule, a layered prefix schedule, and a recursive
subcube schedule.  The subcube schedule indexes the local-function library by
block coordinates; its library depth is linear in the number of block
coordinates rather than in the number of block assignments.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from itertools import product

from .orbit_term_compile import (
    Disc,
    Expr,
    Q,
    UnaryU,
    Var,
    complement,
    normal_selector,
)


@dataclass(frozen=True)
class SlicePlan:
    """Local-coding split for a first-2 anchor slice."""

    anchor: int
    domain_size: int
    block_positions: tuple[int, ...]
    block_assignments: int
    prefix_assignments: int
    library_functions: int


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _allowed_values(position: int, anchor: int) -> tuple[int, ...]:
    return (0, 1) if position < anchor else Q


def _slice_domain_size(arity: int, anchor: int) -> int:
    return 2**anchor * 3 ** (arity - anchor - 1)


def suggested_block_assignment_cap(arity: int, anchor: int) -> int:
    """Return floor(log_3(N/(r-1))), with a safe small-arity floor of one."""

    _require(arity >= 1, "arity must be positive")
    _require(0 <= anchor < arity, "anchor outside arity")
    remaining = arity - 1
    if remaining == 0:
        return 1
    ratio = _slice_domain_size(arity, anchor) // remaining
    exponent = 0
    power = 1
    while power * 3 <= ratio:
        power *= 3
        exponent += 1
    return max(1, exponent)


def _choose_block_positions(
    arity: int,
    anchor: int,
    assignment_cap: int,
) -> tuple[int, ...]:
    """Maximize a 2/3-factor block product without exceeding the cap."""

    _require(assignment_cap >= 1, "block assignment cap must be positive")
    binary = tuple(range(anchor))
    ternary = tuple(range(anchor + 1, arity))
    best_product = 1
    best_binary = 0
    best_ternary = 0
    power_two = 1
    for binary_count in range(len(binary) + 1):
        power_three = 1
        for ternary_count in range(len(ternary) + 1):
            candidate = power_two * power_three
            if best_product < candidate <= assignment_cap:
                best_product = candidate
                best_binary = binary_count
                best_ternary = ternary_count
            power_three *= 3
        power_two *= 2
    return binary[:best_binary] + ternary[:best_ternary]


def slice_plans(
    arity: int,
    *,
    block_assignment_cap: int | None = None,
) -> tuple[SlicePlan, ...]:
    """Describe every anchor slice without constructing its Gray library."""

    plans = []
    for anchor in range(arity):
        cap = (
            suggested_block_assignment_cap(arity, anchor)
            if block_assignment_cap is None
            else block_assignment_cap
        )
        positions = _choose_block_positions(arity, anchor, cap)
        assignments = 1
        for position in positions:
            assignments *= len(_allowed_values(position, anchor))
        domain_size = _slice_domain_size(arity, anchor)
        plans.append(
            SlicePlan(
                anchor=anchor,
                domain_size=domain_size,
                block_positions=positions,
                block_assignments=assignments,
                prefix_assignments=domain_size // assignments,
                library_functions=3**assignments,
            )
        )
    return tuple(plans)


def reflected_ternary_gray(length: int) -> Iterator[tuple[int, ...]]:
    """Yield all ternary words so consecutive words differ in one coordinate."""

    _require(length >= 0, "Gray-word length must be nonnegative")
    words: list[tuple[int, ...]] = [()]
    for _ in range(length):
        extended: list[tuple[int, ...]] = []
        for digit in Q:
            block = words if digit % 2 == 0 else reversed(words)
            extended.extend(word + (digit,) for word in block)
        words = extended
    yield from words


def layered_ternary_selector_count(length: int) -> int:
    """Count selectors in the layered library: 2*sum_(j<length) 3^j."""

    _require(length >= 0, "library length must be nonnegative")
    return 3**length - 1


def absorbing_two(left: Expr, right: Expr) -> Expr:
    """Return 2 iff either input is 2, and otherwise return ``left``."""

    left_flipped = UnaryU(left)
    left_binary = UnaryU(left_flipped)
    return Disc(
        left,
        left_binary,
        Disc(right, left_flipped, left),
    )


def balanced_absorbing_two(nodes: tuple[Expr, ...]) -> Expr:
    """Balanced fold of ``absorbing_two`` over a nonempty tuple."""

    _require(bool(nodes), "absorbing-two fold requires at least one node")
    if len(nodes) == 1:
        return nodes[0]
    midpoint = len(nodes) // 2
    return absorbing_two(
        balanced_absorbing_two(nodes[:midpoint]),
        balanced_absorbing_two(nodes[midpoint:]),
    )


def shallow_ternary_selector(
    selector: Expr,
    zero: Expr,
    one: Expr,
    two: Expr,
    branch_zero: Expr,
    branch_one: Expr,
    branch_two: Expr,
) -> Expr:
    """Select one of three arbitrary branches with branch depth three.

    The supplied value names must evaluate to 0, 1, and 2 on the branch where
    this term is used.  Every branch argument occurs exactly three discriminator
    levels below the root.
    """

    left = Disc(
        zero,
        Disc(selector, two, branch_zero),
        Disc(zero, selector, branch_zero),
    )
    right = Disc(
        Disc(one, selector, branch_one),
        one,
        Disc(selector, two, branch_two),
    )
    return Disc(left, zero, right)


def suggested_global_block_assignment_cap(arity: int) -> int:
    """Return floor(log_3(3^r/r)), with a small-arity floor of one."""

    _require(arity >= 1, "arity must be positive")
    ratio = 3**arity // arity
    exponent = 0
    power = 1
    while power * 3 <= ratio:
        power *= 3
        exponent += 1
    return max(1, exponent)


def _global_block_positions(
    arity: int,
    assignment_cap: int,
) -> tuple[int, ...]:
    _require(assignment_cap >= 1, "block assignment cap must be positive")
    assignments = 1
    count = 0
    while count < arity and assignments * 3 <= assignment_cap:
        assignments *= 3
        count += 1
    return tuple(range(count))


def compile_local_coding_coordinate_selector(
    arity: int,
    selector_indices: Mapping[tuple[int, ...], int],
    *,
    block_assignment_cap: int | None = None,
    library_schedule: str = "gray",
) -> Expr:
    """Compile a compatible coordinate selector with bounded local coding.

    ``block_assignment_cap`` bounds the number of input assignments in each
    local-code block.  If omitted, the asymptotic proof's per-slice cap is used.
    Large caps intentionally create exponentially large libraries.  The
    ``gray`` schedule also has exponential dependency depth; ``layered`` keeps
    dependency depth linear in the number of block assignments while creating
    exactly the same number of library selectors.  ``subcube`` recursively
    Shannon-expands over the block coordinates, retaining ``O(3^M)`` library
    size while using only ``O(log M)`` library depth for ``M`` assignments.
    """

    _require(arity >= 1, "arity must be positive")
    _require(
        library_schedule in {"gray", "layered", "subcube"},
        "library schedule must be gray, layered, or subcube",
    )
    points = tuple(product(Q, repeat=arity))
    _require(set(selector_indices) == set(points), "selector table is not total")
    _require(
        all(0 <= index < arity for index in selector_indices.values()),
        "selector index outside input arity",
    )
    for point in product((0, 1), repeat=arity):
        _require(
            selector_indices[point] == selector_indices[complement(point)],
            "binary selector indices are not complement-invariant",
        )

    variables = tuple(Var(index) for index in range(arity))

    def u2(node: Expr) -> Expr:
        return UnaryU(UnaryU(node))

    def binary_tree(position: int, representative: tuple[int, ...]) -> Expr:
        if position == arity:
            return variables[selector_indices[representative]]
        return normal_selector(
            variables[position],
            variables[0],
            binary_tree(position + 1, representative + (0,)),
            binary_tree(position + 1, representative + (1,)),
        )

    binary = binary_tree(1, (0,))
    plans = slice_plans(
        arity,
        block_assignment_cap=block_assignment_cap,
    )

    def slice_circuit(plan: SlicePlan) -> Expr:
        anchor = plan.anchor
        zero = u2(variables[anchor])
        one = UnaryU(variables[anchor])
        constants: dict[int, Expr] = {0: zero, 1: one, 2: variables[anchor]}
        block_positions = plan.block_positions
        prefix_positions = tuple(
            position
            for position in range(arity)
            if position != anchor and position not in block_positions
        )
        block_points = tuple(
            product(
                *(
                    _allowed_values(position, anchor)
                    for position in block_positions
                )
            )
        )

        def select_position(position: int, branches: tuple[Expr, ...]) -> Expr:
            """Select one arbitrary branch on this slice coordinate."""

            _require(len(branches) in {2, 3}, "unsupported slice alphabet")
            if len(branches) == 2:
                return normal_selector(
                    variables[position],
                    zero,
                    branches[0],
                    branches[1],
                )
            nonzero = normal_selector(
                variables[position],
                one,
                branches[1],
                branches[2],
            )
            return normal_selector(
                variables[position],
                zero,
                branches[0],
                nonzero,
            )

        if not block_positions:
            block_points = ((),)
            library: dict[tuple[int, ...], Expr] = {
                (0,): zero,
                (1,): one,
                (2,): variables[anchor],
            }
        elif library_schedule in {"gray", "layered"}:
            equality_terms = {
                (position, value): normal_selector(
                    variables[position],
                    constants[value],
                    one,
                    zero,
                )
                for position in block_positions
                for value in _allowed_values(position, anchor)
            }
            indicators: dict[tuple[int, ...], Expr] = {}
            for block_point in block_points:
                terms = tuple(
                    equality_terms[position, value]
                    for position, value in zip(
                        block_positions,
                        block_point,
                        strict=True,
                    )
                )
                indicator = terms[0]
                for term in terms[1:]:
                    indicator = normal_selector(indicator, one, term, zero)
                indicators[block_point] = indicator

            if library_schedule == "gray":
                gray_words = tuple(reflected_ternary_gray(len(block_points)))
                first = gray_words[0]
                _require(
                    first == (0,) * len(block_points),
                    "Gray path has wrong root",
                )
                library = {first: zero}
                previous_word = first
                previous_term = zero
                for word in gray_words[1:]:
                    differences = tuple(
                        index
                        for index, (left, right) in enumerate(
                            zip(previous_word, word, strict=True)
                        )
                        if left != right
                    )
                    _require(len(differences) == 1, "Gray path is not unit-Hamming")
                    changed = differences[0]
                    previous_term = normal_selector(
                        indicators[block_points[changed]],
                        one,
                        constants[word[changed]],
                        previous_term,
                    )
                    library[word] = previous_term
                    previous_word = word
            else:
                # Invariant after processing j points: each prefix term has the
                # requested values on those j points and remains zero on every
                # unprocessed point.  Point indicators are pairwise disjoint, so
                # the zero extension reuses its parent while only values 1 and 2
                # need new selectors.
                prefix_library: dict[tuple[int, ...], Expr] = {(): zero}
                selectors_created = 0
                for block_point in block_points:
                    indicator = indicators[block_point]
                    next_library: dict[tuple[int, ...], Expr] = {}
                    for word, parent in prefix_library.items():
                        next_library[word + (0,)] = parent
                        for value in (1, 2):
                            next_library[word + (value,)] = normal_selector(
                                indicator,
                                one,
                                constants[value],
                                parent,
                            )
                            selectors_created += 1
                    prefix_library = next_library
                _require(
                    selectors_created
                    == layered_ternary_selector_count(len(block_points)),
                    "layered library selector census drift",
                )
                library = prefix_library
        else:
            # Recursively enumerate all functions on the block-coordinate
            # subcubes.  At offset j, each truth vector is a concatenation of
            # one suffix truth vector per allowed value of block_positions[j].
            # The number of roots at that level is exactly 3^(suffix domain
            # size), so the total library remains O(3^M).  Its dependency depth
            # is two selector levels per binary block coordinate and four per
            # ternary coordinate, hence O(log M) for M block assignments.
            def subcube_library(offset: int) -> dict[tuple[int, ...], Expr]:
                if offset == len(block_positions):
                    return {
                        (0,): zero,
                        (1,): one,
                        (2,): variables[anchor],
                    }

                suffix = subcube_library(offset + 1)
                position = block_positions[offset]
                alphabet_size = len(_allowed_values(position, anchor))
                entries = tuple(suffix.items())
                result: dict[tuple[int, ...], Expr] = {}
                for choices in product(entries, repeat=alphabet_size):
                    word = tuple(
                        value
                        for suffix_word, _ in choices
                        for value in suffix_word
                    )
                    branches = tuple(term for _, term in choices)
                    result[word] = select_position(position, branches)
                return result

            library = subcube_library(0)
            _require(
                len(library) == 3 ** len(block_points),
                "subcube library function census drift",
            )

        values: list[int | None] = [None] * arity
        values[anchor] = 2

        def select_prefix(offset: int) -> Expr:
            if offset == len(prefix_positions):
                output_vector = []
                for block_point in block_points:
                    for position, value in zip(
                        block_positions,
                        block_point,
                        strict=True,
                    ):
                        values[position] = value
                    point = tuple(int(value) for value in values)
                    output_vector.append(point[selector_indices[point]])
                return library[tuple(output_vector)]

            position = prefix_positions[offset]
            branches = []
            for value in _allowed_values(position, anchor):
                values[position] = value
                branches.append(select_prefix(offset + 1))
            values[position] = None
            return select_position(position, tuple(branches))

        return select_prefix(0)

    slice_terms = tuple(slice_circuit(plan) for plan in plans)

    def first_nonbinary(position: int) -> Expr:
        if position == arity:
            return binary
        return normal_selector(
            u2(variables[position]),
            variables[position],
            first_nonbinary(position + 1),
            slice_terms[position],
        )

    return first_nonbinary(0)


def compile_global_subcube_coordinate_selector(
    arity: int,
    selector_indices: Mapping[tuple[int, ...], int],
    *,
    block_assignment_cap: int | None = None,
) -> Expr:
    """Compile through one balanced global nonbinary anchor.

    A balanced ``absorbing_two`` fold is 2 exactly when some input is 2.  On
    that branch it supplies dynamic names for 0, 1, and 2, allowing one global
    recursive-subcube library.  ``shallow_ternary_selector`` then spends three
    branch-dependency levels per input coordinate.
    """

    _require(arity >= 1, "arity must be positive")
    points = tuple(product(Q, repeat=arity))
    _require(set(selector_indices) == set(points), "selector table is not total")
    _require(
        all(0 <= index < arity for index in selector_indices.values()),
        "selector index outside input arity",
    )
    for point in product((0, 1), repeat=arity):
        _require(
            selector_indices[point] == selector_indices[complement(point)],
            "binary selector indices are not complement-invariant",
        )

    variables = tuple(Var(index) for index in range(arity))
    anchor = balanced_absorbing_two(variables)
    zero = UnaryU(UnaryU(anchor))
    one = UnaryU(anchor)
    two = anchor

    def binary_tree(position: int, representative: tuple[int, ...]) -> Expr:
        if position == arity:
            return variables[selector_indices[representative]]
        return normal_selector(
            variables[position],
            variables[0],
            binary_tree(position + 1, representative + (0,)),
            binary_tree(position + 1, representative + (1,)),
        )

    binary = binary_tree(1, (0,))
    cap = (
        suggested_global_block_assignment_cap(arity)
        if block_assignment_cap is None
        else block_assignment_cap
    )
    block_positions = _global_block_positions(arity, cap)
    prefix_positions = tuple(
        position for position in range(arity) if position not in block_positions
    )
    block_points = tuple(product(Q, repeat=len(block_positions)))

    if not block_positions:
        block_points = ((),)
        library: dict[tuple[int, ...], Expr] = {
            (0,): zero,
            (1,): one,
            (2,): two,
        }
    else:
        def subcube_library(offset: int) -> dict[tuple[int, ...], Expr]:
            if offset == len(block_positions):
                return {
                    (0,): zero,
                    (1,): one,
                    (2,): two,
                }

            suffix = subcube_library(offset + 1)
            position = block_positions[offset]
            entries = tuple(suffix.items())
            result: dict[tuple[int, ...], Expr] = {}
            for choices in product(entries, repeat=3):
                word = tuple(
                    value
                    for suffix_word, _ in choices
                    for value in suffix_word
                )
                branches = tuple(term for _, term in choices)
                result[word] = shallow_ternary_selector(
                    variables[position],
                    zero,
                    one,
                    two,
                    branches[0],
                    branches[1],
                    branches[2],
                )
            return result

        library = subcube_library(0)
        _require(
            len(library) == 3 ** len(block_points),
            "global subcube library function census drift",
        )

    values: list[int | None] = [None] * arity

    def select_prefix(offset: int) -> Expr:
        if offset == len(prefix_positions):
            output_vector = []
            for block_point in block_points:
                for position, value in zip(
                    block_positions,
                    block_point,
                    strict=True,
                ):
                    values[position] = value
                point = tuple(int(value) for value in values)
                output_vector.append(point[selector_indices[point]])
            return library[tuple(output_vector)]

        position = prefix_positions[offset]
        branches = []
        for value in Q:
            values[position] = value
            branches.append(select_prefix(offset + 1))
        values[position] = None
        return shallow_ternary_selector(
            variables[position],
            zero,
            one,
            two,
            branches[0],
            branches[1],
            branches[2],
        )

    nonbinary = select_prefix(0)
    return normal_selector(zero, anchor, binary, nonbinary)

"""Compile Quackenbush-Q orbitwise coordinate selectors to parameter-free terms.

The fixed algebra is Q=({0,1,2}; d,u), with the usual discriminator ``d`` and
``u(0)=1, u(1)=0, u(2)=1``.  A selector table assigns every input tuple an
input-coordinate index.  On B={0,1}, the index must be invariant under bit
complement.  Nonbinary tuples have singleton internal-isomorphism orbits.

The compiler emits a shared DAG using only variables, u, and d.  Recursively
unsharing that DAG gives an ordinary original-signature term tree.  The helper
``expanded_tree_size`` counts that unshared syntax without materializing it.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import product

Q = (0, 1, 2)
B = frozenset((0, 1))


class Expr:
    """Base class for parameter-free Q-term DAG nodes."""


@dataclass(frozen=True)
class Var(Expr):
    index: int


@dataclass(frozen=True)
class UnaryU(Expr):
    value: Expr


@dataclass(frozen=True)
class Disc(Expr):
    """``d(x,y,z)=z`` when x=y, and x otherwise."""

    x: Expr
    y: Expr
    z: Expr


def normal_selector(
    x: Expr,
    y: Expr,
    when_equal: Expr,
    when_different: Expr,
) -> Expr:
    """Return ``when_equal`` iff x=y, using only the discriminator."""

    return Disc(
        Disc(x, y, when_equal),
        Disc(x, y, when_different),
        when_different,
    )


def unary_u(value: int) -> int:
    return {0: 1, 1: 0, 2: 1}[value]


def evaluate(expr: Expr, arguments: Sequence[int]) -> int:
    """Evaluate a compiled DAG, memoizing shared nodes by identity."""

    memo: dict[int, int] = {}

    def go(node: Expr) -> int:
        key = id(node)
        if key in memo:
            return memo[key]
        if isinstance(node, Var):
            if not 0 <= node.index < len(arguments):
                raise IndexError(node.index)
            result = arguments[node.index]
        elif isinstance(node, UnaryU):
            result = unary_u(go(node.value))
        elif isinstance(node, Disc):
            left = go(node.x)
            right = go(node.y)
            result = go(node.z) if left == right else left
        else:  # pragma: no cover - closed node hierarchy
            raise TypeError(type(node))
        memo[key] = result
        return result

    return go(expr)


def complement(values: tuple[int, ...]) -> tuple[int, ...]:
    if any(value not in B for value in values):
        raise ValueError("complement is defined only on B")
    return tuple(1 - value for value in values)


def compile_orbit_coordinate_selector(
    arity: int,
    selector_indices: Mapping[tuple[int, ...], int],
) -> Expr:
    """Compile an internal-isomorphism-invariant coordinate selector.

    ``selector_indices[x]=j`` means that the desired value at x is ``x[j]``.
    The complete table is required.  On binary tuples, complement partners
    must select the same coordinate index.
    """

    if arity < 1:
        raise ValueError("arity must be positive")
    points = tuple(product(Q, repeat=arity))
    if set(selector_indices) != set(points):
        raise ValueError("selector table is not total on Q^arity")
    if any(not 0 <= index < arity for index in selector_indices.values()):
        raise ValueError("selector index outside input arity")
    for point in product((0, 1), repeat=arity):
        if selector_indices[point] != selector_indices[complement(point)]:
            raise ValueError("binary selector indices are not complement-invariant")

    variables = tuple(Var(index) for index in range(arity))

    def u2(node: Expr) -> Expr:
        return UnaryU(UnaryU(node))

    def binary_tree(position: int, representative: tuple[int, ...]) -> Expr:
        # Fix x_0=0.  Equality/difference from x_0 identifies a complement
        # orbit, so the chosen index is valid for either orientation.
        if position == arity:
            return variables[selector_indices[representative]]
        return normal_selector(
            variables[position],
            variables[0],
            binary_tree(position + 1, representative + (0,)),
            binary_tree(position + 1, representative + (1,)),
        )

    binary = binary_tree(1, (0,))

    def exact_tree(anchor: int) -> Expr:
        # On the branch reaching this tree x_anchor=2.  Hence u^2(x_anchor),
        # u(x_anchor), and x_anchor dynamically name 0, 1, and 2.
        zero = u2(variables[anchor])
        one = UnaryU(variables[anchor])
        values: list[int | None] = [None] * arity
        values[anchor] = 2

        def classify(position: int) -> Expr:
            if position == arity:
                point = tuple(int(value) for value in values)
                return variables[selector_indices[point]]
            if position == anchor:
                return classify(position + 1)

            values[position] = 0
            branch_zero = classify(position + 1)
            values[position] = 1
            branch_one = classify(position + 1)
            if position < anchor:
                # Reaching anchor means every earlier coordinate already passed
                # the B-membership test, so its only alternatives are 0 and 1.
                values[position] = None
                return normal_selector(
                    variables[position], zero, branch_zero, branch_one
                )

            values[position] = 2
            branch_two = classify(position + 1)
            values[position] = None

            nonzero = normal_selector(
                variables[position], one, branch_one, branch_two
            )
            return normal_selector(
                variables[position], zero, branch_zero, nonzero
            )

        return classify(0)

    def first_nonbinary(position: int) -> Expr:
        if position == arity:
            return binary
        # u^2(x)=x exactly for x in B.  The first failure supplies value 2
        # as the dynamic anchor for an exact nonbinary-tuple classifier.
        return normal_selector(
            u2(variables[position]),
            variables[position],
            first_nonbinary(position + 1),
            exact_tree(position),
        )

    return first_nonbinary(0)


def distinct_node_count(expr: Expr) -> int:
    """Count shared DAG nodes by identity."""

    seen: set[int] = set()

    def visit(node: Expr) -> None:
        key = id(node)
        if key in seen:
            return
        seen.add(key)
        if isinstance(node, UnaryU):
            visit(node.value)
        elif isinstance(node, Disc):
            visit(node.x)
            visit(node.y)
            visit(node.z)

    visit(expr)
    return len(seen)


def expanded_tree_size(expr: Expr) -> int:
    """Count nodes after recursively unsharing to ordinary term syntax."""

    memo: dict[int, int] = {}

    def size(node: Expr) -> int:
        key = id(node)
        if key in memo:
            return memo[key]
        if isinstance(node, Var):
            result = 1
        elif isinstance(node, UnaryU):
            result = 1 + size(node.value)
        elif isinstance(node, Disc):
            result = 1 + size(node.x) + size(node.y) + size(node.z)
        else:  # pragma: no cover - closed node hierarchy
            raise TypeError(type(node))
        memo[key] = result
        return result

    return size(expr)


def expression_depth(expr: Expr) -> int:
    """Return expanded term-tree depth; sharing does not affect depth."""

    memo: dict[int, int] = {}

    def depth(node: Expr) -> int:
        key = id(node)
        if key in memo:
            return memo[key]
        if isinstance(node, Var):
            result = 1
        elif isinstance(node, UnaryU):
            result = 1 + depth(node.value)
        elif isinstance(node, Disc):
            result = 1 + max(depth(node.x), depth(node.y), depth(node.z))
        else:  # pragma: no cover - closed node hierarchy
            raise TypeError(type(node))
        memo[key] = result
        return result

    return depth(expr)

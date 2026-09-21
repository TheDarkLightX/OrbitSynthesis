"""Compile arbitrary finite truth tables to parameterized discriminator terms.

For a finite quasi-primal algebra the ternary discriminator is an original-
signature term operation. Once carrier elements may be named as synthesis-time
constants, nested discriminator selectors represent every finite function.

This module is deliberately independent of any concrete algebra operations
other than discriminator semantics. It represents the compiled expression as a
shared Python object DAG; serialization/minimization are separate concerns.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Generic, Hashable, Mapping, Sequence, TypeVar

T = TypeVar("T", bound=Hashable)


class Expr(Generic[T]):
    """Base class for discriminator-expression DAG nodes."""


@dataclass(frozen=True)
class Var(Expr[T]):
    index: int


@dataclass(frozen=True)
class Const(Expr[T]):
    value: T


@dataclass(frozen=True)
class Disc(Expr[T]):
    """d(x,y,z) = z when x=y, otherwise x."""

    x: Expr[T]
    y: Expr[T]
    z: Expr[T]


def selector(
    x: Expr[T],
    y: Expr[T],
    when_equal: Expr[T],
    when_different: Expr[T],
) -> Expr[T]:
    """Derived if-then-else from the discriminator.

    Returns ``when_equal`` when x=y and ``when_different`` otherwise.

    N(x,y,u,v) = d(d(x,y,u), d(x,y,v), v).
    """

    return Disc(
        Disc(x, y, when_equal),
        Disc(x, y, when_different),
        when_different,
    )


def evaluate(expr: Expr[T], arguments: Sequence[T]) -> T:
    """Evaluate a compiled expression under standard discriminator semantics."""

    memo: dict[int, T] = {}

    def go(node: Expr[T]) -> T:
        key = id(node)
        if key in memo:
            return memo[key]

        if isinstance(node, Var):
            if not 0 <= node.index < len(arguments):
                raise IndexError(f"variable {node.index} outside {len(arguments)} arguments")
            value = arguments[node.index]
        elif isinstance(node, Const):
            value = node.value
        elif isinstance(node, Disc):
            left = go(node.x)
            right = go(node.y)
            value = go(node.z) if left == right else left
        else:  # pragma: no cover - closed node hierarchy
            raise TypeError(type(node))

        memo[key] = value
        return value

    return go(expr)


def _guard_tuple(
    point: tuple[T, ...],
    value: T,
    fallback: Expr[T],
) -> Expr[T]:
    """Return ``value`` exactly at point, otherwise fallback."""

    branch: Expr[T] = Const(value)
    for index in range(len(point) - 1, -1, -1):
        branch = selector(
            Var(index),
            Const(point[index]),
            branch,
            fallback,
        )
    return branch


def compile_table(
    carrier: Sequence[T],
    arity: int,
    table: Mapping[tuple[T, ...], T],
) -> Expr[T]:
    """Compile one complete scalar truth table.

    ``table`` must contain exactly every point in ``carrier ** arity``.
    Carrier values become named constants in the resulting expression.
    """

    if arity < 0:
        raise ValueError("arity must be nonnegative")
    carrier_tuple = tuple(carrier)
    if not carrier_tuple:
        raise ValueError("carrier must be nonempty")
    if len(set(carrier_tuple)) != len(carrier_tuple):
        raise ValueError("carrier values must be distinct")

    points = tuple(product(carrier_tuple, repeat=arity))
    expected = set(points)
    actual = set(table)
    if actual != expected:
        missing = expected - actual
        extra = actual - expected
        raise ValueError(f"truth table mismatch: missing={len(missing)} extra={len(extra)}")
    if any(value not in expected_carrier for value in table.values() for expected_carrier in [set(carrier_tuple)]):
        raise ValueError("truth table output outside carrier")

    # The final point supplies a default; every earlier point overrides it by
    # an exact tuple guard. This is a DAG because fallback nodes are shared.
    fallback: Expr[T] = Const(table[points[-1]])
    for point in reversed(points[:-1]):
        fallback = _guard_tuple(point, table[point], fallback)
    return fallback


def compile_vector_table(
    carrier: Sequence[T],
    input_arity: int,
    output_arity: int,
    table: Mapping[tuple[T, ...], tuple[T, ...]],
) -> tuple[Expr[T], ...]:
    """Compile a complete vector-valued controller table coordinatewise."""

    if output_arity < 0:
        raise ValueError("output_arity must be nonnegative")

    scalar_tables: list[dict[tuple[T, ...], T]] = [dict() for _ in range(output_arity)]
    for point, output in table.items():
        if len(output) != output_arity:
            raise ValueError("controller output has wrong arity")
        for coordinate, value in enumerate(output):
            scalar_tables[coordinate][point] = value

    return tuple(
        compile_table(carrier, input_arity, scalar_table)
        for scalar_table in scalar_tables
    )


def distinct_node_count(expr: Expr[T]) -> int:
    """Count shared DAG nodes by identity."""

    seen: set[int] = set()

    def visit(node: Expr[T]) -> None:
        key = id(node)
        if key in seen:
            return
        seen.add(key)
        if isinstance(node, Disc):
            visit(node.x)
            visit(node.y)
            visit(node.z)

    visit(expr)
    return len(seen)

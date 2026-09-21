"""Exact minimal-core family construction for finite pure discriminator algebras."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import comb
from typing import Hashable, Iterable, Mapping, Sequence

from .discriminator_core import is_parameter_polynomial_table

Value = Hashable
Row = tuple[Value, Value]


@dataclass(frozen=True)
class CoreFamilyRealization:
    family: tuple[frozenset[Value], ...]
    common_core: frozenset[Value]
    complement_blocks: tuple[frozenset[Value], ...]
    table_items: tuple[tuple[Row, Value], ...]

    @property
    def table(self) -> dict[Row, Value]:
        return dict(self.table_items)


def _carrier(carrier: Sequence[Value]) -> tuple[Value, ...]:
    values = tuple(carrier)
    if not values or len(values) != len(set(values)):
        raise ValueError("carrier must be finite, nonempty, and duplicate-free")
    return values


def _subset_key(subset: frozenset[Value], values: tuple[Value, ...]):
    return tuple(index for index, value in enumerate(values) if value in subset)


def canonical_core_family(carrier: Sequence[Value], family: Iterable[Iterable[Value]]):
    values = _carrier(carrier)
    whole = frozenset(values)
    cores = tuple(frozenset(core) for core in family)
    if not cores:
        raise ValueError("minimal-core family must be nonempty")
    if len(set(cores)) != len(cores) or any(not core <= whole for core in cores):
        raise ValueError("family contains a duplicate or an element outside the carrier")
    if any(left < right or right < left for left, right in combinations(cores, 2)):
        raise ValueError("family must be an antichain")
    return tuple(sorted(cores, key=lambda core: _subset_key(core, values)))


def is_pairwise_cover_antichain(carrier: Sequence[Value], family: Iterable[Iterable[Value]]):
    try:
        cores = canonical_core_family(carrier, family)
    except ValueError:
        return False
    whole = frozenset(_carrier(carrier))
    return all(left | right == whole for left, right in combinations(cores, 2))


def all_subsets(carrier: Sequence[Value]):
    values = _carrier(carrier)
    return tuple(
        frozenset(value for index, value in enumerate(values) if mask & (1 << index))
        for mask in range(1 << len(values))
    )


def foreign_output_core(carrier: Sequence[Value], table: Mapping[Row, Value]):
    values = _carrier(carrier)
    rows = tuple(product(values, repeat=2))
    return frozenset(table[row] for row in rows if table[row] not in row)


def minimal_parameter_cores(carrier: Sequence[Value], table: Mapping[Row, Value]):
    values = _carrier(carrier)
    feasible = tuple(
        core for core in all_subsets(values)
        if is_parameter_polynomial_table(values, core, 2, table)
    )
    return tuple(
        core for core in feasible
        if not any(other < core for other in feasible)
    )


def realize_minimal_core_family(
    carrier: Sequence[Value],
    family: Iterable[Iterable[Value]],
) -> CoreFamilyRealization:
    values = _carrier(carrier)
    whole = frozenset(values)
    cores = canonical_core_family(values, family)
    if not all(left | right == whole for left, right in combinations(cores, 2)):
        raise ValueError("distinct desired cores must pairwise cover the carrier")

    common = frozenset.intersection(*cores)
    blocks = tuple(whole - core for core in cores)
    block_of = {
        value: index
        for index, block in enumerate(blocks)
        for value in block
    }

    table: dict[Row, Value] = {}
    for left, right in product(values, repeat=2):
        left_block = block_of.get(left)
        right_block = block_of.get(right)
        if (
            left_block is not None
            and right_block is not None
            and left_block != right_block
        ):
            table[(left, right)] = left if left_block < right_block else right
        else:
            table[(left, right)] = left

    common_values = tuple(value for value in values if value in common)
    if len(common_values) >= 2:
        for index, value in enumerate(common_values):
            table[(value, value)] = common_values[(index + 1) % len(common_values)]
    elif len(common_values) == 1:
        named = common_values[0]
        anonymous = tuple(value for value in values if value != named)
        if not anonymous:
            raise ValueError(
                "on a one-element carrier the unique operation is parameter-free"
            )
        for value in anonymous:
            table[(value, value)] = named

    return CoreFamilyRealization(
        family=cores,
        common_core=common,
        complement_blocks=blocks,
        table_items=tuple((row, table[row]) for row in product(values, repeat=2)),
    )


def set_partitions(items: Sequence[Value]):
    partitions: list[tuple[frozenset[Value], ...]] = [()]
    for value in items:
        next_rows = []
        for partition in partitions:
            next_rows.append(partition + (frozenset({value}),))
            for index in range(len(partition)):
                next_rows.append(
                    partition[:index]
                    + (partition[index] | {value},)
                    + partition[index + 1 :]
                )
        partitions = next_rows
    return tuple(partitions)


def pairwise_cover_families(carrier: Sequence[Value]):
    values = _carrier(carrier)
    whole = frozenset(values)
    families = [(core,) for core in all_subsets(values)]
    for active in all_subsets(values):
        if len(active) < 2:
            continue
        ordered = tuple(value for value in values if value in active)
        for partition in set_partitions(ordered):
            if len(partition) < 2:
                continue
            families.append(tuple(whole - block for block in partition))
    return tuple(canonical_core_family(values, family) for family in families)


def stirling_second(n: int, k: int) -> int:
    if n < 0 or k < 0:
        raise ValueError("indices must be nonnegative")
    rows = [[0] * (k + 1) for _ in range(n + 1)]
    rows[0][0] = 1
    for size in range(1, n + 1):
        for blocks in range(1, min(size, k) + 1):
            rows[size][blocks] = (
                rows[size - 1][blocks - 1]
                + blocks * rows[size - 1][blocks]
            )
    return rows[n][k]


def bell_number(n: int) -> int:
    return sum(stirling_second(n, k) for k in range(n + 1))


def realizable_family_count(carrier_size: int) -> int:
    if carrier_size < 1:
        raise ValueError("carrier size must be positive")
    if carrier_size == 1:
        return 1
    return 2 ** carrier_size + sum(
        comb(carrier_size, size) * (bell_number(size) - 1)
        for size in range(2, carrier_size + 1)
    )


def family_size_distribution(carrier_size: int):
    if carrier_size < 1:
        raise ValueError("carrier size must be positive")
    if carrier_size == 1:
        return {1: 1}
    result = {1: 2 ** carrier_size}
    for blocks in range(2, carrier_size + 1):
        result[blocks] = sum(
            comb(carrier_size, size) * stirling_second(size, blocks)
            for size in range(blocks, carrier_size + 1)
        )
    return result

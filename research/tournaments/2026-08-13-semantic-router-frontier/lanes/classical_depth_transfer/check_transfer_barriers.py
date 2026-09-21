#!/usr/bin/env python3
"""Finite falsifiers for the Gashkov-to-{d,u} transfer analysis.

This checker does not prove Gashkov's asymptotic theorem.  It checks only the
finite algebraic bridges and the exact change-of-alphabet arithmetic used in
the accompanying report.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    return (1, 0, 1)[x]


def majority(x: int, y: int, z: int) -> int:
    return int(x + y + z >= 2)


def encoded(a: int, bit: int) -> int:
    """Boolean bit represented relative to orientation a."""

    return a ^ bit


def truth_table(fn) -> tuple[int, ...]:
    return tuple(fn(*row) for row in itertools.product((0, 1), repeat=3))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def depth_one_boolean_functions() -> set[tuple[int, ...]]:
    """One {d,u} node fed by literals/constants, plus direct leaves."""

    rows = tuple(itertools.product((0, 1), repeat=3))
    leaves: list[tuple[int, ...]] = []
    for index in range(3):
        variable = tuple(row[index] for row in rows)
        leaves.append(variable)
        leaves.append(tuple(1 - value for value in variable))
    leaves.append((0,) * len(rows))
    leaves.append((1,) * len(rows))

    functions = set(leaves)
    functions.update(tuple(u(value) for value in leaf) for leaf in leaves)
    for left, middle, right in itertools.product(leaves, repeat=3):
        functions.add(
            tuple(d(left[i], middle[i], right[i]) for i in range(len(rows)))
        )
    return functions


def main() -> None:
    boolean_rows = tuple(itertools.product((0, 1), repeat=3))

    require(
        all(d(x, y, z) == majority(x, 1 - y, z) for x, y, z in boolean_rows),
        "Boolean discriminator identity failed",
    )
    require(all(u(1 - x) == 1 - u(x) for x in (0, 1)), "u is not self-dual")
    require(
        all(
            d(1 - x, 1 - y, 1 - z) == 1 - d(x, y, z)
            for x, y, z in boolean_rows
        ),
        "d is not self-dual",
    )

    relative_rows = 0
    for a, x, y in itertools.product((0, 1), repeat=3):
        ex, ey = encoded(a, x), encoded(a, y)
        require(u(ex) == encoded(a, 1 - x), "relative NOT failed")
        require(d(ex, u(a), ey) == encoded(a, x & y), "relative AND failed")
        require(d(ex, a, ey) == encoded(a, x | y), "relative OR failed")
        relative_rows += 1

    anchor = 2
    one = u(anchor)
    zero = u(one)
    require((zero, one, anchor) == (0, 1, 2), "anchor names failed")
    absolute_rows = 0
    for x, y in itertools.product((0, 1), repeat=2):
        require(d(x, one, y) == (x & y), "absolute AND failed")
        require(d(x, zero, y) == (x | y), "absolute OR failed")
        require(u(x) == 1 - x, "absolute NOT failed")
        absolute_rows += 1

    depth_one = depth_one_boolean_functions()
    and3 = truth_table(lambda x, y, z: x & y & z)
    parity3 = truth_table(lambda x, y, z: x ^ y ^ z)
    require(and3 not in depth_one, "depth-one grammar unexpectedly has AND3")
    require(parity3 not in depth_one, "depth-one grammar unexpectedly has parity3")

    alphabet_rows = []
    for r in (16, 64, 256, 1024):
        dense_bits = (pow(3, r) - 1).bit_length()
        log2_formula_ratio = (
            dense_bits
            - math.log2(math.log2(dense_bits))
            - r * math.log2(3)
            + math.log2(r)
        )
        alphabet_rows.append(
            {
                "r": r,
                "minimum_dense_bits": dense_bits,
                "dense_bits_over_r": round(dense_bits / r, 12),
                "log2_formula_size_over_3^r_over_r": round(
                    log2_formula_ratio, 12
                ),
            }
        )

    semantic = {
        "absolute_boolean_gate_rows": absolute_rows,
        "all_binary_generator_self_duality": True,
        "boolean_d_is_majority_x_not_y_z_rows": len(boolean_rows),
        "depth_one_function_count_with_literals_and_constants": len(depth_one),
        "depth_one_has_and3": and3 in depth_one,
        "depth_one_has_parity3": parity3 in depth_one,
        "dense_encoding_diagnostics": alphabet_rows,
        "relative_gate_rows": relative_rows,
    }
    canonical = json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "schema": "orbit.classical_depth_transfer.check.v1",
        "semantic": semantic,
        "semantic_sha256": hashlib.sha256(canonical).hexdigest(),
        "status": "PASS",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Finite-state closure oracle for the direct-Q read-once path barrier."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = (0, 1, 2)


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    return (1, 0, 1)[x]


def build_receipt() -> dict[str, object]:
    # A state is the unary truth table induced by the distinguished payload and
    # whether its unique root path has used only left/right discriminator edges.
    states: set[tuple[tuple[int, int, int], bool]] = {((0, 1, 2), True)}
    layer_sizes: list[int] = []

    while True:
        layer_sizes.append(len(states))
        expanded = set(states)
        for table, outer_only in states:
            expanded.add((tuple(u(value) for value in table), False))
            for left_constant in Q:
                for right_constant in Q:
                    expanded.add((
                        tuple(d(value, left_constant, right_constant) for value in table),
                        outer_only,
                    ))
                    expanded.add((
                        tuple(d(left_constant, value, right_constant) for value in table),
                        False,
                    ))
                    expanded.add((
                        tuple(d(left_constant, right_constant, value) for value in table),
                        outer_only,
                    ))
        if expanded == states:
            break
        states = expanded

    bad_surjections = sorted(
        table for table, outer_only in states
        if not outer_only and len(set(table)) == 3
    )
    good_functions = {table for table, outer_only in states if outer_only}
    bad_functions = {table for table, outer_only in states if not outer_only}

    if bad_surjections:
        raise AssertionError(f"bad path retained a surjection: {bad_surjections}")
    if layer_sizes != [1, 19, 37, 43]:
        raise AssertionError(f"closure layer drift: {layer_sizes}")

    result: dict[str, object] = {
        "theorem": "direct-Q read-once payload paths with unary/middle edges are nonsurjective",
        "status": "exact finite unary-function closure",
        "closure_layers": layer_sizes,
        "fixed_point_states": len(states),
        "outer_only_functions": len(good_functions),
        "bad_path_functions": len(bad_functions),
        "bad_path_surjections": len(bad_surjections),
        "capacity_consequence": "q<=2^h for depth-h read-once direct-Q routers",
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(encoded).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_receipt(), sort_keys=True, indent=2) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

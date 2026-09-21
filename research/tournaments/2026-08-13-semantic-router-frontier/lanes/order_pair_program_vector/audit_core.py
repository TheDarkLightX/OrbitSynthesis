"""Verification routines for the order-pair program-vector construction."""

from __future__ import annotations
from order_pair_model import (
    build_vector, d, expected_pair, output_lower_bound,
    summary_nodes, vector_depth, vector_nodes, words,
)


def verify_monoid() -> int:
    states = {"E": (0, 0), "L": (1, 0), "G": (0, 1)}
    checks = 0
    for an, (al, ag) in states.items():
        for bn, (bl, bg) in states.items():
            expected = states[bn if an == "E" else an]
            actual = (d(al, ag, bl), d(ag, al, bg))
            if actual != expected:
                raise AssertionError(("monoid", an, bn, actual))
            checks += 1
    if states["L"][1] | states["G"][1] != 1:
        raise AssertionError("mutation did not fire")
    return checks + 1


def verify_materialization(max_width: int):
    rows, cases = [], 0
    for width in range(1, max_width + 1):
        q = 3**width
        for root_negative in (False, True):
            dag, outputs, size, depth = build_vector(width, root_negative)
            if size != vector_nodes(width, root_negative):
                raise AssertionError(("size", width, root_negative, size))
            if depth > vector_depth(width):
                raise AssertionError(("depth", width, root_negative, depth))
            for target in words(width):
                values, inputs = dag.evaluate(target)
                for physical, pair in outputs.items():
                    got = tuple(dag.value(root, values, inputs) for root in pair)
                    want = expected_pair(target, physical, root_negative)
                    if got != want:
                        raise AssertionError(
                            ("semantics", width, root_negative,
                             target, physical, got, want)
                        )
                    cases += 1
            rows.append({
                "width": width, "q": q,
                "root": "negative" if root_negative else "positive",
                "nodes": size, "depth": depth,
                "depth_bound": vector_depth(width),
            })
    return rows, cases


def first_gain(target, physical) -> bool:
    if target == physical:
        return False
    for x, p in zip(target, physical):
        if x != p:
            return x == 1 and p == 2
    raise AssertionError("unreachable")


def verify_lower_bound(max_width: int):
    rows = []
    for width in range(2, max_width + 1):
        ws = words(width)
        q = 3**width
        gain_tables = {
            p: tuple(int(first_gain(t, p)) for t in ws)
            for p in ws
        }
        if len(set(gain_tables.values())) != (q + 1) // 2:
            raise AssertionError(("gain classes", width))
        for root_negative in (False, True):
            tables = set()
            for p in ws:
                pairs = [expected_pair(t, p, root_negative) for t in ws]
                tables.add(tuple(pair[0] for pair in pairs))
                tables.add(tuple(pair[1] for pair in pairs))
            tables.discard((0,) * q)
            tables.discard((1,) * q)
            expected = output_lower_bound(width, root_negative)
            if len(tables) != expected:
                raise AssertionError(
                    ("lower bound", width, root_negative, len(tables))
                )
            rows.append({
                "width": width, "q": q,
                "root": "negative" if root_negative else "positive",
                "distinct_nonconstant_outputs": len(tables),
                "formula": expected,
            })
    return rows


def verify_arithmetic(max_width: int) -> int:
    checks = 0
    for width in range(1, max_width + 1):
        q = 3**width
        if 3 * summary_nodes(width) > 7 * q:
            raise AssertionError(("summary bound", width))
        for root_negative in (False, True):
            count = vector_nodes(width, root_negative)
            if 2 * count > 5 * q - 1:
                raise AssertionError(("uniform bound", width, root_negative))
            if width >= 2 and count < output_lower_bound(width, root_negative):
                raise AssertionError(("construction below lower bound", width))
            checks += 3
        if width >= 2:
            if vector_nodes(width, True) != vector_nodes(width, False) + 1:
                raise AssertionError(("sign gap", width))
            checks += 1
    return checks

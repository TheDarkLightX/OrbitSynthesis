#!/usr/bin/env python3
"""No-import audit of emitted compiler-portfolio bundles."""

from __future__ import annotations

import hashlib
from itertools import product
import json
from pathlib import Path
import sys


def canonical_hash(payload) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def without(payload, key):
    return {name: value for name, value in payload.items() if name != key}


def algebra(problem):
    carrier = tuple(problem["algebra"]["carrier"])
    operations = {}
    for row in problem["algebra"]["operations"]:
        points = tuple(product(carrier, repeat=row["arity"]))
        operations[row["name"]] = {
            point: output
            for point, output in zip(points, row["outputs"], strict=True)
        }
    return carrier, operations


def strategy(bundle):
    return {
        tuple(row["observation"]): tuple(row["output"])
        for row in bundle["proof_bundle"]["result"]["strategy"]
    }


def verify_hashes(bundle):
    assert canonical_hash(without(bundle, "manifest_sha256")) == bundle["manifest_sha256"]
    proof = bundle["proof_bundle"]
    assert canonical_hash(without(proof, "manifest_sha256")) == proof["manifest_sha256"]
    portfolio = bundle["compiler_portfolio"]
    assert canonical_hash(without(portfolio, "semantic_sha256")) == portfolio["semantic_sha256"]


def evaluate_dag(problem, implementation, arguments):
    carrier, operations = algebra(problem)
    dag = implementation["dag"]
    values = []

    def value(reference):
        if reference["kind"] == "input":
            assert 0 <= reference["index"] < len(arguments)
            return arguments[reference["index"]]
        assert reference["kind"] == "node"
        assert 0 <= reference["index"] < len(values)
        return values[reference["index"]]

    reachable = set()

    def visit(reference):
        if reference["kind"] == "input":
            return
        index = reference["index"]
        if index in reachable:
            return
        reachable.add(index)
        for argument in dag["nodes"][index]["arguments"]:
            visit(argument)

    for index, node in enumerate(dag["nodes"]):
        name = node["operation"]
        assert name in operations
        arity = next(
            row["arity"]
            for row in problem["algebra"]["operations"]
            if row["name"] == name
        )
        assert len(node["arguments"]) == arity
        assert all(
            argument["kind"] == "input"
            or (
                argument["kind"] == "node"
                and 0 <= argument["index"] < index
            )
            for argument in node["arguments"]
        )
        args = tuple(value(argument) for argument in node["arguments"])
        values.append(operations[name][args])
    for root in dag["roots"]:
        visit(root)
    assert reachable == set(range(len(dag["nodes"])))
    output = tuple(value(root) for root in dag["roots"])
    assert all(value in carrier for value in output)
    return output


def evaluate_mdd(problem, artifact, arguments):
    carrier = tuple(problem["algebra"]["carrier"])
    diagram = artifact["diagram"]
    order = tuple(diagram["variable_order"])
    assert len(order) == len(set(order))
    assert set(order) == set(range(diagram["input_arity"]))
    rank = {variable: index for index, variable in enumerate(order)}
    nodes = diagram["nodes"]
    terminals = diagram["terminals"]
    assert terminals
    assert len({tuple(row) for row in terminals}) == len(terminals)
    assert all(len(row) == diagram["output_arity"] for row in terminals)
    signatures = set()
    for index, node in enumerate(nodes):
        assert node["variable"] in rank
        assert len(node["children"]) == len(carrier)
        signature = (
            node["variable"],
            tuple((child["kind"], child["index"]) for child in node["children"]),
        )
        assert signature not in signatures
        signatures.add(signature)
        assert len(set(signature[1])) > 1
        for child in node["children"]:
            if child["kind"] == "terminal":
                assert 0 <= child["index"] < len(terminals)
            else:
                assert child["kind"] == "node"
                assert 0 <= child["index"] < index
                assert rank[nodes[child["index"]]["variable"]] > rank[node["variable"]]

    reachable_nodes = set()
    reachable_terminals = set()

    def visit(reference):
        if reference["kind"] == "terminal":
            assert 0 <= reference["index"] < len(terminals)
            reachable_terminals.add(reference["index"])
            return
        assert reference["kind"] == "node"
        assert 0 <= reference["index"] < len(nodes)
        if reference["index"] in reachable_nodes:
            return
        reachable_nodes.add(reference["index"])
        for child in nodes[reference["index"]]["children"]:
            visit(child)

    visit(diagram["root"])
    assert reachable_nodes == set(range(len(nodes)))
    assert reachable_terminals == set(range(len(terminals)))

    carrier_index = {value: index for index, value in enumerate(carrier)}
    reference = diagram["root"]
    while reference["kind"] == "node":
        node = nodes[reference["index"]]
        reference = node["children"][carrier_index[arguments[node["variable"]]]]
    return tuple(terminals[reference["index"]])


def check_bundle(path: Path, expected_backend: str | None):
    bundle = json.loads(path.read_text(encoding="utf-8"))
    verify_hashes(bundle)
    portfolio = bundle["compiler_portfolio"]
    proof = bundle["proof_bundle"]
    shannon = [
        attempt
        for attempt in portfolio["attempts"]
        if attempt["backend"] == "fixed-q-shannon-experimental"
    ]
    if proof["result"]["status"] == "infeasible":
        assert portfolio["status"] == "not_applicable"
        assert portfolio["selected_backend"] is None
        return {
            "status": "infeasible",
            "manifest_sha256": bundle["manifest_sha256"],
        }

    assert portfolio["status"] == "compiled"
    assert portfolio["selected_backend"] == expected_backend
    assert portfolio["selected_backend"] != "fixed-q-shannon-experimental"
    assert shannon and shannon[0]["status"] == "diagnostic"
    problem = proof["problem"]
    table = strategy(bundle)
    checked = 0
    if portfolio["selected_kind"] == "original_signature":
        implementation = portfolio["original_signature"]
        assert canonical_hash(without(implementation, "semantic_sha256")) == implementation["semantic_sha256"]
        dag = implementation["dag"]
        assert canonical_hash(without(dag, "semantic_sha256")) == dag["semantic_sha256"]
        for point, expected in table.items():
            assert evaluate_dag(problem, implementation, point) == expected
            checked += 1
        size = len(dag["nodes"])
    else:
        artifact = portfolio["mdd"]
        assert canonical_hash(without(artifact, "semantic_sha256")) == artifact["semantic_sha256"]
        diagram = artifact["diagram"]
        assert canonical_hash(without(diagram, "semantic_sha256")) == diagram["semantic_sha256"]
        for point, expected in table.items():
            assert evaluate_mdd(problem, artifact, point) == expected
            checked += 1
        size = len(diagram["nodes"])
    return {
        "status": "optimal",
        "backend": expected_backend,
        "kind": portfolio["selected_kind"],
        "rows_checked": checked,
        "implementation_nodes": size,
        "manifest_sha256": bundle["manifest_sha256"],
        "portfolio_sha256": portfolio["semantic_sha256"],
    }


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit(
            "usage: audit_portfolio_bundles.py DEFAULT STRUCTURAL MDD INFEASIBLE"
        )
    rows = [
        check_bundle(Path(sys.argv[1]), "exact-semantic-closure"),
        check_bundle(Path(sys.argv[2]), "fixed-q-structural-router"),
        check_bundle(Path(sys.argv[3]), "reduced-vector-mdd"),
        check_bundle(Path(sys.argv[4]), None),
    ]
    result = {
        "schema": "orbit-synthesis/compiler-portfolio-independent/v1",
        "rows": rows,
        "total_controller_rows_checked": sum(
            row.get("rows_checked", 0) for row in rows
        ),
    }
    result["semantic_sha256"] = canonical_hash(result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

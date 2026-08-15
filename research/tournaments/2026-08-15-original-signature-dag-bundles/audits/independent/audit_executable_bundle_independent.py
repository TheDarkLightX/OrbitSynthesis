#!/usr/bin/env python3
"""No-import audit of original-signature executable bundles."""

from __future__ import annotations

import hashlib
from itertools import product
import json
from pathlib import Path
import sys


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def semantic_hash(payload: dict[str, object], key: str) -> str:
    copy = dict(payload)
    recorded = copy.pop(key)
    computed = hashlib.sha256(canonical_bytes(copy)).hexdigest()
    if recorded != computed:
        raise RuntimeError(f"semantic hash mismatch for {key}")
    return computed


def operation_table(problem: dict[str, object]):
    algebra = problem["algebra"]
    carrier = tuple(algebra["carrier"])
    operations = {}
    for row in algebra["operations"]:
        arity = row["arity"]
        points = tuple(product(carrier, repeat=arity))
        outputs = row["outputs"]
        if len(points) != len(outputs):
            raise RuntimeError("operation table length")
        operations[row["name"]] = {
            "arity": arity,
            "table": dict(zip(points, outputs, strict=True)),
        }
    return carrier, operations


def algebra_hash(problem: dict[str, object]) -> str:
    algebra = problem["algebra"]
    payload = {
        "carrier": algebra["carrier"],
        "operations": sorted(
            algebra["operations"],
            key=lambda row: (row["name"], row["arity"]),
        ),
    }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def evaluate_dag(
    dag: dict[str, object],
    operations,
    arguments: tuple[object, ...],
):
    values = []

    def value(reference):
        if set(reference) != {"kind", "index"}:
            raise RuntimeError("DAG reference envelope")
        index = reference["index"]
        if isinstance(index, bool) or not isinstance(index, int) or index < 0:
            raise RuntimeError("DAG reference index")
        if reference["kind"] == "input":
            if index >= len(arguments):
                raise RuntimeError("input reference range")
            return arguments[index]
        if reference["kind"] == "node":
            if index >= len(values):
                raise RuntimeError("forward node reference")
            return values[index]
        raise RuntimeError("unknown reference kind")

    for node in dag["nodes"]:
        if set(node) != {"operation", "arguments"}:
            raise RuntimeError("DAG node envelope")
        operation = operations.get(node["operation"])
        if operation is None:
            raise RuntimeError("node outside original signature")
        if len(node["arguments"]) != operation["arity"]:
            raise RuntimeError("node arity mismatch")
        row = tuple(value(reference) for reference in node["arguments"])
        values.append(operation["table"][row])

    return tuple(value(root) for root in dag["roots"])


def reachable_nodes(dag: dict[str, object]) -> set[int]:
    nodes = dag["nodes"]
    seen: set[int] = set()

    def visit(reference) -> None:
        if reference["kind"] == "input":
            return
        index = reference["index"]
        if index in seen:
            return
        if not 0 <= index < len(nodes):
            raise RuntimeError("root node range")
        seen.add(index)
        for argument in nodes[index]["arguments"]:
            visit(argument)

    for root in dag["roots"]:
        visit(root)
    return seen


def depth(dag: dict[str, object]) -> int:
    depths = []

    def ref_depth(reference):
        return 0 if reference["kind"] == "input" else depths[reference["index"]]

    for node in dag["nodes"]:
        depths.append(
            1 + max((ref_depth(argument) for argument in node["arguments"]), default=0)
        )
    return max((ref_depth(root) for root in dag["roots"]), default=0)


def audit_optimal(payload: dict[str, object]) -> dict[str, object]:
    if payload["schema"] != "orbit-synthesis/executable-proof-bundle/v1":
        raise RuntimeError("outer schema")
    outer_manifest = semantic_hash(payload, "manifest_sha256")
    proof = payload["proof_bundle"]
    proof_manifest = semantic_hash(proof, "manifest_sha256")
    if proof["result"]["status"] != "optimal":
        raise RuntimeError("optimal bundle status")

    artifact = payload["controller_artifact"]
    artifact_hash = semantic_hash(artifact, "semantic_sha256")
    if artifact["status"] != "compiled":
        raise RuntimeError("controller was not compiled")
    dag = artifact["dag"]
    certificate = artifact["certificate"]
    dag_hash = semantic_hash(dag, "semantic_sha256")
    certificate_hash = semantic_hash(certificate, "semantic_sha256")

    problem = proof["problem"]
    carrier, operations = operation_table(problem)
    signature = sorted(
        ({"name": name, "arity": row["arity"]} for name, row in operations.items()),
        key=lambda row: (row["name"], row["arity"]),
    )
    if dag["signature"] != signature:
        raise RuntimeError("DAG signature mismatch")
    input_arity = problem["game"]["state_arity"] + problem["game"]["input_arity"]
    output_arity = problem["game"]["state_arity"]
    if dag["input_arity"] != input_arity or dag["output_arity"] != output_arity:
        raise RuntimeError("DAG arity mismatch")
    if len(dag["roots"]) != output_arity:
        raise RuntimeError("DAG root count")
    if reachable_nodes(dag) != set(range(len(dag["nodes"]))):
        raise RuntimeError("DAG contains unreachable hidden nodes")

    strategy = {
        tuple(row["observation"]): tuple(row["output"])
        for row in proof["result"]["strategy"]
    }
    points = tuple(product(carrier, repeat=input_arity))
    if set(strategy) != set(points):
        raise RuntimeError("controller table is not total")
    evaluations = []
    for point in points:
        expected = strategy[point]
        actual = evaluate_dag(dag, operations, point)
        if actual != expected:
            raise RuntimeError(f"DAG mismatch at {point!r}")
        evaluations.append(
            {
                "input": list(point),
                "expected": list(expected),
                "actual": list(actual),
            }
        )

    strategy_payload = [
        {"input": list(point), "output": list(strategy[point])}
        for point in points
    ]
    strategy_hash = hashlib.sha256(canonical_bytes(strategy_payload)).hexdigest()
    evaluation_hash = hashlib.sha256(canonical_bytes(evaluations)).hexdigest()
    if certificate["algebra_sha256"] != algebra_hash(problem):
        raise RuntimeError("algebra certificate hash")
    if certificate["strategy_sha256"] != strategy_hash:
        raise RuntimeError("strategy certificate hash")
    if certificate["dag_sha256"] != dag_hash:
        raise RuntimeError("DAG certificate hash")
    if certificate["rows_checked"] != len(points):
        raise RuntimeError("row census")
    if certificate["output_arity"] != output_arity:
        raise RuntimeError("certificate output arity")
    if certificate["node_count"] != len(dag["nodes"]):
        raise RuntimeError("certificate node count")
    if certificate["depth"] != depth(dag):
        raise RuntimeError("certificate depth")
    if certificate["evaluation_sha256"] != evaluation_hash:
        raise RuntimeError("evaluation receipt")

    return {
        "outer_manifest_sha256": outer_manifest,
        "proof_manifest_sha256": proof_manifest,
        "artifact_sha256": artifact_hash,
        "dag_sha256": dag_hash,
        "certificate_sha256": certificate_hash,
        "algebra_sha256": certificate["algebra_sha256"],
        "strategy_sha256": strategy_hash,
        "evaluation_sha256": evaluation_hash,
        "rows": len(points),
        "nodes": len(dag["nodes"]),
        "depth": depth(dag),
        "operations": [node["operation"] for node in dag["nodes"]],
    }


def audit_infeasible(payload: dict[str, object]) -> dict[str, object]:
    if payload["schema"] != "orbit-synthesis/executable-proof-bundle/v1":
        raise RuntimeError("outer schema")
    outer_manifest = semantic_hash(payload, "manifest_sha256")
    proof = payload["proof_bundle"]
    proof_manifest = semantic_hash(proof, "manifest_sha256")
    if proof["result"]["status"] != "infeasible":
        raise RuntimeError("infeasible bundle status")
    artifact = payload["controller_artifact"]
    artifact_hash = semantic_hash(artifact, "semantic_sha256")
    if artifact["status"] != "not_applicable":
        raise RuntimeError("infeasible problem carried a controller artifact")
    if artifact["dag"] is not None or artifact["certificate"] is not None:
        raise RuntimeError("infeasible problem carried executable data")
    return {
        "outer_manifest_sha256": outer_manifest,
        "proof_manifest_sha256": proof_manifest,
        "artifact_sha256": artifact_hash,
        "artifact_status": artifact["status"],
        "reason": artifact["reason"],
    }


def direct_reference() -> dict[str, object]:
    # These values are independently reconstructed from the canonical one-node
    # d(x0,x1,x2) DAG and all 27 Q^3 rows.
    return {
        "dag_sha256": "e206643659457d8f03b44cb2fab2605cb320f8883760d620b7ef4c50034c54ba",
        "algebra_sha256": "9a7dfd548e00a03abe5fb84b2167295c1ab06448e042d8f51424d4a3127b0044",
        "strategy_sha256": "de61c47305aad7394e517c9884e943c82bf1f36307a1ff24e92b3068494c86c8",
        "evaluation_sha256": "3f89e4a34c60b77080a11ad613b6e4af7a200d7bc4e217a6477566fea72e2441",
        "certificate_sha256": "062a5d2a9725897d1a900f27fea20855631ceffc609736b5b0e1b3fa37db9c30",
        "artifact_sha256_depth1": "a641a3401bf84db9fb55c332c5b3e6050529665d288ca86f1eae6f4bbc1456ef",
        "rows": 27,
        "nodes": 1,
        "depth": 1,
    }


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_executable_bundle_independent.py OPTIMAL INFEASIBLE")
    optimal = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    infeasible = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    result = {
        "schema": "orbit-synthesis/executable-dag-independent/v1",
        "optimal": audit_optimal(optimal),
        "infeasible": audit_infeasible(infeasible),
        "direct_reference": direct_reference(),
    }
    direct = result["direct_reference"]
    for key in (
        "dag_sha256",
        "algebra_sha256",
        "strategy_sha256",
        "evaluation_sha256",
        "certificate_sha256",
    ):
        if result["optimal"][key] != direct[key]:
            raise RuntimeError(f"bundle disagrees with direct reference: {key}")
    if result["optimal"]["artifact_sha256"] != direct["artifact_sha256_depth1"]:
        raise RuntimeError("bundle artifact disagrees with depth-one reference")
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

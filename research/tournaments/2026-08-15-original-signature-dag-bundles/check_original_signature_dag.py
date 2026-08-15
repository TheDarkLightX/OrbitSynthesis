#!/usr/bin/env python3
"""Exact source-grounded gate for original-signature DAG bundles."""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.executable_bundle import (
    ExecutableProofBundle,
    synthesize_executable_bundle,
    verify_executable_bundle,
)
from orbitsynthesis.original_signature_dag import (
    CompilationLimits,
    DagReference,
    OriginalSignatureNode,
    compile_controller_artifact,
    verify_controller_artifact,
)
from orbitsynthesis.problem_io import FiniteSafetyProblem
from orbitsynthesis.structural_benchmarks import quackenbush_q


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def row(bundle: ExecutableProofBundle) -> dict[str, object]:
    proof = bundle.proof_bundle
    artifact = bundle.controller_artifact
    return {
        "problem": proof.problem.name,
        "status": proof.status,
        "backend": proof.backend,
        "domain": (
            None
            if proof.domain is None
            else [list(state) for state in sorted(proof.domain, key=repr)]
        ),
        "signed_utility": proof.signed_utility,
        "strategy_rows": len(proof.strategy_items),
        "proof_manifest_sha256": proof.manifest_sha256,
        "executable_manifest_sha256": bundle.manifest_sha256,
        "artifact_status": artifact.status,
        "artifact_reason": artifact.reason,
        "artifact_sha256": artifact.semantic_sha256,
        "dag_sha256": None if artifact.dag is None else artifact.dag.semantic_sha256,
        "dag_nodes": None if artifact.dag is None else len(artifact.dag.nodes),
        "dag_depth": (
            None if artifact.certificate is None else artifact.certificate.depth
        ),
        "equivalence_sha256": (
            None
            if artifact.certificate is None
            else artifact.certificate.semantic_sha256
        ),
        "rows_checked": (
            None
            if artifact.certificate is None
            else artifact.certificate.rows_checked
        ),
        "compilation_statistics": artifact.statistics.as_dict(),
    }


def direct_compiler_checks() -> dict[str, object]:
    algebra = quackenbush_q()
    values = tuple(algebra.values)
    discriminator = next(
        operation for operation in algebra.operations if operation.name == "d"
    )
    unary = next(
        operation for operation in algebra.operations if operation.name == "u"
    )

    scalar_table = {
        point: (discriminator(*point),)
        for point in product(values, repeat=3)
    }
    scalar = compile_controller_artifact(
        algebra,
        input_arity=3,
        output_arity=1,
        table=scalar_table,
        limits=CompilationLimits(max_depth=1),
    )
    require(scalar.status == "compiled", "direct discriminator was not compiled")
    require(scalar.dag is not None and scalar.certificate is not None, "DAG")
    require(len(scalar.dag.nodes) == 1, "discriminator should use one node")
    require(scalar.dag.nodes[0].operation == "d", "wrong discriminator node")
    require(
        scalar.dag.nodes[0].arguments
        == (
            DagReference("input", 0),
            DagReference("input", 1),
            DagReference("input", 2),
        ),
        "wrong discriminator arguments",
    )

    vector_table = {
        point: (
            discriminator(*point),
            unary(discriminator(*point)),
        )
        for point in product(values, repeat=3)
    }
    vector = compile_controller_artifact(
        algebra,
        input_arity=3,
        output_arity=2,
        table=vector_table,
        limits=CompilationLimits(max_depth=2),
    )
    require(vector.status == "compiled", "shared two-output table was not compiled")
    require(vector.dag is not None and vector.certificate is not None, "vector DAG")
    require(len(vector.dag.nodes) == 2, "shared vector should use two nodes")
    require(
        [node.operation for node in vector.dag.nodes] == ["d", "u"],
        "shared vector did not expose d then u",
    )
    require(
        vector.dag.nodes[1].arguments == (DagReference("node", 0),),
        "u did not reuse the discriminator root",
    )

    projection_table = {
        point: (point[1],)
        for point in product(values, repeat=3)
    }
    projection = compile_controller_artifact(
        algebra,
        input_arity=3,
        output_arity=1,
        table=projection_table,
        limits=CompilationLimits(max_depth=1),
    )
    require(projection.status == "compiled", "projection was not compiled")
    require(projection.dag is not None, "projection DAG")
    require(not projection.dag.nodes, "projection should have zero operation nodes")
    require(
        projection.dag.roots == (DagReference("input", 1),),
        "projection used the wrong input root",
    )

    constant_table = {
        point: (values[0],)
        for point in product(values, repeat=1)
    }
    unsupported = compile_controller_artifact(
        algebra,
        input_arity=1,
        output_arity=1,
        table=constant_table,
        limits=CompilationLimits(max_depth=1),
    )
    require(unsupported.status == "unsupported", "bounded miss was not explicit")
    require(
        unsupported.reason == "bounded_search_exhausted",
        "unexpected bounded-search reason",
    )

    return {
        "scalar": {
            "dag_sha256": scalar.dag.semantic_sha256,
            "certificate_sha256": scalar.certificate.semantic_sha256,
            "artifact_sha256": scalar.semantic_sha256,
            "nodes": len(scalar.dag.nodes),
            "depth": scalar.certificate.depth,
            "rows": scalar.certificate.rows_checked,
            "statistics": scalar.statistics.as_dict(),
        },
        "shared_vector": {
            "dag_sha256": vector.dag.semantic_sha256,
            "certificate_sha256": vector.certificate.semantic_sha256,
            "nodes": len(vector.dag.nodes),
            "depth": vector.certificate.depth,
            "rows": vector.certificate.rows_checked,
            "statistics": vector.statistics.as_dict(),
        },
        "projection": {
            "nodes": len(projection.dag.nodes),
            "root": projection.dag.roots[0].as_dict(),
        },
        "unsupported": {
            "status": unsupported.status,
            "reason": unsupported.reason,
            "statistics": unsupported.statistics.as_dict(),
        },
    }


def mutation_checks(bundle: ExecutableProofBundle) -> dict[str, bool]:
    artifact = bundle.controller_artifact
    require(artifact.dag is not None, "mutation bundle has no DAG")
    require(artifact.certificate is not None, "mutation bundle has no certificate")
    dag = artifact.dag
    proof = bundle.proof_bundle
    results = {}

    changed_node = replace(
        dag.nodes[0],
        arguments=(
            DagReference("input", 0),
            DagReference("input", 0),
            DagReference("input", 2),
        ),
    )
    wrong_semantics = replace(dag, nodes=(changed_node, *dag.nodes[1:]))
    results["wrong_semantics"] = not verify_controller_artifact(
        replace(artifact, dag=wrong_semantics),
        proof.problem.algebra,
        input_arity=proof.problem.state_arity + proof.problem.input_arity,
        output_arity=proof.problem.state_arity,
        table=proof.strategy,
    )

    forward = replace(
        dag.nodes[0],
        arguments=(
            DagReference("node", 0),
            *dag.nodes[0].arguments[1:],
        ),
    )
    forward_reference = replace(dag, nodes=(forward, *dag.nodes[1:]))
    results["forward_reference"] = not verify_controller_artifact(
        replace(artifact, dag=forward_reference),
        proof.problem.algebra,
        input_arity=proof.problem.state_arity + proof.problem.input_arity,
        output_arity=proof.problem.state_arity,
        table=proof.strategy,
    )

    unreachable = replace(
        dag,
        nodes=(
            *dag.nodes,
            OriginalSignatureNode(
                "u",
                (DagReference("input", 0),),
            ),
        ),
    )
    results["unreachable_node"] = not verify_controller_artifact(
        replace(artifact, dag=unreachable),
        proof.problem.algebra,
        input_arity=proof.problem.state_arity + proof.problem.input_arity,
        output_arity=proof.problem.state_arity,
        table=proof.strategy,
    )

    wrong_certificate = replace(
        artifact.certificate,
        strategy_sha256="0" * 64,
    )
    results["wrong_certificate"] = not verify_controller_artifact(
        replace(artifact, certificate=wrong_certificate),
        proof.problem.algebra,
        input_arity=proof.problem.state_arity + proof.problem.input_arity,
        output_arity=proof.problem.state_arity,
        table=proof.strategy,
    )

    payload = bundle.as_dict()
    payload["manifest_sha256"] = "f" * 64
    try:
        ExecutableProofBundle.from_dict(payload)
    except ValueError:
        results["outer_manifest"] = True
    else:
        results["outer_manifest"] = False

    payload = bundle.as_dict()
    payload["controller_artifact"]["dag"]["nodes"][0]["operation"] = "u"
    payload["controller_artifact"]["dag"]["semantic_sha256"] = "0" * 64
    payload["controller_artifact"]["semantic_sha256"] = "0" * 64
    payload["manifest_sha256"] = "0" * 64
    try:
        ExecutableProofBundle.from_dict(payload)
    except ValueError:
        results["wire_dag_mutation"] = True
    else:
        results["wire_dag_mutation"] = False

    require(all(results.values()), "one DAG artifact mutation was accepted")
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--require-highs", action="store_true")
    args = parser.parse_args()

    optimal_problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/discriminator_policy.json"
    )
    infeasible_problem = FiniteSafetyProblem.load(
        ROOT / "examples/proof_bundle/coupled_required_infeasible.json"
    )

    optimal = synthesize_executable_bundle(
        optimal_problem,
        backend="native",
        dag_policy="required",
        dag_limits=CompilationLimits(max_depth=1),
    )
    require(verify_executable_bundle(optimal), "native executable bundle replay")
    require(optimal.controller_artifact.status == "compiled", "native DAG status")
    require(optimal.controller_artifact.dag is not None, "native DAG absent")
    require(len(optimal.controller_artifact.dag.nodes) == 1, "native DAG size")

    infeasible = synthesize_executable_bundle(
        infeasible_problem,
        backend="native",
        dag_policy="required",
    )
    require(verify_executable_bundle(infeasible), "infeasible executable replay")
    require(
        infeasible.controller_artifact.status == "not_applicable",
        "infeasible problem should have no controller DAG",
    )

    require(
        ExecutableProofBundle.from_json(optimal.to_json()).manifest_sha256
        == optimal.manifest_sha256,
        "optimal executable JSON roundtrip",
    )
    require(
        ExecutableProofBundle.from_json(infeasible.to_json()).manifest_sha256
        == infeasible.manifest_sha256,
        "infeasible executable JSON roundtrip",
    )

    highs = None
    try:
        highs_bundle = synthesize_executable_bundle(
            optimal_problem,
            backend="highs",
            dag_policy="required",
            dag_limits=CompilationLimits(max_depth=1),
        )
    except Exception as error:
        if args.require_highs:
            raise
        highs = {"available": False, "reason": type(error).__name__}
    else:
        require(verify_executable_bundle(highs_bundle), "HiGHS executable replay")
        require(
            highs_bundle.controller_artifact == optimal.controller_artifact,
            "native and HiGHS produced different executable controllers",
        )
        highs = {
            "available": True,
            "executable_manifest_sha256": highs_bundle.manifest_sha256,
            "dag_sha256": highs_bundle.controller_artifact.dag.semantic_sha256,
        }

    direct = direct_compiler_checks()
    mutations = mutation_checks(optimal)

    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        optimal.write(args.out_dir / "optimal.executable.json")
        infeasible.write(args.out_dir / "infeasible.executable.json")

    result = {
        "schema": "orbit-synthesis/original-signature-dag-gate/v1",
        "optimal": row(optimal),
        "infeasible": row(infeasible),
        "highs": highs,
        "direct_compiler": direct,
        "mutations": mutations,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Executable proof bundles with original-signature controller DAGs.

The semantic proof bundle remains a stable inner artifact.  This layer adds a
controller implementation artifact without weakening the existing model,
controller, or optimality checks.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping

from .original_signature_dag import (
    CompilationLimits,
    OriginalSignatureArtifact,
    compile_controller_artifact,
    not_applicable_artifact,
    verify_controller_artifact,
)
from .problem_io import FiniteSafetyProblem
from .proof_bundle import (
    ProofBundle,
    synthesize_proof_bundle,
    verify_proof_bundle,
)
from .proof_bundle_io import strict_proof_bundle_from_dict

_SCHEMA = "orbit-synthesis/executable-proof-bundle/v1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _exact_keys(
    payload: Mapping[str, object],
    expected: frozenset[str],
    *,
    field: str,
) -> None:
    missing = expected - set(payload)
    extra = set(payload) - expected
    if missing:
        raise ValueError(f"{field} is missing key {min(missing)!r}")
    if extra:
        raise ValueError(f"{field} contains unknown key {min(extra)!r}")


@dataclass(frozen=True)
class ExecutableProofBundle:
    proof_bundle: ProofBundle
    controller_artifact: OriginalSignatureArtifact

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _SCHEMA,
            "proof_bundle": self.proof_bundle.as_dict(),
            "controller_artifact": self.controller_artifact.as_dict(),
        }

    @property
    def manifest_sha256(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.semantic_payload())).hexdigest()

    def as_dict(self) -> dict[str, object]:
        payload = self.semantic_payload()
        payload["manifest_sha256"] = self.manifest_sha256
        return payload

    def to_json(self) -> str:
        return json.dumps(
            self.as_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n"

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "ExecutableProofBundle":
        _exact_keys(
            payload,
            frozenset(
                (
                    "schema",
                    "proof_bundle",
                    "controller_artifact",
                    "manifest_sha256",
                )
            ),
            field="executable proof bundle",
        )
        if payload["schema"] != _SCHEMA:
            raise ValueError("unsupported executable proof-bundle schema")
        proof_payload = payload["proof_bundle"]
        artifact_payload = payload["controller_artifact"]
        if not isinstance(proof_payload, Mapping):
            raise TypeError("proof_bundle must be an object")
        if not isinstance(artifact_payload, Mapping):
            raise TypeError("controller_artifact must be an object")
        bundle = cls(
            proof_bundle=strict_proof_bundle_from_dict(proof_payload),
            controller_artifact=OriginalSignatureArtifact.from_dict(
                artifact_payload
            ),
        )
        manifest = payload["manifest_sha256"]
        if not isinstance(manifest, str) or manifest != bundle.manifest_sha256:
            raise ValueError("executable proof-bundle manifest hash mismatch")
        return bundle

    @classmethod
    def from_json(cls, text: str) -> "ExecutableProofBundle":
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise TypeError("executable proof-bundle JSON must contain one object")
        return cls.from_dict(payload)

    @classmethod
    def load(cls, path: str | Path) -> "ExecutableProofBundle":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def write(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")


def synthesize_executable_bundle(
    problem: FiniteSafetyProblem,
    *,
    backend: str = "auto",
    certificate_max_nodes: int = 1_000_000,
    dag_policy: str = "best_effort",
    dag_limits: CompilationLimits | None = None,
) -> ExecutableProofBundle:
    """Synthesize a semantic proof bundle and an original-signature artifact.

    ``dag_policy`` is one of:

    * ``required``: fail unless the bounded compiler produces a DAG;
    * ``best_effort``: preserve an explicit unsupported receipt on exhaustion;
    * ``off``: emit a not-applicable artifact without running the compiler.
    """

    if dag_policy not in {"required", "best_effort", "off"}:
        raise ValueError("dag_policy must be required, best_effort, or off")
    proof = synthesize_proof_bundle(
        problem,
        backend=backend,
        certificate_max_nodes=certificate_max_nodes,
    )
    limits = CompilationLimits() if dag_limits is None else dag_limits

    if proof.status == "infeasible":
        artifact = not_applicable_artifact(limits=limits)
    elif dag_policy == "off":
        artifact = not_applicable_artifact(
            reason="original_signature_compilation_disabled",
            limits=limits,
        )
    else:
        artifact = compile_controller_artifact(
            problem.algebra,
            input_arity=problem.state_arity + problem.input_arity,
            output_arity=problem.state_arity,
            table=proof.strategy,
            limits=limits,
        )
        if dag_policy == "required" and artifact.status != "compiled":
            raise ValueError(
                "original-signature compilation required but bounded compiler "
                f"returned {artifact.reason!r}"
            )

    bundle = ExecutableProofBundle(
        proof_bundle=proof,
        controller_artifact=artifact,
    )
    if not verify_executable_bundle(bundle):
        raise AssertionError("generated executable proof bundle failed replay")
    return bundle


def verify_executable_bundle(bundle: ExecutableProofBundle) -> bool:
    """Verify semantic synthesis, controller implementation, and equivalence."""

    if not verify_proof_bundle(bundle.proof_bundle):
        return False
    proof = bundle.proof_bundle
    artifact = bundle.controller_artifact
    if artifact.compiler != "bounded-semantic-closure/v1":
        return False

    if proof.status == "infeasible":
        return (
            artifact.status == "not_applicable"
            and isinstance(artifact.reason, str)
            and bool(artifact.reason)
            and artifact.dag is None
            and artifact.certificate is None
            and verify_controller_artifact(
                artifact,
                proof.problem.algebra,
                input_arity=(
                    proof.problem.state_arity + proof.problem.input_arity
                ),
                output_arity=proof.problem.state_arity,
                table=None,
            )
        )
    if proof.status != "optimal":
        return False

    if artifact.status == "compiled":
        if artifact.reason is not None:
            return False
        if artifact.dag is None or artifact.certificate is None:
            return False
    elif artifact.status in {"unsupported", "not_applicable"}:
        if not isinstance(artifact.reason, str) or not artifact.reason:
            return False
        if artifact.dag is not None or artifact.certificate is not None:
            return False
    else:
        return False

    return verify_controller_artifact(
        artifact,
        proof.problem.algebra,
        input_arity=proof.problem.state_arity + proof.problem.input_arity,
        output_arity=proof.problem.state_arity,
        table=proof.strategy,
    )

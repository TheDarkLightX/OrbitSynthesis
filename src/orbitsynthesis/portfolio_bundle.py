"""Portable proof bundles with a practical compiler portfolio artifact."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping

from .compiler_portfolio import (
    CompilerPortfolioArtifact,
    CompilerPortfolioConfig,
)
from .compiler_portfolio_policy import verify_portfolio_selection
from .compiler_portfolio_runtime import (
    compile_portfolio_runtime,
    not_applicable_portfolio,
    verify_portfolio_runtime,
)
from .problem_io import FiniteSafetyProblem
from .proof_bundle import ProofBundle, synthesize_proof_bundle, verify_proof_bundle
from .proof_bundle_io import strict_proof_bundle_from_dict

_SCHEMA = "orbit-synthesis/portfolio-proof-bundle/v1"


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
class PortfolioProofBundle:
    proof_bundle: ProofBundle
    compiler_portfolio: CompilerPortfolioArtifact

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _SCHEMA,
            "proof_bundle": self.proof_bundle.as_dict(),
            "compiler_portfolio": self.compiler_portfolio.as_dict(),
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
    def from_dict(cls, payload: Mapping[str, object]) -> "PortfolioProofBundle":
        _exact_keys(
            payload,
            frozenset(
                (
                    "schema",
                    "proof_bundle",
                    "compiler_portfolio",
                    "manifest_sha256",
                )
            ),
            field="portfolio proof bundle",
        )
        if payload["schema"] != _SCHEMA:
            raise ValueError("unsupported portfolio proof-bundle schema")
        proof_payload = payload["proof_bundle"]
        portfolio_payload = payload["compiler_portfolio"]
        if not isinstance(proof_payload, Mapping):
            raise TypeError("portfolio proof_bundle must be an object")
        if not isinstance(portfolio_payload, Mapping):
            raise TypeError("compiler_portfolio must be an object")
        bundle = cls(
            proof_bundle=strict_proof_bundle_from_dict(proof_payload),
            compiler_portfolio=CompilerPortfolioArtifact.from_dict(
                portfolio_payload
            ),
        )
        manifest = payload["manifest_sha256"]
        if not isinstance(manifest, str) or manifest != bundle.manifest_sha256:
            raise ValueError("portfolio proof-bundle manifest hash mismatch")
        return bundle

    @classmethod
    def from_json(cls, text: str) -> "PortfolioProofBundle":
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise TypeError("portfolio proof-bundle JSON must contain one object")
        return cls.from_dict(payload)

    @classmethod
    def load(cls, path: str | Path) -> "PortfolioProofBundle":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def write(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")


def synthesize_portfolio_bundle(
    problem: FiniteSafetyProblem,
    *,
    backend: str = "auto",
    certificate_max_nodes: int = 1_000_000,
    portfolio_config: CompilerPortfolioConfig | None = None,
    implementation_required: bool = True,
) -> PortfolioProofBundle:
    proof = synthesize_proof_bundle(
        problem,
        backend=backend,
        certificate_max_nodes=certificate_max_nodes,
    )
    active = CompilerPortfolioConfig() if portfolio_config is None else portfolio_config
    if proof.status == "infeasible":
        portfolio = not_applicable_portfolio(config=active)
    else:
        portfolio = compile_portfolio_runtime(
            problem.algebra,
            input_arity=problem.state_arity + problem.input_arity,
            output_arity=problem.state_arity,
            table=proof.strategy,
            config=active,
        )
        if implementation_required and portfolio.status != "compiled":
            raise ValueError(
                "compiler portfolio produced no implementation under the "
                f"selected policy: {portfolio.reason!r}"
            )
    bundle = PortfolioProofBundle(
        proof_bundle=proof,
        compiler_portfolio=portfolio,
    )
    if not verify_portfolio_bundle(bundle):
        raise AssertionError("generated portfolio proof bundle failed replay")
    return bundle


def verify_portfolio_bundle(bundle: PortfolioProofBundle) -> bool:
    if not verify_proof_bundle(bundle.proof_bundle):
        return False
    proof = bundle.proof_bundle
    portfolio = bundle.compiler_portfolio
    if not verify_portfolio_selection(portfolio):
        return False
    if proof.status == "infeasible":
        return (
            portfolio.status == "not_applicable"
            and verify_portfolio_runtime(
                portfolio,
                proof.problem.algebra,
                input_arity=proof.problem.state_arity + proof.problem.input_arity,
                output_arity=proof.problem.state_arity,
                table=None,
            )
        )
    if proof.status != "optimal":
        return False
    return verify_portfolio_runtime(
        portfolio,
        proof.problem.algebra,
        input_arity=proof.problem.state_arity + proof.problem.input_arity,
        output_arity=proof.problem.state_arity,
        table=proof.strategy,
    )

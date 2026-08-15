"""Fail-closed JSON loading for portable OrbitSynthesis proof bundles.

``ProofBundle`` is the in-memory semantic object. This module enforces the v1
wire contract before constructing that object: required keys, no unknown keys
outside explicitly extensible metadata, SHA-256 syntax, and the exact result
and certificate envelopes.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Mapping

from .proof_bundle import ProofBundle

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_BUNDLE_KEYS = frozenset(
    (
        "schema",
        "problem",
        "problem_sha256",
        "component_model_sha256",
        "result",
        "optimality_certificate",
        "metadata",
        "manifest_sha256",
    )
)
_RESULT_KEYS = frozenset(
    (
        "status",
        "backend",
        "domain",
        "signed_utility",
        "component_choices",
        "strategy",
        "backend_semantic_sha256",
    )
)
_STRATEGY_KEYS = frozenset(("observation", "output"))
_CERTIFICATE_KEYS = frozenset(
    (
        "schema",
        "model_sha256",
        "problem_sha256",
        "state_count",
        "weights",
        "required_mask",
        "forbidden_mask",
        "target_score",
        "target_domain_mask",
        "root",
        "nodes",
        "semantic_sha256",
        "statistics",
    )
)
_NODE_KEYS = frozenset(
    (
        "kind",
        "state_index",
        "include_child",
        "exclude_child",
        "component_index",
        "upper_bound",
    )
)
_STATISTICS_KEYS = frozenset(
    ("nodes", "branches", "conflict_leaves", "bound_leaves")
)


def _mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be a JSON object")
    if any(not isinstance(key, str) for key in value):
        raise TypeError(f"{field} keys must be strings")
    return value  # type: ignore[return-value]


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


def _sha256(value: object, *, field: str, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256 string")


def strict_proof_bundle_from_dict(
    payload: Mapping[str, object],
) -> ProofBundle:
    """Validate the complete v1 wire envelope and construct a bundle."""

    _exact_keys(payload, _BUNDLE_KEYS, field="proof bundle")
    if payload["schema"] != "orbit-synthesis/proof-bundle/v1":
        raise ValueError("unsupported proof-bundle schema")
    _sha256(payload["problem_sha256"], field="problem_sha256")
    _sha256(
        payload["component_model_sha256"],
        field="component_model_sha256",
    )
    _sha256(payload["manifest_sha256"], field="manifest_sha256")

    result = _mapping(payload["result"], field="result")
    _exact_keys(result, _RESULT_KEYS, field="result")
    _sha256(
        result["backend_semantic_sha256"],
        field="result.backend_semantic_sha256",
        nullable=True,
    )
    strategy = result["strategy"]
    if not isinstance(strategy, list):
        raise TypeError("result.strategy must be a JSON list")
    for index, row in enumerate(strategy):
        parsed = _mapping(row, field=f"result.strategy[{index}]")
        _exact_keys(
            parsed,
            _STRATEGY_KEYS,
            field=f"result.strategy[{index}]",
        )

    certificate = _mapping(
        payload["optimality_certificate"],
        field="optimality_certificate",
    )
    _exact_keys(
        certificate,
        _CERTIFICATE_KEYS,
        field="optimality_certificate",
    )
    _sha256(
        certificate["model_sha256"],
        field="optimality_certificate.model_sha256",
    )
    _sha256(
        certificate["problem_sha256"],
        field="optimality_certificate.problem_sha256",
    )
    _sha256(
        certificate["semantic_sha256"],
        field="optimality_certificate.semantic_sha256",
    )
    nodes = certificate["nodes"]
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("optimality_certificate.nodes must be nonempty")
    for index, node in enumerate(nodes):
        parsed = _mapping(
            node,
            field=f"optimality_certificate.nodes[{index}]",
        )
        _exact_keys(
            parsed,
            _NODE_KEYS,
            field=f"optimality_certificate.nodes[{index}]",
        )
    statistics = _mapping(
        certificate["statistics"],
        field="optimality_certificate.statistics",
    )
    _exact_keys(
        statistics,
        _STATISTICS_KEYS,
        field="optimality_certificate.statistics",
    )

    _mapping(payload["metadata"], field="metadata")
    bundle = ProofBundle.from_dict(payload)
    if bundle.manifest_sha256 != payload["manifest_sha256"]:
        raise ValueError("proof-bundle manifest hash mismatch")
    return bundle


def strict_proof_bundle_from_json(text: str) -> ProofBundle:
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise TypeError("proof-bundle JSON must contain one object")
    return strict_proof_bundle_from_dict(payload)


def load_proof_bundle(path: str | Path) -> ProofBundle:
    return strict_proof_bundle_from_json(
        Path(path).read_text(encoding="utf-8")
    )

"""Portfolio selection across structural, exact, MDD, and research backends.

The practical default does not treat the asymptotic fixed-Q Shannon compiler as
an executable backend.  It records that lane as diagnostic-only while selecting
among materialized implementations:

1. bounded exact semantic closure for tiny tables;
2. targeted fixed-Q signed-router recognition;
3. reduced ordered multi-terminal decision diagrams.

Original-signature implementations retain the stronger algebraic guarantee.
MDD implementations are exact executable decision diagrams but are not claimed
to be terms in the original signature.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Hashable, Mapping

from .decision_diagram import (
    MDDArtifact,
    compile_mdd_artifact,
    not_applicable_mdd_artifact,
    verify_mdd_artifact,
)
from .finite_algebra import FiniteAlgebra
from .fixed_q_structural import (
    BACKEND_ID as Q_STRUCTURAL_BACKEND,
    compile_fixed_q_structural,
    is_quackenbush_q,
)
from .original_signature_dag import (
    CompilationLimits,
    ControllerDAGCertificate,
    OriginalSignatureDAG,
    compile_controller_artifact,
    dag_depth,
    verify_controller_dag_certificate,
)

Value = Hashable
InputRow = tuple[Value, ...]
OutputRow = tuple[Value, ...]

_SCHEMA = "orbit-synthesis/compiler-portfolio/v1"
_EXACT_BACKEND = "exact-semantic-closure"
_STRUCTURAL_BACKEND = "fixed-q-structural-router"
_MDD_BACKEND = "reduced-vector-mdd"
_SHANNON_BACKEND = "fixed-q-shannon-experimental"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=repr,
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


def _integer(value: object, *, field: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise TypeError(f"{field} must be an integer >= {minimum}")
    return value


@dataclass(frozen=True)
class CompilerPortfolioConfig:
    policy: str = "practical"
    exact_max_rows: int = 243
    mdd_max_rows: int = 250_000
    structural_candidate_limit: int = 400_000
    enable_exact: bool = True
    enable_structural: bool = True
    enable_mdd: bool = True
    include_shannon_diagnostic: bool = True
    exact_limits: CompilationLimits = CompilationLimits()

    def __post_init__(self) -> None:
        if self.policy not in {"practical", "original_signature", "mdd_only"}:
            raise ValueError(
                "portfolio policy must be practical, original_signature, or mdd_only"
            )
        for field, value in (
            ("exact_max_rows", self.exact_max_rows),
            ("mdd_max_rows", self.mdd_max_rows),
            ("structural_candidate_limit", self.structural_candidate_limit),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{field} must be a positive integer")
        for field, value in (
            ("enable_exact", self.enable_exact),
            ("enable_structural", self.enable_structural),
            ("enable_mdd", self.enable_mdd),
            ("include_shannon_diagnostic", self.include_shannon_diagnostic),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field} must be Boolean")

    def as_dict(self) -> dict[str, object]:
        return {
            "policy": self.policy,
            "exact_max_rows": self.exact_max_rows,
            "mdd_max_rows": self.mdd_max_rows,
            "structural_candidate_limit": self.structural_candidate_limit,
            "enable_exact": self.enable_exact,
            "enable_structural": self.enable_structural,
            "enable_mdd": self.enable_mdd,
            "include_shannon_diagnostic": self.include_shannon_diagnostic,
            "exact_limits": self.exact_limits.as_dict(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "CompilerPortfolioConfig":
        _exact_keys(
            payload,
            frozenset(
                (
                    "policy",
                    "exact_max_rows",
                    "mdd_max_rows",
                    "structural_candidate_limit",
                    "enable_exact",
                    "enable_structural",
                    "enable_mdd",
                    "include_shannon_diagnostic",
                    "exact_limits",
                )
            ),
            field="compiler portfolio config",
        )
        limits = payload["exact_limits"]
        if not isinstance(limits, Mapping):
            raise TypeError("portfolio exact_limits must be an object")
        return cls(
            policy=str(payload["policy"]),
            exact_max_rows=_integer(
                payload["exact_max_rows"], field="exact_max_rows", minimum=1
            ),
            mdd_max_rows=_integer(
                payload["mdd_max_rows"], field="mdd_max_rows", minimum=1
            ),
            structural_candidate_limit=_integer(
                payload["structural_candidate_limit"],
                field="structural_candidate_limit",
                minimum=1,
            ),
            enable_exact=payload["enable_exact"],  # type: ignore[arg-type]
            enable_structural=payload["enable_structural"],  # type: ignore[arg-type]
            enable_mdd=payload["enable_mdd"],  # type: ignore[arg-type]
            include_shannon_diagnostic=payload["include_shannon_diagnostic"],  # type: ignore[arg-type]
            exact_limits=CompilationLimits.from_dict(limits),
        )


@dataclass(frozen=True)
class BackendAttempt:
    backend: str
    tier: str
    status: str
    implementation_kind: str | None
    reason: str | None
    score: int | None
    metrics_items: tuple[tuple[str, object], ...] = ()

    @property
    def metrics(self) -> dict[str, object]:
        return dict(self.metrics_items)

    def as_dict(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "tier": self.tier,
            "status": self.status,
            "implementation_kind": self.implementation_kind,
            "reason": self.reason,
            "score": self.score,
            "metrics": self.metrics,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "BackendAttempt":
        _exact_keys(
            payload,
            frozenset(
                (
                    "backend",
                    "tier",
                    "status",
                    "implementation_kind",
                    "reason",
                    "score",
                    "metrics",
                )
            ),
            field="compiler backend attempt",
        )
        metrics = payload["metrics"]
        if not isinstance(metrics, Mapping):
            raise TypeError("compiler attempt metrics must be an object")
        backend = payload["backend"]
        tier = payload["tier"]
        status = payload["status"]
        kind = payload["implementation_kind"]
        reason = payload["reason"]
        score = payload["score"]
        if not isinstance(backend, str) or not backend:
            raise ValueError("compiler attempt backend must be nonempty")
        if tier not in {"tiny", "medium", "practical", "research"}:
            raise ValueError("invalid compiler attempt tier")
        if status not in {"compiled", "unsupported", "not_applicable", "diagnostic"}:
            raise ValueError("invalid compiler attempt status")
        if kind is not None and kind not in {"original_signature", "mdd"}:
            raise ValueError("invalid compiler implementation kind")
        if reason is not None and (not isinstance(reason, str) or not reason):
            raise ValueError("compiler attempt reason must be null or nonempty")
        parsed_score = None
        if score is not None:
            parsed_score = _integer(score, field="compiler attempt score")
        return cls(
            backend=backend,
            tier=str(tier),
            status=str(status),
            implementation_kind=None if kind is None else str(kind),
            reason=reason,
            score=parsed_score,
            metrics_items=tuple(sorted(metrics.items())),
        )


@dataclass(frozen=True)
class OriginalSignatureImplementation:
    backend: str
    dag: OriginalSignatureDAG
    certificate: ControllerDAGCertificate

    def semantic_payload(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "dag": self.dag.as_dict(),
            "certificate": self.certificate.as_dict(),
        }

    @property
    def semantic_sha256(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.semantic_payload())).hexdigest()

    def as_dict(self) -> dict[str, object]:
        payload = self.semantic_payload()
        payload["semantic_sha256"] = self.semantic_sha256
        return payload

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "OriginalSignatureImplementation":
        _exact_keys(
            payload,
            frozenset(("backend", "dag", "certificate", "semantic_sha256")),
            field="portfolio original-signature implementation",
        )
        if payload["backend"] not in {_EXACT_BACKEND, _STRUCTURAL_BACKEND}:
            raise ValueError("unsupported portfolio original-signature backend")
        dag = payload["dag"]
        certificate = payload["certificate"]
        if not isinstance(dag, Mapping) or not isinstance(certificate, Mapping):
            raise TypeError("portfolio original-signature data must be objects")
        implementation = cls(
            backend=str(payload["backend"]),
            dag=OriginalSignatureDAG.from_dict(dag),
            certificate=ControllerDAGCertificate.from_dict(certificate),
        )
        if payload["semantic_sha256"] != implementation.semantic_sha256:
            raise ValueError("portfolio original-signature hash mismatch")
        return implementation


@dataclass(frozen=True)
class CompilerPortfolioArtifact:
    status: str
    config: CompilerPortfolioConfig
    selected_backend: str | None
    selected_kind: str | None
    attempts: tuple[BackendAttempt, ...]
    original_signature: OriginalSignatureImplementation | None
    mdd: MDDArtifact | None
    reason: str | None

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _SCHEMA,
            "status": self.status,
            "config": self.config.as_dict(),
            "selected_backend": self.selected_backend,
            "selected_kind": self.selected_kind,
            "attempts": [attempt.as_dict() for attempt in self.attempts],
            "original_signature": (
                None
                if self.original_signature is None
                else self.original_signature.as_dict()
            ),
            "mdd": None if self.mdd is None else self.mdd.as_dict(),
            "reason": self.reason,
        }

    @property
    def semantic_sha256(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.semantic_payload())).hexdigest()

    def as_dict(self) -> dict[str, object]:
        payload = self.semantic_payload()
        payload["semantic_sha256"] = self.semantic_sha256
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "CompilerPortfolioArtifact":
        _exact_keys(
            payload,
            frozenset(
                (
                    "schema",
                    "status",
                    "config",
                    "selected_backend",
                    "selected_kind",
                    "attempts",
                    "original_signature",
                    "mdd",
                    "reason",
                    "semantic_sha256",
                )
            ),
            field="compiler portfolio artifact",
        )
        if payload["schema"] != _SCHEMA:
            raise ValueError("unsupported compiler portfolio schema")
        if payload["status"] not in {"compiled", "unsupported", "not_applicable"}:
            raise ValueError("invalid compiler portfolio status")
        config = payload["config"]
        attempts = payload["attempts"]
        if not isinstance(config, Mapping):
            raise TypeError("compiler portfolio config must be an object")
        if not isinstance(attempts, list):
            raise TypeError("compiler portfolio attempts must be a list")
        parsed_attempts = []
        for index, attempt in enumerate(attempts):
            if not isinstance(attempt, Mapping):
                raise TypeError(f"compiler portfolio attempt {index} must be an object")
            parsed_attempts.append(BackendAttempt.from_dict(attempt))
        original_payload = payload["original_signature"]
        mdd_payload = payload["mdd"]
        original = None
        mdd = None
        if original_payload is not None:
            if not isinstance(original_payload, Mapping):
                raise TypeError("portfolio original-signature implementation must be an object")
            original = OriginalSignatureImplementation.from_dict(original_payload)
        if mdd_payload is not None:
            if not isinstance(mdd_payload, Mapping):
                raise TypeError("portfolio MDD implementation must be an object")
            mdd = MDDArtifact.from_dict(mdd_payload)
        reason = payload["reason"]
        if reason is not None and (not isinstance(reason, str) or not reason):
            raise ValueError("portfolio reason must be null or nonempty")
        artifact = cls(
            status=str(payload["status"]),
            config=CompilerPortfolioConfig.from_dict(config),
            selected_backend=(
                None
                if payload["selected_backend"] is None
                else str(payload["selected_backend"])
            ),
            selected_kind=(
                None if payload["selected_kind"] is None else str(payload["selected_kind"])
            ),
            attempts=tuple(parsed_attempts),
            original_signature=original,
            mdd=mdd,
            reason=reason,
        )
        if artifact.status == "compiled":
            if artifact.selected_backend is None or artifact.selected_kind is None:
                raise ValueError("compiled portfolio requires a selected backend")
            if artifact.reason is not None:
                raise ValueError("compiled portfolio cannot carry a failure reason")
            if artifact.selected_kind == "original_signature":
                if artifact.original_signature is None or artifact.mdd is not None:
                    raise ValueError("original-signature selection has wrong payload")
                if artifact.original_signature.backend != artifact.selected_backend:
                    raise ValueError("selected backend disagrees with implementation")
            elif artifact.selected_kind == "mdd":
                if artifact.mdd is None or artifact.original_signature is not None:
                    raise ValueError("MDD selection has wrong payload")
                if artifact.selected_backend != _MDD_BACKEND:
                    raise ValueError("selected MDD backend identifier is wrong")
            else:
                raise ValueError("compiled portfolio selected invalid kind")
        else:
            if artifact.selected_backend is not None or artifact.selected_kind is not None:
                raise ValueError("noncompiled portfolio cannot select a backend")
            if artifact.original_signature is not None or artifact.mdd is not None:
                raise ValueError("noncompiled portfolio cannot retain implementation")
            if artifact.reason is None:
                raise ValueError("noncompiled portfolio requires a reason")
        if payload["semantic_sha256"] != artifact.semantic_sha256:
            raise ValueError("compiler portfolio semantic hash mismatch")
        return artifact


def _attempt(
    backend: str,
    tier: str,
    status: str,
    *,
    kind: str | None = None,
    reason: str | None = None,
    score: int | None = None,
    metrics: Mapping[str, object] = (),  # type: ignore[assignment]
) -> BackendAttempt:
    values = {} if metrics == () else dict(metrics)
    return BackendAttempt(
        backend=backend,
        tier=tier,
        status=status,
        implementation_kind=kind,
        reason=reason,
        score=score,
        metrics_items=tuple(sorted(values.items())),
    )


def _original_score(dag: OriginalSignatureDAG) -> int:
    return 10 * len(dag.nodes) + dag_depth(dag)


def _mdd_score(artifact: MDDArtifact) -> int:
    if artifact.diagram is None or artifact.certificate is None:
        raise ValueError("cannot score noncompiled MDD")
    return (
        10 * len(artifact.diagram.nodes)
        + 3 * len(artifact.diagram.terminals)
        + artifact.certificate.depth
    )


def compile_portfolio(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    config: CompilerPortfolioConfig | None = None,
) -> CompilerPortfolioArtifact:
    active = CompilerPortfolioConfig() if config is None else config
    row_count = len(algebra.values) ** input_arity
    attempts: list[BackendAttempt] = []
    materialized: list[
        tuple[int, int, str, str, OriginalSignatureImplementation | MDDArtifact]
    ] = []

    if active.enable_exact:
        if row_count > active.exact_max_rows:
            attempts.append(
                _attempt(
                    _EXACT_BACKEND,
                    "tiny",
                    "not_applicable",
                    reason="above_tiny_table_threshold",
                    metrics={"rows": row_count, "row_limit": active.exact_max_rows},
                )
            )
        else:
            exact = compile_controller_artifact(
                algebra,
                input_arity=input_arity,
                output_arity=output_arity,
                table=table,
                limits=active.exact_limits,
            )
            if exact.status == "compiled" and exact.dag is not None and exact.certificate is not None:
                implementation = OriginalSignatureImplementation(
                    backend=_EXACT_BACKEND,
                    dag=exact.dag,
                    certificate=exact.certificate,
                )
                score = _original_score(exact.dag)
                attempts.append(
                    _attempt(
                        _EXACT_BACKEND,
                        "tiny",
                        "compiled",
                        kind="original_signature",
                        score=score,
                        metrics={
                            "rows": row_count,
                            "nodes": len(exact.dag.nodes),
                            "depth": dag_depth(exact.dag),
                            **exact.statistics.as_dict(),
                        },
                    )
                )
                materialized.append((score, 0, _EXACT_BACKEND, "original_signature", implementation))
            else:
                attempts.append(
                    _attempt(
                        _EXACT_BACKEND,
                        "tiny",
                        "unsupported",
                        reason=exact.reason,
                        metrics={"rows": row_count, **exact.statistics.as_dict()},
                    )
                )
    else:
        attempts.append(
            _attempt(_EXACT_BACKEND, "tiny", "not_applicable", reason="disabled")
        )

    if active.enable_structural:
        structural = compile_fixed_q_structural(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            candidate_limit=active.structural_candidate_limit,
        )
        if structural.status == "compiled" and structural.dag is not None and structural.certificate is not None:
            implementation = OriginalSignatureImplementation(
                backend=_STRUCTURAL_BACKEND,
                dag=structural.dag,
                certificate=structural.certificate,
            )
            score = _original_score(structural.dag)
            attempts.append(
                _attempt(
                    _STRUCTURAL_BACKEND,
                    "medium",
                    "compiled",
                    kind="original_signature",
                    score=score,
                    metrics={
                        "rows": row_count,
                        "nodes": len(structural.dag.nodes),
                        "depth": dag_depth(structural.dag),
                        "recognizer": Q_STRUCTURAL_BACKEND,
                        **structural.statistics.as_dict(),
                    },
                )
            )
            materialized.append((score, 1, _STRUCTURAL_BACKEND, "original_signature", implementation))
        else:
            attempts.append(
                _attempt(
                    _STRUCTURAL_BACKEND,
                    "medium",
                    structural.status,
                    reason=structural.reason,
                    metrics={"rows": row_count, **structural.statistics.as_dict()},
                )
            )
    else:
        attempts.append(
            _attempt(_STRUCTURAL_BACKEND, "medium", "not_applicable", reason="disabled")
        )

    if active.enable_mdd:
        mdd = compile_mdd_artifact(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            row_limit=active.mdd_max_rows,
            order_policy="portfolio",
        )
        if mdd.status == "compiled" and mdd.diagram is not None and mdd.certificate is not None:
            score = _mdd_score(mdd)
            attempts.append(
                _attempt(
                    _MDD_BACKEND,
                    "practical",
                    "compiled",
                    kind="mdd",
                    score=score,
                    metrics={
                        "rows": row_count,
                        "nodes": len(mdd.diagram.nodes),
                        "terminals": len(mdd.diagram.terminals),
                        "depth": mdd.certificate.depth,
                        "variable_order": list(mdd.diagram.variable_order),
                        "orders_considered": len(mdd.orders_considered),
                    },
                )
            )
            materialized.append((score, 2, _MDD_BACKEND, "mdd", mdd))
        else:
            attempts.append(
                _attempt(
                    _MDD_BACKEND,
                    "practical",
                    mdd.status,
                    reason=mdd.reason,
                    metrics={"rows": row_count, "row_limit": active.mdd_max_rows},
                )
            )
    else:
        attempts.append(
            _attempt(_MDD_BACKEND, "practical", "not_applicable", reason="disabled")
        )

    if active.include_shannon_diagnostic:
        if is_quackenbush_q(algebra):
            attempts.append(
                _attempt(
                    _SHANNON_BACKEND,
                    "research",
                    "diagnostic",
                    reason="not_materialized_and_never_auto_selected",
                    metrics={
                        "input_arity": input_arity,
                        "output_arity": output_arity,
                        "explicit_rows": row_count,
                        "theorem_threshold_r_ge_64": input_arity >= 64,
                        "automatic_selection": False,
                    },
                )
            )
        else:
            attempts.append(
                _attempt(
                    _SHANNON_BACKEND,
                    "research",
                    "not_applicable",
                    reason="not_exact_quackenbush_q",
                )
            )

    if active.policy == "original_signature":
        eligible = [row for row in materialized if row[3] == "original_signature"]
    elif active.policy == "mdd_only":
        eligible = [row for row in materialized if row[3] == "mdd"]
    else:
        eligible = materialized

    if not eligible:
        return CompilerPortfolioArtifact(
            status="unsupported",
            config=active,
            selected_backend=None,
            selected_kind=None,
            attempts=tuple(attempts),
            original_signature=None,
            mdd=None,
            reason="no_materialized_backend_for_policy",
        )

    _score, _priority, backend, kind, implementation = min(eligible)
    return CompilerPortfolioArtifact(
        status="compiled",
        config=active,
        selected_backend=backend,
        selected_kind=kind,
        attempts=tuple(attempts),
        original_signature=(
            implementation
            if isinstance(implementation, OriginalSignatureImplementation)
            else None
        ),
        mdd=implementation if isinstance(implementation, MDDArtifact) else None,
        reason=None,
    )


def not_applicable_portfolio(
    *,
    config: CompilerPortfolioConfig | None = None,
    reason: str = "no_controller_for_infeasible_problem",
) -> CompilerPortfolioArtifact:
    return CompilerPortfolioArtifact(
        status="not_applicable",
        config=CompilerPortfolioConfig() if config is None else config,
        selected_backend=None,
        selected_kind=None,
        attempts=(),
        original_signature=None,
        mdd=None,
        reason=reason,
    )


def verify_portfolio(
    artifact: CompilerPortfolioArtifact,
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow] | None,
) -> bool:
    if artifact.status == "not_applicable":
        return table is None and artifact.reason is not None
    if table is None:
        return False
    if artifact.status == "unsupported":
        return (
            artifact.selected_backend is None
            and artifact.selected_kind is None
            and artifact.original_signature is None
            and artifact.mdd is None
            and artifact.reason is not None
        )
    if artifact.status != "compiled":
        return False
    compiled_attempts = {
        (attempt.backend, attempt.implementation_kind)
        for attempt in artifact.attempts
        if attempt.status == "compiled"
    }
    if (artifact.selected_backend, artifact.selected_kind) not in compiled_attempts:
        return False
    if artifact.selected_backend == _SHANNON_BACKEND:
        return False
    if artifact.selected_kind == "original_signature":
        implementation = artifact.original_signature
        if implementation is None or artifact.mdd is not None:
            return False
        return verify_controller_dag_certificate(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            dag=implementation.dag,
            certificate=implementation.certificate,
        )
    if artifact.selected_kind == "mdd":
        return (
            artifact.original_signature is None
            and artifact.mdd is not None
            and verify_mdd_artifact(
                artifact.mdd,
                algebra,
                input_arity=input_arity,
                output_arity=output_arity,
                table=table,
            )
        )
    return False

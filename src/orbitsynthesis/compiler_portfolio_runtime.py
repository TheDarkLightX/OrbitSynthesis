"""Practical portfolio execution with one-validation MDD certification.

The wire types and attempt semantics live in :mod:`compiler_portfolio`. This
module runs an ordered fallback chain:

1. exact semantic closure for tiny tables;
2. fixed-Q structural original-signature recognition;
3. reduced vector MDD.

Once a higher-priority materialized tier succeeds, lower deployment tiers are
recorded as skipped rather than executed. The fixed-Q Shannon lane is recorded
as a diagnostic only and is never a selection candidate. Structural recognition
is bounded by an explicit row/work budget so it cannot accidentally scan a
large `3^r` table with hundreds of thousands of term candidates.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Hashable, Mapping

from .compiler_portfolio import (
    BackendAttempt,
    CompilerPortfolioArtifact,
    CompilerPortfolioConfig,
    OriginalSignatureImplementation,
    compile_portfolio as compile_single_tier_portfolio,
    not_applicable_portfolio,
    verify_portfolio as verify_base_portfolio,
)
from .decision_diagram import MDDArtifact
from .decision_diagram_runtime import (
    compile_mdd_artifact_linear,
    verify_mdd_artifact_linear,
)
from .finite_algebra import FiniteAlgebra
from .fixed_q_structural import is_quackenbush_q

Value = Hashable
InputRow = tuple[Value, ...]
OutputRow = tuple[Value, ...]

_EXACT_BACKEND = "exact-semantic-closure"
_STRUCTURAL_BACKEND = "fixed-q-structural-router"
_MDD_BACKEND = "reduced-vector-mdd"
_SHANNON_BACKEND = "fixed-q-shannon-experimental"
_STRUCTURAL_ROW_LIMIT = 2_187
_STRUCTURAL_SCALAR_WORK_BUDGET = 100_000_000


def _attempt_for_backend(
    artifact: CompilerPortfolioArtifact,
    backend: str,
) -> BackendAttempt:
    return next(
        attempt for attempt in artifact.attempts if attempt.backend == backend
    )


def _not_applicable_attempt(
    backend: str,
    tier: str,
    reason: str,
    *,
    metrics: Mapping[str, object] | None = None,
) -> BackendAttempt:
    return BackendAttempt(
        backend=backend,
        tier=tier,
        status="not_applicable",
        implementation_kind=None,
        reason=reason,
        score=None,
        metrics_items=tuple(sorted(({} if metrics is None else dict(metrics)).items())),
    )


def _mdd_attempt(
    artifact: MDDArtifact,
    *,
    row_count: int,
    row_limit: int,
) -> BackendAttempt:
    if (
        artifact.status == "compiled"
        and artifact.diagram is not None
        and artifact.certificate is not None
    ):
        score = (
            10 * len(artifact.diagram.nodes)
            + 3 * len(artifact.diagram.terminals)
            + artifact.certificate.depth
        )
        return BackendAttempt(
            backend=_MDD_BACKEND,
            tier="practical",
            status="compiled",
            implementation_kind="mdd",
            reason=None,
            score=score,
            metrics_items=tuple(
                sorted(
                    {
                        "rows": row_count,
                        "nodes": len(artifact.diagram.nodes),
                        "terminals": len(artifact.diagram.terminals),
                        "depth": artifact.certificate.depth,
                        "variable_order": list(artifact.diagram.variable_order),
                        "orders_considered": len(artifact.orders_considered),
                        "certificate_replay": "one_validation_linear_rows",
                    }.items()
                )
            ),
        )
    return BackendAttempt(
        backend=_MDD_BACKEND,
        tier="practical",
        status=artifact.status,
        implementation_kind=None,
        reason=artifact.reason,
        score=None,
        metrics_items=tuple(
            sorted({"rows": row_count, "row_limit": row_limit}.items())
        ),
    )


def _run_exact_tier(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    active: CompilerPortfolioConfig,
    row_count: int,
) -> tuple[BackendAttempt, OriginalSignatureImplementation | None]:
    if active.policy == "mdd_only":
        return (
            _not_applicable_attempt(
                _EXACT_BACKEND,
                "tiny",
                "policy_excluded",
                metrics={"rows": row_count},
            ),
            None,
        )
    tier_config = replace(
        active,
        policy="original_signature",
        enable_exact=active.enable_exact,
        enable_structural=False,
        enable_mdd=False,
        include_shannon_diagnostic=False,
    )
    artifact = compile_single_tier_portfolio(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=table,
        config=tier_config,
    )
    attempt = _attempt_for_backend(artifact, _EXACT_BACKEND)
    implementation = (
        artifact.original_signature
        if artifact.status == "compiled"
        and artifact.selected_backend == _EXACT_BACKEND
        else None
    )
    return attempt, implementation


def _run_structural_tier(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    active: CompilerPortfolioConfig,
    row_count: int,
) -> tuple[BackendAttempt, OriginalSignatureImplementation | None]:
    if active.policy == "mdd_only":
        return (
            _not_applicable_attempt(
                _STRUCTURAL_BACKEND,
                "medium",
                "policy_excluded",
                metrics={"rows": row_count},
            ),
            None,
        )
    if not active.enable_structural:
        return (
            _not_applicable_attempt(
                _STRUCTURAL_BACKEND,
                "medium",
                "disabled",
                metrics={"rows": row_count},
            ),
            None,
        )
    if row_count > _STRUCTURAL_ROW_LIMIT:
        return (
            _not_applicable_attempt(
                _STRUCTURAL_BACKEND,
                "medium",
                "above_structural_table_threshold",
                metrics={
                    "rows": row_count,
                    "row_limit": _STRUCTURAL_ROW_LIMIT,
                },
            ),
            None,
        )

    effective_candidate_limit = min(
        active.structural_candidate_limit,
        max(1, _STRUCTURAL_SCALAR_WORK_BUDGET // max(1, row_count)),
    )
    tier_config = replace(
        active,
        policy="original_signature",
        enable_exact=False,
        enable_structural=True,
        enable_mdd=False,
        include_shannon_diagnostic=False,
        structural_candidate_limit=effective_candidate_limit,
    )
    artifact = compile_single_tier_portfolio(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=table,
        config=tier_config,
    )
    raw_attempt = _attempt_for_backend(artifact, _STRUCTURAL_BACKEND)
    metrics = raw_attempt.metrics
    metrics.update(
        {
            "configured_candidate_limit": active.structural_candidate_limit,
            "effective_candidate_limit": effective_candidate_limit,
            "scalar_work_budget": _STRUCTURAL_SCALAR_WORK_BUDGET,
            "structural_row_limit": _STRUCTURAL_ROW_LIMIT,
        }
    )
    attempt = replace(
        raw_attempt,
        metrics_items=tuple(sorted(metrics.items())),
    )
    implementation = (
        artifact.original_signature
        if artifact.status == "compiled"
        and artifact.selected_backend == _STRUCTURAL_BACKEND
        else None
    )
    return attempt, implementation


def _shannon_attempt(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    row_count: int,
    enabled: bool,
) -> BackendAttempt | None:
    if not enabled:
        return None
    if not is_quackenbush_q(algebra):
        return BackendAttempt(
            backend=_SHANNON_BACKEND,
            tier="research",
            status="not_applicable",
            implementation_kind=None,
            reason="not_exact_quackenbush_q",
            score=None,
        )
    return BackendAttempt(
        backend=_SHANNON_BACKEND,
        tier="research",
        status="diagnostic",
        implementation_kind=None,
        reason="not_materialized_and_never_auto_selected",
        score=None,
        metrics_items=tuple(
            sorted(
                {
                    "input_arity": input_arity,
                    "output_arity": output_arity,
                    "explicit_rows": row_count,
                    "theorem_threshold_r_ge_64": input_arity >= 64,
                    "automatic_selection": False,
                }.items()
            )
        ),
    )


def compile_portfolio_runtime(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    config: CompilerPortfolioConfig | None = None,
) -> CompilerPortfolioArtifact:
    active = CompilerPortfolioConfig() if config is None else config
    row_count = len(algebra.values) ** input_arity

    exact_attempt, exact_implementation = _run_exact_tier(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=table,
        active=active,
        row_count=row_count,
    )

    if exact_implementation is not None and active.policy != "mdd_only":
        structural_attempt = _not_applicable_attempt(
            _STRUCTURAL_BACKEND,
            "medium",
            "higher_priority_tier_succeeded",
            metrics={"rows": row_count},
        )
        structural_implementation = None
    else:
        structural_attempt, structural_implementation = _run_structural_tier(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            active=active,
            row_count=row_count,
        )

    mdd: MDDArtifact | None = None
    higher_original_succeeded = (
        exact_implementation is not None or structural_implementation is not None
    )
    if active.policy == "original_signature":
        mdd_attempt = _not_applicable_attempt(
            _MDD_BACKEND,
            "practical",
            "policy_excluded",
            metrics={"rows": row_count},
        )
    elif active.policy == "practical" and higher_original_succeeded:
        mdd_attempt = _not_applicable_attempt(
            _MDD_BACKEND,
            "practical",
            "higher_priority_tier_succeeded",
            metrics={"rows": row_count},
        )
    elif active.enable_mdd:
        mdd = compile_mdd_artifact_linear(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            row_limit=active.mdd_max_rows,
            order_policy="portfolio",
        )
        mdd_attempt = _mdd_attempt(
            mdd,
            row_count=row_count,
            row_limit=active.mdd_max_rows,
        )
    else:
        mdd_attempt = _not_applicable_attempt(
            _MDD_BACKEND,
            "practical",
            "disabled",
            metrics={"rows": row_count},
        )

    attempts = [exact_attempt, structural_attempt, mdd_attempt]
    shannon = _shannon_attempt(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        row_count=row_count,
        enabled=active.include_shannon_diagnostic,
    )
    if shannon is not None:
        attempts.append(shannon)

    candidates: list[
        tuple[int, str, str, OriginalSignatureImplementation | MDDArtifact]
    ] = []
    if exact_implementation is not None:
        candidates.append(
            (0, _EXACT_BACKEND, "original_signature", exact_implementation)
        )
    if structural_implementation is not None:
        candidates.append(
            (
                1,
                _STRUCTURAL_BACKEND,
                "original_signature",
                structural_implementation,
            )
        )
    if mdd is not None and mdd.status == "compiled":
        candidates.append((2, _MDD_BACKEND, "mdd", mdd))

    if active.policy == "original_signature":
        eligible = [row for row in candidates if row[2] == "original_signature"]
    elif active.policy == "mdd_only":
        eligible = [row for row in candidates if row[2] == "mdd"]
    else:
        eligible = candidates

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

    _priority, backend, kind, implementation = min(eligible)
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


def verify_portfolio_runtime(
    artifact: CompilerPortfolioArtifact,
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow] | None,
) -> bool:
    if artifact.selected_kind != "mdd":
        return verify_base_portfolio(
            artifact,
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
        )
    if (
        artifact.status != "compiled"
        or artifact.selected_backend != _MDD_BACKEND
        or artifact.original_signature is not None
        or artifact.mdd is None
        or table is None
    ):
        return False
    compiled_attempts = {
        (attempt.backend, attempt.implementation_kind)
        for attempt in artifact.attempts
        if attempt.status == "compiled"
    }
    if (_MDD_BACKEND, "mdd") not in compiled_attempts:
        return False
    return verify_mdd_artifact_linear(
        artifact.mdd,
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=table,
    )


__all__ = [
    "compile_portfolio_runtime",
    "not_applicable_portfolio",
    "verify_portfolio_runtime",
]

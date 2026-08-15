"""Independent deterministic selection check for compiler portfolio artifacts."""

from __future__ import annotations

from .compiler_portfolio import CompilerPortfolioArtifact

_PRIORITY = {
    "exact-semantic-closure": 0,
    "fixed-q-structural-router": 1,
    "reduced-vector-mdd": 2,
}
_EXPECTED_TIER = {
    "exact-semantic-closure": "tiny",
    "fixed-q-structural-router": "medium",
    "reduced-vector-mdd": "practical",
    "fixed-q-shannon-experimental": "research",
}
_EXPECTED_KIND = {
    "exact-semantic-closure": "original_signature",
    "fixed-q-structural-router": "original_signature",
    "reduced-vector-mdd": "mdd",
}


def verify_portfolio_selection(artifact: CompilerPortfolioArtifact) -> bool:
    eligible = []
    seen = set()
    for attempt in artifact.attempts:
        if attempt.backend in seen:
            return False
        seen.add(attempt.backend)
        expected_tier = _EXPECTED_TIER.get(attempt.backend)
        if expected_tier is None or attempt.tier != expected_tier:
            return False
        if attempt.backend == "fixed-q-shannon-experimental":
            if (
                attempt.status == "compiled"
                or attempt.score is not None
                or attempt.implementation_kind is not None
            ):
                return False
            continue
        if attempt.status != "compiled":
            if attempt.score is not None or attempt.implementation_kind is not None:
                return False
            continue
        if attempt.score is None:
            return False
        if attempt.implementation_kind != _EXPECTED_KIND[attempt.backend]:
            return False
        if (
            artifact.config.policy == "original_signature"
            and attempt.implementation_kind != "original_signature"
        ):
            continue
        if (
            artifact.config.policy == "mdd_only"
            and attempt.implementation_kind != "mdd"
        ):
            continue
        eligible.append(
            (
                _PRIORITY[attempt.backend],
                attempt.backend,
                attempt.implementation_kind,
            )
        )

    if artifact.status == "not_applicable":
        return (
            artifact.selected_backend is None
            and artifact.selected_kind is None
            and not eligible
            and not artifact.attempts
        )
    if artifact.status == "unsupported":
        return (
            artifact.selected_backend is None
            and artifact.selected_kind is None
            and not eligible
        )
    if artifact.status != "compiled" or not eligible:
        return False
    expected = min(eligible)
    return (
        artifact.selected_backend == expected[1]
        and artifact.selected_kind == expected[2]
    )

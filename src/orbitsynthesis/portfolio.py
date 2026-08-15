"""Public compiler-portfolio API surface."""

from .compiler_portfolio import (
    BackendAttempt,
    CompilerPortfolioArtifact,
    CompilerPortfolioConfig,
    OriginalSignatureImplementation,
)
from .compiler_portfolio_policy import verify_portfolio_selection
from .compiler_portfolio_runtime import (
    compile_portfolio_runtime,
    not_applicable_portfolio,
    verify_portfolio_runtime,
)
from .decision_diagram import (
    MDDArtifact,
    MDDCertificate,
    MDDNode,
    MDDReference,
    ReducedVectorMDD,
    compile_reduced_mdd,
    evaluate_mdd,
    mdd_depth,
    validate_mdd,
)
from .decision_diagram_runtime import (
    certify_mdd_linear,
    compile_mdd_artifact_linear,
    evaluate_valid_mdd,
    verify_mdd_artifact_linear,
)
from .fixed_q_structural import (
    QStructuralCompilation,
    QStructuralStatistics,
    compile_fixed_q_structural,
    is_quackenbush_q,
)
from .portfolio_bundle import (
    PortfolioProofBundle,
    synthesize_portfolio_bundle,
    verify_portfolio_bundle,
)

__all__ = [
    "BackendAttempt",
    "CompilerPortfolioArtifact",
    "CompilerPortfolioConfig",
    "MDDArtifact",
    "MDDCertificate",
    "MDDNode",
    "MDDReference",
    "OriginalSignatureImplementation",
    "PortfolioProofBundle",
    "QStructuralCompilation",
    "QStructuralStatistics",
    "ReducedVectorMDD",
    "certify_mdd_linear",
    "compile_fixed_q_structural",
    "compile_mdd_artifact_linear",
    "compile_portfolio_runtime",
    "compile_reduced_mdd",
    "evaluate_mdd",
    "evaluate_valid_mdd",
    "is_quackenbush_q",
    "mdd_depth",
    "not_applicable_portfolio",
    "synthesize_portfolio_bundle",
    "validate_mdd",
    "verify_mdd_artifact_linear",
    "verify_portfolio_bundle",
    "verify_portfolio_runtime",
    "verify_portfolio_selection",
]

"""OrbitSynthesis standalone finite-algebra research kernel."""

from .discriminator_compile import (
    Const,
    Disc,
    Expr,
    Var,
    compile_table,
    compile_vector_table,
    distinct_node_count,
    evaluate,
    selector,
)
from .finite_algebra import FiniteAlgebra, FiniteOperation, InternalIsomorphism
from .patchability import (
    ExtensionFailure,
    ObstructionHypergraph,
    PatchabilityResult,
    first_extension_failure,
    has_pointed_extension_property,
    hits_all,
    nonextendable_internal_isomorphisms,
    parameter_patchability_number,
    patchability_obstruction_hypergraph,
)
from .safety import FiniteSafetyGame, SafetySolution

__all__ = [
    "Const",
    "Disc",
    "Expr",
    "ExtensionFailure",
    "FiniteAlgebra",
    "FiniteOperation",
    "FiniteSafetyGame",
    "InternalIsomorphism",
    "ObstructionHypergraph",
    "PatchabilityResult",
    "SafetySolution",
    "Var",
    "compile_table",
    "compile_vector_table",
    "distinct_node_count",
    "evaluate",
    "first_extension_failure",
    "has_pointed_extension_property",
    "hits_all",
    "nonextendable_internal_isomorphisms",
    "parameter_patchability_number",
    "patchability_obstruction_hypergraph",
    "selector",
]

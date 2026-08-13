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
from .safety import FiniteSafetyGame, SafetySolution

__all__ = [
    "Const",
    "Disc",
    "Expr",
    "FiniteAlgebra",
    "FiniteOperation",
    "FiniteSafetyGame",
    "InternalIsomorphism",
    "SafetySolution",
    "Var",
    "compile_table",
    "compile_vector_table",
    "distinct_node_count",
    "evaluate",
    "selector",
]

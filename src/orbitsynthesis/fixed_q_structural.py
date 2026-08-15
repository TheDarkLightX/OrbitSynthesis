"""Targeted structural compilation for Quackenbush's three-element algebra.

This backend is deliberately narrower than semantic closure.  It recognizes
projection/unary rails, one discriminator-router layer, and one nested signed
router layer.  The search is target-driven, bounded, and intended for medium
explicit controllers whose structure is simple even when their truth tables
are no longer tiny.

A miss is only ``unsupported_by_structural_templates``.  It is not a
nondefinability result.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Hashable, Mapping

from .finite_algebra import FiniteAlgebra
from .original_signature_dag import (
    ControllerDAGCertificate,
    DagReference,
    OriginalSignatureDAG,
    OriginalSignatureNode,
    certify_controller_dag,
)

Value = Hashable
InputRow = tuple[Value, ...]
OutputRow = tuple[Value, ...]

BACKEND_ID = "fixed-q-structural-router/v1"


@dataclass(frozen=True)
class QStructuralStatistics:
    semantic_functions: int
    candidates_tried: int
    router_terms: int
    depth_reached: int
    candidate_limit: int

    def as_dict(self) -> dict[str, int]:
        return {
            "semantic_functions": self.semantic_functions,
            "candidates_tried": self.candidates_tried,
            "router_terms": self.router_terms,
            "depth_reached": self.depth_reached,
            "candidate_limit": self.candidate_limit,
        }


@dataclass(frozen=True)
class QStructuralCompilation:
    status: str
    reason: str | None
    statistics: QStructuralStatistics
    dag: OriginalSignatureDAG | None
    certificate: ControllerDAGCertificate | None


@dataclass(frozen=True)
class _Term:
    operation: str
    input_index: int | None = None
    arguments: tuple["_Term", ...] = ()


def _q_operations(algebra: FiniteAlgebra):
    if set(algebra.values) != {0, 1, 2}:
        return None
    operations = {operation.name: operation for operation in algebra.operations}
    if set(operations) != {"d", "u"}:
        return None
    disc = operations["d"]
    unary = operations["u"]
    if disc.arity != 3 or unary.arity != 1:
        return None
    for x, y, z in product((0, 1, 2), repeat=3):
        if disc(x, y, z) != (z if x == y else x):
            return None
    expected_u = {0: 1, 1: 0, 2: 1}
    if any(unary(value) != expected_u[value] for value in (0, 1, 2)):
        return None
    return disc, unary


def is_quackenbush_q(algebra: FiniteAlgebra) -> bool:
    return _q_operations(algebra) is not None


def _normalize_table(
    algebra: FiniteAlgebra,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
) -> tuple[tuple[InputRow, ...], dict[InputRow, OutputRow]]:
    if isinstance(input_arity, bool) or not isinstance(input_arity, int) or input_arity < 0:
        raise ValueError("input_arity must be a nonnegative integer")
    if isinstance(output_arity, bool) or not isinstance(output_arity, int) or output_arity < 0:
        raise ValueError("output_arity must be a nonnegative integer")
    carrier = tuple(algebra.values)
    points = tuple(product(carrier, repeat=input_arity))
    if set(table) != set(points):
        raise ValueError("controller table must contain exactly every input row")
    normalized = {}
    carrier_set = set(carrier)
    for point in points:
        output = tuple(table[point])
        if len(output) != output_arity:
            raise ValueError("controller output has wrong arity")
        if not set(output) <= carrier_set:
            raise ValueError("controller output leaves the carrier")
        normalized[point] = output
    return points, normalized


def _apply_disc(
    left: tuple[Value, ...],
    middle: tuple[Value, ...],
    right: tuple[Value, ...],
) -> tuple[Value, ...]:
    return tuple(
        z if x == y else x
        for x, y, z in zip(left, middle, right, strict=True)
    )


def _apply_unary(values: tuple[Value, ...]) -> tuple[Value, ...]:
    return tuple(0 if value == 1 else 1 for value in values)


def _emit_dag(
    algebra: FiniteAlgebra,
    input_arity: int,
    roots: tuple[_Term, ...],
) -> OriginalSignatureDAG:
    nodes: list[OriginalSignatureNode] = []
    node_index: dict[tuple[str, tuple[DagReference, ...]], int] = {}

    def emit(term: _Term) -> DagReference:
        if term.operation == "input":
            if term.input_index is None:
                raise AssertionError("input term lost its index")
            return DagReference("input", term.input_index)
        arguments = tuple(emit(argument) for argument in term.arguments)
        key = (term.operation, arguments)
        existing = node_index.get(key)
        if existing is not None:
            return DagReference("node", existing)
        index = len(nodes)
        nodes.append(
            OriginalSignatureNode(
                operation=term.operation,
                arguments=arguments,
            )
        )
        node_index[key] = index
        return DagReference("node", index)

    root_refs = tuple(emit(root) for root in roots)
    return OriginalSignatureDAG(
        input_arity=input_arity,
        output_arity=len(roots),
        signature=tuple(
            sorted((operation.name, operation.arity) for operation in algebra.operations)
        ),
        nodes=tuple(nodes),
        roots=root_refs,
    )


def compile_fixed_q_structural(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    candidate_limit: int = 400_000,
) -> QStructuralCompilation:
    """Recognize a bounded family of fixed-Q signed-router terms.

    Recognized templates are shared across output coordinates:

    * input projections;
    * ``u(projection)``;
    * ``d(a,b,c)`` with rails ``a,b,c`` chosen from those bases;
    * ``u(d(a,b,c))``;
    * one nested router layer with a prior router in any argument position,
      prioritizing the payload/right argument.
    """

    if isinstance(candidate_limit, bool) or not isinstance(candidate_limit, int) or candidate_limit < 1:
        raise ValueError("candidate_limit must be a positive integer")
    q_operations = _q_operations(algebra)
    if q_operations is None:
        return QStructuralCompilation(
            status="not_applicable",
            reason="not_exact_quackenbush_q",
            statistics=QStructuralStatistics(0, 0, 0, 0, candidate_limit),
            dag=None,
            certificate=None,
        )

    points, normalized = _normalize_table(
        algebra,
        input_arity,
        output_arity,
        table,
    )
    targets = tuple(
        tuple(normalized[point][coordinate] for point in points)
        for coordinate in range(output_arity)
    )
    if not targets:
        dag = OriginalSignatureDAG(
            input_arity=input_arity,
            output_arity=0,
            signature=tuple(
                sorted((operation.name, operation.arity) for operation in algebra.operations)
            ),
            nodes=(),
            roots=(),
        )
        certificate = certify_controller_dag(
            algebra,
            input_arity=input_arity,
            output_arity=0,
            table=normalized,
            dag=dag,
        )
        return QStructuralCompilation(
            status="compiled",
            reason=None,
            statistics=QStructuralStatistics(input_arity, 0, 0, 0, candidate_limit),
            dag=dag,
            certificate=certificate,
        )

    term_by_semantic: dict[tuple[Value, ...], _Term] = {}
    depth_by_semantic: dict[tuple[Value, ...], int] = {}
    target_terms: dict[tuple[Value, ...], _Term] = {}
    target_set = set(targets)
    candidates_tried = 0
    router_semantics: list[tuple[Value, ...]] = []

    def register(
        semantic: tuple[Value, ...],
        term: _Term,
        depth: int,
        *,
        router: bool = False,
    ) -> None:
        if semantic not in term_by_semantic:
            term_by_semantic[semantic] = term
            depth_by_semantic[semantic] = depth
            if router:
                router_semantics.append(semantic)
        if semantic in target_set and semantic not in target_terms:
            target_terms[semantic] = term_by_semantic[semantic]

    for index in range(input_arity):
        semantic = tuple(point[index] for point in points)
        register(
            semantic,
            _Term(operation="input", input_index=index),
            0,
        )
    input_semantics = tuple(term_by_semantic)
    for semantic in input_semantics:
        unary_semantic = _apply_unary(semantic)
        register(
            unary_semantic,
            _Term(operation="u", arguments=(term_by_semantic[semantic],)),
            1,
        )
    base_semantics = tuple(term_by_semantic)

    def exhausted() -> bool:
        return all(target in target_terms for target in targets)

    if not exhausted():
        stop = False
        for left in base_semantics:
            if stop:
                break
            for middle in base_semantics:
                if stop:
                    break
                for right in base_semantics:
                    candidates_tried += 1
                    if candidates_tried > candidate_limit:
                        stop = True
                        break
                    semantic = _apply_disc(left, middle, right)
                    term = _Term(
                        operation="d",
                        arguments=(
                            term_by_semantic[left],
                            term_by_semantic[middle],
                            term_by_semantic[right],
                        ),
                    )
                    register(semantic, term, 1, router=True)
                    unary_semantic = _apply_unary(semantic)
                    register(
                        unary_semantic,
                        _Term(operation="u", arguments=(term_by_semantic[semantic],)),
                        2,
                    )
                    if exhausted():
                        stop = True
                        break

    if not exhausted() and candidates_tried <= candidate_limit:
        # A signed router typically carries its continuation in the third
        # argument, so try that shape before the two symmetric alternatives.
        inner_semantics = tuple(router_semantics)
        stop = False
        for inner_position in (2, 0, 1):
            if stop:
                break
            for inner in inner_semantics:
                if stop:
                    break
                for first in base_semantics:
                    if stop:
                        break
                    for second in base_semantics:
                        candidates_tried += 1
                        if candidates_tried > candidate_limit:
                            stop = True
                            break
                        arguments = [first, second]
                        arguments.insert(inner_position, inner)
                        left, middle, right = arguments
                        semantic = _apply_disc(left, middle, right)
                        term = _Term(
                            operation="d",
                            arguments=tuple(
                                term_by_semantic[value] for value in arguments
                            ),
                        )
                        register(semantic, term, 2)
                        unary_semantic = _apply_unary(semantic)
                        register(
                            unary_semantic,
                            _Term(operation="u", arguments=(term_by_semantic[semantic],)),
                            3,
                        )
                        if exhausted():
                            stop = True
                            break

    statistics = QStructuralStatistics(
        semantic_functions=len(term_by_semantic),
        candidates_tried=min(candidates_tried, candidate_limit),
        router_terms=len(router_semantics),
        depth_reached=max(depth_by_semantic.values(), default=0),
        candidate_limit=candidate_limit,
    )
    if not exhausted():
        reason = (
            "candidate_limit"
            if candidates_tried > candidate_limit
            else "unsupported_by_structural_templates"
        )
        return QStructuralCompilation(
            status="unsupported",
            reason=reason,
            statistics=statistics,
            dag=None,
            certificate=None,
        )

    roots = tuple(target_terms[target] for target in targets)
    dag = _emit_dag(algebra, input_arity, roots)
    certificate = certify_controller_dag(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=normalized,
        dag=dag,
    )
    return QStructuralCompilation(
        status="compiled",
        reason=None,
        statistics=statistics,
        dag=dag,
        certificate=certificate,
    )

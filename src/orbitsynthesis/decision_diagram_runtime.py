"""One-validation runtime for reduced MDD artifacts.

The wire types and builder live in :mod:`decision_diagram`.  This companion
keeps exhaustive certification linear in the explicit truth-table size by
validating the diagram once and then replaying rows through a precomputed
carrier index.  The public per-call evaluator remains defensive.
"""

from __future__ import annotations

import hashlib
from itertools import product
import json
from typing import Hashable, Mapping, Sequence

from .decision_diagram import (
    MDDArtifact,
    MDDCertificate,
    ReducedVectorMDD,
    compile_reduced_mdd,
    mdd_depth,
    validate_mdd,
)
from .finite_algebra import FiniteAlgebra
from .original_signature_dag import (
    algebra_semantic_sha256,
    strategy_semantic_sha256,
)

Value = Hashable
InputRow = tuple[Value, ...]
OutputRow = tuple[Value, ...]
_COMPILER = "reduced-ordered-mdd/v1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=repr,
    ).encode("utf-8")


def _normalize_table(
    algebra: FiniteAlgebra,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
) -> tuple[tuple[InputRow, ...], dict[InputRow, OutputRow]]:
    if (
        isinstance(input_arity, bool)
        or not isinstance(input_arity, int)
        or input_arity < 0
    ):
        raise ValueError("input_arity must be a nonnegative integer")
    if (
        isinstance(output_arity, bool)
        or not isinstance(output_arity, int)
        or output_arity < 0
    ):
        raise ValueError("output_arity must be a nonnegative integer")
    carrier = tuple(algebra.values)
    carrier_set = set(carrier)
    points = tuple(product(carrier, repeat=input_arity))
    if set(table) != set(points):
        raise ValueError("controller table must contain exactly every input row")
    normalized: dict[InputRow, OutputRow] = {}
    for point in points:
        output = tuple(table[point])
        if len(output) != output_arity:
            raise ValueError("controller output has wrong arity")
        if not set(output) <= carrier_set:
            raise ValueError("controller output leaves the carrier")
        normalized[point] = output
    return points, normalized


def evaluate_valid_mdd(
    diagram: ReducedVectorMDD,
    arguments: Sequence[Value],
    *,
    carrier_index: Mapping[Value, int] | None = None,
) -> OutputRow:
    """Evaluate an already validated MDD without repeating graph validation."""

    if len(arguments) != diagram.input_arity:
        raise ValueError("MDD input row has wrong arity")
    index = (
        {value: position for position, value in enumerate(diagram.carrier)}
        if carrier_index is None
        else carrier_index
    )
    try:
        reference = diagram.root
        while reference.kind == "node":
            node = diagram.nodes[reference.index]
            reference = node.children[index[arguments[node.variable]]]
        return diagram.terminals[reference.index]
    except KeyError as error:
        raise ValueError("MDD input contains value outside carrier") from error


def certify_mdd_linear(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    diagram: ReducedVectorMDD,
) -> MDDCertificate:
    points, normalized = _normalize_table(
        algebra,
        input_arity,
        output_arity,
        table,
    )
    if not validate_mdd(diagram):
        raise ValueError("invalid MDD")
    if tuple(diagram.carrier) != tuple(algebra.values):
        raise ValueError("MDD carrier order disagrees with finite algebra")
    if diagram.input_arity != input_arity or diagram.output_arity != output_arity:
        raise ValueError("MDD arity disagrees with controller table")

    carrier_index = {
        value: position for position, value in enumerate(diagram.carrier)
    }
    rows = []
    for point in points:
        expected = normalized[point]
        actual = evaluate_valid_mdd(
            diagram,
            point,
            carrier_index=carrier_index,
        )
        if actual != expected:
            raise ValueError(
                f"MDD mismatch at {point!r}: {actual!r}!={expected!r}"
            )
        rows.append(
            {
                "input": list(point),
                "expected": list(expected),
                "actual": list(actual),
            }
        )
    return MDDCertificate(
        algebra_sha256=algebra_semantic_sha256(algebra),
        strategy_sha256=strategy_semantic_sha256(
            algebra,
            input_arity,
            output_arity,
            normalized,
        ),
        mdd_sha256=diagram.semantic_sha256,
        rows_checked=len(points),
        node_count=len(diagram.nodes),
        terminal_count=len(diagram.terminals),
        depth=mdd_depth(diagram),
        evaluation_sha256=hashlib.sha256(_canonical_bytes(rows)).hexdigest(),
    )


def compile_mdd_artifact_linear(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    row_limit: int = 250_000,
    order_policy: str = "portfolio",
) -> MDDArtifact:
    if (
        isinstance(row_limit, bool)
        or not isinstance(row_limit, int)
        or row_limit < 1
    ):
        raise ValueError("MDD row_limit must be a positive integer")
    row_count = len(algebra.values) ** input_arity
    if row_count > row_limit:
        return MDDArtifact(
            status="unsupported",
            compiler=_COMPILER,
            reason="explicit_table_row_limit",
            diagram=None,
            certificate=None,
            row_limit=row_limit,
            orders_considered=(),
        )
    diagram, orders = compile_reduced_mdd(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=table,
        order_policy=order_policy,
    )
    certificate = certify_mdd_linear(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=table,
        diagram=diagram,
    )
    return MDDArtifact(
        status="compiled",
        compiler=_COMPILER,
        reason=None,
        diagram=diagram,
        certificate=certificate,
        row_limit=row_limit,
        orders_considered=orders,
    )


def verify_mdd_artifact_linear(
    artifact: MDDArtifact,
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow] | None,
) -> bool:
    if artifact.compiler != _COMPILER:
        return False
    if artifact.status == "not_applicable":
        return (
            table is None
            and artifact.diagram is None
            and artifact.certificate is None
            and not artifact.orders_considered
        )
    if table is None:
        return False
    if artifact.status == "unsupported":
        return (
            artifact.diagram is None
            and artifact.certificate is None
            and not artifact.orders_considered
        )
    if (
        artifact.status != "compiled"
        or artifact.diagram is None
        or artifact.certificate is None
    ):
        return False
    if len(set(artifact.orders_considered)) != len(artifact.orders_considered):
        return False
    if artifact.diagram.variable_order not in artifact.orders_considered:
        return False
    if len(algebra.values) ** input_arity > artifact.row_limit:
        return False
    try:
        return artifact.certificate == certify_mdd_linear(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            diagram=artifact.diagram,
        )
    except (KeyError, TypeError, ValueError):
        return False

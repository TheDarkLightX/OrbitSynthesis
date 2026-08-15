"""Original-signature controller DAGs and exact finite-table compilation.

The compiler is intentionally bounded.  It searches the semantic closure of the
declared basic operations starting from input projections.  Every successful
artifact is therefore an original-signature term DAG: there are no ad-hoc
constants, selector primitives, or hidden lookup-table nodes.

Failure to find a term inside the declared bounds is reported as
``unsupported``.  It is not a proof that no term exists.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import product
import json
from typing import Hashable, Iterable, Mapping, Sequence

from .finite_algebra import FiniteAlgebra

Value = Hashable
InputRow = tuple[Value, ...]
OutputRow = tuple[Value, ...]

_DAG_SCHEMA = "orbit-synthesis/original-signature-dag/v1"
_CERT_SCHEMA = "orbit-synthesis/controller-dag-equivalence/v1"
_ARTIFACT_SCHEMA = "orbit-synthesis/controller-dag-artifact/v1"
_COMPILER = "bounded-semantic-closure/v1"


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
class DagReference:
    kind: str
    index: int

    def as_dict(self) -> dict[str, object]:
        return {"kind": self.kind, "index": self.index}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "DagReference":
        _exact_keys(payload, frozenset(("kind", "index")), field="DAG reference")
        kind = payload["kind"]
        if kind not in {"input", "node"}:
            raise ValueError("DAG reference kind must be input or node")
        return cls(
            kind=str(kind),
            index=_integer(payload["index"], field="DAG reference index"),
        )


@dataclass(frozen=True)
class OriginalSignatureNode:
    operation: str
    arguments: tuple[DagReference, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "arguments": [argument.as_dict() for argument in self.arguments],
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "OriginalSignatureNode":
        _exact_keys(
            payload,
            frozenset(("operation", "arguments")),
            field="DAG node",
        )
        operation = payload["operation"]
        arguments = payload["arguments"]
        if not isinstance(operation, str) or not operation:
            raise ValueError("DAG operation must be a nonempty string")
        if not isinstance(arguments, list):
            raise TypeError("DAG node arguments must be a list")
        parsed_arguments = []
        for index, argument in enumerate(arguments):
            if not isinstance(argument, Mapping):
                raise TypeError(f"DAG node argument {index} must be an object")
            parsed_arguments.append(DagReference.from_dict(argument))
        return cls(
            operation=operation,
            arguments=tuple(parsed_arguments),
        )


@dataclass(frozen=True)
class OriginalSignatureDAG:
    input_arity: int
    output_arity: int
    signature: tuple[tuple[str, int], ...]
    nodes: tuple[OriginalSignatureNode, ...]
    roots: tuple[DagReference, ...]

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _DAG_SCHEMA,
            "input_arity": self.input_arity,
            "output_arity": self.output_arity,
            "signature": [
                {"name": name, "arity": arity}
                for name, arity in self.signature
            ],
            "nodes": [node.as_dict() for node in self.nodes],
            "roots": [root.as_dict() for root in self.roots],
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
        cls,
        payload: Mapping[str, object],
    ) -> "OriginalSignatureDAG":
        _exact_keys(
            payload,
            frozenset(
                (
                    "schema",
                    "input_arity",
                    "output_arity",
                    "signature",
                    "nodes",
                    "roots",
                    "semantic_sha256",
                )
            ),
            field="original-signature DAG",
        )
        if payload["schema"] != _DAG_SCHEMA:
            raise ValueError("unsupported original-signature DAG schema")
        signature_payload = payload["signature"]
        nodes_payload = payload["nodes"]
        roots_payload = payload["roots"]
        if not isinstance(signature_payload, list):
            raise TypeError("DAG signature must be a list")
        signature = []
        for index, row in enumerate(signature_payload):
            if not isinstance(row, Mapping):
                raise TypeError(f"DAG signature row {index} must be an object")
            _exact_keys(
                row,
                frozenset(("name", "arity")),
                field=f"DAG signature row {index}",
            )
            name = row["name"]
            if not isinstance(name, str) or not name:
                raise ValueError(f"DAG signature row {index} has invalid name")
            signature.append(
                (name, _integer(row["arity"], field=f"DAG signature row {index} arity"))
            )
        if not isinstance(nodes_payload, list):
            raise TypeError("DAG nodes must be a list")
        nodes = []
        for index, row in enumerate(nodes_payload):
            if not isinstance(row, Mapping):
                raise TypeError(f"DAG node {index} must be an object")
            nodes.append(OriginalSignatureNode.from_dict(row))
        if not isinstance(roots_payload, list):
            raise TypeError("DAG roots must be a list")
        roots = []
        for index, row in enumerate(roots_payload):
            if not isinstance(row, Mapping):
                raise TypeError(f"DAG root {index} must be an object")
            roots.append(DagReference.from_dict(row))
        dag = cls(
            input_arity=_integer(payload["input_arity"], field="DAG input_arity"),
            output_arity=_integer(payload["output_arity"], field="DAG output_arity"),
            signature=tuple(signature),
            nodes=tuple(nodes),
            roots=tuple(roots),
        )
        recorded = payload["semantic_sha256"]
        if not isinstance(recorded, str) or recorded != dag.semantic_sha256:
            raise ValueError("original-signature DAG semantic hash mismatch")
        return dag


@dataclass(frozen=True)
class CompilationLimits:
    max_depth: int = 3
    max_semantic_functions: int = 10_000
    max_combinations: int = 500_000
    max_exploration_nodes: int = 50_000
    max_operation_arity: int = 4

    def __post_init__(self) -> None:
        for field, value in self.as_dict().items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{field} must be a positive integer")

    def as_dict(self) -> dict[str, int]:
        return {
            "max_depth": self.max_depth,
            "max_semantic_functions": self.max_semantic_functions,
            "max_combinations": self.max_combinations,
            "max_exploration_nodes": self.max_exploration_nodes,
            "max_operation_arity": self.max_operation_arity,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "CompilationLimits":
        expected = frozenset(
            (
                "max_depth",
                "max_semantic_functions",
                "max_combinations",
                "max_exploration_nodes",
                "max_operation_arity",
            )
        )
        _exact_keys(payload, expected, field="DAG compilation limits")
        return cls(
            **{
                key: _integer(payload[key], field=f"DAG compilation limit {key}", minimum=1)
                for key in expected
            }
        )


@dataclass(frozen=True)
class CompilationStatistics:
    semantic_functions: int = 0
    combinations_tried: int = 0
    exploration_nodes: int = 0
    depth_reached: int = 0
    skipped_operations: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "semantic_functions": self.semantic_functions,
            "combinations_tried": self.combinations_tried,
            "exploration_nodes": self.exploration_nodes,
            "depth_reached": self.depth_reached,
            "skipped_operations": self.skipped_operations,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "CompilationStatistics":
        expected = frozenset(
            (
                "semantic_functions",
                "combinations_tried",
                "exploration_nodes",
                "depth_reached",
                "skipped_operations",
            )
        )
        _exact_keys(payload, expected, field="DAG compilation statistics")
        return cls(
            **{
                key: _integer(payload[key], field=f"DAG compilation statistic {key}")
                for key in expected
            }
        )


class OriginalSignatureCompilationError(ValueError):
    def __init__(
        self,
        reason: str,
        statistics: CompilationStatistics,
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.statistics = statistics


@dataclass(frozen=True)
class ControllerDAGCertificate:
    algebra_sha256: str
    strategy_sha256: str
    dag_sha256: str
    rows_checked: int
    output_arity: int
    node_count: int
    depth: int
    evaluation_sha256: str

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _CERT_SCHEMA,
            "algebra_sha256": self.algebra_sha256,
            "strategy_sha256": self.strategy_sha256,
            "dag_sha256": self.dag_sha256,
            "rows_checked": self.rows_checked,
            "output_arity": self.output_arity,
            "node_count": self.node_count,
            "depth": self.depth,
            "evaluation_sha256": self.evaluation_sha256,
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
        cls,
        payload: Mapping[str, object],
    ) -> "ControllerDAGCertificate":
        expected = frozenset(
            (
                "schema",
                "algebra_sha256",
                "strategy_sha256",
                "dag_sha256",
                "rows_checked",
                "output_arity",
                "node_count",
                "depth",
                "evaluation_sha256",
                "semantic_sha256",
            )
        )
        _exact_keys(payload, expected, field="controller DAG certificate")
        if payload["schema"] != _CERT_SCHEMA:
            raise ValueError("unsupported controller DAG certificate schema")
        certificate = cls(
            algebra_sha256=str(payload["algebra_sha256"]),
            strategy_sha256=str(payload["strategy_sha256"]),
            dag_sha256=str(payload["dag_sha256"]),
            rows_checked=_integer(payload["rows_checked"], field="rows_checked"),
            output_arity=_integer(payload["output_arity"], field="output_arity"),
            node_count=_integer(payload["node_count"], field="node_count"),
            depth=_integer(payload["depth"], field="depth"),
            evaluation_sha256=str(payload["evaluation_sha256"]),
        )
        for field in (
            certificate.algebra_sha256,
            certificate.strategy_sha256,
            certificate.dag_sha256,
            certificate.evaluation_sha256,
        ):
            if len(field) != 64 or any(char not in "0123456789abcdef" for char in field):
                raise ValueError("controller DAG certificate contains malformed SHA-256")
        if payload["semantic_sha256"] != certificate.semantic_sha256:
            raise ValueError("controller DAG certificate semantic hash mismatch")
        return certificate


@dataclass(frozen=True)
class OriginalSignatureArtifact:
    status: str
    compiler: str
    limits: CompilationLimits
    statistics: CompilationStatistics
    reason: str | None
    dag: OriginalSignatureDAG | None
    certificate: ControllerDAGCertificate | None

    def semantic_payload(self) -> dict[str, object]:
        return {
            "schema": _ARTIFACT_SCHEMA,
            "status": self.status,
            "compiler": self.compiler,
            "limits": self.limits.as_dict(),
            "statistics": self.statistics.as_dict(),
            "reason": self.reason,
            "dag": None if self.dag is None else self.dag.as_dict(),
            "certificate": (
                None if self.certificate is None else self.certificate.as_dict()
            ),
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
        cls,
        payload: Mapping[str, object],
    ) -> "OriginalSignatureArtifact":
        expected = frozenset(
            (
                "schema",
                "status",
                "compiler",
                "limits",
                "statistics",
                "reason",
                "dag",
                "certificate",
                "semantic_sha256",
            )
        )
        _exact_keys(payload, expected, field="controller DAG artifact")
        if payload["schema"] != _ARTIFACT_SCHEMA:
            raise ValueError("unsupported controller DAG artifact schema")
        if payload["status"] not in {"compiled", "unsupported", "not_applicable"}:
            raise ValueError("invalid controller DAG artifact status")
        if payload["compiler"] != _COMPILER:
            raise ValueError("unsupported original-signature compiler identifier")
        limits_payload = payload["limits"]
        statistics_payload = payload["statistics"]
        if not isinstance(limits_payload, Mapping):
            raise TypeError("controller DAG limits must be an object")
        if not isinstance(statistics_payload, Mapping):
            raise TypeError("controller DAG statistics must be an object")
        dag_payload = payload["dag"]
        certificate_payload = payload["certificate"]
        dag = None
        certificate = None
        if dag_payload is not None:
            if not isinstance(dag_payload, Mapping):
                raise TypeError("controller DAG must be an object or null")
            dag = OriginalSignatureDAG.from_dict(dag_payload)
        if certificate_payload is not None:
            if not isinstance(certificate_payload, Mapping):
                raise TypeError("controller DAG certificate must be an object or null")
            certificate = ControllerDAGCertificate.from_dict(certificate_payload)
        reason = payload["reason"]
        if reason is not None and (not isinstance(reason, str) or not reason):
            raise ValueError("controller DAG reason must be null or nonempty")
        artifact = cls(
            status=str(payload["status"]),
            compiler=str(payload["compiler"]),
            limits=CompilationLimits.from_dict(limits_payload),
            statistics=CompilationStatistics.from_dict(statistics_payload),
            reason=reason,
            dag=dag,
            certificate=certificate,
        )
        if artifact.status == "compiled":
            if artifact.dag is None or artifact.certificate is None or artifact.reason is not None:
                raise ValueError("compiled artifact must contain DAG and certificate")
        else:
            if artifact.dag is not None or artifact.certificate is not None:
                raise ValueError("noncompiled artifact cannot contain DAG or certificate")
            if artifact.reason is None:
                raise ValueError("noncompiled artifact requires a reason")
        if payload["semantic_sha256"] != artifact.semantic_sha256:
            raise ValueError("controller DAG artifact semantic hash mismatch")
        return artifact


def algebra_semantic_sha256(algebra: FiniteAlgebra) -> str:
    carrier = tuple(algebra.values)
    operations = []
    for operation in sorted(algebra.operations, key=lambda row: (row.name, row.arity)):
        operations.append(
            {
                "name": operation.name,
                "arity": operation.arity,
                "outputs": [
                    operation(*arguments)
                    for arguments in product(carrier, repeat=operation.arity)
                ],
            }
        )
    payload = {"carrier": list(carrier), "operations": operations}
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def strategy_semantic_sha256(
    algebra: FiniteAlgebra,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
) -> str:
    points, normalized = _normalized_table(
        algebra,
        input_arity,
        output_arity,
        table,
    )
    payload = [
        {"input": list(point), "output": list(normalized[point])}
        for point in points
    ]
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _normalized_table(
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
    carrier_set = set(carrier)
    points = tuple(product(carrier, repeat=input_arity))
    expected = set(points)
    if set(table) != expected:
        raise ValueError(
            "controller table must contain exactly every carrier input point"
        )
    normalized: dict[InputRow, OutputRow] = {}
    for point in points:
        output = tuple(table[point])
        if len(output) != output_arity:
            raise ValueError("controller output has wrong arity")
        if not set(output) <= carrier_set:
            raise ValueError("controller output leaves the algebra carrier")
        normalized[point] = output
    return points, normalized


def _validate_reference(
    reference: DagReference,
    *,
    input_arity: int,
    node_limit: int,
) -> bool:
    if reference.kind == "input":
        return 0 <= reference.index < input_arity
    return reference.kind == "node" and 0 <= reference.index < node_limit


def dag_depth(dag: OriginalSignatureDAG) -> int:
    depths: list[int] = []
    def reference_depth(reference: DagReference) -> int:
        return 0 if reference.kind == "input" else depths[reference.index]
    for node in dag.nodes:
        depths.append(
            1 + max((reference_depth(argument) for argument in node.arguments), default=0)
        )
    return max((reference_depth(root) for root in dag.roots), default=0)


def validate_original_signature_dag(
    algebra: FiniteAlgebra,
    dag: OriginalSignatureDAG,
) -> bool:
    operations = tuple(sorted(algebra.operations, key=lambda row: (row.name, row.arity)))
    if len({operation.name for operation in operations}) != len(operations):
        return False
    expected_signature = tuple(
        sorted((operation.name, operation.arity) for operation in operations)
    )
    if dag.signature != expected_signature:
        return False
    if len(dag.roots) != dag.output_arity:
        return False
    operation_by_name = {operation.name: operation for operation in operations}
    for index, node in enumerate(dag.nodes):
        operation = operation_by_name.get(node.operation)
        if operation is None or len(node.arguments) != operation.arity:
            return False
        if not all(
            _validate_reference(
                argument,
                input_arity=dag.input_arity,
                node_limit=index,
            )
            for argument in node.arguments
        ):
            return False
    if not all(
        _validate_reference(
            root,
            input_arity=dag.input_arity,
            node_limit=len(dag.nodes),
        )
        for root in dag.roots
    ):
        return False
    reachable: set[int] = set()
    def visit(reference: DagReference) -> None:
        if reference.kind == "input" or reference.index in reachable:
            return
        reachable.add(reference.index)
        for argument in dag.nodes[reference.index].arguments:
            visit(argument)
    for root in dag.roots:
        visit(root)
    return reachable == set(range(len(dag.nodes)))


def evaluate_original_signature_dag(
    algebra: FiniteAlgebra,
    dag: OriginalSignatureDAG,
    arguments: Sequence[Value],
) -> OutputRow:
    if len(arguments) != dag.input_arity:
        raise ValueError("DAG input row has wrong arity")
    if not validate_original_signature_dag(algebra, dag):
        raise ValueError("invalid original-signature DAG")
    operations = {operation.name: operation for operation in algebra.operations}
    values: list[Value] = []
    def value(reference: DagReference) -> Value:
        return (
            arguments[reference.index]
            if reference.kind == "input"
            else values[reference.index]
        )
    for node in dag.nodes:
        operation = operations[node.operation]
        values.append(operation(*(value(argument) for argument in node.arguments)))
    return tuple(value(root) for root in dag.roots)


def _extract_reachable_dag(
    *,
    input_arity: int,
    output_arity: int,
    signature: tuple[tuple[str, int], ...],
    exploration_nodes: list[OriginalSignatureNode],
    roots: tuple[DagReference, ...],
) -> OriginalSignatureDAG:
    reachable: set[int] = set()
    def visit(reference: DagReference) -> None:
        if reference.kind == "input" or reference.index in reachable:
            return
        reachable.add(reference.index)
        for argument in exploration_nodes[reference.index].arguments:
            visit(argument)
    for root in roots:
        visit(root)
    order = tuple(sorted(reachable))
    remap = {old: new for new, old in enumerate(order)}
    nodes = []
    for old in order:
        node = exploration_nodes[old]
        nodes.append(
            OriginalSignatureNode(
                operation=node.operation,
                arguments=tuple(
                    DagReference(
                        argument.kind,
                        (
                            argument.index
                            if argument.kind == "input"
                            else remap[argument.index]
                        ),
                    )
                    for argument in node.arguments
                ),
            )
        )
    remapped_roots = tuple(
        DagReference(
            root.kind,
            root.index if root.kind == "input" else remap[root.index],
        )
        for root in roots
    )
    return OriginalSignatureDAG(
        input_arity=input_arity,
        output_arity=output_arity,
        signature=signature,
        nodes=tuple(nodes),
        roots=remapped_roots,
    )


def compile_original_signature_dag(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    limits: CompilationLimits | None = None,
) -> tuple[OriginalSignatureDAG, CompilationStatistics]:
    """Search bounded semantic term closure and return a shared multi-output DAG."""

    active_limits = CompilationLimits() if limits is None else limits
    points, normalized = _normalized_table(
        algebra,
        input_arity,
        output_arity,
        table,
    )
    target_signatures = tuple(
        tuple(normalized[point][coordinate] for point in points)
        for coordinate in range(output_arity)
    )
    search_operations = tuple(
        sorted(algebra.operations, key=lambda row: (row.arity, row.name))
    )
    if len({operation.name for operation in search_operations}) != len(search_operations):
        raise ValueError("basic operation names must be unique")
    signature = tuple(
        sorted((operation.name, operation.arity) for operation in search_operations)
    )

    best: dict[tuple[Value, ...], DagReference] = {}
    depths: dict[tuple[Value, ...], int] = {}
    exploration_nodes: list[OriginalSignatureNode] = []
    node_index: dict[tuple[str, tuple[DagReference, ...]], int] = {}
    combinations_tried = 0
    skipped_operations = sum(
        operation.arity > active_limits.max_operation_arity
        for operation in search_operations
    )
    depth_reached = 0

    def statistics() -> CompilationStatistics:
        return CompilationStatistics(
            semantic_functions=len(best),
            combinations_tried=combinations_tried,
            exploration_nodes=len(exploration_nodes),
            depth_reached=depth_reached,
            skipped_operations=skipped_operations,
        )

    def add(
        semantic: tuple[Value, ...],
        reference: DagReference,
        depth: int,
    ) -> None:
        if semantic not in best:
            best[semantic] = reference
            depths[semantic] = depth

    for index in range(input_arity):
        add(
            tuple(point[index] for point in points),
            DagReference("input", index),
            0,
        )
    if len(best) > active_limits.max_semantic_functions:
        raise OriginalSignatureCompilationError(
            "semantic_function_limit",
            statistics(),
        )

    if all(target in best for target in target_signatures):
        roots = tuple(best[target] for target in target_signatures)
        return (
            _extract_reachable_dag(
                input_arity=input_arity,
                output_arity=output_arity,
                signature=signature,
                exploration_nodes=exploration_nodes,
                roots=roots,
            ),
            statistics(),
        )

    def intern(
        operation_name: str,
        arguments: tuple[DagReference, ...],
    ) -> DagReference:
        key = (operation_name, arguments)
        existing = node_index.get(key)
        if existing is not None:
            return DagReference("node", existing)
        if len(exploration_nodes) >= active_limits.max_exploration_nodes:
            raise OriginalSignatureCompilationError(
                "exploration_node_limit",
                statistics(),
            )
        index = len(exploration_nodes)
        exploration_nodes.append(
            OriginalSignatureNode(
                operation=operation_name,
                arguments=arguments,
            )
        )
        node_index[key] = index
        return DagReference("node", index)

    for depth in range(1, active_limits.max_depth + 1):
        depth_reached = depth
        semantic_snapshot = tuple(best)
        found = False
        for operation in search_operations:
            if operation.arity > active_limits.max_operation_arity:
                continue
            if operation.arity == 0:
                if depth != 1:
                    continue
                argument_rows: Iterable[tuple[tuple[Value, ...], ...]] = ((),)
            else:
                eligible = tuple(
                    semantic
                    for semantic in semantic_snapshot
                    if depths[semantic] <= depth - 1
                )
                argument_rows = product(eligible, repeat=operation.arity)

            for semantics in argument_rows:
                if operation.arity and max(depths[row] for row in semantics) != depth - 1:
                    continue
                combinations_tried += 1
                if combinations_tried > active_limits.max_combinations:
                    raise OriginalSignatureCompilationError(
                        "combination_limit",
                        statistics(),
                    )
                output_semantic = tuple(
                    operation(
                        *(semantic[row_index] for semantic in semantics)
                    )
                    for row_index in range(len(points))
                )
                if output_semantic in best:
                    continue
                reference = intern(
                    operation.name,
                    tuple(best[semantic] for semantic in semantics),
                )
                add(output_semantic, reference, depth)
                if len(best) > active_limits.max_semantic_functions:
                    raise OriginalSignatureCompilationError(
                        "semantic_function_limit",
                        statistics(),
                    )
                if all(target in best for target in target_signatures):
                    found = True
                    break
            if found:
                break
        if found:
            break

    if not all(target in best for target in target_signatures):
        reason = (
            "operation_arity_limit"
            if skipped_operations == len(search_operations) and search_operations
            else "bounded_search_exhausted"
        )
        raise OriginalSignatureCompilationError(reason, statistics())

    roots = tuple(best[target] for target in target_signatures)
    dag = _extract_reachable_dag(
        input_arity=input_arity,
        output_arity=output_arity,
        signature=signature,
        exploration_nodes=exploration_nodes,
        roots=roots,
    )
    if not validate_original_signature_dag(algebra, dag):
        raise AssertionError("compiler produced an invalid original-signature DAG")
    return dag, statistics()


def certify_controller_dag(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    dag: OriginalSignatureDAG,
) -> ControllerDAGCertificate:
    points, normalized = _normalized_table(
        algebra,
        input_arity,
        output_arity,
        table,
    )
    if dag.input_arity != input_arity or dag.output_arity != output_arity:
        raise ValueError("controller DAG arity disagrees with strategy table")
    if not validate_original_signature_dag(algebra, dag):
        raise ValueError("invalid original-signature DAG")
    rows = []
    for point in points:
        expected = normalized[point]
        actual = evaluate_original_signature_dag(algebra, dag, point)
        if actual != expected:
            raise ValueError(
                f"controller DAG mismatch at {point!r}: {actual!r}!={expected!r}"
            )
        rows.append(
            {
                "input": list(point),
                "expected": list(expected),
                "actual": list(actual),
            }
        )
    evaluation_hash = hashlib.sha256(_canonical_bytes(rows)).hexdigest()
    return ControllerDAGCertificate(
        algebra_sha256=algebra_semantic_sha256(algebra),
        strategy_sha256=strategy_semantic_sha256(
            algebra,
            input_arity,
            output_arity,
            normalized,
        ),
        dag_sha256=dag.semantic_sha256,
        rows_checked=len(points),
        output_arity=output_arity,
        node_count=len(dag.nodes),
        depth=dag_depth(dag),
        evaluation_sha256=evaluation_hash,
    )


def verify_controller_dag_certificate(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    dag: OriginalSignatureDAG,
    certificate: ControllerDAGCertificate,
) -> bool:
    try:
        return certificate == certify_controller_dag(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            dag=dag,
        )
    except (KeyError, TypeError, ValueError):
        return False


def compile_controller_artifact(
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow],
    limits: CompilationLimits | None = None,
) -> OriginalSignatureArtifact:
    active_limits = CompilationLimits() if limits is None else limits
    try:
        dag, statistics = compile_original_signature_dag(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            limits=active_limits,
        )
        certificate = certify_controller_dag(
            algebra,
            input_arity=input_arity,
            output_arity=output_arity,
            table=table,
            dag=dag,
        )
    except OriginalSignatureCompilationError as error:
        return OriginalSignatureArtifact(
            status="unsupported",
            compiler=_COMPILER,
            limits=active_limits,
            statistics=error.statistics,
            reason=error.reason,
            dag=None,
            certificate=None,
        )
    return OriginalSignatureArtifact(
        status="compiled",
        compiler=_COMPILER,
        limits=active_limits,
        statistics=statistics,
        reason=None,
        dag=dag,
        certificate=certificate,
    )


def not_applicable_artifact(
    *,
    reason: str = "no_controller_for_infeasible_problem",
    limits: CompilationLimits | None = None,
) -> OriginalSignatureArtifact:
    return OriginalSignatureArtifact(
        status="not_applicable",
        compiler=_COMPILER,
        limits=CompilationLimits() if limits is None else limits,
        statistics=CompilationStatistics(),
        reason=reason,
        dag=None,
        certificate=None,
    )


def verify_controller_artifact(
    artifact: OriginalSignatureArtifact,
    algebra: FiniteAlgebra,
    *,
    input_arity: int,
    output_arity: int,
    table: Mapping[InputRow, OutputRow] | None,
) -> bool:
    if artifact.status == "not_applicable":
        return table is None
    if table is None:
        return False
    if artifact.status == "unsupported":
        return artifact.dag is None and artifact.certificate is None
    if artifact.status != "compiled":
        return False
    if artifact.dag is None or artifact.certificate is None:
        return False
    return verify_controller_dag_certificate(
        algebra,
        input_arity=input_arity,
        output_arity=output_arity,
        table=table,
        dag=artifact.dag,
        certificate=artifact.certificate,
    )

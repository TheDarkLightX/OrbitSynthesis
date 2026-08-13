#!/usr/bin/env python3
"""Fail-closed checker for the Boolean-R9 lift of conservative Q-term DAGs.

The checker freezes an exact depth-three Boolean projection router, represents
each Q value by two Boolean planes, materializes bounded compatible selector
tables in the original {d,u} signature, and checks the size/depth arithmetic.
Its PASS is finite evidence for a manuscript theorem, not a novelty, optimality,
patent, freedom-to-operate, or practical-performance conclusion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from functools import cache
from itertools import product
from pathlib import Path
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.quasiprimal_orbit_term_compiler import (  # noqa: E402
    compatible_tables,
    random_compatible_table,
)
from experiments.quasiprimal_programmable_projection_routing import (  # noqa: E402
    Shape,
    balanced_shape,
    ceil_log,
    compile_relative_binary_control,
    compile_ternary_control,
    materialize_route,
    operation_depth,
    partition_chunks,
    prepare_controls,
    program_terms,
    shape_internal_count,
    shape_leaf_count,
    value_names,
)
from orbitsynthesis.orbit_term_compile import (  # noqa: E402
    Disc,
    Expr,
    Q,
    UnaryU,
    Var,
    complement,
    distinct_node_count,
    evaluate,
    normal_selector,
)
from orbitsynthesis.orbit_term_compile_local import balanced_absorbing_two  # noqa: E402


WITNESS_PATH = (
    ROOT
    / "research/tournaments/2026-08-13-router-frontier/lanes/capacity/boolean_q9_r8_radius1.json"
)
WITNESS_SHA256 = "d3c25e47ce671d8a5d484d6c50cc0b3fccf7f6bb5507097ef8bff6bcbbbe529c"
WITNESS_SEMANTIC_SHA256 = (
    "ae7f2fae8d16e64fc207b997c17424264d03c193d474f1ea6954a89f0c0bdb25"
)
INDEPENDENT_AUDIT_PATH = (
    ROOT / "research/tournaments/2026-08-13-router-frontier/audits/capacity/audit_r9.py"
)
INDEPENDENT_AUDIT_SHA256 = (
    "33a88fd65044cb19b1ae948fb83e8bef8bb2d57ff49cafa65c59005b6e513c62"
)
DEPENDENCY_PATHS = (
    ROOT / "experiments/quasiprimal_orbit_term_compiler.py",
    ROOT / "experiments/quasiprimal_programmable_projection_routing.py",
    ROOT / "src/orbitsynthesis/orbit_term_compile.py",
    ROOT / "src/orbitsynthesis/orbit_term_compile_local.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_witness() -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...], dict[str, object]]:
    require(sha256_path(WITNESS_PATH) == WITNESS_SHA256, "frozen R9 witness drifted")
    payload = json.loads(WITNESS_PATH.read_text())
    require(payload["status"] == "SAT_EXACT" and payload["exact"] is True, "R9 is not exact")
    require(payload["q"] == 9 and payload["depth"] == 3, "R9 arity/depth drift")
    labels = tuple(int(value) for value in payload["labels"])
    programs = tuple(tuple(int(bit) for bit in row) for row in payload["programs"])
    control_positions = tuple(index for index, label in enumerate(labels) if label == 0)
    require(len(labels) == 27 and len(control_positions) == 18, "R9 leaf census drift")
    require(sorted(label for label in labels if label) == list(range(1, 10)), "R9 branch census drift")
    require(len(programs) == 9 and all(len(row) == 18 for row in programs), "R9 program census drift")
    full_rows = payload["full_control_rows"]
    require(
        all(tuple(int(row[position]) for position in control_positions) == programs[target]
            for target, row in enumerate(full_rows)),
        "compact/full R9 programs disagree",
    )
    semantic = {key: payload[key] for key in ("q", "depth", "labels", "programs", "matches_per_target")}
    semantic_sha = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    require(semantic_sha == WITNESS_SEMANTIC_SHA256, "R9 semantic hash drift")
    require(semantic_sha == payload["semantic_sha256"], "stored R9 semantic hash drift")
    return labels, programs, payload


R9_LABELS, R9_PROGRAMS, R9_WITNESS = load_witness()


def r9_router(controls: Sequence[Expr], branches: Sequence[Expr]) -> Expr:
    require(len(controls) == 18, "R9 requires 18 controls")
    require(len(branches) == 9, "R9 requires nine branches")
    control_iter = iter(controls)
    leaves = [next(control_iter) if label == 0 else branches[label - 1] for label in R9_LABELS]
    layer = leaves
    for _ in range(3):
        layer = [Disc(*layer[3 * index : 3 * index + 3]) for index in range(len(layer) // 3)]
    require(len(layer) == 1, "R9 tree did not reduce to one root")
    return layer[0]


def code_names(names: Sequence[Expr]) -> tuple[tuple[Expr, Expr], ...]:
    require(len(names) == 3, "Q coding requires three value names")
    zero, one, _two = names
    return ((zero, zero), (zero, one), (one, zero))


def decode_pair(bits: tuple[Expr, Expr], names: Sequence[Expr]) -> Expr:
    require(len(names) == 3, "Q decoding requires three value names")
    zero, one, two = names
    high, low = bits
    return Disc(Disc(high, one, two), zero, low)


def primitive_checks() -> dict[str, object]:
    require(sha256_path(INDEPENDENT_AUDIT_PATH) == INDEPENDENT_AUDIT_SHA256, "independent audit drifted")
    skeleton_controls = tuple(Var(index) for index in range(18))
    skeleton_branches = tuple(Var(index) for index in range(18, 27))
    skeleton = r9_router(skeleton_controls, skeleton_branches)
    require(operation_depth(skeleton) == 3, "R9 dependency depth drift")
    require(distinct_node_count(skeleton) - 27 == 13, "R9 discriminator census drift")

    anchor = Var(0)
    names = value_names(anchor)
    bit_names = names[:2]
    branches = tuple(Var(index) for index in range(1, 10))
    boolean_checks = 0
    for target, program in enumerate(R9_PROGRAMS):
        term = r9_router(program_terms(program, bit_names), branches)
        for values in product((0, 1), repeat=9):
            require(evaluate(term, (2, *values)) == values[target], f"absolute R9 failed at {target}")
            boolean_checks += 1

    relative_names = (anchor, UnaryU(anchor))
    complement_checks = 0
    for target, program in enumerate(R9_PROGRAMS):
        term = r9_router(program_terms(program, relative_names), branches)
        for orientation in (0, 1):
            for relative_values in product((0, 1), repeat=9):
                values = tuple(value ^ orientation for value in relative_values)
                require(
                    evaluate(term, (orientation, *values)) == values[target],
                    f"complement-relative R9 failed at {target}",
                )
                complement_checks += 1

    codes = code_names(names)
    decoder_checks = 0
    for value, bits in enumerate(codes):
        require(evaluate(decode_pair(bits, names), (2,)) == value, f"decoder failed at {value}")
        decoder_checks += 1

    q_checks = 0
    for target, program in enumerate(R9_PROGRAMS):
        controls = program_terms(program, bit_names)
        high_branches = tuple(Var(1 + 2 * index) for index in range(9))
        low_branches = tuple(Var(2 + 2 * index) for index in range(9))
        decoded = decode_pair(
            (r9_router(controls, high_branches), r9_router(controls, low_branches)),
            names,
        )
        for values in product(Q, repeat=9):
            arguments = [2]
            for value in values:
                arguments.extend((value >> 1, value & 1))
            require(evaluate(decoded, tuple(arguments)) == values[target], f"Q-plane R9 failed at {target}")
            q_checks += 1

    mutation_failures = 0
    effective_mutation_slot = None
    for slot in range(len(R9_PROGRAMS[0])):
        mutated = list(R9_PROGRAMS[0])
        mutated[slot] ^= 1
        mutated_term = r9_router(program_terms(mutated, bit_names), branches)
        failures = sum(
            evaluate(mutated_term, (2, *values)) != values[0]
            for values in product((0, 1), repeat=9)
        )
        if failures > mutation_failures:
            mutation_failures = failures
            effective_mutation_slot = slot
    require(effective_mutation_slot is not None and mutation_failures > 0, "no effective R9 mutation")
    require(all(len(set(code)) < 3 for code in product((0, 1), repeat=3)), "one-plane pigeonhole drift")
    return {
        "r9_discriminator_nodes": 13,
        "r9_dependency_depth": 3,
        "boolean_checks": boolean_checks,
        "complement_relative_checks": complement_checks,
        "q_plane_checks": q_checks,
        "decoder_checks": decoder_checks,
        "effective_mutation_failures": mutation_failures,
        "effective_mutation_slot": effective_mutation_slot,
        "code": [[0, 0], [0, 1], [1, 0]],
        "decoder": "d(d(high,one,two),zero,low)",
    }


def encoded_parameters(arity: int) -> dict[str, object]:
    require(arity >= 2, "encoded parameters start at arity two")
    ratio = 3**arity // arity
    cap = 0
    power = 1
    while power * 3 <= ratio:
        power *= 3
        cap += 1
    cap = max(1, cap)
    block_assignments = 1
    block_positions = 0
    while block_assignments * 3 <= cap:
        block_assignments *= 3
        block_positions += 1
    g3 = max(1, ceil_log(3, arity))
    g2 = max(1, ceil_log(2, arity))
    ternary_chunks = partition_chunks(tuple(range(block_positions, arity)), g3)
    binary_chunks = partition_chunks(tuple(range(1, arity)), g2)
    l9_nonbinary = ceil_log(9, block_assignments) + sum(
        ceil_log(9, 3 ** len(chunk)) for chunk in ternary_chunks
    )
    l9_binary = sum(ceil_log(9, 2 ** len(chunk)) for chunk in binary_chunks)
    return {
        "H": cap,
        "block_positions": block_positions,
        "M": block_assignments,
        "P": 3 ** (arity - block_positions),
        "g3": g3,
        "g2": g2,
        "ternary_chunks": ternary_chunks,
        "binary_chunks": binary_chunks,
        "L9_nonbinary": l9_nonbinary,
        "L9_binary": l9_binary,
    }


def certified_size_bound(
    arity: int,
    *,
    parallel_planes: bool = True,
    per_level_sharing: bool = True,
    decode_once: bool = True,
) -> int:
    require(parallel_planes, "serial planes do not certify the depth bound")
    require(per_level_sharing, "per-node controls do not certify the size bound")
    require(decode_once, "repeated decoding does not certify the depth bound")
    parameters = encoded_parameters(arity)
    m = int(parameters["M"])
    p = int(parameters["P"])
    g3 = int(parameters["g3"])
    g2 = int(parameters["g2"])
    l9_nonbinary = int(parameters["L9_nonbinary"])
    l9_binary = int(parameters["L9_binary"])
    return (
        78 * 3**m
        + 26 * (p - 1)
        + 63 * l9_nonbinary * (3**g3 - 1)
        + 13 * (2 ** (arity - 1) - 1)
        + 54 * l9_binary * (2**g2 - 1)
        + 4 * arity
        + 64
    )


def certified_depth_bound(arity: int, *, include_decode: bool = True) -> int:
    require(include_decode, "Q decoder omitted from depth accounting")
    parameters = encoded_parameters(arity)
    anchor_depth = 3 * ceil_log(2, arity)
    nonbinary = (
        anchor_depth
        + 2
        + 3 * int(parameters["g3"])
        + 3 * int(parameters["L9_nonbinary"])
        + 2
    )
    binary = 1 + 2 * int(parameters["g2"]) + 3 * int(parameters["L9_binary"])
    return max(nonbinary, binary, anchor_depth + 2) + 2


def route_pair(
    shape: Shape,
    leaves: Sequence[tuple[Expr, Expr]],
    controls: tuple[tuple[Expr, ...], ...],
) -> tuple[Expr, Expr]:
    require(bool(leaves), "pair router requires leaves")
    return tuple(
        materialize_route(shape, tuple(pair[plane] for pair in leaves), controls, 9, r9_router)
        for plane in range(2)
    )  # type: ignore[return-value]


def compile_encoded_selector(
    arity: int, selector_indices: Mapping[tuple[int, ...], int]
) -> Expr:
    require(arity >= 1, "arity must be positive")
    points = tuple(product(Q, repeat=arity))
    require(set(selector_indices) == set(points), "selector table is not total")
    require(all(0 <= index < arity for index in selector_indices.values()), "selector index outside arity")
    for point in product((0, 1), repeat=arity):
        require(
            selector_indices[point] == selector_indices[complement(point)],
            "binary selector table is not complement-invariant",
        )
    variables = tuple(Var(index) for index in range(arity))
    if arity == 1:
        return variables[0]

    anchor = balanced_absorbing_two(variables)
    names = value_names(anchor)
    codes = code_names(names)
    parameters = encoded_parameters(arity)
    block_count = int(parameters["block_positions"])
    block_positions = tuple(range(block_count))
    prefix_chunks = tuple(parameters["ternary_chunks"])
    binary_chunks = tuple(parameters["binary_chunks"])

    def ternary_control_compiler(
        positions: tuple[int, ...], table: Mapping[tuple[int, ...], int]
    ) -> Expr:
        return compile_ternary_control(positions, table, variables, names)

    block_assignments = tuple(product(Q, repeat=block_count))
    if block_count == 0:
        library: dict[tuple[int, ...], tuple[Expr, Expr]] = {
            (value,): codes[value] for value in Q
        }
    else:
        block_shape, block_controls = prepare_controls(
            block_assignments, block_positions, 9, R9_PROGRAMS, ternary_control_compiler
        )

        def build_library(node: Shape, depth: int = 0) -> dict[tuple[int, ...], tuple[Expr, Expr]]:
            if isinstance(node, int):
                return {(value,): codes[value] for value in Q}
            child_libraries = tuple(build_library(child, depth + 1) for child in node)
            result: dict[tuple[int, ...], tuple[Expr, Expr]] = {}
            for choices in product(*(tuple(child.items()) for child in child_libraries)):
                word = tuple(value for child_word, _pair in choices for value in child_word)
                pair_leaves = [pair for _child_word, pair in choices]
                while len(pair_leaves) < 9:
                    pair_leaves.append(pair_leaves[-1])
                result[word] = tuple(
                    r9_router(block_controls[depth], tuple(pair[plane] for pair in pair_leaves))
                    for plane in range(2)
                )  # type: ignore[assignment]
            require(len(result) == 3 ** shape_leaf_count(node), "encoded library census drift")
            return result

        library = build_library(block_shape)

    prefix_packets = []
    for chunk in prefix_chunks:
        assignments = tuple(product(Q, repeat=len(chunk)))
        prefix_packets.append(
            prepare_controls(assignments, chunk, 9, R9_PROGRAMS, ternary_control_compiler)
        )

    values: list[int | None] = [None] * arity

    def select_prefix(chunk_index: int) -> tuple[Expr, Expr]:
        if chunk_index == len(prefix_chunks):
            output_vector = []
            for block_point in block_assignments:
                for position, value in zip(block_positions, block_point, strict=True):
                    values[position] = value
                point = tuple(int(value) for value in values)
                output_vector.append(point[selector_indices[point]])
            return library[tuple(output_vector)]
        chunk = prefix_chunks[chunk_index]
        assignments = tuple(product(Q, repeat=len(chunk)))
        leaves = []
        for assignment in assignments:
            for position, value in zip(chunk, assignment, strict=True):
                values[position] = value
            leaves.append(select_prefix(chunk_index + 1))
        for position in chunk:
            values[position] = None
        shape, controls = prefix_packets[chunk_index]
        return route_pair(shape, leaves, controls)

    nonbinary = decode_pair(select_prefix(0), names)
    bit_names = (variables[0], UnaryU(variables[0]))

    def binary_control_compiler(
        positions: tuple[int, ...], table: Mapping[tuple[int, ...], int]
    ) -> Expr:
        return compile_relative_binary_control(positions, table, variables, bit_names)

    binary_packets = []
    for chunk in binary_chunks:
        assignments = tuple(product((0, 1), repeat=len(chunk)))
        binary_packets.append(
            prepare_controls(assignments, chunk, 9, R9_PROGRAMS, binary_control_compiler)
        )

    representative = [0] * arity

    def select_binary(chunk_index: int) -> Expr:
        if chunk_index == len(binary_chunks):
            point = tuple(representative)
            return variables[selector_indices[point]]
        chunk = binary_chunks[chunk_index]
        assignments = tuple(product((0, 1), repeat=len(chunk)))
        leaves = []
        for assignment in assignments:
            for position, value in zip(chunk, assignment, strict=True):
                representative[position] = value
            leaves.append(select_binary(chunk_index + 1))
        shape, controls = binary_packets[chunk_index]
        return materialize_route(shape, leaves, controls, 9, r9_router)

    return normal_selector(names[0], anchor, select_binary(0), nonbinary)


def verify_compiler(arity: int, table: Mapping[tuple[int, ...], int]) -> dict[str, int]:
    term = compile_encoded_selector(arity, table)
    checked = 0
    for point in product(Q, repeat=arity):
        require(evaluate(term, point) == point[table[point]], f"compiler mismatch at {arity}:{point}")
        checked += 1
    operation_nodes = distinct_node_count(term) - arity
    depth = operation_depth(term)
    if arity >= 2:
        require(operation_nodes <= certified_size_bound(arity), "finite size bound failed")
        require(depth <= certified_depth_bound(arity), "finite depth bound failed")
    return {"tuples_checked": checked, "operation_nodes": operation_nodes, "operation_depth": depth}


@cache
def encoded_library_nodes(points: int) -> int:
    require(points >= 1, "library point count must be positive")
    if points == 1:
        return 0
    shape = balanced_shape(points, 9)
    return 26 * 3**points + sum(encoded_library_nodes(shape_leaf_count(child)) for child in shape)


def recurrence_checks() -> dict[str, object]:
    for points in range(1, 257):
        require(encoded_library_nodes(points) <= 78 * 3**points, f"library recurrence failed at {points}")
    coefficient = 3 * math.log(3, 9)
    require(abs(coefficient - 1.5) < 1e-15, "R9 coefficient identity drift")
    require(coefficient < 3 * math.log(3, 8) < 3 * math.log(3, 6), "coefficient ordering drift")
    rows = []
    for arity in (16, 32, 64, 128, 256, 512, 1024, 4096):
        parameters = encoded_parameters(arity)
        depth = certified_depth_bound(arity)
        rows.append({
            "arity": arity,
            "M": parameters["M"],
            "L9_nonbinary": parameters["L9_nonbinary"],
            "L9_binary": parameters["L9_binary"],
            "depth_bound": depth,
            "depth_per_arity": depth / arity,
        })
    mutations = {}
    for name, kwargs in (
        ("serial_planes", {"parallel_planes": False}),
        ("per_node_controls", {"per_level_sharing": False}),
        ("redecode_each_level", {"decode_once": False}),
    ):
        rejected = False
        try:
            certified_size_bound(16, **kwargs)
        except RuntimeError:
            rejected = True
        require(rejected, f"{name} accounting mutation survived")
        mutations[f"{name}_rejected"] = rejected
    decoder_rejected = False
    try:
        certified_depth_bound(16, include_decode=False)
    except RuntimeError:
        decoder_rejected = True
    require(decoder_rejected, "decoder omission mutation survived")
    mutations["decoder_omission_rejected"] = decoder_rejected
    serial_rates = tuple((q, h, math.log(q) / h) for q, h in ((6, 3), (7, 3), (8, 3), (9, 3)))
    require(max(serial_rates, key=lambda row: row[2])[:2] == (9, 3), "serial-rate maximum drift")
    return {
        "library_points_checked": 256,
        "candidate_coefficient": coefficient,
        "candidate_coefficient_exact": "3*log_9(3)=3/2",
        "structural_rows": rows,
        "mutation_checks": mutations,
        "serial_router_rates": [{"q": q, "depth": h, "log_capacity_per_depth": rate} for q, h, rate in serial_rates],
    }


def compiler_checks() -> dict[str, object]:
    rows = []
    total_tables = 0
    total_tuples = 0
    arity_one = {point: 0 for point in product(Q, repeat=1)}
    result = verify_compiler(1, arity_one)
    rows.append({"arity": 1, "tables": 1, **result})
    total_tables += 1
    total_tuples += result["tuples_checked"]
    arity_two = [verify_compiler(2, table) for table in compatible_tables(2)]
    require(len(arity_two) == 128, "arity-two table census drift")
    rows.append({
        "arity": 2,
        "tables": 128,
        "tuples_checked": sum(row["tuples_checked"] for row in arity_two),
        "max_operation_nodes": max(row["operation_nodes"] for row in arity_two),
        "max_operation_depth": max(row["operation_depth"] for row in arity_two),
    })
    total_tables += 128
    total_tuples += rows[-1]["tuples_checked"]
    for arity, seeds in ((3, (93101, 93102, 93103)), (4, (94101, 94102)), (5, (95101,))):
        checks = [verify_compiler(arity, random_compatible_table(arity, seed)) for seed in seeds]
        rows.append({
            "arity": arity,
            "tables": len(checks),
            "tuples_checked": sum(row["tuples_checked"] for row in checks),
            "max_operation_nodes": max(row["operation_nodes"] for row in checks),
            "max_operation_depth": max(row["operation_depth"] for row in checks),
        })
        total_tables += len(checks)
        total_tuples += rows[-1]["tuples_checked"]
    invalid = random_compatible_table(3, 99917)
    point = next(iter(product((0, 1), repeat=3)))
    invalid[point] = 0
    invalid[complement(point)] = 1
    rejected = False
    try:
        compile_encoded_selector(3, invalid)
    except RuntimeError:
        rejected = True
    require(rejected, "non-complement-invariant table mutation survived")
    return {
        "rows": rows,
        "total_tables_checked": total_tables,
        "total_tuple_evaluations": total_tuples,
        "noncomplement_table_mutation_rejected": rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args()
    summary = {
        "schema": "orbit-synthesis/q-via-boolean-r9-routing/v2",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "model": "parameter-free original-signature shared DAG; operation nodes; variables depth zero",
        "replay": {
            "normal": "python3 experiments/quasiprimal_boolean_r9_routing.py --out runs/quasiprimal_boolean_r9_routing/summary.json",
            "optimized": "python3 -O experiments/quasiprimal_boolean_r9_routing.py",
            "required_relation": "normal and optimized stdout byte-identical; --out regenerates the committed JSON receipt exactly",
        },
        "source_sha256": sha256_path(Path(__file__).resolve()),
        "dependency_sha256": {
            str(path.relative_to(ROOT)): sha256_path(path) for path in DEPENDENCY_PATHS
        },
        "witness_sha256": sha256_path(WITNESS_PATH),
        "witness_semantic_sha256": WITNESS_SEMANTIC_SHA256,
        "independent_audit_sha256": sha256_path(INDEPENDENT_AUDIT_PATH),
        "primitive_checks": primitive_checks(),
        "compiler_checks": compiler_checks(),
        "recurrence_checks": recurrence_checks(),
        "claim_boundary": (
            "Finite semantics, bounded composed compilers, recurrence arithmetic, and mutations only. "
            "The all-arity O(3^r/r) size and (3/2)r+O(r/log r) depth result remains a "
            "manuscript proof pending formal verification and complete prior-art review. No novelty, "
            "optimality, practical-performance, patent, FTO, license, or Tau-capability claim is made."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    output = "PASS Q-via-Boolean-R9 programmable routing\n" + json.dumps(summary, indent=2, sort_keys=True) + "\n"
    print(output, end="")
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

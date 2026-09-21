#!/usr/bin/env python3
"""Independent audit of the recursive signed discriminator-router family.

This checker does not import the author implementation.  It reconstructs the
canonical family from ternary path digits, exhausts the small members, checks
the frozen R27 with a direct ternary ROBDD apply, extracts mutation witnesses,
and fails closed on byte or schema drift.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Literal


Bit = Literal[0, 1]
Kind = Literal["P", "N"]
CONTROL = 0
TOURNAMENT = Path(__file__).resolve().parents[2]
STATE = TOURNAMENT / "STATE.md"
AUTHOR = TOURNAMENT / "lanes/fused/check_strong_router_family.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def majority(x: int, y: int, z: int) -> int:
    return int(x + y + z >= 2)


def unary_u(value: int) -> int:
    require(value in (0, 1, 2), "u input left Q")
    return (1, 0, 1)[value]


def base3_digits(value: int, width: int) -> tuple[int, ...]:
    require(0 <= value < 3**width, "base-three value out of range")
    digits = [0] * width
    for index in reversed(range(width)):
        value, digits[index] = divmod(value, 3)
    require(value == 0, "base-three conversion did not terminate")
    return tuple(digits)


def branch_positions(kind: Kind, depth: int) -> tuple[int, ...]:
    """Derive positions directly from prefix digits, not author recursion."""

    require(depth >= 1, "depth must be positive")
    root_sign = int(kind == "N")
    positions = []
    for prefix_index in range(3 ** (depth - 1)):
        prefix = base3_digits(prefix_index, depth - 1)
        current_sign = root_sign ^ (sum(digit == 1 for digit in prefix) & 1)
        positions.append(3 * prefix_index + current_sign)
    return tuple(positions)


def expected_labels(kind: Kind, depth: int) -> tuple[int, ...]:
    labels = [CONTROL] * (3**depth)
    for branch, position in enumerate(branch_positions(kind, depth), start=1):
        labels[position] = branch
    return tuple(labels)


def path_middle_parity(position: int, depth: int) -> int:
    return sum(digit == 1 for digit in base3_digits(position, depth)) & 1


def base_leaves(kind: Kind, mode: str, value: int) -> tuple[int | None, ...]:
    """One-level leaf values; None denotes the unique payload leaf."""

    if kind == "P":
        table = {
            ("projection", 0): (None, 0, 0),
            ("constant", 0): (None, 1, 0),
            ("constant", 1): (None, 0, 1),
        }
    else:
        table = {
            ("projection", 0): (0, None, 1),
            ("constant", 0): (0, None, 0),
            ("constant", 1): (1, None, 1),
        }
    require((mode, value) in table, "invalid base mode")
    return table[(mode, value)]


def full_program(
    kind: Kind,
    depth: int,
    mode: Literal["constant", "projection"],
    value: int,
) -> tuple[int | None, ...]:
    """Reconstruct a program by propagating semantic modes down the tree."""

    capacity = 3 ** (depth - 1)
    require(depth >= 1, "program depth must be positive")
    require(
        (mode == "constant" and value in (0, 1))
        or (mode == "projection" and 0 <= value < capacity),
        "invalid recursive mode",
    )
    if depth == 1:
        return base_leaves(kind, mode, value)

    child_kinds: tuple[Kind, Kind, Kind] = (
        ("P", "N", "P") if kind == "P" else ("N", "P", "N")
    )
    if mode == "constant":
        modes = (("constant", value),) * 3
    else:
        group, local_target = divmod(value, 3 ** (depth - 2))
        by_group = (
            (("projection", local_target), ("constant", 0), ("constant", 0)),
            (("constant", 0), ("projection", local_target), ("constant", 1)),
            (("constant", 0), ("constant", 0), ("projection", local_target)),
        )
        modes = by_group[group]
    leaves: list[int | None] = []
    for child_kind, (child_mode, child_value) in zip(child_kinds, modes, strict=True):
        leaves.extend(full_program(child_kind, depth - 1, child_mode, child_value))
    return tuple(leaves)


def expected_compact_program(
    kind: Kind,
    depth: int,
    mode: Literal["constant", "projection"],
    value: int,
) -> tuple[int, ...]:
    labels = expected_labels(kind, depth)
    leaves = full_program(kind, depth, mode, value)
    require(len(labels) == len(leaves), "program/label length mismatch")
    require(
        all((leaf is None) == (label != CONTROL) for leaf, label in zip(leaves, labels, strict=True)),
        "payload/control shape mismatch",
    )
    return tuple(int(leaf) for leaf, label in zip(leaves, labels, strict=True) if label == CONTROL)


def concrete_evaluate(
    labels: tuple[int, ...], program: tuple[int, ...], values: tuple[int, ...]
) -> int:
    require(len(labels) > 0 and len(labels) == 3 ** round_log3(len(labels)), "labels are not a full tree")
    require(len(program) == labels.count(CONTROL), "program width mismatch")
    control_index = 0
    layer: list[int] = []
    for label in labels:
        if label == CONTROL:
            layer.append(program[control_index])
            control_index += 1
        else:
            require(1 <= label <= len(values), "branch label out of range")
            layer.append(values[label - 1])
    while len(layer) > 1:
        require(len(layer) % 3 == 0, "malformed ternary layer")
        layer = [
            discriminator(layer[index], layer[index + 1], layer[index + 2])
            for index in range(0, len(layer), 3)
        ]
    return layer[0]


def round_log3(value: int) -> int:
    require(value >= 1, "log input must be positive")
    depth = 0
    power = 1
    while power < value:
        power *= 3
        depth += 1
    require(power == value, "value is not a power of three")
    return depth


class DirectTernaryROBDD:
    """Canonical ROBDD with a direct three-argument discriminator apply."""

    def __init__(self) -> None:
        self.nodes: list[tuple[int, int, int] | None] = [None, None]
        self.unique: dict[tuple[int, int, int], int] = {}
        self.d_cache: dict[tuple[int, int, int], int] = {}

    def make(self, variable: int, low: int, high: int) -> int:
        if low == high:
            return low
        key = (variable, low, high)
        result = self.unique.get(key)
        if result is None:
            result = len(self.nodes)
            self.nodes.append(key)
            self.unique[key] = result
        return result

    def variable(self, index: int) -> int:
        return self.make(index, 0, 1)

    def top(self, node: int) -> int:
        record = self.nodes[node]
        return record[0] if record is not None else 10**9

    def cofactor(self, node: int, variable: int, bit: int) -> int:
        record = self.nodes[node]
        if record is None or record[0] != variable:
            return node
        return record[1 + bit]

    def apply_discriminator(self, x: int, y: int, z: int) -> int:
        key = (x, y, z)
        cached = self.d_cache.get(key)
        if cached is not None:
            return cached
        if x < 2 and y < 2 and z < 2:
            result = discriminator(x, y, z)
        else:
            variable = min(self.top(x), self.top(y), self.top(z))
            low = self.apply_discriminator(
                self.cofactor(x, variable, 0),
                self.cofactor(y, variable, 0),
                self.cofactor(z, variable, 0),
            )
            high = self.apply_discriminator(
                self.cofactor(x, variable, 1),
                self.cofactor(y, variable, 1),
                self.cofactor(z, variable, 1),
            )
            result = self.make(variable, low, high)
        self.d_cache[key] = result
        return result

    def evaluate_tree(
        self, labels: tuple[int, ...], program: tuple[int, ...], variables: tuple[int, ...]
    ) -> int:
        require(len(program) == labels.count(CONTROL), "ROBDD program width mismatch")
        iterator = iter(program)
        layer = [next(iterator) if label == CONTROL else variables[label - 1] for label in labels]
        while len(layer) > 1:
            layer = [
                self.apply_discriminator(layer[index], layer[index + 1], layer[index + 2])
                for index in range(0, len(layer), 3)
            ]
        return layer[0]

    def distinguish(self, left: int, right: int, width: int) -> tuple[int, ...] | None:
        """Return a concrete valuation on which two ROBDDs differ."""

        memo: dict[tuple[int, int], dict[int, int] | None] = {}

        def visit(a: int, b: int) -> dict[int, int] | None:
            if a == b:
                return None
            if a < 2 and b < 2:
                return {} if a != b else None
            key = (a, b)
            if key in memo:
                return memo[key]
            variable = min(self.top(a), self.top(b))
            for bit in (0, 1):
                suffix = visit(
                    self.cofactor(a, variable, bit), self.cofactor(b, variable, bit)
                )
                if suffix is not None:
                    result = dict(suffix)
                    result[variable] = bit
                    memo[key] = result
                    return result
            memo[key] = None
            return None

        partial = visit(left, right)
        if partial is None:
            return None
        return tuple(partial.get(index, 0) for index in range(width))


def semantic_sha(payload: dict[str, object]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "semantic_sha256"}
    return hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_witness(payload: dict[str, object]) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    require(payload.get("schema") == "orbit-synthesis/strong-discriminator-r27/v1", "schema drift")
    require(payload.get("depth") == 4, "R27 depth drift")
    require(payload.get("capacity") == 27, "R27 capacity drift")
    require(payload.get("discriminator_nodes") == 40, "R27 node count drift")
    require(payload.get("semantic_sha256") == semantic_sha(payload), "R27 semantic hash mismatch")

    raw_labels = payload.get("labels")
    raw_programs = payload.get("programs")
    require(isinstance(raw_labels, list), "labels missing")
    require(isinstance(raw_programs, list), "programs missing")
    require(all(type(value) is int for value in raw_labels), "labels are not integers")
    labels = tuple(raw_labels)
    require(labels == expected_labels("P", 4), "R27 labels differ from recurrence")
    require(len(labels) == 81 and labels.count(CONTROL) == 54, "R27 leaf census drift")
    require(sorted(label for label in labels if label) == list(range(1, 28)), "R27 branch census drift")

    controls = tuple(index for index, label in enumerate(labels) if label == CONTROL)
    branches = tuple(index for index, label in enumerate(labels) if label != CONTROL)
    require(payload.get("control_positions") == list(controls), "control position list drift")
    require(payload.get("branch_positions") == list(branches), "branch position list drift")
    require(len(raw_programs) == 27, "R27 program count drift")
    programs = []
    for target, raw_row in enumerate(raw_programs):
        require(isinstance(raw_row, list), f"program {target} is not a list")
        require(len(raw_row) == 54, f"program {target} width drift")
        require(all(type(bit) is int and bit in (0, 1) for bit in raw_row), f"program {target} has a non-bit")
        row = tuple(raw_row)
        require(
            row == expected_compact_program("P", 4, "projection", target),
            f"program {target} differs from recurrence",
        )
        programs.append(row)
    return labels, tuple(programs)


def expect_rejected(payload: dict[str, object]) -> None:
    rejected = False
    try:
        validate_witness(payload)
    except (RuntimeError, TypeError, ValueError):
        rejected = True
    require(rejected, "malformed witness mutation survived")


def truth_and_induction_checks() -> dict[str, int]:
    truth_rows = 0
    complement_rows = 0
    for x, y, z in product((0, 1), repeat=3):
        value = discriminator(x, y, z)
        require(value == majority(x, 1 - y, z), "twisted-majority identity failed")
        require(
            discriminator(1 - x, 1 - y, 1 - z) == 1 - value,
            "simultaneous-complement identity failed",
        )
        truth_rows += 1
        complement_rows += 1

    induction_rows = 0
    for kind in ("P", "N"):
        for constant in (0, 1):
            require(discriminator(constant, constant, constant) == constant, "constant induction failed")
            induction_rows += 1
        for group in range(3):
            for x in (0, 1):
                signed = x if kind == "P" else 1 - x
                child_outputs = (
                    (signed, 0, 0),
                    (0, 1 - signed, 1),
                    (0, 0, signed),
                )[group]
                require(
                    discriminator(*child_outputs) == signed,
                    f"projection induction failed at {kind}:{group}:{x}",
                )
                induction_rows += 1
    return {
        "twisted_majority_rows": truth_rows,
        "complement_equivariance_rows": complement_rows,
        "induction_transition_rows": induction_rows,
    }


def structural_checks(max_depth: int = 6) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for depth in range(1, max_depth + 1):
        capacity = 3 ** (depth - 1)
        for kind in ("P", "N"):
            labels = expected_labels(kind, depth)
            expected_sign = int(kind == "N")
            require(len(labels) == 3**depth, "structural leaf count drift")
            require(labels.count(CONTROL) == 2 * capacity, "structural control count drift")
            require(sorted(label for label in labels if label) == list(range(1, capacity + 1)), "structural branch census drift")
            require(
                all(
                    path_middle_parity(position, depth) == expected_sign
                    for position, label in enumerate(labels)
                    if label != CONTROL
                ),
                "structural path polarity drift",
            )
            for constant in (0, 1):
                require(
                    len(expected_compact_program(kind, depth, "constant", constant))
                    == 2 * capacity,
                    "constant program width drift",
                )
            rows.append(
                {
                    "kind": kind,
                    "depth": depth,
                    "capacity": capacity,
                    "branch_leaves": capacity,
                    "control_leaves": 2 * capacity,
                    "discriminator_nodes": (3**depth - 1) // 2,
                    "branch_path_polarity": expected_sign,
                }
            )
    return rows


def exhaustive_small_checks(max_depth: int = 3) -> int:
    checks = 0
    for depth in range(1, max_depth + 1):
        capacity = 3 ** (depth - 1)
        for kind in ("P", "N"):
            labels = expected_labels(kind, depth)
            for values in product((0, 1), repeat=capacity):
                for constant in (0, 1):
                    program = expected_compact_program(kind, depth, "constant", constant)
                    require(concrete_evaluate(labels, program, values) == constant, "small constant replay failed")
                    checks += 1
                for target in range(capacity):
                    program = expected_compact_program(kind, depth, "projection", target)
                    expected = values[target] if kind == "P" else 1 - values[target]
                    require(concrete_evaluate(labels, program, values) == expected, "small projection replay failed")
                    checks += 1
    return checks


def bounded_family_robdd_checks(depth: int = 4) -> tuple[int, int]:
    """Check P and N independently of the serialized P-only witness."""

    capacity = 3 ** (depth - 1)
    bdd = DirectTernaryROBDD()
    variables = tuple(bdd.variable(index) for index in range(capacity))
    checks = 0
    for kind in ("P", "N"):
        labels = expected_labels(kind, depth)
        for constant in (0, 1):
            root = bdd.evaluate_tree(
                labels,
                expected_compact_program(kind, depth, "constant", constant),
                variables,
            )
            require(root == constant, f"bounded ROBDD constant failed at {kind}:{constant}")
            checks += 1
        for target in range(capacity):
            root = bdd.evaluate_tree(
                labels,
                expected_compact_program(kind, depth, "projection", target),
                variables,
            )
            expected = (
                variables[target]
                if kind == "P"
                else bdd.make(target, 1, 0)
            )
            require(root == expected, f"bounded ROBDD projection failed at {kind}:{target}")
            checks += 1
    return checks, len(bdd.nodes)


def representation_bridge_checks() -> dict[str, int]:
    """Finite checks of the local bridge identities, not compiler integration."""

    anchor = 2
    one = unary_u(anchor)
    zero = unary_u(one)
    require((zero, one, anchor) == (0, 1, 2), "nonbinary anchor names failed")

    codes = ((0, 0), (0, 1), (1, 0))
    decoder_checks = 0
    for value, (high, low) in enumerate(codes):
        decoded = discriminator(discriminator(high, one, anchor), zero, low)
        require(decoded == value, "two-plane decoder identity failed")
        decoder_checks += 1

    # On the binary branch a logical program bit p is represented physically
    # by orientation for p=0 and u(orientation) for p=1.  Exhaust the R9 member
    # to ensure this relative representation returns the physical target.
    depth = 3
    capacity = 9
    labels = expected_labels("P", depth)
    relative_checks = 0
    for target in range(capacity):
        logical_program = expected_compact_program("P", depth, "projection", target)
        for logical_values in product((0, 1), repeat=capacity):
            for orientation in (0, 1):
                physical_values = tuple(bit ^ orientation for bit in logical_values)
                physical_program = tuple(
                    orientation if bit == 0 else unary_u(orientation)
                    for bit in logical_program
                )
                require(
                    concrete_evaluate(labels, physical_program, physical_values)
                    == physical_values[target],
                    "complement-relative R9 bridge failed",
                )
                relative_checks += 1
    return {
        "nonbinary_anchor_name_checks": 3,
        "shared_anchor_u_nodes_required": 2,
        "two_plane_decoder_checks": decoder_checks,
        "two_plane_decoder_d_nodes_required": 2,
        "binary_relative_r9_checks": relative_checks,
        "shared_binary_u_nodes_required": 1,
    }


def r27_bdd_and_mutations(
    labels: tuple[int, ...], programs: tuple[tuple[int, ...], ...]
) -> tuple[list[dict[str, object]], int]:
    bdd = DirectTernaryROBDD()
    variables = tuple(bdd.variable(index) for index in range(27))
    mutations: list[dict[str, object]] = []
    for target, program in enumerate(programs):
        root = bdd.evaluate_tree(labels, program, variables)
        require(root == variables[target], f"R27 ROBDD projection failed at target {target}")
        effective = None
        for slot in range(len(program)):
            mutated = program[:slot] + (1 - program[slot],) + program[slot + 1 :]
            mutated_root = bdd.evaluate_tree(labels, mutated, variables)
            valuation = bdd.distinguish(mutated_root, variables[target], 27)
            if valuation is None:
                continue
            require(
                concrete_evaluate(labels, mutated, valuation) != valuation[target],
                "ROBDD mutation witness failed concrete replay",
            )
            effective = {
                "target": target,
                "control_slot": slot,
                "counterexample": list(valuation),
            }
            break
        require(effective is not None, f"no effective R27 mutation at target {target}")
        mutations.append(effective)
    return mutations, len(bdd.nodes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness", required=True)
    parser.add_argument("--expected-witness-sha", required=True)
    parser.add_argument("--expected-author-sha", required=True)
    parser.add_argument("--expected-state-sha", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    witness_path = Path(args.witness).resolve()
    require(file_sha256(STATE) == args.expected_state_sha, "STATE bytes drifted")
    require(file_sha256(AUTHOR) == args.expected_author_sha, "author source bytes drifted")
    require(file_sha256(witness_path) == args.expected_witness_sha, "R27 witness bytes drifted")
    payload = json.loads(witness_path.read_text())
    require(isinstance(payload, dict), "R27 payload is not an object")
    require(
        payload.get("generator_source_sha256") == args.expected_author_sha,
        "R27 embedded generator hash mismatch",
    )
    require(
        payload.get("frozen_state_sha256") == args.expected_state_sha,
        "R27 embedded STATE hash mismatch",
    )
    labels, programs = validate_witness(payload)

    malformed = []
    for name, mutate in (
        ("branch_label", lambda value: value["labels"].__setitem__(branch_positions("P", 4)[0], 2)),
        ("program_nonbit", lambda value: value["programs"][0].__setitem__(0, 2)),
        ("program_truncated", lambda value: value["programs"][0].pop()),
        ("position_list", lambda value: value["branch_positions"].pop()),
        ("node_count", lambda value: value.__setitem__("discriminator_nodes", 39)),
        ("semantic_hash", lambda value: value.__setitem__("semantic_sha256", "0" * 64)),
    ):
        changed = copy.deepcopy(payload)
        mutate(changed)
        if name != "semantic_hash":
            changed["semantic_sha256"] = semantic_sha(changed)
        expect_rejected(changed)
        malformed.append(name)

    algebra = truth_and_induction_checks()
    structures = structural_checks()
    small_checks = exhaustive_small_checks()
    bounded_bdd_checks, bounded_bdd_nodes = bounded_family_robdd_checks()
    bridges = representation_bridge_checks()
    mutations, bdd_nodes = r27_bdd_and_mutations(labels, programs)
    summary: dict[str, object] = {
        "schema": "orbit-synthesis/strong-family-independent-audit/v1",
        "verdict": "PASS_EXACT_RECURSIVE_BOOLEAN_FAMILY",
        "subject": {
            "state_sha256": args.expected_state_sha,
            "author_source_sha256": args.expected_author_sha,
            "r27_witness_sha256": args.expected_witness_sha,
            "r27_semantic_sha256": payload["semantic_sha256"],
        },
        "algebra_checks": algebra,
        "structural_rows": structures,
        "exhaustive_small_boolean_checks": small_checks,
        "bounded_p4_n4_robdd_checks": bounded_bdd_checks,
        "bounded_p4_n4_robdd_nodes": bounded_bdd_nodes,
        "representation_bridge_checks": bridges,
        "r27_robdd_projection_checks": 27,
        "r27_robdd_nodes_after_checks": bdd_nodes,
        "r27_effective_mutations": mutations,
        "malformed_mutations_rejected": malformed,
        "exact_family_statement": (
            "For every h>=1, the explicit full d-only skeleton P_h has 3^(h-1) "
            "branch leaves, 2*3^(h-1) programmable Boolean control leaves, "
            "(3^h-1)/2 discriminator nodes, dependency depth h, and one fixed "
            "Boolean program for every requested target; N_h has the same counts "
            "and returns the complement of each requested branch. In a compiler, "
            "the logical program is address-only; its physical binary names are "
            "complement-relative to x0."
        ),
        "legality_boundary": (
            "No NOT node or constant node occurs inside the recursive skeleton. "
            "N_h obtains negative polarity from middle-child discriminator paths. "
            "The 0/1 controls are parameters of the Boolean gadget, not nullary "
            "operations of Q. Turning them into parameter-free original-signature "
            "terms requires the separately audited nonbinary-anchor or "
            "complement-relative binary bridge and its full cost accounting."
        ),
        "claim_boundary": (
            "This audit proves the explicit recursive Boolean family and checks the "
            "frozen R27. It does not by itself prove the all-arity compiler size/depth "
            "bridge, novelty, optimality, practical value, patent/FTO status, license "
            "rights, or any Tau claim."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("PASS independent strong-family audit")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

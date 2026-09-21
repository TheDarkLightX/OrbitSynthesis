#!/usr/bin/env python3
"""Exact packed-semantic search around the frozen direct-Q R6 router.

Every Q^q truth table is stored as three Python integer bitsets, one bitset
per output value.  Subtree dynamic programming computes the exact set of
semantics obtainable by independently programming control leaves with
0, 1, or 2.  No valuation-by-valuation SMT instance is built.

PASS establishes only the explicitly enumerated neighborhoods below.  It is
not a global depth-three direct-Q capacity bound.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations, product
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[5]
BASELINE_SOURCE = ROOT / "experiments/quasiprimal_programmable_projection_routing.py"
FROZEN_BASELINE_SHA256 = (
    "c38e9c006f0109397827345c42acb24debae55a373ee6861b8eafc35e1b65265"
)

CONTROL = -1
CONST0 = -2
CONST1 = -3
CONST2 = -4
CONSTANT_LABELS = (CONST0, CONST1, CONST2)

# Full depth-three leaf order of the frozen R6 skeleton.  The program slots
# occur in the same order as R6_PROGRAMS in the frozen baseline source.
R6_LABELS = (
    CONTROL, CONTROL, 1,
    CONTROL, 4, CONTROL,
    CONTROL, CONTROL, 3,
    CONTROL, 4, CONTROL,
    CONTROL, 4, CONTROL,
    CONTROL, 0, CONTROL,
    CONTROL, CONTROL, 5,
    CONTROL, 0, CONTROL,
    CONTROL, CONTROL, 2,
)

R6_PROGRAMS = (
    (1, 2, 1, 1, 2, 1, 1, 2, 1, 2, 2, 1, 1, 2, 1, 2, 0, 1),
    (0, 0, 1, 1, 1, 2, 1, 1, 2, 2, 0, 2, 1, 0, 1, 2, 1, 2),
    (1, 2, 1, 1, 0, 2, 0, 0, 2, 2, 2, 2, 2, 1, 2, 2, 0, 0),
    (2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 1, 2, 0, 2, 2, 0, 0, 1),
    (2, 0, 0, 2, 0, 2, 2, 1, 0, 1, 1, 0, 2, 1, 2, 2, 1, 2),
    (1, 2, 1, 1, 0, 2, 0, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 1),
)

Packed = tuple[int, int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disc_value(left: int, right: int, fallback: int) -> int:
    return fallback if left == right else left


def full_tree_values(leaves: Sequence[int]) -> int:
    require(len(leaves) == 27, "depth-three full tree needs 27 leaves")
    layer = list(leaves)
    for _ in range(3):
        require(len(layer) % 3 == 0, "malformed discriminator layer")
        layer = [
            disc_value(*layer[offset : offset + 3])
            for offset in range(0, len(layer), 3)
        ]
    require(len(layer) == 1, "full tree did not reduce to one value")
    return layer[0]


class PackedUniverse:
    def __init__(self, arity: int) -> None:
        require(arity >= 1, "packed universe needs positive arity")
        self.arity = arity
        valuations = tuple(product((0, 1, 2), repeat=arity))
        self.valuation_count = len(valuations)
        self.full_mask = (1 << self.valuation_count) - 1
        self.constants = tuple(
            self._encode(value for _ in valuations) for value in (0, 1, 2)
        )
        self.variables = tuple(
            self._encode(valuation[index] for valuation in valuations)
            for index in range(arity)
        )

    def _encode(self, values: Iterable[int]) -> Packed:
        masks = [0, 0, 0]
        for index, value in enumerate(values):
            masks[value] |= 1 << index
        require(
            (masks[0] | masks[1] | masks[2]) == self.full_mask,
            "packed semantic did not cover its universe",
        )
        require(
            not (masks[0] & masks[1] or masks[0] & masks[2] or masks[1] & masks[2]),
            "packed semantic planes overlap",
        )
        return masks[0], masks[1], masks[2]

    def disc(self, left: Packed, right: Packed, fallback: Packed) -> Packed:
        equal = (
            (left[0] & right[0])
            | (left[1] & right[1])
            | (left[2] & right[2])
        )
        unequal = self.full_mask ^ equal
        return tuple(
            (unequal & left[value]) | (equal & fallback[value])
            for value in range(3)
        )  # type: ignore[return-value]


class SemanticDP:
    def __init__(self, arity: int, *, cache_mid: bool) -> None:
        self.universe = PackedUniverse(arity)
        self.cache_mid = cache_mid
        self.cache: dict[tuple[int, ...], frozenset[Packed]] = {}

    def leaf_semantics(self, label: int) -> frozenset[Packed]:
        if label == CONTROL:
            return frozenset(self.universe.constants)
        if label in CONSTANT_LABELS:
            return frozenset((self.universe.constants[-label - 2],))
        require(0 <= label < self.universe.arity, "branch label outside arity")
        return frozenset((self.universe.variables[label],))

    def subtree(self, labels: tuple[int, ...]) -> frozenset[Packed]:
        require(len(labels) in (1, 3, 9), "unsupported subtree width")
        use_cache = len(labels) <= 3 or self.cache_mid
        if use_cache and labels in self.cache:
            return self.cache[labels]
        if len(labels) == 1:
            result = self.leaf_semantics(labels[0])
        else:
            width = len(labels) // 3
            children = tuple(
                self.subtree(labels[offset : offset + width])
                for offset in range(0, len(labels), width)
            )
            result = frozenset(
                self.universe.disc(left, right, fallback)
                for left in children[0]
                for right in children[1]
                for fallback in children[2]
            )
        if use_cache:
            self.cache[labels] = result
        return result

    def root_children(self, labels: Sequence[int]) -> tuple[frozenset[Packed], ...]:
        require(len(labels) == 27, "router label vector must have 27 leaves")
        return tuple(
            self.subtree(tuple(labels[offset : offset + 9]))
            for offset in range(0, 27, 9)
        )

    def contains_root(
        self,
        children: tuple[frozenset[Packed], ...],
        target: Packed,
    ) -> bool:
        require(len(children) == 3, "root requires three child semantic sets")
        for left in children[0]:
            for right in children[1]:
                equal = (
                    (left[0] & right[0])
                    | (left[1] & right[1])
                    | (left[2] & right[2])
                )
                unequal = self.universe.full_mask ^ equal
                if any(
                    (unequal & left[value]) != (unequal & target[value])
                    for value in range(3)
                ):
                    continue
                for fallback in children[2]:
                    if all(
                        (equal & fallback[value]) == (equal & target[value])
                        for value in range(3)
                    ):
                        return True
        return False

    def projection_vector(self, labels: Sequence[int]) -> tuple[bool, ...]:
        children = self.root_children(labels)
        return tuple(
            self.contains_root(children, variable)
            for variable in self.universe.variables
        )


def baseline_replay() -> dict[str, object]:
    require(sha256_path(BASELINE_SOURCE) == FROZEN_BASELINE_SHA256, "baseline drift")
    control_positions = tuple(
        position for position, label in enumerate(R6_LABELS) if label == CONTROL
    )
    require(len(control_positions) == 18, "R6 control census drift")
    require(sorted(label for label in R6_LABELS if label >= 0) == [0, 0, 1, 2, 3, 4, 4, 4, 5], "R6 branch census drift")

    matches = []
    mutation_mismatches = None
    for target, program in enumerate(R6_PROGRAMS):
        target_matches = 0
        mutated_matches = 0
        mutated = list(program)
        mutated[0] = (mutated[0] + 1) % 3
        for valuation in product((0, 1, 2), repeat=6):
            leaves = [
                program[control_positions.index(position)]
                if label == CONTROL
                else valuation[label]
                for position, label in enumerate(R6_LABELS)
            ]
            target_matches += full_tree_values(leaves) == valuation[target]
            if target == 0:
                mutated_leaves = [
                    mutated[control_positions.index(position)]
                    if label == CONTROL
                    else valuation[label]
                    for position, label in enumerate(R6_LABELS)
                ]
                mutated_matches += full_tree_values(mutated_leaves) == valuation[target]
        require(target_matches == 3**6, f"frozen R6 target {target} failed")
        matches.append(target_matches)
        if target == 0:
            mutation_mismatches = 3**6 - mutated_matches

    require(mutation_mismatches is not None and mutation_mismatches > 0, "mutation ineffective")
    dp = SemanticDP(6, cache_mid=True)
    vector = dp.projection_vector(R6_LABELS)
    require(vector == (True,) * 6, "packed DP failed to recover frozen R6")
    return {
        "q": 6,
        "exact_checks": 6 * 3**6,
        "matches_per_target": matches,
        "packed_projection_vector": list(vector),
        "effective_mutation_mismatches": mutation_mismatches,
    }


def inserted_labels(new_labels: Sequence[int], positions: Sequence[int]) -> tuple[int, ...]:
    require(len(new_labels) == len(positions), "insertion labels/positions disagree")
    labels = list(R6_LABELS)
    for label, position in zip(new_labels, positions, strict=True):
        require(labels[position] == CONTROL, "insertion did not replace a control")
        labels[position] = label
    return tuple(labels)


def search_r7_radii() -> list[dict[str, object]]:
    controls = tuple(position for position, label in enumerate(R6_LABELS) if label == CONTROL)
    dp = SemanticDP(7, cache_mid=True)
    rows = []
    for radius in range(1, 5):
        candidates = 0
        new_target_hits = 0
        full_hits: list[list[int]] = []
        best_surviving_projection_count = 0
        survivor_vectors = []
        for positions in combinations(controls, radius):
            candidates += 1
            labels = inserted_labels((6,) * radius, positions)
            children = dp.root_children(labels)
            if not dp.contains_root(children, dp.universe.variables[6]):
                continue
            new_target_hits += 1
            vector = tuple(
                dp.contains_root(children, variable)
                for variable in dp.universe.variables
            )
            best_surviving_projection_count = max(best_surviving_projection_count, sum(vector))
            survivor_vectors.append(
                {"positions": list(positions), "projection_vector": list(vector)}
            )
            if all(vector):
                full_hits.append(list(positions))
        require(not full_hits, f"unexpected R7 witness at radius {radius}")
        survivor_sha = hashlib.sha256(
            json.dumps(survivor_vectors, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        best_rows = [
            row
            for row in survivor_vectors
            if sum(row["projection_vector"]) == best_surviving_projection_count
        ]
        rows.append(
            {
                "radius": radius,
                "candidates": candidates,
                "new_target_hits": new_target_hits,
                "full_router_hits": full_hits,
                "best_projection_count_among_new_target_hits": best_surviving_projection_count,
                "survivor_vectors_sha256": survivor_sha,
                "highest_scoring_survivor_count": len(best_rows),
                "first_highest_scoring_survivors": best_rows[:3],
            }
        )
    require([row["candidates"] for row in rows] == [18, 153, 816, 3060], "R7 radius census drift")
    return rows


def search_minimal_multi_insertions(arity: int) -> dict[str, object]:
    require(arity in (8, 9), "this exact search covers R8 or R9")
    insertions = arity - 6
    controls = tuple(position for position, label in enumerate(R6_LABELS) if label == CONTROL)
    dp = SemanticDP(arity, cache_mid=False)
    candidates = 0
    all_new_target_hits = 0
    full_hits = []
    for positions in combinations(controls, insertions):
        candidates += 1
        labels = inserted_labels(tuple(range(6, arity)), positions)
        children = dp.root_children(labels)
        if not all(
            dp.contains_root(children, dp.universe.variables[target])
            for target in range(6, arity)
        ):
            continue
        all_new_target_hits += 1
        vector = tuple(
            dp.contains_root(children, variable)
            for variable in dp.universe.variables
        )
        if all(vector):
            full_hits.append(
                {"positions": list(positions), "projection_vector": list(vector)}
            )
    require(not full_hits, f"unexpected direct-Q R{arity} witness")
    expected = 153 if arity == 8 else 816
    require(candidates == expected, f"R{arity} candidate census drift")
    return {
        "q": arity,
        "neighborhood": f"choose {insertions} frozen R6 controls and insert one copy of each new branch",
        "candidate_count_modulo_new_label_permutation": candidates,
        "all_new_target_hits": all_new_target_hits,
        "full_router_hits": full_hits,
    }


def specialized_labels(labels: Sequence[int], target: int, other_value: int) -> tuple[int, ...]:
    constant_label = CONSTANT_LABELS[other_value]
    return tuple(
        label if label == CONTROL else (0 if label == target else constant_label)
        for label in labels
    )


def search_minimal_r10() -> dict[str, object]:
    controls = tuple(position for position, label in enumerate(R6_LABELS) if label == CONTROL)
    unary_dp = SemanticDP(1, cache_mid=True)
    candidates = 0
    specialization_survivors = []
    for positions in combinations(controls, 4):
        candidates += 1
        labels = inserted_labels((6, 7, 8, 9), positions)
        passed = True
        for target in range(6, 10):
            for other_value in (0, 1, 2):
                specialized = specialized_labels(labels, target, other_value)
                if unary_dp.projection_vector(specialized) != (True,):
                    passed = False
                    break
            if not passed:
                break
        if passed:
            specialization_survivors.append((positions, labels))

    require(candidates == 3060, "R10 candidate census drift")
    require(
        [positions for positions, _ in specialization_survivors] == [(0, 6, 18, 24)],
        "R10 specialization survivor drift",
    )
    exact_dp = SemanticDP(10, cache_mid=False)
    exact_survivors = []
    survivor_rows = []
    for positions, labels in specialization_survivors:
        children = exact_dp.root_children(labels)
        new_vector = tuple(
            exact_dp.contains_root(children, exact_dp.universe.variables[target])
            for target in range(6, 10)
        )
        survivor_rows.append(
            {"positions": list(positions), "new_target_vector": list(new_vector)}
        )
        if all(new_vector):
            full_vector = tuple(
                exact_dp.contains_root(children, variable)
                for variable in exact_dp.universe.variables
            )
            if all(full_vector):
                exact_survivors.append(list(positions))
    require(not exact_survivors, "unexpected direct-Q R10 witness")
    return {
        "q": 10,
        "neighborhood": "choose four frozen R6 controls and insert b6,b7,b8,b9 once each",
        "candidate_count_modulo_new_label_permutation": candidates,
        "necessary_specializations": "for every new target, set all other branches uniformly to each of 0,1,2",
        "specialization_survivors": survivor_rows,
        "full_router_hits": exact_survivors,
    }


def r6_branch_slot_partitions() -> dict[str, object]:
    """Search every seven-label partition of the nine frozen R6 branch slots."""
    slots = tuple(position for position, label in enumerate(R6_LABELS) if label >= 0)
    require(len(slots) == 9, "R6 branch-slot census drift")
    partitions = []
    # Seven nonempty unlabeled blocks of nine elements have shape 3+1+...+1
    # or 2+2+1+...+1. Canonical block order is by the least member.
    for triple in combinations(range(9), 3):
        used = set(triple)
        blocks = [tuple(triple)] + [(index,) for index in range(9) if index not in used]
        partitions.append(blocks)
    for four in combinations(range(9), 4):
        a, b, c, d = four
        for pair1, pair2 in (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))):
            used = set(four)
            blocks = [pair1, pair2] + [(index,) for index in range(9) if index not in used]
            partitions.append(blocks)
    require(len(partitions) == 462, "seven-block partition census drift")

    dp = SemanticDP(7, cache_mid=True)
    full_hits = []
    first_failed_target_counts = [0] * 7
    for blocks in partitions:
        ordered = sorted((tuple(sorted(block)) for block in blocks), key=lambda block: block[0])
        labels = [CONTROL] * 27
        for branch, block in enumerate(ordered):
            for slot_index in block:
                labels[slots[slot_index]] = branch
        children = dp.root_children(labels)
        vector = []
        for target, variable in enumerate(dp.universe.variables):
            reachable = dp.contains_root(children, variable)
            vector.append(reachable)
            if not reachable:
                first_failed_target_counts[target] += 1
                break
        if len(vector) == 7 and all(vector):
            full_hits.append(
                {"blocks": [list(block) for block in ordered], "projection_vector": list(vector)}
            )
    require(not full_hits, "unexpected R7 witness on frozen branch slots")
    return {
        "q": 7,
        "neighborhood": "all 462 seven-block partitions of the nine frozen R6 branch positions; controls fixed",
        "candidate_count": len(partitions),
        "first_failed_target_counts": first_failed_target_counts,
        "full_router_hits": full_hits,
    }


def malformed_gate() -> bool:
    rejected = False
    try:
        SemanticDP(7, cache_mid=False).root_children(R6_LABELS[:-1])
    except RuntimeError:
        rejected = True
    require(rejected, "malformed 26-leaf tree survived")
    return rejected


def main() -> None:
    summary = {
        "schema": "orbit-synthesis/direct-q-packed-semantic-neighborhood/v1",
        "algebra": "Q=({0,1,2}; d), d(x,y,z)=z if x=y else x",
        "grammar": "full depth-three discriminator tree; branch leaves plus independent absolute Q-valued control leaves",
        "representation": "exact three-plane Python-integer truth-table bitsets with bottom-up semantic-set DP",
        "baseline_source_sha256": sha256_path(BASELINE_SOURCE),
        "baseline": baseline_replay(),
        "r7_control_insertion_radii": search_r7_radii(),
        "r7_frozen_branch_slot_partitions": r6_branch_slot_partitions(),
        "r8_minimal_insertion": search_minimal_multi_insertions(8),
        "r9_minimal_insertion": search_minimal_multi_insertions(9),
        "r10_minimal_insertion": search_minimal_r10(),
        "malformed_tree_rejected": malformed_gate(),
        "claim_boundary": (
            "Exact bounded NO_HIT results only for the displayed frozen-R6 neighborhoods. "
            "They are not global direct-Q R7/R8/R9/R10 UNSAT results, not a lower bound "
            "for arbitrary Q terms, and not novelty, patent, FTO, practical-performance, "
            "or Tau-capability evidence. Controls are program values independent of payload."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS direct-Q packed semantic neighborhood search")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

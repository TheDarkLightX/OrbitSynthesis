#!/usr/bin/env python3
"""Independent lower-bound replay: frozen R9 lies in positive-polarity grammar."""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
WITNESS = (
    ROOT
    / "research/tournaments/2026-08-13-router-frontier/lanes/capacity/boolean_q9_r8_radius1.json"
)
WITNESS_SHA256 = "d3c25e47ce671d8a5d484d6c50cc0b3fccf7f6bb5507097ef8bff6bcbbbe529c"
BITS = (0, 1)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


def polarity(leaf: int) -> int:
    middle = 0
    value = leaf
    for _ in range(3):
        middle += value % 3 == 1
        value //= 3
    return -1 if middle % 2 else 1


def evaluate(labels: list[int], row: list[int], valuation: tuple[int, ...]) -> int:
    values = [
        row[position] if label == 0 else valuation[label - 1]
        for position, label in enumerate(labels)
    ]
    while len(values) > 1:
        values = [disc(*values[3 * index : 3 * index + 3]) for index in range(len(values) // 3)]
    return values[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args()
    require(hashlib.sha256(WITNESS.read_bytes()).hexdigest() == WITNESS_SHA256, "R9 bytes drifted")
    payload = json.loads(WITNESS.read_text())
    require(payload["status"] == "SAT_EXACT" and payload["exact"] is True, "R9 not exact")
    require(payload["q"] == 9 and payload["depth"] == 3, "R9 q/depth drift")
    labels = [int(value) for value in payload["labels"]]
    rows = [[int(value) for value in row] for row in payload["full_control_rows"]]
    branch_positions = [(position, label - 1) for position, label in enumerate(labels) if label]
    require(len(labels) == 27, "R9 leaf count drift")
    require(sorted(branch for _, branch in branch_positions) == list(range(9)), "R9 branch census drift")
    require(all(polarity(position) == 1 for position, _ in branch_positions), "R9 has negative-polarity branch")
    require(len(rows) == 9 and all(len(row) == 27 for row in rows), "R9 control rows drift")

    matches = []
    mutations = []
    controls = [position for position, label in enumerate(labels) if label == 0]
    for target in range(9):
        target_matches = sum(
            evaluate(labels, rows[target], valuation) == valuation[target]
            for valuation in product(BITS, repeat=9)
        )
        require(target_matches == 512, f"R9 projection failed at target {target}")
        matches.append(target_matches)
        effective = None
        for position in controls:
            mutated = list(rows[target])
            mutated[position] ^= 1
            mutation_matches = sum(
                evaluate(labels, mutated, valuation) == valuation[target]
                for valuation in product(BITS, repeat=9)
            )
            if mutation_matches < 512:
                effective = {
                    "target": target,
                    "position": position,
                    "matches_after_flip": mutation_matches,
                }
                break
        require(effective is not None, f"no effective mutation for target {target}")
        mutations.append(effective)

    summary: dict[str, object] = {
        "schema": "orbitsynthesis/positive-r9-lower/v1",
        "witness_sha256": WITNESS_SHA256,
        "q": 9,
        "depth": 3,
        "branch_positions": branch_positions,
        "all_branch_positions_positive": True,
        "positive_leaf_count": sum(polarity(position) == 1 for position in range(27)),
        "negative_leaf_count": sum(polarity(position) == -1 for position in range(27)),
        "matches_per_target": matches,
        "checks": sum(matches),
        "effective_mutations": mutations,
        "claim_boundary": "Exact finite lower bound P_pos(3)>=9 only; generic compiler and novelty are separate.",
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS positive-polarity R9 lower bound")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

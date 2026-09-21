#!/usr/bin/env python3
"""Exact recurrence/census checker for the sibling-shared rail construction.

This lane extends the direct absorbing-rail representation with two semantic
hash-consing identities:

* O_(a s) = O_a whenever the suffix s contains no physical digit 2;
* N_(a 1) = O_(a 2), where N is the not-zero-mode rail.

The first removes duplicate gain materialization.  The second lets every
negative a1 output point at an already requested sibling output.  The script
reuses the independent executable semantics in check_native_scan.py but owns
its analytic recurrences and all-width asymptotic ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from functools import cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "check_native_scan.py"
STATE = HERE.parents[1] / "STATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_subject():
    spec = importlib.util.spec_from_file_location("native_scan_subject", SUBJECT)
    require(spec is not None and spec.loader is not None, "cannot load subject")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@cache
def rail_nodes(width: int) -> int:
    """All (Z,O) rails for a block, excluding the two global names."""
    require(width >= 1, "positive rail width")
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    q_left = 3**left
    q_right = 3**right
    return (
        rail_nodes(left)
        + rail_nodes(right)
        + q_left * q_right
        + q_left * (q_right - 1) // 2
    )


@cache
def extended_nodes(width: int) -> int:
    """All (Z,O,N) rails, excluding names; N is needed only on a suffix."""
    require(width >= 1, "positive extended width")
    if width == 1:
        return 4
    left = (width + 1) // 2
    right = width // 2
    q_left = 3**left
    q_right = 3**right
    return (
        rail_nodes(left)
        + extended_nodes(right)
        # q zero rails; only 2q/3 new not-zero rails because
        # N_(a1)=O_(a2) reuses all q/3 middle-sibling cases.
        + 2 * q_left * q_right
        - 3 ** (width - 1)
        + q_left * (q_right - 1) // 2
    )


def overlap_count(width: int, root_sign: int) -> int:
    """Requested N_(a1)=O_(a2) overlaps for the chosen root sign."""
    require(width >= 1 and root_sign in (0, 1), "bad overlap input")
    prefixes = 3 ** (width - 1)
    return (prefixes + (1 if root_sign == 0 else -1)) // 2


def vector_nodes(width: int, root_sign: int) -> int:
    """Safe pre-hash-cons upper ledger including the two global names."""
    require(width >= 1 and root_sign in (0, 1), "bad vector input")
    if width == 1:
        return 5 + root_sign
    left = (width + 1) // 2
    right = width // 2
    q_left = 3**left
    q_right = 3**right
    q = q_left * q_right
    distinct_root_gains = q_left * (q_right - 1) // 2
    return (
        2
        + rail_nodes(left)
        + extended_nodes(right)
        + distinct_root_gains
        + q
        - overlap_count(width, root_sign)
    )


def arithmetic(max_width: int) -> dict[str, object]:
    worst_scaled_slack: int | None = None
    worst_ratio = (0, 0, 1)
    rows = []
    for width in range(1, max_width + 1):
        q = 3**width
        for root_sign in (0, 1):
            nodes = vector_nodes(width, root_sign)
            # Explicit all-width convergence envelope.
            error_scale = 3 ** ((width + 1) // 2)
            slack = 4 * q + 15 * error_scale - 3 * nodes
            require(slack >= 0, "4q/3+sqrt envelope failed")
            worst_scaled_slack = slack if worst_scaled_slack is None else min(worst_scaled_slack, slack)
            if nodes * worst_ratio[2] > worst_ratio[1] * q:
                worst_ratio = (width, nodes, q)
            if width <= 16:
                rows.append(
                    {
                        "width": width,
                        "root_sign": root_sign,
                        "q": q,
                        "nodes": nodes,
                        "scaled_lower_gap": 3 * nodes - 4 * q,
                        "envelope_slack": slack,
                    }
                )
    return {
        "widths": max_width,
        "rows": rows,
        "all_width_envelope": "3*S(w) <= 4*3^w + 15*3^ceil(w/2)",
        "asymptotic": "S(w) <= (4/3+o(1))*3^w",
        "worst_envelope_slack": worst_scaled_slack,
        "max_ratio": {
            "width": worst_ratio[0],
            "numerator": worst_ratio[1],
            "denominator": worst_ratio[2],
        },
    }


def exact(max_width: int) -> dict[str, object]:
    subject = load_subject()
    rows = []
    comparisons = 0
    for width in range(1, max_width + 1):
        q = 3**width
        for root_sign in (0, 1):
            dag, pairs, _digits = subject.build_projection_vector(width, root_sign)
            roots = subject.flatten_roots(pairs, width)
            actual_nodes = dag.reachable_operation_count(roots)
            require(actual_nodes <= vector_nodes(width, root_sign), "ledger undercounts DAG")
            require(max(dag.depths[root] for root in roots) <= 3 + subject.ceil_log2(width), "depth drift")
            for target in subject.words(width):
                actual = subject.evaluate_pairs(dag, pairs, target)
                for index, physical in enumerate(subject.words(width)):
                    expected = subject.expected_pair(root_sign, physical, target, "projection")
                    require(actual[index] == expected, "semantic mismatch")
                    comparisons += 1
            rows.append(
                {
                    "width": width,
                    "root_sign": root_sign,
                    "q": q,
                    "actual_nodes": actual_nodes,
                    "upper_nodes": vector_nodes(width, root_sign),
                    "depth": max(dag.depths[root] for root in roots),
                }
            )
    return {"max_width": max_width, "comparisons": comparisons, "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=6)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(1 <= args.max_width <= 7, "exact budget")
    payload: dict[str, object] = {
        "schema": "orbit-synthesis/sibling-shared-program-vector/v1",
        "status": "PROVISIONAL_EXACT_UPPER_MATCHES_LEADING_OUTPUT_LOWER",
        "state_sha256": sha256_path(STATE),
        "subject_sha256": sha256_path(SUBJECT),
        "exact": exact(args.max_width),
        "arithmetic": arithmetic(4096),
        "claim": {
            "upper": "S(w) <= 4q/3 + 5*3^ceil(w/2)",
            "leading": "limsup S(w)/q <= 4/3",
            "depth": "D(w) <= 3+ceil(log2 w)",
            "scope": "one fixed root sign, A=2, scalar same-DAG/free-fanout original d/u signature",
        },
        "nonclaims": [
            "No second independent audit yet.",
            "No Lean proof yet.",
            "No exact finite-width optimum beyond the established small bases.",
            "No formula or bounded-fanout transfer.",
            "No integrated compiler, novelty, or FTO promotion.",
        ],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["semantic_sha256"] = hashlib.sha256(canonical).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

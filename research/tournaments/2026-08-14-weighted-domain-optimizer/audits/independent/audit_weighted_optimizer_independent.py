#!/usr/bin/env python3
"""No-import exhaustive audit of the unary weighted-domain corpus.

For Quackenbush Q, a unary original-signature term operation is determined by

* one Boolean value f(0), with f(1)=1-f(0) by the internal complement; and
* an arbitrary value f(2) in Q.

Thus exactly six unary term functions need be checked.  This script imports no
OrbitSynthesis implementation and independently solves all 512 unary safety
relations under the same six weighted scenarios as the primary audit.
"""

from __future__ import annotations

import hashlib
import json

SCENARIOS = (
    ("unit", (1, 1, 1), 0, 0),
    ("skew", (3, -2, 1), 0, 0),
    ("negative", (-3, 5, 0), 0, 0),
    ("zero", (0, 0, 0), 0, 0),
    ("require-zero", (2, 1, -4), 1, 0),
    ("forbid-two", (1, 4, 9), 0, 4),
)
TERM_FUNCTIONS = tuple(
    (zero_value, 1 - zero_value, two_value)
    for zero_value in (0, 1)
    for two_value in (0, 1, 2)
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def feasible(relation_mask: int, domain_mask: int) -> bool:
    for function in TERM_FUNCTIONS:
        valid = True
        for source in range(3):
            if not domain_mask & (1 << source):
                continue
            target = function[source]
            if not domain_mask & (1 << target):
                valid = False
                break
            if not relation_mask & (1 << (3 * source + target)):
                valid = False
                break
        if valid:
            return True
    return False


def objective(mask: int, weights: tuple[int, ...]) -> tuple[int, int, int]:
    return (
        sum(weight for index, weight in enumerate(weights) if mask & (1 << index)),
        mask.bit_count(),
        mask,
    )


def corpus() -> dict[str, object]:
    rows = []
    feasible_instances = 0
    infeasible_instances = 0
    for relation_mask in range(1 << 9):
        for label, weights, required, forbidden in SCENARIOS:
            best = None
            for domain_mask in range(1 << 3):
                if required & ~domain_mask or forbidden & domain_mask:
                    continue
                if not feasible(relation_mask, domain_mask):
                    continue
                row = objective(domain_mask, weights)
                if best is None or row > best:
                    best = row
            if best is None:
                rows.append([relation_mask, label, None])
                infeasible_instances += 1
            else:
                rows.append([relation_mask, label, list(best)])
                feasible_instances += 1
    rendered = json.dumps(rows, separators=(",", ":"))
    return {
        "term_functions": len(TERM_FUNCTIONS),
        "relations": 1 << 9,
        "scenarios": len(SCENARIOS),
        "instances": len(rows),
        "feasible_instances": feasible_instances,
        "infeasible_instances": infeasible_instances,
        "corpus_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
    }


def preference() -> dict[str, object]:
    preferences = {
        (0, 1): 5,
        (1, 0): 5,
        (2, 2): 3,
    }
    scored = []
    for function in TERM_FUNCTIONS:
        score = sum(preferences.get((source, function[source]), 0) for source in range(3))
        scored.append((score, function))
    best_score, best_function = max(scored, key=lambda row: row[0])
    require(best_score == 13, "preference score drift")
    require(best_function == (1, 0, 2), "preference function drift")
    return {
        "score": best_score,
        "function": list(best_function),
    }


def main() -> None:
    result = {
        "schema": "orbit-synthesis/weighted-domain-optimizer-independent/v1",
        "unary_corpus": corpus(),
        "preference": preference(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

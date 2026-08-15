#!/usr/bin/env python3
"""No-import audit of the two portable proof-bundle examples."""

from __future__ import annotations

import hashlib
from itertools import product
import json
from pathlib import Path
import sys

Q = (0, 1, 2)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def check_hashes(bundle: dict[str, object]) -> None:
    recorded_manifest = bundle["manifest_sha256"]
    semantic = dict(bundle)
    semantic.pop("manifest_sha256")
    if canonical_hash(semantic) != recorded_manifest:
        raise AssertionError("bundle manifest mismatch")

    problem = bundle["problem"]
    if canonical_hash(problem) != bundle["problem_sha256"]:
        raise AssertionError("problem hash mismatch")

    certificate = dict(bundle["optimality_certificate"])
    recorded_certificate = certificate.pop("semantic_sha256")
    certificate.pop("statistics")
    if canonical_hash(certificate) != recorded_certificate:
        raise AssertionError("certificate hash mismatch")


def exact_q(problem: dict[str, object]) -> None:
    algebra = problem["algebra"]
    if algebra["carrier"] != [0, 1, 2]:
        raise AssertionError("unexpected carrier")
    operations = {row["name"]: row for row in algebra["operations"]}
    expected_d = [
        discriminator(*arguments)
        for arguments in product(Q, repeat=3)
    ]
    if operations["d"] != {"name": "d", "arity": 3, "outputs": expected_d}:
        raise AssertionError("wrong discriminator table")
    if operations["u"] != {"name": "u", "arity": 1, "outputs": [1, 0, 1]}:
        raise AssertionError("wrong unary table")


def transition_map(problem: dict[str, object]):
    relation = problem["game"]["safe_relation"]
    if relation["mode"] != "allowed":
        raise AssertionError("bundles must carry canonical allowlists")
    result = {}
    for row in relation["transitions"]:
        key = (tuple(row["state"]), tuple(row["input"]))
        result.setdefault(key, set()).add(tuple(row["output"]))
    return result


def audit_optimal(bundle: dict[str, object]) -> dict[str, object]:
    check_hashes(bundle)
    problem = bundle["problem"]
    exact_q(problem)
    result = bundle["result"]
    if result["status"] != "optimal":
        raise AssertionError("optimal example lost optimal status")
    if result["domain"] != [[0], [1], [2]]:
        raise AssertionError("optimal domain is not the full carrier")
    if result["signed_utility"] != 3:
        raise AssertionError("optimal score is not three")

    safe = transition_map(problem)
    expected_safe = {
        ((x,), (y, z)): {(discriminator(x, y, z),)}
        for x, y, z in product(Q, repeat=3)
    }
    if safe != expected_safe:
        raise AssertionError("safe relation is not the discriminator graph")

    strategy = {
        tuple(row["observation"]): tuple(row["output"])
        for row in result["strategy"]
    }
    expected_strategy = {
        (x, y, z): (discriminator(x, y, z),)
        for x, y, z in product(Q, repeat=3)
    }
    if strategy != expected_strategy:
        raise AssertionError("controller table is not exactly d")

    certificate = bundle["optimality_certificate"]
    if certificate["target_score"] != 3:
        raise AssertionError("wrong certified optimum")
    if certificate["target_domain_mask"] != 7:
        raise AssertionError("wrong full-domain mask")
    if any(weight != 1 for weight in certificate["weights"]):
        raise AssertionError("wrong optimal weights")
    if certificate["required_mask"] or certificate["forbidden_mask"]:
        raise AssertionError("unexpected hard state mask")

    # All three weights are positive. The exact root upper bound is three, so
    # the full-domain target can be certified by a one-node bound proof.
    nodes = certificate["nodes"]
    if len(nodes) != 1 or nodes[0]["kind"] != "bound":
        raise AssertionError("expected one-node full-domain bound proof")
    if nodes[0]["upper_bound"] != 3:
        raise AssertionError("wrong root upper bound")

    return {
        "problem_sha256": bundle["problem_sha256"],
        "manifest_sha256": bundle["manifest_sha256"],
        "strategy_rows": len(strategy),
        "certificate_nodes": len(nodes),
        "score": result["signed_utility"],
    }


def unary_term_tables():
    # Exact unary Q-term census from internal-complement preservation:
    # f(1)=1-f(0), while f(2) is arbitrary.
    return tuple((a, 1 - a, b) for a in (0, 1) for b in Q)


def audit_infeasible(bundle: dict[str, object]) -> dict[str, object]:
    check_hashes(bundle)
    problem = bundle["problem"]
    exact_q(problem)
    result = bundle["result"]
    if result["status"] != "infeasible":
        raise AssertionError("coupled example became feasible")
    if result["domain"] is not None or result["strategy"]:
        raise AssertionError("infeasible result carried a controller")

    safe = transition_map(problem)
    expected_safe = {
        ((0,), ()): {(0,)},
        ((1,), ()): {(0,)},
        ((2,), ()): {(2,)},
    }
    if safe != expected_safe:
        raise AssertionError("unexpected coupled safety table")

    required = {(0,), (1,)}
    feasible = []
    for table in unary_term_tables():
        for include_two in (False, True):
            domain = set(required)
            if include_two:
                domain.add((2,))
            valid = True
            for state in domain:
                output = (table[state[0]],)
                if output not in domain or output not in safe.get((state, ()), set()):
                    valid = False
                    break
            if valid:
                feasible.append((table, sorted(domain)))
    if feasible:
        raise AssertionError("a Q-term controller satisfied the coupled instance")

    certificate = bundle["optimality_certificate"]
    if certificate["target_score"] is not None:
        raise AssertionError("infeasibility proof carried a target score")
    if certificate["required_mask"] != 3:
        raise AssertionError("required-state mask is not {0,1}")
    if any(node["kind"] == "bound" for node in certificate["nodes"]):
        raise AssertionError("infeasibility proof used an objective bound")

    return {
        "problem_sha256": bundle["problem_sha256"],
        "manifest_sha256": bundle["manifest_sha256"],
        "unary_term_tables_checked": len(unary_term_tables()),
        "candidate_domains_checked": 2 * len(unary_term_tables()),
        "certificate_nodes": len(certificate["nodes"]),
    }


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: audit_bundle_examples_independent.py OPTIMAL INFEASIBLE")
    optimal = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    infeasible = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    result = {
        "schema": "orbit-synthesis/portable-proof-bundle-independent/v1",
        "optimal": audit_optimal(optimal),
        "infeasible": audit_infeasible(infeasible),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

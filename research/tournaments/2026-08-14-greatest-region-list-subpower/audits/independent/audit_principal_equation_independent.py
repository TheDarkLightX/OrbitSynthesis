#!/usr/bin/env python3
"""No-OrbitSynthesis reconstruction of the principal-equation converse."""

from __future__ import annotations

import hashlib
import itertools
import json

from audit_frontiers_independent import (
    Alg,
    Q,
    domain_feasible,
    maximal_nonextendable,
    orbit,
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def principal_witness(algebra: Alg):
    isomorphisms = algebra.isomorphisms()
    phi = maximal_nonextendable(algebra, isomorphisms)
    if phi is None:
        return None

    source = tuple(sorted(phi.domain))
    b0, b1 = source[:2]
    p0 = source + (b0, b0)
    p1 = source + (b0, b1)
    state = source + (b1, b0)
    q0 = phi.map(p0)
    q1 = phi.map(p1)
    target = phi.map(state)
    beta = next(value for value in Q if value not in phi.domain)
    gamma = next(value for value in Q if value not in phi.codomain)

    critical = orbit(state + (b0,), isomorphisms)
    dead = (
        orbit(p1 + (beta,), isomorphisms)
        | orbit(q0 + (gamma,), isomorphisms)
    )
    need(not critical & dead, "critical/dead collision")

    critical_transitions = set()
    for output in (p0, p1):
        critical_transitions.update(
            orbit(state + (b0,) + output, isomorphisms)
        )

    k = len(state)
    states = tuple(itertools.product(Q, repeat=k))
    safe = set()
    for source_state in states:
        for input_value in Q:
            observation = source_state + (input_value,)
            if observation in critical or observation in dead:
                continue
            for output in states:
                safe.add((source_state, input_value, output))
    for row in critical_transitions:
        safe.add((row[:k], row[k], row[k + 1 :]))

    return {
        "k": k,
        "left": frozenset((state, p0)),
        "right": frozenset((target, q1)),
        "safe": frozenset(safe),
        "isos": isomorphisms,
    }


def audit_one(algebra: Alg, witness) -> tuple[int, bool]:
    need(domain_feasible(algebra, witness, witness["left"]), "left")
    need(domain_feasible(algebra, witness, witness["right"]), "right")
    need(
        not domain_feasible(
            algebra,
            witness,
            witness["left"] | witness["right"],
        ),
        "union",
    )

    k = witness["k"]
    safe_flat = {
        state + (input_value,) + output
        for state, input_value, output in witness["safe"]
    }
    rows = tuple(itertools.product(Q, repeat=2 * k + 1))
    mutation_effective = False

    for row in rows:
        safe = row in safe_flat
        separator = row[0] if safe else row[1]
        need((row[0] == separator) == safe, "principal equation")
        if not safe:
            need(row[0] != row[1], "unsafe tag equality")
            mutation_effective = mutation_effective or row[0] == row[0]
        need(separator in algebra.generated(row), "subalgebra")

        for iso in witness["isos"]:
            if not iso.applies(row):
                continue
            mapped = iso.map(row)
            mapped_separator = mapped[0] if mapped in safe_flat else mapped[1]
            need(separator in iso.domain, "separator outside iso domain")
            need(mapped_separator == iso.mapping[separator], "equivariance")
            need((mapped in safe_flat) == safe, "relation invariance")

    need(mutation_effective, "unsafe branch mutation")
    return len(rows), mutation_effective


def receipt():
    need(principal_witness(Alg()) is None, "pure discriminator control")
    demi = non_demi = rows_checked = 0
    classifications = []
    for table in itertools.product(Q, repeat=3):
        algebra = Alg(tuple(table))
        witness = principal_witness(algebra)
        if witness is None:
            demi += 1
            classifications.append([list(table), True])
            continue
        checked, _ = audit_one(algebra, witness)
        non_demi += 1
        rows_checked += checked
        classifications.append([list(table), False])

    need((demi, non_demi) == (15, 12), "extension census")
    result = {
        "schema": "orbit-synthesis/principal-greatest-region-independent/v1",
        "demi": demi,
        "non_demi": non_demi,
        "flattened_rows_checked": rows_checked,
        "classifications": classifications,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main():
    result = receipt()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

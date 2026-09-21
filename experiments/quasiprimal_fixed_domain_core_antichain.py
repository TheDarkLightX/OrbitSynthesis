#!/usr/bin/env python3
"""Exact no-least-core witness and exhaustive pure-discriminator census."""
from __future__ import annotations
import argparse, hashlib, json, sys
from itertools import permutations, product
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
Q = (0, 1, 2)
ROWS = tuple(product(Q, repeat=2))
IDX = {row: i for i, row in enumerate(ROWS)}
CORES = tuple(frozenset(Q[i] for i in range(3) if mask >> i & 1) for mask in range(8))
SUBALGEBRAS = tuple(core for core in CORES if core)

def discriminator(x, y, z):
    return z if x == y else x

def target(x, y):
    return 2 if (x, y) == (2, 2) else 0

def internal_isomorphisms(core):
    result = []
    for source in SUBALGEBRAS:
        if not core <= source:
            continue
        source_order = tuple(sorted(source))
        for codomain in SUBALGEBRAS:
            if len(source) != len(codomain) or not core <= codomain:
                continue
            for image in permutations(sorted(codomain)):
                mapping = dict(zip(source_order, image, strict=True))
                if any(mapping[value] != value for value in core):
                    continue
                if all(mapping[discriminator(x, y, z)] == discriminator(mapping[x], mapping[y], mapping[z]) for x, y, z in product(source_order, repeat=3)):
                    result.append((source, mapping))
    return tuple(result)

CONSTRAINTS = {
    core: tuple(
        (IDX[row], IDX[tuple(mapping[x] for x in row)], source, tuple(mapping.get(x, -1) for x in Q))
        for source, mapping in internal_isomorphisms(core)
        for row in product(sorted(source), repeat=2)
    )
    for core in CORES
}

def preserves(core, table):
    return all(table[i] in source and table[j] == mapping[table[i]] for i, j, source, mapping in CONSTRAINTS[core])

def direct_census():
    operation_counts = {core: 0 for core in CORES}
    budget_counts = {}
    multiplicities = {}
    for table in product(Q, repeat=9):
        feasible = [core for core in CORES if preserves(core, table)]
        for core in feasible:
            operation_counts[core] += 1
        budget = min(map(len, feasible))
        budget_counts[budget] = budget_counts.get(budget, 0) + 1
        multiplicity = sum(len(core) == budget for core in feasible)
        multiplicities[multiplicity] = multiplicities.get(multiplicity, 0) + 1
    by_size = {size: {count for core, count in operation_counts.items() if len(core) == size} for size in range(4)}
    assert all(len(values) == 1 for values in by_size.values())
    counts = {size: next(iter(values)) for size, values in by_size.items()}
    assert counts == {0: 2, 1: 24, 2: 3888, 3: 19683}
    assert budget_counts == {0: 2, 1: 66, 2: 9932, 3: 9683}
    assert multiplicities == {1: 18151, 2: 1488, 3: 44}
    witness_table = tuple(target(*row) for row in ROWS)
    minima = [core for core in CORES if preserves(core, witness_table) and len(core) == 2]
    assert set(minima) == {frozenset({0, 1}), frozenset({0, 2})}
    assert all(discriminator(x, discriminator(x, y, 1), 0) == target(x, y) for x, y in ROWS)
    assert all(discriminator(x, discriminator(x, y, discriminator(x, 2, 0)), 0) == target(x, y) for x, y in ROWS)
    return {
        "operation_counts_by_core_size": counts,
        "minimum_budget_counts": budget_counts,
        "minimum_core_multiplicity_counts": multiplicities,
        "witness_minimum_cores": [sorted(core) for core in minima],
    }

def api_witness():
    sys.path.insert(0, str(ROOT / "src"))
    from orbitsynthesis.finite_algebra import FiniteAlgebra
    from orbitsynthesis.fixed_domain import deterministic_table_reduction, minimum_cores_for_domain
    algebra = FiniteAlgebra.from_callables(Q, {"d": (3, discriminator)})
    reduction = deterministic_table_reduction(algebra, 2, target)
    result = minimum_cores_for_domain(reduction.game, reduction.full_domain)
    assert {point.core for point in result.all_feasible} == {frozenset({0, 1}), frozenset({0, 2}), frozenset(Q)}
    assert {point.core for point in result.minimum_rank} == {frozenset({0, 1}), frozenset({0, 2})}
    assert result.least_core is None
    return {
        "all_feasible_cores": [sorted(point.core) for point in result.all_feasible],
        "minimum_rank_cores": [sorted(point.core) for point in result.minimum_rank],
        "least_core": None,
        "minimum_parameter_budget": result.minimum_parameter_budget,
        "strategy_matches_target": all(point.strategy == reduction.target_strategy for point in result.minimum_rank),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", type=Path)
    parser.add_argument("--direct-only", action="store_true")
    args = parser.parse_args()
    semantic = {
        "schema": "orbit-synthesis/fixed-domain-core-antichain/v1",
        "direct_census": direct_census(),
        "api_witness": None if args.direct_only else api_witness(),
        "statuses": {"unique_least_core": "FAILED", "budget_only": "FAILED", "core_antichain": "TESTED_ONLY", "table_reduction": "TESTED_ONLY"},
    }
    semantic["semantic_sha256"] = hashlib.sha256(json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if args.out_root:
        args.out_root.mkdir(parents=True, exist_ok=True)
        (args.out_root / "summary.json").write_text(json.dumps(semantic, indent=2, sort_keys=True) + "\n")
    print(json.dumps(semantic, sort_keys=True))

if __name__ == "__main__":
    main()

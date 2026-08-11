#!/usr/bin/env python3
"""Benchmark the support-symbolic ocLTL §5.2 feasibility relation for ABA.

This script compares two views of the same pure-ABA three-variable object:

1. the explicit outer combination space
       T2 x T1 x {0,1}^|Delta|
   of size 45*2^d;
2. the ROBDD obtained from the support circuit
       exists Q . RowCompat(P,Q) & ColCompat(R,Q)
                  & AND_i (D_i <-> delta_i(Q)).

For the first benchmark family, every delta_i is an atomic equation `f_i=0`
represented by the 8-bit minterm support of f_i.

The code uses the small dependency-free ROBDD reference manager from
`aba_support_bdd.py`.  Exhaustive enumeration of all 255 complete T3 support
patterns is used only as an independent validation/counting oracle, not to
construct the BDD.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass

from aba_support_bdd import ROBDD


@dataclass(frozen=True)
class Layout:
    p: tuple[int, ...]
    r: tuple[int, ...]
    d: tuple[int, ...]
    q: tuple[int, ...]


def layout(num_delta: int) -> Layout:
    """Variable order: P(4), R(2), D(d), Q(8)."""
    p = tuple(range(4))
    r = tuple(range(4, 6))
    d = tuple(range(6, 6 + num_delta))
    q = tuple(range(6 + num_delta, 14 + num_delta))
    return Layout(p=p, r=r, d=d, q=q)


def eq(manager: ROBDD, left: int, right: int) -> int:
    return manager.apply("eq", left, right)


def atomic_eq0_on_q(manager: ROBDD, q_vars: tuple[int, ...], term_mask: int) -> int:
    """Support translation of f=0 for an 8-minterm Boolean term."""
    literals = [
        manager.neg(manager.var(q_vars[v]))
        for v in range(8)
        if term_mask & (1 << v)
    ]
    return manager.conjunction(*literals)


def build_feasibility_bdd(term_masks: list[int]) -> tuple[ROBDD, int]:
    """Construct Feas(P,R,D) without enumerating T3."""
    manager = ROBDD()
    lay = layout(len(term_masks))

    clauses: list[int] = []

    # Valid complete T2/T1 support codes: exactly the nonzero bit patterns.
    clauses.append(manager.disjunction(*(manager.var(v) for v in lay.p)))
    clauses.append(manager.disjunction(*(manager.var(v) for v in lay.r)))

    # Row projection: T3 -> T2 on (m,x).
    for row in range(4):
        rhs = manager.disjunction(
            manager.var(lay.q[2 * row]),
            manager.var(lay.q[2 * row + 1]),
        )
        clauses.append(eq(manager, manager.var(lay.p[row]), rhs))

    # Column projection: T3 -> T1 on y.
    for col in range(2):
        rhs = manager.disjunction(
            *(manager.var(lay.q[2 * row + col]) for row in range(4))
        )
        clauses.append(eq(manager, manager.var(lay.r[col]), rhs))

    # Declared data truth bits.
    for i, mask in enumerate(term_masks):
        delta = atomic_eq0_on_q(manager, lay.q, mask)
        clauses.append(eq(manager, manager.var(lay.d[i]), delta))

    relation = manager.conjunction(*clauses)
    projected = manager.exists(relation, set(lay.q))
    return manager, projected


def feature_signature(type_support: int, term_masks: list[int]) -> tuple[bool, ...]:
    """(T2 support, y T1 support, Delta truth pattern) for one T3 type."""
    p = tuple(
        bool(type_support & ((1 << (2 * row)) | (1 << (2 * row + 1))))
        for row in range(4)
    )
    r = tuple(
        bool(type_support & sum(1 << (2 * row + col) for row in range(4)))
        for col in range(2)
    )
    d = tuple(not bool(type_support & mask) for mask in term_masks)
    return p + r + d


def realized_signature_count(term_masks: list[int]) -> int:
    return len(
        {
            feature_signature(type_support, term_masks)
            for type_support in range(1, 256)
        }
    )


def run_samples(seed: int = 123, max_delta: int = 6, samples: int = 100) -> None:
    rng = random.Random(seed)
    print("ABA ocLTL support-feasibility ROBDD benchmark")
    print("seed=", seed)
    print(
        "d | outer patterns | median realized | median BDD nodes | min..max BDD"
    )
    print("--+----------------+-----------------+------------------+------------")

    for d in range(max_delta + 1):
        bdd_sizes: list[int] = []
        realized: list[int] = []

        for _ in range(samples):
            # Nonzero masks avoid a syntactically trivial constant-0 term.
            masks = [rng.randrange(1, 256) for _ in range(d)]
            manager, root = build_feasibility_bdd(masks)
            bdd_sizes.append(manager.reachable_nonterminals(root))
            realized.append(realized_signature_count(masks))

        outer = 45 * (1 << d)
        print(
            f"{d:1d} | {outer:14d} | "
            f"{statistics.median(realized):15.1f} | "
            f"{statistics.median(bdd_sizes):16.1f} | "
            f"{min(bdd_sizes):3d}..{max(bdd_sizes):3d}"
        )


def self_test() -> None:
    # No data predicates: every T2 x T1 projection pair is feasible.
    manager, root = build_feasibility_bdd([])
    assert manager.reachable_nonterminals(root) == 6
    assert realized_signature_count([]) == 45

    # A singleton minterm test has both outcomes somewhere in T3.
    assert realized_signature_count([1]) > 45

    # Whatever Delta is, at most 255 distinct outer signatures can be
    # witnessed because there are only 255 complete T3 supports.
    rng = random.Random(7)
    for d in range(1, 7):
        masks = [rng.randrange(1, 256) for _ in range(d)]
        assert realized_signature_count(masks) <= 255


def main() -> None:
    self_test()
    run_samples()


if __name__ == "__main__":
    main()

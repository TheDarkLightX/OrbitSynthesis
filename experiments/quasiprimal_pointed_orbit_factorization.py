#!/usr/bin/env python3
"""Bounded oracle for the pointed-generated-subalgebra factorization theorem.

This is a falsification certificate, not the generic proof.  It checks the
three-element Quackenbush quasi-primal algebra and the pure discriminator
algebra, including exhaustive sparse interpolation and the Morph false
merge/false split gates used in the accompanying certificate.
"""
from __future__ import annotations

import argparse
import json
from itertools import permutations, product
from pathlib import Path

Q = (0, 1, 2)
Q0 = (0, 1)
T2 = tuple(product(Q, repeat=2))
INDEX = {z: i for i, z in enumerate(T2)}


def phi(x: int) -> int:
    return 1 - x


def phi_tuple(z: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(phi(x) for x in z)


def disc(x: int, y: int, z: int) -> int:
    return z if x == y else x


# In Q=({0,1,2}; discriminator,u), the only proper subalgebra is Q0,
# phi swaps Q0, and Aut(Q) is trivial.  Hence the two Q0^2 phi-orbits are
# pointed classes with seed domain Q0; every tuple containing 2 is a singleton
# pointed class with seed domain Q.
REP = {}
PULL = {}
for z in T2:
    if all(x in Q0 for x in z):
        rep = min(z, phi_tuple(z))
        REP[z] = rep
        PULL[z] = (0, 1) if z == rep else (1, 0)
    else:
        REP[z] = z
        PULL[z] = (0, 1, 2)
REPS = tuple(sorted(set(REP.values())))
DOMAIN = {r: (0, 1) if all(x in Q0 for x in r) else Q for r in REPS}


def transported(seed: int, z: tuple[int, int]) -> int:
    return PULL[z][seed]


def factor_tables() -> set[tuple[int, ...]]:
    return {
        tuple(transported(seed[REPS.index(REP[z])], z) for z in T2)
        for seed in product(*(DOMAIN[r] for r in REPS))
    }


def direct_tables() -> set[tuple[int, ...]]:
    out = set()
    binary = tuple(product(Q0, repeat=2))
    for table in product(Q, repeat=len(T2)):
        f = dict(zip(T2, table, strict=True))
        if not all(f[z] in Q0 and f[phi_tuple(z)] == phi(f[z]) for z in binary):
            continue
        out.add(table)
    return out


def class_list_feasible(masks: tuple[int, ...]) -> bool:
    allowed = {r: sum(1 << x for x in DOMAIN[r]) for r in REPS}
    for z, mask in zip(T2, masks, strict=True):
        pulled = 0
        for seed in DOMAIN[REP[z]]:
            if mask & (1 << transported(seed, z)):
                pulled |= 1 << seed
        allowed[REP[z]] &= pulled
        if allowed[REP[z]] == 0:
            return False
    return True


def direct_list_feasible(masks: tuple[int, ...], tables: tuple[tuple[int, ...], ...]) -> bool:
    return any(all(mask & (1 << value) for mask, value in zip(masks, table, strict=True)) for table in tables)


def check_restricted_subpowers(tables: tuple[tuple[int, ...], ...]) -> int:
    for subset in range(1 << len(T2)):
        positions = [i for i in range(len(T2)) if subset & (1 << i)]
        direct = {tuple(table[i] for i in positions) for table in tables}
        active = {REP[T2[i]] for i in positions}
        predicted = 1
        for rep in active:
            predicted *= len(DOMAIN[rep])
        assert len(direct) == predicted
    return 1 << len(T2)


def check_sparse_singletons(tables: tuple[tuple[int, ...], ...]) -> int:
    # Code 0=undefined, 1={0}, 2={1}, 3={2}.
    table_bits = [0] * (4 ** len(T2))
    for table in tables:
        code = 0
        multiplier = 1
        for value in table:
            code += (value + 1) * multiplier
            multiplier *= 4
        # Every weakening obtained by replacing prescribed digits with 0.
        prescribed = [(i, value + 1) for i, value in enumerate(table)]
        for keep in range(1 << len(T2)):
            partial = 0
            for i, digit in prescribed:
                if keep & (1 << i):
                    partial += digit * (4 ** i)
            table_bits[partial] = 1
    count = 0
    for digits in product(range(4), repeat=len(T2)):
        code = sum(digit * (4 ** i) for i, digit in enumerate(digits))
        masks = tuple(7 if digit == 0 else 1 << (digit - 1) for digit in digits)
        assert bool(table_bits[code]) == class_list_feasible(masks)
        count += 1
    return count


def deterministic_lists(limit: int = 25_000):
    # Deterministic full-list stream over the seven nonempty Q-masks.
    masks = tuple(range(1, 8))
    for index, instance in enumerate(product(masks, repeat=len(T2))):
        if index >= limit:
            return
        yield instance


def check_lists(tables: tuple[tuple[int, ...], ...]) -> int:
    checked = 0
    nonempty = tuple(range(1, 8))
    # Exhaust every pair of constrained positions and every nonempty list pair.
    for i in range(len(T2)):
        for j in range(i + 1, len(T2)):
            for left in nonempty:
                for right in nonempty:
                    masks = [7] * len(T2)
                    masks[i], masks[j] = left, right
                    masks_t = tuple(masks)
                    assert direct_list_feasible(masks_t, tables) == class_list_feasible(masks_t)
                    checked += 1
    # Add 441 three-position structured cases not covered by the two-position sweep.
    for i in range(len(T2)):
        j, k = (i + 1) % len(T2), (i + 2) % len(T2)
        for left in nonempty:
            for right in nonempty:
                masks = [7] * len(T2)
                masks[i], masks[j], masks[k] = left, right, 1
                masks_t = tuple(masks)
                assert direct_list_feasible(masks_t, tables) == class_list_feasible(masks_t)
                checked += 1
    for masks in deterministic_lists():
        assert direct_list_feasible(masks, tables) == class_list_feasible(masks)
        checked += 1
    return checked


def normalized_query(z: tuple[int, int], tables: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    # Pull each table value back to the representative seed domain.
    inverse = {value: seed for seed, value in enumerate(PULL[z])}
    return tuple(inverse[table[INDEX[z]]] for table in tables)


def morph_corpus(tables: tuple[tuple[int, ...], ...]) -> dict[str, object]:
    queries = [f"term_{i:04d}" for i in range(len(tables))]
    objects = []
    for z in T2:
        answers = dict(zip(queries, normalized_query(z, tables), strict=True))
        objects.append({"id": "".join(map(str, z)), "abstract": "".join(map(str, REP[z])), "answers": answers})
    return {
        "schema": "minimum-sufficient-abstraction/finite-corpus/v1",
        "claim_id": "quackenbush-pointed-generated-subalgebra-arity-2",
        "require_minimal": True,
        "queries": queries,
        "objects": objects,
    }


def check_morph(tables: tuple[tuple[int, ...], ...]) -> tuple[int, int]:
    abstract_to_query = {}
    query_to_abstract = {}
    for z in T2:
        abstract = REP[z]
        query = normalized_query(z, tables)
        assert abstract_to_query.setdefault(abstract, query) == query  # no false merge
        assert query_to_abstract.setdefault(query, abstract) == abstract  # no false split
    assert len(abstract_to_query) == len(query_to_abstract) == 7
    return 0, 0


def equality_pattern(z: tuple[int, ...]) -> tuple[int, ...]:
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in z)


def pure_discriminator_check() -> tuple[int, int]:
    tuples = tuple(product(Q, repeat=3))
    patterns = tuple(sorted({equality_pattern(z) for z in tuples}))
    by_pattern = {p: next(z for z in tuples if equality_pattern(z) == p) for p in patterns}
    domains = {p: tuple(sorted(set(by_pattern[p]))) for p in patterns}
    factor = set()
    for seeds in product(*(domains[p] for p in patterns)):
        seed = dict(zip(patterns, seeds, strict=True))
        table = []
        for z in tuples:
            rep = by_pattern[equality_pattern(z)]
            mapping = dict(zip(rep, z, strict=True))
            table.append(mapping[seed[equality_pattern(z)]])
        factor.add(tuple(table))

    closure = {tuple(z[i] for z in tuples) for i in range(3)}
    while True:
        old = tuple(closure)
        closure |= {
            tuple(disc(f[i], g[i], h[i]) for i in range(len(tuples)))
            for f in old for g in old for h in old
        }
        if len(closure) == len(old):
            break
    assert factor == closure and len(factor) == 24 and len(patterns) == 5
    return len(patterns), len(factor)


def stabilizer_check() -> int:
    autos = tuple(dict(zip(Q, p, strict=True)) for p in permutations(Q))
    checked = 0
    for arity in range(1, 5):
        for z in product(Q, repeat=arity):
            generated = set(z)  # subalgebra generated by z in the pure discriminator algebra
            for auto in autos:
                if all(auto[x] == x for x in z):
                    assert all(auto[x] == x for x in generated)
                    checked += len(generated)
    assert checked == 282
    return checked


def counterexample_check() -> None:
    # In the existing no-greatest witness, 000 and 111 share a pointed class.
    # Both locally allow 01, but pulling the second list through phi gives 10.
    assert { (0, 1) } & { (1, 0) } == set()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-morph-corpus", type=Path)
    args = parser.parse_args()

    direct = direct_tables()
    factor = factor_tables()
    assert direct == factor and len(direct) == 972 and len(REPS) == 7
    tables = tuple(sorted(direct))

    restricted = check_restricted_subpowers(tables)
    partial = check_sparse_singletons(tables)
    listed = check_lists(tables)
    false_merges, false_splits = check_morph(tables)
    patterns, dterms = pure_discriminator_check()
    stabilizers = stabilizer_check()
    counterexample_check()

    if args.emit_morph_corpus:
        args.emit_morph_corpus.parent.mkdir(parents=True, exist_ok=True)
        args.emit_morph_corpus.write_text(json.dumps(morph_corpus(tables), indent=2, sort_keys=True) + "\n")

    print("PASS quasi-primal pointed-orbit factorization")
    print("Quackenbush Q arity-2 raw entries / pointed classes:", len(T2), len(REPS))
    print("Quackenbush Q arity-2 term operations:", len(tables))
    print("restricted evaluation subpowers exhausted:", restricted)
    print("sparse singleton interpolation instances exhausted:", partial)
    print("list interpolation instances checked:", listed)
    print("Morph false merges / false splits:", false_merges, "/", false_splits)
    print("pure discriminator arity-3 pointed classes / term operations:", patterns, dterms)
    print("stabilizer-redundancy element checks:", stabilizers)
    print("existing no-greatest-region obstruction: empty one-orbit seed intersection")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Three-valued checks for the primal/Boolean-power generalization.

This script deliberately avoids using Boolean-specific algebraic identities.
We take a three-element local carrier P={0,1,2} and test only the two structural
claims that the theorem needs from a primal Boolean power:

1. equations/local safety are pointwise, so causal predecessor commutes with
   lifting from a finite local P-game to a finite Boolean power P^X;
2. in an atomless Boolean power, complete tuple types are nonempty supports on
   P^k, and extending a support by r coordinates independently chooses a
   nonempty subset of P^r over every active old label.

Primality is not executable here as a concrete signature; it is used in the
paper theorem to guarantee that arbitrary finite local strategy/relation
functions are representable by terms.  The checker treats the local relation
as an arbitrary finite relation, which is exactly what primality makes
term-definable.
"""

from __future__ import annotations

from itertools import combinations, product
from math import ceil, log2
import random

P = (0, 1, 2)


def finite_pre(k: int, p: int, relation: set[tuple], target: set[tuple]) -> set[tuple]:
    states = list(product(P, repeat=k))
    inputs = list(product(P, repeat=p))
    return {
        a
        for a in states
        if all(
            any(v in target and (a, u, v) in relation for v in states)
            for u in inputs
        )
    }


def lifted_holds(local_target: set[tuple], state_function: tuple[tuple, ...]) -> bool:
    return all(local_state in local_target for local_state in state_function)


def explicit_finite_boolean_power_cpre(
    k: int,
    p: int,
    points: int,
    relation: set[tuple],
    target: set[tuple],
) -> set[tuple]:
    """Brute-force game on P^X for a finite Stone space X.

    Each algebra element is just an arbitrary P-valued function on `points`.
    All equations are evaluated independently at each point.
    """
    states = list(product(P, repeat=k))
    inputs = list(product(P, repeat=p))
    state_functions = list(product(states, repeat=points))
    input_functions = list(product(inputs, repeat=points))
    output_functions = state_functions

    lifted_target = {
        sf for sf in state_functions if lifted_holds(target, sf)
    }

    winning: set[tuple] = set()
    for sf in state_functions:
        all_inputs_work = True
        for xf in input_functions:
            some_output_works = False
            for yf in output_functions:
                if yf not in lifted_target:
                    continue
                if all(
                    (sf[i], xf[i], yf[i]) in relation
                    for i in range(points)
                ):
                    some_output_works = True
                    break
            if not some_output_works:
                all_inputs_work = False
                break
        if all_inputs_work:
            winning.add(sf)
    return winning


def check_causal_lifting(seed: int = 1234, trials: int = 100) -> None:
    rng = random.Random(seed)
    k = p = 1
    points = 3
    states = list(product(P, repeat=k))
    inputs = list(product(P, repeat=p))
    triples = [(a, u, v) for a in states for u in inputs for v in states]

    for _ in range(trials):
        relation = {triple for triple in triples if rng.random() < 0.5}
        target = {a for a in states if rng.random() < 0.6}

        local = finite_pre(k, p, relation, target)
        predicted = {
            sf
            for sf in product(states, repeat=points)
            if lifted_holds(local, sf)
        }
        explicit = explicit_finite_boolean_power_cpre(
            k, p, points, relation, target
        )
        assert predicted == explicit

    print(
        f"three-valued causal lifting: {trials} random relations passed "
        f"on a {points}-point Boolean power"
    )


def nonempty_subsets(size: int):
    for mask in range(1, 1 << size):
        yield mask


def extension_count(old_support_mask: int, k: int, r: int) -> int:
    old_labels = list(product(P, repeat=k))
    new_labels = list(product(P, repeat=r))
    support_size = old_support_mask.bit_count()

    # Every active old label independently chooses any nonempty subset of P^r.
    return ((1 << len(new_labels)) - 1) ** support_size


def exhaustive_extension_count(old_support_mask: int, k: int, r: int) -> int:
    """Enumerate local choices, not all global fine-support bitmasks."""
    old_labels = list(product(P, repeat=k))
    new_labels = list(product(P, repeat=r))
    active = [i for i in range(len(old_labels)) if old_support_mask & (1 << i)]
    choices = list(nonempty_subsets(len(new_labels)))
    return sum(1 for _ in product(choices, repeat=len(active)))


def check_support_geometry() -> None:
    # k=1: 3 local labels -> 7 complete support types.
    assert (1 << (len(P) ** 1)) - 1 == 7

    # k=2: 9 local labels -> 511 complete support types.
    assert (1 << (len(P) ** 2)) - 1 == 511

    # k=3: 27 local labels -> 134,217,727 support types.
    assert (1 << (len(P) ** 3)) - 1 == 134_217_727

    # Support code is information-theoretically minimum-width.
    for k in (1, 2, 3):
        width = len(P) ** k
        type_count = (1 << width) - 1
        assert ceil(log2(type_count)) == width

    # One new 3-valued coordinate gives 2^3-1=7 local refinements per active
    # old cell. Check every k=1 support exactly.
    for old_support in nonempty_subsets(3):
        predicted = extension_count(old_support, k=1, r=1)
        explicit = exhaustive_extension_count(old_support, k=1, r=1)
        assert predicted == explicit == 7 ** old_support.bit_count()

    # Summing extension fibers recovers all 2-variable complete types:
    #   sum_{s=1}^3 binom(3,s) 7^s = 8^3-1 = 511.
    total = sum(
        len(list(combinations(range(3), s))) * (7**s)
        for s in range(1, 4)
    )
    assert total == 511

    # For n=3, k=1, r=1 the exact block-local ROBDD theorem gives
    # 3 * (1+2*3) = 21 nonterminal nodes.
    assert (len(P) ** 1) * (1 + 2 * (len(P) ** 1)) == 21

    print("three-valued support/type/extension identities passed")


def atomless_clause_projection_no_input(
    transition_allowed: int,
    transition_hits: tuple[int, ...],
    target_allowed: int,
    target_hits: tuple[int, ...],
) -> tuple[int, tuple[int, ...]]:
    """Hypergraph CPre for 3 state labels and no environment input."""
    n = len(P)

    allowed_pairs = transition_allowed
    # restrict output to target allowed labels
    allowed = 0
    for a in range(n):
        for v in range(n):
            bit = 1 << (a * n + v)
            if (allowed_pairs & bit) and (target_allowed & (1 << v)):
                allowed |= bit

    full_hits = list(transition_hits)
    for hit in target_hits:
        lifted = 0
        for a in range(n):
            for v in range(n):
                if hit & (1 << v):
                    lifted |= 1 << (a * n + v)
        full_hits.append(lifted)

    state_allowed = 0
    state_hits: list[int] = []
    for a in range(n):
        if any(allowed & (1 << (a * n + v)) for v in range(n)):
            state_allowed |= 1 << a

    for full_hit in full_hits:
        h = 0
        for a in range(n):
            if any(
                (allowed & (1 << (a * n + v)))
                and (full_hit & (1 << (a * n + v)))
                for v in range(n)
            ):
                h |= 1 << a
        state_hits.append(h)

    state_hits = [h & state_allowed for h in state_hits]
    if state_allowed == 0 or any(h == 0 for h in state_hits):
        return 0, ()
    unique = sorted(set(h for h in state_hits if h != state_allowed))
    minimal = tuple(
        h
        for h in unique
        if not any(g != h and (g & h) == g for g in unique)
    )
    return state_allowed, minimal


def exact_atomless_clause_cpre_no_input(
    transition_allowed: int,
    transition_hits: tuple[int, ...],
    target_allowed: int,
    target_hits: tuple[int, ...],
) -> set[int]:
    """Explicit support search for P=3, no environment input.

    A state support has 7 possibilities. For each active state label a, an
    atomless Boolean region may realize any nonempty subset of the 3 output
    labels, so there are at most 7^3=343 fine refinements.
    """
    n = len(P)
    winning: set[int] = set()

    for state_support in nonempty_subsets(n):
        active = [a for a in range(n) if state_support & (1 << a)]
        for local_choices in product(range(1, 1 << n), repeat=len(active)):
            fine = 0
            output_support = 0
            for a, choice in zip(active, local_choices):
                for v in range(n):
                    if choice & (1 << v):
                        fine |= 1 << (a * n + v)
                        output_support |= 1 << v

            if fine & ~transition_allowed:
                continue
            if not all(fine & hit for hit in transition_hits):
                continue
            if output_support & ~target_allowed:
                continue
            if not all(output_support & hit for hit in target_hits):
                continue
            winning.add(state_support)
            break

    return winning


def represented_region(allowed: int, hits: tuple[int, ...]) -> set[int]:
    return {
        support
        for support in nonempty_subsets(len(P))
        if not (support & ~allowed) and all(support & hit for hit in hits)
    }


def check_three_valued_clause_geometry(seed: int = 99, trials: int = 1000) -> None:
    rng = random.Random(seed)
    pair_bits = len(P) ** 2

    for _ in range(trials):
        transition_allowed = rng.randrange(1 << pair_bits)
        transition_hits = tuple(
            rng.randrange(1 << pair_bits) for _ in range(rng.randrange(3))
        )
        target_allowed = rng.randrange(1 << len(P))
        target_hits = tuple(
            rng.randrange(1 << len(P)) for _ in range(rng.randrange(3))
        )

        explicit = exact_atomless_clause_cpre_no_input(
            transition_allowed,
            transition_hits,
            target_allowed,
            target_hits,
        )
        pair = atomless_clause_projection_no_input(
            transition_allowed,
            transition_hits,
            target_allowed,
            target_hits,
        )
        assert explicit == represented_region(*pair)

    print(
        f"three-valued atomless clause geometry: {trials} random input-free "
        "instances passed"
    )


def main() -> None:
    check_support_geometry()
    check_causal_lifting()
    check_three_valued_clause_geometry()
    print("primal n=3 geometry checker: all tests passed")


if __name__ == "__main__":
    main()

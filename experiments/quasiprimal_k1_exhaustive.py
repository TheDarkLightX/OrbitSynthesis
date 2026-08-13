#!/usr/bin/env python3
"""Exact k=1,m=1 calibration for the Quackenbush quasi-primal algebra.

This is a finite checker for QUASIPRIMAL_OBSTRUCTION_MINIMALITY.md.
It is not the proof of arbitrary-input k=1 union closure.

Algebra:
    Q={0,1,2}, proper nontrivial subalgebra B={0,1},
    phi swaps 0 and 1, Aut(Q) trivial.

For arity-two controller tables f(state,input), the quasi-primal
term-function characterization gives exactly 972 term functions.

For a single safety equation p=g on transition triples
(state,input,next), whether p=g is phi-invariant on B^3 and arbitrary
outside B^3. Hence the full equation-safety family has 23 independent
safe/unsafe bits.

Rather than iterate all 2^23 safety masks, for each candidate state
domain W we compute inclusion-minimal safe-bit requirement masks of
term controllers that keep W invariant. Any no-common-superset witness
would persist after shrinking its safety mask to the union of the two
witness-controller requirement masks. This makes the pair search exact.
"""

from __future__ import annotations

from itertools import product

Q = (0, 1, 2)
B = (0, 1)


def phi(x: int) -> int:
    assert x in B
    return 1 - x


def phi_tuple(z: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(phi(x) for x in z)


def term_controllers() -> tuple[tuple[int, ...], ...]:
    observations = tuple(product(Q, repeat=2))
    binary = tuple(product(B, repeat=2))

    reps: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for z in binary:
        if z in seen:
            continue
        zp = phi_tuple(z)
        reps.append(z)
        seen.add(z)
        seen.add(zp)

    outside = tuple(z for z in observations if z not in set(binary))
    tables: list[tuple[int, ...]] = []

    for rep_values in product(B, repeat=len(reps)):
        base: dict[tuple[int, int], int] = {}
        for z, value in zip(reps, rep_values):
            zp = phi_tuple(z)
            base[z] = value
            base[zp] = phi(value)

        for outside_values in product(Q, repeat=len(outside)):
            table = dict(base)
            table.update(zip(outside, outside_values))
            tables.append(tuple(table[z] for z in observations))

    assert len(tables) == 972
    return tuple(tables)


def transition_feature_map() -> tuple[dict[tuple[int, int, int], int], int]:
    """Return the 23 independent equality-status bits for p=g."""

    feature: dict[tuple[int, int, int], int] = {}
    seen: set[tuple[int, int, int]] = set()
    index = 0

    for t in product(B, repeat=3):
        if t in seen:
            continue
        tp = phi_tuple(t)
        feature[t] = index
        feature[tp] = index
        seen.add(t)
        seen.add(tp)
        index += 1

    for t in product(Q, repeat=3):
        if t not in feature:
            feature[t] = index
            index += 1

    assert index == 23
    return feature, index


def domain(mask: int) -> frozenset[int]:
    return frozenset(a for a in Q if (mask >> a) & 1)


def minimal_requirement_masks(
    wmask: int,
    controllers: tuple[tuple[int, ...], ...],
    feature: dict[tuple[int, int, int], int],
) -> tuple[int, ...]:
    observations = tuple(product(Q, repeat=2))
    obs_index = {z: i for i, z in enumerate(observations)}
    W = domain(wmask)

    requirements: list[int] = []
    for controller in controllers:
        required = 0
        closed = True
        for state in W:
            for inp in Q:
                nxt = controller[obs_index[(state, inp)]]
                if nxt not in W:
                    closed = False
                    break
                required |= 1 << feature[(state, inp, nxt)]
            if not closed:
                break
        if closed:
            requirements.append(required)

    requirements = sorted(set(requirements), key=lambda b: (b.bit_count(), b))
    minimal: list[int] = []
    for bits in requirements:
        if not any((old & bits) == old for old in minimal):
            minimal.append(bits)
    return tuple(minimal)


def feasible(requirements: tuple[int, ...], safe_bits: int) -> bool:
    return any((req & safe_bits) == req for req in requirements)


def main() -> None:
    controllers = term_controllers()
    feature, feature_count = transition_feature_map()

    requirements = {
        wmask: minimal_requirement_masks(wmask, controllers, feature)
        for wmask in range(1, 1 << len(Q))
    }

    expected_counts = {
        0b001: 1,
        0b010: 1,
        0b011: 16,
        0b100: 1,
        0b101: 16,
        0b110: 16,
        0b111: 972,
    }
    assert {w: len(req) for w, req in requirements.items()} == expected_counts

    checked = 0
    for left in range(1, 8):
        for right in range(left + 1, 8):
            # Only incomparable domains can witness failure of greatestness.
            if (left & right) == left or (left & right) == right:
                continue

            union = left | right
            for left_req in requirements[left]:
                for right_req in requirements[right]:
                    checked += 1
                    safe_bits = left_req | right_req

                    common_superset = False
                    for candidate in range(1, 8):
                        if (candidate & union) != union:
                            continue
                        if feasible(requirements[candidate], safe_bits):
                            common_superset = True
                            break

                    if not common_superset:
                        raise AssertionError(
                            "found k=1 no-common-superset witness: "
                            f"left={domain(left)}, right={domain(right)}, "
                            f"safe_bits={safe_bits:#x}"
                        )

    print("PASS: exact k=1,m=1 Quackenbush calibration")
    print(f"term controllers: {len(controllers)}")
    print(f"independent single-equation safety bits: {feature_count}")
    print(f"minimal pair-mask combinations checked: {checked}")
    print("no two term-winning domains lack a common term-winning superset")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bounded exact checker for notes/ABA_CLAUSE_SAFETY_HYPERGRAPH.md.

The explicit game has one state BA variable s, one environment BA variable x,
and one controller/next-state BA variable y.  Complete types are nonempty
supports on the corresponding Boolean Venn cells:

    s       : 2 cells,   3 supports
    (s,x)   : 4 cells,  15 supports
    (s,x,y) : 8 cells, 255 supports

A transition clause is represented by:

    Q subseteq L
    Q intersects G_j for every transition hit set G_j.

A target state region is represented by:

    Y subseteq A
    Y intersects H_t for every target hit set H_t.

For random instances, compare explicit forall-input-type / exists-output-type
enumeration against the closed-form hypergraph predecessor transform.
"""

from __future__ import annotations

from itertools import product
import random


def extensions(base_support: int, base_dims: int, extra_dims: int):
    n_base_cells = 1 << base_dims
    refinements = 1 << extra_dims
    active = [a for a in range(n_base_cells) if base_support & (1 << a)]

    for local_masks in product(range(1, 1 << refinements), repeat=len(active)):
        fine = 0
        for a, local in zip(active, local_masks):
            for extra in range(refinements):
                if local & (1 << extra):
                    fine |= 1 << (a | (extra << base_dims))
        yield fine


def projection(mask: int, total_dims: int, keep_positions: list[int]) -> int:
    out = 0
    for cell in range(1 << total_dims):
        if not (mask & (1 << cell)):
            continue
        projected = 0
        for j, pos in enumerate(keep_positions):
            if cell & (1 << pos):
                projected |= 1 << j
        out |= 1 << projected
    return out


def region_holds(support: int, allowed: int, hits: tuple[int, ...]) -> bool:
    return (
        support != 0
        and not (support & ~allowed)
        and all(support & hit for hit in hits)
    )


def explicit_cpre(
    transition_allowed: int,
    transition_hits: tuple[int, ...],
    target_allowed: int,
    target_hits: tuple[int, ...],
) -> set[int]:
    """Exact support-game CPre by enumeration."""
    winning: set[int] = set()

    for state_support in range(1, 4):
        all_input_types_work = True

        for sx_support in extensions(state_support, base_dims=1, extra_dims=1):
            some_output_type_works = False

            for sxy_support in extensions(sx_support, base_dims=2, extra_dims=1):
                if sxy_support & ~transition_allowed:
                    continue
                if not all(sxy_support & hit for hit in transition_hits):
                    continue

                y_support = projection(
                    sxy_support, total_dims=3, keep_positions=[2]
                )
                if region_holds(y_support, target_allowed, target_hits):
                    some_output_type_works = True
                    break

            if not some_output_type_works:
                all_input_types_work = False
                break

        if all_input_types_work:
            winning.add(state_support)

    return winning


def preimage_y(y_mask: int) -> int:
    full = 0
    for cell in range(8):
        y = (cell >> 2) & 1
        if y_mask & (1 << y):
            full |= 1 << cell
    return full


def exists_y(full_mask: int) -> int:
    """Project an s,x,y cell set to an s,x cell set."""
    out = 0
    for sx in range(4):
        if any(full_mask & (1 << (sx | (y << 2))) for y in range(2)):
            out |= 1 << sx
    return out


def forall_x(sx_mask: int) -> int:
    """State labels whose entire two-point input fiber lies in sx_mask."""
    out = 0
    for state in range(2):
        if all(sx_mask & (1 << (state | (x << 1))) for x in range(2)):
            out |= 1 << state
    return out


def canonicalize(allowed: int, hits: list[int]) -> tuple[int, tuple[int, ...]]:
    hits = [hit & allowed for hit in hits]
    if allowed == 0 or any(hit == 0 for hit in hits):
        return 0, ()

    unique = sorted(set(hits))
    minimal: list[int] = []
    for hit in unique:
        if any(other != hit and (other & hit) == other for other in unique):
            continue
        minimal.append(hit)
    return allowed, tuple(minimal)


def hypergraph_cpre(
    transition_allowed: int,
    transition_hits: tuple[int, ...],
    target_allowed: int,
    target_hits: tuple[int, ...],
) -> tuple[int, tuple[int, ...]]:
    """Closed-form predecessor from ABA_CLAUSE_SAFETY_HYPERGRAPH.md."""

    # 1. Target allowed cells restrict full transition cells.
    allowed_full = transition_allowed & preimage_y(target_allowed)

    # 2. Transition hits plus target hit requirements lifted to full cells.
    full_hits = list(transition_hits) + [preimage_y(h) for h in target_hits]

    # 3. Existential output projection.
    allowed_sx = exists_y(allowed_full)
    hit_sx = [exists_y(allowed_full & hit) for hit in full_hits]

    # 4. Universal input projection.
    allowed_state = forall_x(allowed_sx)
    hit_state = [forall_x(hit) for hit in hit_sx]

    return canonicalize(allowed_state, hit_state)


def represented_region(allowed: int, hits: tuple[int, ...]) -> set[int]:
    return {
        support
        for support in range(1, 4)
        if region_holds(support, allowed, hits)
    }


def verify_instance(
    transition_allowed: int,
    transition_hits: tuple[int, ...],
    target_allowed: int,
    target_hits: tuple[int, ...],
) -> None:
    explicit = explicit_cpre(
        transition_allowed,
        transition_hits,
        target_allowed,
        target_hits,
    )
    allowed, hits = hypergraph_cpre(
        transition_allowed,
        transition_hits,
        target_allowed,
        target_hits,
    )
    predicted = represented_region(allowed, hits)
    assert explicit == predicted, (
        transition_allowed,
        transition_hits,
        target_allowed,
        target_hits,
        explicit,
        (allowed, hits),
        predicted,
    )


def edge_cases() -> None:
    # No transition restriction and top target: every state wins.
    verify_instance(0xFF, (), 0b11, ())

    # No allowed transition cell: no state wins.
    verify_instance(0, (), 0b11, ())

    # Static one-inequation target s!=0 is not a principal ideal.
    # It is represented by allowed={0,1}, hit={1}.
    assert represented_region(0b11, (0b10,)) == {0b10, 0b11}

    # A target hit that is outside target_allowed makes the target empty.
    verify_instance(0xFF, (), 0b01, (0b10,))


def randomized_checks(seed: int = 314159, trials: int = 5000) -> None:
    rng = random.Random(seed)
    for _ in range(trials):
        transition_allowed = rng.randrange(256)
        transition_hits = tuple(
            rng.randrange(256) for _ in range(rng.randrange(3))
        )
        target_allowed = rng.randrange(4)
        target_hits = tuple(rng.randrange(4) for _ in range(rng.randrange(3)))
        verify_instance(
            transition_allowed,
            transition_hits,
            target_allowed,
            target_hits,
        )
    print(f"{trials} randomized exact hypergraph-CPre checks passed")


def main() -> None:
    edge_cases()
    randomized_checks()
    print("ABA clause safety hypergraph checker: all tests passed")


if __name__ == "__main__":
    main()

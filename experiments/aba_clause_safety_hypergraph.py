#!/usr/bin/env python3
"""Exact bounded checks for ABA clause safety hypergraph synthesis.

The explicit game has one state BA variable s, one environment BA variable x,
and one controller/next-state BA variable y. Complete types are nonempty
supports on 2, 4, and 8 Venn cells respectively.

We validate both one-step CPre and whole greatest-fixed-point trajectories
against the closed-form hypergraph recurrence.
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
    target_region: set[int],
) -> set[int]:
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
                y_support = projection(sxy_support, total_dims=3, keep_positions=[2])
                if y_support in target_region:
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
    out = 0
    for sx in range(4):
        if any(full_mask & (1 << (sx | (y << 2))) for y in range(2)):
            out |= 1 << sx
    return out


def forall_x(sx_mask: int) -> int:
    out = 0
    for state in range(2):
        if all(sx_mask & (1 << (state | (x << 1))) for x in range(2)):
            out |= 1 << state
    return out


def canonicalize(allowed: int, hits: list[int]) -> tuple[int, tuple[int, ...]]:
    """Canonical clause region over NONEMPTY supports.

    A hit equal to `allowed` is tautological: every valid complete ABA support
    is nonempty and already contained in `allowed`, so it necessarily hits the
    whole allowed set. This subtlety matters for fixed-point equality.
    """
    hits = [hit & allowed for hit in hits]
    if allowed == 0 or any(hit == 0 for hit in hits):
        return 0, ()

    unique = sorted(set(hit for hit in hits if hit != allowed))
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
    allowed_full = transition_allowed & preimage_y(target_allowed)
    full_hits = list(transition_hits) + [preimage_y(h) for h in target_hits]

    allowed_sx = exists_y(allowed_full)
    hit_sx = [exists_y(allowed_full & hit) for hit in full_hits]

    allowed_state = forall_x(allowed_sx)
    hit_state = [forall_x(hit) for hit in hit_sx]
    return canonicalize(allowed_state, hit_state)


def represented_region(allowed: int, hits: tuple[int, ...]) -> set[int]:
    return {
        support for support in range(1, 4)
        if region_holds(support, allowed, hits)
    }


def verify_one_step(
    transition_allowed: int,
    transition_hits: tuple[int, ...],
    target_allowed: int,
    target_hits: tuple[int, ...],
) -> None:
    target = represented_region(target_allowed, target_hits)
    explicit = explicit_cpre(transition_allowed, transition_hits, target)
    pair = hypergraph_cpre(
        transition_allowed, transition_hits, target_allowed, target_hits
    )
    predicted = represented_region(*pair)
    assert explicit == predicted, (
        transition_allowed, transition_hits, target_allowed, target_hits,
        explicit, pair, predicted,
    )


def explicit_fixed_point(
    transition_allowed: int, transition_hits: tuple[int, ...]
) -> list[set[int]]:
    region = {1, 2, 3}
    sequence = [region]
    while True:
        nxt = explicit_cpre(transition_allowed, transition_hits, region)
        sequence.append(nxt)
        if nxt == region:
            return sequence
        region = nxt


def hypergraph_fixed_point(
    transition_allowed: int, transition_hits: tuple[int, ...]
) -> list[tuple[int, tuple[int, ...]]]:
    pair: tuple[int, tuple[int, ...]] = (0b11, ())
    sequence = [pair]
    while True:
        nxt = hypergraph_cpre(
            transition_allowed, transition_hits, pair[0], pair[1]
        )
        sequence.append(nxt)
        if nxt == pair:
            return sequence
        pair = nxt


def verify_fixed_point(
    transition_allowed: int, transition_hits: tuple[int, ...]
) -> None:
    explicit = explicit_fixed_point(transition_allowed, transition_hits)
    symbolic = hypergraph_fixed_point(transition_allowed, transition_hits)
    assert len(explicit) == len(symbolic), (
        transition_allowed, transition_hits, explicit, symbolic
    )
    for e, pair in zip(explicit, symbolic):
        assert e == represented_region(*pair), (
            transition_allowed, transition_hits, explicit, symbolic
        )


def edge_cases() -> None:
    verify_one_step(0xFF, (), 0b11, ())
    verify_one_step(0, (), 0b11, ())

    # Static s!=0 region: allowed={0,1}, hit={1}; not a principal ideal.
    assert represented_region(0b11, (0b10,)) == {0b10, 0b11}

    # Hit==allowed is tautological on nonempty supports and MUST canonicalize away.
    assert canonicalize(0b11, [0b11]) == (0b11, ())

    # Hit outside target allowed makes the target empty after restriction.
    assert canonicalize(0b01, [0b10]) == (0, ())


def randomized_one_step(seed: int = 314159, trials: int = 5000) -> None:
    rng = random.Random(seed)
    for _ in range(trials):
        transition_allowed = rng.randrange(256)
        transition_hits = tuple(
            rng.randrange(256) for _ in range(rng.randrange(3))
        )
        target_allowed = rng.randrange(4)
        target_hits = tuple(rng.randrange(4) for _ in range(rng.randrange(3)))
        verify_one_step(
            transition_allowed, transition_hits, target_allowed, target_hits
        )
    print(f"{trials} randomized exact one-step checks passed")


def randomized_fixed_points(seed: int = 271828, trials: int = 2000) -> None:
    rng = random.Random(seed)
    max_steps = 0
    for _ in range(trials):
        transition_allowed = rng.randrange(256)
        transition_hits = tuple(
            rng.randrange(256) for _ in range(rng.randrange(3))
        )
        verify_fixed_point(transition_allowed, transition_hits)
        max_steps = max(
            max_steps,
            len(explicit_fixed_point(transition_allowed, transition_hits)) - 1,
        )
    print(
        f"{trials} randomized fixed-point trajectories passed; "
        f"max observed iterations={max_steps}"
    )


def main() -> None:
    edge_cases()
    randomized_one_step()
    randomized_fixed_points()
    print("ABA clause safety hypergraph checker: all tests passed")


if __name__ == "__main__":
    main()

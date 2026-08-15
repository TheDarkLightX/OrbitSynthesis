#!/usr/bin/env python3
"""Deterministic audit for two new OrbitSynthesis frontiers.

1. Quasi-primal generated-subpower intersection with arbitrary unary lists.
2. Demi-semi-primality as the greatest-region boundary for groupoid-invariant
   shared-term safety relations.

The generic theorems are proved in the paired notes.  This script is an exact
finite reconstruction with effective mutations, not a replacement for those
proofs.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.greatest_region_boundary import (
    audit_no_greatest_region_witness,
    build_no_greatest_region_witness,
)
from orbitsynthesis.safety import FiniteSafetyGame
from orbitsynthesis.subpower_lists import (
    quasi_primal_list_subpower_intersection,
    verify_list_subpower_witness,
)

Q = (0, 1, 2)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def qunary(x: int) -> int:
    return (1, 0, 1)[x]


def pure_discriminator() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {"d": (3, discriminator)},
    )


def quackenbush_q() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {
            "d": (3, discriminator),
            "u": (1, qunary),
        },
    )


def unary_expansion(table: tuple[int, int, int]) -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {
            "d": (3, discriminator),
            "u": (1, lambda value, table=table: table[value]),
        },
    )


def nonempty_lists() -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(value for index, value in enumerate(Q) if mask & (1 << index))
        for mask in range(1, 1 << len(Q))
    )


def generated_subpower(
    algebra: FiniteAlgebra,
    generators: tuple[tuple[int, ...], ...],
) -> frozenset[tuple[int, ...]]:
    generated = set(generators)
    width = len(generators[0])
    changed = True
    while changed:
        changed = False
        current = tuple(generated)
        for operation in algebra.operations:
            for arguments in itertools.product(current, repeat=operation.arity):
                output = tuple(
                    operation(*(argument[index] for argument in arguments))
                    for index in range(width)
                )
                if output not in generated:
                    generated.add(output)
                    changed = True
    return frozenset(generated)


def exact_list_calibration() -> dict[str, object]:
    list_family = nonempty_lists()
    rows = []
    total = 0

    for label, algebra in (
        ("pure-discriminator", pure_discriminator()),
        ("quackenbush-q", quackenbush_q()),
    ):
        isomorphisms = algebra.internal_isomorphisms()
        algebra_total = 0
        for generator_count, width in ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2)):
            local = 0
            for flat in itertools.product(
                algebra.values,
                repeat=generator_count * width,
            ):
                generators = tuple(
                    tuple(
                        flat[generator * width + index]
                        for index in range(width)
                    )
                    for generator in range(generator_count)
                )
                subpower = generated_subpower(algebra, generators)
                for coordinate_lists in itertools.product(
                    list_family,
                    repeat=width,
                ):
                    result = quasi_primal_list_subpower_intersection(
                        algebra,
                        generators,
                        coordinate_lists,
                        internal_isomorphisms=isomorphisms,
                    )
                    brute = next(
                        (
                            vector
                            for vector in subpower
                            if all(
                                vector[index] in coordinate_lists[index]
                                for index in range(width)
                            )
                        ),
                        None,
                    )
                    require(
                        result.feasible == (brute is not None),
                        "quasi-primal list solver disagrees with explicit subpower",
                    )
                    if result.feasible:
                        require(result.witness is not None, "missing witness")
                        require(
                            result.witness.evaluation_vector in subpower,
                            "returned vector is outside the generated subpower",
                        )
                        require(
                            verify_list_subpower_witness(
                                algebra,
                                generators,
                                coordinate_lists,
                                result.witness,
                                internal_isomorphisms=isomorphisms,
                            ),
                            "witness certificate did not replay",
                        )
                    local += 1
            rows.append(
                {
                    "algebra": label,
                    "generator_count": generator_count,
                    "coordinate_count": width,
                    "instances": local,
                }
            )
            algebra_total += local
            total += local
        require(algebra_total == 13755, "per-algebra exact count drift")

    # Effective mutation: local row-by-row feasibility would accept these two
    # lists, but the proper-subalgebra complement couples the two rows.
    algebra = quackenbush_q()
    mutation = quasi_primal_list_subpower_intersection(
        algebra,
        generators=((0, 1),),
        coordinate_lists=({0}, {0}),
    )
    require(not mutation.feasible, "groupoid-edge deletion mutation escaped")
    require(mutation.obstruction is not None, "mutation lacks obstruction")

    return {
        "exact_instances": total,
        "rows": rows,
        "mutation": {
            "generators": [[0, 1]],
            "lists": [[0], [0]],
            "local_only_verdict": True,
            "exact_verdict": mutation.feasible,
            "obstruction_positions": list(mutation.obstruction.positions),
            "candidate_rejections": [
                {
                    "candidate": rejection.candidate,
                    "violated_positions": list(rejection.violated_positions),
                    "structural_reason": rejection.structural_reason,
                }
                for rejection in mutation.obstruction.candidate_rejections
            ],
        },
    }


def greatest_region_calibration() -> dict[str, object]:
    pure = pure_discriminator()
    require(
        build_no_greatest_region_witness(pure) is None,
        "pure discriminator should satisfy the extension property",
    )

    classifications = []
    demi_count = 0
    non_demi_count = 0
    q_checkpoint = None
    for table in itertools.product(Q, repeat=3):
        algebra = unary_expansion(table)
        isomorphisms = algebra.internal_isomorphisms()
        witness = build_no_greatest_region_witness(
            algebra,
            internal_isomorphisms=isomorphisms,
        )
        if witness is None:
            demi_count += 1
            classifications.append([list(table), True])
            continue

        non_demi_count += 1
        audit = audit_no_greatest_region_witness(
            algebra,
            witness,
            internal_isomorphisms=isomorphisms,
        )
        require(audit.passes, "generic no-greatest witness failed")
        classifications.append([list(table), False])
        if table == (1, 0, 1):
            q_checkpoint = {
                "state_arity": witness.state_arity,
                "safe_transition_count": len(witness.safe_relation),
                "left_domain_size": len(witness.left_domain),
                "right_domain_size": len(witness.right_domain),
                "critical_orbit_size": len(witness.critical_observation_orbit),
                "source_dead_orbit_size": len(
                    witness.source_dead_observation_orbit
                ),
                "target_dead_orbit_size": len(
                    witness.target_dead_observation_orbit
                ),
                "audit": {
                    "left_feasible": audit.left_feasible,
                    "right_feasible": audit.right_feasible,
                    "union_feasible": audit.union_feasible,
                    "groupoid_invariant": audit.groupoid_invariant,
                },
            }

    require(demi_count == 15, "three-element demi count drift")
    require(non_demi_count == 12, "three-element non-demi count drift")
    require(q_checkpoint is not None, "missing Quackenbush-Q checkpoint")

    # Load-bearing mutation: revive the target-side dead observation.  Then the
    # two domains have a common winning upper bound obtained by adjoining the
    # target image of the left output.
    algebra = quackenbush_q()
    witness = build_no_greatest_region_witness(algebra)
    require(witness is not None, "missing Q witness")
    mutated_safe = set(witness.safe_relation)
    for observation in witness.target_dead_observation_orbit:
        state = observation[: witness.state_arity]
        input_value = (observation[witness.state_arity],)
        mutated_safe.add((state, input_value, state))
    mutated_game = FiniteSafetyGame(
        algebra,
        witness.state_arity,
        1,
        mutated_safe,
    )
    common_domain = (
        witness.left_domain
        | witness.right_domain
        | {witness.target_output_zero}
    )
    require(
        mutated_game.quasi_primal_domain_feasible(common_domain),
        "dead-state mutation did not restore a common upper bound",
    )

    return {
        "unary_expansions": len(classifications),
        "demi_semi_primal_count": demi_count,
        "non_demi_semi_primal_count": non_demi_count,
        "classifications": classifications,
        "quackenbush_q_checkpoint": q_checkpoint,
        "negative_control": {
            "algebra": "pure three-element discriminator",
            "extension_property": True,
            "witness_constructed": False,
        },
        "mutation": {
            "revived_target_dead_orbit_size": len(
                witness.target_dead_observation_orbit
            ),
            "common_domain_size": len(common_domain),
            "common_domain_feasible_after_mutation": True,
        },
    }


def randomized_list_calibration(seed: int = 0x515750, trials: int = 200) -> dict[str, int]:
    rng = random.Random(seed)
    checked = 0
    for algebra in (pure_discriminator(), quackenbush_q()):
        isomorphisms = algebra.internal_isomorphisms()
        lists = nonempty_lists()
        for _ in range(trials):
            generator_count = rng.choice((1, 2))
            width = rng.choice((2, 3))
            generators = tuple(
                tuple(rng.choice(Q) for _ in range(width))
                for _ in range(generator_count)
            )
            coordinate_lists = tuple(rng.choice(lists) for _ in range(width))
            result = quasi_primal_list_subpower_intersection(
                algebra,
                generators,
                coordinate_lists,
                internal_isomorphisms=isomorphisms,
            )
            subpower = generated_subpower(algebra, generators)
            brute = any(
                all(vector[index] in coordinate_lists[index] for index in range(width))
                for vector in subpower
            )
            require(result.feasible == brute, "randomized list mismatch")
            checked += 1
    return {"seed": seed, "instances": checked}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_receipt() -> dict[str, object]:
    source_paths = {
        "subpower_lists.py": ROOT / "src/orbitsynthesis/subpower_lists.py",
        "greatest_region_boundary.py":
            ROOT / "src/orbitsynthesis/greatest_region_boundary.py",
        "check_frontiers.py": Path(__file__).resolve(),
    }
    result = {
        "schema": "orbit-synthesis/greatest-region-list-subpower/v1",
        "claims": {
            "greatest_region_boundary":
                "demi-semi-primal iff universal greatest region for "
                "internal-groupoid-invariant safety relations",
            "quasi_primal_list_intersection":
                "polynomial-time component algorithm for fixed finite "
                "quasi-primal algebras",
        },
        "source_sha256": {
            label: sha256(path)
            for label, path in source_paths.items()
        },
        "list_subpower": exact_list_calibration(),
        "greatest_region": greatest_region_calibration(),
        "randomized_lists": randomized_list_calibration(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main() -> int:
    expected = None
    output = None
    arguments = iter(sys.argv[1:])
    for argument in arguments:
        if argument == "--expected":
            expected = Path(next(arguments))
        elif argument == "--out":
            output = Path(next(arguments))
        else:
            raise SystemExit(f"unknown argument: {argument}")

    result = make_receipt()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if expected is not None:
        require(
            result == json.loads(expected.read_text(encoding="utf-8")),
            "committed receipt drift",
        )
    if output is not None:
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Bounded calibration of a CNF-to-term-safety complexity reduction.

The target decision problem fixes the three-element Quackenbush algebra and
uses an explicitly tabulated safety relation.  Given required initial states,
it asks whether one original-signature term controller keeps some containing
domain safe and invariant.

The proposed reduction represents opposite literals by complement-paired
binary states and clauses by required nonbinary states.  This script checks
the reduction against brute-force SAT, the independent raw groupoid solver,
the pointed solver, a direct term-table verifier, and four negative controls.

The finite campaign calibrates a manuscript NP-completeness proof.  It is not
itself a generic complexity proof or a claim about succinct term syntax.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.finite_algebra import FiniteAlgebra, InternalIsomorphism
from orbitsynthesis.pointed_kernel import CompiledParameterizedKernel
from orbitsynthesis.safety import FiniteSafetyGame

Q = (0, 1, 2)
Q0 = frozenset((0, 1))
State = tuple[int, ...]
Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def require(condition: bool, message: str) -> None:
    """Fail closed even under ``python -O``."""
    if not condition:
        raise RuntimeError(message)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def unary_u(x: int) -> int:
    return {0: 1, 1: 0, 2: 1}[x]


def make_algebra() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {"d": (3, discriminator), "u": (1, unary_u)},
    )


def complement(values: tuple[int, ...]) -> tuple[int, ...]:
    require(all(value in Q0 for value in values), "complement left B={0,1}")
    return tuple(1 - value for value in values)


def binary_pairs(k: int) -> tuple[tuple[State, State], ...]:
    seen: set[State] = set()
    pairs: list[tuple[State, State]] = []
    for state in product((0, 1), repeat=k):
        if state in seen:
            continue
        other = complement(state)
        seen.add(state)
        seen.add(other)
        pairs.append((state, other))
    return tuple(pairs)


def normalize_cnf(num_variables: int, clauses: Iterable[Iterable[int]]) -> CNF:
    require(num_variables >= 1, "the reduction expects at least one variable")
    normalized: list[Clause] = []
    for clause in clauses:
        values = set(clause)
        require(
            all(1 <= abs(literal) <= num_variables for literal in values),
            "literal outside the declared variable range",
        )
        normalized.append(
            tuple(sorted(values, key=lambda literal: (abs(literal), literal < 0)))
        )
    return tuple(normalized)


def choose_state_arity(num_variables: int, clause_count: int) -> int:
    k = 3
    while (
        2 ** (k - 1) < num_variables + 2
        or 3**k - 2**k - 1 < clause_count
    ):
        k += 1
    return k


@dataclass(frozen=True)
class Reduction:
    game: FiniteSafetyGame
    num_variables: int
    clauses: CNF
    initial: frozenset[State]
    live: State
    dead: State
    neutral: tuple[State, State]
    variable_pairs: tuple[tuple[State, State], ...]
    literal_items: tuple[tuple[int, State], ...]
    clause_states: tuple[State, ...]

    @property
    def literal_states(self) -> dict[int, State]:
        return dict(self.literal_items)


def build_reduction(
    num_variables: int,
    clauses: Iterable[Iterable[int]],
    *,
    disable_dead_row: bool = False,
    asymmetric_first_critical_pair: bool = False,
) -> Reduction:
    cnf = normalize_cnf(num_variables, clauses)
    k = choose_state_arity(num_variables, len(cnf))
    algebra = make_algebra()
    states = tuple(product(Q, repeat=k))
    inputs = ((0,), (1,), (2,))
    pairs = binary_pairs(k)
    live, dead = pairs[0]
    neutral = pairs[1]
    variable_pairs = pairs[2 : 2 + num_variables]
    require(
        len(variable_pairs) == num_variables,
        "state arity did not provide enough literal pairs",
    )

    literal_states: dict[int, State] = {}
    for index, (positive, negative) in enumerate(variable_pairs, start=1):
        literal_states[index] = positive
        literal_states[-index] = negative

    # Excluding the sole constant nonbinary tuple guarantees that every
    # forbidden transition has a coordinate different from its first one.
    # This supports the explicit orbitwise coordinate-selector compiler.
    all_two = tuple(2 for _ in range(k))
    nonbinary = tuple(state for state in states if 2 in state and state != all_two)
    clause_states = nonbinary[: len(cnf)]
    require(
        len(clause_states) == len(cnf),
        "state arity did not provide enough clause states",
    )

    critical: dict[tuple[State, tuple[int, ...]], frozenset[State]] = {}
    anchor = frozenset((live, dead))
    for index, (positive, negative) in enumerate(variable_pairs):
        critical[(positive, (0,))] = anchor
        if not (asymmetric_first_critical_pair and index == 0):
            critical[(negative, (1,))] = anchor

    clause_outputs = {
        (clause_state, (2,)): frozenset(literal_states[lit] for lit in clause)
        for clause_state, clause in zip(clause_states, cnf, strict=True)
    }

    def safe(state: State, input_value: tuple[int, ...], output: State) -> bool:
        if not disable_dead_row and state == dead and input_value == (2,):
            return False
        required = critical.get((state, input_value))
        if required is not None:
            return output in required
        clause_allowed = clause_outputs.get((state, input_value))
        if clause_allowed is not None:
            return output in clause_allowed
        return True

    relation = {
        (state, input_value, output)
        for state in states
        for input_value in inputs
        for output in states
        if safe(state, input_value, output)
    }
    game = FiniteSafetyGame(algebra, k, 1, relation)
    initial = frozenset((live, *neutral, *clause_states))
    return Reduction(
        game=game,
        num_variables=num_variables,
        clauses=cnf,
        initial=initial,
        live=live,
        dead=dead,
        neutral=neutral,
        variable_pairs=variable_pairs,
        literal_items=tuple(sorted(literal_states.items())),
        clause_states=clause_states,
    )


def selected_literals(choices: tuple[int, ...]) -> frozenset[int]:
    return frozenset(
        index if choice > 0 else -index
        for index, choice in enumerate(choices, start=1)
        if choice
    )


def partial_domain(reduction: Reduction, choices: tuple[int, ...]) -> frozenset[State]:
    literals = reduction.literal_states
    return reduction.initial | frozenset(
        literals[literal] for literal in selected_literals(choices)
    )


def hits_every_clause(cnf: CNF, selected: frozenset[int]) -> bool:
    return all(any(literal in selected for literal in clause) for clause in cnf)


def assignment_satisfies(cnf: CNF, assignment: tuple[bool, ...]) -> bool:
    def literal_true(literal: int) -> bool:
        value = assignment[abs(literal) - 1]
        return value if literal > 0 else not value

    return all(any(literal_true(literal) for literal in clause) for clause in cnf)


def brute_force_sat(num_variables: int, cnf: CNF) -> bool:
    return any(
        assignment_satisfies(cnf, assignment)
        for assignment in product((False, True), repeat=num_variables)
    )


def verify_strategy(
    reduction: Reduction,
    domain: frozenset[State],
    strategy: dict[tuple[int, ...], State],
    isomorphisms: tuple[InternalIsomorphism, ...],
) -> None:
    game = reduction.game
    require(set(strategy) == set(game.observations), "strategy table is not total")
    for observation, output in strategy.items():
        require(output in game.outputs, f"unknown output at {observation}")
        state, input_value = game.split_observation(observation)
        if state in domain:
            require(output in domain, f"strategy leaves its domain at {observation}")
            require(
                game.is_safe(state, input_value, output),
                f"strategy violates safety at {observation}",
            )

    arity = game.state_arity + game.input_arity
    for isomorphism in isomorphisms:
        for observation in product(tuple(isomorphism.domain), repeat=arity):
            output = strategy[observation]
            require(
                all(value in isomorphism.domain for value in output),
                "strategy fails subalgebra preservation",
            )
            mapped_observation = isomorphism.map_tuple(observation)
            require(
                strategy[mapped_observation] == isomorphism.map_tuple(output),
                "strategy fails internal-isomorphism equivariance",
            )


def verify_single_equation(reduction: Reduction) -> None:
    """Check ``Safe(z) iff p(z)=g(z)`` and that ``g`` is a Q-term table."""

    game = reduction.game
    k = game.state_arity
    arity = 2 * k + 1

    def right(flat: tuple[int, ...]) -> int:
        state = flat[:k]
        input_value = (flat[k],)
        output = flat[k + 1 :]
        projection = flat[0]
        if game.is_safe(state, input_value, output):
            return projection
        separating_index = next(
            (index for index in range(1, len(flat)) if flat[index] != projection),
            None,
        )
        require(
            separating_index is not None,
            "unsafe transition has no coordinate separating it from p",
        )
        return flat[separating_index]

    for state in game.states:
        for input_value in game.inputs:
            for output in game.outputs:
                flat = state + input_value + output
                require(
                    (flat[0] == right(flat))
                    == game.is_safe(state, input_value, output),
                    f"equation disagrees with safety at {flat}",
                )

    for isomorphism in game.algebra.internal_isomorphisms():
        for flat in product(tuple(isomorphism.domain), repeat=arity):
            value = right(flat)
            require(value in isomorphism.domain, "g leaves an internal subalgebra")
            require(
                right(isomorphism.map_tuple(flat)) == isomorphism.map_value(value),
                "g fails internal-isomorphism equivariance",
            )


def check_formula(num_variables: int, clauses: Iterable[Iterable[int]]) -> dict[str, int | bool]:
    reduction = build_reduction(num_variables, clauses)
    verify_single_equation(reduction)
    game = reduction.game
    isomorphisms = game.algebra.internal_isomorphisms()
    kernel = CompiledParameterizedKernel(
        game,
        frozenset(),
        internal_isomorphisms=isomorphisms,
    )

    feasible_count = 0
    candidate_count = 0
    for choices in product((-1, 0, 1), repeat=num_variables):
        candidate_count += 1
        domain = partial_domain(reduction, choices)
        expected = hits_every_clause(reduction.clauses, selected_literals(choices))
        pointed = kernel.strategy_pointed(domain)
        reference = kernel.strategy_reference(domain)
        require(
            (pointed is not None) == (reference is not None),
            "pointed/reference disagreement",
        )
        require(
            (pointed is not None) == expected,
            "normal-form term safety disagrees with clause hitting",
        )
        if pointed is not None:
            feasible_count += 1
            verify_strategy(reduction, domain, pointed, isomorphisms)
            require(reference is not None, "reference disappeared after agreement")
            verify_strategy(reduction, domain, reference, isomorphisms)

    sat = brute_force_sat(num_variables, reduction.clauses)
    require((feasible_count > 0) == sat, "SAT and term safety disagree")
    return {
        "variables": num_variables,
        "clauses": len(reduction.clauses),
        "state_arity": game.state_arity,
        "states": len(game.states),
        "relation_bits": len(game.states) * len(game.inputs) * len(game.outputs),
        "candidate_domains": candidate_count,
        "feasible_normal_form_domains": feasible_count,
        "satisfiable": sat,
    }


def exhaustive_two_variable_corpus() -> tuple[tuple[Clause, ...], ...]:
    literals = (-2, -1, 1, 2)
    clause_universe: list[Clause] = [()]
    clause_universe.extend((literal,) for literal in literals)
    clause_universe.extend(tuple(pair) for pair in combinations(literals, 2))
    formulas: list[tuple[Clause, ...]] = []
    for clause_count in range(4):
        formulas.extend(
            tuple(clause_universe[index] for index in indices)
            for indices in combinations_with_replacement(
                range(len(clause_universe)), clause_count
            )
        )
    return tuple(formulas)


def three_variable_corpus() -> tuple[CNF, ...]:
    boundaries: list[CNF] = [
        (),
        ((),),
        ((1, -1),),
        ((1,), (-1,)),
        ((1, 1, 2), (-1, 3), (-2, -3)),
        tuple(
            tuple(
                index if bit == 0 else -index
                for index, bit in enumerate(bits, start=1)
            )
            for bits in product((0, 1), repeat=3)
        ),
    ]
    rng = random.Random(20260813)
    literals = (-3, -2, -1, 1, 2, 3)
    for _ in range(24):
        formula = []
        for _clause in range(rng.randrange(0, 9)):
            length = rng.randrange(0, 4)
            formula.append(tuple(rng.choice(literals) for _ in range(length)))
        boundaries.append(tuple(formula))
    return tuple(boundaries)


def mutation_checks() -> dict[str, bool]:
    unsat = ((1,), (-1,))
    base = build_reduction(1, unsat)
    isomorphisms = base.game.algebra.internal_isomorphisms()
    base_kernel = CompiledParameterizedKernel(
        base.game, frozenset(), internal_isomorphisms=isomorphisms
    )
    both_literals = base.initial | frozenset(base.literal_states.values())

    naive_local_false_positive = (
        base_kernel.local_feasible(both_literals)
        and base_kernel.strategy_pointed(both_literals) is None
    )

    clause_states_not_required = frozenset((base.live, *base.neutral))
    missing_initial_false_accept = (
        base_kernel.strategy_pointed(clause_states_not_required) is not None
    )

    no_dead = build_reduction(1, unsat, disable_dead_row=True)
    no_dead_kernel = CompiledParameterizedKernel(
        no_dead.game,
        frozenset(),
        internal_isomorphisms=no_dead.game.algebra.internal_isomorphisms(),
    )
    no_dead_domain = (
        no_dead.initial
        | frozenset(no_dead.literal_states.values())
        | frozenset((no_dead.dead,))
    )
    disabled_dead_false_accept = (
        no_dead_kernel.strategy_pointed(no_dead_domain) is not None
    )

    asymmetric = build_reduction(
        1,
        ((1,),),
        asymmetric_first_critical_pair=True,
    )
    asymmetric_equation_rejected = False
    try:
        verify_single_equation(asymmetric)
    except RuntimeError:
        asymmetric_equation_rejected = True

    checks = {
        "naive_local_accepts_unsat_witness": naive_local_false_positive,
        "omitting_clause_initials_accepts_unsat_witness": missing_initial_false_accept,
        "disabling_dead_row_accepts_unsat_witness": disabled_dead_false_accept,
        "asymmetric_critical_pair_rejected_by_term_gate": asymmetric_equation_rejected,
    }
    require(all(checks.values()), "one or more mutation controls failed")
    return checks


def size_rows() -> list[dict[str, int]]:
    rows = []
    for variables, clauses in ((1, 1), (2, 3), (3, 8), (8, 16), (16, 32), (64, 128)):
        k = choose_state_arity(variables, clauses)
        states = 3**k
        rows.append(
            {
                "variables": variables,
                "clauses": clauses,
                "state_arity": k,
                "states": states,
                "explicit_relation_bits": 3 * states * states,
            }
        )
    return rows


def main() -> None:
    rows: list[dict[str, int | bool]] = []
    two_variable = exhaustive_two_variable_corpus()
    for formula in two_variable:
        rows.append(check_formula(2, formula))
    three_variable = three_variable_corpus()
    for formula in three_variable:
        rows.append(check_formula(3, formula))

    mutations = mutation_checks()
    summary = {
        "schema": "orbit-synthesis/quasiprimal-cnf-initial-safety/v1",
        "algebra": "Quackenbush Q=({0,1,2};d,u)",
        "decision_problem": "explicit-relation initial-set term safety",
        "source_problem": "CNF-SAT (hardness proof may restrict to 3-CNF)",
        "corpus": {
            "exhaustive_two_variable_formulas": len(two_variable),
            "three_variable_boundary_and_seeded_formulas": len(three_variable),
            "formulas": len(rows),
            "candidate_normal_form_domains": sum(
                int(row["candidate_domains"]) for row in rows
            ),
            "sat_term_safety_mismatches": 0,
            "pointed_reference_mismatches": 0,
            "strategy_verification_failures": 0,
            "single_equation_failures": 0,
        },
        "satisfiable_formulas": sum(bool(row["satisfiable"]) for row in rows),
        "unsatisfiable_formulas": sum(not bool(row["satisfiable"]) for row in rows),
        "mutation_checks": mutations,
        "size_rows": size_rows(),
        "claim_boundary": (
            "Bounded calibration only. The generic NP-completeness claim rests on "
            "a separate manuscript proof under review. This receipt checks semantic "
            "one-equation definability; a separate compiler campaign checks polynomial "
            "table-relative term syntax, which is not succinct in arity."
        ),
    }
    summary["semantic_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PASS quasi-primal CNF initial-safety reduction")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

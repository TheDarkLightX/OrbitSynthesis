#!/usr/bin/env python3
"""No-import reconstruction of the generator-compressed converse."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from dataclasses import dataclass

Q = (0, 1, 2)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


@dataclass(frozen=True)
class Iso:
    domain: frozenset[int]
    codomain: frozenset[int]
    mapping_items: tuple[tuple[int, int], ...]

    @property
    def mapping(self) -> dict[int, int]:
        return dict(self.mapping_items)

    def applies(self, values) -> bool:
        return all(value in self.domain for value in values)

    def map_tuple(self, values) -> tuple[int, ...]:
        mapping = self.mapping
        return tuple(mapping[value] for value in values)

    def map_value(self, value: int) -> int:
        return self.mapping[value]


class Algebra:
    def __init__(self, unary=None) -> None:
        self.unary = unary

    def operations(self):
        yield 3, discriminator
        if self.unary is not None:
            yield 1, lambda value: self.unary[value]

    def generated(self, generators) -> frozenset[int]:
        result = set(generators)
        need(bool(result), "empty generators")
        changed = True
        while changed:
            changed = False
            current = tuple(result)
            for arity, operation in self.operations():
                for arguments in itertools.product(current, repeat=arity):
                    value = operation(*arguments)
                    if value not in result:
                        result.add(value)
                        changed = True
        return frozenset(result)

    def subalgebras(self):
        result = []
        for mask in range(1, 8):
            subset = frozenset(
                value for index, value in enumerate(Q) if mask & (1 << index)
            )
            if all(
                operation(*arguments) in subset
                for arity, operation in self.operations()
                for arguments in itertools.product(subset, repeat=arity)
            ):
                result.append(subset)
        return tuple(result)

    def isomorphisms(self):
        result = []
        for domain in self.subalgebras():
            source = tuple(sorted(domain))
            for codomain in self.subalgebras():
                if len(domain) != len(codomain):
                    continue
                for image in itertools.permutations(sorted(codomain)):
                    mapping = dict(zip(source, image))
                    if all(
                        mapping[operation(*arguments)]
                        == operation(*(mapping[value] for value in arguments))
                        for arity, operation in self.operations()
                        for arguments in itertools.product(source, repeat=arity)
                    ):
                        result.append(
                            Iso(
                                domain,
                                codomain,
                                tuple(sorted(mapping.items())),
                            )
                        )
        return tuple(result)

    def minimum_generators(self, subalgebra):
        values = tuple(value for value in Q if value in subalgebra)
        for size in range(1, len(values) + 1):
            for chosen in itertools.combinations(values, size):
                if self.generated(chosen) == subalgebra:
                    return chosen
        raise AssertionError("subalgebra failed to generate itself")


def extends(larger: Iso, smaller: Iso) -> bool:
    return (
        smaller.domain <= larger.domain
        and smaller.codomain <= larger.codomain
        and all(
            larger.mapping.get(value) == image
            for value, image in smaller.mapping_items
        )
    )


def choose_partial(algebra: Algebra, isomorphisms):
    carrier = frozenset(Q)
    automorphisms = tuple(
        isomorphism
        for isomorphism in isomorphisms
        if isomorphism.domain == carrier and isomorphism.codomain == carrier
    )
    nonextendable = tuple(
        isomorphism
        for isomorphism in isomorphisms
        if len(isomorphism.domain) > 1
        and not any(extends(auto, isomorphism) for auto in automorphisms)
    )
    maximal = tuple(
        isomorphism
        for isomorphism in nonextendable
        if not any(
            other != isomorphism and extends(other, isomorphism)
            for other in nonextendable
        )
    )
    if not maximal:
        return None
    return min(
        maximal,
        key=lambda isomorphism: (
            len(algebra.minimum_generators(isomorphism.domain)),
            -len(isomorphism.domain),
            repr(isomorphism.mapping_items),
        ),
    )


def orbit(seed, isomorphisms):
    reached = {tuple(seed)}
    stack = [tuple(seed)]
    while stack:
        item = stack.pop()
        for isomorphism in isomorphisms:
            if isomorphism.applies(item):
                mapped = isomorphism.map_tuple(item)
                if mapped not in reached:
                    reached.add(mapped)
                    stack.append(mapped)
    return frozenset(reached)


@dataclass
class Witness:
    phi: Iso
    generators: tuple[int, ...]
    state_arity: int
    source_state: tuple[int, ...]
    target_state: tuple[int, ...]
    source_output_zero: tuple[int, ...]
    source_output_one: tuple[int, ...]
    target_output_zero: tuple[int, ...]
    target_output_one: tuple[int, ...]
    critical_input: int
    left_domain: frozenset
    right_domain: frozenset
    critical_observations: frozenset
    dead_observations: frozenset
    safe_relation: frozenset


def build(algebra: Algebra):
    isomorphisms = algebra.isomorphisms()
    phi = choose_partial(algebra, isomorphisms)
    if phi is None:
        return None

    source_values = tuple(sorted(phi.domain))
    first, second = source_values[:2]
    generators = algebra.minimum_generators(phi.domain)
    source_output_zero = generators + (first, first)
    source_output_one = generators + (first, second)
    source_state = generators + (second, first)
    target_output_zero = phi.map_tuple(source_output_zero)
    target_output_one = phi.map_tuple(source_output_one)
    target_state = phi.map_tuple(source_state)
    source_dead_input = next(value for value in Q if value not in phi.domain)
    target_dead_input = next(value for value in Q if value not in phi.codomain)

    critical_observations = orbit(
        source_state + (first,),
        isomorphisms,
    )
    need(
        target_state + (phi.map_value(first),) in critical_observations,
        "critical transport",
    )
    dead_observations = (
        orbit(source_output_one + (source_dead_input,), isomorphisms)
        | orbit(target_output_zero + (target_dead_input,), isomorphisms)
    )
    need(
        not critical_observations & dead_observations,
        "critical/dead collision",
    )

    critical_transitions = set()
    for output in (source_output_zero, source_output_one):
        critical_transitions.update(
            orbit(source_state + (first,) + output, isomorphisms)
        )

    state_arity = len(source_state)
    states = tuple(itertools.product(Q, repeat=state_arity))
    safe = set()
    for state in states:
        for input_value in Q:
            observation = state + (input_value,)
            if observation in critical_observations or observation in dead_observations:
                continue
            safe.add((state, input_value, state))
    for row in critical_transitions:
        safe.add((row[:state_arity], row[state_arity], row[state_arity + 1 :]))

    left_domain = frozenset((source_state, source_output_zero))
    right_domain = frozenset((target_state, target_output_one))
    need(
        not any(
            observation[:state_arity] in left_domain | right_domain
            for observation in dead_observations
        ),
        "dead orbit reached protected state",
    )
    return Witness(
        phi,
        generators,
        state_arity,
        source_state,
        target_state,
        source_output_zero,
        source_output_one,
        target_output_zero,
        target_output_one,
        first,
        left_domain,
        right_domain,
        critical_observations,
        dead_observations,
        frozenset(safe),
    )


def domain_feasible(algebra: Algebra, witness: Witness, domain) -> bool:
    isomorphisms = algebra.isomorphisms()
    state_arity = witness.state_arity
    states = tuple(itertools.product(Q, repeat=state_arity))
    observations = tuple(
        state + (input_value,)
        for state in states
        for input_value in Q
    )
    domains = {}
    for observation in observations:
        state, input_value = observation[:state_arity], observation[state_arity]
        generated = algebra.generated(observation)
        allowed = {
            output
            for output in states
            if all(value in generated for value in output)
        }
        if state in domain:
            allowed = {
                output
                for output in allowed
                if output in domain
                and (state, input_value, output) in witness.safe_relation
            }
        if not allowed:
            return False
        domains[observation] = allowed

    edges = {observation: [] for observation in observations}
    neighbors = {observation: set() for observation in observations}
    for isomorphism in isomorphisms:
        for observation in itertools.product(
            tuple(isomorphism.domain),
            repeat=state_arity + 1,
        ):
            target = isomorphism.map_tuple(observation)
            edges[observation].append((target, isomorphism))
            neighbors[observation].add(target)
            neighbors[target].add(observation)

    seen = set()
    for representative in observations:
        if representative in seen:
            continue
        component = set()
        stack = [representative]
        while stack:
            observation = stack.pop()
            if observation in component:
                continue
            component.add(observation)
            stack.extend(neighbors[observation] - component)
        seen.update(component)

        solved = False
        for candidate in domains[representative]:
            assignment = {representative: candidate}
            queue = [representative]
            failed = False
            while queue and not failed:
                source = queue.pop()
                output = assignment[source]
                for target, isomorphism in edges[source]:
                    if not all(value in isomorphism.domain for value in output):
                        failed = True
                        break
                    mapped = isomorphism.map_tuple(output)
                    if mapped not in domains[target]:
                        failed = True
                        break
                    if target in assignment and assignment[target] != mapped:
                        failed = True
                        break
                    if target not in assignment:
                        assignment[target] = mapped
                        queue.append(target)
            if not failed and set(assignment) == component:
                solved = True
                break
        if not solved:
            return False
    return True


def principal_safe(witness: Witness):
    states = tuple(itertools.product(Q, repeat=witness.state_arity))
    safe = {
        (state, input_value, output)
        for state, input_value, output in witness.safe_relation
        if state + (input_value,) in witness.critical_observations
    }
    for state in states:
        for input_value in Q:
            observation = state + (input_value,)
            if (
                observation in witness.critical_observations
                or observation in witness.dead_observations
            ):
                continue
            for output in states:
                safe.add((state, input_value, output))
    return frozenset(safe)


def principal_audit(algebra: Algebra, witness: Witness):
    safe = principal_safe(witness)
    safe_flattened = {
        state + (input_value,) + output
        for state, input_value, output in safe
    }
    all_rows = set(
        itertools.product(Q, repeat=2 * witness.state_arity + 1)
    )
    unsafe = all_rows - safe_flattened
    isomorphisms = algebra.isomorphisms()
    projection_by_row = {}
    orbit_count = 0

    while len(projection_by_row) < len(unsafe):
        seed = min(unsafe - set(projection_by_row), key=repr)
        component = orbit(seed, isomorphisms)
        need(component <= unsafe, "unsafe orbit crossed safety boundary")
        alternate = next(
            (
                index
                for index, value in enumerate(seed)
                if value != seed[0]
            ),
            None,
        )
        need(alternate is not None, "constant unsafe tuple")
        for row in component:
            need(row[alternate] != row[0], "orbit lost projection separation")
            projection_by_row[row] = alternate
        orbit_count += 1

    single_projection_exists = any(
        all(row[index] != row[0] for row in unsafe)
        for index in range(1, 2 * witness.state_arity + 1)
    )
    for row in all_rows:
        is_safe = row in safe_flattened
        separator = row[0] if is_safe else row[projection_by_row[row]]
        need((row[0] == separator) == is_safe, "principal equation")
        need(separator in algebra.generated(row), "separator left generated subalgebra")
        for isomorphism in isomorphisms:
            if not isomorphism.applies(row):
                continue
            mapped = isomorphism.map_tuple(row)
            mapped_safe = mapped in safe_flattened
            need(mapped_safe == is_safe, "relation invariance")
            mapped_separator = (
                mapped[0]
                if mapped_safe
                else mapped[projection_by_row[mapped]]
            )
            need(
                mapped_separator == isomorphism.map_value(separator),
                "separator equivariance",
            )
            if not is_safe:
                need(
                    projection_by_row[mapped] == projection_by_row[row],
                    "orbit projection drift",
                )
    return (
        len(all_rows),
        not single_projection_exists,
        len(safe),
        len(unsafe),
        orbit_count,
    )


def receipt():
    counts = Counter()
    classifications = []
    rows_checked = 0
    strict_reductions = 0
    q_checkpoint = None

    for table in itertools.product(Q, repeat=3):
        algebra = Algebra(tuple(table))
        witness = build(algebra)
        if witness is None:
            counts["demi"] += 1
            classifications.append([list(table), True, None])
            continue

        counts["non_demi"] += 1
        counts[f"arity_{witness.state_arity}"] += 1
        need(
            algebra.generated(witness.generators) == witness.phi.domain,
            "generator prefix",
        )
        need(
            witness.state_arity == len(witness.generators) + 2,
            "compressed state arity",
        )
        need(domain_feasible(algebra, witness, witness.left_domain), "left")
        need(domain_feasible(algebra, witness, witness.right_domain), "right")
        need(
            not domain_feasible(
                algebra,
                witness,
                witness.left_domain | witness.right_domain,
            ),
            "union",
        )

        baseline_arity = len(witness.phi.domain) + 2
        strict_reductions += int(witness.state_arity < baseline_arity)
        (
            rows,
            no_single_projection,
            safe_count,
            unsafe_count,
            unsafe_orbits,
        ) = principal_audit(algebra, witness)
        rows_checked += rows
        classifications.append(
            [list(table), False, witness.state_arity]
        )

        if table == (1, 0, 1):
            q_checkpoint = {
                "generators": list(witness.generators),
                "state_arity": witness.state_arity,
                "baseline_arity": baseline_arity,
                "principal_rows": rows,
                "principal_safe_transitions": safe_count,
                "principal_unsafe_transitions": unsafe_count,
                "unsafe_groupoid_orbits": unsafe_orbits,
                "no_single_alternate_projection_exists": no_single_projection,
            }

    need((counts["demi"], counts["non_demi"]) == (15, 12), "census")
    need((counts["arity_3"], counts["arity_4"]) == (6, 6), "arity distribution")
    need(strict_reductions == 6, "strict reductions")
    need(rows_checked == 131220, "flattened row count")
    need(q_checkpoint is not None, "Q checkpoint")

    result = {
        "schema": "orbit-synthesis/generator-compressed-converse-independent/v1",
        "demi": counts["demi"],
        "non_demi": counts["non_demi"],
        "arity_distribution": {
            "3": counts["arity_3"],
            "4": counts["arity_4"],
        },
        "strict_arity_reductions": strict_reductions,
        "flattened_rows_checked": rows_checked,
        "baseline_flattened_rows": 236196,
        "classifications": classifications,
        "quackenbush_q": q_checkpoint,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


if __name__ == "__main__":
    print(json.dumps(receipt(), indent=2, sort_keys=True))

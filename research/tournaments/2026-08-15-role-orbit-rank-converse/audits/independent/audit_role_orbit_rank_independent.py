#!/usr/bin/env python3
"""No-import reconstruction of the role-orbit greatest-region converse."""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from dataclasses import dataclass

Q = (0, 1, 2)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def d(x: int, y: int, z: int) -> int:
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

    def map_tuple(self, values):
        mapping = self.mapping
        return tuple(mapping[value] for value in values)

    def map_value(self, value: int) -> int:
        return self.mapping[value]


class Alg:
    def __init__(self, unary=None):
        self.unary = unary

    def operations(self):
        yield 3, d
        if self.unary is not None:
            yield 1, lambda value: self.unary[value]

    def generated(self, generators):
        result = set(generators)
        need(result, "empty generator convention is outside this audit")
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
        for mask in range(1, 1 << len(Q)):
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
        subalgebras = self.subalgebras()
        for domain in subalgebras:
            source = tuple(sorted(domain))
            for codomain in subalgebras:
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

    def minimum_generator_size(self, subalgebra) -> int:
        ordered = tuple(sorted(subalgebra))
        for size in range(1, len(ordered) + 1):
            for chosen in itertools.combinations(ordered, size):
                if self.generated(chosen) == subalgebra:
                    return size
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


def maximal_nonextendable(algebra: Alg, isomorphisms):
    carrier = frozenset(Q)
    automorphisms = tuple(
        iso
        for iso in isomorphisms
        if iso.domain == carrier and iso.codomain == carrier
    )
    bad = tuple(
        iso
        for iso in isomorphisms
        if len(iso.domain) > 1
        and not any(extends(automorphism, iso) for automorphism in automorphisms)
    )
    return tuple(
        iso
        for iso in bad
        if not any(other != iso and extends(other, iso) for other in bad)
    )


def generating_orbit_representatives(
    algebra: Alg,
    subalgebra: frozenset[int],
    arity: int,
    isomorphisms,
):
    automorphisms = tuple(
        iso
        for iso in isomorphisms
        if iso.domain == subalgebra and iso.codomain == subalgebra
    )
    generating = tuple(
        values
        for values in itertools.product(tuple(sorted(subalgebra)), repeat=arity)
        if algebra.generated(values) == subalgebra
    )
    seen = set()
    representatives = []
    for values in generating:
        if values in seen:
            continue
        orbit = frozenset(
            automorphism.map_tuple(values) for automorphism in automorphisms
        )
        seen.update(orbit)
        representatives.append(min(orbit, key=repr))
    return tuple(sorted(representatives, key=repr))


def three_role_basis(algebra: Alg, subalgebra, isomorphisms):
    upper = algebra.minimum_generator_size(subalgebra) + 2
    counts = []
    for arity in range(1, upper + 1):
        representatives = generating_orbit_representatives(
            algebra, subalgebra, arity, isomorphisms
        )
        counts.append(len(representatives))
        if len(representatives) >= 3:
            return arity, representatives[:3], tuple(counts), len(representatives)
    raise AssertionError("d(B)+2 upper bound failed")


def choose_obstruction(algebra: Alg, isomorphisms):
    candidates = []
    for partial in maximal_nonextendable(algebra, isomorphisms):
        arity, roles, counts, orbit_count = three_role_basis(
            algebra, partial.domain, isomorphisms
        )
        candidates.append(
            (
                arity,
                -len(partial.domain),
                repr(partial.mapping_items),
                partial,
                roles,
                counts,
                orbit_count,
            )
        )
    if not candidates:
        return None
    chosen = min(candidates, key=lambda item: item[:3])
    return chosen[3:]


def orbit(seed, isomorphisms):
    reached = {tuple(seed)}
    stack = [tuple(seed)]
    while stack:
        values = stack.pop()
        for isomorphism in isomorphisms:
            if not isomorphism.applies(values):
                continue
            target = isomorphism.map_tuple(values)
            if target not in reached:
                reached.add(target)
                stack.append(target)
    return frozenset(reached)


@dataclass
class Witness:
    phi: Iso
    role_counts: tuple[int, ...]
    available_role_orbits: int
    k: int
    a: tuple[int, ...]
    ap: tuple[int, ...]
    p0: tuple[int, ...]
    p1: tuple[int, ...]
    q0: tuple[int, ...]
    q1: tuple[int, ...]
    critical_input: int
    left: frozenset
    right: frozenset
    critical: frozenset
    dead: frozenset
    safe: frozenset


def build(algebra: Alg):
    isomorphisms = algebra.isomorphisms()
    selected = choose_obstruction(algebra, isomorphisms)
    if selected is None:
        return None
    phi, roles, counts, orbit_count = selected
    a, p0, p1 = roles
    k = len(a)
    ap = phi.map_tuple(a)
    q0 = phi.map_tuple(p0)
    q1 = phi.map_tuple(p1)
    critical_input = min(phi.domain)
    beta = next(value for value in Q if value not in phi.domain)
    gamma = next(value for value in Q if value not in phi.codomain)

    critical = orbit(a + (critical_input,), isomorphisms)
    need(
        ap + (phi.map_value(critical_input),) in critical,
        "critical transport",
    )
    dead = orbit(p1 + (beta,), isomorphisms) | orbit(
        q0 + (gamma,), isomorphisms
    )
    need(not critical & dead, "critical/dead collision")

    critical_transitions = set()
    for output in (p0, p1):
        critical_transitions.update(
            orbit(a + (critical_input,) + output, isomorphisms)
        )

    states = tuple(itertools.product(Q, repeat=k))
    safe = set()
    for state in states:
        for input_value in Q:
            observation = state + (input_value,)
            if observation in critical or observation in dead:
                continue
            safe.add((state, input_value, state))
    for row in critical_transitions:
        safe.add((row[:k], row[k], row[k + 1 :]))

    left = frozenset((a, p0))
    right = frozenset((ap, q1))
    need(
        not any(observation[:k] in left | right for observation in dead),
        "dead orbit reached protected state",
    )
    return Witness(
        phi,
        counts,
        orbit_count,
        k,
        a,
        ap,
        p0,
        p1,
        q0,
        q1,
        critical_input,
        left,
        right,
        critical,
        dead,
        frozenset(safe),
    )


def domain_feasible(algebra: Alg, witness: Witness, domain):
    isomorphisms = algebra.isomorphisms()
    k = witness.k
    states = tuple(itertools.product(Q, repeat=k))
    observations = tuple(state + (value,) for state in states for value in Q)
    domains = {}
    for observation in observations:
        state, input_value = observation[:k], observation[k]
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
                and (state, input_value, output) in witness.safe
            }
        if not allowed:
            return False
        domains[observation] = allowed

    edges = {observation: [] for observation in observations}
    neighbors = {observation: set() for observation in observations}
    for isomorphism in isomorphisms:
        for observation in itertools.product(
            tuple(isomorphism.domain), repeat=k + 1
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
    states = tuple(itertools.product(Q, repeat=witness.k))
    safe = {
        (state, input_value, output)
        for state, input_value, output in witness.safe
        if state + (input_value,) in witness.critical
    }
    for state in states:
        for input_value in Q:
            observation = state + (input_value,)
            if observation in witness.critical or observation in witness.dead:
                continue
            for output in states:
                safe.add((state, input_value, output))
    return frozenset(safe)


def separator_map(algebra: Alg, witness: Witness, isomorphisms):
    safe = principal_safe(witness)
    safe_flat = frozenset(
        state + (input_value,) + output
        for state, input_value, output in safe
    )
    all_rows = frozenset(itertools.product(Q, repeat=2 * witness.k + 1))
    unsafe = all_rows - safe_flat
    separator = {}
    components = 0

    while len(separator) < len(unsafe):
        seed = min(unsafe - set(separator), key=repr)
        component = orbit(seed, isomorphisms)
        need(component <= unsafe, "unsafe orbit crossed safe relation")
        selected = None
        for candidate in sorted(algebra.generated(seed)):
            if candidate == seed[0]:
                continue
            assignment = {seed: candidate}
            queue = [seed]
            failed = False
            while queue and not failed:
                source = queue.pop()
                value = assignment[source]
                for isomorphism in isomorphisms:
                    if not isomorphism.applies(source):
                        continue
                    target = isomorphism.map_tuple(source)
                    if target not in component:
                        continue
                    if value not in isomorphism.domain:
                        failed = True
                        break
                    mapped = isomorphism.map_value(value)
                    if mapped == target[0]:
                        failed = True
                        break
                    if target in assignment and assignment[target] != mapped:
                        failed = True
                        break
                    if target not in assignment:
                        assignment[target] = mapped
                        queue.append(target)
            if not failed and set(assignment) == set(component):
                selected = assignment
                break
        need(selected is not None, "unsafe orbit lacks generated separator")
        separator.update(selected)
        components += 1
    return safe_flat, separator, components


def principal_audit(algebra: Alg, witness: Witness):
    isomorphisms = algebra.isomorphisms()
    safe, separator, components = separator_map(algebra, witness, isomorphisms)
    rows = tuple(itertools.product(Q, repeat=2 * witness.k + 1))
    for row in rows:
        is_safe = row in safe
        value = row[0] if is_safe else separator[row]
        need((row[0] == value) == is_safe, "principal equation")
        need(value in algebra.generated(row), "separator left generated subalgebra")
        if not is_safe:
            need(value != row[0], "unsafe separator collision")
        for isomorphism in isomorphisms:
            if not isomorphism.applies(row):
                continue
            mapped = isomorphism.map_tuple(row)
            need((mapped in safe) == is_safe, "relation invariance")
            mapped_value = mapped[0] if mapped in safe else separator[mapped]
            need(
                mapped_value == isomorphism.map_value(value),
                "separator equivariance",
            )
    return len(rows), len(rows) - len(safe), components, len(safe)


def compile_counts(algebra: Alg, witness: Witness):
    isomorphisms = algebra.isomorphisms()
    k = witness.k
    states = tuple(itertools.product(Q, repeat=k))
    observations = tuple(state + (value,) for state in states for value in Q)
    safe = principal_safe(witness)
    edges = {observation: [] for observation in observations}
    neighbors = {observation: set() for observation in observations}
    for isomorphism in isomorphisms:
        for observation in itertools.product(
            tuple(isomorphism.domain), repeat=k + 1
        ):
            target = isomorphism.map_tuple(observation)
            edges[observation].append((target, isomorphism))
            neighbors[observation].add(target)
            neighbors[target].add(observation)

    seen = set()
    components = []
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
        components.append(tuple(sorted(component, key=repr)))

    candidate_count = 0
    clause_count = len(components)
    for component in components:
        representative = component[0]
        generated = algebra.generated(representative)
        representative_outputs = tuple(
            output
            for output in states
            if all(value in generated for value in output)
        )
        signatures = set()
        for candidate in representative_outputs:
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
                    if target in assignment and assignment[target] != mapped:
                        failed = True
                        break
                    if target not in assignment:
                        assignment[target] = mapped
                        queue.append(target)
            if failed or set(assignment) != set(component):
                continue

            forbidden = set()
            closure = set()
            for observation, output in assignment.items():
                state, input_value = observation[:k], observation[k]
                if (state, input_value, output) not in safe:
                    forbidden.add(state)
                elif state != output:
                    closure.add((state, output))
            signature = (frozenset(forbidden), frozenset(closure))
            if signature in signatures:
                continue
            signatures.add(signature)
            candidate_count += 1
            clause_count += len(forbidden) + len(closure)

    return {
        "states": len(states),
        "observations": len(observations),
        "components": len(components),
        "candidate_rules": candidate_count,
        "variables": len(states) + candidate_count,
        "hard_clauses": clause_count,
    }


def generator_tag_upper(algebra: Alg, witness: Witness) -> int:
    return algebra.minimum_generator_size(witness.phi.domain) + 2


def receipt():
    counts = Counter()
    classifications = []
    flattened_rows = 0
    strict = 0
    q_checkpoint = None
    aggregate_role = Counter()
    aggregate_generator = {
        "states": 648,
        "observations": 1944,
        "components": 1800,
        "candidate_rules": 101436,
        "variables": 102084,
        "hard_clauses": 103062,
    }

    for table in itertools.product(Q, repeat=3):
        algebra = Alg(tuple(table))
        witness = build(algebra)
        if witness is None:
            counts["demi"] += 1
            classifications.append([list(table), True, None])
            continue

        counts["non_demi"] += 1
        counts[f"rank_{witness.k}"] += 1
        need(witness.role_counts[-1] >= 3, "rank endpoint")
        need(all(count < 3 for count in witness.role_counts[:-1]), "rank minimality")
        need(
            all(
                algebra.generated(role) == witness.phi.domain
                for role in (witness.a, witness.p0, witness.p1)
            ),
            "role generation",
        )
        need(domain_feasible(algebra, witness, witness.left), "left domain")
        need(domain_feasible(algebra, witness, witness.right), "right domain")
        need(
            not domain_feasible(algebra, witness, witness.left | witness.right),
            "union",
        )

        upper = generator_tag_upper(algebra, witness)
        if witness.k < upper:
            strict += 1
        principal = principal_audit(algebra, witness)
        flattened_rows += principal[0]
        model = compile_counts(algebra, witness)
        aggregate_role.update(model)
        classifications.append(
            [
                list(table),
                False,
                witness.k,
                upper,
                list(witness.role_counts),
                model["candidate_rules"],
            ]
        )
        if table == (1, 0, 1):
            q_checkpoint = {
                "role_rank": witness.k,
                "generator_tag_upper_bound": upper,
                "generating_orbit_counts": list(witness.role_counts),
                "available_rank_three_orbits": witness.available_role_orbits,
                "roles": [
                    list(witness.a),
                    list(witness.p0),
                    list(witness.p1),
                ],
                "principal_rows": principal[0],
                "unsafe_rows": principal[1],
                "unsafe_groupoid_orbits": principal[2],
                "safe_rows": principal[3],
                "domain_model": model,
            }

    need((counts["demi"], counts["non_demi"]) == (15, 12), "extension census")
    need(counts["rank_3"] == 12, "rank distribution")
    need(strict == 6, "strict generator-tag improvements")
    need(flattened_rows == 26244, "flattened row census")
    need(q_checkpoint is not None, "missing Q checkpoint")
    role_model = dict(aggregate_role)
    expected_role = {
        "states": 324,
        "observations": 972,
        "components": 876,
        "candidate_rules": 19392,
        "variables": 19716,
        "hard_clauses": 20010,
    }
    need(role_model == expected_role, "aggregate role model census")

    result = {
        "schema": "orbit-synthesis/role-orbit-rank-converse-independent/v1",
        "demi": counts["demi"],
        "non_demi": counts["non_demi"],
        "role_rank_distribution": {"3": counts["rank_3"]},
        "strict_improvements_over_generator_tags": strict,
        "flattened_rows_checked": flattened_rows,
        "generator_compressed_flattened_rows": 131220,
        "full_listing_flattened_rows": 236196,
        "aggregate_domain_models": {
            "generator_tags": aggregate_generator,
            "role_orbits": role_model,
        },
        "classifications": classifications,
        "quackenbush_q": q_checkpoint,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


if __name__ == "__main__":
    print(json.dumps(receipt(), indent=2, sort_keys=True))

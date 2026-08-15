#!/usr/bin/env python3
"""Independent no-import reconstruction of the two frontier results."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

Q = (0, 1, 2)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


class Iso:
    def __init__(self, domain, codomain, mapping):
        self.domain = frozenset(domain)
        self.codomain = frozenset(codomain)
        self.mapping = dict(mapping)

    def applies(self, values):
        return all(value in self.domain for value in values)

    def map(self, values):
        return tuple(self.mapping[value] for value in values)


class Alg:
    def __init__(self, unary=None):
        self.unary = unary

    def operations(self):
        yield 3, d
        if self.unary is not None:
            yield 1, lambda value: self.unary[value]

    def generated(self, values):
        result = set(values)
        changed = True
        while changed:
            changed = False
            current = tuple(result)
            for arity, operation in self.operations():
                for args in itertools.product(current, repeat=arity):
                    value = operation(*args)
                    if value not in result:
                        result.add(value)
                        changed = True
        return frozenset(result)

    def subalgebras(self):
        result = []
        for mask in range(1, 8):
            subset = frozenset(v for i, v in enumerate(Q) if mask & (1 << i))
            if all(
                operation(*args) in subset
                for arity, operation in self.operations()
                for args in itertools.product(subset, repeat=arity)
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
                        mapping[operation(*args)]
                        == operation(*(mapping[value] for value in args))
                        for arity, operation in self.operations()
                        for args in itertools.product(source, repeat=arity)
                    ):
                        result.append(Iso(domain, codomain, mapping))
        return tuple(result)


def extends(larger: Iso, smaller: Iso) -> bool:
    return (
        smaller.domain <= larger.domain
        and smaller.codomain <= larger.codomain
        and all(larger.mapping.get(x) == y for x, y in smaller.mapping.items())
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
        and not any(extends(auto, iso) for auto in automorphisms)
    )
    maximal = tuple(
        iso
        for iso in bad
        if not any(other is not iso and extends(other, iso) for other in bad)
    )
    return None if not maximal else min(
        maximal,
        key=lambda iso: (-len(iso.domain), repr(sorted(iso.mapping.items()))),
    )


def generated_subpower(algebra: Alg, generators):
    generated = set(generators)
    width = len(generators[0])
    changed = True
    while changed:
        changed = False
        current = tuple(generated)
        for arity, operation in algebra.operations():
            for args in itertools.product(current, repeat=arity):
                value = tuple(
                    operation(*(argument[index] for argument in args))
                    for index in range(width)
                )
                if value not in generated:
                    generated.add(value)
                    changed = True
    return frozenset(generated)


def list_feasible(algebra: Alg, generators, lists, isomorphisms):
    rows = tuple(
        tuple(generator[index] for generator in generators)
        for index in range(len(lists))
    )
    distinct = tuple(dict.fromkeys(rows))
    positions = {
        row: tuple(i for i, observed in enumerate(rows) if observed == row)
        for row in distinct
    }
    row_set = set(distinct)
    edges = {row: [] for row in distinct}
    neighbors = {row: set() for row in distinct}
    for iso in isomorphisms:
        for row in distinct:
            if iso.applies(row):
                target = iso.map(row)
                if target in row_set:
                    edges[row].append((target, iso))
                    neighbors[row].add(target)
                    neighbors[target].add(row)

    seen = set()
    for representative in distinct:
        if representative in seen:
            continue
        component = set()
        stack = [representative]
        while stack:
            row = stack.pop()
            if row in component:
                continue
            component.add(row)
            stack.extend(neighbors[row] - component)
        seen.update(component)

        solved = False
        for candidate in algebra.generated(representative):
            assigned = {representative: candidate}
            queue = [representative]
            failed = False
            while queue and not failed:
                source = queue.pop()
                value = assigned[source]
                for target, iso in edges[source]:
                    if value not in iso.domain:
                        failed = True
                        break
                    mapped = iso.mapping[value]
                    if target in assigned and assigned[target] != mapped:
                        failed = True
                        break
                    if target not in assigned:
                        assigned[target] = mapped
                        queue.append(target)
            if failed or set(assigned) != component:
                continue
            if any(
                value not in lists[index]
                for row, value in assigned.items()
                for index in positions[row]
            ):
                continue
            solved = True
            break
        if not solved:
            return False
    return True


def list_audit():
    family = tuple(
        frozenset(v for i, v in enumerate(Q) if mask & (1 << i))
        for mask in range(1, 8)
    )
    configurations = {
        "pure": ((1, 1), (1, 2), (2, 1)),
        "q": ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2)),
    }
    counts = {}
    for label, algebra in (("pure", Alg()), ("q", Alg((1, 0, 1)))):
        isomorphisms = algebra.isomorphisms()
        checked = 0
        for generator_count, width in configurations[label]:
            for flat in itertools.product(Q, repeat=generator_count * width):
                generators = tuple(
                    tuple(flat[j * width + i] for i in range(width))
                    for j in range(generator_count)
                )
                subpower = generated_subpower(algebra, generators)
                for lists in itertools.product(family, repeat=width):
                    exact = list_feasible(algebra, generators, lists, isomorphisms)
                    brute = any(
                        all(vector[i] in lists[i] for i in range(width))
                        for vector in subpower
                    )
                    need(exact == brute, "list differential")
                    checked += 1
        expected = 525 if label == "pure" else 13755
        need(checked == expected, "list census")
        counts[label] = checked

    mutation = list_feasible(
        Alg((1, 0, 1)),
        ((0, 1),),
        (frozenset((0,)), frozenset((0,))),
        Alg((1, 0, 1)).isomorphisms(),
    )
    need(not mutation, "groupoid-edge mutation")
    return {"instances": sum(counts.values()), "per_algebra": counts}


def orbit(seed, isomorphisms):
    reached = {tuple(seed)}
    stack = [tuple(seed)]
    while stack:
        item = stack.pop()
        for iso in isomorphisms:
            if iso.applies(item):
                mapped = iso.map(item)
                if mapped not in reached:
                    reached.add(mapped)
                    stack.append(mapped)
    return frozenset(reached)


def build_witness(algebra: Alg):
    isomorphisms = algebra.isomorphisms()
    phi = maximal_nonextendable(algebra, isomorphisms)
    if phi is None:
        return None
    source = tuple(sorted(phi.domain))
    b0, b1 = source[:2]
    p = source + (b0, b0)
    r = source + (b0, b1)
    a = source + (b1, b0)
    q, s, ap = phi.map(p), phi.map(r), phi.map(a)
    outside_source = next(v for v in Q if v not in phi.domain)
    outside_target = next(v for v in Q if v not in phi.codomain)
    critical = orbit(a + (b0,), isomorphisms)
    dead_r = orbit(r + (outside_source,), isomorphisms)
    dead_q = orbit(q + (outside_target,), isomorphisms)
    need(not critical & (dead_r | dead_q), "orbit collision")

    k = len(a)
    critical_transitions = set()
    for output in (p, r):
        critical_transitions.update(orbit(a + (b0,) + output, isomorphisms))
    safe = set()
    for state in itertools.product(Q, repeat=k):
        for input_value in Q:
            observation = state + (input_value,)
            if observation not in critical and observation not in dead_r | dead_q:
                safe.add((state, input_value, state))
    for item in critical_transitions:
        safe.add((item[:k], item[k], item[k + 1 :]))
    return {
        "k": k,
        "left": frozenset((a, p)),
        "right": frozenset((ap, s)),
        "safe": frozenset(safe),
        "isos": isomorphisms,
    }


def domain_feasible(algebra: Alg, witness, domain):
    k = witness["k"]
    states = tuple(itertools.product(Q, repeat=k))
    observations = tuple(state + (u,) for state in states for u in Q)
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
                and (state, input_value, output) in witness["safe"]
            }
        if not allowed:
            return False
        domains[observation] = allowed

    edges = {observation: [] for observation in observations}
    neighbors = {observation: set() for observation in observations}
    for iso in witness["isos"]:
        for observation in observations:
            if iso.applies(observation):
                target = iso.map(observation)
                edges[observation].append((target, iso))
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
            assigned = {representative: candidate}
            queue = [representative]
            failed = False
            while queue and not failed:
                source = queue.pop()
                output = assigned[source]
                for target, iso in edges[source]:
                    if not all(value in iso.domain for value in output):
                        failed = True
                        break
                    mapped = iso.map(output)
                    if mapped not in domains[target]:
                        failed = True
                        break
                    if target in assigned and assigned[target] != mapped:
                        failed = True
                        break
                    if target not in assigned:
                        assigned[target] = mapped
                        queue.append(target)
            if not failed and set(assigned) == component:
                solved = True
                break
        if not solved:
            return False
    return True


def greatest_audit():
    rows = []
    demi = non_demi = 0
    for table in itertools.product(Q, repeat=3):
        algebra = Alg(tuple(table))
        witness = build_witness(algebra)
        if witness is None:
            demi += 1
            rows.append([list(table), True])
            continue
        non_demi += 1
        need(domain_feasible(algebra, witness, witness["left"]), "left")
        need(domain_feasible(algebra, witness, witness["right"]), "right")
        need(
            not domain_feasible(
                algebra,
                witness,
                witness["left"] | witness["right"],
            ),
            "union",
        )
        rows.append([list(table), False])
    need((demi, non_demi) == (15, 12), "extension census")
    need(build_witness(Alg()) is None, "pure discriminator control")
    return {"demi": demi, "non_demi": non_demi, "classifications": rows}


def receipt():
    result = {
        "schema": "orbit-synthesis/greatest-region-list-subpower-independent/v2",
        "list_subpower": list_audit(),
        "greatest_region": greatest_audit(),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def main():
    expected = output = None
    arguments = iter(sys.argv[1:])
    for argument in arguments:
        if argument == "--expected":
            expected = Path(next(arguments))
        elif argument == "--out":
            output = Path(next(arguments))
        else:
            raise SystemExit(argument)
    result = receipt()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if expected:
        need(result == json.loads(expected.read_text()), "receipt drift")
    if output:
        output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

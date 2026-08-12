#!/usr/bin/env python3
"""Exhaustive 3-element discriminator+unary boundary experiment.

Enumerate all 3^3=27 unary maps u:D->D on D={0,1,2}.  Every algebra
(D; discriminator, u) is quasi-primal because the discriminator is basic.

For each algebra:
- enumerate all subalgebras and internal isomorphisms;
- test the demi-semi-primal extension property;
- when it fails, locate a nonextendable swap of a 2-element subalgebra;
- build a uniform single-equation safety witness;
- verify by the full internal-isomorphism groupoid CSP that W1 and W2 are
  term-winning while W1 union W2 is not.

Result for this complete family: 15 demi, 12 non-demi, and all 12 non-demi
members admit the uniform no-greatest-region obstruction.
"""

from __future__ import annotations

from itertools import combinations, permutations, product

D = (0, 1, 2)
STATES = tuple(product(D, repeat=2))
INPUTS = tuple(product(D, repeat=2))
OUTPUTS = STATES


def nonempty_subsets():
    for r in range(1, len(D) + 1):
        for xs in combinations(D, r):
            yield frozenset(xs)


def subalgebras(u):
    # The discriminator is conservative, so closure is exactly closure under u.
    return [S for S in nonempty_subsets() if all(u[x] in S for x in S)]


def internal_isomorphisms(u):
    out = []
    subs = subalgebras(u)
    for S in subs:
        for T in subs:
            if len(S) != len(T):
                continue
            source = sorted(S)
            for target_values in permutations(sorted(T)):
                f = dict(zip(source, target_values))
                if all(f[u[x]] == u[f[x]] for x in S):
                    # Every bijection also preserves the discriminator.
                    out.append((S, T, f))
    return out


def full_automorphisms(u):
    universe = frozenset(D)
    return [
        f for S, T, f in internal_isomorphisms(u)
        if S == universe and T == universe
    ]


def extends_to_automorphism(phi, automorphisms) -> bool:
    return any(all(g[x] == y for x, y in phi.items()) for g in automorphisms)


def is_demi_semi_primal(u) -> bool:
    auts = full_automorphisms(u)
    return all(
        extends_to_automorphism(phi, auts)
        for _, _, phi in internal_isomorphisms(u)
    )


def find_nonextendable_two_point_swap(u):
    auts = full_automorphisms(u)
    for S in subalgebras(u):
        if len(S) != 2:
            continue
        a, b = sorted(S)
        swap = {a: b, b: a}
        if all(swap[u[x]] == u[swap[x]] for x in S):
            if not extends_to_automorphism(swap, auts):
                return S, swap
    return None


def closure_under_internal_isos(seeds, isos):
    closed = set(seeds)
    changed = True
    while changed:
        changed = False
        for t in tuple(closed):
            for S, _, phi in isos:
                if all(x in S for x in t):
                    image = tuple(phi[x] for x in t)
                    if image not in closed:
                        closed.add(image)
                        changed = True
    return frozenset(closed)


def generated_subalgebra(observation, u):
    generated = set(observation)
    changed = True
    while changed:
        changed = False
        for x in tuple(generated):
            y = u[x]
            if y not in generated:
                generated.add(y)
                changed = True
    return frozenset(generated)


def build_observation_groupoid(u, arity=4):
    observations = tuple(product(D, repeat=arity))
    adjacency = {z: [] for z in observations}
    isos = internal_isomorphisms(u)
    for S, _, phi in isos:
        for z in product(sorted(S), repeat=arity):
            image = tuple(phi[x] for x in z)
            adjacency[z].append((image, phi, S))
    return observations, adjacency


def exact_term_winning(u, safe, W) -> bool:
    """Exact fixed-domain feasibility using all internal isomorphisms."""
    W = set(W)
    observations, adjacency = build_observation_groupoid(u)

    candidates = {}
    for z in observations:
        state, inp = z[:2], z[2:]
        sg = generated_subalgebra(z, u)
        values = {
            v for v in OUTPUTS
            if all(x in sg for x in v)
        }
        if state in W:
            values = {v for v in values if v in W and safe(state, inp, v)}
        if not values:
            return False
        candidates[z] = values

    seen = set()
    for root in observations:
        if root in seen:
            continue

        component = {root}
        stack = [root]
        while stack:
            z = stack.pop()
            for image, _, _ in adjacency[z]:
                if image not in component:
                    component.add(image)
                    stack.append(image)
        seen.update(component)

        component_feasible = False
        for root_value in candidates[root]:
            assignment = {root: root_value}
            queue = [root]
            ok = True
            while queue and ok:
                z = queue.pop()
                value = assignment[z]
                for image, phi, source in adjacency[z]:
                    if not all(x in source for x in value):
                        ok = False
                        break
                    image_value = tuple(phi[x] for x in value)
                    if image_value not in candidates[image]:
                        ok = False
                        break
                    if image in assignment:
                        if assignment[image] != image_value:
                            ok = False
                            break
                    else:
                        assignment[image] = image_value
                        queue.append(image)
            if ok:
                component_feasible = True
                break

        if not component_feasible:
            return False

    return True


def build_uniform_obstruction(u):
    bad = find_nonextendable_two_point_swap(u)
    assert bad is not None
    S, _ = bad
    a, b = sorted(S)
    c = next(x for x in D if x not in S)
    isos = internal_isomorphisms(u)

    # k=2 state, m=2 input.  The special observation spans the two-point
    # subalgebra, avoiding singleton-subalgebra obstructions.
    special_observation = (a, b, a, b)
    special_seeds = [
        special_observation + (a, b),
        special_observation + (b, a),
    ]
    special_unsafe = closure_under_internal_isos(special_seeds, isos)

    # The dead observation contains all three carrier values, so no proper
    # internal isomorphism acts on it.  Close under the full groupoid anyway.
    dead_state = (b, b)
    dead_input = (a, c)
    dead_seeds = [dead_state + dead_input + v for v in OUTPUTS]
    dead_unsafe = closure_under_internal_isos(dead_seeds, isos)

    assert special_unsafe.isdisjoint(dead_unsafe)
    unsafe = special_unsafe | dead_unsafe

    def safe(state, inp, output):
        return state + inp + output not in unsafe

    # A single equation p=g defines the safe relation.
    # - on special unsafe orbits, use the second state projection;
    # - on dead unsafe orbits, use the first input projection;
    # - otherwise copy the first state projection.
    # Each branch is invariant under the internal-isomorphism groupoid.
    def g(t):
        if t in special_unsafe:
            return t[1]
        if t in dead_unsafe:
            return t[2]
        return t[0]

    # Verify g is an original-signature term through the quasi-primal
    # preservation characterization.
    for source, _, phi in isos:
        for t in product(sorted(source), repeat=6):
            image = tuple(phi[x] for x in t)
            assert g(image) == phi[g(t)]

    for t in product(D, repeat=6):
        assert ((t[0] == g(t)) == (t not in unsafe))

    W1 = frozenset({(a, b), (a, a)})
    W2 = frozenset({(b, a), (a, a)})

    return {
        "S": S,
        "a": a,
        "b": b,
        "c": c,
        "dead_state": dead_state,
        "safe": safe,
        "W1": W1,
        "W2": W2,
    }


def main() -> None:
    demi = []
    non_demi = []

    for values in product(D, repeat=3):
        u = {x: values[x] for x in D}
        if is_demi_semi_primal(u):
            demi.append(values)
            continue

        obstruction = build_uniform_obstruction(u)
        W1 = obstruction["W1"]
        W2 = obstruction["W2"]
        safe = obstruction["safe"]

        assert exact_term_winning(u, safe, W1)
        assert exact_term_winning(u, safe, W2)
        assert not exact_term_winning(u, safe, W1 | W2)

        # Any common winning superset would have to add the phi-partner
        # dead_state, but that state has an input with no safe successor.
        dead = obstruction["dead_state"]
        a = obstruction["a"]
        c = obstruction["c"]
        assert all(not safe(dead, (a, c), v) for v in OUTPUTS)

        non_demi.append(values)

    assert len(demi) == 15
    assert len(non_demi) == 12
    assert len(demi) + len(non_demi) == 27

    print("PASS complete 3-element discriminator+unary boundary")
    print("total unary expansions: 27")
    print("demi-semi-primal: 15")
    print("non-demi: 12")
    print("non-demi with verified uniform no-greatest obstruction: 12")
    print("non-demi unary tables:", non_demi)


if __name__ == "__main__":
    main()

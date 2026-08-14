# Exact weighted optimization of clone-constrained winning domains

**Status:** exact algorithm and proof note, 2026-08-14.  The implementation
reuses the compiled pointed-class semantics of OrbitSynthesis and adds an exact
branch-and-bound objective layer.  Primary and no-import bounded audits are
included.  The algorithm is not claimed polynomial-time in the number of game
states, is not yet Lean-formalized, and has not received external peer review.

## 1. Why optimization is the right practical interface

For ordinary finite safety games, the union of winning regions is winning, so
a greatest winning region is the canonical answer.  Shared-term safety can
behave differently.  A quasi-primal algebra with nonextendable internal
isomorphisms may have many incomparable maximal term-winning domains and no
common winning upper bound.

Enumerating every maximal domain is mathematically informative, but it can be
exponentially larger than the answer a user needs.  A practical system should
instead support questions such as:

- Which compatible domain has maximum utility?
- Which high-value states should be retained when some states are costly?
- Which states are mandatory or forbidden?
- Among strategies for the selected domain, which actions are preferred?

This note gives an exact optimizer for those questions without assuming that a
greatest region exists.

## 2. Optimization problem

Fix a compiled clone-constrained safety instance with finite state set

```text
S=(s_0,...,s_(n-1)).
```

Let `F` be the family of domains admitted by the pointed internal-isomorphism
constraints.  Inputs are:

```text
w:S -> Z                    integral state weights,
R subseteq S                required states,
X subseteq S                forbidden states,
R intersect X = empty.
```

For a domain `W`, write

```text
score(W)=sum_(s in W) w(s),
mask(W)=sum_(s_i in W) 2^i.
```

The optimizer maximizes the exact lexicographic objective

```text
(score(W), |W|, mask(W))
```

over

```text
W in F,
R subseteq W,
W intersect X = empty.
```

The second and third coordinates make the answer deterministic.  They do not
change the primary weighted objective.

Optional integer action preferences

```text
p:(observation,output) -> Z
```

are optimized only after the winning domain is fixed.  Each pointed component
chooses the valid seed with greatest transported preference score.  Since
pointed components are independent once `W` is fixed, this secondary choice is
exact.

## 3. Compiled seed-rule semantics

A fixed parameter core decomposes observations into pointed classes.  Each
class has finitely many representative output seeds.  For every seed and every
source state, compilation records:

- an **unsafe-source set**: including one of these states kills the seed; and
- a **requirement set**: including the source requires all transported output
  states to be included.

Thus a complete domain mask `D` admits a seed rule exactly when

```text
unsafe(seed) intersect D = empty
```

and

```text
requirements(seed,D) subseteq D.
```

A domain is feasible exactly when every pointed class admits at least one seed.
This is the same exact semantics used by the maximal-domain engine.

## 4. Branch-and-bound algorithm

A search node carries two disjoint masks:

```text
I = states forced into the domain,
E = states forced out of the domain.
```

### 4.1 Exact propagation

For every pointed class:

1. discard seed rules incompatible with `(I,E)`;
2. if no seed remains, emit a minimized two-sided nogood and prune;
3. include every state required by all surviving seeds;
4. exclude every undecided state whose inclusion would kill all surviving
   seeds;
5. repeat to a fixed point.

The propagation rules preserve exactly the feasible completions of the partial
assignment.

### 4.2 Objective upper bound

For every undecided state:

- include it in the optimistic completion when its weight is nonnegative;
- exclude it when its weight is negative.

This maximizes the additive score over every unconstrained completion.  Zero
weights are included, which also maximizes the secondary cardinality and mask
coordinates.  Hence

```text
UB(I,E)
```

is a valid lexicographic upper bound on every feasible completion below the
search node.

If

```text
UB(I,E) <= incumbent,
```

the node cannot improve the current optimum and is pruned.

### 4.3 Branching

Among undecided states, the implementation chooses the state maximizing

```text
(|weight|, structural impact, signed weight, canonical order).
```

Nonnegative states are tried inside first; negative states are tried outside
first.  This is a performance heuristic only and does not affect exactness.

## 5. Correctness theorem

### Theorem — exact weighted domain optimization

For every compiled pointed kernel, integer weight map, disjoint required and
forbidden sets, and finite action-preference map, the optimizer either:

1. reports that no feasible compatible domain satisfies the hard constraints;
   or
2. returns a domain `W`, total clone-compatible strategy `f`, and objective
   value such that:

```text
R subseteq W,
W intersect X = empty,
W is feasible,
```

and for every feasible `V` satisfying the same hard constraints,

```text
(score(V),|V|,mask(V))
 <=
(score(W),|W|,mask(W)).
```

Among valid total strategies on `W`, the returned strategy has maximum summed
action-preference score.

### Proof

Propagation removes no feasible completion: each forced inclusion is required
by every surviving seed of one pointed class, and each forced exclusion is a
state whose inclusion destroys every surviving seed.  A conflict is returned
only when one class has no viable seed.

The optimistic objective is an upper bound for every completion because the
score is additive: all positive and zero-weight undecided states are included
and every negative-weight state is excluded.  Therefore bound pruning cannot
remove a better feasible solution.

Every unpruned undecided state is eventually branched both ways.  Complete
leaves are checked against the exact seed rules.  Hence every feasible domain
is either visited or lies below a node whose valid upper bound is no greater
than the incumbent.  The final incumbent is globally optimal.

For a fixed domain, pointed classes share no seed variable.  Selecting the
highest-preference valid seed independently in every class therefore maximizes
the total action-preference sum. `square`

## 6. API

```python
from orbitsynthesis import (
    CompiledParameterizedKernel,
    optimize_weighted_domain,
    verify_weighted_domain_result,
)

kernel = CompiledParameterizedKernel(
    game,
    frozenset(),
    internal_isomorphisms=game.algebra.internal_isomorphisms(),
)

result = optimize_weighted_domain(
    kernel,
    state_weights={state_a: 10, state_b: -4},
    default_weight=1,
    required_states={initial_state},
    forbidden_states={failure_state},
    action_preferences={
        (observation, preferred_output): 5,
    },
)

assert verify_weighted_domain_result(
    kernel,
    result,
    state_weights={state_a: 10, state_b: -4},
    default_weight=1,
    required_states={initial_state},
    forbidden_states={failure_state},
    action_preferences={
        (observation, preferred_output): 5,
    },
)
```

The result includes:

- the optimal domain and total strategy;
- exact score, cardinality, and canonical mask;
- required/forbidden sets and state order;
- weight and preference digests;
- learned two-sided nogoods;
- branch, conflict, and bound-pruning statistics; and
- a deterministic search-trace SHA-256.

For bounded state sets, verification independently enumerates every domain
mask.  For larger instances, the current verifier performs deterministic
branch-and-bound replay.  A separately checkable proof log for large instances
is a future engineering target.

## 7. Deterministic evidence

Primary checker:

```text
research/tournaments/2026-08-14-weighted-domain-optimizer/
  check_weighted_optimizer.py
```

It compares branch-and-bound against exact mask enumeration for:

```text
512 unary safety relations over Q,
6 weight/constraint scenarios,
3,072 total instances.
```

The fixed census is:

```text
2,880 feasible,
192 infeasible.
```

The canonical objective corpus has SHA-256

```text
ab589ba21f07278b82308c9a79dbc90b6846b882345764efb66df72c7e3e4346
```

The primary checker also verifies:

- every feasible result through the public verifier;
- negative, zero, and positive weights;
- required and forbidden states;
- a secondary action-preference optimum of `13`;
- an effective strategy mutation;
- a nine-state pruning example; and
- fail-closed rejection of malformed optimization inputs.

The no-import audit uses the exact six unary term functions of Quackenbush `Q`
and independently reproduces the same complete corpus.

## 8. Claim boundary

The algorithm is exact but worst-case exponential in `|S|`.  The result does
not establish polynomial-time weighted optimization for arbitrary quasi-primal
safety instances, a compact proof certificate for every large search, a
minimal nogood set, or an approximation theorem.

The implementation assumes that the caller has selected a controller semantic
class whose algebraic hypotheses are justified.  It optimizes the compiled
pointed constraints; it does not itself prove quasi-primality or
semi-/demi-semi-primality.

Publication novelty, patent/FTO status, and practical performance against
MaxSAT, BDD/MDD, or logic-synthesis systems remain unassessed.
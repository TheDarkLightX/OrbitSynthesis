# Seed selector elimination and proof-carrying domain nogoods

**Status:** DERIVED exact logical normalization + finite calibration. Resolution, selector variables, and clause learning are classical. OrbitSynthesis-specific content is the exact mapping from pointed seed rules to domain-only conflict certificates and the bounded primitive-reason core. Tau-independent. Not Lean-checked.

## 1. Exact Boolean encoding

For every state p introduce Boolean variable

`w_p = 1 iff p belongs to W`.

For pointed class E and seed a introduce selector

`y_(E,a)`.

Require exactly one seed per class.

If seed a is unsafe at source p, add

`NOT y_(E,a) OR NOT w_p`.

If seed a requires successor q whenever p is active, add

`NOT y_(E,a) OR NOT w_p OR w_q`.

Required and forbidden domain states are ordinary unit clauses.

### Theorem 1 -- selector CNF is exact

The Boolean formula is satisfiable exactly when there is a domain W and one seed choice for every pointed class satisfying the compiled pointed-kernel semantics.

Fixing the y selectors leaves precisely the unsafe-source and forward-closure conditions of the chosen seeds.

## 2. The current custom solver is projected selector reasoning

The bitset/nogood search branches on domain membership but does not explicitly branch on seed selectors.

At a partial domain assignment it maintains the set of viable seeds of each class. When all seeds of one class are killed it learns a domain-only two-sided nogood.

Thus its logical normal form is:

> existentially hide the y variables, search only over w variables, and learn clauses projected onto the domain vocabulary.

A repository `DomainNogood(include=I, exclude=X)` is exactly the clause

`OR_(p in I) NOT w_p  OR  OR_(q in X) w_q`.

It is falsified precisely by completions containing every state in I and excluding every state in X.

## 3. Primitive seed-kill reasons

Fix disjoint partial sets I and X.

A seed is killed for one of two primitive reasons.

### Unsafe reason

If `p in I intersection Unsafe_a`, then choosing the seed violates

`NOT y_a OR NOT w_p`.

The domain repair literal is

`NOT w_p`.

### Broken-requirement reason

If `p in I`, `q in X`, and seed a has implication `p -> q`, then choosing the seed violates

`NOT y_a OR NOT w_p OR w_q`.

The domain repair clause is

`NOT w_p OR w_q`.

Every killed seed has at least one primitive reason of size one or two.

## 4. Resolution eliminates a whole class

Suppose a class has m seeds and every seed is killed.

Begin with its at-least-one clause

`y_1 OR ... OR y_m`.

For every seed i choose one violated primitive selector clause

`NOT y_i OR D_i`,

where D_i has one or two domain literals.

Resolve successively on `y_1,...,y_m`.

The result is

`D_1 OR ... OR D_m`.

All selected D_i are false under the current partial assignment, so this is a valid learned domain clause.

### Theorem 2 -- bounded proof core

Every class conflict with m seeds has a resolution-derived domain nogood containing at most `2m` distinct domain literals.

The abstract bound is tight: m seeds can be killed by pairwise-disjoint broken requirements, forcing two distinct literals per seed in any conflict subassignment.

This gives an a priori proof core whose size depends on class width, not on the number of states already assigned by the branch search.

## 5. Exact minimum conflict is a minimum reason union

For each killed seed a, let `Reasons(a)` contain all primitive violated reason-literal sets:

- `{NOT w_p}` for active unsafe p;
- `{NOT w_p, w_q}` for active p and excluded required successor q.

A subassignment L remains a class conflict iff every seed a has at least one reason `R in Reasons(a)` with `R subseteq L`.

### Theorem 3 -- minimum-conflict equivalence

The cardinality of a minimum class-conflict subassignment equals

`min | union_a R_a |`

where one chooses

`R_a in Reasons(a)`

for every seed a.

### Proof

Any union of one kill reason per seed kills every seed and is therefore a conflict.

Conversely, let L be any conflicting subassignment. Since each seed is killed under L, that seed has at least one primitive reason fully contained in L. Choose one such reason for every seed. Their union is contained in L and is itself a conflict.

Therefore an optimal conflict always has this form. QED.

## 6. Production consequence

The current greedy conflict minimizer starts from the entire partial assignment and deletes literals while the class remains conflicting.

A stronger exact-by-construction front end is:

1. enumerate the primitive violated reasons of every killed seed;
2. choose one short reason per seed, preferring overlap;
3. union them to obtain a sound core of at most `2m` literals;
4. run greedy deletion only on that core;
5. retain the selected reasons as a replayable resolution receipt.

For small classes, exact minimum-union search can replace the overlap heuristic.

The resulting nogood remains independently replayable against the original seed obligations.

## 7. Interaction with semantic seed canonicalization

Run the reduction from `SEED_RULE_SEMANTIC_KERNEL.md` first.

If semantic equivalence/dominance shrinks a class from raw width m to semantic width r, the universal proof-core bound improves from

`2m`

to

`2r`.

So canonical seed reduction and proof-carrying conflict learning reinforce each other.

## 8. Exact bounded calibration

An independent three-state checker generated random classes with up to four seeds and random disjoint partial assignments.

For every actual class conflict it compared:

1. exhaustive cardinality-minimum search over all conflict subassignments;
2. exhaustive minimum union of one primitive reason per seed.

It checked 4,443 conflicts with zero mismatches.

Deterministic receipt:

`6132a7759dfb07d7b1b67481f00208ed6bf7421734e007d08210c5df98a0af8d`.

The finite computation calibrates Theorem 3; the proof is combinatorial and independent of the random campaign.

## 9. Relation to SAT proof systems

Modern CDCL solvers learn clauses and can be simulated by resolution. The selector derivation above is therefore classical proof-system machinery specialized to the seed-rule compiler.

Do not claim resolution, selector variables, projected clauses, or generic clause learning as new.

The OrbitSynthesis-specific chain is

`term-controller interpolation`
`-> pointed observation classes`
`-> transported seed rules`
`-> selector clauses`
`-> domain-only resolution certificate`.

This chain preserves enough algebraic provenance to explain a Boolean conflict back in controller language.

## 10. Solver architecture consequence

There are now three explicit compiler layers:

1. **algebraic semantic compiler:** controller term constraints -> pointed classes and transports;
2. **seed semantic kernel:** raw seed rules -> safe SCC/preorder canonical form and semantic antichain;
3. **Boolean search:** class selectors + domain variables, with lazy selector elimination and learned domain clauses.

This makes a direct SAT backend a useful independent reference implementation rather than a competing mathematical semantics.

The benchmark question becomes:

> how much Boolean search is removed by algebraic and graph canonicalization before a generic SAT engine sees the instance?

## 11. Next targets

1. Add primitive-reason receipts to learned nogoods.
2. Compare current full-assignment greedy minimization with bounded proof-core-first minimization.
3. Build an independent selector-CNF reference backend for differential testing.
4. Compare projected maximal-domain enumeration against the specialized bitset search.
5. Determine which class-width / reason-overlap parameters predict minimum-nogood size.

# Seed-rule semantic kernel

**Status:** DERIVED + finite-calibrated. Exact graph/Horn semantics for one compiled seed rule and exact semantic dominance between seeds. Tau-independent. Not Lean-checked.

## 1. Raw seed rule

Fix a finite state set V. A compiled seed is a pair `(U,E)` where

- `U subseteq V` is its unsafe-source set;
- `E subseteq V x V` is the directed implication relation obtained from its successor requirements.

A domain W validates the seed iff

`W intersection U = empty`

and W is E-forward-closed:

`p in W and (p,q) in E -> q in W`.

The raw edge list is not canonical: transitive edges, edges below doomed states, and SCC-internal presentations can all differ while defining exactly the same domain family.

## 2. Safe kernel of one seed

Define

`Doom(U,E) = {p : p can reach some u in U by E}`

and

`G(U,E) = V \ Doom(U,E)`.

### Theorem 1 -- greatest seed-valid domain

`G(U,E)` is the greatest domain validating `(U,E)`.

Every valid domain is contained in G, and G itself is E-closed and avoids U.

Thus all states in `Doom(U,E)` are semantically dead for this seed and may be removed from its representation.

## 3. SCC/preorder canonical semantics

Restrict E to G and quotient by strongly connected components.

Inside one SCC, membership is all-or-none in any E-closed domain. The condensation graph is a DAG. A valid domain is exactly a union of SCCs that is upward-closed under reachability in this DAG.

Equivalently, define the reachability preorder

`p <=_E q  iff q is reachable from p`.

Then seed-valid domains are exactly the upward-closed subsets of G for this preorder.

### Corollary 2 -- semantic equivalence

Two seeds define exactly the same valid-domain family iff

1. they have the same greatest valid set G; and
2. their reachability preorders agree on G.

So a canonical semantic seed object is:

`(safe SCC set, condensation reachability order)`.

Raw transitive implications are representation noise.

## 4. Exact static dominance

For seeds a and b, say **a dominates b** when every domain validating b also validates a. In a class disjunction, b is then redundant because

`Valid_a OR Valid_b = Valid_a`.

Let `G_b` be b's greatest valid domain.

### Theorem 3 -- static dominance criterion

`Valid_b(W) -> Valid_a(W)` for every W iff:

1. every state in `G_b` is allowed by a, equivalently `U_a intersection G_b = empty`; and
2. for every implication `(p,q)` of a with `p in G_b`, q is reachable from p using b's implication graph.

### Necessity

`G_b` itself validates b. Hence it must avoid `U_a`.

If p is in `G_b`, then `Reach_b({p})` is a b-valid domain. If a requires `p -> q`, this domain must contain q, so q is b-reachable from p.

### Sufficiency

Take any b-valid W. It lies in `G_b`, so it avoids `U_a`. If p is in W and a requires `p -> q`, b-closure of W contains every b-reachable successor of p; by condition 2 it contains q. Thus W validates a.

This is strictly stronger than raw subset pruning. Example:

- a requires `p -> q`;
- b requires `p -> r` and `r -> q`.

Then b entails a even though a's edge does not occur literally in b.

## 5. Exact contextual dominance inside a search cone

A branch-and-bound node fixes disjoint sets:

- I: states required in every completion;
- X: states excluded from every completion.

Say b is **cone-feasible** if some b-valid W satisfies

`I subseteq W`, `W intersection X = empty`.

This holds iff

`Reach_b(I) intersection (U_b union X) = empty`.

If b is cone-feasible, define its greatest completion in the cone:

`G_b(I,X) = V \ PreStar_b(U_b union X)`.

It automatically contains I.

### Theorem 4 -- contextual dominance criterion

Within the cone `(I,X)`, every b-valid completion also validates a iff:

1. `U_a intersection G_b(I,X) = empty`; and
2. for every a-implication `p -> q` with `p in G_b(I,X)`,

`q in Reach_b(I union {p})`.

If b is cone-infeasible, b can simply be removed from the viable seed set.

### Proof mechanism

For any possible source p, the smallest b-valid completion in the cone that contains p is

`Reach_b(I union {p})`.

Therefore a's obligation at p is forced by b exactly when q already lies in that least completion.

This is Horn entailment expressed entirely as graph reachability.

## 6. Exact class simplification

For each pointed class before generic search:

1. compile every seed to `(U,E)`;
2. remove doomed states and compute SCC condensation;
3. quotient semantically equivalent seeds;
4. remove every seed whose valid-domain family is contained in another seed's family;
5. retain only the antichain of semantically weakest, nonredundant seeds.

At a search node the same idea can be reapplied contextually after I/X propagation.

This is exact. It changes neither the feasible-domain family nor reconstructed controller existence.

## 7. Why this matters for the width boundary

Raw seed count can overstate the true switch width.

A class with many syntactically different seeds may collapse to:

- one semantic seed: graph-closure regime;
- a small antichain: bounded switch search;
- a genuinely large semantic antichain: generic nogood/SAT regime.

Therefore the solver should report both

- raw seed width; and
- **semantic antichain width after entailment reduction**.

The latter is the relevant combinatorial parameter.

## 8. Finite validation

An independent checker compared the graph criterion against brute enumeration of complete domains.

### Exhaustive contextual test on two states

It exhausts:

- all 64 seed semantics `(U,E)` on a two-state universe;
- all ordered seed pairs `(a,b)`;
- all 9 disjoint partial cones `(I,X)`.

Total entailment checks:

`64 * 64 * 9 = 36,864`.

For every case, the graph criterion agrees with brute logical implication over all complete domains.

### Random three-state test

10,000 deterministic random seed-pair/cone instances were also checked against brute domain enumeration.

Zero mismatches.

Deterministic receipt:

`7f2804c13c65bc2bc88d515c799e1220f5b702bb9bc636076c829b68500b9ff1`.

The computations calibrate the proof; they are not the proof.

## 9. Noether-style compression

The inner object of a seed is not its list of local obligations.

It is a finite reachability order on the states that can survive the seed.

This exposes three layers that the raw representation mixes together:

1. **impossible states**: those that can flow into unsafe states;
2. **inseparable states**: SCCs that must enter or leave together;
3. **true order constraints**: reachability between SCCs.

Everything else is presentation.

## 10. Implementation plan

Do not immediately modify the production search without a repository replay.

A safe integration sequence is:

1. add a reference canonicalizer beside `CompiledPointedRules`;
2. differentially compare class feasibility for every complete domain before/after simplification on the existing 1,536 + 24,576 corpus;
3. compare maximal-domain sets and reconstructed strategies;
4. measure raw width versus semantic width per parameter core;
5. only then add contextual dominance to the bitset search.

The most important empirical question is whether semantic quotienting removes enough seeds to matter on real pointed kernels, not whether graph entailment itself is fast.

## 11. Next questions

1. What semantic widths occur across the existing quasi-primal benchmark families?
2. Can SCC/preorder certificates be reused across stronger/weaker parameter cores?
3. Can a class's semantic seed antichain be represented symbolically instead of explicitly when it is large?
4. Does the patchability obstruction hypergraph predict semantic width collapse?
5. Which algebraic conditions force every pointed class to have semantic width one?

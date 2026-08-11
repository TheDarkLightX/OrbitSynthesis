# Exponential canonical-response width in Henson graphs

**Status:** DERIVED exact lower bound; bounded exhaustive checks completed for small n,m; not yet formalized.

`MAXIMAL_RESPONSE_ANTICHAIN.md` shows that upward synthesis over a downward legal response family needs only the inclusion-maximal legal responses. This note proves that even that canonical antichain can be exponentially large in a very simple Henson instance.

## 1. Setup

Fix `n>=3` and consider the Henson `K_n`-free graph.

Let the old finite base graph be

`G_m = m K_(n-1)`,

the disjoint union of m copies of the `(n-1)`-clique.

This graph is `K_n`-free, so it is a valid finite base in the Henson age.

Let the clique blocks be

`C_1,...,C_m`,

with `|C_j|=n-1`.

A fresh response vertex y with neighborhood `N subseteq V(G_m)` is legal iff N contains no `(n-1)`-clique.

Since the only `(n-1)`-cliques of `G_m` are the blocks C_j,

`N legal  iff  for every j, C_j not-subseteq N`.

Equivalently N must omit at least one vertex from every block.

## 2. Exact maximal-response count

### Theorem 1

A legal neighborhood N is inclusion-maximal iff, for every block C_j, it omits exactly one vertex of C_j.

### Proof

If N omits at least two vertices from some block, one omitted vertex can be added without completing the whole clique, so N was not maximal.

If N omits exactly one vertex from every block, adding any omitted vertex completes that entire `(n-1)`-clique inside N and makes the fresh extension illegal. Hence N is maximal.

### Corollary 2

The number of maximal legal response types is

`|Max(E(G_m))| = (n-1)^m`.

Each of the m blocks independently chooses which one of its n-1 vertices is omitted.

Writing the total base size as

`N = m(n-1)`,

the width is

`(n-1)^(N/(n-1))`,

which is exponential in N for every fixed n>=3.

## 3. Important special cases

### Triangle-free Henson graph H_3

The base is a matching of m disjoint edges.

A maximal legal fresh neighborhood chooses exactly one endpoint from each edge, so

`|Max|=2^m`.

### K_4-free Henson graph H_4

The base is m disjoint triangles.

A maximal legal fresh neighborhood contains exactly two vertices from every triangle, so

`|Max|=3^m`.

## 4. Conflict-hypergraph duality

The response conflict hypergraph is exactly

`C={C_1,...,C_m}`,

a set of m pairwise disjoint hyperedges of rank n-1.

Its minimal transversals choose exactly one vertex from every C_j. Hence there are `(n-1)^m` minimal transversals, and their complements are the maximal legal response neighborhoods.

Thus fixed conflict rank does **not** imply polynomially many canonical maximal responses.

## 5. But the exponential family factorizes perfectly

Although flat enumeration needs `(n-1)^m` actions, the family is the Cartesian product of m independent local choices:

`choice_j in C_j` = the one omitted vertex in block j.

So a factorized representation needs only O(m(n-1)) incidence data plus m local `exactly-one` choices.

This gives a crucial distinction:

- **response-antichain size** is exponential;
- **response-family description size** is linear in the base graph for this family.

Therefore action enumeration is the wrong representation even after complete-type reduction.

## 6. Synthesis consequence

For an upward target Good,

`exists legal fresh response N. Good(N)`

can be phrased as an existential constraint over the m local omission choices rather than an explicit disjunction over `(n-1)^m` maximal neighborhoods.

The natural representation candidates include:

- product decision diagrams;
- d-DNNF / structured decomposable circuits;
- ZDDs;
- SAT/CSP encodings over one omission variable per conflict component;
- symmetry quotienting when the clique blocks are interchangeable.

## 7. General lower-bound lesson

The hierarchy is now:

1. unique greatest response: one canonical action;
2. several maximal responses: finite antichain;
3. exponentially many maximal responses but compact conflict factorization;
4. general conflict hypergraph requiring hypergraph dualization / knowledge compilation;
5. flat complete-type game as fallback.

Each step preserves more structure than simple response enumeration.

## 8. Bounded checks

A direct finite exhaustive oracle was run for:

- n=3, m=1,2,3 -> 2,4,8 maximal responses;
- n=4, m=1,2,3 -> 3,9,27;
- n=5, m=1,2,3 -> 4,16,64.

All matched `(n-1)^m` exactly.

## 9. Next questions

1. Characterize conflict-hypergraph classes whose maximal-response family admits polynomial-size structured circuits even when the antichain is exponential.
2. Use treewidth/hypertree-width of the conflict hypergraph as a response-compilation parameter.
3. Prove compact d-DNNF/SDD bounds for disjoint or bounded-treewidth one-point obstruction hypergraphs.
4. Combine response circuit compilation with the positive-mu-calculus fixed-point layer.
5. Determine whether Henson synthesis over bounded-treewidth old bases becomes fixed-parameter tractable in the obstruction width/treewidth.

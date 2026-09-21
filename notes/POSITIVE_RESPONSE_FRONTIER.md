# Positive response frontiers: exact branching after monotone compression

**Status:** DERIVED finite-order theorem with exact examples. This refines `POSITIVE_SIGNATURE_DOMINANCE.md`: even when no greatest response exists, monotone objectives need only the inclusion-maximal realized positive signatures.

## 1. Signature family

Let E be a finite response-type fiber and Delta a finite family of predicates used only positively by the objective abstraction.

For each response type e define

`sigma(e) subseteq Delta`.

Let

`S_Delta(E) = { sigma(e) : e in E }`.

The positive fragment preorder is inclusion of signatures.

## 2. Maximal-signature theorem

Let

`Front_Delta(E) = Max_subset(S_Delta(E))`

be the inclusion-maximal realized signatures.

### Theorem 1 — dominated response types can be deleted

For every monotone Boolean objective F on Delta,

`exists e in E. F(sigma(e))`

iff

`exists s in Front_Delta(E). F(s)`.

### Proof

Every finite signature s is contained in some inclusion-maximal realized signature t. If F(s)=1, monotonicity gives F(t)=1. The reverse implication is immediate because every frontier signature is realized.

Thus system existential branching for the positive fragment depends on the frontier, not on the number of complete response types.

## 3. Exact positive response width

Define

`w_Delta(E) := |Front_Delta(E)|`.

Interpretation:

- `w=1`: one dominant response signature; existential system choice collapses completely;
- `w=k`: at most k genuinely nondominated response branches remain for every positive objective over Delta;
- the quotient also merges different complete response types with the same positive signature.

This is an exact fragment-relative branching parameter.

`w=1` is equivalent to union-realizability from `POSITIVE_SIGNATURE_DOMINANCE.md`.

## 4. Pure equality examples

Fix b distinct parameter equality classes.

### Positive equalities

`Delta_eq = {y=a_1,...,y=a_b}`.

Realized signatures are:

- each singleton `{y=a_i}`;
- the empty signature from a fresh y.

The maximal signatures are the b singletons, so

`w_eq = b`.

Thus positive equality objectives reduce the infinite response domain to exactly b nondominated equality choices.

### Positive disequalities

`Delta_neq={y!=a_i}`.

The fresh type realizes all b predicates and dominates every equality type. Hence

`w_neq=1`.

## 5. Dense linear order examples

Let distinct parameters satisfy

`a_1 < ... < a_k`.

Take positive predicates

`R_i := (a_i<y)`

and

`L_i := (y<a_i)`.

### One orientation

Using only all R_i, a point to the right of everything dominates: width 1.

Using only all L_i, a point to the left of everything dominates: width 1.

### Both orientations

For each open cut j=0,...,k, with

`a_j < y < a_(j+1)`

using the obvious endpoint conventions, the signature is

`{R_i : i<=j} UNION {L_i : i>j}`.

These k+1 cut signatures are pairwise incomparable.

A response exactly equal to a_j omits both `R_j` and `L_j` and is dominated by a neighboring open cut.

Therefore

`w_DLO = k+1`

for the mixed left/right positive inequality fragment.

So the complete one-point type count is not the correct branching measure; the positive response frontier is smaller and has a simple cut geometry.

## 6. Rado graph

Fix k distinct parameters.

### Positive adjacency only

Every adjacency subset is realized. The full adjacency signature dominates, so

`w=1`.

### One chosen polarity per parameter

Suppose Delta contains at most one of

`E(y,a_i)` or `not E(y,a_i)`

for each i. The Rado extension property realizes all selected desired polarities simultaneously, so again

`w=1`.

### Both polarities on r coordinates

Suppose for r parameter positions both adjacency and non-adjacency are independent positive atoms.

Each realized response chooses exactly one polarity at each of those r positions. Different choices are incomparable, and all `2^r` choices are realized.

Hence

`w=2^r`.

This gives an exact polarity-sensitive branching law for the random graph.

## 7. Henson K_n-free graph

For a fresh response y over a finite induced parameter graph G, positive adjacency signatures are exactly subsets A of `V(G)` containing no `(n-1)`-clique.

The maximal positive response signatures are therefore exactly the **maximal K_(n-1)-clique-free vertex subsets** of G.

Thus

`w(G) = number of maximal K_(n-1)-clique-free subsets of G`.

### Henson H_3

For the countable triangle-free Henson graph, allowed adjacency signatures are independent sets of G. Therefore the positive response frontier is the family of maximal independent sets.

Take G to be a matching of m disjoint edges (`k=2m` vertices). It is triangle-free and embeds in H_3.

A maximal independent set chooses exactly one endpoint from every edge, yielding

`w(G)=2^m=2^(k/2)`.

So positive-adjacency response branching can be exponential even though the theory is homogeneous and omega-categorical.

### General H_n

Let G be a disjoint union of m copies of `K_(n-1)`. This is K_n-free and hence embeds in H_n.

A maximal K_(n-1)-free vertex subset must omit exactly one vertex from every clique component. Therefore

`w(G)=(n-1)^m`

for

`k=m(n-1)`.

Again the positive response frontier can be exponential.

## 8. Hypergraph transversal duality

Let `K(G)` be the hypergraph whose hyperedges are the `(n-1)`-cliques of G.

A set A is K_(n-1)-clique-free iff its complement hits every hyperedge of `K(G)`.

Moreover:

- A is maximal clique-free
- iff `V(G)\A` is a minimal transversal of `K(G)`.

Therefore the Henson positive response frontier is exactly the complement of the minimal-transversal hypergraph:

`Front = { V\T : T in Tr(K(G)) }`.

This reconnects fragment-relative response compression to `ABA_HYPERGRAPH_DUALITY.md`: the same blocker/transversal algorithms can be used both for upward state-property representation and for enumerating nondominated response signatures in non-dominant theories.

## 9. General forbidden-pattern theorem

Suppose positive signatures are subsets of a finite feature universe D and feasibility is downward closed:

`S feasible and T subseteq S => T feasible`.

Let H be the hypergraph of inclusion-minimal forbidden feature sets.

Then maximal feasible signatures are exactly complements of minimal transversals of H.

### Proof

S is feasible iff it contains no forbidden hyperedge, equivalently `D\S` hits every forbidden hyperedge. Maximality of S is equivalent to minimality of its complement as a hitting set.

Thus whenever response feasibility is given by monotone forbidden patterns, the exact positive response frontier is a hypergraph dualization problem.

## 10. Partially collapsed reactive games

At each environment/partial type p compute

`Front_Delta(E_p)`.

Then replace the original response type fiber by one representative per frontier signature.

This is exact for all objectives positive in Delta.

The resulting system branching factor at p is

`w_Delta(E_p)`.

Global synthesis may therefore combine:

- deterministic fibers (`w=1`);
- small-frontier fibers;
- genuinely high-width fibers.

This is a much finer abstraction than a theory-wide yes/no tractability label.

## 11. Quantitative backend policy

A theory plugin can expose:

- signature computation;
- dominance test (`w=1`);
- maximal-signature enumeration;
- forbidden-pattern hypergraph when available;
- symbolic frontier representation when explicit enumeration is too large.

Suggested selection:

- `w=1`: dominant-response / box-modality collapse;
- small explicit w: bounded branching game;
- frontier given by compact symmetry/orbit description: quotient game;
- forbidden-pattern hypergraph with favorable dualization parameters: transversal engine;
- large unstructured frontier: generic type/game fallback.

## 12. Next theorem questions

1. Which omega-categorical homogeneous structures have polynomially bounded positive response width for natural atomic fragments?
2. Which structures admit FPT frontier enumeration under forbidden-pattern rank/treewidth/VC-dimension parameters?
3. Is bounded positive response width preserved by products / bounded lookback constructions used by ocLTL?
4. Can response frontiers themselves be quotient by automorphism orbits before game construction?
5. How does frontier width interact with strategy memory under nested mu-calculus objectives?
6. Can polymorphism identities bound frontier width without explicitly enumerating types?

The central invariant is now:

> **the antichain of nondominated positive response signatures**, not the cardinality of the complete response-type fiber.

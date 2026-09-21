# Maximal-response antichains: the next level beyond dominant synthesis

**Status:** DERIVED finite-order theorem with graph/hypergraph specialization. Hypergraph transversal algorithms are classical/active literature; their use as canonical response generators for infinite-structure synthesis is the research connection under investigation.

The greatest-response theorem is the best possible case, but it is not the only useful extremal reduction.

## 1. Finite downward legal response family

Let E be a finite response-code poset ordered by inclusion (or more generally a finite preorder). Let

`L subseteq E`

be the legal response family.

Assume L is downward closed in the response-information order and let

`Max(L)`

be its inclusion-maximal elements.

For an upward target Good:

### Theorem 1 — maximal-response reduction

`exists e in L. Good(e)`

iff

`exists m in Max(L). Good(m)`.

### Proof

Every legal e can be extended along the finite poset to some maximal legal m>=e. Upwardness carries Good from e to m. The converse is immediate.

Thus the infinite/conceptual system action space can often be replaced by a canonical finite antichain of maximal response types.

The dominant-response theorem is exactly the special case

`|Max(L)|=1`.

## 2. Modal consequence

When `Max(L)` has one element, existential response choice disappears and CPre becomes a box modality on the environment-only maximal-response transition.

When there are k>1 maximal responses, one obtains instead a finite disjunction/diamond over the k canonical maximal actions:

`forall environment P. exists m in Max(L_P). Good(m)`.

This is still potentially far smaller than enumerating every complete response type.

The response-antichain width

`r(P)=|Max(L_P)|`

is therefore a natural synthesis complexity parameter.

## 3. Conflict hypergraph representation

Let the response code be a subset N of a finite ground set V.

Suppose legality is downward closed. Let C be the hypergraph of inclusion-minimal illegal subsets (conflicts):

`C = { F subseteq V : F illegal and every proper subset of F is legal }`.

Then

`N is legal`

iff

`N contains no hyperedge F in C`.

So legal responses are exactly the independent sets of C.

## 4. Maximal legal responses and hypergraph blockers

Let `Tr(C)` be the hypergraph of inclusion-minimal transversals/hitting sets of C.

### Theorem 2

A set N is a maximal legal response iff

`V\N`

is a minimal transversal of C.

Hence

`Max(L) = { V\T : T in Tr(C) }`.

### Proof

N is legal iff its complement T intersects every conflict edge, i.e. T is a transversal. N is maximal legal iff deleting any vertex from T (equivalently adding it to N) destroys transversality, exactly minimality of T.

Thus canonical response enumeration is hypergraph dualization.

## 5. Greatest-response case revisited

The response family has a unique greatest element U iff the conflict hypergraph has a unique minimal transversal

`V\U`.

For a downward+union-closed legal family, the conflict hypergraph consists only of singleton forbidden vertices after minimization, so the unique minimal transversal is exactly the set of individually forbidden choices.

This recovers `MONOTONE_GRAPH_EXTENSION_CLASSIFICATION.md`.

## 6. Henson K_n-free graph

Fix a finite old K_n-free graph G and restrict to a fresh response vertex y.

A neighborhood N is legal iff G[N] contains no K_(n-1).

Define the conflict hypergraph

`C_(n-1)(G)`

whose vertices are V(G) and whose hyperedges are the vertex sets of all `(n-1)`-cliques of G.

Then:

- legal fresh neighborhoods = independent sets of `C_(n-1)(G)`;
- maximal legal fresh neighborhoods = maximal K_(n-1)-clique-free vertex subsets;
- their complements = minimal transversals of the `(n-1)`-clique hypergraph.

Therefore the Henson response problem is not an unstructured complete-type search. It is a canonical hypergraph-transversal problem.

### Triangle-free Henson graph H_3

Conflicts are ordinary edges of G.

Maximal legal neighborhoods are maximal independent sets of G, equivalently complements of minimal vertex covers.

So system response synthesis reduces to the well-studied maximal-independent-set / minimal-vertex-cover structure of the old graph.

## 7. Complexity hierarchy from conflict structure

The response synthesis problem can be routed by the conflict hypergraph:

### Width 1: unique maximal response

One canonical action. Synthesis collapses to environment-only model checking for upward objectives.

### Small maximal-response antichain

Enumerate a few canonical actions and retain a small finite game.

### Structured conflict hypergraph

Use transversal algorithms exploiting parameters such as:

- rank (maximum conflict size);
- VC dimension;
- transversal rank;
- conformality;
- maximum degree;
- symmetry.

### General conflict hypergraph

Hypergraph dualization is itself a difficult enumeration problem; no universal polynomial algorithm is known.

This is an intrinsic combinatorial barrier, not merely a poor theory encoding.

## 8. Literature hooks

Relevant algorithmic frontiers include:

- fixed-rank transversal enumeration;
- incremental-polynomial enumeration for bounded-VC-dimension hypergraphs;
- transversal-rank / conformality parameterizations.

For Henson K_n-free graphs, the conflict hypergraph has fixed rank n-1, but its number of minimal transversals can still be exponential. Output size remains a real lower bound.

## 9. General monotone graph classes

For a subgraph-closed finite graph class K and G in K, construct the conflict hypergraph C_K(G) of inclusion-minimal fresh neighborhoods N such that `G+_N y` leaves K.

Then Theorem 2 always gives the exact canonical maximal fresh responses.

`MONOTONE_GRAPH_EXTENSION_CLASSIFICATION.md` characterizes when every C_K(G) reduces to singleton conflicts, which is exactly the unique-greatest-response case.

Thus the maximal-response-antichain theorem strictly generalizes that classification.

## 10. Synthesis interpretation

Suppose the environment produces a partial old type sigma and the response fragment yields conflict hypergraph C_sigma.

Instead of quantifying over every complete response type, compute

`A_sigma = {complement T : T in Tr(C_sigma)}`.

For an upward target W:

`exists response. W`

iff

`exists a in A_sigma. W(a)`.

Hence a theory plugin can expose **canonical maximal response actions** rather than a flat complete-type set.

This is analogous to antichain state-space compression, but on the action/type-extension side.

## 11. Generalization target

For relational structures beyond graphs, define a response conflict hypergraph whose vertices are independently selectable positive incidences of the new element and whose hyperedges are minimal jointly inconsistent incidence sets.

If legality is monotone/downward in this incidence order, the same blocker duality applies.

The hard model-theoretic question becomes:

> when can complete response extensions be coordinatized by independently selectable incidences so that all inconsistency is captured by a finite conflict hypergraph?

ABA, Rado fresh adjacency, and monotone graph ages all have such coordinatizations; DLO uses a chain rather than a set-system coordinate geometry.

## 12. Next tests

1. Build explicit Henson H_3/H_4 response-antichain generators and compare against complete one-point type enumeration.
2. Measure maximal-response width on random finite K_n-free bases.
3. Exploit fixed conflict rank n-1 with modern transversal enumeration.
4. Add symmetry quotienting of the conflict hypergraph before dualization.
5. Determine whether response-antichain width predicts synthesis cost better than total one-point type count.

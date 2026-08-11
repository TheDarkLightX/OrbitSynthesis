# Paper 2 candidate: Extremal and Obstruction-Width Synthesis over Homogeneous Infinite Structures

**Status:** research outline. The central theorem schema is derived; novelty relative to infinite-domain synthesis/model theory still requires a focused literature review.

## Working thesis

For reactive synthesis over infinite homogeneous / omega-categorical structures, the complexity of **response extension geometry** can matter more than the total number of complete types.

A useful hierarchy is:

1. one greatest legal response type;
2. a small antichain of maximal legal response types;
3. exponentially many maximal responses but a compact conflict hypergraph/circuit;
4. bounded-width knowledge-compilable response constraints;
5. general finite complete-type game.

This paper would develop the mathematical theory behind levels 1-4 and classify standard structures/fragments.

## 1. Generic finite extension fibers

Fix a partial/base type sigma. Let `Ext(sigma)` be the finite set of complete response extension types.

The baseline is omega-categoricity: `Ext(sigma)` is finite.

The new question is structural:

> what order/algebra/constraint geometry does `Ext(sigma)` carry, and how succinctly can legal response subfamilies be represented?

## 2. Greatest-extension theorem

Let legal responses form a finite preorder with computable greatest legal element g, and let Good be upward.

Then

`exists legal e. Good(e)  iff  Good(g)`.

This elementary order theorem becomes a synthesis theorem when the response order is induced uniformly/effectively by complete extension types.

### Consequence

System existential choice disappears from CPre for the upward fragment; synthesis reduces to environment-only box/modal model checking.

## 3. Fragment-specific extension semilattices

A sufficient mechanism is a finite join-semilattice on extension types such that legal response sets are subsemilattices.

The legal join of all responses is then the canonical greatest action.

Crucially this is a **type-level, fragment-specific** semilattice and need not be a global polymorphism of the base structure.

## 4. Standard-structure classification

### Equality

One-point types over b distinct parameters form a star semilattice:

- equality types E_i below;
- fresh type F on top.

Conjunctions of equality/disequality literals either pin one equality type or leave F as greatest response.

Positive freshness/disequality objectives are upward.

### Dense linear order

One-point types over a finite tuple form a finite chain of equality points and gaps.

Every satisfiable legal subset has greatest and least elements.

Upward order objectives use the greatest response; downward objectives use the least.

### Rado graph, fresh response

Fresh types are adjacency subsets of the finite base, a Boolean cube under union.

Conjunctive adjacency/nonadjacency constraints produce an interval

`R subseteq N subseteq A\F`

with greatest response `A\F`.

### Atomless Boolean algebra

Response support types form the much richer cell-support semilattice studied in Paper 1.

### Henson K_n-free graph

Fresh neighborhoods must avoid an `(n-1)`-clique. Legal neighborhoods are not union-closed; a base `(n-1)`-clique gives the minimal dominant-response obstruction.

## 5. Monotone graph-class classification

For a graph class K closed under deleting edges, fresh legal neighborhoods form a downward set family.

### Theorem

The following are equivalent:

1. every fresh extension family is union-closed;
2. every fresh extension family is a Boolean cube `P(U_G)`;
3. every minimal forbidden graph of K has maximum degree <=1.

This gives an exact graph-theoretic classification of the dominant-response property in monotone graph classes.

## 6. One-point obstruction incidence width

Generalize from graphs to relation-monotone finite relational classes.

For a minimal forbidden structure H and distinguished response element v, count independently selectable positive relation incidences involving v.

Define

`omega_1(K)=max one-point incidence count over minimal forbiddens`.

Then:

- `omega_1<=1` exactly yields unique greatest-response cubes;
- general finite `omega_1=r` yields a response conflict hypergraph of rank <=r.

This parameter measures the arity of local response incompatibility.

## 7. Maximal-response antichain theorem

For any finite downward legal response family L and upward target Good,

`exists legal e. Good(e)`

iff

`exists maximal legal m. Good(m)`.

Thus when no greatest response exists, synthesis still needs only the canonical antichain `Max(L)`.

## 8. Conflict hypergraph / transversal duality

If legal response codes are subsets avoiding minimal conflicts C, then maximal legal responses are complements of minimal transversals of C.

This imports hypergraph-dualization structure directly into response synthesis.

### Henson specialization

For H_n, C is the `(n-1)`-clique hypergraph of the old graph.

Maximal fresh neighborhoods are complements of its minimal hitting sets.

## 9. Exponential response-width lower bound

Use base

`G_m=m K_(n-1)`.

Then H_n has exactly

`(n-1)^m`

maximal fresh response types.

So fixed obstruction rank does not imply a polynomial number of canonical actions.

However the conflict hypergraph is m disjoint edges/hyperedges and has a linear-size factorized description.

## 10. Response knowledge compilation

Legal responses are a CNF over incidence bits:

`AND_conflict OR NOT x_v`.

Upward target obligations add positive clauses.

Use established bounded-incidence-treewidth knowledge compilation / QBF projection results to avoid response enumeration when the conflict formula is structurally narrow.

For the disjoint-clique Henson lower bound, maximal-action width is exponential but incidence treewidth is constant.

This demonstrates why **response circuit complexity** is a more faithful parameter than response count.

## 11. Synthesis hierarchy

Proposed canonical hierarchy:

### Level 0 — dominant response

One maximal response. CPre becomes box.

### Level 1 — bounded response antichain

Finite small action set.

### Level 2 — factored conflict family

Potentially exponentially many maximal responses, compact CNF/d-DNNF/SDD.

### Level 3 — bounded structural width

Compile/project by tree decomposition or knowledge compilation.

### Level 4 — general hypergraph dualization

Use transversal/SAT algorithms.

### Level 5 — complete type game

Fallback when no useful extension geometry is detected.

## 12. Relation to polymorphisms / CSP theory

Global polymorphism identities are central to omega-categorical CSP tractability.

A semilattice polymorphism can imply response closure in some fragments, but the OrbitSynthesis extension order is more local:

- depends on a base type;
- depends on response fragment/polarity;
- may exist even without an obvious global semilattice polymorphism.

The research question is to characterize implications between:

- polymorphism identities;
- one-point obstruction width;
- extension semilattice structure;
- response circuit complexity;
- reactive synthesis tractability.

## 13. Strong negative example

Henson graphs are free-amalgamation homogeneous structures, yet dominant neighborhood union fails.

Therefore free amalgamation alone is not the synthesis criterion.

The relevant obstruction is local multi-incidence incompatibility at the new response point.

## 14. Potential general theorem target

A mature theorem might say:

> For an effectively omega-categorical structure with an effective response-incidence presentation, positive reactive synthesis is parameterized by the circuit/obstruction complexity of its one-point extension fibers. Unique extrema yield synthesis-to-model-checking collapse; bounded conflict rank yields bounded-rank response CSPs; bounded incidence width yields fixed-parameter response projection.

Every adjective in this statement needs a precise definition before publication.

## 15. Novelty questions to resolve

1. Has one-point extension geometry been used as a parameter in reactive synthesis?
2. Does model-theoretic literature already name the union-closed / extremal extension-fiber property?
3. Are there existing forbidden-structure characterizations equivalent to the monotone graph theorem?
4. Can polymorphism clone results imply our extension-semiltattice conditions automatically in major reduct classes?
5. How much of the response-conflict reduction is already implicit in infinite-domain CSP propagation?

## 16. Candidate titles

- *Extremal Response Types in Reactive Synthesis over Homogeneous Structures*
- *One-Point Obstructions and Reactive Synthesis over Infinite Structures*
- *From Greatest Extensions to Conflict Hypergraphs: A Theory of Reactive Response Compression*

The third title best captures the current hierarchy.

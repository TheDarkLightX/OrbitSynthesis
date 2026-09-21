# Extremal synthesis from semilattice-closed response fibers

**Status:** DERIVED finite-order criterion; CSP/polymorphism context is classical. The purpose is to identify a reusable sufficient condition behind ABA's dominant response and connect it carefully to the omega-categorical polymorphism frontier.

The strongest ABA synthesis simplification discovered so far is:

> for every environment observation, one greatest legal system response dominates every other legal response for upward objectives.

This note isolates an algebraic sufficient condition for the same phenomenon.

## 1. Finite response-fiber semilattice

Fix one environment/partial state observation p.

Let

`E_p`

be the finite set of abstract system response codes/types compatible with p.

Assume E_p carries a binary operation

`join : E_p x E_p -> E_p`

that is:

- associative;
- commutative;
- idempotent.

Define the induced partial order

`x <= y iff join(x,y)=y`.

Then every finite nonempty subset has a join.

## 2. Legal responses closed under join

Let

`Legal_p subseteq E_p`

be the response codes satisfying the permanent transition constraints.

Assume:

`x,y in Legal_p => join(x,y) in Legal_p`.

Since E_p is finite, if Legal_p is nonempty then

`top_p := join of all x in Legal_p`

belongs to Legal_p and is its greatest element.

## 3. Upward objective collapse

Let W be an objective/target predicate on responses that is upward in the induced order:

`x in W and x <= y => y in W`.

### Theorem 1 — greatest-witness principle

If Legal_p is nonempty, then

`exists x in Legal_p. x in W`

iff

`top_p in W`.

### Proof

The reverse direction is immediate.

For the forward direction, choose x in Legal_p intersect W. By construction `x<=top_p`; upwardness gives `top_p in W`.

This is the abstract algebraic core of the ABA maximal-support theorem.

## 4. Conjunctions of join-preserved constraints give join-closed legal sets

Suppose each transition constraint relation C on response codes is preserved by join:

`C(x) and C(y) => C(join(x,y))`.

Then any conjunction of such constraints defines a join-closed Legal_p.

Therefore the greatest-witness theorem applies automatically.

## 5. Polymorphisms as a sufficient source of closure

For a relational structure M, a polymorphism is an operation on M preserving every basic relation coordinatewise.

Suppose M has an idempotent semilattice polymorphism `join_M` and a legal response relation is primitive-positive definable from relations preserved by it.

Take two concrete legal response tuples sharing the same parameter/environment tuple a. Idempotence gives

`join_M(a,a)=a`,

so coordinatewise join keeps the fixed parameters unchanged. Polymorphism preservation keeps the joined response legal.

Thus concrete legal-response sets are semilattice-closed.

If the response/type abstraction is compatible with this operation and the relevant objective fragment is upward under the induced response order, Theorem 1 yields a canonical greatest response.

### Important scope

This is a **sufficient** condition. It is not claimed necessary, and it is not a proposed CSP dichotomy criterion.

The omega-categorical CSP literature shows that tractability is governed by much subtler polymorphism-clone identities/topology in general.

## 6. ABA is similar but not literally this polymorphism argument

For the full Boolean-algebra signature with complement, ordinary BA join

`x OR y`

is not a homomorphism/polymorphism of all BA operations in the naïve relational/algebraic sense required above.

ABA's useful semilattice lives instead on the **extension support codes**:

- a response code is a set of active fine Venn cells;
- join is set union;
- zero/equation legality is downward/avoidance based and union of individually legal responses over a fixed partial support remains legal only after restricting to the common allowed-cell universe;
- atomlessness realizes the union support as a concrete BA element.

So ABA supplies a **type-fiber semilattice** even when no global semilattice polymorphism of the full BA signature is being invoked.

This distinction should be preserved in any general theorem.

## 7. Random graph example: positive fresh-adjacency fragment

Let R be the Rado/random graph and fix a finite tuple of old vertices a.

For a fresh new vertex y, its one-point extension type is determined by the subset

`N_y subseteq a`

of old vertices adjacent to y.

The Rado extension property realizes every subset N_y.

Order codes by inclusion and use union as join.

Then:

- extension codes form the full Boolean semilattice `P(a)`;
- top is adjacency to every old vertex;
- every positive formula built monotonically from edge atoms `E(y,a_i)` is upward.

Therefore existential choice in this positive fresh-adjacency fragment is witnessed by an all-adjacent fresh vertex.

This is a direct non-ABA instance of the extremal-synthesis criterion.

The Rado graph is the Fraisse limit of all finite graphs and is omega-categorical/homogeneous.

## 8. Random relational structures

More generally, for the Fraisse limit of all finite structures in a finite relational vocabulary, the fresh one-point extension code records the truth values of finitely many relation atoms involving the new point and old parameters.

In the unconstrained random structure those local relation bits can be chosen independently.

Hence the extension-code space is a Boolean cube, union/OR is a semilattice join, and the all-true code is a top response for the positive atomic fragment.

This suggests a family of omega-categorical theory plugins with the same dominant-response phenomenon as ABA, though with different code geometry.

## 9. Henson graphs show why free/homogeneous is not enough

In the countable homogeneous K_n-free Henson graph, a fresh vertex's allowed neighborhood among old vertices cannot contain a `(n-1)`-clique, otherwise adding the new vertex creates a forbidden K_n.

Two individually admissible neighborhoods can have a union containing such a clique.

Therefore admissible one-point extension codes are not generally closed under union and need not possess a top.

So:

`homogeneous + omega-categorical`

does not imply the extremal-response property.

The forbidden-configuration geometry matters.

## 10. Equality and dense order: fragment dependence

### Pure equality

One-point extensions include mutually exclusive equality choices `y=a_i` plus a fresh type. There is no single extension satisfying all positive equality atoms.

But a **disequality-only/freshness fragment** has a canonical fresh witness distinct from every old parameter.

### Dense linear order `(Q,<)`

The full one-point type space consists of equality positions and open cuts; there is no top satisfying both arbitrary lower-bound and upper-bound demands.

However, a one-sided fragment containing only lower-bound atoms `a_i<y` has a canonical top-like witness: choose y above all finitely many parameters. Dually an upper-bound-only fragment has a bottom-like witness.

Thus extremal synthesis is a property of

`(theory, response encoding, allowed formula polarity)`,

not of the theory alone.

## 11. Connection to the omega-categorical CSP frontier

For finite and omega-categorical relational structures, primitive-positive definability and polymorphism preservation are deeply linked. Modern infinite-domain CSP classifications are organized around polymorphism clones and identities such as pseudo-Siggers conditions, with important subtleties absent in finite domains.

Relevant primary context:

- Barto & Pinsker, *The algebraic dichotomy conjecture for infinite domain Constraint Satisfaction Problems*, arXiv:1602.04353.
- Bodirsky, Mottet, Olsak, Oprsal, Pinsker, Willard, *omega-categorical structures avoiding height 1 identities*, Trans. AMS 2021 / arXiv:2006.12254.
- Mottet, *Promise and Infinite-Domain Constraint Satisfaction*, CSL 2024.

OrbitSynthesis should therefore ask a synthesis-specific question rather than importing the CSP dichotomy wholesale:

> Which polymorphism/type-fiber operations make reactive response fibers admit computable extremal witnesses for useful temporal fragments?

## 12. Candidate classification program

For an effectively omega-categorical M:

1. enumerate/represent one-point or bounded-block response types;
2. search for an effective semilattice/join operation on each response fiber;
3. prove closure of the legal-transition fragment under join;
4. identify the maximal upward formula fragment preserved by the order;
5. test whether environment extensions have a dual minimal/cofinal family;
6. derive the resulting CPre algebra;
7. compare complexity with generic complete-type synthesis.

Test structures first:

- equality;
- DLO;
- Rado graph;
- random directed graph/hypergraphs;
- Henson graphs;
- ABA;
- finite products of these where ocLTL applies.

## 13. Stronger abstract target

The finite semilattice theorem suggests a possible source of tractable synthesis classes:

`factorized finite type fibers + effective semilattice closure + upward temporal predicates`.

This is stronger than omega-categoricity but far weaker/more local than requiring a global semilattice polymorphism of the entire theory.

The next mathematical task is to determine when such a type-fiber semilattice is induced by a genuine polymorphism, when it exists only at the orbit/type level (as in ABA), and whether this distinction predicts synthesis complexity.

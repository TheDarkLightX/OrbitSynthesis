# Deterministic ABA clause games with adversarial inputs: graph-period theorem

**Status:** DERIVED reduction to exact-length reachability plus standard finite-digraph periodicity; strongly-connected cyclic-class consequences derived; literature novelty of the synthesis application not established.

This generalizes `ABA_FUNCTIONAL_CLAUSE_GAMES.md` from one deterministic map to a family of deterministic maps indexed by environment input labels.

## 1. Deterministic transition equation

Let S be the n=`2^k` Boolean state-cell labels and I the finite Boolean input-label set.

Assume the transition equation forces a unique output/next label

`delta_u(a) in S`

for every current state label a and input label u.

There is therefore no controller choice at the Boolean-label level; the controller is the term-defined deterministic transition.

For every target B subseteq S, the cube predecessor is

`P(B) = {a : for every u in I, delta_u(a) in B}.`

Since every delta_u is total,

`P(S)=S`.

## 2. Union transition graph

Build the directed graph D on S with edge

`a -> b`

iff

`b=delta_u(a)`

for at least one input label u.

Define ordinary existential graph predecessor

`R(B) := {a : exists edge a->b with b in B}.`

Then

`P(B)=S \ R(S\B)`.

### Theorem 1 — iterate duality

For every t>=0,

`P^t(B) = S \ R^t(S\B).`

### Proof

P is `complement o R o complement`. Since complement is an involution,

`P^2 = c R c c R c = c R^2 c`,

and induction gives the result.

Thus inequation-hit propagation is exactly the complement of **exact-length reachability** in the unlabeled union graph. Input labels disappear from the orbit analysis once D is built.

## 3. Transition inequation injection

Let transition inequation i have full-cell support G_i on deterministic triples `(a,u,delta_u(a))`.

For it to be guaranteed against every possible input label inside one active state region, define the robust current hit set

`C_i := {a : for every u, (a,u,delta_u(a)) in G_i}.`

Because A=S is invariant, the clause recurrence injects C_i every round and propagates old hits by P.

Hence the candidate temporal obligations are

`P^t(C_i)=S\R^t(S\C_i)`.

## 4. Boolean adjacency matrix formulation

Let M be the n x n Boolean adjacency matrix of D.

`R^t(B)` is the set of row indices having a 1 in `M^t` in some column from B.

Therefore every eventual-periodicity theorem for Boolean matrix powers immediately bounds the ABA hit recurrence.

Let

- `kappa(D)` be an index/transient after which the support pattern of M^t is periodic;
- `pi(D)` be the eventual period.

Then every hit orbit `P^t(C_i)` is periodic after kappa with period dividing pi.

### Corollary 1 — generic deterministic-input bound

The direct clause fixed point stabilizes no later than

`kappa(D)+pi(D)`

rounds after all distinct transient/periodic phases have been injected, and before canonical subsumption stores at most

`q (kappa(D)+pi(D))`

raw temporal obligations.

This uses the standard matrix-power index/period as a synthesis parameter rather than inventing a new graph invariant.

## 5. Strongly connected period-d case

Assume D is strongly connected with period d, the gcd of its directed cycle lengths.

There is a unique cyclic partition

`S = C_0 disjoint-union ... disjoint-union C_(d-1)`

such that every edge goes from C_i to C_(i+1 mod d).

For sufficiently large t, every vertex in C_i has a path of length exactly t to every vertex in

`C_(i+t mod d)`,

and to no vertex in a different cyclic class. This is the standard eventual support pattern of powers of an irreducible Boolean matrix.

### Theorem 2 — eventual hit formula

For every H subseteq S and every sufficiently large t,

`P^t(H)
 = union { C_i : C_(i+t mod d) subseteq H }.`

### Proof

By Theorem 1, a state a lies in P^t(H) iff **no** length-t path from a ends in `S\H`, equivalently every length-t endpoint lies in H.

For large t, if a lies in C_i, the set of length-t endpoints is exactly the whole cyclic class `C_(i+t mod d)`. Therefore a is retained iff that entire class is contained in H. The criterion is constant across source class C_i.

## 6. Primitive mixing kills proper persistent hits

A strongly connected digraph is primitive iff its period is 1.

Then there is only one cyclic class, namely S itself. Theorem 2 gives, for every proper H subsetneq S,

`P^t(H)=empty`

for all sufficiently large t.

### Corollary 2 — primitive impossibility

In a total deterministic-input ABA safety game, if D is primitive and some persistent transition inequation injects a proper robust hit set

`empty != C_i subsetneq S`,

then the greatest winning region is empty.

The recurrence eventually generates the empty hit constraint, which no complete ABA support can satisfy.

### Interpretation

Primitive mixing means that from every Boolean state label, the environment has exact-length words reaching every Boolean label after enough steps. A proper inequation witness set cannot be guaranteed forever by any nonempty support ensemble.

This is not merely an algorithmic shortcut; it is a semantic unrealizability criterion.

## 7. Periodic SCCs explain surviving obligations

For strongly connected period d>1, a proper hit H can survive indefinitely only through whole cyclic classes.

If H contains no entire cyclic class, Theorem 2 again gives

`P^t(H)=empty`

for all sufficiently large t, so the safety game is unrealizable once that hit is persistent.

If H contains one or more entire cyclic classes, its eventual predecessor orbit is just a rotation of those classes through the d phases.

Thus after the transient, each inequation contributes at most d phase obligations before subsumption.

## 8. Directed cycle and Landau extremes

A directed n-cycle is strongly connected of period n and has singleton cyclic classes. Every nonempty hit is a union of whole cyclic classes, so obligations can rotate without dying.

A permutation is a disjoint union of directed cycles. Its period is the lcm of those cycle lengths. Maximizing that lcm gives the Landau-function lower bound in `ABA_CLAUSE_WORST_CASES.md`.

Hence:

- primitive/mixing graph: proper persistent hit dies;
- large-period permutation graph: proper hits can have long incomparable orbits.

The same classical graph period explains both extremes.

## 9. Practical algorithm

For deterministic Tau safety specifications:

1. compile the Boolean cell transition functions delta_u;
2. construct or symbolically analyze the union graph D;
3. compute SCCs and their periods;
4. before hypergraph fixed-point iteration, apply quick unrealizability tests:
   - in a primitive SCC relevant to all winning cells, a proper persistent hit cannot survive;
   - more generally, test whether a hit contains required cyclic classes;
5. use matrix-power index/period bounds to cap hit-orbit exploration.

The 2024/2025 digraph-complexity literature shows that graph period and index-of-convergence questions have well-developed algorithms; OrbitSynthesis should reuse them rather than rederive generic matrix theory.

## 10. Scope

This theorem assumes the transition equation makes the Boolean-label next state deterministic. With controller choice among several labels, P is `forall input / exists output` and cannot in general be reduced to powers of one ordinary adjacency graph.

That nondeterministic-controller case remains governed by the general monotone map P from `ABA_CLAUSE_SAFETY_RECURRENCE.md`.

## 11. Next research target

For deterministic-with-input specifications whose union graph is reducible, derive a compositional SCC theorem:

- characterize which SCC/cyclic-class hit patterns survive;
- propagate obligations along the condensation DAG;
- combine known Boolean-matrix convergence bounds with the canonical hit antichain;
- test whether this yields a polynomial-time backend for bounded-period SCC decompositions.

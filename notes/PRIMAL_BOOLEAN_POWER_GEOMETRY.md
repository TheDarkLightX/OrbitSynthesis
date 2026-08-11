# Support and synthesis geometry of atomless Boolean powers of finite primal algebras

**Status:** DERIVED synthesis-oriented generalization from classical Boolean-power representation and homogeneity of the countable atomless Boolean algebra. Universal-algebra/model-theory ingredients are classical; the synthesis package is under novelty review.

Let P be a finite primal algebra of cardinality n>=2, and let B be the countable atomless Boolean algebra.

Let

`D = P[B]`

be the Boolean power of P by B. Concretely, an element of D is a P-labeled finite Boolean partition of 1, equivalently a continuous locally constant map from the Stone space of B to the finite discrete set P.

The Boolean algebra case is P=2.

## 1. Joint support of a tuple

For a k-tuple

`a=(a_1,...,a_k) in D^k`,

let

`Supp(a) subseteq P^k`

be the set of local label tuples that occur on a nonzero Boolean region.

Equivalently, for every `v=(v_1,...,v_k) in P^k`, intersect the Boolean regions on which `a_i=v_i`; v belongs to the support iff that intersection is nonzero.

The support is always nonempty.

### Lemma 1 — every nonempty support is realizable

For every

`empty != S subseteq P^k`,

there is a tuple a with `Supp(a)=S`.

**Reason.** Split 1 in the atomless Boolean algebra into |S| pairwise disjoint nonzero pieces and label the pieces by the elements of S. Read off each coordinate.

## 2. Orbit classification

Two k-tuples with the same support induce two finite Boolean partitions indexed by the same nonempty label set S.

The countable atomless Boolean algebra is homogeneous: every isomorphism between finite Boolean subalgebras extends to an automorphism. Map the partition atoms with label v in the first tuple to those with label v in the second tuple and extend.

The induced Boolean-power automorphism sends one tuple to the other.

Conversely, support is invariant under automorphisms because the P labels are term-definable constants in a primal algebra and therefore cannot be permuted by an algebra automorphism.

### Theorem 1 — exact orbits

Aut(D)-orbits on `D^k` are in bijection with the nonempty subsets of `P^k`.

Hence the orbit count is

`2^(n^k)-1`.

By Ryll–Nardzewski, D is omega-categorical and

`|T_k(D)| = 2^(n^k)-1`.

This specializes to

`2^(2^k)-1`

for the countable atomless Boolean algebra.

## 3. Information-optimal support code

A support is represented by one Boolean bit for every local label `v in P^k`, so the code width is

`n^k`.

Because every nonempty support is realized, any binary injection of all complete k-types needs at least

`ceil(log2(2^(n^k)-1)) = n^k`

bits.

### Corollary 2

The local-label support vector is a minimum-width binary code for complete k-types of D.

Unlike an arbitrary binary type number, its coordinates retain the Boolean-power geometry.

## 4. Exact extension count

Fix a k-tuple with support size

`s=|S|`.

Add r new D-elements.

Inside every active old region v, the r new coordinates may realize any **nonempty subset** of the `n^r` local P^r labels, independently across old regions.

### Theorem 3

The number of complete `(k+r)`-type extensions is

`(2^(n^r)-1)^s`.

For one new D-element:

`(2^n-1)^s`.

## 5. Factorized extension relation

Let `z_v` be the old support bit for `v in P^k` and `w_(v,b)` the fine bit for

`b in P^r`.

The exact extension relation is

`Ext(z,w)
 = AND_{v in P^k}
   [ z_v <-> OR_{b in P^r} w_(v,b) ].`

This is the same local nonempty-refinement relation as in ABA, with 2 replaced by n.

Under the block-local ROBDD order

`z_v` followed by all `w_(v,b)` for one v before moving to the next v,

the local relation

`z <-> OR_{j=1}^{n^r} w_j`

has exactly

`1 + 2 n^r`

nonterminal nodes.

### Theorem 4 — exact extension ROBDD size

The whole extension relation has exactly

`n^k (1 + 2 n^r)`

nonterminal ROBDD nodes under that order.

Thus explicit extension branching may be enormous while the compatibility relation remains linear in the fine support-code width.

## 6. Equations and inequations are support constraints

Let `t,u` be terms in k variables.

Their interpretations on P give functions

`t^P,u^P : P^k -> P`.

Define the disagreement set

`D_(t,u) := {v in P^k : t^P(v) != u^P(v)}.`

Because Boolean-power operations are pointwise:

`t(a)=u(a)`

iff

`Supp(a) intersect D_(t,u) = empty`.

And

`t(a)!=u(a)`

iff

`Supp(a) intersect D_(t,u) != empty`.

So:

- an equation forbids a local-label set;
- an inequation imposes a hit requirement.

## 7. Normalized clause semantics

A finite conjunction of equations can be combined semantically into one allowed local set A, and each inequation yields a hit set H_i.

Therefore every equation/inequation clause denotes exactly

`R(A;H)
 = { empty != S subseteq A : S intersects H_i for every i }.`

Because P is primal, every subset of `P^k` is the disagreement/zero set of a suitable term equation/inequation: arbitrary local characteristic functions are term-definable.

### Theorem 5 — exact clause carrier

Over the atomless Boolean power P[B], normalized equation-plus-inequation clauses are exactly the upward-closed families of nonempty supports inside an allowed local-label set A.

The canonical prime-hit / maximal-loser / minimal-winner theory from `ABA_CLAUSE_SUPPORT_LATTICE.md` transfers verbatim with ground set `P^k`.

## 8. Clause safety predecessor transfers verbatim

Consider a causal safety game with:

- current local labels `a in P^k`;
- environment labels `u in P^p`;
- controller/next labels `v in P^k`.

Let transition equations define an allowed local triple relation L and transition inequations define hit sets G_i.

For a target clause region `R(A;H)`, define

`P_L(B)
 := {a : forall u exists v in B with (a,u,v) in L}`

and

`J_i(B)
 := {a : forall u exists v in B with (a,u,v) in L intersect G_i}`.

Exactly the proof of `ABA_CLAUSE_SAFETY_HYPERGRAPH.md` gives:

### Theorem 6 — primal Boolean-power clause recurrence

`CPre(R(A;H))
 = Canon(
     P_L(A),
     {J_i(A)}_i union {P_L(H) : H in H}
   ).`

The proof uses atomlessness of the Boolean skeleton B to realize all finitely many allowed local output labels simultaneously inside every active state/input region.

## 9. Maximal-response strategy

At a nonempty fixed point `(A_*,H_*)`, define

`V_(a,u)={v in A_* : (a,u,v) in L}`.

In each nonzero Boolean region carrying local state/input label `(a,u)`, realize **all** labels in `V_(a,u)` on nonzero subregions.

The same argument as in the ABA case proves this maximal local refinement simultaneously satisfies:

- transition equations;
- transition inequations;
- next allowed set A_*;
- every fixed-point hit obligation.

Thus the clause game has a memoryless **support policy** plus an effective finite partition-witness problem in the Boolean skeleton.

## 10. Equation-only theorem is stronger and needs no atomlessness

If there are no inequations, only one output label per local `(a,u)` needs to be chosen. Primality term-defines the finite positional strategy, so no Boolean-region splitting is required.

Hence `PRIMAL_ALGEBRA_SAFETY_LIFTING.md` applies to **every** algebra in V(P), not merely atomless Boolean powers.

The atomless hypothesis enters precisely when several nonzero witness labels may need to coexist inside one region.

## 11. Worst-case lower bounds transfer

Because P is primal:

- every local transition relation L can be represented equationally;
- every local hit set can be represented by an inequation.

Therefore the Sperner and Landau constructions from `ABA_CLAUSE_WORST_CASES.md` transfer with

`N=|P|^k=n^k`

local state labels.

One inequation can force a canonical hit antichain of size

`binom(N,floor(N/2))`,

and deterministic permutation dynamics can force Landau-function-many temporal obligations.

So the structural backend remains parameterized rather than universally polynomial.

## 12. Direct ocLTL consequence

For the countable atomless Boolean power D=P[B]:

- `|T_1|=2^n-1`;
- `|T_2|=2^(n^2)-1`;
- `|T_3|=2^(n^3)-1`.

Generic ocLTL type enumeration therefore grows extremely fast even for small n.

But support codes use only:

- `n^2` bits for a `(m,x)` type;
- `n^3` bits for `(m,x,y)`;

and restriction is the local OR projection

`z_(m,x) <-> OR_y w_(m,x,y)`.

This creates a whole explicit family of omega-categorical data domains where Asor's abstract finite-type reduction can be compiled through structure-preserving support coordinates.

## 13. A concrete n=3 research instance

Take any 3-element primal algebra, equivalently a suitable 3-dimensional Boolean-like algebra / functionally complete algebra.

Then:

- `T_1`: `2^3-1=7` types;
- `T_2`: `2^9-1=511` types;
- `T_3`: `2^27-1=134,217,727` types;
- support-code widths: 3, 9, 27 bits respectively;
- one-variable extension ROBDD from k retained local coordinates:
  `n^k(1+2n)` = `7*3^k` nodes.

This is an excellent stress case: explicit `T_3` is already enormous, while structural compatibility is tiny.

## 14. Relationship to current universal-algebra literature

Modern nBA / semi-primal work explicitly presents Boolean powers as P-valued clopen partitions over Boolean skeletons and recovers Foster's theorem for primal algebras. Recent filtered-Boolean-power work also proves omega-categoricity for broad finite-algebra Boolean powers under hypotheses.

Those algebraic facts are prior art.

The candidate synthesis contribution is to use this geometry as the finite carrier for:

- exact causal safety lifting;
- clause-hypergraph fixed points;
- support-coded ocLTL compilation;
- explicit complexity/lower-bound analysis.

## 15. Next frontier

1. Implement and exhaustively validate the n=3 support geometry / safety lifting on finite Boolean powers.
2. Determine whether the countable atomless Boolean power of every finite **semi-primal** algebra still admits a support carrier with a restricted strategy clone.
3. Characterize synthesis complexity by the clone of term functions when P is not primal.
4. Check whether this leads naturally to a hierarchy:
   primal -> semi-primal/quasi-primal -> general finite generator,
   with progressively less local strategy freedom.
5. Search universal-algebraic automata/control literature before claiming this hierarchy as new.

# Positive fixed-point calculus on the zero-safe ABA cell arena

**Status:** DERIVED algebraic closure theorem. Reachability/Büchi strategy extraction and executable differential tests are next. Standard modal μ-calculus game fixed-point formulas are classical; the candidate contribution is the exact ABA antichain representation and theory-specific CPre implementation.

The earlier safety work used one canonical support clause

`C(Z;H)`.

After the zero/equation arena is fixed at

`A*=V\Z*`,

the positive family H is much more expressive than it first appears:

> it canonically represents **every upward-closed property of nonempty state supports inside A***.

This extends the support backend beyond safety.

## 1. Upward support properties

Let A be a finite allowed cell set and let

`Sigma_A = P(A) \ {empty}`

be the valid complete supports inside A.

A family

`W subseteq Sigma_A`

is **upward closed** if

`S in W and S subseteq T subseteq A`

implies

`T in W`.

Every conjunction of disequation obligations is upward closed: once a support hits every required set, activating more allowed cells cannot hurt.

## 2. Positive-clause representation is complete for upward families

For a family H of nonempty masks `H subseteq P(A)`, define

`Phi_H
 = { S in Sigma_A : for every h in H, S intersect h != empty }`.

### Theorem 1 — every upward family has a positive CNF

For every upward-closed W:

- if W is empty, use distinguished False;
- otherwise W=`Phi_H` for a finite antichain H.

### Construction

Let M be the inclusion-maximal supports in `Sigma_A \ W` (the maximal false supports).

For each `M in M`, create the clause

`h_M := A \ M`.

Because A itself belongs to every nonempty upward family W, each maximal false M is a proper subset of A and h_M is nonempty.

Then

`S in W`

iff

`for every maximal false M, S intersects A\M`.

This is exactly `Phi_H`.

After removing redundant supersets, H is the canonical positive antichain from `CANONICAL_SUPPORT_CLAUSES.md`.

Thus positive support clauses are not merely a small syntactic subclass: at fixed A they are the standard finite monotone-Boolean-function representation by prime positive clauses.

## 3. Lattice order

For normalized antichains H and K, semantic implication is

`Phi_H subseteq Phi_K`

iff

for every `k in K` there exists `h in H` with

`h subseteq k`.

A smaller obligation mask is stronger because it is harder for a support to hit.

This gives efficient subset tests by mask containment.

## 4. Conjunction

`Phi_H AND Phi_K`

is represented by

`Meet(H,K)=Min_subset(H UNION K)`.

This is the existing clause-conjunction operation.

## 5. Disjunction stays in the same representation when A is fixed

Use distributivity:

`(AND_{h in H} Hit(h))
 OR
 (AND_{k in K} Hit(k))`

is equivalent to

`AND_{h in H, k in K} [Hit(h) OR Hit(k)]`.

But

`Hit(h) OR Hit(k) = Hit(h UNION k)`.

Therefore:

### Theorem 2 — join formula

For non-false positive clauses over the same allowed arena A,

`Phi_H OR Phi_K
 = Phi_{Join(H,K)}`

where

`Join(H,K)
 = Min_subset({h UNION k : h in H, k in K}).`

Conventions:

- H empty represents Top; Top OR anything = Top;
- distinguished False OR Phi_K = Phi_K.

The pairwise product can be much larger than either input family; closure does not imply cheapness.

## 6. Why different zero masks break the one-clause form

The fixed-A condition is essential.

Take A={a,b}.

- branch 1 forbids a and allows only support `{b}`;
- branch 2 forbids b and allows only support `{a}`.

Their union is

`{{a},{b}}`

but excludes `{a,b}`.

No upward property inside the common allowed arena `{a,b}` can do that.

Thus arbitrary disjunction of clauses with different zero masks leaves the fixed-A monotone lattice.

This identifies the correct boundary:

> upward objectives **inside a permanent zero-safe arena** remain closed; introducing new branch-specific zero/equation restrictions does not.

## 7. CPre maps upward properties to upward properties

Freeze the zero-safe arena A* and Step's zero relation as in `ABA_CELL_GAME.md`.

Let B be the fixed positive Step seed family on state cells and let

`barL : P(A*) -> P(A*)`

be the robust target predecessor.

For a positive antichain H, the exact support predecessor is

`CPre_pos(H)
 = Min_subset(B UNION {barL(h): h in H})`,

with False if any required mask becomes empty.

This is the same transform proved for safety clauses.

Because every upward property has such an H, CPre is now an exact operation on the entire finite lattice `Up(Sigma_A*)`.

### Maximal-support explanation

If **some** allowed system response produces a next support in an upward target W, then taking **all** allowed fine response cells produces a next support that contains the witness next support and therefore also lies in W.

So one maximal response simultaneously satisfies every prime positive clause of W.

This is why CPre of an arbitrary upward property reduces clausewise rather than requiring branch search.

## 8. Antichains form a finite distributive-lattice presentation

Upward-closed families of subsets of a finite set form a finite distributive lattice under union/intersection.

The canonical H antichains give a concrete representation of that lattice:

- meet = antichain-minimized family union;
- join = antichain-minimized pairwise set union;
- bottom = False;
- top = empty obligation family.

This is closely related to the classical antichain representation of monotone Boolean functions / free distributive lattices. The abstract lattice is not novel.

The OrbitSynthesis contribution under test is that ABA CPre has an exact mask operation inside this lattice.

## 9. Reachability closure

Let Target be an upward state-support property in the zero-safe arena, represented by antichain T.

The standard reachability winning region is

`Reach = mu X. [Target OR CPre(X)].`

Every approximant is upward and is represented by the antichain recurrence

`H_(n+1)
 = Join(T, CPre_pos(H_n))`,

starting from False.

Therefore:

### Theorem 3 — exact upward reachability calculus

Reachability with upward Target and permanent zero-safe ABA Step can be solved entirely in canonical positive support antichains without complete-type enumeration.

Join may cause combinatorial blowup; this is a closure theorem, not a polynomial complexity result.

## 10. Büchi closure

Let F be an upward Büchi target property.

The standard Büchi game fixed point can be written schematically as

`Win_Buchi
 = nu Z. mu Y.
     [(F AND CPre(Z)) OR CPre(Y)]`.

(Exact predecessor/player conventions should match the implementation arena; the standard nested μ/ν form is intended.)

Every operation in this formula is one of:

- antichain meet;
- antichain join;
- ABA positive CPre;
- least/greatest fixed point in a finite lattice.

Hence:

### Theorem 4 — upward Büchi stays in the antichain lattice

For an upward Büchi target F on the fixed zero-safe ABA arena, every nested fixed-point approximant remains an upward support property representable by a canonical positive antichain.

The same observation applies to any positive modal μ-calculus expression built from upward atomic predicates, AND, OR, and the ABA controllable predecessor.

## 11. Positive modal μ-calculus fragment

Define formulas from:

- upward atomic support predicates;
- fixed-point variables interpreted as upward properties;
- conjunction;
- disjunction;
- CPre;
- least/greatest fixed points with positive variable occurrences.

### Theorem 5 — representation closure

Every formula denotes an upward-closed support family on A* and can be evaluated exactly in the finite antichain lattice.

### Proof

Structural induction:

- atoms upward by assumption;
- meet/join preserve upwardness and have exact antichain operations;
- CPre preserves upwardness by the maximal-support theorem;
- monotone fixed-point iteration over the finite lattice remains inside it and terminates.

## 12. Constructive strategies extend beyond safety

For one CPre query against an upward target W, the same maximal-response type works:

`Q_max(P)=all zero-safe Step-allowed full cells above observed partial support P`.

If any response reaches W, Q_max does too because W is upward.

For reachability/Büchi, the strategy must additionally choose the **appropriate fixed-point/rank target** at each step so progress is guaranteed. The standard reachability/Büchi rank extracted from fixed-point iteration can provide that control layer; within each CPre call, Q_max realizes the selected upward target.

Thus theory witness selection remains simple even when temporal progress requires memory/ranks.

## 13. Complexity boundary

Let N=|A*|.

The number of possible antichains of subsets of an N-element set is governed by the Dedekind numbers and is enormous. Individual antichains can have Sperner size

`binom(N,floor(N/2))`.

Join can multiply obligation families before minimization.

Therefore the positive μ-calculus closure result does **not** imply efficient worst-case liveness synthesis.

It identifies an exact finite symbolic algebra in which further structural parameters can be exploited:

- permutation/group symmetry;
- BDD/pathwidth when appropriate;
- deterministic cell dynamics;
- orbit descriptors;
- bounded antichain width;
- structured objective predicates.

## 14. Next executable tests

1. Implement antichain Join and differential-test reachability against explicit complete-type games for d=1.
2. Implement the standard nested Büchi fixed point and compare on small explicit games.
3. Verify maximal-response strategy ranks concretely in the dyadic ABA model.
4. Search for small counterexamples when Target introduces an additional zero mask, pinning the exact nonclosure boundary.
5. Determine which common Tau temporal specifications compile to upward objectives after permanent safety constraints are separated.

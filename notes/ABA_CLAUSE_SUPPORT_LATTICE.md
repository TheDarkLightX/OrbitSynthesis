# ABA clause regions as canonical upward-closed support families

**Status:** DERIVED finite support characterization; corrected after whole-fixed-point differential testing exposed the special role of the forbidden empty support. Standard monotone-Boolean / hypergraph blocker duality is used and not claimed novel.

## 1. Support universe and implicit nonemptiness

Fix k Boolean-algebra variables and let

`U={0,1}^k`, `|U|=2^k`.

A complete ABA k-type is a **nonempty** support `S subseteq U`.

A normalized clause

`f=0 AND AND_i g_i!=0`

has support semantics

`R(A;H)
 = { empty != S subseteq A : S intersects H for every H in H }`.

The nonemptiness condition is part of complete-type semantics, not normally stored as an inequation. This matters for canonicalization and hypergraph duality.

## 2. Exact semantic characterization

### Theorem 1

A nonempty family

`F subseteq P(U) \ {empty}`

is definable by one normalized ABA equation-plus-inequations clause iff, with

`A := union F`,

it is upward closed inside A:

`S in F and S subseteq T subseteq A  ==>  T in F`.

### Clause to upset

Adding allowed cells cannot destroy an already witnessed inequation, so every clause region is upward closed within A.

### Upset to clause

Consider only **valid nonempty supports**. Let

`L_valid := (P(A) \ {empty}) \ F`.

This is downward closed inside the nonempty support poset.

Let `MaxLose(F)` be its inclusion-maximal elements. For every M in MaxLose(F), define

`H_M := A \ M`.

Because M is nonempty and M!=A, each H_M is a proper nonempty subset of A.

A valid support S is winning iff it is not contained in any maximal losing support, equivalently iff

`S intersects H_M != empty`

for every M. Hence

`F = R(A; {A\M : M in MaxLose(F)}).`

If there are no valid losing supports, F is simply every nonempty subset of A and no explicit hit is needed.

## 3. The tautological full hit

A candidate hit

`H=A`

is always true on the semantic domain because every valid S is nonempty and contained in A.

Therefore it is **not** a prime explicit inequation constraint and must be deleted during canonicalization.

This is the bug found by the end-to-end fixed-point checker: retaining H=A preserves the denoted region but makes the representation noncanonical and can delay syntactic fixed-point equality.

## 4. Unique explicit prime-hit antichain

Define

`PrimeHit(F) := {A\M : M in MaxLose(F)}`.

These are proper nonempty subsets of A and form an antichain.

### Theorem 2

For nonempty F, the pair

`(A, PrimeHit(F))`

is the unique irredundant **nontrivial explicit** positive-hit CNF representation on the domain of complete supports.

Equivalently:

- `A=union F`;
- maximal valid losing supports are unique;
- each explicit prime hit is their complement inside A.

## 5. Restoring ordinary hypergraph duality with one implicit edge

Standard hypergraph blocker/transversal duality works over all subsets, including the empty set. Our semantic domain excludes empty support.

To use the standard theory without distortion, define the **augmented hit hypergraph**

`Hbar(F) := PrimeHit(F) union {A}`.

The added edge A is not an explicit inequation: it encodes the implicit axiom `S!=empty`.

Now the inclusion-minimal winning supports are exactly the ordinary minimal transversals:

`MinWin(F) = Tr(Hbar(F)).`

Conversely, for the Sperner clutter Hbar,

`Hbar(F) = Tr(MinWin(F))`.

Recover the explicit prime-hit representation by deleting the distinguished implicit edge A.

### Top-region example

If F is every nonempty subset of A, then

`PrimeHit(F)=empty`

but

`Hbar(F)={A}`.

Its minimal transversals are exactly the singleton subsets of A, which are indeed the minimal complete supports in the top region.

This is why applying blocker duality directly to the empty explicit hit family was incorrect.

## 6. Three equivalent extremal views

Every nonempty clause region therefore has:

1. **PrimeHit(F):** nontrivial support sets every winning type must hit;
2. **MaxLose(F):** maximal valid losing supports, with `MaxLose={A\H : H in PrimeHit}`;
3. **MinWin(F):** minimal winning supports, the transversals of `PrimeHit union {A}`.

These antichains can differ greatly in size.

## 7. Representation portfolio

- Prime hits are natural for `ABA_CLAUSE_SAFETY_RECURRENCE.md`, because each hit propagates independently under P.
- Maximal losers are natural for falsifiers and exclusion witnesses.
- Minimal winners may be useful for concrete witness enumeration.

Switching from prime hits to minimal winners is hypergraph transversal/dualization and can be expensive, so a portfolio solver needs a cost model rather than unconditional conversion.

## 8. Monotone Boolean function view

Fix A and introduce support variables z_a.

The explicit clause is

`AND_{H in PrimeHit(F)} OR_{a in H} z_a`,

but it is interpreted together with the implicit nonemptiness clause

`OR_{a in A} z_a`.

Thus clause regions are exactly monotone Boolean functions on the **nonzero** support assignments, together with the allowed-variable restriction A.

This explains both the antichain representation and its worst-case size.

## 9. Dedekind/Sperner warning

For n=|A|, upward-closed support families live at the Dedekind-number scale. A largest antichain has

`binom(n, floor(n/2))`

members by Sperner's theorem.

Since n=`2^k`, exact clause representations can be enormous in k. The direct backend is a structural/parameterized method, not a universal succinctness theorem.

## 10. Why the reactive recurrence is still special

The safety backend does not apply arbitrary monotone-Boolean transformations. It has the structured recurrence

`A_(t+1)=P(A_t)`

and

`H_(t+1)=CanonHits(P(A_t), J(A_t) union P[H_t]).`

Each old prime hit is transported independently by one finite cube predecessor P; q transition inequations inject only q candidates per iteration before tautology deletion and subsumption.

That dynamical restriction is the right place to seek practical or parameterized bounds.

## 11. Established antichain methods

Antichains are standard in monotone verification/games, and modern implementations combine them with SAT, tries, and subsumption. OrbitSynthesis should reuse those techniques.

The candidate contribution here is not antichains themselves but the ABA-specific support semantics and predecessor transform that land exactly in this lattice.

## 12. Useful canonical operations

For explicit PrimeHit:

- restrict every hit to A;
- empty hit => empty region;
- hit equal to A => delete as implicit-nonemptiness tautology;
- remove duplicates;
- remove supersets of smaller hits;
- compare canonical A and sorted hit antichain for semantic equality.

When hypergraph duality is needed, temporarily add the implicit edge A, perform standard blocker/transversal operations, then remove A again from the explicit prime-hit side.

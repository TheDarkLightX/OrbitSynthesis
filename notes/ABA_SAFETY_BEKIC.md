# Bekić decomposition of the ABA clause safety fixed point

**Status:** DERIVED theorem using the standard Bekić fixed-point principle plus the support-clause calculus. Extensively randomized against the ordinary exact clause fixed point in private research execution; a repository oracle accompanies this note. Lean formalization pending.

This note sharpens `ABA_SAFETY_CLAUSE_FIXEDPOINT.md`.

The central structural fact is that the safety operator is **triangular**:

- the equation/zero component of the next winning region depends only on the previous equation/zero component;
- the disequation/positive component may depend on both.

This permits a two-phase greatest-fixed-point computation.

## 1. Cell maps

Let:

- `V` = state support cells;
- `P` = `(state,input)` support cells;
- `U` = `(state,input,next)` support cells.

Let the cell projections be

`n : U -> V`   (next-state coordinate),

`s : U -> P`   (forget system/next coordinate),

`e : P -> V`   (forget environment input).

For a map `p:X->Y`, use the powerset adjoints from `TYPE_ADJOINT_CALCULUS.md`:

`p_!(A)=p[A]`

and

`p_*(A)={y : p^{-1}(y) subseteq A}`.

## 2. Step and safety clauses

Write

`Step = C(Z_T; H_T)`

and

`Safe = C(Z_S; H_S)`.

For a candidate state clause

`W=C(Z;H)`,

the full forbidden mask used in `Step AND W(next)` is

`F_Z := Z_T UNION n^{-1}(Z)`.

Notice that **H does not occur in F_Z**.

## 3. Zero component

Existential system projection turns a fine forbidden set F into

`s_*(F)`:

a partial cell is forbidden iff every system refinement is forbidden.

Universal environment projection then turns that into

`e_!(s_*(F))`:

a state cell is forbidden iff some environment refinement is forbidden.

After conjunction with Safe, define

`f(Z)
 := Z_S UNION e_!(s_*(Z_T UNION n^{-1}(Z))).`

### Theorem 1 — zero triangularity

For every non-false clause W with forbidden mask Z, the forbidden mask of

`Safe AND CPre(W)`

is exactly `f(Z)`, independent of W's positive obligations.

The map f is monotone under subset inclusion.

### Corollary 1 — zero fixed point

Starting from `Z_0=empty`, iterate

`Z_(k+1)=f(Z_k)`.

The chain is increasing and stabilizes at the least fixed point

`Z* = mu f`.

Because V is finite, there are at most `|V|` strict increases.

The corresponding allowed state-cell set is

`A* := V \ Z*`.

In semantic winning-set order, A* is the greatest zero/allowed component.

## 4. Why Bekić applies

Represent a support-clause property redundantly as a pair

`(A,R)`

where:

- A is the set of allowed support cells;
- R is an upward-closed positive property of supports;
- the represented models are nonempty supports `S subseteq A` satisfying R.

The safety operator induces a monotone map on this product lattice of the form

`F(A,R) = (a(A), g(A,R))`,

because the allowed/equation component ignores R.

The standard Bekić principle for greatest fixed points of monotone maps on product complete lattices therefore gives

`nu F = (A*, nu R. g(A*,R))`,

where A* is first solved independently.

Equivalently in forbidden coordinates, compute Z* first and then freeze it while solving the positive component.

Bekić's theorem is classical; this decomposition is an application of it to the support-clause safety operator, not a new fixed-point principle.

## 5. Positive transform at fixed Z*

Freeze `Z=Z*` and write

`F* := Z_T UNION n^{-1}(Z*)`.

For any positive fine-cell obligation `K subseteq U`, define

`T(K)
 := e_*( s_!( K \ F* ) ).`

Interpretation:

1. remove fine cells forbidden by Step or the next winning zero mask;
2. existentially project allowed witnesses through the system choice;
3. universally require every environment refinement to have such a witness.

### Step seeds

Each positive Step obligation `K in H_T` contributes the state obligation

`T(K)`.

Safe contributes its positive masks `H_S` directly.

Define the seed family

`B := H_S UNION {T(K): K in H_T}`.

### Previous-winning obligations

For a state obligation `G subseteq V`, its pullback to next-state fine cells is `n^{-1}(G)`.

Define the unary obligation transformer

`L(G) := T(n^{-1}(G)).`

Then, apart from canonical normalization and the distinguished False case, the fixed-Z* positive update is

`H -> B UNION {L(G): G in H}`.

## 6. Normalized transformer

All positive masks are interpreted relative to A*.

Define

`barL(G) := L(G) INTERSECT A*`.

Two identities explain why canonical antichain reduction is safe:

### Lemma 2 — forbidden-cell invariance

`barL(G)=barL(G INTERSECT A*)`.

Reason: next-state cells outside A* are already removed by `F*` before existential projection.

### Lemma 3 — validity is stable

`barL(A*)=A*`.

Reason: `Hit(A*)` is tautological for a nonempty next support avoiding Z*. Its predecessor is exactly the zero-feasible state region; intersecting with the final allowed region A* leaves A*.

### Lemma 4 — monotonicity

If `G subseteq H`, then

`barL(G) subseteq barL(H)`.

This follows because inverse image, set difference by fixed F*, direct image, and right image are all monotone in the positive set.

Consequently:

- intersecting obligations with A* does not lose future consequences;
- dropping the tautological obligation A* is safe forever;
- if G is kept and a superset H is removed as redundant, every future `barL^t(H)` remains redundant relative to `barL^t(G)`.

## 7. Distinguished False bottom

A critical subtlety: the positive component needs a distinguished bottom `False`.

If any required positive mask becomes empty after restriction to A*, the support clause is unsatisfiable. `False` is absorbing under the semantic safety operator.

It cannot be represented merely as an ordinary antichain paired with the same Z*.

### Failed first formulation

An initial implementation omitted this bottom state. On a small d=1 example it produced a spurious two-cycle:

`ordinary obligations -> False -> ordinary obligations`.

The second transition was an implementation error: once the winning region is False, pulling it into Step makes the full relation False, so the operator remains False.

This counterexample is retained as negative knowledge rather than hidden.

## 8. Orbit-closure theorem

Normalize the seed family B relative to A*:

- replace every mask by intersection with A*;
- if any becomes empty, the result is False;
- drop A*;
- remove duplicate masks and inclusion supersets.

Assume the result is non-false and call its antichain `B_min`.

For each seed `b in B_min`, follow its finite orbit

`b, barL(b), barL^2(b), ...`

until a mask repeats.

If any orbit reaches the empty mask, the winning region is False.

Otherwise let

`O := UNION_{b in B_min} {barL^t(b) : t>=0}`

with A* itself omitted as tautological.

Because the mask universe is finite, every orbit eventually repeats and O is finite.

### Theorem 2 — positive greatest fixed point

If no orbit reaches the empty mask, the positive component of the greatest safety fixed point is exactly the inclusion-minimal antichain

`H* = Min_subset(O)`.

Hence the final winning clause is

`W* = C(Z*; H*)`.

### Proof sketch

Let `Norm` denote canonical positive antichain normalization relative to A*.

Starting from positive top `H_0=empty`, the fixed-Z iteration is

`H_(n+1)=Norm(B UNION barL[H_n])`.

Let

`O_n = UNION_{b in B_min, 0<=t<n} barL^t(b)`.

Using Lemmas 2–4:

- removing forbidden cells commutes with future barL;
- dropping A* never creates a future nontrivial obligation;
- removing a superset H in favor of G subseteq H remains sound after applying barL because `barL(G) subseteq barL(H)`.

Therefore

`H_n = Norm(O_n)`

by induction.

Finite O_n eventually stabilizes to O, yielding the stated fixed point. Because this is iteration from positive top, it is the greatest positive fixed point for frozen A*, and Bekić gives the greatest full safety fixed point.

## 9. Individual obligation orbits need not converge

Do **not** replace orbit closure by a per-obligation fixed-point computation.

The monotone map barL can have cycles among incomparable masks.

Random exact searches found:

- 2-cycles already for d=1;
- 3-cycles for d=2;
- 4-cycles for d=3.

This is compatible with monotonicity: monotone maps on a powerset lattice can permute incomparable elements.

The correct algorithm follows each orbit until **repetition**, not until `barL(G)=G`.

## 10. Algorithm

### Phase I — zero attractor

Iterate f from empty until Z* stabilizes.

Cost: at most `|V|` strict zero-mask growth steps.

### Phase II — obligation orbits

1. compute A*=V\Z*;
2. compute normalized seed antichain B_min;
3. for each seed, iterate barL until a repeated mask;
4. if an empty mask occurs, return False;
5. collect all nontrivial orbit masks;
6. return their inclusion-minimal antichain.

The seeds are independent except for final antichain minimization, so their orbit exploration is embarrassingly parallel.

## 11. Complexity

Let

`N=|V|`

be the number of state support cells.

The zero phase has at most N strict additions.

A single obligation orbit has at most `2^N` distinct masks in the worst case, because barL is a deterministic map on `P(V)`. Thus the crude worst-case positive bound remains exponential:

`O(|B_min| 2^N * cost(barL))`.

The theorem is therefore a **decomposition and representation result**, not a polynomial-time claim.

Possible improvements come from:

- short empirical orbit periods;
- antichain pruning;
- structural restrictions on Step;
- graph-width/locality of the cell maps;
- symbolic cycle detection.

## 12. Strategy consequence

`ABA_SAFETY_STRATEGY.md` chooses the maximal allowed full response support

`Q_max(P)=fiber(P) \ F*`.

Notice that this response mask depends on Z* and Step's zero constraints, but not on the positive fixed-point antichain H*.

The positive phase determines **which** state/input types are winning; once a partial type is winning, all allowed fine cells form a witness for every positive obligation.

This further exposes the triangular structure:

- zero phase defines the local response envelope;
- positive orbit phase certifies recurring hit obligations;
- concrete output is realized from the maximal response type by Asor's effective extension-witness interface.

## 13. Validation performed

The corrected two-phase solver was compared against ordinary whole-clause greatest-fixed-point iteration on randomized exact clause games:

- 20,000 d=1 tests after fixing the False-bottom bug;
- 5,000 `(d=1,e=2)` tests;
- 3,000 `(d=2,e=1)` tests;
- 2,000 packed `(d=2,e=2)` tests;
- 500 `(d=3,e=1)` tests.

The independent orbit-closure implementation was then compared again on:

- 10,000 `(d=1,e=1)`;
- 5,000 `(d=1,e=2)`;
- 5,000 `(d=2,e=1)`;
- 3,000 `(d=2,e=2)`;
- 1,000 `(d=3,e=1)`.

No mismatches were found in those bounded tests.

These are falsification results, not substitutes for the proof.

## 14. Literature positioning

Bekić decomposition of simultaneous monotone fixed points is classical. Official Isabelle/HOL libraries include a `Bekic's Theorem` section for complete lattices, and the principle is standard in recursion/fixed-point theory.

The candidate OrbitSynthesis contribution is the discovery that the ABA support-clause safety operator has exactly the triangular form needed for Bekić, followed by the further reduction of its positive component to finite independent obligation orbits.

## 15. Next questions

1. Characterize barL orbit lengths for structured Tau transition clauses; the generic `2^N` bound is likely very pessimistic.
2. Determine whether barL belongs to a known semigroup class under additional Step restrictions (idempotent, eventually periodic with bounded period, closure/interior operator, etc.).
3. Formalize Bekić decomposition independently of ABA, then instantiate the support-clause operator.
4. Benchmark two-phase solving against ordinary clause iteration and Tau's current fixed-point machinery.
5. Extend from safety to richer objectives; disjunction/least-fixed-point operations will likely require a richer representation than one support clause.

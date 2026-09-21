# Phase 2 theorem / conjecture ledger — cell-game synthesis

This ledger begins after the support-type / quantifier-elimination results in `research/CONJECTURES.md`.

Statuses:

- **DERIVED** — complete paper proof in repository, not necessarily Lean-checked.
- **BOUNDED-CHECKED** — independent finite/random executable falsification passed for the stated range.
- **CLASSICAL+SPECIALIZED** — mathematical principle is established literature; ABA specialization/algorithmic use is ours to evaluate.
- **CONJECTURE** — not proved.
- **NEGATIVE** — counterexample/lower bound established.

## P2-B1 — ABA clause safety reduces to a finite cell game

**Status:** DERIVED + BOUNDED-CHECKED.

For d state BA coordinates, e environment coordinates, d next/output coordinates, and constant-partition rank rho(C), define state/partial/full Venn-cell universes

`|V|=rho(C)2^d`,

`|P|=rho(C)2^(d+e)`,

`|U|=rho(C)2^(2d+e)`.

For conjunctive equation/disequation Step/Safe formulas, complete ABA state types are nonempty subsets of V, but the zero/equation dynamics reduce exactly to the ordinary alternating cell predecessor

`Pre(A)={v: forall p over v, exists allowed u over p with next(u) in A}`.

Positive disequations become robust-witness target sets on V.

**Mechanism:** ABA complete types are active Venn-cell supports and active coarse cells refine independently.

**Files:** `ABA_CELL_GAME.md`, `ABA_SAFETY_CLAUSE_FIXEDPOINT.md`.

**Checks:** explicit 3/15/255-type game comparison for d=e=1 passed on 200 random games; later clause-level tests cover larger d.

---

## P2-B2 — canonical support clause is closed under safety CPre

**Status:** DERIVED + BOUNDED-CHECKED.

A normalized clause is one forbidden mask Z plus an inclusion-antichain of positive hit masks H.

For

`CPre(W)=forall input. exists output,next. [Step AND W(next)]`,

pullback, conjunction, existential projection, and universal projection all preserve this representation.

Thus

`W_0=Top`,

`W_(n+1)=normalize(Safe AND CPre(W_n))`

stays in one canonical support clause until it reaches False or the greatest fixed point.

**Canonicality:** normalized mask equality is semantic equivalence inside the fragment.

**Files:** `CANONICAL_SUPPORT_CLAUSES.md`, `ABA_SAFETY_CLAUSE_FIXEDPOINT.md`.

---

## P2-B3 — Bekić decomposition of the safety fixed point

**Status:** DERIVED + heavily BOUNDED-CHECKED; Bekić principle itself CLASSICAL.

The safety operator is triangular.

Forbidden masks obey an independent monotone recurrence

`Z_(n+1)=f(Z_n)`.

Compute first

`Z*=mu f`,

or equivalently the greatest allowed-cell safety set A*.

With Z* frozen, positive obligations are generated from a finite seed family B by a unary monotone target transformer `barL`.

The positive fixed point is the inclusion-minimal antichain of all finite seed orbits under barL, unless an orbit reaches empty, in which case the winning region is False.

**Critical bottom state:** False is a distinguished absorbing bottom and cannot be encoded as an ordinary antichain at fixed Z*.

**Checks:** corrected decomposition matched ordinary exact clause fixed points on tens of thousands of random games through d=3, including packed d=2,e=2.

**File:** `ABA_SAFETY_BEKIC.md`.

---

## P2-N1 — first Bekić implementation without False was wrong

**Status:** NEGATIVE / minimal counterexample retained.

The first two-phase implementation omitted distinguished semantic bottom. A d=1 game reached False in the positive phase and then incorrectly regenerated seed obligations, creating a two-cycle.

**Correction:** False is absorbing. After correction no mismatch was found in the expanded random suites.

**Lesson:** triangular coordinate formulas do not justify pretending every semantic bottom has ordinary coordinate data.

---

## P2-B4 — positive obligation map is the cell controllable predecessor

**Status:** DERIVED.

On the final zero-safe arena A*,

`barL(G)=A* intersect Pre(G)`.

Thus positive obligation dynamics are not a mysterious logical recurrence: they are repeated target-set controllable predecessor on the finite cell game.

Nontrivial cycles are therefore possible even though barL is monotone.

**Observed exact cycles:** length 2 for d=1, length 3 for d=2, length 4 for d=3 in random falsification searches.

**Files:** `ABA_CELL_GAME.md`, `ABA_SAFETY_BEKIC.md`.

---

## P2-B5 — monotone-dynamics universality

**Status:** DERIVED; prior monotone-network theory CLASSICAL.

With enough environment refinements, a single pure-ABA Step zero-equation can realize any monotone map

`F:P(V)->P(V)`

satisfying

`F(empty)=empty`, `F(V)=V`

as the cell predecessor Pre.

Construction: express each coordinate predicate `v in F(G)` as a positive CNF; environment refinements index clauses; allowed next cells are clause members; the Step equation forbids every other full minterm.

**Important correction:** an earlier version stated only top preservation. That was false because every genuine cell predecessor also maps empty to empty.

**File:** `ABA_MONOTONE_DYNAMICS_UNIVERSALITY.md`.

---

## P2-B6 — tight Sperner bound on periodic obligation dynamics

**Status:** DERIVED from classical monotone-map + Sperner arguments.

Every periodic orbit of a monotone powerset map is an antichain. Hence on N state cells

`period <= binom(N,floor(N/2))`.

The bound is tight for bottom/top-preserving monotone maps: cyclically permute the middle layer, map lower layers to empty and upper layers to V, then invoke P2-B5.

The final canonical obligation antichain can attain the same Sperner maximum.

**Caveat:** the tight construction may have a very large Step description; this is a cell-width lower bound, not a compact-source lower bound.

---

## P2-B7 — compact LFSR exponential lower bound

**Status:** DERIVED + BOUNDED-CHECKED.

Choose a primitive degree-d polynomial over GF(2). Its companion LFSR permutation fixes zero and cycles all `2^d-1` nonzero cell labels.

Encode the deterministic next relation with O(d) BA equations/XOR structure. Add one Safe disequation requiring one nonzero minterm.

Then:

- obligation period = `2^d-1`;
- ordinary fixed-point iteration has `2^d-1` strict positive strengthenings;
- final canonical clause has `2^d-1` irredundant singleton obligations.

Small-d executable checks passed for d=2..5: 3,7,15,31 strict steps.

**File:** `ABA_LFSR_LOWER_BOUND.md`.

---

## P2-B8 — deterministic/permutation fast paths

**Status:** DERIVED.

If every partial cell has one next cell and that next depends only on the current state cell via pi, then

`barL(G)=pi^{-1}(G)`.

If pi is a permutation, obligation dynamics are a cyclic group action. Compute orbit periods from the point-cycle decomposition instead of iterating logical CPre.

Singleton seed obligations reduce to a required-cell mask equal to the union of their point orbits.

**File:** `ABA_EASY_CELL_DYNAMICS.md`.

---

## P2-B9 — stutter / pin easy classes

**Status:** DERIVED.

### System-stutter

If under every environment refinement the system can remain at the current safe cell, then

`G subseteq barL(G)`.

Every later orbit mask is a superset of its seed and is antichain-redundant. Positive fixed point is just the normalized seed family.

### Environment-pin

If every cell has an environment refinement whose only safe system response is stuttering at that cell, then

`barL(G) subseteq G`.

Each seed orbit decreases and stabilizes within at most N cell removals.

**File:** `ABA_EASY_CELL_DYNAMICS.md`.

---

## P2-B10 — linear-time zero safety attractor on explicit cell incidence

**Status:** CLASSICAL finite-game algorithm + DERIVED ABA specialization.

Use one live-response counter per partial cell. When a next state becomes losing, decrement counters of transitions entering it. A partial cell spoils when its counter hits zero; its state cell then becomes losing.

Cost after cell relation generation:

`O(|V|+|P|+|U_allowed|)`.

Equation-only ABA safety synthesis therefore needs no positive phase at all and can return the allowed-cell mask A* directly.

**File:** `ABA_CELL_GAME_ALGORITHMS.md`.

---

## P2-B11 — exact S_d histogram quotient for symmetric packed specs

**Status:** DERIVED + BOUNDED-CHECKED; finite-game symmetry reduction CLASSICAL.

If Step/Safe are invariant under simultaneous permutation of d packed coordinates, the diagonal `S_d` action reduces cell counts to:

`|V/S_d| = d+1`,

`|P/S_d| = binom(d+3,3)`,

`|U/S_d| = binom(d+7,7)`.

Orbit labels are histograms of 1-, 2-, and 3-bit coordinate patterns. Projections become histogram marginalization.

Pre, zero attractor, invariant positive masks, and the maximal-support strategy descend exactly to the quotient.

**Checks:** full concrete vs histogram quotient matched for random invariant games d=1..4, including positive predecessor tests.

**File:** `ABA_SYMMETRY_QUOTIENT.md`.

---

## P2-C1 — structure-aware backend portfolio

**Status:** CONJECTURE / engineering program.

Select representation/algorithm from recognized cell dynamics:

- equation-only: queue/counter attractor;
- stutter: seed antichain only;
- pin/contractive: decreasing orbits;
- deterministic: functional graph;
- permutation/linear: algebraic group orbit;
- full symmetry: histogram quotient;
- low crossing width: ROBDD;
- general clause: mask/hypergraph + Bekić orbit solver;
- unsupported/high-cost: Tau existing path.

Measure semantic parameters rather than raw formula length alone.

---

## P2-C2 — compact symmetry detection

**Status:** OPEN.

Automatically detect a useful group action from Tau source syntax / compiled masks, or accept a declared replicated-coordinate symmetry and verify it.

First target: diagonal coordinate `S_d` symmetry.

---

## P2-C3 — extend beyond safety

**Status:** OPEN FRONTIER.

Safety works because the greatest-fixed-point step is conjunction + CPre, and one support clause is closed under those operations.

Reachability/liveness introduces disjunction and/or nested least/greatest fixed points. A single support clause is not generally closed under disjunction when branches have different forbidden masks.

Candidate next representations:

- antichain/DNF of support clauses;
- ZDD/BDD only where structural width permits;
- cell-game objective algorithms with orbit-labeled obligations;
- theory-specific abstractions that avoid explicit DNF branch explosion.

Counterexample search should precede any claim of closure.

---

## P2-C4 — generalize the cell-game factorization beyond ABA

**Status:** OPEN.

Test equality, DLO, Rado graph, and free-amalgamation homogeneous structures for an analogue of:

`complete type = admissible active local components`

with cheap left/right quantifier adjoints and a finite component game.

Do not infer this from omega-categoricity alone.

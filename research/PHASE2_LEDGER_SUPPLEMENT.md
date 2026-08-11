# Phase 2 ledger supplement — positive fixed points and extremal game semantics

This supplement **supersedes P2-C3 (`extend beyond safety`) in `PHASE2_LEDGER.md`**. The safety/liveness boundary stated there was too pessimistic.

## P2-B12 — positive antichains represent every upward support property

**Status:** DERIVED + exhaustive finite algebra check.

Fix the permanent zero-safe cell arena `A*`. Valid complete state types are nonempty supports `S subseteq A*`.

Every upward-closed family of such supports has a canonical positive-CNF / antichain representation

`Phi_H = {S : for every h in H, S intersects h}`,

with distinguished False for the empty family of models.

The canonical H consists of complements of maximal false supports, reduced to an inclusion antichain.

Lattice operations:

- meet / AND: `Min(H union K)`;
- join / OR: `Min({h union k : h in H, k in K})`;
- top: empty obligation family;
- bottom: distinguished False.

**Checks:** the OR law was exhaustively checked for every canonical upward family on 1–4 cell arenas, including all 166 canonical upward functions at 4 cells.

**File:** `notes/ABA_POSITIVE_MU_CALCULUS.md`.

---

## P2-B13 — CPre is exact on the full upward-property lattice

**Status:** DERIVED.

For any upward target W in the permanent zero-safe arena, system response existence is captured exactly by the support-clause/cell predecessor. The result is upward again.

At antichain level:

`CPre_pos(H)
 = Min(B union {barL(h): h in H})`,

with False if any mandatory obligation becomes empty.

Thus ABA CPre is an exact endomap of the finite distributive lattice of upward complete-support properties.

**Mechanism:** any witness response is contained in the greatest zero-feasible response, and upward targets are preserved by enlarging a response.

**Files:** `ABA_POSITIVE_MU_CALCULUS.md`, `ABA_EXTREMAL_RESPONSE_PRINCIPLE.md`.

---

## P2-B14 — upward reachability calculus

**Status:** DERIVED + BOUNDED-CHECKED against explicit complete-type games.

For an upward target T in the permanent zero-safe arena,

`Reach = mu X. [T OR CPre(X)]`

can be evaluated exactly by antichain meet/join/CPre operations without complete-type enumeration.

**Checks:** 5,000 random `d=e=1` games compared every symbolic least-fixed-point approximant against the explicit 3-state-type / 15-partial-type / 255-full-type game oracle. No mismatches were found.

**File / oracle:** `ABA_POSITIVE_MU_CALCULUS.md`, `experiments/aba_positive_mu_calculus.py`.

---

## P2-B15 — upward Büchi calculus

**Status:** DERIVED + BOUNDED-CHECKED against explicit nested fixed points.

For an upward Büchi target F, the standard nested game fixed point

`nu Z. mu Y. [(F AND CPre(Z)) OR CPre(Y)]`

stays in the same canonical antichain lattice.

**Checks:** 5,000 random `d=e=1` games compared every outer `nu` approximant and every nested inner `mu` approximant against explicit complete-type game semantics. No mismatches were found.

The sampled outer chains reached length 4 and inner chains length 3; these empirical lengths are not worst-case claims.

**File / oracle:** `ABA_POSITIVE_MU_CALCULUS.md`, `experiments/aba_positive_mu_calculus.py`.

---

## P2-B16 — positive modal mu-calculus closure

**Status:** DERIVED structural theorem.

After fixing the permanent zero/equation-safe arena, any formula built positively from:

- upward atomic support predicates;
- AND;
- OR;
- ABA controllable predecessor;
- least and greatest fixed points;

stays in the finite antichain lattice of upward support properties.

This includes the upward reachability and Büchi cases above and, more generally, the corresponding positive modal mu-calculus fragment.

**Boundary:** branch-specific/new zero or negative restrictions can break upward closure. A two-cell counterexample is in `ABA_POSITIVE_MU_CALCULUS.md`.

---

## P2-B17 — maximal-system / minimal-environment extremal principle

**Status:** DERIVED + BOUNDED-CHECKED.

For an observed partial support P, let

`Max(P)`

contain **every** full Venn cell above P that:

- satisfies Step's zero/equation constraints; and
- has next cell inside the permanent zero-safe arena.

Then Max(P) is the greatest zero-feasible response support.

For every upward target W:

`exists system response satisfying Step positives and W`

iff

`Max(P) satisfies Step positives and W`.

Thus the system existential quantifier has a canonical greatest witness.

The corresponding Good predicate is upward in the environment partial support. Therefore universal environment checking reduces to inclusion-minimal environment supports: exactly one input refinement per active state cell.

**Checks:**

- 5,000 random `d=e=1` games against explicit complete-type CPre;
- 2,000 `(d=2,e=1)`;
- 500 packed `(d=2,e=2)`;
- 100 `(d=3,e=1)` against exact canonical-clause CPre.

No mismatches were found.

**File:** `notes/ABA_EXTREMAL_RESPONSE_PRINCIPLE.md`.

---

## P2-N2 — `safety vs liveness` is the wrong representation boundary

**Status:** NEGATIVE / corrected claim.

The previous ledger suggested that disjunction/liveness would necessarily require a richer DNF-of-clauses representation.

That is false **once the zero-safe arena is fixed**: positive antichains are already closed under OR and represent every upward support property.

Correct boundary:

> positive/upward temporal objectives inside a permanent zero-safe arena stay in one antichain lattice; new dynamic zero/equation restrictions or other non-upward atoms may leave it.

---

## P2-C5 — reachability/Büchi strategy extraction under Tau continuation semantics

**Status:** OPEN DETAIL, not a correctness gap in the fixed-point sets.

Within every CPre call, the maximal response type is target-independent and is a valid witness whenever any upward witness exists.

For reachability/Büchi, the standard fixed-point rank/progress argument determines which predecessor target is being pursued. The concrete BA output is then obtained by realizing Max(P) through Asor's effective extension-witness interface.

Before claiming a complete Tau runtime strategy for reachability, fix Tau's exact deadlock/continuation convention: a state that has already reached a reachability target may still need an infinite legal continuation because Tau specifications execute indefinitely.

A safe formulation may combine reachability with the permanent legal-continuation/safety invariant explicitly.

# Extremal response principle for upward ABA targets

**Status:** DERIVED order-theoretic theorem; differentially checked against explicit complete-type CPre for 5,000 random d=e=1 games and against the exact clause predecessor on larger random dimensions. Concrete witness realization uses Asor's effective extension interface / the dyadic reference model.

This is the current strongest explanation of why the positive support calculus avoids search over system response types.

## 1. Fixed zero-safe arena

Use the ABA cell arena from `ABA_CELL_GAME.md`.

Let:

- V = state cells;
- P = partial `(state,input)` cells;
- U = full `(state,input,next)` cells;
- `state:P->V`, `partial:U->P`, `next:U->V`.

Let A* be the permanent zero/equation-safe state-cell arena. Let Z_T be the Step forbidden full-cell mask.

Define the zero-safe allowed full cells

`U* := {u in U : u notin Z_T and next(u) in A*}.`

By definition of A*, for every state cell `v in A*` and every partial cell p over v, there exists at least one `u in U*` over p.

Step may also contain positive/disequation obligations `K_1,...,K_q subseteq U`.

## 2. Partial support extensions

A concrete/complete state type is a nonempty support

`S subseteq A*`.

An environment partial support P extends S iff:

1. every p in P projects to a state cell in S;
2. for every v in S, P contains at least one partial cell over v.

Write

`Env(S)`

for all such P.

## 3. The greatest system response support

For a partial support P define

`Max(P)
 := {u in U* : partial(u) in P}.`

### Theorem 1 — Max(P) is the greatest zero-feasible extension

For every `P in Env(S)`:

1. Max(P) restricts exactly to P;
2. Max(P) obeys every Step zero/equation constraint;
3. its next support lies inside A*;
4. every other full support Q that restricts to P, obeys the Step zero constraints, and stays in A* satisfies

   `Q subseteq Max(P)`.

### Proof

Every active p lies above some v in A*. Zero safety guarantees at least one U* cell over p, so Max(P) restricts exactly to P.

All its cells are in U* by construction, giving 2 and 3.

Any other zero-feasible Q can contain only full cells over P that are Step-allowed and next-safe, hence only members of Max(P).

Thus the response poset has a **greatest element**.

## 4. Existential system choice collapses for upward conditions

Let W be any upward-closed property of next supports inside A*.

Say a full response Q is positively legal when it additionally hits every Step positive mask K_j.

### Theorem 2 — greatest-witness theorem

For fixed P, the following are equivalent:

1. there exists a full response Q over P such that:
   - Q obeys Step zero constraints;
   - Q hits every K_j;
   - `next(Q) in W`;
2. Max(P) hits every K_j and `next(Max(P)) in W`.

### Proof

2 -> 1 is immediate because Max(P) is itself a zero-feasible full extension.

For 1 -> 2, Theorem 1 gives `Q subseteq Max(P)`.

- every positive Step obligation is upward under support inclusion, so if Q hits K_j, Max(P) hits K_j;
- `next(Q) subseteq next(Max(P))`;
- W is upward, so `next(Q) in W` implies `next(Max(P)) in W`.

Therefore the maximal response is a witness whenever any witness exists.

### Consequence

For upward targets, the system does **not** need to search among complete response types. The existential system quantifier is evaluated by one canonical response support.

This is stronger than saying that a witness can be found effectively: the type-level witness is order-theoretically greatest and target-independent.

## 5. Monotonicity in the environment support

Fix the same current state support S. If

`P subseteq P'`

are both in Env(S), then

`Max(P) subseteq Max(P')`.

Hence, for a fixed upward target W, the predicate

`Good_W(P)
 := [Max(P) hits all Step positives
     and next(Max(P)) in W]`

is upward under inclusion of partial supports.

## 6. Minimal environment extensions

A partial support P in Env(S) is inclusion-minimal iff it contains **exactly one partial cell above every active state cell v in S**.

Call this finite family

`MinEnv(S)`.

Every P in Env(S) contains at least one member of MinEnv(S): choose one p over each active v.

### Theorem 3 — minimal-environment theorem

For every upward target W,

`for every P in Env(S), Good_W(P)`

iff

`for every P in MinEnv(S), Good_W(P)`.

### Proof

The forward direction is trivial.

For the reverse direction, take any P in Env(S) and choose minimal `P0 subseteq P`. By assumption Good_W(P0), and by upward monotonicity Good_W(P).

### Consequence

The universal environment quantifier need not range over all complete partial support types. It suffices to consider one selected input refinement per active state cell.

This is the exact dual extremal principle to the maximal system response.

## 7. CPre without type enumeration

Combining Theorems 2 and 3:

### Theorem 4 — extremal CPre formula

For an upward target W, a state support S belongs to the controllable predecessor iff

`for every P in MinEnv(S):
    Max(P) satisfies Step positives
    and next(Max(P)) belongs to W.`

No complete full response type is enumerated.

The system choice has disappeared entirely from the decision problem; only adversarial minimal environment selections remain.

## 8. Recovering the robust-witness cell transform

Take the atomic upward target

`Hit(G) := [next support intersects G]`.

For one active state cell v, define

`v in L(G)`

iff every partial cell p over v has at least one U* response into G.

### Theorem 5

For a state support S,

`for every P in MinEnv(S), next(Max(P)) intersects G`

iff

`S intersects L(G)`.

### Proof

**If.** Choose `v in S intersect L(G)`. Every minimal P contains one p over v. By definition of L(G), Max(P) contains a response from p into G.

**Only if.** If no v in S belongs to L(G), choose for each v one bad partial cell p_v with no U* response into G. The set `{p_v : v in S}` is a minimal environment extension P. Max(P) has no next cell in G.

This re-derives the positive-clause predecessor rule from an extremal-game principle rather than from formula manipulation.

## 9. Why the same maximal response works for every upward target

Max(P) depends only on:

- the observed partial support P;
- Step's zero/equation constraints;
- the permanent zero-safe arena A*.

It does **not** depend on the upward target W or on its antichain representation.

Thus every CPre query in the positive support calculus uses the same canonical type-level response function

`P -> Max(P)`.

Different temporal objectives change which states/partial supports are considered winning, but not which full response type is greatest once a CPre obligation is feasible.

This is a major simplification for synthesis implementation.

### Important semantic caveat

For reachability-like objectives, whether states that have already reached the target must still admit infinite legal continuation depends on the exact game/Tau execution semantics. The greatest-witness theorem for each CPre call is independent of that convention; do not infer a full objective-independent runtime strategy for arbitrary temporal semantics without fixing the deadlock/totality convention.

## 10. Concrete witness realization

Max(P) is a complete full support type.

Asor's effectively presented ocLTL setting provides an algorithm that, from the current concrete tuple and a compatible target complete type, computes a concrete extension witness.

Therefore a concrete system move is:

1. compute P from the actual current state/input tuple;
2. compute Max(P) by masks;
3. invoke the effective type-extension witness routine;
4. output the resulting concrete BA value(s).

`DYADIC_ABA_WITNESS.md` gives an explicit reference implementation in a concrete countable atomless BA.

## 11. Complexity of minimal environment enumeration

If the state support S contains s active state cells and there are e BA input coordinates, every state cell has `2^e` partial-cell refinements.

Therefore

`|MinEnv(S)| = (2^e)^s = 2^(e s)`.

This can still be enormous when s is large.

The robust-witness/cell-predecessor factorization avoids explicitly enumerating those minimal environment supports for positive clauses: one tests each state cell locally instead.

So Theorem 3 is primarily an explanatory extremal theorem; the cell algorithm remains the computationally preferable implementation.

## 12. Relation to order/game theory

The mechanism is an instance of a general monotonicity principle:

- system feasible responses form a poset with a greatest zero-feasible element;
- success predicates are upward, so the greatest response dominates every other response;
- environment extensions form an upward-closed poset, and the resulting success predicate is upward, so universal checking reduces to minimal elements.

What is ABA-specific is that atomlessness and Venn support factorization guarantee the greatest response exists as the union of all locally allowed refinements and is realizable as a complete type.

## 13. Validation

The extremal CPre formulation was compared against:

- explicit complete-type CPre on 5,000 random d=e=1 games (3 state / 15 partial / 255 full types);
- exact canonical-clause CPre on 2,000 random `(d=2,e=1)` games;
- 500 packed `(d=2,e=2)` games;
- 100 `(d=3,e=1)` games.

No mismatches were found in those bounded tests.

## 14. Next questions

1. Identify which non-ABA structures have a greatest compatible response type for upward objectives.
2. Characterize objective fragments whose theory predicates are upward after separating permanent zero constraints.
3. Use the extremal principle to simplify reachability/Büchi strategy extraction and prove the exact continuation convention needed for Tau.
4. Determine whether minimal environment extensions admit symmetry or product compression beyond the cellwise robust-witness transform.

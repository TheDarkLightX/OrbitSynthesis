# Dominant maximal-response strategy and box-modality collapse

**Status:** DERIVED from the extremal-response theorem. The modal/fixed-point facts about box operators are classical; the candidate contribution is the ABA-specific dominant response that turns synthesis into environment-only model checking on the upward fragment.

This note reorganizes the positive ABA synthesis results around one operator identity.

## 1. Reactive support game

Fix the permanent zero/equation-safe ABA cell arena A* and Step's zero/equation constraints.

At a complete state support S:

1. the environment chooses a partial support `P in Env(S)`;
2. the system chooses a full response support Q extending P;
3. Q must satisfy Step zero constraints and Step positive/disequation obligations;
4. the next state is `next(Q)`.

For an upward target W, the ordinary controllable predecessor is

`CPre(W)
 = {S : for every P in Env(S),
        there exists a legal Q over P with next(Q) in W}.`

## 2. Canonical maximal response

`ABA_EXTREMAL_RESPONSE_PRINCIPLE.md` defines

`Max(P)
 = every full cell above P that is Step-zero-allowed and whose next cell lies in A*.`

It proves:

- Max(P) is the greatest zero-feasible response support;
- if any response satisfies Step positives and an upward target W, Max(P) does too.

Therefore the system's existential response choice is redundant for every upward target.

## 3. Max-induced environment transition system

Define a partial transition function on environment choices:

`NextMax(P) := next(Max(P))`

when Max(P) satisfies every Step positive obligation.

If Max(P) fails a Step positive obligation, **no** legal response exists for P. Represent this by a distinguished failure state `dead`.

Define an environment-only relation R_max from state supports:

- for every `P in Env(S)` with legal Max(P), add edge

  `S -> NextMax(P)`;

- for every P with illegal Max(P), add edge

  `S -> dead`.

No system choice remains in this transition system.

The same relation can be generated using only inclusion-minimal environment supports because target goodness is upward in P, but the all-P definition is conceptually simplest.

## 4. Box operator

For a set W of ordinary state supports not containing dead, define

`Box_max(W)
 = {S : every R_max-successor of S belongs to W}.`

Equivalently, S belongs iff:

- every environment choice admits a legal maximal response; and
- every maximal-response next support lies in W.

### Theorem 1 — CPre becomes box

For every upward W,

`CPre(W)=Box_max(W)`.

### Proof

Fix S and P.

By the greatest-witness theorem:

`exists legal Q over P with next(Q) in W`

iff

`Max(P) is legal and next(Max(P)) in W`.

Apply this equivalence under the universal environment quantifier.

## 5. Complete meet preservation

The universal box modality preserves arbitrary intersections.

### Theorem 2

For every family `(W_i)` of upward target sets,

`CPre(intersection_i W_i)
 = intersection_i CPre(W_i)`.

### Proof

By Theorem 1 and elementary universal quantification:

`all successors in intersection W_i`

iff

`for every i, all successors in W_i`.

### Why this is unusual for synthesis

A generic game predecessor

`forall environment. exists system action. ...`

need not preserve intersections because different conjuncts may require different system actions.

ABA's greatest response is one action that dominates every other response for upward targets, so the existential player no longer breaks meet preservation.

This is the algebraic reason the conjunctive support calculus works.

## 6. Prime-clause propagation is just box on generators

An upward support property has canonical positive-CNF form

`W = intersection_{h in H} Hit(h)`.

By Theorem 2,

`CPre(W)
 = intersection_{h in H} CPre(Hit(h))`

plus the fixed Step-positive legality obligations.

`ABA_CELL_GAME.md` proves

`CPre(Hit(h)) = Hit(L(h))`

for the robust witness-cell predecessor L.

Therefore the entire positive-clause transform

`H -> B union L[H]`

is simply the action of a meet-homomorphism on the prime positive clauses.

This gives a shorter conceptual proof of the independent-obligation propagation used in `ABA_SAFETY_BEKIC.md`.

## 7. Safety fixed point as box-closure of seeds

Let P be the fixed positive property contributed by Safe and Step legality.

The safety operator is

`F(X)=P AND Box_max(X)`.

Since Box_max preserves intersections, iterating from top yields

`F^n(Top)
 = P
   AND Box_max(P)
   AND Box_max^2(P)
   AND ...
   AND Box_max^(n-1)(P)`.

### Theorem 3 — safety invariant as modal orbit closure

The greatest safety fixed point is

`nu X. [P AND Box_max(X)]
 = intersection_{t>=0} Box_max^t(P)`

on the finite support state space.

At prime-clause level, this is exactly the seed obligation orbit closure of the Bekić solver.

Thus the earlier Bekić/orbit theorem can also be read as a general invariant-generation identity for a box modality.

## 8. Positive mu-calculus becomes model checking under a fixed strategy

Consider any formula built from:

- upward atomic state-support predicates;
- AND / OR;
- controllable predecessor CPre;
- monotone least/greatest fixed points.

Replace every CPre by Box_max.

### Theorem 4 — synthesis/model-checking collapse

The winning set of the original ABA game for every formula in this positive modal mu-calculus fragment is exactly the denotation of the resulting ordinary modal mu-calculus formula on the environment-only transition system R_max.

### Proof

Structural induction on formulas. Atomic/Boolean/fixed-point cases are immediate. The modal case is Theorem 1. Since the semantic operators are identical at every stage, their least/greatest fixed points are identical.

## 9. Dominant strategy theorem

### Theorem 5

For the positive modal mu-calculus fragment, whenever a state is winning in the original two-player ABA support game, the type-level strategy

`after every environment partial support P, play Max(P)`

is sufficient.

No objective-specific choice among response complete types is required.

The temporal objective/rank determines **which states are winning**, but it does not change the system's selected full response type at a winning modal step.

### Constructive concrete strategy

Use Asor's effective type-extension witness routine to realize Max(P) as concrete BA output data. `DYADIC_ABA_WITNESS.md` supplies an explicit reference model.

## 10. Strategy independence needs a fixed legal-continuation semantics

The theorem is about the game/modal semantics generated by CPre and permanent Step legality.

For a Tau runtime, every execution continues indefinitely. Reachability specifications therefore need a convention ensuring that reaching the target does not excuse future transition illegality.

A clean implementation can formulate liveness **under the permanent winning continuation invariant**, or otherwise make the infinite-play/deadlock convention explicit.

Do not use Theorem 5 to bypass that semantic choice.

## 11. Environment-only transition can still be huge

System choice disappears, but R_max is not automatically small.

For a support S with s active state cells and e BA input coordinates, the number of inclusion-minimal environment partial supports is

`2^(e s)`.

The cell robust-witness representation avoids enumerating these for positive clauses, and symmetry quotients can collapse them further.

So synthesis-to-model-checking collapse is structural, not by itself a polynomial algorithm.

## 12. Connection to right adjoints

A box modality is a right adjoint and therefore meet-preserving. This connects directly to `TYPE_ADJOINT_CALCULUS.md`.

The sequence is:

1. generic first-order system existential is a left adjoint/direct image;
2. the fiberwise greatest-extension theorem evaluates that left adjoint at one maximal code on upward sets;
3. only universal environment quantification remains;
4. universal predecessor is a right adjoint/box.

This is the clean categorical explanation of the ABA positive-fragment collapse.

## 13. Generalization criterion

The same synthesis/model-checking collapse holds in any theory/encoding satisfying:

1. every system response fiber has a computable greatest admissible response;
2. the objective/transition positive predicates are upward in the response order;
3. concrete greatest response types are effectively realizable.

This is the abstract criterion in `FIBERWISE_EXTREMAL_SYNTHESIS.md`.

Equality and DLO fail the obvious greatest-extension property; a fresh-vertex positive fragment of the Rado graph has an analogous greatest adjacency response.

## 14. New implementation architecture

For the protected ABA positive fragment:

`source specification`

-> separate permanent zero constraints

-> compute zero-safe cell arena A*

-> compile one canonical Max response generator

-> discard system branching

-> solve the remaining temporal objective as environment-only symbolic model checking

-> realize Max responses concretely at runtime.

This is a much stronger design than running a generic game solver over complete theory types.

## 15. Validation basis

The modal identity is the theorem behind several independent bounded checks already performed:

- 5,000 explicit-type CPre comparisons for arbitrary upward targets at d=e=1;
- larger-dimensional exact clause-CPre comparisons;
- 5,000 reachability and 5,000 Buchi games with every fixed-point approximant compared against the explicit 3/15/255-type game oracle.

No mismatch was found in those bounded tests.

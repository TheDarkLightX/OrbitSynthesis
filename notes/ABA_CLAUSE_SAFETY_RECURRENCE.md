# Direct fixed-point recurrence for ABA clause safety games

**Status:** DERIVED from `ABA_CLAUSE_SAFETY_HYPERGRAPH.md`; bounded differential checks support the one-step theorem; end-to-end fixed-point checker pending. Literature novelty is under review.

This note makes the hypergraph predecessor theorem algorithmic by isolating the ordinary finite cube predecessor that transports both the allowed region and every inequation obligation.

## 1. Finite transition data

Let

- `S={0,1}^k` be Boolean state-cell labels;
- `I={0,1}^p` be Boolean input labels;
- `V={0,1}^k` be output/next-state labels.

A normalized ABA safety transition clause is represented by:

- an allowed triple set `L subseteq S x I x V`, coming from the transition equation;
- transition hit sets `G_1,...,G_q subseteq S x I x V`, coming from transition inequations.

A state-region approximation is represented canonically as

`R(A; H)`

where

- `A subseteq S` is the allowed state-cell set;
- `H` is an inclusion-minimal antichain of nonempty subsets of A;
- an ABA state support `T` belongs to the region iff `T subseteq A` and `T intersects H` for every `H in H`.

## 2. The ordinary cube predecessor P

Define

`P(B)
 := { a in S : for every u in I, exists v in B with (a,u,v) in L }.`

This is exactly the controllable predecessor of the finite Boolean-cube game determined by the transition equation alone.

It is monotone in B.

## 3. Transition-hit injection J_i

For each transition inequation hit set `G_i`, define

`J_i(B)
 := { a in S : for every u in I,
        exists v in B with (a,u,v) in L intersect G_i }.`

A state cell belongs to `J_i(B)` precisely when, no matter which Boolean input label the environment selects in that region, the controller has an allowed next-state label in B that also witnesses transition inequation i.

Since `L intersect G_i subseteq L`,

`J_i(B) subseteq P(B)`.

## 4. Existing target hits propagate by the same P

Let `H subseteq A` be one target hit set.

The lifted target requirement says that the next-state support must intersect H.

The hypergraph predecessor construction gives the new hit set

`{a : for every u, exists v in H with (a,u,v) in L}`,

which is exactly

`P(H)`.

Because H is contained in A and P is monotone,

`P(H) subseteq P(A)`.

This is the key decoupling.

## 5. Exact predecessor recurrence

### Theorem 1

Let `Min(.)` delete duplicate hit sets and every hit set that strictly contains another one. If any hit set is empty, the represented region is empty.

Then

`CPre( R(A; H) )
 = R(
      P(A),
      Min( {J_i(A) : 1<=i<=q} union {P(H) : H in H} )
     ).`

Thus the equation part and inequation obligations evolve by one finite monotone set transformer P plus q finite injection maps J_i.

No complete ABA type is enumerated.

## 6. Kleene iteration from the top

Initialize

`A_0=S`

and

`H_0=empty`.

The descending safety iteration is

`A_(t+1)=P(A_t)`

and

`H_(t+1)
 = Min(
     {J_i(A_t) : 1<=i<=q}
     union
     {P(H) : H in H_t}
   ).`

Stop when the canonical pair `(A_t,H_t)` stops changing.

Because the canonical pair denotes exactly the current winning approximation, this is exactly the ordinary greatest-fixed-point iteration restricted to the clause-representable sublattice.

## 7. The allowed component converges independently

The sequence A_t does not depend on any inequation.

It is exactly the equation-only finite cube safety iteration from `EQUATIONAL_SAFETY_CUBE_GAME.md`.

Therefore:

- `A_t` descends monotonically;
- it reaches the equation-only greatest fixed point `A_*` after at most `|S|=2^k` strict cell removals.

Inequations can continue to strengthen the hit antichain after A has stabilized, but they never change which individual Boolean state cells are equation-safe.

## 8. Expanded obligation history

Ignoring antichain minimization for notation, the recurrence expands as

`H_t
 = { P^(t-1-r)( J_i(A_r) )
     : 0 <= r < t, 1 <= i <= q }.`

Thus every transition inequation injects a new obligation at every time layer, and older obligations are transported one step backward by the same cube predecessor P.

This is a finite-horizon interpretation:

`P^d(J_i(A_r))`

is the set of Boolean state labels from which the controller can force an i-witness d predecessor steps later while respecting the equation-safe transition relation encoded by the relevant target set.

Antichain minimization removes semantically weaker supersets.

## 9. Maximal-response controller

Suppose the fixed point is the nonempty canonical pair

`(A_*, H_*)`.

For an actual current ABA state s in this winning region and an actual input tuple x, consider each nonzero joint `(s,x)` Venn region with Boolean label `(a,u)`.

Define the allowed output-label set

`V_(a,u)
 := { v in A_* : (a,u,v) in L }`.

Since `a in A_*=P(A_*)`, every such set is nonempty.

### Theorem 2 — maximal response is winning

A controller may, inside every nonzero joint `(a,u)` region, realize **every** label in `V_(a,u)` as a nonzero output refinement.

The union of all these local maximal refinements:

1. satisfies the transition equation;
2. makes the next-state support a subset of A_*;
3. witnesses every transition inequation;
4. makes the next-state support hit every H in H_*.

Hence it is a memoryless winning support policy.

### Proof

The first two items hold by construction.

For a transition hit G_i, the fixed-point state support must hit `J_i(A_*)`. Choose an active state label a in that hit. By definition of J_i, for every input label u there is some v in `V_(a,u)` whose full cell lies in G_i. Whatever nonempty input refinement the environment realizes inside cell a, the maximal controller includes such a v, so G_i is hit.

For a target hit H in H_*, fixed-point closure contains the predecessor requirement P(H). The current state support therefore hits P(H). On such an active state label a, every input label u has an allowed v in H. The maximal response includes it, so the next support hits H.

All hit requirements are satisfied simultaneously because atomlessness realizes all finitely many allowed local output labels at once.

## 10. A striking separation of responsibilities

The **response relation** of the maximal controller depends only on:

- the transition equation L; and
- the final allowed cell set A_*.

The inequations do not require the controller to choose a special subset of allowed labels. They determine which support states are winning through H_*, while the controller simply realizes all equation-safe output labels.

In short:

- equations determine the safe local move relation;
- inequations determine global support obligations;
- atomlessness lets the maximal local move realize all obligations simultaneously.

This is the inner structural reason the clause game remains tractable symbolically.

## 11. Concrete witness realization

Unlike the equation-only fragment, the maximal policy may need several distinct output labels to be nonzero inside the same joint `(s,x)` region.

For a region b and a finite nonempty label set V of size d, the concrete controller needs a finite partition

`b = b_1 OR ... OR b_d`

into pairwise disjoint nonzero pieces and assigns one output label to each piece.

Atomlessness guarantees such a partition for every finite d.

An effective Tau backend therefore needs a deterministic/effective split-witness routine. The abstract synthesis problem and the concrete witness-construction problem should be kept separate in the implementation and in correctness proofs.

## 12. Fixed-point implementation

For moderate k, use machine-word / bitset masks:

- A and every H are n-bit masks, `n=2^k`;
- L and G_i are masks/circuits on `2^(2k+p)` Boolean triple labels;
- P and J_i are repeated `forall input / exists output` projections;
- H is maintained as an inclusion antichain.

For larger n, switch representations only when measured structure demands it:

- ZDD for large sparse antichains;
- ROBDD for dense symbolic set maps;
- SAT/QBF projection for compact transition circuits.

The mathematical recurrence is representation-independent.

## 13. Worst-case warning

The antichain H can be very large. By Sperner's theorem it can contain

`binom(2^k, 2^(k-1))`

minimal hit sets in the worst case, and such a static clause is expressible with ordinary ABA inequations.

Moreover, P is a general monotone Boolean set transformer of the form

`a in P(B) iff AND_u OR_{v in B} L(a,u,v)`.

With enough input labels, coordinate functions of this form can express arbitrary positive CNF conditions on B. Therefore no small-orbit or polynomial-antichain bound should be assumed for unrestricted clause games.

The research target is parameterized structure, not universal compression.

## 14. Favorable subclasses to test

The recurrence exposes concrete structure that may control H growth:

1. no inequations: H stays empty, giving the `2^k`-state cube theorem;
2. nested/laminar transition hit sets;
3. deterministic or functional equation-safe transitions;
4. input-free systems, where P is ordinary existential graph predecessor;
5. bounded number q of transition inequations;
6. transition relations preserving a laminar family under P;
7. symmetric predicates whose hit orbits collapse under cell automorphisms.

These should be attacked by small exhaustive search before theorem building.

## 15. Next validation target

Implement end-to-end canonical iteration and compare its entire sequence, not only one predecessor, against explicit complete-support safety iteration for all small transition clauses where feasible.

Then measure:

- number of iterations;
- allowed-cell removals;
- raw hit count before minimization;
- canonical antichain width;
- number of distinct P-orbit masks;
- concrete maximal-response split arity.

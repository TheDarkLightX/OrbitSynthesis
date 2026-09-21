# The finite cell game underlying ABA clause safety synthesis

**Status:** DERIVED structural theorem; reorganizes the support-clause results around a finite alternating arena of Venn cells. The construction is exact for the conjunctive equation/disequation safety fragment. Literature positioning as an ABA-specific powerset lifting is still under review.

This note gives the current best "inner ground" explanation of the algorithm.

The apparent state space of complete ABA types is enormous:

`complete state types = nonempty subsets of the state Venn-cell universe V`.

If `|V|=N`, that is

`2^N-1`

complete types.

But the safety dynamics factor through an ordinary finite game on the **N individual cells**.

## 1. Cell universes

Let the reactive step use:

- d current state/memory BA coordinates;
- e environment input BA coordinates;
- d system output / next-state BA coordinates.

With a finite interpreted-constant partition of rank `rho(C)`, define:

`V = constant-regions x {0,1}^d`

for state cells,

`P = constant-regions x {0,1}^{d+e}`

for partial `(state,input)` cells,

`U = constant-regions x {0,1}^{2d+e}`

for full `(state,input,next)` cells.

Widths:

`|V| = rho(C) 2^d`,

`|P| = rho(C) 2^(d+e)`,

`|U| = rho(C) 2^(2d+e)`.

There are natural projections

`state : P -> V`,

`partial : U -> P`,

`next : U -> V`.

## 2. Zero/equation part of Step and Safe

Let

`Z_T subseteq U`

be the full cells forbidden by Step's combined equation, and

`Z_S subseteq V`

be the state cells forbidden by Safe's combined equation.

Write

`A_S = V \ Z_S`.

For a target cell set `A subseteq V`, define the cell-level controllable predecessor

`Pre(A)
 := { v in V :
      for every p in P with state(p)=v,
      there exists u in U with
        partial(u)=p,
        u notin Z_T,
        next(u) in A }.`

This is an ordinary monotone predecessor operator on the finite cell universe V.

## 3. Zero fixed point is an ordinary finite safety game

Define

`A_0=V`

and

`A_(n+1)=A_S intersect Pre(A_n)`.

### Theorem 1

If `Z_n` is the forbidden mask of the nth whole support-clause safety approximant, then

`A_n = V \ Z_n`.

Therefore

`A* = nu A. [A_S intersect Pre(A)]`

is exactly the complement of the zero fixed point `Z*` from `ABA_SAFETY_BEKIC.md`.

### Proof

A partial cell p is existentially impossible against target A iff every full refinement u over p is either Step-forbidden or has next(u) outside A.

A state cell v is universally losing iff **some** environment refinement p over v is existentially impossible.

Taking the complement gives exactly:

`v survives iff every p over v has some allowed u leading into A`.

Conjunction with Safe additionally requires `v in A_S`.

This is the standard finite safety predecessor condition.

### Consequence

The double-exponential complete-type zero game reduces exactly to a finite alternating safety game with only

`N=rho(C)2^d`

state cells.

The losing-cell attractor has at most N strict growth steps.

## 4. Why complete supports reduce cellwise for equations

A complete ABA state type is a nonempty support

`S subseteq V`.

For the equation/zero part, a support S survives one round against target allowed set A iff

`S subseteq Pre(A)`.

### Reason

The environment can refine each active state cell independently. If one active v has a bad environment cell p with no allowed system response, the environment can include that p in its partial support and defeat the support.

Conversely, if every active v is in Pre(A), then every environment refinement of every active cell has an allowed response. The system can choose compatible refinements independently inside each active cell.

Thus zero safety is **universal over the active support cells**, explaining why it is represented by one forbidden mask.

## 5. Positive obligations are robust witness cells

A disequation/positive clause does not require every active support cell to help. It requires the complete support to hit some target set.

Fix the final zero-safe arena A*.

Allowed full cells are

`U* := {u in U : u notin Z_T and next(u) in A*}`.

For a target next-state cell set `G subseteq A*`, define

`L(G)
 := { v in V :
      for every p over v,
      there exists u in U* over p with next(u) in G }.`

Then normalize to the safe arena:

`barL(G)=A* intersect L(G)`.

This is exactly the obligation transformer of `ABA_SAFETY_BEKIC.md`.

### Theorem 2 — support-level positive predecessor

For a nonempty state support `S subseteq A*`,

`for every environment partial support extending S,
 there exists a system full support whose next support hits G`

iff

`S intersect barL(G) != empty`.

### Proof

**If.** Choose a robust witness cell `v in S intersect barL(G)`. Every environment support extending S must contain at least one partial cell p over v. By definition of L(G), every such p has an allowed full refinement into G. The system includes one such refinement, so the global next support hits G.

**Only if.** If no active state cell lies in L(G), then for each `v in S` choose a bad environment refinement `p_v` over v having no allowed full response into G. Atomlessness realizes the partial support containing these chosen p_v cells. No system extension of that partial support can hit G.

The positive clause is therefore an **existential robust-witness condition on the active state cells**.

## 6. Step disequation labels

A positive Step obligation is a fine-cell set

`K subseteq U`.

Define its robust state witness set

`Seed(K)
 := { v in V :
      for every p over v,
      there exists u in U* over p with u in K }.`

Then a complete state support S can guarantee satisfaction of that Step disequation in the round iff

`S intersect Seed(K) != empty`.

Safe's state-only disequations are already witness sets in V.

Thus the positive seed family is

`B = H_S UNION {Seed(K): K in H_T}`.

## 7. The entire support winning family from the cell game

Let O be the finite orbit closure of B under barL from `ABA_SAFETY_BEKIC.md`.

Let H* be its inclusion-minimal nontrivial antichain, unless an orbit reaches the empty set, in which case the winning region is False.

### Theorem 3 — powerset-lifted winning family

If the result is non-false, the complete ABA state types that are safety-winning are exactly

`WinSupports
 = { nonempty S subseteq A* :
     for every H in H*, S intersect H != empty }.`

So the `2^N-1` complete support states are never enumerated. Their winning subset is represented by:

- the N-cell base safety winning set A*;
- a finite antichain H* of robust-witness target sets generated by the cell predecessor dynamics.

## 8. Cell-game interpretation of obligation cycles

The map barL is simply the safe cell-level controllable predecessor applied to a target set.

This explains the nontrivial cycles found during falsification:

a controllable-predecessor operator on target subsets is monotone, but its orbit on incomparable subsets need not converge pointwise.

For example, a deterministic cell transition that swaps two state cells gives

`barL({a})={b}`

and

`barL({b})={a}`.

The positive phase needs the **orbit closure**, not a fixed point of each individual target mask.

## 9. Maximal-support strategy in cell-game language

For an actual observed partial support `P0 subseteq P`, define

`Q_max(P0)
 := {u in U* : partial(u) in P0}`.

In words: activate every Step-allowed full cell above the observed environment partial support whose next cell stays in A*.

The zero-game property guarantees every active partial cell has at least one such refinement.

If the current support is winning, the robust-witness obligations guarantee that Q_max hits every Step and propagated positive target that must be hit.

Thus the maximal-support strategy is simply:

> keep **all** cell-game system moves that remain inside the zero-safe arena.

No additional tie-breaking is needed at the type level.

Asor's effective extension-witness procedure then realizes this full support as concrete BA output data.

## 10. Why the reduction is ABA-specific

The finite cell arena is not obtained merely from omega-categoricity.

It works because in atomless Boolean algebra:

1. a complete tuple type is exactly the set of active generated Venn cells;
2. every nonzero coarse cell can be refined independently into any nonempty collection of finer cells;
3. equations only remove cells;
4. disequations only require at least one active cell from a target set.

These four facts make complete-type dynamics a structured powerset lift of cell dynamics.

A different omega-categorical structure may have interactions between extension choices that prevent such independent cellwise factorization.

## 11. Complexity gap

Pure ABA, d state coordinates:

`N=2^d` cell states.

Complete state types:

`2^N-1 = 2^(2^d)-1`.

The full one-step cell universe for d environment and d next coordinates has

`2^(3d)` cells,

while complete full types number

`2^(2^(3d))-1`.

The clause safety algorithm works over the singly-exponential cell universes and mask families rather than the double-exponential complete-type game graph.

This is the cleanest current explanation of where the computational saving comes from.

## 12. Relationship to generic synthesis modulo theories

Generic synthesis-modulo-theories methods may Booleanize theory predicates, query an SMT solver, refine abstractions, or synthesize witness functions.

The cell-game theorem is more theory-specific:

- the finite base arena is derived directly from the finitely generated ABA subalgebra geometry;
- complete theory types are its nonempty powerset lift;
- the protected safety fragment can be solved exactly on the base cells plus witness-set antichains.

Whether this exact ABA reduction is novel in the literature remains a prior-art question; the underlying ideas of powerset constructions and symbolic games are classical.

## 13. Generalization criterion suggested by the theorem

For another omega-categorical theory, ask whether complete tuple types admit:

1. a finite set of local components/cells;
2. type = admissible set of active components;
3. extension = independent local refinement subject to simple constraints;
4. quantifier adjoints reducible to finite component-game operations.

This is a more concrete version of the "succinct effective type hyperdoctrine" program from `TYPE_ADJOINT_CALCULUS.md`.

## 14. Next questions

1. Characterize the dynamical complexity of the cell predecessor barL.
2. Find syntactic Step classes for which barL is extensive, contractive, idempotent, or otherwise cycle-free.
3. Derive sharp upper bounds on orbit periods using monotone-map / Sperner theory.
4. Test whether equality, DLO, or free-amalgamation structures admit analogous finite component games.
5. Build the actual clause safety solver around this cell arena and benchmark it against complete-type and Tau baselines.

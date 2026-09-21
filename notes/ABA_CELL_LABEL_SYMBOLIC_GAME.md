# ABA cell-label symbolic game: keep the Tau term circuit, not the cell table

**Status:** DERIVED representation theorem; the finite-state symbolic-game machinery is classical. The research contribution under investigation is the exact reduction from the ABA support/type game to this d-bit cell-label game and its interaction with the positive support calculus.

The earlier `ABA_CELL_GAME.md` reduced a game over complete ABA support types to a finite game on Venn cells. This note makes the next representation change:

> a Venn cell is itself only a Boolean valuation of the underlying BA coordinates.

Therefore the cell game can be represented by the original Boolean term circuits instead of enumerating its `2^d`, `2^(d+e)`, and `2^(2d+e)` cells.

## 1. Cell labels

Take

- state BA coordinates `s_1,...,s_d`;
- environment/input BA coordinates `i_1,...,i_e`;
- next/system BA coordinates `n_1,...,n_d`.

A state Venn cell is a bit vector

`v in {0,1}^d`.

A partial state/input cell is

`p=(v,a) in {0,1}^(d+e)`.

A full state/input/next cell is

`u=(v,a,w) in {0,1}^(2d+e)`.

These are exactly the minterm labels used throughout the support representation.

## 2. A Boolean-algebra term already is its cell predicate

Let

`f(s,i,n)`

be a Boolean-algebra term built from variables, `0`, `1`, meet, join, complement, and XOR/syntactic sugar reducible to them.

Evaluate the same syntax in the two-element Boolean algebra `{0,1}`. Write the resulting ordinary Boolean function as

`f^2 : {0,1}^(2d+e) -> {0,1}`.

The minterm support of f is precisely

`A_f={u : f^2(u)=1}`.

Therefore, on a complete ABA support Q,

`f(Q)=0`

iff Q contains no cell u with `f^2(u)=1`.

This is the support theorem in circuit rather than truth-table form.

## 3. Zero Step equations become a Boolean transition circuit

Suppose the zero/equation portion of Step is

`f_1=0 AND ... AND f_m=0`.

A full cell u is zero-feasible exactly when every equation term evaluates to 0 at u.

Define the Boolean transition predicate

`R(v,a,w)
 := AND_j NOT f_j^2(v,a,w)`.

Then

`R(v,a,w)=1`

iff the full Venn cell `(v,a,w)` is allowed by every Step equation.

No list of `2^(2d+e)` full cells need be constructed.

The syntax DAG/circuit for R is obtained directly from the Tau Boolean terms plus one negation per equation and one outer conjunction.

## 4. Zero Safe equations become a Boolean state predicate

If permanent state safety contains equations

`g_1(s)=0 AND ... AND g_r(s)=0`,

define

`Safe0(v)=AND_j NOT g_j^2(v)`.

The allowed state-cell fixed point is the ordinary finite safety-game greatest fixed point

`A* = nu A. [Safe0 AND Pre_R(A)]`

where

`Pre_R(A)(v)
 := forall a in {0,1}^e,
      exists w in {0,1}^d.
      R(v,a,w) AND A(w)`.

Thus the zero phase is exactly symbolic reactive safety synthesis over d Boolean state bits.

## 5. The equation-only ABA game is not double-exponential

At the complete-type level there are

`2^(2^d)-1`

possible ABA state types.

At the explicit cell level there are

`2^d`

state cells.

At the symbolic cell-label level there are only

`d`

Boolean state variables plus the source-sized circuit `Safe0,R`.

The semantic state space is still `2^d`, so no complexity miracle is claimed. The point is that **source structure is preserved** instead of being destroyed by minterm/type enumeration.

This is the standard setting in which BDD, SAT/QBF, IC3/PDR-style, interpolation, and structure-aware game algorithms become applicable.

## 6. Positive obligation masks are also Boolean functions on cell labels

A state disequation

`h(s) != 0`

requires a complete support to contain at least one cell where

`h^2(v)=1`.

So its obligation hyperedge is

`H_h={v : h^2(v)=1}`,

represented directly by the Boolean circuit h rather than by a `2^d`-bit mask.

After the zero arena is frozen, the robust target predecessor of an arbitrary cell mask G is

`L_G(v)
 := A*(v) AND
    forall a. exists w.
      R(v,a,w) AND A*(w) AND G(w)`.

If G itself has a symbolic representation, this is a quantified Boolean formula/circuit over d state bits.

Thus every positive-obligation orbit from `ABA_SAFETY_BEKIC.md` can in principle be maintained symbolically.

## 7. Dominant response is a symbolic relation too

For one observed partial cell `(v,a)`, the maximal allowed next-cell set is

`MaxNext(v,a)
 = { w : R(v,a,w) AND A*(w) }`.

This is exactly the Boolean relation

`R(v,a,w) AND A*(w)`.

For an upward target W expressed by obligation masks, the system succeeds iff every relevant minimal environment extension sees a maximal response satisfying W, as proved in `ABA_EXTREMAL_RESPONSE_PRINCIPLE.md` and `ABA_DOMINANT_STRATEGY.md`.

Hence strategy representation can stay symbolic until a concrete witness BA element must be reconstructed.

## 8. Source-structure parameters become meaningful

The reduction exposes the interaction graph of the original specification.

Useful candidate parameters now include:

- circuit/formula size of R;
- variable incidence degree;
- primal/incidence treewidth or pathwidth;
- OBDD crossing width / few-subterms count under an ordering;
- symmetry group on the d coordinates;
- deterministic/functional structure in w;
- affine/linear structure over GF(2);
- Horn/dual-Horn or other closed Boolean classes after support compilation.

These parameters can be exponentially smaller than an explicit cell table.

## 9. Relation to the OBDD results already in the repository

`ABA_EXTENSION_ROBDD.md` proved a tiny ROBDD for the **generic atomless extension relation** on support bits.

This note concerns a different level:

- support-bit BDD: Boolean variables say whether Venn cells are active in a complete type;
- cell-label BDD: Boolean variables are the labels of one Venn cell itself.

The latter has only d state variables and directly preserves the original Tau term syntax.

Both can be useful, but they solve different representation problems.

## 10. Why this does not contradict the OBDD lower bounds

`ABA_OBDD_LOWER_BOUNDS.md` embeds hard monotone CNFs in support-level properties. Likewise, arbitrary Tau Boolean terms can define Boolean functions with exponential OBDD size under every variable ordering.

So a BDD is not universally compact even at cell-label level.

The gain is that we can now inspect the source circuit before choosing a backend instead of first expanding it to `2^d` cells.

## 11. Exact compiler fast path

For a homogeneous atomless-BA clause fragment, a compiler can proceed as follows:

1. keep each equation/disequation Boolean term as a DAG/circuit;
2. form `Safe0(s)` and `R(s,i,n)` directly;
3. solve the zero safety game symbolically on d state bits;
4. compile each positive obligation as its Boolean term/circuit on state-cell labels;
5. use the structure-aware backend selected for the resulting symbolic cell game;
6. reconstruct concrete ABA outputs only after a response support/type is chosen.

This path never requires enumerating complete ABA types.

## 12. New theorem target

The central algorithmic question sharpens to:

> Which Tau source classes make the cell-label game and its positive target transforms tractable under a representation whose size is polynomial/FPT in source-level structural parameters?

This is now a source-sensitive question rather than a raw `|T_k|` question.

The first classes to test are:

1. bounded incidence/pathwidth;
2. replicated-coordinate symmetry;
3. deterministic/permutation/affine next-state relations;
4. bounded-width local terms / sparse variable incidence;
5. combinations of the above.

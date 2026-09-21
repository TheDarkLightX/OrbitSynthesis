# Fixed-point elimination over omega-categorical structures: baseline theorem

**Status:** DERIVED baseline theorem; novelty not claimed; formalization pending.

This note makes precise the observation behind the `ocLTL` conclusion that fixed-point-definable temporal fragments can be handled directly over an omega-categorical structure.

## Setup

Let `M` be a countable omega-categorical structure in a finite or countable first-order signature, and fix an arity `k`.

Let `R` be a fresh k-ary relation symbol. Let

`theta(x_bar; R)`

be a parameter-free first-order formula in which `R` occurs only positively. It induces an operator

`F : P(M^k) -> P(M^k)`

by

`F(X) = { a_bar in M^k : (M,X) |= theta(a_bar;R) }`.

Positivity of `R` implies monotonicity of `F`.

## Theorem 1 — orbit-finite fixed-point stabilization

Let `N=|T_k(M)|`, the finite number of complete parameter-free k-types of `M`. Then:

1. the least fixed point of `F` is parameter-free first-order definable;
2. the greatest fixed point of `F` is parameter-free first-order definable;
3. ascending iteration from `empty` reaches the least fixed point after at most `N` strict increases;
4. descending iteration from `M^k` reaches the greatest fixed point after at most `N` strict decreases.

## Proof

By Ryll-Nardzewski, `Aut(M)` has exactly `N` orbits on `M^k`, one for each complete k-type. Each orbit is first-order definable because every complete type is isolated.

A parameter-free definable k-ary relation is `Aut(M)`-invariant, hence is a union of these orbits. Conversely every union of the finitely many isolated orbits is first-order definable. Thus the Boolean algebra of parameter-free definable k-ary relations is canonically isomorphic to the finite powerset lattice

`P(T_k(M))`.

The operator `F` is equivariant because `theta` is parameter-free: automorphisms preserve its truth. Therefore `F` maps orbit-unions to orbit-unions and induces a monotone endomap

`F_bar : P(T_k(M)) -> P(T_k(M))`.

On a finite powerset lattice, the ascending Kleene chain

`empty <= F_bar(empty) <= F_bar^2(empty) <= ...`

can strictly increase at most `N` times because each strict increase adds at least one orbit. It therefore stabilizes at the least fixed point. The descending chain from all of `T_k(M)` is dual and stabilizes at the greatest fixed point after at most `N` strict decreases.

The resulting orbit-unions are finite unions of isolated types, hence first-order definable.

## Theorem 2 — formula-level algorithm without explicit type enumeration

Assume additionally that the first-order theory `Th(M)` is decidable effectively enough to test formula equivalence; quantifier elimination is sufficient but not necessary.

Define formulas iteratively:

`psi_0(x_bar) := false`

`psi_(n+1)(x_bar) := theta(x_bar; R := psi_n)`

where every occurrence of `R(t_bar)` is replaced by `psi_n(t_bar)` with the appropriate substitution/renaming of bound variables.

At each step, decide whether

`Th(M) |= forall x_bar. (psi_(n+1) <-> psi_n)`.

When equality holds, stop. Theorem 1 guarantees termination after at most `N` strict changes. The final formula defines the least fixed point. Start from `true` for the greatest fixed point.

This algorithm does not need to enumerate `T_k` explicitly. Quantifier elimination / normalization may be used after each iteration to control expression size.

## ABA specialization

For the atomless Boolean algebra, `N = 2^(2^k)-1`. Therefore a monotone parameter-free first-order k-ary fixed-point computation can have at most

`2^(2^k)-1`

strict orbit changes.

For `k=3`, the absolute orbit-height bound is 255 strict changes.

This is a worst-case semantic bound, not a runtime bound. Formula normalization can still blow up dramatically.

## Safety synthesis connection

A standard safety winning region has greatest-fixed-point form

`W = nu X. (Safe intersect CPre(X))`

where `CPre` is the controllable-predecessor operator. In a first-order data theory, a typical one-step predecessor has quantifier pattern analogous to

`CPre(X)(state) := forall input. exists output,next_state. Step(state,input,output,next_state) and X(next_state)`

(up to the precise game convention).

The occurrence of `X` is positive, so this is a monotone first-order operator when `Step` and `Safe` are first-order definable. Thus Theorem 1 provides the semantic termination argument over omega-categorical structures.

The actual OrbitSynthesis research problem is **not** whether this finite-lattice argument exists. It is:

> For which theories and specification classes does formula-level fixed-point iteration remain substantially smaller/faster than explicit type/orbit enumeration?

That is an algorithmic representation question.

## Falsification / caveats

Do not apply the theorem silently when:

- the fixed-point predicate occurs negatively;
- parameters are introduced without tracking parameter-orbits/types;
- the state dimension changes during iteration;
- the operator is not first-order definable;
- witness reconstruction requires data not preserved by the symbolic formula;
- equivalence checking is unavailable/effectively intractable.

The theorem proves termination/definability, not practical efficiency.

## Noether-style mechanism

The fixed point disappears into first-order logic not by magic but because omega-categoricity turns the semantic universe of parameter-free k-ary properties into a **finite Boolean algebra of orbits**. Monotone recursion cannot create infinitely many distinct orbit-unions. The hidden finiteness is the inner ground of the elimination result.

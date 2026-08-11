# Causal safety synthesis over Boolean powers of arbitrary finite algebras

**Status:** DERIVED structural theorem. This corrects an earlier over-strong use of primality: primality is NOT needed for the Boolean-power predecessor commutation itself. Classical Boolean-power / patchwork semantics are prior art; the reactive-synthesis application is under novelty review.

Let M be any finite nontrivial algebra in a finitary signature and let B be any Boolean algebra. Write

`A = M[B]`

for the Boolean power: equivalently, finitely-valued continuous maps from the Stone space X of B to the finite discrete algebra M, with operations evaluated pointwise.

No primal, discriminator, Mal'cev, lattice, or atomless assumption is needed in Sections 1–6.

## 1. Local finite safety relation

Fix:

- k state variables s;
- p environment-input variables x;
- k controller-output variables y, also used as next state.

Let E(s,x,y) be a finite conjunction of equations in the language of M.

Evaluate E in M and define the finite local safe relation

`R_E subseteq M^k x M^p x M^k`.

For `W subseteq M^k`, define

`Pre_M(W)
 := {a in M^k : for every u in M^p,
        exists v in W with (a,u,v) in R_E}.`

## 2. Lift local state sets to the Boolean power

For a state tuple

`s in A^k`,

let

`Img(s) := {s(xi) : xi in X} subseteq M^k`.

Because s is locally constant, Img(s) is finite.

For a local set W define

`Lift(W) := {s in A^k : Img(s) subseteq W}.`

This means every Stone point / Boolean region carries a local state label in W.

## 3. One-step causal predecessor commutes with Boolean power

### Theorem 1

For every finite algebra M, every Boolean algebra B, every equational local safety relation E, and every `W subseteq M^k`,

`CPre_A(Lift(W)) = Lift(Pre_M(W)).`

### Sufficiency

Assume `Img(s) subseteq Pre_M(W)` and let the environment choose an arbitrary actual Boolean-power input `x in A^p`.

The joint tuple `(s,x)` induces a finite clopen partition of X into cells

`X_(a,u) = {xi : s(xi)=a and x(xi)=u}`.

For every nonempty cell choose one local response

`v_(a,u) in W`

with `(a,u,v_(a,u)) in R_E`, possible because `a in Pre_M(W)`.

Now define y pointwise by setting

`y(xi)=v_(a,u)` on X_(a,u).

This is a finitely-valued locally constant map, hence an element of the Boolean power A. At every point E holds in M and y(xi) lies in W. Since equations in A are evaluated pointwise,

- E(s,x,y) holds in A;
- `y in Lift(W)`.

Thus s is a controllable predecessor.

### Necessity

Suppose `Img(s)` contains `a notin Pre_M(W)`. Then some local input label u has no safe response in W.

The fiber

`X_a={xi:s(xi)=a}`

is a nonempty clopen set. Choose an A-input x that is constantly u on X_a and arbitrary constant outside it. Boolean powers are closed under such clopen patching.

Any y in Lift(W) has `y(xi) in W` on X_a. By choice of u, the local equation E fails at every point of X_a for every such response. Hence no safe y exists.

## 4. Greatest-fixed-point collapse

The top local set is `M^k`, and

`Lift(M^k)=A^k`.

Iterating Theorem 1 gives:

### Theorem 2

Let

`W_* = nu W . Pre_M(W)`

be the finite local safety winning set. Then the winning region of the Boolean-power game is exactly

`Win_A = Lift(W_*).`

The local descending iteration has at most

`|M|^k`

strict state-label removals.

This theorem is set-theoretic/game-semantic. It does not say Lift(W_*) is definable by one equation in the original signature.

## 5. Positional patchwork controller

Finite safety games admit positional strategies. Let

`sigma : W_* x M^p -> W_*`

choose a safe local response.

The proof above defines a memoryless Boolean-power controller:

> on each clopen joint-label region `(a,u)`, output the constant local label `sigma(a,u)`.

This controller is always an internal A-valued response because Boolean powers have the patchwork property.

### Important distinction

The controller function

`A^(k+p) -> A^k`

need not be a **term operation of A** in the original algebraic signature.

It is a well-defined locally patched strategy. Term-definability is a separate algebraic property.

## 6. Exact role of primality

Now let P be finite primal.

Primality adds two major facts:

1. **term strategy:** every finite function `P^(k+p)->P^k`, including sigma, is coordinatewise represented by terms, so the patchwork controller collapses to ordinary algebraic terms in `(s,x)`;
2. **arbitrary local relation/set definability:** characteristic functions of arbitrary finite local subsets/relations are term-definable, so arbitrary finite safety games can be encoded equationally.

Foster's theorem adds a third:

3. **whole-variety lifting:** every algebra in `V(P)` is a Boolean power of P, so Theorems 1–2 apply to every algebra in the primal variety, not merely to a chosen Boolean power.

Thus the correct hierarchy is:

`finite M + Boolean power`  -> exact causal game lifting and patchwork strategy;

`finite primal P + Boolean power` -> plus term-definable strategy and arbitrary local equational relation;

`finite primal P + any A in V(P)` -> plus Foster gives the result for the entire variety.

## 7. Why this is stronger conceptually

The finite collapse does not come from functional completeness. It comes from the **patchwork representation**:

- equations are pointwise;
- current state/input values induce finitely many clopen local regions;
- a safe finite response can be selected independently on each region;
- clopen patching produces a valid Boolean-power element.

Primality is only what internalizes that lookup table as an ordinary term.

This is the true inner ground.

## 8. Equation-defined targets versus arbitrary lifted targets

Theorem 1 holds for every set W, even if W is not definable in M by equations or first-order formulas.

For synthesis inside a logical language, definability matters:

- in a primal algebra, every W is equation-definable by a characteristic term;
- in a non-primal algebra, the finite winning set W_* may fail to correspond to a compact/available formula in the original signature.

So realizability can collapse finitely even when symbolic winning-region elimination in the source language does not.

This distinction should be kept explicit in any comparison with Tau or ocLTL.

## 9. Inequations over an atomless Boolean skeleton

Now additionally assume B is atomless and the transition/target formula is one equation-plus-inequations clause.

For terms t,u, define the local disagreement set

`D_(t,u)={a in M^k:t^M(a)!=u^M(a)}`.

In M[B]:

- `t=u` iff the local image/support avoids D_(t,u);
- `t!=u` iff the support hits D_(t,u).

Thus a normalized clause again denotes

`R(A;H)={empty != S subseteq A : S intersects every H_i}`

on local label supports.

The proof of `ABA_CLAUSE_SAFETY_HYPERGRAPH.md` uses only:

- pointwise equation semantics;
- disagreement-set semantics of inequation;
- atomless finite splitting of a nonzero Boolean region.

Therefore it transfers to the atomless Boolean power of **any finite algebra M** for the local sets actually induced by its terms.

### Theorem 3 — arbitrary finite-algebra atomless Boolean-power clause recurrence

With local allowed relation L and local transition hit sets G_i coming from the given terms,

`CPre(R(A;H))
 = Canon(
     P_L(A),
     {J_i(A)}_i union {P_L(H):H in H}
   )`

with the same definitions of P_L and J_i as in the ABA notes.

Primality is not needed for the recurrence; it only makes **every** local A/H/L/G set term-representable.

## 10. Atomlessness boundary

Equation-only lifting never splits a joint `(state,input)` region: choose one local output label for the whole region. Hence arbitrary B works.

Clause synthesis with several inequations may need multiple distinct output labels to coexist inside the same nonzero region. The maximal-response proof achieves this by finite splitting.

So:

- equation-only safety: any Boolean skeleton;
- equation+inequation support recurrence: atomless (or enough finite divisibility for the demanded splits).

This is a structural boundary, not a technical artifact.

## 11. Validation outside the Boolean special case

`experiments/primal_n3_geometry.py` uses a three-element local carrier without any two-valued Boolean identities.

It checks:

- 100 random local safety relations on a three-point finite Boolean power: full pointwise CPre equals Lift(Pre);
- three-valued support/type/extension counts expected for an atomless Boolean power;
- 1,000 random input-free equation/inequation support games on three local state labels: explicit atomless support refinement agrees with the hypergraph CPre formula.

These are bounded independence checks, not substitutes for the general proofs.

## 12. Prior-art boundary

Boolean powers, Boolean products, and the patchwork property are classical algebraic model theory. Sequential Boolean-equation synthesis is classical from Wang / Even–Meyer in the two-valued setting.

The candidate synthesis contribution should therefore be phrased narrowly:

> identify causal safety-game predecessor/fixed-point operations that commute with Boolean-power patchwork, and exploit that commutation as a structure-preserving backend for Tau/ocLTL-style infinite data.

Do not claim Boolean powers or finite local synthesis themselves are new.

## 13. Next generalization

For general Boolean products rather than constant-fiber Boolean powers, local factors may vary across Stone points. The same proof suggests a finite family of local games glued over clopen factor regions.

Before pursuing this, check the Boolean-product / sheaf model-theory literature: this is exactly where Feferman–Vaught style decomposition may already provide the correct general theorem.

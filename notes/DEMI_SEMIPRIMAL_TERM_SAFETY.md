# Original-signature safety synthesis for demi-semi-primal algebras

**Status:** DERIVED theorem. Uses Quackenbush's classical demi-semi-primal extension property plus the classical quasi-primal term-function characterization. The orbitwise safety specialization is under novelty review.

This fills the algorithmic gap between:

- `SEMIPRIMAL_TERM_SAFETY.md`, where all strategy choices decouple locally; and
- `QUASIPRIMAL_TERM_SAFETY_CSP.md`, where arbitrary internal isomorphisms may create a full groupoid-coupled strategy CSP.

The exact intermediate object is the global automorphism group.

## 1. Demi-semi-primality

Let D be a finite quasi-primal algebra.

D is **demi-semi-primal** if every isomorphism between nontrivial subalgebras of D extends to an automorphism of D.

Quackenbush introduced the class in 1971. Intuitively, such an algebra has as many definable operations as possible subject to its subalgebras and automorphisms.

Let

`G = Aut(D)`.

## 2. Term functions need only subalgebras + global automorphisms

### Lemma 1

For finite demi-semi-primal D, a total function

`f:D^m -> D`

is a term operation iff:

1. it preserves subalgebras, equivalently
   `f(z) in Sg_D(z)` for every tuple z; and
2. it is G-equivariant:
   `f(gz)=g f(z)` for every `g in G`.

### Proof

Every term operation has both properties.

Conversely, let

`phi:S_1 -> S_2`

be an internal isomorphism and take `z in S_1^m`. By demi-semi-primality, extend phi to some `g in Aut(D)`.

Subalgebra preservation gives

`f(z) in S_1`.

Therefore

`f(phi z)
 = f(gz)
 = g f(z)
 = phi f(z)`.

So f preserves every internal isomorphism. Quasi-primality then makes f a term operation.

This derives the standard Foster-Pixley/Quackenbush characterization directly from the extension property.

## 3. Finite local safety game

Fix:

- local states `a in D^k`, with `k>=1`;
- environment inputs `u in D^p`;
- controller / next-state labels `v in D^k`;
- equation-defined safe relation
  `R subseteq D^k x D^p x D^k`.

Because R is defined by terms/equations, it is invariant under every automorphism:

`(a,u,v) in R iff (ga,gu,gv) in R`.

We seek one positional controller whose coordinates are original-signature D-terms.

## 4. Observation stabilizers

For an observation

`z=(a,u) in D^(k+p)`,

let

`G_z = {g in G : gz=z}`

be its pointwise stabilizer.

Define the stabilizer-fixed output set

`Fix_z^k
 = {v in D^k : gv=v for every g in G_z}`.

Why this condition appears:

If we choose an output v for one representative z of a G-orbit and extend equivariantly by

`sigma(gz)=gv`,

then the definition is independent of which g carries the representative to the same observation exactly when v is fixed by G_z.

## 5. Orbitwise term-admissible actions

For target state set `W subseteq D^k`, define

`Adm_W(a,u)
 := {v in W :
       (a,u,v) in R,
       every coordinate of v lies in Sg_D(a,u),
       v in Fix_(a,u)^k }.`

The generated-subalgebra condition enforces subalgebra preservation.

The stabilizer condition enforces well-defined global automorphism equivariance when one action is propagated across an observation orbit.

## 6. Demi-semi predecessor

Restrict attention to G-invariant state sets W. Define

`DPre(W)
 := {a in D^k : for every u in D^p,
       Adm_W(a,u) is nonempty }.`

### Lemma 2

If W is G-invariant, then DPre(W) is G-invariant.

### Proof

Take `a in DPre(W)` and `g in G`. For an input u at ga, pull it back to `g^(-1)u`. Choose

`v in Adm_W(a,g^(-1)u)`.

Then gv lies in W by invariance, is safe by invariance of R, lies in the generated subalgebra of `(ga,u)`, and is fixed by the conjugate stabilizer of `(ga,u)`. Thus ga belongs to DPre(W).

## 7. Exact greatest-fixed-point theorem

Start from

`W_0=D^k`

and iterate

`W_(t+1)=DPre(W_t)`.

Every W_t is G-invariant. Let W_* be the greatest fixed point.

### Theorem 1 — exact term-winning region

W_* is exactly the set of local states from which there exists a memoryless safety controller whose output coordinates are D-terms.

### Sufficiency

For each G-orbit of observations `(a,u)` with `a in W_*`, choose one representative z and one

`v_z in Adm_(W_*)(z)`.

Extend to the whole orbit by

`sigma(gz)=g v_z`.

The stabilizer-fixed condition makes this well-defined.

For observation orbits whose state is outside W_*, complete the total table arbitrarily while retaining the two algebraic constraints. This is always possible when k>=1: at a representative observation z choose, for example, its first state coordinate repeated in every output coordinate. That element lies in `Sg(z)` and is fixed by the stabilizer of z.

The resulting total sigma:

- preserves generated subalgebras;
- is G-equivariant.

By Lemma 1, every coordinate is a D-term.

On W_* it is safe and remains in W_* for every input, so it is winning.

### Necessity

Let sigma be any D-term positional controller and let `Win_sigma` be the local states from which its induced closed-loop system is safe forever against all inputs.

Because sigma commutes with automorphisms and R is automorphism-invariant, `Win_sigma` is G-invariant.

At every winning observation, sigma's output:

- lies in the generated subalgebra;
- is fixed by the observation stabilizer;
- is safe and remains inside `Win_sigma`.

Hence

`Win_sigma subseteq DPre(Win_sigma)`.

By greatest-fixed-point maximality,

`Win_sigma subseteq W_*`.

So no term controller wins outside W_*.

## 8. Orbit quotient algorithm

The theorem avoids the full quasi-primal strategy-table CSP.

Precompute:

1. G=Aut(D);
2. G-orbits on state tuples `D^k`;
3. G-orbits on observations `D^(k+p)`;
4. one stabilizer G_z per observation-orbit representative;
5. generated subalgebras `Sg(z)`.

Represent W as a set of state orbits.

For each winning observation-orbit representative z, test whether there is a safe output v satisfying:

- v's state orbit is selected in W;
- `v in Sg(z)^k`;
- `v in Fix(G_z)^k`.

One orbitwise choice can then be propagated to every observation in that orbit.

This replaces `|D|^(k+p)` independent table variables plus internal-groupoid equalities by a quotient game over global automorphism orbits.

## 9. Semi-primal special case

A semi-primal algebra has only identity internal isomorphisms. In particular its global automorphism group is trivial.

Then every stabilizer condition is vacuous and G-orbits are singletons.

`DPre` reduces exactly to the generated-subalgebra predecessor `TPre` of `SEMIPRIMAL_TERM_SAFETY.md`.

## 10. Primal special case

A primal algebra has:

- trivial automorphism group;
- no proper nonempty subalgebras.

The generated-subalgebra and stabilizer filters disappear, leaving the ordinary finite safety predecessor.

## 11. Why the Quackenbush counterexample is excluded

`QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md` uses a three-element quasi-primal Q with an internal automorphism

`phi:{0,1}->{0,1}`

that cannot be extended to an automorphism of Q; indeed `Aut(Q)` is trivial.

Thus Q is **not** demi-semi-primal.

The obstruction exploited by that game is precisely what the extension property rules out: a strategy choice is coupled by an internal symmetry that is invisible to the global automorphism group.

This makes the counterexample and Theorem 1 complementary boundary results.

## 12. Automorphism-only filtering is still not enough

Even in a demi-semi-primal algebra, it is not enough merely to quotient observations by G.

For an observation with nontrivial stabilizer, the chosen output must be fixed by that stabilizer or equivariant propagation is ambiguous.

The correct local orbit action set is therefore

`safe ∩ target ∩ generated-subalgebra ∩ stabilizer-fixed`.

This stabilizer condition is the same well-definedness constraint that appears throughout equivariant/nominal computation.

## 13. Relation to Quackenbush's characterization

Quackenbush's 1971 demi-semi-primal theory describes these algebras as having as many polynomial/term functions as possible subject to automorphisms and subalgebras.

The theorem above turns that static clone characterization into a reactive algorithm:

> quotient the safety game by global automorphisms, retain generated-subalgebra and stabilizer admissibility, and run an ordinary greatest fixed point on orbit sets.

## 14. Validation target

Use the discriminator-only algebra on a three-element set as a clean demi-semi-primal example:

- every subset is a subalgebra;
- every isomorphism between equal-size subalgebras extends to a permutation of the whole set;
- the automorphism group is S3.

Generate random equation-defined safe relations from random term-function tables and compare:

1. the DPre orbit fixed point;
2. an explicit global equivariant/subalgebra-preserving strategy-table CSP.

The two should agree for every tested instance.

## 15. Next rung

The current clone/synthesis hierarchy is now:

1. **primal:** ordinary finite safety game;
2. **semi-primal:** generated-subalgebra action-filter game;
3. **demi-semi-primal:** global automorphism-orbit game with stabilizer-fixed actions;
4. **quasi-primal:** full internal-isomorphism groupoid strategy CSP in general;
5. **general finite algebra:** full term-clone constraint problem.

The next mathematical question is whether known natural-duality/Pol-Inv descriptions give similarly finite, structured controller constraints for broader finite-algebra classes.

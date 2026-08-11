# Original-signature safety synthesis over quasi-primal algebras as a finite strategy-table CSP

**Status:** DERIVED exact reduction from Pixley's classical characterization of quasi-primal term operations. Cross-observation coupling is now PROVED NECESSARY IN GENERAL by `QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md`. The universal-algebra preservation theorem is prior art; the synthesis reduction is under novelty review.

`SEMIPRIMAL_TERM_SAFETY.md` gives a simple greatest-fixed-point operator because semi-primal term operations are exactly the subalgebra-preserving functions and the relevant choices can be made observation-by-observation.

For a general quasi-primal algebra, nontrivial internal isomorphisms can couple different table entries. The exact generic formulation is a finite constraint problem over the entire positional strategy table.

## 1. Quasi-primal preservation theorem

Let Q be a finite quasi-primal algebra.

Classically, an operation

`f:Q^m -> Q`

is a term operation iff it preserves every isomorphism between subalgebras of Q. Equivalently, it preserves the internal-isomorphism relational structure of Q.

An internal isomorphism is an isomorphism

`phi:S_1 -> S_2`

between subalgebras of Q.

Preservation means that for every tuple z in `S_1^m`,

1. `f(z) in S_1`, and
2. `f(phi(z)) = phi(f(z))`.

The first condition is obtained from the identity internal isomorphism on every subalgebra.

Older quasi-primal literature sometimes phrases the characterization using polynomial functions; modern clone formulations state it in term-function language. OrbitSynthesis should be explicit about the convention used when constants/parameters matter.

## 2. Finite local safety game

Fix:

- local states `a in Q^k`;
- environment inputs `u in Q^p`;
- controller / next-state labels `v in Q^k`;
- a safe local relation `R subseteq Q^k x Q^p x Q^k` defined by the safety equations.

We want a **single positional controller whose coordinates are Q-terms**.

Unlike ordinary finite safety games, choices at different observations cannot necessarily be combined independently because term tables must satisfy internal-isomorphism equations.

## 3. Strategy-table variables

For every complete local observation

`z=(a,u) in Q^(k+p)`

and every output coordinate `j=1,...,k`, introduce a finite-domain variable

`Y_(z,j) in Q`.

Let

`Y_z=(Y_(z,1),...,Y_(z,k))`.

These variables describe a total positional table

`sigma:Q^(k+p) -> Q^k`.

## 4. Term-clone constraints

For every internal isomorphism

`phi:S_1 -> S_2`

and every observation tuple `z in S_1^(k+p)`, impose, for every output coordinate j,

`Y_(phi(z),j) = phi(Y_(z,j))`.

Because the identity on S_1 is among the internal isomorphisms, this also forces

`Y_(z,j) in Sg_Q(z)`.

### Theorem 1 — exact table interpolation

The full table Y satisfies all these constraints iff every coordinate function

`z -> Y_(z,j)`

is a term operation of Q.

This is Pixley's quasi-primal preservation theorem applied coordinatewise.

## 5. Winning-domain variables

Introduce one Boolean variable

`W_a`

for every local state `a in Q^k`.

Interpret `W_a=true` as saying that the synthesized term controller is required to keep the safety invariant from state a.

For every state a and input u, add the guarded constraints

`W_a -> [ (a,u,Y_(a,u)) in R ]`

and

`W_a -> W_(Y_(a,u))`.

For a required initial state set I, assert

`W_a=true`

for every `a in I`.

## 6. Exact synthesis theorem

### Theorem 2

The finite CSP described above is satisfiable iff there exists a positional controller

`sigma:Q^(k+p)->Q^k`

whose coordinates are terms of Q and which wins the safety game from every required initial state in I.

### CSP -> term controller

A satisfying assignment gives a total strategy table Y. The internal-isomorphism constraints imply every coordinate is a Q-term by Theorem 1.

The true W states form a forward-invariant safe set under that table for every environment input and contain I. Hence the term controller wins from I.

### Term controller -> CSP

Given a winning positional Q-term controller, set Y to its finite table. Term operations preserve all internal isomorphisms, so the clone constraints hold.

Let W be any safe invariant domain containing I under the controller. Then the guarded safety/invariance constraints hold.

## 7. Why the global coupling is genuinely necessary

Ordinary positional strategies can be assembled state-by-state because action choices are independent.

Quasi-primal term operations may couple observations z and phi(z) through

`Y_phi(z)=phi(Y_z)`.

This is not merely a conservative complication.

`QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md` uses Quackenbush's three-element quasi-primal algebra

`Q=({0,1,2}; discriminator, u)`

with proper subalgebra `Q0={0,1}` and nonextendable internal automorphism `phi:0<->1`.

It constructs a **single-equation safety relation** for which:

- the semi-primal-style generated-subalgebra predecessor has nonempty fixed point
  `{00,10,11}`;
- every state/input observation in that fixed point has a locally generated safe successor;
- nevertheless, exhaustive internal-isomorphism table checking proves that no nonempty state domain admits an original-signature Q-term winning strategy.

The critical pair is

`((0,0),1) <-> ((1,1),0)`.

Staying inside the naive domain forces output 10 at both observations, while term equivariance forces the second output to be

`phi(10)=01`.

Thus no purely statewise/local action filter can be exact for all quasi-primal algebras.

## 8. Semi-primal simplification

A finite algebra is semi-primal iff it is quasi-primal and its only internal isomorphisms are the identity maps on subalgebras.

Then the table constraints reduce to

`Y_(z,j) in Sg_Q(z)`

with no coupling between distinct observations.

The CSP factorizes observation-by-observation, and eliminating Y yields exactly the local action-filter predecessor

`TPre`

from `SEMIPRIMAL_TERM_SAFETY.md`.

So semi-primality is not just one point on a taxonomy: it is the exact decoupling boundary for the generic preservation-based formulation.

## 9. Primal simplification

A primal algebra has no proper subalgebras and no nontrivial internal-isomorphism constraints. Every finite function is a term operation.

The strategy-table constraints disappear completely, reducing to the ordinary finite safety game.

## 10. Clone-theoretic hierarchy

The synthesis problem has a precise algebraic ladder.

### Primal

Term clone = all functions.

Algorithm: ordinary finite safety game.

### Semi-primal

Term clone = subalgebra-preserving functions.

Algorithm: ordinary finite safety game after local generated-subalgebra action filtering.

### Quasi-primal

Term clone = functions preserving internal isomorphisms.

Algorithm: finite safety invariant + globally equivariant strategy-table CSP in general.

### General finite algebra

Term clone may require preservation of a larger invariant relational structure (Pol-Inv / natural-duality data). The same table-constraint idea applies in principle, but a compact finite basis need not be available in a convenient form.

## 11. Boolean-power / Tau interpretation

For a Boolean power Q[B], arbitrary patchwork strategies are easier than original-signature term strategies: `FINITE_BOOLEAN_POWER_SAFETY.md` reduces them to the unconstrained finite local game.

If the implementation uses `TAU_FINITE_BOOLEAN_POWER_ENCODING.md`, Tau can compile **any** finite strategy table to BA representation-bit terms, bypassing the original Q-term clone.

So distinguish three controller notions:

1. arbitrary Boolean-power patchwork controller;
2. Tau/BA-representation term controller;
3. original-Q-signature term controller.

The first two can realize arbitrary local tables; the third is governed by the algebra's term clone and can fail even when the first two succeed.

The Quackenbush counterexample proves this distinction is semantic, not merely an API choice.

## 12. Solver implementation

For a fixed small Q, preprocess once:

- all subalgebras;
- all internal isomorphisms;
- observation tuples in their domains;
- induced equality/permutation constraints on strategy-table entries.

Then compile a safety game to SAT/SMT/CSP:

- finite-domain output variables Y;
- Boolean winning-domain variables W;
- clone/equivariance constraints;
- guarded transition-safety constraints;
- guarded next-state-in-W constraints;
- initial-state assertions.

Optimization can maximize `sum_a W_a` or answer realizability from a specified initial set.

Do not assume the union of all term-controllable invariant domains is itself term-controllable: global clone constraints can prevent independent controller tables from being merged.

## 13. Counterexample status

The former falsification target is now **ACHIEVED**.

Artifacts:

- `notes/QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md`
- `experiments/quasiprimal_coupling_counterexample.py`

The checker verifies:

- Quackenbush algebra structure;
- naive fixed point;
- exhaustive failure of all nonempty term-strategy domains;
- phi invariance of the 13 safe tuples;
- existence of an equation definition via functions satisfying the quasi-primal preservation criterion.

This should be promoted into any eventual theorem hierarchy because it demonstrates strict separation between semi-primal and quasi-primal synthesis algorithms.

## 14. Next structural question: demi-semi-primality

Quackenbush also studied **demi-semi-primal** algebras, where every internal isomorphism extends to a global automorphism.

The counterexample above deliberately uses an internal automorphism that does **not** extend globally.

This suggests a sharp next question:

> If every internal isomorphism extends to a global automorphism, can the quasi-primal strategy CSP be quotient-compressed to global automorphism orbits, yielding an exact orbitwise safety algorithm simpler than the full internal-groupoid CSP?

This is the most natural next rung because it attacks exactly the mechanism used by the counterexample rather than choosing an unrelated algebraic condition.

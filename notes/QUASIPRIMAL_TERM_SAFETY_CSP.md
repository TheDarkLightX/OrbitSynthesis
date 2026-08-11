# Original-signature safety synthesis over quasi-primal algebras as a finite strategy-table CSP

**Status:** DERIVED exact reduction from Pixley's classical characterization of quasi-primal term operations. The universal-algebra preservation theorem is prior art; the synthesis reduction is under novelty review.

`SEMIPRIMAL_TERM_SAFETY.md` gives a simple greatest-fixed-point operator because semi-primal term operations are exactly the subalgebra-preserving functions and the relevant choices can be made observation-by-observation.

For a general quasi-primal algebra, nontrivial internal isomorphisms couple different table entries. The right exact formulation is a finite constraint problem over the entire positional strategy table.

## 1. Quasi-primal preservation theorem

Let Q be a finite quasi-primal algebra.

Classically, an operation

`f:Q^m -> Q`

is a term operation iff it preserves every internal isomorphism between subalgebras of Q.

An internal isomorphism is an isomorphism

`phi:S_1 -> S_2`

between subalgebras of Q.

Preservation means that for every tuple z in `S_1^m`,

1. `f(z) in S_1`, and
2. `f(phi(z)) = phi(f(z))`.

The first condition is already obtained from the identity internal isomorphism on every subalgebra.

## 2. Finite local safety game

Fix:

- local states `a in Q^k`;
- environment inputs `u in Q^p`;
- controller / next-state labels `v in Q^k`;
- a safe local relation `R subseteq Q^k x Q^p x Q^k` defined by the safety equations.

We want a **single positional controller whose coordinates are Q-terms**.

Unlike ordinary finite safety games, choices at different observations cannot necessarily be combined independently because term tables must satisfy the internal-isomorphism equations.

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

This is precisely Pixley's quasi-primal preservation theorem applied coordinatewise.

## 5. Winning-domain variables

Introduce one Boolean variable

`W_a`

for every local state `a in Q^k`.

Interpret `W_a=true` as saying that the synthesized term controller is required to keep the safety invariant from state a.

For every state a and input u, add the guarded constraints

`W_a -> [ (a,u,Y_(a,u)) in R ]`

and

`W_a -> W_(Y_(a,u))`.

The second clause means the next local state remains inside the chosen invariant winning domain.

For a required initial state set I, also assert

`W_a=true` for every `a in I`.

## 6. Exact synthesis theorem

### Theorem 2

The finite CSP described above is satisfiable iff there exists a positional controller

`sigma:Q^(k+p)->Q^k`

whose coordinates are terms of Q and which wins the safety game from every required initial state in I.

### CSP -> term controller

A satisfying assignment gives a total strategy table Y. The internal-isomorphism constraints imply every coordinate is a Q-term by Theorem 1.

The true W states form a forward-invariant safe set under that table for every environment input, and contain I. Hence the term controller wins from I.

### Term controller -> CSP

Given a winning positional Q-term controller, set Y to its finite table. Term operations preserve all internal isomorphisms, so the clone constraints hold.

Let W be any safe invariant domain containing I under the controller—for example all local states from which its induced closed-loop transition is safe forever. Then the guarded safety/invariance constraints hold.

## 7. Why a CSP, not necessarily one statewise predecessor

Ordinary positional strategies can be combined state-by-state because action choices are independent.

Quasi-primal term operations may couple two observations z and phi(z) through

`Y_phi(z)=phi(Y_z)`.

Therefore the existence of a term controller from state a and from state b separately does not automatically justify independently combining the two finite tables.

The global strategy-table CSP retains exactly the coupling that a naive predecessor operator would lose.

Whether a simpler greatest-fixed-point presentation exists for important subclasses is an open question; do not assume it.

## 8. Semi-primal simplification

A finite algebra is semi-primal iff it is quasi-primal and its only internal isomorphisms are the identity maps on subalgebras.

Then the table constraints reduce to

`Y_(z,j) in Sg_Q(z)`

with no coupling between distinct observations.

The CSP factorizes observation-by-observation, and eliminating the Y variables yields exactly the local action-filter predecessor

`TPre`

from `SEMIPRIMAL_TERM_SAFETY.md`.

Thus the semi-primal fixed-point theorem is the decoupled special case of this CSP.

## 9. Primal simplification

A primal algebra has no proper subalgebras and no nontrivial internal isomorphism constraints. Every finite function is a term operation.

The strategy-table constraints disappear completely, reducing to the ordinary finite safety game.

This recovers the primal theorem.

## 10. Clone-theoretic hierarchy

The synthesis problem now has a precise algebraic ladder:

### Primal

Term clone = all functions.

Algorithm: ordinary finite safety game.

### Semi-primal

Term clone = subalgebra-preserving functions.

Algorithm: ordinary finite safety game after local generated-subalgebra action filtering.

### Quasi-primal

Term clone = functions preserving internal isomorphisms.

Algorithm: finite safety invariant + globally equivariant strategy-table CSP.

### General finite algebra

Term clone may require preservation of a larger relational structure (Pol–Inv / natural-duality data). The same idea suggests a constraint system whose table variables are restricted to the term clone, but a compact universal description need not exist.

## 11. Boolean-power / Tau interpretation

For a Boolean power Q[B], arbitrary patchwork strategies are easier than original-signature term strategies: `FINITE_BOOLEAN_POWER_SAFETY.md` reduces them to the unconstrained finite local game.

If the implementation uses `TAU_FINITE_BOOLEAN_POWER_ENCODING.md`, Tau can compile **any** finite strategy table to BA representation-bit terms, bypassing the original Q-term clone.

So there are three distinct controller notions:

1. arbitrary Boolean-power patchwork controller;
2. Tau/BA-representation term controller;
3. original-Q-signature term controller.

The first two can realize arbitrary local tables; the third is governed by the algebra's term clone.

This distinction should be explicit in any API or paper claim about synthesized controller expressibility.

## 12. Solver implementation

For a fixed small Q, preprocess once:

- all subalgebras;
- all internal isomorphisms;
- the observation tuples in their domains;
- the induced equality/permutation constraints on strategy-table entries.

Then compile a particular safety game to SAT/SMT/CSP:

- finite-domain output variables Y;
- Boolean winning-domain variables W;
- clone/equivariance constraints;
- guarded transition-safety constraints;
- guarded next-state-in-W constraints;
- initial-state assertions.

Optimization can maximize `sum_a W_a` or search for a controller satisfying a specified initial condition; maximal cardinality is not the same concept as a unique greatest winning region unless closure is proved.

## 13. Falsification target

Find the smallest quasi-primal-but-not-semi-primal algebra and a safety game for which:

- every state/input observation has some locally generated safe output;
- the semi-primal-style pointwise action filter would accept;
- but the internal-isomorphism CSP is unsatisfiable.

Such an example would demonstrate that the coupling layer is mathematically necessary, not merely a conservative implementation choice.

Conversely, if no such example exists for equation-defined safety relations, seek a theorem explaining why the equivariant selection always exists and simplify this note accordingly.

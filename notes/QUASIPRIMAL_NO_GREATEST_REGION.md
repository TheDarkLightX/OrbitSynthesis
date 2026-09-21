# Quasi-primal term safety can have no greatest winning region

**Status:** DERIVED negative theorem with an exact finite checker. The quasi-primal term-function characterization is classical. The concrete reactive counterexample is new to this repository and remains under prior-art review. Not Lean-checked.

This strengthens `QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md`.

That earlier witness showed that a local generated-subalgebra predecessor can accept states although no nonempty original-signature term-winning domain exists.

The result here shows something stronger:

> even when several nonempty term-winning domains exist, their family need not have a greatest element.

Thus the ordinary safety-game picture of one greatest controllable region can fail solely because the controller is required to be an original-signature term operation.

## 1. Algebra

Use Quackenbush's three-element quasi-primal algebra

`Q = ({0,1,2}; d, u)`

where

`d(x,y,z) = z if x=y, else x`

is the ternary discriminator and

`u(0)=1,  u(1)=0,  u(2)=1`.

The exact checker verifies directly that:

- the only nonempty proper subalgebra is
  `Q0={0,1}`;
- `phi:Q0->Q0`, `phi(0)=1`, `phi(1)=0`, is an automorphism of Q0;
- the full algebra Q has trivial automorphism group.

Classically, because Q is quasi-primal, a total operation is a Q-term iff it preserves every internal isomorphism. For this concrete algebra the only nontrivial cross-table constraint comes from phi on Q0.

## 2. Game dimensions

Take

- state arity `k=2`;
- one environment input `u in Q`;
- next-state/controller output `v in Q^2`.

A controller therefore has two coordinate functions of arity three:

`f_j(s1,s2,u)`.

When `(s1,s2,u)` lies in `Q0^3`, every Q-term coordinate must:

1. return an element of Q0; and
2. commute with phi.

So paired observations

`000 <-> 111`

must receive paired outputs

`v <-> phi(v)`

coordinatewise.

## 3. Single-equation safety relation

Let

`p(s1,s2,u,v1,v2)=s1`.

Define the unsafe set U by two mechanisms.

### U_dead — make state 10 impossible

Every transition with

`state=(1,0), input=2`

is unsafe, regardless of the output.

This makes state 10 belong to no nonempty winning invariant domain.

### U_pair — force the critical phi-coupling

At observation 000 and its phi-image 111, forbid binary outputs 00 and 11.

Explicitly the four binary unsafe tuples are

- `(0,0,0,0,0)`;
- `(0,0,0,1,1)`;
- `(1,1,1,1,1)`;
- `(1,1,1,0,0)`.

Thus, among binary outputs, observations 000 and 111 permit exactly

`01` and `10`.

This four-tuple set is phi-invariant.

### Construct a term g

Define a total function `g:Q^5->Q` by

`g(t)=p(t)` on safe tuples,

and

`g(t)=1-p(t)` on unsafe tuples.

Every unsafe tuple has first coordinate 0 or 1, so the second clause is well-defined.

On `Q0^5`, the unsafe set is phi-invariant. Hence

`g(phi t)=phi(g(t))`

and `g(t) in Q0` for all binary t.

Outside `Q0^5`, the only proper-subalgebra/internal-isomorphism constraints do not apply. Therefore g preserves every internal isomorphism of Q and, by quasi-primality, g is a Q-term.

Consequently the safety relation is the **single original-signature equation**

`p = g`.

The executable checker constructs g by its complete finite table and verifies both the equation and phi preservation exhaustively.

## 4. Two winning domains

Let

`W1={00,01}`

and

`W2={11,01}`.

### W1 is term-winning

For every binary observation whose state lies in W1, its phi-paired observation has state 11 or 10, neither of which lies in W1.

Therefore each constrained phi-pair has only one side inside W1.

At the special observation 000 choose output 01. At every other constrained binary observation choose any safe output in W1; for observations containing 2 choose an arbitrary safe output in W1.

Propagate the binary choices by phi to the unconstrained paired observations.

The resulting total coordinate tables preserve Q0 and phi, hence are Q-terms, and are safe/invariant on W1.

### W2 is term-winning

The same argument applies symmetrically.

At the special observation 111 choose output 01. Its phi-paired observation 000 lies outside W2.

Again the table extends to Q-term coordinate functions and wins on W2.

The checker constructs these tables explicitly through the exact internal-isomorphism constraints.

## 5. Their union is not term-winning

The union is

`W1 union W2 = {00,01,11}`.

Now **both** observations 000 and 111 are constrained because their states 00 and 11 lie in the candidate domain.

At 000 the controller must choose a binary output that is:

- safe;
- in the candidate domain.

The only possibility is 01, because 10 is not in the domain and 00/11 are unsafe there.

Term equivariance then forces the output at 111 to be

`phi(01)=10`.

But 10 is not in the domain.

Contradiction.

Therefore `W1 union W2` is not term-winning.

This already proves that the family of Q-term-winning invariant domains is not union-closed.

## 6. No common winning superset

Union failure alone does not rule out a larger winning region containing both W1 and W2.

The dead-state gadget closes that loophole.

Any common winning superset W of W1 and W2 contains states 00 and 11, so the 000/111 argument applies.

At those two observations, a phi-compatible safe pair of binary outputs must be either

`01 <-> 10`

or

`10 <-> 01`.

Thus W must contain state 10.

But state 10 has environment input 2 with **no safe transition at all**.

Hence no winning invariant domain can contain 10.

Contradiction.

### Theorem 1 — no greatest term-winning region

This single-equation safety game has at least two nonempty original-signature Q-term-winning domains W1 and W2, but no term-winning domain contains both.

Therefore the poset of term-winning invariant domains under inclusion has no greatest element.

## 7. Exact finite enumeration

`experiments/quasiprimal_no_greatest_region.py` checks all `2^9=512` candidate state domains.

It verifies:

- W1 is term-winning;
- W2 is term-winning;
- `W1 union W2` is not term-winning;
- state 10 occurs in no winning domain;
- there is no winning common superset of W1 and W2;
- exactly 128 candidate domains are term-winning, including the empty domain;
- exactly two inclusion-maximal term-winning domains exist.

Those maximal domains are

`M1 = Q^2 - {10,11}`

and

`M2 = Q^2 - {10,00}`.

Both have seven states and are incomparable.

The enumeration is a finite falsification/checking artifact, not the logical proof of the theorem; the proof is the short coupling argument above.

## 8. Why ordinary greatest-fixed-point synthesis breaks

For unrestricted finite safety games, positional action choices can be patched state-by-state. The union of winning invariant regions is winning, yielding a greatest winning region and the familiar controllable-predecessor greatest fixed point.

Here patching fails because one Q-term controller is a **single globally constrained table**.

The internal isomorphism couples the controller's value at 000 to its value at 111 even when those two observations arose from different local winning constructions.

That is the inner reason the lattice property fails.

The obstruction is not:

- infinite state;
- temporal memory;
- Boolean-power complexity;
- Tau implementation details;
- quantifier elimination.

It occurs in a nine-state finite game with one environment symbol coordinate and an equation-defined safety relation.

## 9. Consequences for synthesis APIs

There are now three distinct questions.

### A. Fixed-domain feasibility

Given W, does one term controller keep W safe?

`QUASIPRIMAL_TERM_SAFETY_CSP.md` answers this exactly with a strategy-table CSP.

### B. Initial-set realizability

Given required initial states I, does one term controller win from all of I?

Again the global CSP is exact.

### C. "The" winning region

There need not be a single largest invariant domain controlled by one original-signature term strategy.

An API must therefore choose semantics explicitly, for example:

- return all inclusion-maximal controllable domains;
- optimize one domain under a specified objective;
- answer feasibility from a specified initial set;
- compute per-state existential controllability while warning that the witnesses may require different controllers.

Returning one set called "the greatest winning region" is unsound in the general quasi-primal term-controller setting.

## 10. Boundary with demi-semi-primality

`DEMI_SEMIPRIMAL_TERM_SAFETY.md` proves a greatest-fixed-point theorem when every internal isomorphism extends to a global automorphism.

The present Q fails exactly that hypothesis:

- phi is an internal automorphism of Q0;
- phi does not extend to an automorphism of Q;
- `Aut(Q)` is trivial.

So the positive demi-semi-primal theorem and this negative quasi-primal theorem meet at a sharp structural boundary:

> **extendable symmetries can be handled orbitwise; genuinely partial symmetries can destroy global patchability of winning regions.**

`experiments/demi_discriminator_orbit_check.py` supplies the complementary finite calibration on the pure three-element discriminator algebra, where all partial subalgebra isomorphisms extend globally.

## 11. Prior-art boundary

Classical sources establish the algebraic ingredients:

- quasi-primal/discriminator term-function interpolation by preservation of internal isomorphisms;
- Quackenbush's demi-semi-primal extension-property hierarchy.

Game literature separately studies permissive/maximal strategies and cases where one strategy does not subsume all winning behavior.

Current searches have not found this exact algebraically constrained safety-game counterexample or the no-greatest-domain theorem for term-clone-restricted controllers. That is only a bounded prior-art result, not a publication novelty conclusion.

## 12. Next falsification targets

1. Minimize the witness: can state arity `k=1` ever suffice for an equation-defined quasi-primal counterexample, or is `k=2` minimal?
2. Minimize the algebra: can a two-element non-primal algebra produce the same phenomenon?
3. Characterize clones C for which C-controller winning domains are always union-closed for every C-invariant safety relation.
4. Test whether the extension property of demi-semi-primal algebras is not only sufficient but, within finite quasi-primal algebras, necessary for universal greatest-region behavior.
5. Determine the complexity of enumerating all maximal controllable domains from the relational-basis CSP.

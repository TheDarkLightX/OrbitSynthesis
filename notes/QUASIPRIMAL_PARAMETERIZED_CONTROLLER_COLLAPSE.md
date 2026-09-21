# Parameterized controllers collapse quasi-primal safety to unrestricted finite safety

**Status:** DERIVED reactive consequence of classical discriminator/primality theory. Functional completeness after naming constants is classical; no novelty is claimed for the discriminator truth-table compiler. The controller-semantics consequence is important to OrbitSynthesis architecture. Tau-independent.

## 1. Why controller semantics must name parameters explicitly

The existing hierarchy studies **original-signature term controllers**.

That means a controller coordinate must be represented by a term whose only leaves are:

- the controller's observation variables; and
- nullary symbols already present in the algebra's original signature.

No arbitrary carrier element may be inserted merely because it is convenient for one synthesized controller.

Universal algebra also studies **polynomial/parameterized operations**, where fixed carrier elements may be used as parameters/constants in the representing term.

For finite quasi-primal algebras, these two semantics are radically different.

## 2. Discriminator

Let Q be a finite quasi-primal algebra.

Classically Q has the ternary discriminator as a term operation:

`d(x,y,z) = z if x=y, else x`.

This is one of the standard characterizations of quasi-primality.

## 3. Build ordinary if-then-else from the discriminator

Define

`N(x,y,u,v)
 = d(d(x,y,u), d(x,y,v), v)`.

### Lemma 1 -- normal selector

`N(x,y,u,v)=u` when `x=y`, and `N(x,y,u,v)=v` when `x!=y`.

### Proof

If `x!=y`, both inner discriminator calls return x, so the outer call sees equal first two arguments and returns its third argument v.

If `x=y`, the inner calls return u and v. If u=v, the outer discriminator returns its third argument v=u. If u!=v, it returns its first argument u.

So in either subcase the result is u. QED.

No parameters were used to define N; it is an original-signature Q-term because d is.

## 4. Naming carrier elements makes every truth table representable

Now expand Q by a nullary constant symbol for every element of its finite carrier.

Let

`f:Q^n -> Q`

be arbitrary.

For every input tuple

`a=(a_1,...,a_n) in Q^n`,

the expanded language can test the conjunction

`x_1=a_1, ..., x_n=a_n`

using nested N-selectors and return the named constant `f(a)` on that branch.

Enumerating all tuples of Q^n and nesting these equality-controlled branches yields a term in the expanded language representing f exactly.

### Theorem 2 -- parameterized functional completeness

Every finitary function on a finite quasi-primal algebra is a polynomial/parameterized operation when arbitrary carrier elements may be named as constants.

Equivalently, the expansion of Q by all carrier constants is primal/functionally complete.

This is classical discriminator-algebra theory; the construction above is included to make the controller consequence explicit.

## 5. Reactive consequence

Consider a finite safety game over local state/input labels from Q.

Suppose controller coordinates are allowed to be **parameterized Q-terms**, with arbitrary fixed elements of Q available as synthesis-time constants.

Any finite positional controller table

`sigma:Q^(k+m) -> Q^k`

has k arbitrary finite coordinate functions.

By Theorem 2, every coordinate is representable by a parameterized Q-term.

Therefore:

### Theorem 3 -- quasi-primal parameter collapse

For finite quasi-primal Q, parameterized-term positional safety synthesis is exactly ordinary finite positional safety synthesis.

The winning region is the ordinary greatest fixed point

`W* = gfp(CPre)`.

A finite positional winning strategy exists on W* iff a parameterized original-algebra controller exists, and every chosen positional table can be compiled to parameterized Q-terms.

## 6. The demi/quasi boundary is parameter-free

`QUASIPRIMAL_DEMI_EQUATIONAL_CHARACTERIZATION.md` proves:

> among finite quasi-primal algebras, demi-semi-primality exactly characterizes universal greatest-region behavior for **original-signature term controllers**.

Theorem 3 here shows that this obstruction disappears when arbitrary parameters are admitted.

Thus there are at least three distinct semantics:

### S1 -- original-signature term controller

No fresh carrier parameters.

Sensitive to subalgebras, automorphisms, and internal isomorphisms.

Demi/non-demi boundary matters.

### S2 -- parameterized/polynomial controller

Arbitrary fixed carrier elements may be named by the synthesized program.

For finite quasi-primal Q: every finite table is representable.

### S3 -- unrestricted finite table / external representation

No algebraic syntax restriction at all.

For finite quasi-primal Q, S2 and S3 have the same finite positional expressive power, though their compiled representations differ.

## 7. Revisit the no-greatest-region counterexample

The Quackenbush no-greatest witness does **not** say the underlying safety game lacks a largest ordinarily controllable region.

It says separately winning domains cannot be patched by one **parameter-free term table**, because that table must respect a nonextendable internal isomorphism.

A parameterized controller can name carrier elements and implement the two sides independently by case distinction.

So the obstruction is one of **language expressivity**, not ordinary game-theoretic controllability.

This is an important interpretation guardrail for any paper or product description.

## 8. Compiler construction

A naive exact compiler for a scalar truth table uses a decision tree.

For each tuple `a in Q^n`, build a guard that tests all coordinates against the named constants `a_i`. On a match, return the named constant `f(a)`; otherwise continue to the next tuple.

Term size is polynomial in the explicit truth-table size, roughly

`O(n |Q|^n)`

selector nodes before simplification.

For a k-output controller, compile k coordinate tables separately.

This is already sufficient as a reference implementation.

More compact representations can later share prefixes or compile the decision tree to a DAG/BDD-like object before emitting a term.

## 9. Standalone implementation

`src/orbitsynthesis/discriminator_compile.py` implements a small representation-independent AST compiler using:

- variables;
- named constants;
- discriminator nodes.

It derives the N-selector from d rather than assuming a separate primitive.

The evaluator can be supplied an arbitrary finite carrier and the standard discriminator semantics, so it is independent of Tau.

`experiments/discriminator_parameterized_compile.py` exhaustively checks all 27 unary functions on a three-element carrier and a deterministic sample of binary truth tables.

## 10. Prior-art boundary

Classical/source-bound:

- Pixley's ternary-discriminator characterization of quasi-primal algebras;
- functional completeness/primality after sufficiently naming constants;
- decision-tree interpolation over a finite discriminator algebra.

Derived/useful here:

- the explicit controller-semantics split S1/S2/S3;
- the observation that the demi/quasi greatest-region theorem is exactly a parameter-free expressivity phenomenon;
- using a discriminator-table compiler as the bridge from unrestricted finite safety synthesis to parameterized algebraic controller code.

## 11. Product boundary

An API must never expose a generic option called merely `term_controller=True`.

It should distinguish at least:

- `original_signature_term`;
- `parameterized_term`;
- `unrestricted_table`.

Otherwise a solver can silently claim realizability under a strictly stronger controller language than the specification intended.

## 12. Next questions

1. For non-quasi-primal finite algebras, characterize when polynomial controllers collapse to unrestricted tables.
2. Quantify the smallest parameter set C subseteq Q needed to make a given winning table representable.
3. Minimize discriminator decision trees/DAGs for synthesized controllers.
4. Treat parameter budget as a controller-complexity measure: zero parameters recovers the term-clone hierarchy; all parameters recover unrestricted quasi-primal control.

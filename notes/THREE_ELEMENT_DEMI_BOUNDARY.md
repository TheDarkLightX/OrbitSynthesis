# Complete three-element discriminator+unary calibration of the demi boundary

**Status:** FINITE-VERIFIED complete classification for one 27-algebra laboratory, combined with the derived demi-semi-primal greatest-region theorem. This is not a classification of all finite quasi-primal algebras.

## 1. Question

`DEMI_SEMIPRIMAL_TERM_SAFETY.md` gives a positive theorem:

> if every internal isomorphism extends to a global automorphism, equation-defined original-signature term safety admits an orbitwise greatest-fixed-point algorithm.

`QUASIPRIMAL_NO_GREATEST_REGION.md` gives one negative quasi-primal example where the extension property fails and no greatest term-winning domain exists.

This suggests the stronger conjecture:

> **Conjecture (universal greatest-region boundary).** Among finite quasi-primal algebras, the demi-semi-primal extension property is exactly the condition under which every equation-defined finite safety game has a greatest original-signature term-winning region.

The first systematic falsification target is the complete family of three-element discriminator algebras with one unary expansion.

## 2. Complete finite family

Let

`D={0,1,2}`

and include the ternary discriminator

`d(x,y,z)=z if x=y, else x`.

For every unary map

`u:D->D`,

form

`A_u=(D;d,u)`.

There are exactly

`3^3=27`

such unary maps.

Because the discriminator is a basic operation, every member of this family is quasi-primal.

For each of the 27 algebras the checker exhaustively computes:

1. every nonempty subalgebra;
2. every isomorphism between subalgebras;
3. every full automorphism;
4. whether every internal isomorphism extends to a full automorphism.

## 3. Classification result

`experiments/three_element_demi_boundary.py` finds exactly:

- 15 demi-semi-primal expansions;
- 12 non-demi expansions.

For every one of the 12 non-demi cases, the checker finds a two-element subalgebra

`S={a,b}`

whose swap

`phi(a)=b`, `phi(b)=a`

is an internal automorphism that does **not** extend to an automorphism of the full three-element algebra.

This is an exhaustive statement about this 27-member family.

## 4. Uniform negative construction for all 12 non-demi members

The same game template works for every non-demi member.

Let c be the third carrier element outside S.

Use:

- state arity `k=2`;
- input arity `m=2`;
- special observation
  `z=(a,b,a,b)`;
- its internal-isomorphism image
  `phi(z)=(b,a,b,a)`.

Define two candidate domains

`W1={ab,aa}`

and

`W2={ba,aa}`.

The common output aa is deliberately not phi-fixed:

`phi(aa)=bb`.

### Special unsafe orbit

At z, mark outputs ab and ba unsafe, and close those unsafe transition tuples under **all** internal isomorphisms of the algebra.

Thus at z the relevant safe S-valued outputs are aa and bb, and the same structure is transported consistently to every groupoid image.

### Dead-state orbit

Make state bb dead at input `(a,c)` by declaring every output unsafe there, again closing under all internal isomorphisms.

The observation

`(b,b,a,c)`

contains all three carrier values. Hence no proper subalgebra contains it. In this three-element non-demi family the full automorphism group is trivial, so this dead gadget introduces no unwanted partial-symmetry coupling.

## 5. The safety relation is one equation

The checker explicitly constructs one total function g on transition tuples.

Let p be the first state projection.

Define g by branches:

- on the special unsafe groupoid orbit, use the second state projection;
- on the dead unsafe orbit, use the first input projection;
- everywhere else, use p.

Each branch is closed under the internal-isomorphism groupoid, and each selected projection commutes with every partial isomorphism on its domain.

The checker verifies exhaustively that

`g(phi(t))=phi(g(t))`

for **every** internal isomorphism and every tuple in its domain.

By the quasi-primal term-function characterization, g is therefore a term operation.

The safe transition relation is exactly the single equation

`p=g`.

## 6. Why W1 and W2 win

For W1, the special observation z lies inside the domain while its phi-image has state ba outside W1.

So the controller may choose aa at z. The forced paired value bb occurs only at an observation whose state is outside the required invariant domain.

All other constrained observations have a safe output in W1, and the full internal-isomorphism groupoid CSP has a solution.

The same argument holds for W2 at the paired observation.

The checker uses all internal isomorphisms, not only the selected swap, and confirms:

`TermWin(W1)=true`

and

`TermWin(W2)=true`.

## 7. Why their union fails

The union contains both special states ab and ba:

`W1 union W2={ab,ba,aa}`.

At z, the only safe output from that union is aa.

Internal-isomorphism preservation forces the paired observation to output

`phi(aa)=bb`.

But bb is not in the union.

Thus the union is not term-winning.

Any common winning superset would have to add bb.

But bb is dead at input `(a,c)`.

Therefore W1 and W2 have no common term-winning superset, so no greatest term-winning region exists.

## 8. Bounded equivalence theorem for this laboratory

Combining:

1. the general positive theorem for demi-semi-primal algebras; and
2. the uniform verified negative construction above for every non-demi member,

we obtain:

### Finite classification result

For every algebra

`A_u=(D;d,u)`

on the three-element set D with arbitrary unary u, the following are equivalent:

1. `A_u` is demi-semi-primal;
2. every internal isomorphism extends to a global automorphism;
3. the derived orbit/stabilizer predecessor theorem applies to every automorphism-invariant/equation-defined finite safety game;
4. `A_u` does not belong to the 12-member class for which the uniform single-equation no-greatest-region obstruction is constructed.

Be careful with item 4: this is an exhaustive classification **inside this 27-member family**, not a proof of the unrestricted conjecture.

## 9. Why this matters

The previous hierarchy could have been accidental:

- semi-primal happened to be easy;
- one quasi-primal example happened to be hard;
- demi-semi-primal happened to admit an orbit algorithm.

The complete 27-algebra calibration gives stronger evidence that the real mechanism is the **extension of partial symmetries to global symmetries**.

When extension holds, one representative strategy choice can be propagated consistently along a global group orbit and patched with other orbits.

When extension fails, two individually valid local strategy tables can impose incompatible values once their required domains are combined.

That is the Noether-style inner ground of the boundary.

## 10. LEAP-style quotient interpretation

The positive side has an exact finite portal:

`concrete term-controller game`

`-> quotient observations/states by Aut(A)`

`-> enforce generated-subalgebra + stabilizer-fixed action conditions`

`-> solve quotient safety fixed point`

`-> lift representative actions equivariantly`

`-> verify in the original finite game`.

This matches LEAP's verifier-gated quotient/lift methodology: a quotient result counts only after the lifted controller passes the original-domain semantics.

The non-demi witnesses are exactly cases where that global-automorphism portal loses a partial symmetry that still constrains term tables.

## 11. Next theorem target

The strongest surviving conjecture is:

> **Conjecture.** For finite quasi-primal Q, universal existence of a greatest original-signature term-winning domain for every equation-defined finite safety game is equivalent to Q being demi-semi-primal.

Falsification plan:

1. search larger quasi-primal algebras with a nonextendable internal isomorphism but no usable two-point-swap obstruction;
2. abstract the uniform witness from a swap to an arbitrary nonextendable internal isomorphism;
3. identify the exact separation conditions on tuples needed to build the two incomparable winning domains;
4. test whether extra full automorphisms can force the dead-state orbit to collide with the desired winning domains;
5. search the classical literature for an existing extension/amalgamation theorem that implies or refutes this equivalence.

## 12. Reproducibility

Run:

`python experiments/three_element_demi_boundary.py`

Expected summary:

- total unary expansions: 27;
- demi-semi-primal: 15;
- non-demi: 12;
- non-demi with verified uniform no-greatest obstruction: 12.

This checker is deterministic and exhaustive over the 27 algebra signatures. Its game feasibility check uses the complete internal-isomorphism groupoid for each constructed witness.

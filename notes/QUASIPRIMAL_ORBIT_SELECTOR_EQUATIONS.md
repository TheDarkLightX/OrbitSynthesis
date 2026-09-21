# Orbit-selector lemma: groupoid-invariant safety as one quasi-primal term equation

**Status:** DERIVED lemma from the classical Pixley characterization of quasi-primal term operations. The orbitwise projection technique is classical in spirit and closely parallels the standard proof of Quackenbush's demi-semi-primal characterization; it is not claimed as a new universal-algebra interpolation technique. Its use to compress the reactive obstruction to one equation is under prior-art review.

## 1. Setup

Let Q be a finite quasi-primal algebra.

Let `Iso(Q)` denote the inverse-semigroup/groupoid of isomorphisms between subalgebras of Q.

A relation

`R subseteq Q^N`

is **groupoid-invariant** when every internal isomorphism preserves R wherever it is defined. Equivalently, R is a union of orbits of the natural partial action of `Iso(Q)` on Q^N.

Fix a distinguished coordinate index p.

Assume:

> for every tuple `x notin R`, there exists some coordinate j with `x_j != x_p`.

In words: no forbidden tuple is forced to be constant relative to coordinate p.

## 2. Classical quasi-primal interpolation fact

For finite quasi-primal Q, a total operation

`f:Q^N -> Q`

is a term operation iff it preserves the subuniverses of `Q^2` that are graphs of isomorphisms between subalgebras.

Equivalently, it is enough here to verify:

1. subalgebra preservation; and
2. internal-isomorphism equivariance.

This is the classical Pixley characterization.

The construction below deliberately returns one of its input coordinates at every tuple, so subalgebra preservation is automatic.

## 3. Choose one separating coordinate per forbidden orbit

For every groupoid orbit O contained in the complement of R, choose one representative

`x^O in O`.

By hypothesis, choose a coordinate

`j(O)`

such that

`x^O_(j(O)) != x^O_p`.

Because internal isomorphisms are injective and act on values without permuting tuple positions, the same coordinate separates every tuple in O:

`y_(j(O)) != y_p`

for all `y in O`.

## 4. Define an orbitwise coordinate selector

Define

`g:Q^N -> Q`

by

- if `x in R`, set `g(x)=x_p`;
- if `x` belongs to forbidden orbit O, set `g(x)=x_(j(O))`.

This is a total function because the safe and forbidden groupoid orbits partition Q^N.

## 5. g preserves subalgebras

Let D be any subalgebra of Q and let

`x in D^N`.

The value g(x) is always one of the coordinates of x.

Hence

`g(x) in D`.

So g preserves every subalgebra.

This conservative/coordinate-selector property is stronger than needed.

## 6. g preserves every internal isomorphism

Let

`psi:D -> E`

be an internal isomorphism and let `x in D^N`.

Then x and psi(x) lie in the same groupoid orbit.

### If x is safe

Groupoid invariance of R makes psi(x) safe as well, so

`g(psi(x)) = psi(x_p) = psi(g(x))`.

### If x is forbidden

The entire orbit uses the same coordinate index j(O), hence

`g(psi(x))
 = psi(x_(j(O)))
 = psi(g(x))`.

Thus g respects every internal isomorphism.

By Pixley's quasi-primal term-function characterization, g is an original-signature Q-term operation.

## 7. Single-equation representation

### Theorem 1 -- orbit-selector equation lemma

Under the assumptions above, there exists an N-ary term g of Q such that

`R(x) iff x_p = g(x)`.

### Proof

On R, g(x)=x_p by definition.

Outside R, the selected coordinate is different from x_p throughout its forbidden orbit, so `g(x)!=x_p`.

Sections 5--6 prove that g is a Q-term. QED.

## 8. Why this does not say every groupoid-invariant relation is one equation

The separating-coordinate hypothesis matters.

If a forbidden tuple is constant in every coordinate relative to p, no coordinate selector can distinguish it from p there.

A more general term might still separate it, depending on the algebra's unary/nullary structure, but Theorem 1 does not claim this.

For the reactive obstruction in `QUASIPRIMAL_DEMI_RELATIONAL_CHARACTERIZATION.md`, the hypothesis is guaranteed by construction:

- every special forbidden transition contains an ordered enumeration of a nontrivial subalgebra, hence at least two different values;
- every dead forbidden transition contains an input tuple enumerating the whole carrier, hence multiple distinct values.

Taking p to be the first state coordinate therefore works uniformly.

## 9. Prior-art correction: the orbit-separation move is classical

The proof of the classical demi-semi-primal characterization uses essentially the same representation move.

Given a nonextendable internal isomorphism `iota:S->T`, order S as a tuple sigma and T as `tau=iota(sigma)`. Nonextendability implies sigma and tau lie in different global-automorphism orbits. One then defines a conservative operation piecewise by coordinate projections on automorphism orbits to obtain an operation preserving subalgebras and automorphisms but not iota.

This is the standard Quackenbush/Pixley orbit-separation mechanism; a concise proof is recorded by Keith Kearnes in connection with Burris--Sankappanavar Exercise IV.10.5.

OrbitSynthesis must therefore **not** claim novelty for:

- ordered subalgebra enumeration as an orbit tag;
- defining conservative functions by different coordinate projections on symmetry orbits.

The research contribution under investigation is the reactive use of this mechanism to characterize greatest-region patchability.

## 10. Concrete calibration

The general-relation calibration for the three-element Quackenbush algebra has transition arity 11.

A finite checker constructs g exactly as above:

- 320 forbidden transition tuples;
- 306 forbidden groupoid orbits in the concrete algebra;
- every forbidden orbit has a coordinate different from p;
- `safe(x) iff g(x)=x_p` on all `3^11=177147` transition tuples;
- phi-equivariance holds on all `2^11=2048` binary tuples.

The general logical proof is Theorem 1; these counts are only a finite calibration.

## 11. Consequence for the demi boundary

Combining this lemma with the non-demi reactive construction upgrades the relation-level result:

> every non-demi finite quasi-primal algebra admits a **single-equation** finite safety game whose original-signature term-winning domains have no greatest element.

The exact characterization is stated in `QUASIPRIMAL_DEMI_RELATIONAL_CHARACTERIZATION.md` after the equation-level upgrade.

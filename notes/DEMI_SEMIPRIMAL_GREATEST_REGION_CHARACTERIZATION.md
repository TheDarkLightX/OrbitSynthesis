# Demi-semi-primality exactly characterizes greatest-region term safety

**Status:** derived equivalence theorem, strengthened to a single-equation
converse on 2026-08-14. The positive direction is the existing
orbit/stabilizer greatest-fixed-point theorem. The converse is a generic
construction from every nonextendable internal isomorphism. Primary and
separately written no-import reconstructions validate the construction on all
27 unary expansions of the three-element discriminator algebra. Lean,
external review, and publication-novelty review remain pending.

## 1. Setting

Let `A` be a finite quasi-primal algebra. A safety instance has states `A^k`,
environment inputs `A^m`, controller outputs `A^k`, and a safe relation

```text
R subseteq A^k x A^m x A^k.
```

One positional controller is used at every observation, and every output
coordinate must be an original-signature term operation of `A`.

A domain `W subseteq A^k` is **term-winning** when one such total controller is
safe on every observation whose state lies in `W` and always returns a next
state in `W`.

## 2. Main theorem

### Theorem — exact greatest-region boundary

For a finite quasi-primal algebra `A`, the following are equivalent.

1. `A` is demi-semi-primal: every internal isomorphism between nontrivial
   subalgebras extends to an automorphism of `A`.
2. Every finite safety instance whose safe relation is defined by one
   original-signature equation has a greatest term-winning invariant domain.
3. The same holds for every finite relation invariant under all internal
   isomorphisms.
4. In every such instance, the union of all term-winning domains is
   term-winning.

Thus

```text
all internal symmetries extend globally
  <=> shared-term winning regions are universally patchable.
```

## 3. Positive direction

Assume `A` is demi-semi-primal and write `G=Aut(A)`. Quasi-primal
interpolation plus the extension property gives

```text
f is an A-term
iff
f(z) in Sg_A(z) for every z
and
f(gz)=g f(z) for every g in G.
```

For a `G`-invariant target `W`, the existing predecessor `DPre(W)` requires at
each observation:

- a safe successor in `W`;
- coordinates inside the generated subalgebra; and
- fixation by the observation stabilizer.

`DEMI_SEMIPRIMAL_TERM_SAFETY.md` proves that the greatest fixed point of this
operator is exactly the term-winning region. Equation-defined relations are
term invariant, hence automorphism invariant. This proves the positive half.

## 4. Choose a maximal partial symmetry

Assume `A` is not demi-semi-primal. Choose a nonextendable internal
isomorphism

```text
phi:B -> C
```

maximal under graph inclusion.

It has no proper internal-isomorphism extension: an extendable proper extension
would extend `phi`, while a nonextendable proper extension contradicts
maximality.

List all elements of `B`:

```text
g=(g_1,...,g_l).
```

Choose distinct `b_0,b_1 in B`, put `k=l+2`, and define

```text
a   =(g,b_1,b_0),
p_0 =(g,b_0,b_0),
p_1 =(g,b_0,b_1).
```

Transport by `phi`:

```text
a'=phi(a), q_0=phi(p_0), q_1=phi(p_1).
```

The full `g` prefix pins any internal isomorphism on all of `B`; the final two
tags distinguish the three states.

Choose `beta in A-B` and `gamma in A-C`. Use one environment coordinate.

## 5. Critical and dead orbits

At the critical observation

```text
z=(a,b_0)
```

permit exactly `p_0,p_1`, then close these transitions under every internal
isomorphism. At

```text
z'=(a',phi(b_0))
```

the permitted outputs are exactly `q_0,q_1`.

Make the complete internal-groupoid orbits of

```text
(p_1,beta), (q_0,gamma)
```

dead: they have no safe output.

At every observation outside the critical and dead orbits, permit every
output.

Maximal nonextendability prevents a dead orbit from reaching any state needed
by the one-sided domains. Such a collision would agree with `phi` on the full
listed copy of `B` and extend it past `B` or `C`.

## 6. Two winners but no common upper bound

Let

```text
W_L={a,p_0},
W_R={a',q_1}.
```

`W_L` wins by choosing `p_0` at `z`; the transported `q_0` occurs only at the
unconstrained state `a'`. Elsewhere all outputs are safe. The componentwise
partial table extends to a term by quasi-primal interpolation.

Symmetrically, `W_R` wins by choosing `q_1` at `z'`, transporting `p_1` to the
unconstrained source observation.

Their union is not winning: it contains only `p_0` on the source side and only
`q_1` on the target side, but `phi(p_0)=q_0`.

Any common winning upper bound must use one compatible critical pair:

```text
p_0 <-> q_0
or
p_1 <-> q_1.
```

Since it already contains `p_0` and `q_1`, it must add dead state `q_0` or dead
state `p_1`. Either lets the environment choose the corresponding dead input.
Hence no common term-winning upper bound exists.

## 7. One equation defines the generic witness

Flatten a transition to

```text
x=(state,input,output) in A^(2k+1).
```

Let

```text
p(x)=x_1
```

be the first projection. Define a total operation

```text
g(x)=x_1  if x is safe,
     x_2  if x is unsafe.
```

Every unsafe tuple lies in a critical or dead orbit and begins with the tagged
listing of `B` or `C`. Therefore its first two coordinates are distinct, so

```text
x is safe iff p(x)=g(x).
```

The operation `g` is an `A`-term:

- both branches are projections, so `g(x) in Sg_A(x)`;
- safety is internal-groupoid invariant, so every internal isomorphism
  preserves which branch is taken;
- consequently `g(phi(x))=phi(g(x))` whenever the internal isomorphism applies.

By quasi-primal interpolation, `g` is an original-signature term. Thus the
generic converse relation is defined by the single equation

```text
p=g.
```

This upgrades the equivalence from arbitrary compatible relations to the
one-equation fragment.

## 8. Shared structural lemma

The one-sided controllers and the list-subpower algorithm use the same fact:
partial term interpolation over a finite quasi-primal algebra factors over
connected components of the internal-isomorphism groupoid.

Inside a component, one representative value determines every transported
value. Across components, choices patch independently. Demi-semi-primality
turns every such partial component into a global automorphism orbit; a
nonextendable component destroys universal patchability.

## 9. Executable evidence

Implementations:

```text
src/orbitsynthesis/greatest_region_boundary.py
src/orbitsynthesis/principal_greatest_region.py
```

The primary and independent audits enumerate every unary expansion

```text
({0,1,2};d,u).
```

They find exactly

```text
15 extension-property expansions,
12 nonextendable expansions.
```

For every nonextendable expansion they verify:

- two feasible one-sided domains;
- an infeasible union;
- no-greatest dead-state structure;
- internal-groupoid invariance;
- exact equality `safe iff p=g` on every flattened transition;
- generated-subalgebra preservation of `g`; and
- internal-isomorphism equivariance of `g`.

The pure discriminator algebra is the extendable negative control. Reviving one
dead orbit restores a common upper bound, showing the dead gadget is
load-bearing.

## 10. Remaining work

The main mathematical equivalence is now closed. The next tasks are proof
hardening rather than another conjectural construction:

1. formalize the groupoid-component interpolation lemma in Lean;
2. formalize the maximal-nonextendable orbit-separation argument;
3. formalize the principal-equation separator;
4. obtain external universal-algebra and game-theory review;
5. determine whether a smaller universal state arity is possible.

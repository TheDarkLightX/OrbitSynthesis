# Demi-semi-primality exactly characterizes universal greatest-region safety

**Status:** new derived equivalence theorem, 2026-08-14.  The positive
direction specializes the existing demi-semi-primal orbit/stabilizer
predecessor.  The converse below is a generic construction from an arbitrary
nonextendable internal isomorphism.  A primary implementation and a separately
written no-import reconstruction validate the construction on all 27 unary
expansions of the three-element discriminator algebra.  The theorem is not yet
Lean-formalized or externally peer reviewed.  Publication novelty remains
**UNKNOWN**.

## 1. Scope

Let `A` be a finite quasi-primal algebra.  A finite safety instance consists
of

- states `A^k`, with `k>=1`;
- environment inputs `A^m`, with `m>=0`;
- controller outputs / next states `A^k`; and
- a safe relation

```text
R subseteq A^k x A^m x A^k.
```

One positional controller must be used at every observation, and each output
coordinate must be an original-signature term operation of `A`.

The converse requires the natural semantic closure condition on the relation.

### Internal-groupoid invariance

For every internal isomorphism

```text
psi:B -> C
```

between nontrivial subalgebras, and every transition whose state, input, and
output entries all lie in `B`,

```text
R(a,u,v) iff R(psi(a),psi(u),psi(v)).
```

Because inverse internal isomorphisms are present, one-way preservation is
equivalent to the displayed biconditional.

Every equation-defined relation has the relevant preservation property.  The
theorem below is stated for all groupoid-invariant relations.  A stronger
claim that the generic converse witness can always be chosen to be one
principal equation is **not** asserted here.

A domain `W subseteq A^k` is **term-winning** if one total coordinatewise
`A`-term controller is safe on every observation with state in `W` and always
returns a next state in `W`.

## 2. Main equivalence

### Theorem — greatest-region characterization

For a finite quasi-primal algebra `A`, the following are equivalent.

1. `A` is demi-semi-primal: every internal isomorphism between nontrivial
   subalgebras extends to an automorphism of `A`.

2. Every finite internal-groupoid-invariant safety instance over `A` has a
   greatest term-winning invariant domain.

3. In every such instance, the union of all term-winning invariant domains is
   itself term-winning.

Thus the exact structural boundary is

```text
extendable internal symmetries
    <=> universal patchability of shared-term winning regions.
```

This is stronger than observing one positive class and one negative example:
every failure of the extension property now produces a finite no-greatest
safety game.

## 3. Positive direction

Assume `A` is demi-semi-primal and put

```text
G=Aut(A).
```

The classical quasi-primal interpolation theorem plus the extension property
gives the exact term-function characterization:

```text
f is an A-term
iff
f(z) lies in Sg_A(z) for every z
and
f(gz)=g f(z) for every g in G.
```

For a `G`-invariant target set `W`, define `DPre(W)` by retaining state `a`
exactly when every input `u` has a safe successor `v in W` such that

- every coordinate of `v` lies in `Sg_A(a,u)`; and
- `v` is fixed by the stabilizer of `(a,u)` in `G`.

`DEMI_SEMIPRIMAL_TERM_SAFETY.md` proves that the greatest fixed point of
`DPre` is exactly the term-winning region.  Internal-groupoid invariance of
`R` implies in particular automorphism invariance, so that theorem applies.

Hence every term-winning domain is contained in one term-winning greatest
fixed point.  This proves `1 => 2`, and `2 => 3` is immediate.

## 4. Converse setup

Assume that `A` is not demi-semi-primal.  Choose a nonextendable internal
isomorphism

```text
phi:B -> C
```

that is maximal under graph inclusion.

Maximality has a load-bearing consequence:

> `phi` has no proper internal-isomorphism extension at all.

Indeed, a proper extension that itself extended to a global automorphism would
make `phi` globally extendable; a proper extension that did not extend
globally would contradict maximality.

Both `B` and `C` are proper and have at least two elements.  List all elements
of `B` in a fixed order:

```text
g=(g_1,...,g_l).
```

Choose distinct `b_0,b_1 in B`.  Put `k=l+2` and define three source-side
states

```text
a   =(g,b_1,b_0),
p_0 =(g,b_0,b_0),
p_1 =(g,b_0,b_1).
```

Transport them by `phi`:

```text
a'  =phi(a),
q_0 =phi(p_0),
q_1 =phi(p_1).
```

The initial `g` block lists the entire source subalgebra.  Consequently, an
internal isomorphism mapping any one of these tagged source tuples to another
is already determined on all of `B`.  The last two coordinates then prevent
unwanted identifications among `a,p_0,p_1`.  The same holds on the target
side.

Choose

```text
beta in A-B,
gamma in A-C.
```

Use one environment coordinate.

## 5. Critical and dead groupoid orbits

Let the critical observation be

```text
z=(a,b_0)
```

and its transported partner

```text
z'=(a',phi(b_0)).
```

At `z`, make exactly `p_0,p_1` safe.  Close both transitions

```text
(z,p_0), (z,p_1)
```

under every internal isomorphism.  At `z'` the safe outputs are therefore
exactly

```text
q_0,q_1.
```

Now make two observations dead:

```text
(p_1,beta),
(q_0,gamma),
```

together with their complete internal-groupoid orbits.  A dead observation
has no safe output.

At every observation outside the critical and dead orbits, permit only the
self-loop.

This defines the complete finite relation `R_phi`.

### Why the orbit sets do not collide

The tuple tags rule out collisions that would fix the listed source or target
subalgebra and then change the final coordinates.

The remaining dangerous collision would extend `phi` or `phi^{-1}` past its
domain.  For example, an internal isomorphism mapping

```text
(p_1,beta) -> (q_1,x)
```

must agree with `phi` on the listed copy of every element of `B`, and would
therefore properly extend `phi` to the subalgebra generated by `B union
{beta}`.  Maximality forbids it.

The symmetric argument applies to `(q_0,gamma)`.  Therefore:

- the critical orbit is disjoint from both dead orbits;
- no dead orbit reaches `a,a',p_0,q_1`; and
- the safe outputs at `z,z'` are exactly the two displayed pairs.

By construction, `R_phi` is invariant under every internal isomorphism.

## 6. Two one-sided winning domains

Define

```text
W_L={a,p_0},
W_R={a',q_1}.
```

### `W_L` wins

At the only constrained critical observation `z`, choose `p_0`.  Internal
equivariance propagates `q_0` to `z'`, whose state is outside `W_L`.
Every other observation with state in `W_L` has its self-loop.

The critical groupoid component and the self-loop components are disjoint.
Choose the displayed values on those components and use a projection on every
remaining component.  The resulting total table

- takes values in the generated subalgebra of each observation; and
- preserves every internal isomorphism.

Quasi-primal interpolation therefore makes each coordinate an `A`-term.

### `W_R` wins

At `z'`, choose `q_1`.  Equivariance propagates `p_1` back to the unconstrained
observation `z`.  The same componentwise extension argument gives a total term
controller.

Thus both domains are term-winning.

## 7. No common winning upper bound

The union is

```text
W_L union W_R={a,a',p_0,q_1}.
```

At `z`, only `p_0` belongs to this union.  At `z'`, only `q_1` belongs to it.
But

```text
phi(p_0)=q_0 != q_1,
```

so no term controller can win on the union.

More strongly, let `W` be any common winning upper bound.  At the critical
pair, a term-compatible safe choice must be one of

```text
p_0 <-> q_0,
p_1 <-> q_1.
```

Because `W` already contains `p_0` and `q_1`, either choice forces `W` to
contain `q_0` or `p_1`.

But `q_0` and `p_1` are dead states: the environment can choose `gamma` or
`beta`, respectively, and no safe transition exists.

Therefore no term-winning domain contains both `W_L` and `W_R`.  The family
of winning domains has no greatest member.  This proves the contrapositive of
`2 => 1` and completes the equivalence.

## 8. Connection to list-constrained subpowers

The one-sided feasibility arguments above use the same structural fact as
`QUASIPRIMAL_LIST_SUBPOWER_TRACTABILITY.md`:

> partial term interpolation over a finite quasi-primal algebra factors over
> connected components of the internal-isomorphism groupoid.

The greatest-region theorem and the practical list solver are therefore two
faces of one mechanism:

- inside one component, choices are globally coupled;
- across components, choices patch independently;
- demi-semi-primality turns every partial coupling into a global automorphism
  orbit, restoring a monotone greatest-fixed-point operator;
- a genuinely partial symmetry permits domains that are separately
  controllable but cannot be patched.

## 9. Deterministic evidence

The implementation

```text
src/orbitsynthesis/greatest_region_boundary.py
```

constructs `R_phi` from a graph-maximal nonextendable isomorphism and replays
the exact quasi-primal strategy CSP.

The primary and no-import audits enumerate all 27 unary expansions

```text
({0,1,2}; d, u)
```

of the pure three-element discriminator algebra.

They find:

```text
15 expansions with the extension property,
12 expansions without it.
```

For every one of the 12 non-demi-semi-primal expansions, the generic
construction produces:

- two feasible term-winning domains;
- an infeasible union;
- an internal-groupoid-invariant relation;
- exact critical output pairs; and
- two effective dead states.

The pure discriminator algebra is the extendable negative control and produces
no converse witness.

A mutation that revives one dead observation restores a common winning upper
bound, showing that the dead-state gadget is load-bearing rather than
decorative.

## 10. Boundary and next theorem

This theorem is exact for **internal-groupoid-invariant finite relations**.

The following stronger specialization remains open:

> Does every non-demi-semi-primal finite quasi-primal algebra admit a
> **single-equation-defined** no-greatest witness?

Quackenbush's concrete algebra `Q` does.  The generic relation above is finite
and compatible, but a universal principal-equation separator has not been
proved.

That definability question, end-to-end Lean formalization, and external
algebra/game review are the next high-value proof-hardening tasks.

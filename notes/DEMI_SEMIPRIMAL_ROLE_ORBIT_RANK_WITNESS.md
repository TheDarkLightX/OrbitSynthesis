# Role-orbit rank for the one-equation greatest-region converse

**Status:** new theorem strengthening, 2026-08-15. This note is stacked on the
generator-compressed converse. It replaces the common generating prefix plus
two tag coordinates by three automorphism-orbit-separated generating tuples.
The result is not yet Lean-formalized or externally peer reviewed. Publication
novelty and legal conclusions remain **UNKNOWN**.

## 1. Three-role orbit rank

Let `B` be a nontrivial finite subalgebra of a finite algebra `A`. For `k>=1`,
write

```text
Gen_k(B)={x in B^k : Sg_A(x)=B}.
```

The internal automorphism group `Aut(B)` acts diagonally on `Gen_k(B)`. Define

```text
rho_3(B)=min{k>=1 : |Gen_k(B)/Aut(B)|>=3}.
```

Call this the **three-role orbit rank**.

The rank is always finite. If `g` is a minimum nonempty generating tuple for
`B` and `b_0!=b_1` lie in `B`, then

```text
(g,b_1,b_0),
(g,b_0,b_0),
(g,b_0,b_1)
```

all generate `B` and lie in three distinct `Aut(B)`-orbits. An automorphism
mapping one to another would fix `g` coordinatewise, hence would be the
identity on `B`, contradicting the distinct tags. Therefore

```text
rho_3(B)<=d(B)+2,
```

where `d(B)` is the minimum nonempty generating rank.

The previous PR #33 theorem used this universal upper bound directly. The new
construction uses the exact orbit rank.

## 2. Rank-sensitive converse theorem

Let `A` be a finite quasi-primal algebra that is not demi-semi-primal. Choose a
graph-maximal nonextendable internal isomorphism

```text
phi:B->C
```

minimizing `rho_3(B)` among graph-maximal obstructions. Put

```text
rho(A)=rho_3(B).
```

Choose three generating tuples in distinct `Aut(B)`-orbits:

```text
a,p_0,p_1 in Gen_rho(A)(B).
```

Transport them by `phi`:

```text
a'=phi(a), q_0=phi(p_0), q_1=phi(p_1).
```

Use the same critical and dead observations as the previous converse:

```text
critical: (a,b_0),
dead:     (p_1,beta), (q_0,gamma),
```

where `b_0 in B`, `beta in A-B`, and `gamma in A-C`.

At the critical observation permit `p_0,p_1`, close those transitions under
the internal groupoid, make the two dead observation orbits outputless, and
use self-loops elsewhere.

### Theorem 1 — role-orbit compressed converse

The resulting shared-term safety instance has state arity

```text
rho(A),
```

has two separately term-winning domains

```text
W_L={a,p_0},
W_R={a',q_1},
```

and has no term-winning common upper bound.

### Why the three orbit conditions are sufficient

Each of `a,p_0,p_1` generates all of `B`. Therefore an internal isomorphism
mapping any one of them determines its action throughout `B`.

Pairwise distinct `Aut(B)`-orbits prevent source-side collisions among the
three roles. A source-to-target collision, composed with `phi^-1`, would give
the same forbidden source automorphism. A collision involving `beta` or
`gamma` would properly extend `phi` or `phi^-1`, contradicting graph
maximality.

Since `a` generates `B`, the stabilizer of the critical observation acts
trivially on `B`; hence its two displayed outputs are exact. Quasi-primal
interpolation then patches the one-sided tables. The old dead-state argument
shows that every common upper bound must add `p_1` or `q_0`, both losing.

Thus `rho_3(B)` is not merely an encoding statistic. It is the exact minimum
state arity for this generic three-role obstruction schema: three distinct
source roles require three distinct `Aut(B)`-orbits of generating tuples.
This is not claimed to be a lower bound against every imaginable no-greatest
gadget.

## 3. One equation without projection-only separation

At minimum role rank, an unsafe flattened transition may be constant as a
tuple of coordinates, so no alternate coordinate projection need differ from
the first projection. The projection-only separator from PR #33 is therefore
not universal at the sharper rank.

Use a generated-value separator instead.

Let `p(x)=x_1`. Broaden the safe relation exactly as before: retain the
critical transitions, keep the dead observations empty, and permit every
output elsewhere.

For each unsafe internal-groupoid orbit choose a representative `x`. The tuple
`x` contains a role that generates `B` or `C`; at a dead observation it also
contains an outside value. Hence `Sg_A(x)` is nontrivial. Choose

```text
c_x in Sg_A(x)-{p(x)}.
```

Transport `c_x` through the orbit. This is path-independent: any internal
automorphism fixing the complete tuple `x` fixes every coordinate of `x`, and
those coordinates generate `Sg_A(x)`, so the automorphism is the identity on
that subalgebra.

Define

```text
g(x)=p(x)                 on safe tuples,
g(psi(x))=psi(c_x)        on an unsafe orbit.
```

Then

```text
g(x) in Sg_A(x)
```

and `g` commutes with every internal isomorphism. By quasi-primal
interpolation, `g` is an original-signature term. Injectivity preserves
`psi(c_x)!=p(psi(x))`, so

```text
x is safe iff p(x)=g(x).
```

### Theorem 2 — one-equation role-rank converse

Every non-demi-semi-primal finite quasi-primal algebra has a no-greatest
shared-term safety instance of state arity `rho(A)` whose safe relation is one
original-signature equation.

## 4. Exact three-element classification

The primary implementation and a separately written no-import reconstruction
exhaust all 27 unary expansions of the three-element discriminator algebra.
They recover the established classification

```text
15 demi-semi-primal,
12 non-demi-semi-primal.
```

For every one of the 12 non-demi expansions,

```text
rho(A)=3.
```

The exact generating-orbit counts at the selected source subalgebra are either

```text
(0,1,3)
```

or

```text
(1,2,4)
```

for arities `1,2,3`. Thus arity three is also the exact lower bound inside the
three-role schema for all 12 examples.

This strictly improves the generator-tag construction in six cases:

```text
generator-tag arity 4 -> role-orbit arity 3.
```

The complete principal-row census changes from

```text
full-list construction:       236,196
generator-tag construction:   131,220
role-orbit construction:       26,244
```

## 5. Practical model reduction

Across the 12 non-demi unary expansions, compiling the principal games to the
exact eager domain model gives:

| Quantity | Generator tags | Role orbits |
|---|---:|---:|
| states | 648 | 324 |
| observations | 1,944 | 972 |
| groupoid components | 1,800 | 876 |
| candidate rules | 101,436 | 19,392 |
| CNF variables | 102,084 | 19,716 |
| hard clauses | 103,062 | 20,010 |

The reduction occurs before SAT, MaxSAT, or lazy conflict learning.

For each of the six strictly improved expansions, the eager principal model
shrinks from

```text
81 states, 243 observations,
15,144 candidate rules,
15,225 variables,
15,360 hard clauses
```

to

```text
27 states, 81 observations,
1,470 candidate rules,
1,497 variables,
1,518 hard clauses.
```

For Quackenbush `Q`, PR #33 had already reached the exact role rank:

```text
|Gen_1(B)/Aut(B)|=1,
|Gen_2(B)/Aut(B)|=2,
|Gen_3(B)/Aut(B)|=4.
```

Thus its state arity remains three, with the same 1,762 candidate rules and
1,789-variable eager model.

## 6. Implementation and evidence

Public module:

```text
src/orbitsynthesis/role_orbit_witness.py
```

Key APIs:

```text
generating_tuple_orbit_representatives
three_role_orbit_basis
role_orbit_minimal_maximal_nonextendable_internal_isomorphism
build_role_orbit_no_greatest_region_witness
audit_role_orbit_no_greatest_region_witness
build_role_orbit_principal_no_greatest_region_witness
audit_role_orbit_principal_no_greatest_region_witness
```

Independent reconstruction:

```text
research/tournaments/2026-08-15-role-orbit-rank-converse/
  audits/independent/audit_role_orbit_rank_independent.py
```

It checks the role-rank lower census, one-sided and union feasibility,
generated-value separator, all principal rows, and exact eager-domain counts.

Independent semantic SHA-256:

```text
a33f884a4da2882f850a1b131c438133bcde355ecac5aa0bd2892fe0090b746f
```

## 7. Boundary

- `rho_3(B)` is optimal for the generic three-role obstruction schema, not yet
  for arbitrary one-equation safety games.
- Empty generating tuples and nullary signatures remain outside the current
  standalone-kernel convention.
- The result is not Lean-formalized or externally peer reviewed.
- Prior-art novelty remains unknown.
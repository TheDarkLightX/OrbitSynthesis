# Role-orbit rank greatest-region converse

Date: 2026-08-15  
Verdict: **the generic one-equation converse can be compressed to the exact
three-role automorphism-orbit rank of the obstructing subalgebra.**

## Theorem

For a nontrivial finite subalgebra `B`, let

```text
Gen_k(B)={x in B^k : Sg(x)=B}
```

and let `Aut(B)` act diagonally. Define

```text
rho_3(B)=min{k : |Gen_k(B)/Aut(B)|>=3}.
```

If a finite quasi-primal algebra has a graph-maximal nonextendable internal
isomorphism `phi:B->C`, then the generic no-greatest shared-term safety witness
can be built with state arity `rho_3(B)`. Among graph-maximal obstructions one
may choose the minimum such rank.

The three source-side roles are generating tuples in distinct `Aut(B)`-orbits:

```text
critical state a,
left output p_0,
right output p_1.
```

Each role pins an internal isomorphism on all of `B`; orbit separation replaces
the common generator prefix and explicit tags from the preceding construction.

The universal bound

```text
rho_3(B)<=d(B)+2
```

follows from the old tagged tuples, but can be strict.

## One-equation separator

At exact role rank, unsafe tuples need not admit one alternate coordinate
projection. Instead, for each unsafe internal-groupoid orbit choose a generated
value different from the first projection and transport it through the orbit.
Path independence follows because the flattened tuple generates its subalgebra.
The resulting operation preserves generated subalgebras and all internal
isomorphisms, hence is a term by quasi-primal interpolation.

The broad relation remains principal:

```text
safe(x) iff x_1=g(x).
```

## Exact three-element census

All 27 unary expansions of the three-element discriminator were checked.

```text
15 demi-semi-primal
12 non-demi-semi-primal
```

Every non-demi expansion has exact three-role rank

```text
rho_3=3.
```

Six of the twelve improve strictly over the generator-tag bound:

```text
4 -> 3 state coordinates.
```

Principal flattened-row counts:

```text
full listing:       236,196
generator tags:     131,220
role orbits:         26,244
```

## Aggregate eager-domain reduction

Across the 12 non-demi expansions:

| Quantity | Generator tags | Role orbits |
|---|---:|---:|
| states | 648 | 324 |
| observations | 1,944 | 972 |
| components | 1,800 | 876 |
| candidate rules | 101,436 | 19,392 |
| CNF variables | 102,084 | 19,716 |
| hard clauses | 103,062 | 20,010 |

For each of the six strictly improved expansions, candidate rules fall from
`15,144` to `1,470` before SAT or MaxSAT search.

## Quackenbush-Q checkpoint

For `B={0,1}` in `Q=(Q;d,u)`, the generating-orbit counts are

```text
arity 1: 1
arity 2: 2
arity 3: 4
```

so arity three is an exact lower bound for the three-role schema. The selected
roles are

```text
(0,0,0), (0,0,1), (0,1,0).
```

The principal game has 2,187 flattened rows, 104 unsafe rows in 98 groupoid
orbits, and an eager model with 1,762 candidate rules, 1,789 variables, and
1,817 hard clauses.

## Evidence

Primary checker:

```text
check_role_orbit_rank.py
```

Independent no-import reconstruction:

```text
audits/independent/audit_role_orbit_rank_independent.py
```

The independent reconstruction was run under ordinary and optimized Python
with byte-identical output.

```text
script SHA-256
bbadcf6a15c81e5d8f75889520dda33a24057855a8d2ecc9c872eaa7c51c9f44

output SHA-256
21197585ddd61f960f943309badfcf7146a1bd5eb32e4d8a899eff4ee422b4f9

semantic SHA-256
a33f884a4da2882f850a1b131c438133bcde355ecac5aa0bd2892fe0090b746f
```

## Boundary

- `rho_3(B)` is exact for this three-role obstruction schema, not a universal
  lower bound for every possible no-greatest game.
- The result assumes the quasi-primal interpolation theorem.
- Empty generating tuples and nullary signatures are outside the current
  kernel convention.
- Lean formalization, external review, and novelty review remain pending.

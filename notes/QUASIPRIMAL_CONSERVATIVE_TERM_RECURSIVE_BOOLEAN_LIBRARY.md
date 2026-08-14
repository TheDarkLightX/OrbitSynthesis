# Recursive Boolean function libraries and a `62/25` fixed-Q compiler

**Status:** exact manuscript strengthening, 2026-08-14. This note is stacked
on the plane-shared compiler. It preserves the fixed algebra, signed routers,
sibling-shared scalar program vectors, pivot-normalized anchor,
complement-relative binary branch, decoder, and final glue.

The new step shares not only identical high/low plane roots, but also every
recursive suffix subfunction inside the universal Boolean libraries. A primary
standalone reconstruction and a separately written no-import audit check the
semantics, cost recurrence, finite arities, analytic tail, and depth ledger.
The integrated theorem is not yet formalized end to end in Lean or externally
peer reviewed. Novelty and legal conclusions remain **UNKNOWN**.

## 1. Result

For every `r>=64` and every `f in CT_r(Q)`, there is one parameter-free
original-signature free-fanout scalar DAG with

```text
size < (62/25)*3^r/r.
```

Writing `C=ceil(log_2 r)`, the same construction satisfies

```text
depth <= r+C+2*ceil((4C+2)/3)+15.
```

In particular, its depth is `r+O(log r)` with leading coefficient one.

The preceding explicit global constant was `67/25=2.68`. The local
fixed-sign program-vector theorem remains unchanged: its leading scalar-output
constant is still exactly `4/3` in its declared model.

The exact charged upper ratio over `64<=r<=16384` is maximal at `r=64`:

```text
size*r/3^r = 2.473270139955782682...
```

This is bounded validation evidence, not an exact global optimum or a matching
lower bound.

## 2. Recursive Boolean-library lemma

Fix a local address cube `Q^t` and a subset `S` of `M` live rows. Consider all
Boolean functions

```text
beta:S->{0,1},
```

extended by zero outside `S`.

Recursively split `S` by the first address coordinate. For a table `beta`, its
three restrictions are roots in the corresponding child libraries. Combine
those three roots with one capacity-three positive signed router controlled by
the current address digit.

A capacity-three router has four discriminator nodes and depth two. All tables
at one coordinate, in every group, share the same one-digit scalar program
vector for that coordinate.

At a fixed recursion level the nonempty subsets form a partition of `S`. If
their sizes are `M_1,...,M_k`, then

```text
sum_i 2^M_i <= 2^M.
```

This follows repeatedly from `2^a+2^b<=2^(a+b)` for positive `a,b`.
Consequently all zero-extended Boolean tables on `S` have a shared
original-signature library using at most

```text
4*t*2^M + 5*t
```

operation nodes. The `5t` term deliberately overcharges one complete
one-digit program vector per address coordinate. The library depth above the
raw anchor and address inputs is at most

```text
2t+3.
```

The construction is scalar throughout. A Q-valued table still consists of two
distinguished scalar roots from the shared Boolean family.

## 3. Schedule and portfolio

Let `J` be the largest integer satisfying

```text
9*r^3*2^J <= 3^r.
```

Put

```text
T=floor(log_3(rJ)).
```

For each

```text
delta in {-2,-1,0,1,2},
```

define

```text
t=T+delta,
N=3^t,
g=ceil(N/J),
s=r-t,
P=3^s.
```

Partition the `N` local address words into `g` balanced consecutive groups.
Every group has at most `J` live rows.

For each group, build its complete recursive Boolean library. For each group
and each plane, one capacity-`P` positive router selects the required Boolean
root from the prefix assignment. The `2g` prefix routers cost

```text
g*(3P-1)
```

nodes and share one width-`s` program vector.

Two capacity-`N` positive routers then select the correct group high and low
outputs from the local address. They cost

```text
3N-1
```

nodes and share one width-`t` program vector. Decode once and glue once.

For each arity, choose the least exact charged candidate, breaking ties by the
smaller `delta`. This is a fixed five-element portfolio.

## 4. Exact charged ledger

Let the candidate groups have live sizes `M_1,...,M_g`. Its upper ledger is

```text
4t*sum_i 2^M_i + 5t          recursive Boolean libraries
+g*(3P-1)                     prefix plane routers
+S_P(t)+S_P(s)-2              group and prefix vectors, shared names
+(3N-1)                       two local group-selection routers
+(2r-1)+2+3+1                 fast anchor, decoder, glue, u(x_0)
+B_router+B_control.          complement-relative binary branch
```

This is an inclusive upper bound. Any additional hash-consing coincidences
only reduce the actual union.

## 5. Size proof

Write

```text
U=3^r/r.
```

### 5.1 Exact finite range

For every integer

```text
64<=r<=339,
```

the checker constructs all five candidate ledgers with exact integers,
selects the least, and verifies

```text
25*size*r < 62*3^r.
```

The finite maximum is the displayed `r=64` value.

### 5.2 Analytic tail

For `r>=340`, choose

```text
t=ceil(log_3(rJ)).
```

This candidate is one of `T` or `T+1`, hence belongs to the portfolio. It
satisfies

```text
rJ <= N < 3rJ,
g < 3r+1.
```

A residue-two induction gives

```text
J>=3r/2
```

from `r=340` onward. It is enough to check `r=340,341` in

```text
9*r^3*2^ceil(3r/2) <= 3^r;
```

increasing `r` by two multiplies the power-of-two part by `8`, while

```text
8*(342/340)^3 < 9.
```

#### Prefix main term

The prefix routers and leading term of `S_P(s)` contribute at most

```text
(3g+4/3)P.
```

Since `g<=N/J+1` and `N>=rJ`, their normalized cost is at most

```text
3r/J + 13/(3J)
<=2+26/(9r).
```

#### Recursive local libraries

The Boolean budget gives

```text
2^J <= 3^r/(9r^3).
```

Also `J<2r`, hence `N<6r^2`, and therefore `t<=2C`. Since `g<3r+1`,

```text
L_recursive/U
 <=4t*g/(9r^2)
 <=8C(3r+1)/(9r^2).
```

For `r>=340`, `C<=r/32`, so

```text
L_recursive/U <= (3r+1)/(36r).
```

#### Lower-order terms

The prefix half-width error is below `U/1000`. The coordinate vectors, local
width-`t` vector, group routers, anchor, decoder, glue, and `u(x_0)` are below
`33r^2` nodes and hence below `U/1000` from `r=340`. The binary routers and
binary controls each contribute another `U/1000`.

Thus

```text
size/U
 < 2 + 26/(9r) + (3r+1)/(36r) + 4/1000
 <=2 + 26/(9*340) + (3*340+1)/(36*340) + 4/1000
 <62/25.
```

The final comparison is an exact rational inequality.

## 6. Depth

Let `A=C+2` be the fast-anchor depth. A recursive local Boolean root has depth
at most

```text
A+2t+3.
```

The prefix routers add `s+1` levels after the maximum of the local roots and
their width-`s` controls. The two local group routers add `t+1` levels, and
the one-shot decoder and glue add four. Therefore

```text
D <= r+C+max(2t+11,ceil(log_2 s)+11).
```

The portfolio has `t<=T+2`. Since `J<2r` and `log_3 2<2/3`,

```text
t <= ceil((4C+2)/3)+2.
```

Also `ceil(log_2 s)<=C`. Hence

```text
D <= r+C+2*ceil((4C+2)/3)+15.
```

The finite range is checked by the same exact ledger.

## 7. Evidence

Primary checker:

`research/tournaments/2026-08-14-recursive-boolean-library/check_recursive_boolean_library.py`

It checks:

- exact Q-to-Boolean plane factorization;
- all `512` subsets of `Q^2`;
- all `19,683` Boolean tables across those subsets;
- `177,147` recursive semantic evaluations;
- the recursive cost bound and an effective wrong-branch mutation;
- selected width-three non-product subsets;
- all five candidate ledgers through arity 16,384;
- the exact finite range and analytic tail separately;
- the depth theorem; and
- normal/optimized byte equality.

A second checker independently reconstructs the recursive libraries, rail
recurrences, five-candidate portfolio, binary branch, finite proof, analytic
tail, and depth ledger.

Primary semantic SHA-256:

```text
fb47ab33d1efa4648e8c11811ff18b283b1b3990c0ab35bcbcfdd29c4f21a07a
```

Independent semantic SHA-256:

```text
a9f3fd40348d0040ff5baac1e284e712685c019f4f54f42b955c3c975a8b3005
```

## 8. Boundaries

The theorem does not alter the local `4/3` program-vector constant, prove a
matching global lower constant, determine the exact global optimum, or settle
the optimal additive depth term. It gives no formula or bounded-fanout bound
and makes no novelty or legal conclusion. The integrated construction is not
yet serialized and proved end to end in Lean.

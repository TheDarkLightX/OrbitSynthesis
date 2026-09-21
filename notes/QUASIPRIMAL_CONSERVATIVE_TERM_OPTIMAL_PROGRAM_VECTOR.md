# Sibling-shared program vectors for conservative Q-term DAGs

**Status:** exact local manuscript theorem. The construction and its scalar-output
lower bound have two independent no-author-import audits, deterministic normal
and optimized replays, mutation checks, and Lean proofs of the semantic rail
identities, exact cost recurrences, all-width upper envelope, and uniform
upper bound. A separate integrated source note now proves the all-arity
compiler using this vector; that compiler is not a lower-bound consequence of
the local theorem and is not yet formalized end to end in Lean. Publication
novelty, finite-width exact optimality, practical performance, patent freedom
to operate, and rights under an unsigned developer license remain **UNKNOWN**.

## 1. Scope and cost model

Fix

```text
Q=({0,1,2};d,u),
d(x,y,z)=z if x=y and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

Let `w>=1` and `q=3^w`. Work on the nonbinary branch, where the shared anchor
has value `A=2`; then

```text
one=u(A),  zero=u(one)
```

are legal dynamically generated names. Size counts scalar `d` and `u` nodes in
the union of the ancestor subgraphs of all distinguished output roots. The two
name nodes are charged, raw address variables have depth zero, fan-out is free,
and no nullary constants or payload wires are available.

The result concerns one fixed signed-router root sign, P or N, at a time. It is
not a simultaneous P-and-N bound, an unshared-formula bound, a bounded-fanout
bound, or a lower bound for an arbitrary integrated router that avoids exposing
these exact scalar controls.

## 2. Exact theorem

**Theorem (sibling-shared program vector).** For either fixed root sign, all
`2q` address-program controls of the signed discriminator router have one legal
address-only original-signature shared DAG of size `S(w)` and depth `D(w)` with

```text
3*S(w) <= 4q+15*3^ceil(w/2),
S(w)   <= 7q/3,
D(w)   <= 3+ceil(log_2 w).
```

Consequently

```text
S(w)=(4/3+o(1))q.
```

The number of distinct requested scalar functions is exactly `4q/3` for P and
`4q/3+1` for N. Hence every DAG in this declared scalar-output grammar needs at
least those numbers of operation nodes. The leading size constant is therefore
exactly `4/3` in this local model.

The first exact constructed sizes, including both names, are

| `w` | `q` | P nodes | N nodes | depth bound |
|---:|---:|---:|---:|---:|
| 1 | 3 | 5 | 6 | 3 |
| 2 | 9 | 20 | 21 | 4 |
| 3 | 27 | 57 | 58 | 5 |
| 4 | 81 | 151 | 152 | 5 |
| 5 | 243 | 398 | 399 | 6 |
| 6 | 729 | 1,098 | 1,099 | 6 |
| 7 | 2,187 | 3,112 | 3,113 | 6 |
| 8 | 6,561 | 9,083 | 9,084 | 6 |

Width zero uses only the two names and is a separate base case.

## 3. First-mismatch rails

For target word `t` and physical word `p`, let `B_p(t)` indicate that the first
mismatch exists and is not `(t_j,p_j)=(1,2)`, and let `G_p(t)` indicate that the
first mismatch is exactly that exceptional pair. Equality is the residual state
`(B,G)=(0,0)`. The rails are disjoint and compose over consecutive blocks by

```text
B_AB=d(B_A,G_A,B_B),
G_AB=d(G_A,B_A,G_B).
```

Writing `N_p=not B_p`, the third rail composes in the same layer:

```text
N_AB=d(G_A,B_A,N_B).
```

For one address digit `x`, the four non-name operation nodes are

```text
physical 0: B=d(x,A,one),       G=zero,
physical 1: B=d(one,x,zero),    G=zero,
physical 2: B=u(d(x,A,one)),    G=d(x,A,zero).
```

The final positive control pair is `(B,G)` and the final negative pair is
`(G,N)`. Boolean constants use `(1-c,c)` in a positive cell and `(c,c)` in a
negative cell, so no extra constant constructor is introduced.

## 4. Exact sharing and recurrence

Two semantic identities become literal root reuse in the constructed DAG:

```text
G_(a s)=G_a       when the physical suffix s contains no digit 2,
N_(a1)=G_(a2).
```

The first removes gain merges whose right rail is zero. The second lets every
eligible not-B rail point to its already materialized sibling gain rail.

Put `a=ceil(w/2)`, `b=floor(w/2)`, `A0=3^a`, and `q=3^w`. Let `R(w)` count the
complete `(B,G)` library and `E(w)` the complete `(B,G,N)` suffix library,
excluding the two names. Then

```text
R(1)=4,
R(w)=R(a)+R(b)+q+A0*(3^b-1)/2,

E(1)=4,
E(w)=R(a)+E(b)+2q-q/3+A0*(3^b-1)/2.
```

The top mixed/gain overlaps are

```text
O_P(w)=(3^(w-1)+1)/2,
O_N(w)=(3^(w-1)-1)/2.
```

For `w>=2`, the exact constructed sizes are therefore

```text
S_P(w)=2+R(a)+E(b)+A0*(3^b-1)/2+q-O_P(w),
S_N(w)=2+R(a)+E(b)+A0*(3^b-1)/2+q-O_N(w).
```

Induction gives `R(w)<=20*3^w/9` and `E(w)<=26*3^w/9`. Substitution in the
last display gives

```text
3*S(w)<=4q+15*3^ceil(w/2).
```

The uniform `7q/3` bound follows for `w>=4`; widths one through three are the
listed base cases. The child terms are `o(q)`, proving the leading `4/3` term.
The one-digit rails have depth at most three and every balanced merge adds one
layer, which proves `D(w)<=3+ceil(log_2 w)`.

## 5. Scalar-output lower bound

The gain family has `(q+1)/2` distinct functions. The sign-selected B/N family
has `q` distinct functions. The only cross-family identities are

```text
N_(a1)=G_(a2).
```

Their number is `(q/3+1)/2` for P and `(q/3-1)/2` for N. Inclusion--exclusion
therefore yields exactly

```text
P: 4q/3,
N: 4q/3+1
```

distinct requested scalar controls. Each is Boolean-valued, whereas `A` is
fixed at 2 and every raw address coordinate takes all three values. None is a
free terminal. One scalar operation node can root at most one new scalar
function, proving the lower bound.

This argument proves the leading constant only. It does not prove the exact
finite-width minimum, a global compiler lower bound, or an extra all-width
additive gate.

## 6. Evidence and boundary

Primary lane:

- `research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/REPORT.md`;
- `research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/check_native_scan.py`;
- `research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/check_optimal_scan.py`; and
- `research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/OptimalRailSemantics.lean`.

Independent audits:

- `research/tournaments/2026-08-13-program-vector-optimization/lanes/referee/kuhn_boolean_rail_audit/REPORT.md`; and
- `research/tournaments/2026-08-13-program-vector-optimization/lanes/algebraic/REPORT.md`.

Formal lane:

- `research/tournaments/2026-08-13-program-vector-optimization/lanes/formal_optimized/REPORT.md`; and
- `research/tournaments/2026-08-13-program-vector-optimization/lanes/formal_gap_closure/REPORT.md`.

The checkers cover exact semantics through bounded widths, structural counts,
recurrence arithmetic, mutation falsifiers, and normal/optimized equality. The
optimized Lean lane proves the rail algebra, one-digit bases, zero-gain reuse,
sibling identity, final decoding, exact arithmetic recurrences,
`3S<=4q+15*3^ceil(w/2)`, and `S<=7q/3`. Its formal cost object is a declared
recurrence ledger rather than a serialized hash-consed DAG; the executable
construction and independent structural audit provide the refinement
evidence. The follow-up formal lane proves the matched sharp depth recurrence,
truth-table extensionality, the bad/not-bad semantics, and injectivity of
those two families. The gain quotient and signed overlap inclusion-exclusion
needed for the final distinct-output census are not yet formalized.

The earlier `7q`, `6+2*ceil(log_2 w)` theorem remains correct historical
evidence. It is superseded as a local upper bound, not retroactively altered.

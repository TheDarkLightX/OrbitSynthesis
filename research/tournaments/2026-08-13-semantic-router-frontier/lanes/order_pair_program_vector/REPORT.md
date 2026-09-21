# Order-pair program vector: exact improved theorem

Date: 2026-08-13

Status: **new exact construction, independently executable; formal lane in progress.**

## Verdict

The frozen `7q` parallel program-vector theorem can be strengthened substantially.
For a signed router of address width `w>=1` and capacity `q=3^w`, the exact
projection-program vector admits a constant-free original-signature shared DAG
with an exact sign-specific node recurrence, depth

```text
3 + ceil(log_2 w),
```

and

```text
C_s(w) = (4/3 + o(1)) q.
```

Uniformly for either root sign,

```text
2 C_s(w) <= 5q - 1.
```

For `w>=2`, the vector itself has respectively

```text
positive root: 4q/3 - 1,
negative root: 4q/3
```

distinct nonconstant output functions.  Hence every single-output-gate DAG
with the same raw inputs needs at least that many operation nodes.  The new
construction therefore has the asymptotically optimal leading size constant
`4/3` for this exact frozen output vector.  This is an output-count lower bound,
not a claim of exact finite-width optimality.

The prior theorem remains valid and is preserved as a fallback.  This lane
changes neither the signed router nor the conditional status of the integrated
all-arity compiler.

## 1. The inner object: a three-state first-decision monoid

For a target address `t` and physical address `p`, let

```text
E_p(t) = [t=p],
G_p(t) = [the first mismatch is (t_j,p_j)=(1,2)],
L_p(t) = not E_p(t) and not G_p(t).
```

Exactly one of `E,L,G` holds.  Concatenating a left segment `A` and a right
segment `B` obeys the first-decision law

```text
state(AB) = state(B), if state(A)=E,
            state(A), otherwise.
```

Thus `E` is an identity and `L,G` are left zeros.  This is the three-element
monoid obtained by adjoining an identity to a two-element left-zero semigroup.
It is also the one-coordinate face monoid `{0,+,-}` after relabelling.

Encode the states by the exact Boolean pair

```text
E = (0,0),  L = (1,0),  G = (0,1).
```

On legal pairs, the fixed discriminator itself is the product:

```text
L_AB = d(L_A,G_A,L_B),
G_AB = d(G_A,L_A,G_B).
```

Both coordinates therefore compose with two discriminator nodes in one layer.
The earlier `(E,G)` representation used three nodes and two layers per merge.
The improvement is structural: it exposes the algebra already present in the
router program instead of implementing Boolean conjunction and disjunction
separately.

## 2. Exact one-digit terms

On the nonbinary branch let

```text
two=A, one=u(A), zero=u(u(A)),
```

under the explicit premise `A=2`.  For a target digit `x`, define

```text
a   = u(x),
g   = u(a),
l_2 = d(zero,x,a),
l_0 = d(x,A,a).
```

Then the three physical one-digit summaries are

```text
p=0: (L,G)=(l_0,zero),
p=1: (L,G)=(a,zero),
p=2: (L,G)=(l_2,g).
```

This uses four operation nodes beyond the two shared name nodes and has depth
three above the raw anchor/address inputs.  Exhaustive multi-output closure
confirms that four nodes are necessary for these four unary functions when the
shared names are free; that finite fact is not used as a generic lower bound.

## 3. Sharing the gain roots

The function `G_p` depends only on the prefix of `p` ending at its last digit
`2`.  If `p` contains no `2`, then `G_p=0`.  Consequently, among all width-`n`
physical words there are exactly

```text
(3^n+1)/2
```

distinct gain functions, including zero, and `(3^n-1)/2` nonzero gain classes.

Let `A(n)` count all nodes beyond the two shared names in a balanced package of
all `(L,G)` summaries.  Put `a=floor(n/2)` and `b=ceil(n/2)`.  The exact
recurrence is

```text
A(1)=4,
A(n)=A(a)+A(b)+3^n+3^a(3^b-1)/2  for n>=2.
```

The `3^n` term materializes every loss root.  For each left word only one gain
root is materialized for each nonzero right gain class; the zero class reuses
the left gain.  A direct induction gives

```text
3 A(n) <= 7*3^n.
```

The recurrence itself is much sharper: `A(n)=(3/2+o(1))3^n`.

## 4. Sign-aware upper roots

Write

```text
H_p = not L_p = E_p or G_p.
```

The same product gives

```text
H_AB = d(G_A,L_A,H_B).
```

At one digit,

```text
H_0=L_2, H_1=G_2, H_2=L_0.
```

More generally,

```text
H_(a1)=G_(a2).
```

Therefore an `H` root is built only for right-child words ending `0` or `2`;
a word ending `1` reuses an existing gain root.  If `X(n)` counts the extra
partial-`H` package, then

```text
X(1)=0,
X(n)=X(ceil(n/2))+2*3^(n-1)  for n>=2,
X(n)<=3^n-3.
```

At the top merge, let `h_s(w)` be the number of negative bottom cells whose
physical word ends in `1`.  Those cells require `(G,H)`, and their `H` root is
already a gain root.  Exact parity counting gives

```text
h_positive(w)=(3^w+3)/6,
h_negative(w)=(3^w-3)/6.
```

For `w>=2`, with `b=ceil(w/2)`, the complete vector count including the two
shared names is

```text
C_s(w)=2+A(w)+X(b)-h_s(w).
```

At width one, `C_positive(1)=C_negative(1)=6`.  For `w>=2`, the negative-root
construction has exactly one more node than the positive-root construction.
The first values are

| `w` | `q` | positive | negative | depth |
|---:|---:|---:|---:|---:|
| 1 | 3 | 6 | 6 | 3 |
| 2 | 9 | 20 | 21 | 4 |
| 3 | 27 | 66 | 67 | 5 |
| 4 | 81 | 151 | 152 | 5 |
| 5 | 243 | 428 | 429 | 6 |
| 6 | 729 | 1110 | 1111 | 6 |
| 7 | 2187 | 3184 | 3185 | 6 |

The displayed recurrence implies both

```text
2 C_s(w) <= 5*3^w-1
```

and

```text
C_s(w)=(4/3+o(1))3^w.
```

Balanced composition adds one operation layer per split, so the complete
projection vector has depth at most

```text
3+ceil(log_2 w).
```

No final complement layer is needed: the sign-aware `L` or `H` output is
formed directly at the root merge.

## 5. Matching leading lower bound

Put a partial order on digits with the sole strict comparison `1<2`, leaving
`0` incomparable with both.  Extend it lexicographically by first mismatch.
Then

```text
G_p(t)=[t<p],
H_p(t)=[t<=p],
L_p(t)=[t not<= p].
```

This order-theoretic description explains all sharing identities:

- the principal ideals `H_p` are pairwise distinct because `p` is their unique
  maximum;
- the `L_p` are pairwise distinct as their complements;
- the strict ideals `G_p` are classified by the prefix through the last `2`;
- `H_(a1)=G_(a2)` is exactly the case in which a principal ideal is also one
  of those strict ideals;
- for width at least two, the `L` and `H` families are disjoint.

For every physical word, one program slot is `G_p`; the other is `L_p` at a
positive bottom cell and `H_p` at a negative bottom cell.  Removing the shared
constant-zero gain class and the exact `H/G` overlaps yields

```text
positive root: 4q/3-1 distinct nonconstant outputs,
negative root: 4q/3 distinct nonconstant outputs.
```

A node computes only one function.  None of these nonconstant Boolean outputs
is a raw ternary address input.  Hence those counts are operation-node lower
bounds for any DAG realizing the exact ordered vector.  Together with the
recurrence, this proves asymptotic leading-constant optimality.

## 6. Deterministic evidence

The lane checker builds a concrete hash-consed original-signature DAG, walks
only nodes reachable from the `2q` distinguished roots, and checks:

- all nine products of the three legal pair states;
- an effective unguarded-gain mutation;
- exact node recurrence and depth for both signs through width seven;
- all `10,761,678` target/physical/sign projection cases through width seven;
- distinct output-function counts through width five;
- arithmetic bounds through width 500; and
- byte-identical normal and optimized receipts.

Recorded semantic SHA-256:

```text
bc2378444813857cb3943fff3b45164e21a486fc588b89c9125e6fbdbc2fd83d
```

The canonical rendered audit output SHA-256 (4,205 bytes) is

```text
dc2170109f22d30a4c994bc76503e964c5e535c3323fe333560364afc8d76abc
```

The raw committed `receipt.json` SHA-256 (3,239 bytes) is

```text
4f9909fd45e9590146f9de9aa3d6ef930c3513998edb77eb71e65a961482df97
```

Replay permits whitespace and object-key ordering differences while preserving
JSON types and every field, including the semantic digest. Duplicate keys and
non-finite numbers reject. `test_receipt.py` exercises the real bounded audit
CLI under ordinary and optimized Python against changed types, counts, digests
and fields. The original committed receipt bytes remain unchanged.

## 7. Scope and publication boundary

This result strengthens the exact nonbinary projection-program vector.  It
does **not** by itself discharge the manuscript's compiler interfaces
`(I1)--(I7)`, the all-binary complement-relative construction, two-plane
decoding, selector-table compiler, finite fallback, or same-DAG integration.
The end-to-end `O(3^r/r)` and `r+O(log r)` theorem therefore remains
conditional until those interfaces are reconstructed together.

Associative prefix computation and the identity-adjoined two-element
left-zero monoid are classical.  The potentially paper-relevant contribution
is the exact conjunction here: identification of the frozen router program
with that monoid, its two-rail realization by the original discriminator,
last-`2` gain-class sharing, sign-aware `H/G` root reuse, the charged recurrence,
and the matching output-count leading lower bound.  A targeted search has not
yet established publication novelty for that conjunction.  Novelty, patent
freedom to operate, and optimal finite-width constants remain **UNKNOWN**.

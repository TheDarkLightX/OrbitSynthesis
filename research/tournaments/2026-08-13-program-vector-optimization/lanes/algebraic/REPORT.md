# Algebraic program-vector optimization

Date: 2026-08-13

## Verdict

**PASS: an exact recursive terminal-mixed gain/loss construction has size
`(4/3+o(1))q` and depth at most `3+ceil(log_2 w)`.**  Here `q=3^w` and
the count is for one chosen P or N root sign.  It includes the two absolute
names and all `2q` physical control roots.  An explicit all-width envelope is

```text
3*operation_nodes <= 4q+15*3^ceil(w/2),
operation_nodes <= 7q/3.
```

The uniform bound is sharp for the N construction at `w=2`, where the exact
P/N sizes are 20 and 21.  A scalar-output count gives lower bounds `4q/3` and
`4q/3+1`, so the
new construction matches that lower bound in its leading term.  This is an
asymptotic statement only in the declared local, scalar, free-fanout shared-DAG
model; it is not an exact global minimum or a result about formulas.

The frozen baseline is at STATE SHA-256

```text
6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6
```

Its `7q` size and `6+2*ceil(log_2 w)` depth remain the comparison baseline.

## Exact theorem

Fix `w>=0`, `q=3^w`, and either signed-router root sign.  There is a
constant-free original-signature `{d,u}` multi-output shared DAG with raw
inputs `A,t_0,...,t_(w-1)` such that, under the premise `A=2`, its two roots
for every physical word `p in {0,1,2}^w` are exactly the frozen projection
controls.  The DAG has no payload dependency.  It also realizes either
Boolean constant mode with only the two name nodes.

For projection mode, the exact constructed sizes begin

| `w` | `q` | P nodes | N nodes | depth |
|---:|---:|---:|---:|---:|
| 0 | 1 | 2 | 2 | 2 |
| 1 | 3 | 5 | 6 | 3 |
| 2 | 9 | 20 | 21 | 4 |
| 3 | 27 | 57 | 58 | 5 |
| 4 | 81 | 151 | 152 | 5 |
| 5 | 243 | 398 | 399 | 6 |
| 6 | 729 | 1,098 | 1,099 | 6 |
| 7 | 2,187 | 3,112 | 3,113 | 6 |
| 8 | 6,561 | 9,083 | 9,084 | 6 |
| 9 | 19,683 | 26,772 | 26,773 | 7 |
| 10 | 59,049 | 79,642 | 79,643 | 7 |

The certified depth upper bound is two at `w=0` and
`3+ceil(log_2 w)` for `w>=1`.

## First-mismatch algebra

Let `L_p(t)` be one exactly when the first mismatch exists and is not
`(t_j,p_j)=(1,2)`.  Let `G_p(t)` be one exactly when the first mismatch is
that gain pair.  Equality is the residual state `(L,G)=(0,0)`.  Concatenated
blocks obey

```text
L_AB = d(L_A,G_A,L_B),
G_AB = d(G_A,L_A,G_B).
```

If the left block is equal, the equal first two discriminator inputs pass the
right rail.  Otherwise the disjoint one-hot left rails absorb the result.
This is the associative first-non-equal monoid encoded by `(loss,gain)`.

Under `A=2`, define

```text
one=u(A), zero=u(one).
```

For one address digit `x`, all generic rails use four operation nodes:

```text
physical 0: L=d(x,A,one),    G=zero,
physical 1: L=u(x),          G=zero,
physical 2: L=u(d(x,A,one)), G=u(u(x)).
```

Their nonconstant truth tables are `[0,1,1]`, `[1,0,1]`, `[1,0,0]`, and
`[0,1,0]`.  They are four distinct noninput scalar functions, so four nodes
are also necessary in this declared generic pair interface.

## Sharing the gain rail

When a right gain rail is identically zero,

```text
d(G_A,L_A,zero)=G_A
```

on the disjoint Boolean state domain.  The construction therefore points
directly to `G_A` and allocates no merge node.  Across all `b`-digit physical
right words there are exactly

```text
(3^b+1)/2
```

distinct gain rails including zero.  Each nonzero rail is identified by the
physical prefix ending at its last digit `2`; the later `0/1` suffix does not
matter.  Thus there are `(3^b-1)/2` distinct nonzero rails.

Put the longer half on the left: `a=ceil(w/2)`, `b=floor(w/2)`.  Let `R(w)`
be the exact generic `(L,G)` state-node count excluding `one,zero`.  Structural
hash-consing gives

```text
R(0)=0,
R(1)=4,
R(w)=R(a)+R(b)+3^w+3^a*(3^b-1)/2.          (w>=2)
```

The `3^w` term is one distinct loss merge per physical word.  The last term
is one gain merge for every left word and every distinct nonzero right gain
rail.  The zero class reuses the left rail.  Distinct loss roots, distinct
nonzero gain classes, dependency sets, and ordered `d` arguments rule out
unaccounted structural collisions.  The checker confirms this exact
recurrence through width ten.

## Terminal mixed-rail specialization

A generic full state is unnecessary at the final merge.  Let
`N_B=not L_B`.  The sign-selected first control is built directly:

```text
positive cell: M_AB=d(L_A,G_A,L_B),
negative cell: M_AB=d(G_A,L_A,N_B).
```

The full pair is `(M_AB,G_AB)` for a positive cell and `(G_AB,M_AB)` for a
negative cell.  The second formula returns zero after a left loss, one after
a left gain, and passes `N_B` after left equality, so it is exactly
`not L_AB`.

The load-bearing cross-rail identity is

```text
not L_(c1) = G_(c2)                             (every prefix c).
```

It follows directly by separating an earlier prefix mismatch from the equal
prefix case.  The right block recursively co-produces `(L,G,N)`.  Every
not-loss rail whose physical word ends in `1` points at the gain rail of its
`2` sibling.  Only the other two final-digit classes allocate a not-loss
merge.  Let `E(w)` be the exact extended-state node count, excluding the two
names.  With `A0=3^a`, `B0=3^b`, structural hash-consing gives

```text
E(1)=4,
E(w)=R(a)+E(b)+2*3^w-3^(w-1)+A0*(B0-1)/2.       (w>=2)
```

The terms after the child blocks are respectively one loss merge per word,
two-thirds of the not-loss merges after sibling reuse, and the distinct
nonzero gain merges.  The same identity makes a negative top mixed node
coincide structurally with an already-requested top gain node.  The exact
top overlap counts are

```text
O_P(w)=(3^(w-1)+1)/2,
O_N(w)=(3^(w-1)-1)/2.
```

They count even- or odd-parity prefixes respectively.  Consequently, for
`w>=2`, the exact operation count of the explicit hash-consed construction is

```text
S_P(w)=2+R(a)+E(b)+A0*(B0-1)/2+3^w-O_P(w),
S_N(w)=2+R(a)+E(b)+A0*(B0-1)/2+3^w-O_N(w).
```

At width one, a sign-specialized direct base gives `S_P(1)=5` and
`S_N(1)=6`; at width zero both sizes are two.

## All-width bounds and leading term

First, `R(w)<=20*3^w/9`.  Widths one through three are direct bases.  For
`w>=4`, put `A0=3^a`, `B0=3^b`; both are at least nine.  The induction reduces
to

```text
31*A0+40*B0 <= 13*A0*B0,
```

which follows already from `A0,B0>=9`.

Likewise `E(w)<=26*3^w/9`.  The same induction reduces to

```text
31*A0+52*B0 <= 13*A0*B0,
```

again immediate when `A0,B0>=9`; widths one through three are direct bases.
The exact top ledger simplifies to

```text
S_P(w)=4q/3+R(a)+E(b)-A0/2+3/2,
S_N(w)=4q/3+R(a)+E(b)-A0/2+5/2.
```

Since `B0<=A0`, the two child bounds give

```text
S_N(w) <= 4q/3+(83/18)A0+5/2.
```

For `w>=3`, `(83/18)A0+5/2<=5A0`; widths one and two are direct.  Thus

```text
3*S(w) <= 4q+15*3^ceil(w/2).
```

For `w>=4`, the same display is at most `7q/3`; widths zero through three are
direct.  Hence `S<=7q/3` uniformly for either root sign.

The child terms are `O(3^ceil(w/2))=o(q)`, so the exact top formulas give

```text
S_P(w)=(4/3+o(1))q,
S_N(w)=(4/3+o(1))q.
```

## Scalar-output lower bound

For `w>=1`, the distinct scalar controls number exactly

```text
P: 4q/3,
N: 4q/3+1.
```

One proof partitions them into:

1. `q` distinct sign-selected loss/not-loss functions;
2. `(q+1)/2` distinct gain functions, including zero; and
3. the cross-rail overlaps above, numbering `(q/3+1)/2` for P and
   `(q/3-1)/2` for N.

The elementary three-block recurrences

```text
L_(0c)=(L_c,1,1), L_(1c)=(1,L_c,1), L_(2c)=(1,0,L_c),
G_(0c)=(G_c,0,0), G_(1c)=(0,G_c,0), G_(2c)=(0,1,G_c)
```

prove distinctness and show that the only mixed/gain intersections are
`not L_(c1)=G_(c2)`.  Every control is Boolean, whereas each raw address input
takes the value `2` somewhere and `A` is constantly `2` on this branch.
Therefore no control is a free raw input.  Since one scalar `{d,u}` node can
materialize at most one new scalar function, the distinct-output counts are
gate lower bounds.  The executable checker independently enumerates these
counts through width five.

Thus the upper and lower bounds have the same `4q/3` leading term in this
declared local model.  This does not determine the exact minimum at finite
width or transfer to formulas, bounded fanout, another input convention, or
the integrated compiler.

## Native ternary and other reconstructions

The checker also constructs three deliberately less optimized variants.

| construction | uniform size | asymptotic size | depth |
|---|---:|---:|---:|
| frozen baseline | `7q` | at most `7q` | `6+2*ceil(log_2 w)` |
| native ternary state | `4q` | at most `4q` | `4+ceil(log_2 w)` |
| unpruned gain/loss pair | P `29q/9`, N `10q/3` | `(13/6+o(1))q` | `4+ceil(log_2 w)` |
| zero-gain shared generic rails | `3q` | `(2+o(1))q` | `4+ceil(log_2 w)` |
| terminal-mixed rails | P `7q/3`, N `22q/9` | `(4/3+o(1))q` | `4+ceil(log_2 w)` |
| recursive terminal-mixed rails | `7q/3` | `(4/3+o(1))q` | `3+ceil(log_2 w)` |

For the native variant, encode loss/gain/equal as `0/1/2`.  The associative
block law is the single node `S_AB=d(S_A,A,S_B)`.  It still needs two output
extraction nodes per physical state, which is why the one-node merge alone
does not beat the terminal-mixed Boolean rails.

An exact census of all 24 injective encodings of equal/loss/gain into two
bits finds four whose two coordinates each compose with one `d`: the positive
one-hot code, its coordinate swap, and their bitwise complements.  The frozen
negative code does not compose coordinatewise in two nodes, so the final
sign specialization is substantive rather than a relabeling.

## Depth and legality ledger

- `one=u(A)` and `zero=u(one)` cost two nodes and have maximum depth two.
- The generic one-digit rails have maximum depth three.
- Every balanced block merge adds one layer.
- Extended not-loss rails are co-produced recursively in the same balanced
  merge layers; the terminal merge adds one.  The total is at most
  `3+ceil(log_2 w)`.
- Every term uses only `d`, `u`, `A`, and raw address digits.  There are no
  nullary constants or hidden negations.
- Every projection output dependency is a subset of `{A,t_i}`.  No payload
  wire enters the program.
- The absolute meanings of `one,zero` require `A=2`; an `A=1` mutation fails
  already at width one.
- Constant programs use only the two names: positive `(1-c,c)`, negative
  `(c,c)`.
- All size statements use free fanout and scalar multi-output shared DAGs.

## Falsifiers and replay

The standard-library-only checker imports no Orbit implementation.  It
performs:

- 5,978,710 exact target/physical control-pair identities through width six
  across five independent constructions and both root signs;
- direct ROBDD replay of 242 projections and 20 constant modes through width
  four, with an effective target-control mutation for every projection;
- 9,268 concrete payload valuations through width two;
- exact structural materialization through width ten;
- all-width recurrence arithmetic through width 512; and
- the bounded scalar-output count and cross-rail identity through width five.

Effective counterexamples reject: the wrong ternary neutral, unguarded later
gain, a missing negative complement, a missing one-digit complement, eliding
a nonzero right gain, duplicating the cross-rail outputs, and changing the
anchor from two.

Replay:

```text
python3 research/tournaments/2026-08-13-program-vector-optimization/lanes/algebraic/check_algebraic_program_vector.py
python3 -O research/tournaments/2026-08-13-program-vector-optimization/lanes/algebraic/check_algebraic_program_vector.py
```

Normal and optimized runs both return `PASS` with semantic SHA-256

```text
647f91c6c85173bbcb275e43a2301a67c61a7fd4d703b4720664a1341d7277aa
```

Checker SHA-256:

```text
1680570460d8567bee54f73caa4a6f49265627b1cbed2f6a294867fa31a5f19d
```

## Nonclaims

This lane does not establish novelty, prior-art priority, patent or copyright
status, freedom to operate, Tau-license rights, practical performance, the
binary branch, a formula bound, bounded-fanout complexity, an integrated
compiler theorem, or an exact finite-width global optimum.  No manuscript,
frozen tournament artifact, or shared implementation was edited.

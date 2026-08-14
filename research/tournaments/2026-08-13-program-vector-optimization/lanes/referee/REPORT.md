# Fresh-room referee report: optimized exact program vectors

Date: 2026-08-13

## Verdict

**SALVAGED AS AN EXACT LOCAL THEOREM.**  The external log's formulas were not
available, but two independent reconstructions work.  The better uniform
ledger is a Boolean gain/loss representation:

```text
27 * size <= 100q < 108q = 27 * 4q,
depth <= 4+ceil(log_2 w),
q=3^w.
```

This includes every one of the `2q` physical control roots, the two dynamic
names, and every final negative-cell complement.  A direct ternary-state
construction independently gives `size<=4q-1` with the same depth.  Both
constructions cover either root sign, projection mode, and both constant
modes.  They are shared-DAG/free-fanout results on the nonbinary branch
`A=2`; they are not formula, binary-branch, or integrated-compiler theorems.

The frozen candidate contract was inspected at SHA-256

```text
6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6
```

No frozen frontier, note, or manuscript file was edited.

## Exact theorem supported by this lane

Let `w>=0`, `q=3^w`, and fix either signed-router root sign.  Let
`p,t in {0,1,2}^w` be a physical branch and requested address.  There is a
constant-free original-signature `{d,u}` multi-output shared DAG whose raw
inputs are `A,t_0,...,t_(w-1)` such that, whenever `A=2`, its two distinguished
roots for every `p` equal the exact projection-mode controls of the frozen
signed router.  The DAG is independent of routed payload wires.  For `w>=1`,

```text
27 * operation_nodes <= 100q,
operation_depth       <= 4+ceil(log_2 w).
```

At `w=0`, two name nodes and depth two suffice.  For either constant mode,
the complete vector reuses only the same two names and has depth at most two.

The size inequality is an upper bound for one chosen root sign.  It does not
claim that the P and N vectors are simultaneously materialized in that count.
Both signs are proved by the same construction and checked separately.

## Reconstruction A: gain/loss pair

Define disjoint Boolean signals

```text
L_p(t)=1  iff the first mismatch exists and is not (t_j,p_j)=(1,2),
G_p(t)=1  iff the first mismatch is (t_j,p_j)=(1,2).
```

Equality is the residual state `(L,G)=(0,0)`.  If adjacent segments have
states `(L_A,G_A)` and `(L_B,G_B)`, then exactly

```text
L_AB=d(L_A,G_A,L_B),
G_AB=d(G_A,L_A,G_B).
```

Indeed, an equal left segment has equal discriminator inputs and passes the
right state; a loss or gain has unequal inputs and returns the corresponding
left bit.  Thus a balanced merge costs two `d` nodes but only one depth layer.

### Original-signature base

Under `A=2`, put `one=u(A)` and `zero=u(one)`.  For one requested digit `x`,
the three physical branches use

```text
physical 0: L=d(x,A,one),  G=zero,
physical 1: L=u(x),        G=zero,
physical 2: L=u(d(x,A,one)), G=d(x,A,zero).
```

These are four non-name nodes.  Their truth tables are respectively
`[0,1,1]`, `[1,0,1]`, `[1,0,0]`, and `[0,1,0]`.

### Exact final controls

For a positive bottom cell the pair is already

```text
(L,G).
```

For a negative cell it is

```text
(G,u(L)).
```

This is the load-bearing complement charge.  It gives `(0,1)` in the equal
negative state, `(0,0)` in loss, and `(1,1)` in gain.  If the root is P, the
number of negative cells is `(q-1)/2`; if it is N, it is `(q+1)/2`.

### All-width size proof

Let `T(w)` be a pre-hash-consing construction upper ledger excluding the two
shared names and final negative complements.  Treating every requested merge
node as new (actual hash-consing can only reduce the count), balanced
bisection gives

```text
T(1)=4,
T(w)=T(floor(w/2))+T(ceil(w/2))+2*3^w.
```

Direct calculation gives `T(1)=4`, `T(2)=26`, and `T(3)=84`.  Hence
`9T(w)<=28*3^w` for these bases.  For `w>=4`, writing
`a=floor(w/2)`, `b=ceil(w/2)`, the induction closes because

```text
14*(3^a+3^b) <= 5*3^w.
```

For even and odd `w`, this reduces respectively to `28<=5*3^a` and
`56<=15*3^a`, with `a>=2`.

The worst sign therefore costs

```text
U(w) <= 2+T(w)+(q+1)/2.
```

For `w>=3`, the preceding bound and `q>=27` give

```text
U(w) <= (28/9+1/2)q+5/2 <= (100/27)q.
```

Widths zero, one, and two give worst-sign ledgers `2`, `8`, and `33`, so the
same integer inequality `27U(w)<=100q` holds there as well.

### Depth proof

The names have depths one and two.  The deepest one-digit state has depth
three.  Each balanced merge adds one, and the negative conversion adds at
most one.  The balanced split tree has height `ceil(log_2 w)`, proving

```text
depth <= 4+ceil(log_2 w).
```

## Reconstruction B: native ternary first-mismatch state

Encode

```text
loss=0, gain=1, equal=2.
```

Then the entire segment law is the single node

```text
S_AB=d(S_A,A,S_B).
```

The one-digit physical states are produced by three nodes:

```text
S_0=d(zero,x,A)       = [2,0,0],
S_1=d(zero,u(x),A)    = [0,2,0],
S_2=x                 = [0,1,2].
```

The claimed one-node composition does **not** make the output vector free.
Every physical state still needs two extraction nodes:

```text
positive: (d(zero,S,one), d(S,A,zero)),
negative: (d(S,A,zero),   d(S,A,one)).
```

If `R(w)` is the analogous pre-hash-consing state-node upper ledger, then

```text
R(1)=3,
R(w)=R(floor(w/2))+R(ceil(w/2))+3^w.
```

The elementary split inequality
`2*(3^floor(w/2)+3^ceil(w/2))<=3^w+3` proves
`R(w)<=2*3^w-3`.  Adding two names and `2q` extraction nodes gives
`size<=4q-1`.  Its depth is again at most `4+ceil(log_2 w)`.

The gain/loss construction has the better proved uniform constant because
positive outputs are already state roots and only negative cells require one
conversion.  The native construction is the simpler semantic explanation for
why one-layer composition is possible.

## Hidden-cost audit

| Attack | Result |
|---|---|
| All `2q` outputs | Every ordered physical branch has two distinguished roots; compressed state alone is not counted as the answer. |
| Both P/N signs | Checked separately.  The N sign has the larger `(q+1)/2` complement charge. |
| Final complements | Explicit `u(L)` per negative gain/loss cell; omitting it fails already at width one. |
| Anchor/value names | `u(A),u(u(A))` contribute two shared nodes.  Their absolute meanings are asserted only under `A=2`. |
| Address representation | Raw `Q`-valued target digits are free inputs to this local theorem.  Every output dependency is a subset of `{A,t_i}`; no payload enters. |
| Base indicators | Gain/loss charges four one-digit nodes; native state charges three. |
| Final pair extraction | Native encoding charges exactly two candidate nodes per physical state. |
| Fan-out | Child vectors are adjoined once and reused across the Cartesian merge.  The result does not transfer to formulas or bounded fan-out. |
| Constant modes | Positive `(1-c,c)` and negative `(c,c)` pairs reuse only `one,zero`. |
| Width zero | Handled separately with two names and depth two. |

## Effective counterexamples and scoped lower check

Lexicographically first witnesses found by the checker include:

- omitting the negative loss complement: width one, P root,
  `t=(0),p=(1)`, expected `(0,0)`, mutated `(0,1)`;
- unguarded later gain: width two, `t=(0,1),p=(1,2)`, expected loss
  `(1,0)`, mutated contradictory `(1,1)`;
- dropping the physical-two loss base: width one, `t=(0),p=(2)`;
- using native state directly as a control pair: width one,
  `t=p=(0)`, producing the non-Boolean pair `(2,1)`; and
- using `1` rather than the equal code `2` in native composition: width two,
  `t=(0,0),p=(0,1)`.

An exhaustive nine-row check in the declared gain/loss interface found no
composition with only one new `u/d` node when the available roots are raw
`L_A,G_A,L_B,G_B,0,1,2`.  The two displayed discriminator nodes pass.  This
is a scoped straight-line-interface lower bound, not a global lower bound on
all encodings or shared vectors.

All six bijective native encodings of equal/loss/gain were checked.  One-node
state composition works for each when its equal code is used, but final-pair
extraction costs remain load-bearing.  This finite extraction search does not
exclude cross-branch sharing outside its declared unary grammar.

## Replay evidence

The standard-library-only checker independently constructs hash-consed `d/u`
DAGs.  It materializes both reconstructions and both root signs through width
nine, compares every target/physical pair through width five, checks payload
semantics, checks both constant modes, and verifies the integer recurrences
through width 512.

Exact bounded counts per reconstruction are:

```text
projection control-pair checks     132,860
base-cell payload checks           265,720
constant-mode pair checks            1,456  (gain/loss lane)
```

Normal and `python -O` receipts are byte-identical.  Replay with:

```text
python3 research/tournaments/2026-08-13-program-vector-optimization/lanes/referee/check_gain_loss_vector.py \
  --out research/tournaments/2026-08-13-program-vector-optimization/lanes/referee/receipt.json

python3 -O research/tournaments/2026-08-13-program-vector-optimization/lanes/referee/check_gain_loss_vector.py \
  --out research/tournaments/2026-08-13-program-vector-optimization/lanes/referee/receipt_optimized.json

cmp -s research/tournaments/2026-08-13-program-vector-optimization/lanes/referee/receipt.json \
  research/tournaments/2026-08-13-program-vector-optimization/lanes/referee/receipt_optimized.json
```

Current hashes are recorded in `manifest.json`.

## Promotion boundary

This lane establishes a stronger local candidate by explicit all-width proof
and independent executable construction.  Before changing the frozen
manuscript, the project should:

1. obtain a second independent audit or Lean port of the gain/loss recurrence,
   original-signature base, sign conversion, and `100q/27` ledger;
2. update the compiler arithmetic rather than mechanically replacing every
   `7q` by `4q`; and
3. preserve the nonbinary `A=2`, free-fanout, multi-output, and conditional
   integrated-compiler boundaries.

No claim is made here about global optimality, ordinary formulas, the binary
branch, publication novelty, practical performance, patents, or FTO.

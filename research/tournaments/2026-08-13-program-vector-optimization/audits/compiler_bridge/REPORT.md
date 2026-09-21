# Independent compiler-bridge audit

Date: 2026-08-13  
Verdict: **PASS for both current realization interfaces (N) and (B);
promotion is mathematically supported after proof integration.**

## Result

For every `r>=64` and every total selector
`sigma:Q^r->{0,...,r-1}` that is invariant under simultaneous Boolean
complement, the constructions reconstructed in this lane give one legal,
constant-free, original-signature `{d,u}` shared DAG whose value is
`x_(sigma(x))`.  With

```text
L = 4+ceil(log_3(r^2)),
H = r-L,
M = 3^floor(log_3 H),
b = log_3 M,
P = 3^(r-b),
```

the independently charged bounds are

```text
size  < 34*3^r/r,
depth <= r+4*ceil(log_2 r)+9.
```

The size constant is deliberately conservative.  Exact integer replay over
`64<=r<=16384` has maximum charged ratio
`size*r/3^r = 14.925925925925929...` at `r=93`; this bounded maximum is not
claimed for all arities.

This closes the two unresolved interfaces in the current manuscript.  Its
(N) interface is exactly the nonbinary construction proved below; its (B)
interface is exactly the complement-relative binary construction proved
below.  In the older I1--I7 wording, I2--I6 therefore need not remain
black-box assumptions.

I1, the coordinate-selector characterization, is upstream of this lane.  The
current manuscript explicitly removes it from the hypothesis list by citing
Proposition 3.3; this audit did not reprove Proposition 3.1/3.3.  I7 is not
needed for asymptotic existence: finitely many arities can be absorbed because
`CT_r(Q)` is, by definition, a finite set of term operations; the named
Theorem 6.1 gives an explicit fallback.

Recommendation: integrate or cite the explicit N/B proofs here, then promote
Conditional Theorem 6.10.  If the paper is not ready to integrate them, state
the selector-parametric compiler theorem as the exact intermediate result
rather than continuing to assume semantically unspecified realization
interfaces.  This internal audit alone is not an external-peer-review or
publication gate, so merely deleting “Conditional” without carrying the
proof would overstate the manuscript evidence.

## Premise ledger

| premise | audit status | precise scope |
|---|---|---|
| I1 selector representation | **NOT REPROVED** | assumed total `sigma`, complement-invariant on the Boolean cube |
| I2 global anchor | **PROVED / REPLAYED** | exact `4(r-1)` operations, exact balanced depth `3ceil(log_2 r)` |
| signed P router used by I3/I4 | **PROVED / REPLAYED** | Boolean branch payloads, absolute controls on `A=2`, complement-relative controls on the binary cube |
| optimized P program vector | **PROVED / REPLAYED** | one root sign, `2*3^w` address-only roots, scalar free-fanout shared DAG |
| I3 two-plane nonbinary compiler | **PROVED / REPLAYED** | inclusive charged upper bound; actual cross-table hash sharing may only reduce it |
| I4 binary compiler | **PROVED / REPLAYED** | complement-invariant `sigma`, residual-first chunks, physical controls relative to `x_0` |
| I5 same-DAG substitution | **PROVED BY CONSTRUCTION** | each block vector is adjoined once and reused by all tables and both planes |
| I6 decoder and glue | **PROVED / REPLAYED** | one decoder, three new glue nodes, two glue levels |
| I7 finite fallback | **NOT RECONSTRUCTED** | unnecessary for big-O existence; use the named earlier compiler for explicit finite values |

No semantic gadget in I2--I6 is left as an assumption in this report.  The
all-width vector inequalities and the all-arity analytic estimates are
ordinary induction/inequality proofs backed by bounded executable replay;
they are not a serialized Lean proof of the integrated compiler.

## I2: exact anchor

On `Q={0,1,2}`, use

```text
d(x,y,z) = z if x=y, and x otherwise,
u(0)=1, u(1)=0, u(2)=1,
h(x,y) = d(x,u(u(x)),d(y,u(x),x)).
```

A nine-row check gives

```text
h(x,y)=2  iff x=2 or y=2,
h(x,y)=x  otherwise.
```

Fold `h` over `x_0,...,x_(r-1)` using the longer half on the left.  Induction
therefore gives an anchor `A` with

```text
A=2    off the Boolean cube,
A=x_0  on the Boolean cube.
```

Every combine allocates exactly four operation nodes.  The two child DAGs
have disjoint variable supports, so none of those four ordered nodes collides
with a child or another combine.  Hence the exact count is `4(r-1)`.  If
`D(r)` is the balanced depth, the longer-left split gives

```text
D(1)=0,
D(r)=D(ceil(r/2))+3=3ceil(log_2 r).
```

On `A=2`, the legal names are

```text
one=u(A),  zero=u(one).
```

They are ordinary charged operation nodes, not nullaries.

## Signed router and optimized program vector

The independent checker reconstructs

```text
P_1(x,c0,c1)=d(x,c0,c1),
N_1(x,c0,c1)=d(c0,x,c1),
P_h=d(P_(h-1),N_(h-1),P_(h-1)),
N_h=d(N_(h-1),P_(h-1),N_(h-1)),
```

with disjoint branch/control cells.  A P router of capacity
`q=3^(h-1)` has exactly

```text
(3q-1)/2 discriminator nodes and depth h.
```

Middle-child parity determines whether a bottom cell has P or N sign.

For target word `t` and physical word `p`, let `B_p(t)` be one when the
first mismatch exists and is not `(t_j,p_j)=(1,2)`, and let `G_p(t)` be one
when the first mismatch is that exceptional pair.  The P-root cell controls
are

```text
(B,G)       at even middle-digit parity,
(G,not B)   at odd middle-digit parity.
```

The reconstructed sibling-shared vector has exact P counts

```text
w:       1   2   3    4    5     6
S_P(w):  5  20  57  151  398  1098
```

and, for every `w>=1`,

```text
3*S_P(w) <= 4*3^w+15*3^ceil(w/2),
S_P(w)   <= 7*3^w/3,
D_P(w)   <= 3+ceil(log_2 w).
```

Width zero uses the two names.  This lane reconstructed the loss/gain merge,
zero-gain reuse, and `not-B_(a1)=G_(a2)` sibling reuse directly; it did not
import a frozen vector builder.

## I3: two-plane nonbinary compiler

Encode Q by legal Boolean planes

```text
0 -> (0,0),  1 -> (0,1),  2 -> (1,0).
```

For the local `b`-digit block there are `M=3^b` addresses.  Materialize all
`3^M` Q-valued local tables.  Each table uses two capacity-M P routers, but
every table and both planes reference the same width-b program vector.

For each prefix `p`, the selector induces the local table

```text
g_p(l)=(p,l)_(sigma(p,l)).
```

Two capacity-P prefix routers select the high/low roots of `g_p`, sharing one
width-`r-b` vector.  Decode only once:

```text
Dec(high,low)=d(d(high,one,A),zero,low).
```

The decoder has two discriminator nodes and two levels.  Its legal-code truth
table is exact; no behavior of the unused `(1,1)` code is assumed.

The inclusive charged nonbinary-side ledger, already reserving the unique
three-node final glue, is

```text
N_NB = (3M-1)3^M
     + (3P-1)
     + S_P(b)+S_P(r-b)-2
     + 4(r-1)+2+3.
```

The `-2` shares `one,zero` between the two vectors.  This is an inclusive
component upper bound: structural coincidences among different constant
table routers are not needed and can only make the actual DAG smaller.

Put `C=ceil(log_2 r)`.  Before glue, the explicit depth ledger is

```text
D_local  <= 3C+D_P(b)+b+1,
D_prefix <= max(D_local,3C+D_P(r-b))+(r-b)+1,
D_NB     <= D_prefix+2
         <= r+4C+7.
```

For size, `H>=r/2` and `r/6<M<=H` for `r>=64`.  The two-log reserve gives
`3^M<=3^r/(81r^2)`.  Writing `U=3^r/r`:

```text
local routers                         < U/27,
prefix routers plus prefix vector     < 32U,
local vector plus anchor/decoder/glue < U/2.
```

The last inequality follows from an upper bound below `7r` operation nodes
and `14r^2<3^r` for `r>=64`.

## I4: complement-relative binary compiler

On the Boolean cube define relative address bits

```text
z_i=0 iff x_i=x_0.
```

They are invariant under simultaneous complement.  Choose

```text
k=floor(sqrt r), q=3^k, h=k+1,
w=floor(log_2 q).
```

Partition the `r-1` relative coordinates into chunks of width at most `w`,
placing the short residual chunk first.  At each level, encode the `2^c`
live chunk words by the first `2^c` ternary router branches and point every
unused branch to the last live child.

A logical control table `f:{0,1}^c->{0,1}` is not installed as an absolute
constant.  Its physical wire is

```text
F(x)=x_0 xor f(z).
```

Use leaves `x_0,u(x_0)` and the equality/difference selector

```text
Sel(x_i,x_0,E,D)=d(d(x_i,x_0,E),d(x_i,x_0,D),D).
```

This allocates at most `3(2^c-1)` nodes and depth `2c+1` per physical
control.  All router instances at one level share its `2q` controls.

For the representative with `x_0=0`, these are the absolute P-vector control
bits and the router selects the requested branch.  Under simultaneous
complement, every payload and physical control is complemented.  Since `d`
is self-dual on the Boolean cube, the selected output complements too.  The
same selector index is therefore correct on both orbit members.  This is the
legality argument; treating the controls as literal 0/1 constants is false.

If `I` is the number of router instances and the chunks have widths `c_j`, a
standalone charged upper bound is

```text
B_router  = ((3q-1)/2) I,
B_control = sum_j 6q(2^(c_j)-1),
B_total   = B_router+B_control+1.
```

The final `+1` is `u(x_0)`.  In the united DAG it is already an internal node
of the anchor and is not charged twice.  For `r>=64`, elementary estimates
give

```text
B_router  < U/4,
B_control < U/4.
```

For example, `I<2^(r-1)`, `sqrt(r)<=r/4`, and
`3^(r-2floor(sqrt r))>=r^4` reduce the two inequalities to decreasing
one-variable bounds from `r=64` onward.

The intrinsic binary critical path is bounded by

```text
D_B,int <= (k+1)ceil((r-1)/w)+2w+1.
```

The older conservative ledger retained in the manuscript is

```text
D_B,ret = (k+1)ceil((r-1)/w)+2w+3ceil(log_2 r)+8.
```

Exact replay shows

```text
D_B,ret(338)=338,
D_B,ret(339)=338,
```

and 338 is the last arity at which this ledger is not strictly below `r`.
There are earlier isolated passes, so 339 is the eventual threshold, not the
first pass.  For `r>=900`, the standard `k>=30` tail reduces to

```text
k^3-27k^2-19k+9>0,
```

which is positive at 30 and increasing.  Crucially, 338 is a boundary for
the deliberately serial retained ledger.  It is not the critical-path
boundary of the same-DAG union.

## I5/I6: union, decoder, and glue

The union charges each object once:

- the anchor once;
- one local and one prefix vector, sharing their two name nodes;
- each vector once across every table, router instance, and both planes;
- the binary controls once per chunk level;
- `u(x_0)` by reusing the identical anchor subnode;
- one decoder; and
- one final glue.

Put `s=u(u(A))`.  The exact glue is

```text
Glue(A,B,N)=d(d(s,A,B),d(s,A,N),N).
```

The names already contain `s=zero`, so the glue adds exactly three new
discriminator nodes.  On the Boolean cube, `s=A` and it returns `B`; off the
cube, `A=2,s=0` and it returns `N`.  Its added depth is two.

The actual united-DAG depth is therefore

```text
max(3ceil(log_2 r)+2, D_B,int, D_NB)+2
<= r+4ceil(log_2 r)+9.
```

It is a maximum, never a sum of the two branches.  Over the complete replay
range `64..16384`, the nonbinary path dominates the intrinsic binary path.

Combining the component bounds yields

```text
size/U < 32+1/27+1/2+1/4+1/4 < 34.
```

## Restricted KPG/router barrier

The native KPG state encoding

```text
K=0, P=2, G=1,
merge(S_A,S_B)=d(S_A,2,S_B)
```

is correct and associative: it returns the first non-P state.  The checker
verifies its truth table and all 27 associativity rows.  It is an upper
construction, not a lower-bound principle.  This audit does not reproduce a
separate claimed `~4q` implementation count; the exact exposed-control
construction used above is already `(4/3+o(1))q`.

There is a valid restricted-family cut lemma.  If

1. a scalar control depends essentially on all `w` raw address inputs,
2. a syntactic cut forces that control to be completed before substitution,
   and
3. below the cut it traverses an otherwise untouched depth-`w+1` signed
   router,

then fan-in three forces at least `ceil(log_3 w)` pre-cut levels and the path
has length at least

```text
w+1+ceil(log_3 w).
```

This is **not** a lower bound for arbitrary original-signature shared DAGs.
An explicitly checked three-way mux interleaves payloads with an address
digit and has no all-address program-vector cut.  More generally a fused
router can avoid exposing these scalar roots, and the local/prefix compiler
overlaps the local payload path with the prefix-control path before taking a
maximum.  Thus no global `r+ceil(log_3 r)-O(1)` floor follows from the cut
argument.

## Optimization opportunities

The reconstructed ledger isolates the useful next targets.

- **Anchor depth.** The current `3ceil(log_2 r)` anchor is serially upstream
  of both nonbinary program vectors and is the largest explicit logarithmic
  coefficient.  A shallower ternary absorber, a fused anchor/rail
  construction, or slice-local naming could improve the additive term.
- **Interleaving.** The restricted cut lemma suggests optimizing outside the
  exposed-vector family: interleave partial first-mismatch states with router
  levels or fuse the decoder/router.  No such improvement is claimed here.
- **Binary branch.** The intrinsic binary path is already below the
  nonbinary path in the audited range.  Further work should target shared
  control size or replace the depth-two-per-bit equality tree; optimizing the
  conservative 338 threshold alone would not improve the current global
  critical path.
- **Schedule constant.** The observed charged ratios are far below 34.
  Tightening the reserve and floor-power transitions may improve constants,
  but the two-log reserve is load-bearing: replacing it by one logarithm
  fails at `r=6574`, where `H=M=6561` and the local library alone exceeds one
  Shannon unit.

## Evidence and killer falsifiers

The self-contained checker performs:

- 3,279 anchor evaluations through arity seven, with exact count/depth;
- 597,870 target/physical P-vector identities through width six;
- 4,632 full router target/payload cases through width two;
- all 128 compatible arity-two selector tables plus four deterministic
  arity-three tables through both compilers and the glue, totaling 1,260
  complete Q-tuples;
- exact integer size/depth replay for every `64<=r<=16384`; and
- KPG and interleaved-mux truth tables.

Effective negative controls reject:

- deleting one unary node from the anchor;
- swapping a physical control pair;
- swapping decoder planes;
- using absolute binary controls rather than `x_0`-relative controls;
- a non-complement-invariant selector;
- swapping the binary/nonbinary glue branches;
- replacing the two-log reserve with one logarithm;
- claiming strict `D_B,ret<r` at `r=338`; and
- summing branch depths instead of taking the same-DAG maximum.

Further accounting falsifiers, stated explicitly for future implementations,
are duplicating a program vector per table or plane, decoding every local
table rather than once at the output, charging padding as fresh live tables,
putting the residual chunk last, or treating shared fan-out as formula
duplication.

## Reproduction and frozen scope

```text
python3 research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge/check_compiler_bridge.py
python3 -O research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge/check_compiler_bridge.py
```

The two outputs must be byte-identical.  Frozen inputs at audit time:

```text
STATE.md                              6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6
FIXED_Q_TERM_COMPLEXITY_DRAFT.md      47e017956f2a8e7b9fc8103f78432b5725a673459abd542ae2ad2ef58cd79654
check_compiler_bridge.py              375f922cf91a7878d634faa4eceb648b89a907d8596c822346b2faee890445f6
semantic result                       73a43b1e4292b56824e82a471833e69252c52f212463f182a90df63703eec23e
```

Receipts and the lane manifest bind the final bytes; if the checker changes,
the hashes in this paragraph are superseded by that manifest.

## Nonclaims

This audit does not establish novelty, prior art, freedom to operate, patent
status, copyright status, rights under an unsigned license, practical
performance, formula-size bounds, bounded-fanout bounds, the optimal additive
depth, or a global router-family lower bound.  It does not edit or authorize
promotion of the manuscript.

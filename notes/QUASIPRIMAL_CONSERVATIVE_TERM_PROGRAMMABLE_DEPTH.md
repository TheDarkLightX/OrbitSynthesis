# Programmable projection routing for conservative Q-term DAGs

**Status:** manuscript theorem under independent review. The fixed gadgets and
bounded compiler have a deterministic normal/optimized receipt. The generic
proof below is not Lean-checked, and publication novelty, coefficient
optimality, patent scope, freedom to operate, and any relationship to private
Tau work remain **UNKNOWN**.

## 1. Theorem

Fix `Q=({0,1,2};d,u)`, where `d(x,y,z)=z` when `x=y` and `d(x,y,z)=x`
otherwise, and `u(0)=1`, `u(1)=0`, `u(2)=1`. Let `CT_r(Q)` be the conservative
parameter-free `r`-ary term operations. Size counts original-signature
operation nodes in a shared DAG, fan-out is free, and variables have depth
zero.

### Theorem -- simultaneous order-optimal size and programmable depth

Every `f in CT_r(Q)` has one parameter-free original-signature term DAG with

`size=O(3^r/r)`

and

`depth <= (3*log_6(3))*r + O(r/log r)`.

Together with the syntax-counting lower bound,

`r-log_3(log r)-O(1) <= Delta_r(Q) <= (3*log_6(3))*r+O(r/log r)`.

Thus the explicit asymptotic leading-coefficient interval narrows from
`[1,3]` to

`[1,3*log_6(3)] = [1,1.839441578296...]`.

Neither endpoint is claimed optimal.

## 2. Fixed projection gadgets

The compiler uses two exact original-signature discriminator skeletons. `R6`
has 13 discriminator nodes, dependency depth three, 18 control slots, and six
fixed control programs over `Q`. Exhaustive evaluation proves

`R6(p6_j;b0,...,b5)=b_j`

for all six targets and all `3^6` branch valuations. `R7` has 12 discriminator
nodes, dependency depth three, 16 Boolean control slots, and seven programs.
It satisfies

`R7(p7_j;b0,...,b6)=b_j`

for every Boolean branch valuation. Since `d` commutes with simultaneous
Boolean complement, the same identity holds in complement-relative form.
Consequently the binary branch uses `x_0` and `u(x_0)` as relative names and
does not assume unavailable global constants.

The exact skeletons and every program word are frozen in
`experiments/quasiprimal_programmable_projection_routing.py` and reproduced in
`research/tournaments/2026-08-13-paper-frontier/lanes/circuit/REPORT.md`.
This note does not claim that six is the maximum ternary projection capacity
at depth three.

## 3. Balanced programmable codes

For a finite set `X` of size `N` and fan-out `q>=2`, recursively divide every
non-singleton block into `min(q,t)` nonempty parts whose sizes differ by at
most one. The resulting tree has height at most `ceil(log_q N)` and at most
`N-1` internal nodes.

At any fixed level, the nodes partition the still-active points. Their local
child labels therefore combine into one total digit function on `X`; completed
paths receive arbitrary padding. Only one family of control functions per
level is needed. For successive chunks of sizes `N_1,...,N_m`, with
`P_j=product_(i<=j) N_i`, the number of routers telescopes:

`sum_j P_(j-1)(N_j-1)=P_m-1`.

This per-level sharing and exact telescoping are essential. Per-router control
compilation or sparse full code trees would not establish the claimed size.

## 4. Nonbinary compiler and size

Use the existing balanced absorbing anchor `A`, with `A=2` exactly when an
input is nonbinary, `A=x_0` on the binary cube, `size(A)=O(r)`, and
`depth(A)<=3*ceil(log_2 r)`. On the nonbinary branch,
`u(u(A)),u(A),A` name `0,1,2`.

Let

```text
H=max(1,floor(log_3(3^r/r))),
M=3^b, the largest power of 3 with M<=H,
P=3^(r-b).
```

Use the `b` coordinates as a local block. A balanced six-way recursive library
contains every `Q`-valued function on its `M` assignments. If `G(t)` counts
the library's new discriminator nodes, then

```text
G(0)=G(1)=0,
G(t)=13*3^t+sum_i G(t_i),
G(t)<=26*3^t.
```

The last bound follows by balanced splitting and induction. The prefix needs
at most `P-1` six-way routers. Split control coordinates into chunks of width
`g_3=ceil(log_3 r)` and compile each level's 18 control functions with the
existing ternary decision tree. Since every control has `O(3^g_3)=O(r)` size
and there are `O(r)` code levels, all control preprocessing is `O(r^2)`.
Thus the nonbinary block, prefix, controls, and anchor total `O(3^r/r)` nodes.

## 5. Binary compiler, depth, and composition

On the binary cube use relative bits `z_i=[x_i != x_0]`. Complementary tuples
have the same relative address, so a compatible coordinate-selector table has
one selected index per address. Split the relative coordinates into chunks of
width `g_2=ceil(log_2 r)`, route them with balanced seven-way codes, and compile
control leaves as `x_0` or `u(x_0)`. This branch uses `O(2^r+r^2)` nodes.

Let `L_6` and `L_7` be the sums of the balanced code heights over the
nonbinary and binary chunks, including the local block in `L_6`. Then

```text
L_6 <= log_6(3)*r+O(r/log r),
L_7 <= log_7(2)*r+O(r/log r).
```

The exact construction obeys

```text
D_nonbinary <= 3*ceil(log_2 r)+2+3*ceil(log_3 r)+3*L_6,
D_binary    <= 1+2*ceil(log_2 r)+3*L_7.
```

A final normal selector separates the binary and nonbinary branches and adds
two levels. Since `3*log_6(3)=1.839441...` and
`3*log_7(2)=1.068621...`, the nonbinary branch dominates. This proves the
theorem on the same DAG for which the size bound was counted.

Small arities are covered directly; unused router inputs are padded with an
existing child and are never selected.

## 6. Deterministic evidence and audit boundary

The checker is
`experiments/quasiprimal_programmable_projection_routing.py`. It checks:

- all 4,374 six-way and 896 seven-way projection cases;
- 896 complement-relative cases;
- all 128 compatible arity-two selector tables and fixed-seed arities three
  through five, totaling 1,992 full-table evaluations;
- the library recurrence through 128 points and structural formulas through
  arity 4,096; and
- effective gadget mutations, illegal absolute controls, omitted controls,
  per-node controls, sparse codes, binary-depth omission, and a
  non-complement-invariant selector table.

Normal and optimized runs agree at semantic SHA-256
`e663534756cf67ffb12fd9ae3fe722c465bd70cd91b73af1fb8084af1c0706dc`.
The receipt is
`runs/quasiprimal_programmable_projection_routing/summary.json`.

Finite replay checks implementations and recurrence arithmetic; it does not
prove the generic theorem. The generic argument above remains a manuscript
proof under independent review and awaits Lean formalization.

## 7. Prior art, provenance, and nonclaims

Lupanov local coding, Shannon counting, multivalued circuit synthesis,
multiplexer analysis, and linear-depth synthesis over finite bases are
classical. Russian and international sources already study depth versus
complexity for multivalued functional systems. Chinese-language results also
study ternary decomposition and reversible synthesis in different bases and
cost models. The focused search found no direct public match for these exact
`R6`/`R7` witnesses and the fixed incomplete-clone coefficient, but search
non-detection is weak negative evidence only.

The construction uses only public mathematics and independently written
OrbitSynthesis artifacts. It does not use Tau code, specifications, private
communications, or an unsigned developer license. This is a provenance
statement, not legal advice.

Do not currently claim:

- publication novelty or independence from all Russian, Chinese, or
  international prior art;
- an optimal depth coefficient or a matching leading lower bound;
- practical improvement at small arity;
- an ordinary unshared-tree bound;
- the same result for arbitrary quasi-primal algebras;
- Lean verification or peer review;
- any result about private Tau capabilities; or
- patent freedom to operate.

The smallest next mathematical target is either a checked formalization of the
balanced-code sharing and complement-relative induction, or a construction
with more than six ternary projections per depth-three layer.

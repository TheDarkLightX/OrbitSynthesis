# Integrated sibling-vector compiler over the fixed three-element algebra

**Status:** manuscript theorem source note, 2026-08-13. The construction and
ledgers have a frozen independent no-author-import replay. This note is not an
external peer review, novelty opinion, patent/FTO opinion, license analysis, or
practical-performance claim.

## Theorem

Let `Q={0,1,2}` with

```text
d(x,y,z)=z if x=y, and d(x,y,z)=x otherwise,
u(0)=1, u(1)=0, u(2)=1.
```

Every conservative parameter-free `r`-ary term operation of this algebra has
one original-signature free-fanout scalar DAG with

```text
size  = O(3^r/r),
depth = r+O(log r).
```

For `r>=64`, the construction below has

```text
size  < 34*3^r/r,
depth <= r+4*ceil(log_2 r)+9.
```

Inputs are free and have depth zero; each `d` or `u` node costs one; sharing is
the union of ancestors in one DAG.

## Common selector and anchor

The coordinate-selector theorem supplies a total
`sigma:Q^r->{0,...,r-1}` such that `f(x)=x_(sigma(x))`, with `sigma` invariant
under simultaneous complement on the Boolean cube.

The ordered balanced fold

```text
h(x,y)=d(x,u(u(x)),d(y,u(x),x))
```

creates `A=2` off the Boolean cube and `A=x_0` on it. It has exactly `4(r-1)`
operation nodes and depth `3ceil(log_2 r)`. On `A=2`, the charged names are
`one=u(A)` and `zero=u(one)`.

## Nonbinary branch

For `r>=64`, set

```text
L=4+ceil(log_3(r^2)), H=r-L,
M=3^floor(log_3 H), b=log_3 M,
s=r-b, P=3^s.
```

Write `x=(p,l)` with `p in Q^s` and `l in Q^b`. For each fixed prefix define

```text
g_p(l)=(p,l)_(sigma(p,l)).
```

Build the universal library of all `3^M` Q-valued tables on `Q^b`. Encode
values by

```text
0 -> (0,0), 1 -> (0,1), 2 -> (1,0).
```

Every table uses two capacity-M P routers and all tables and both planes share
one width-b sibling-shared program vector. Two capacity-P P routers, sharing
one width-s vector, select the two roots of `g_p`. Decode once with

```text
Dec(high,low)=d(d(high,one,A),zero,low).
```

This is `0,1,2` on legal codes `00,01,10`. Thus the decoded result is exactly
`x_(sigma(x))`; no nullary constant occurs.

Let `S_P(w)` be the optimized fixed-P vector size. The local theorem gives

```text
S_P(w)<=7*3^w/3,
D_P(w)<=3+ceil(log_2 w).
```

An inclusive upper ledger for the nonbinary branch, already reserving the
final three-node glue, is

```text
N_NB=(3M-1)3^M+(3P-1)+S_P(b)+S_P(s)-2+4(r-1)+2+3.
```

Here `-2` shares the two names across vectors. The inequalities
`ceil(log_3(r^2))<=2log_3(r)+1` and `5+2log_3(r)<r/2` show `H>r/2`, hence
`M>r/6`; and
the two-log reserve gives `3^M<=3^r/(81r^2)`. In units
`U=3^r/r`,

```text
local routers                         < U/27,
prefix routers plus the prefix vector < 32U,
local vector plus fixed overhead      < U/2.
```

The last line uses fewer than `7r` nodes and `14r^2<3^r` for `r>=64`.

Put `C=ceil(log_2 r)`. Before final glue,

```text
D_local  <= 3C+D_P(b)+b+1,
D_prefix <= max(D_local,3C+D_P(s))+s+1,
D_NB     <= D_prefix+2 <= r+4C+7.
```

## Binary branch

On the Boolean cube put `z_i=0` iff `x_i=x_0`. Choose

```text
k=floor(sqrt r), q=3^k, w=floor(log_2 q).
```

Partition the `r-1` relative bits into chunks of width at most `w`, with the
short residual chunk first. Fix an injection
`iota_c:{0,1}^c->{0,1,2}^k` into the first `2^c` branch words. At each level a
capacity-q P router uses those live words; unused branches repeat the last
live child. Each logical control table is the corresponding P-control
coordinate for `iota_c(z)`. On the `x_0=0` representative, terminal word `z`
uses leaf `x_(sigma(0,z))`.

A logical control bit `f(z)` is represented physically as `x_0 xor f(z)`.
From leaves `x_0,u(x_0)`, use

```text
Sel(x_i,x_0,E,D)=d(d(x_i,x_0,E),d(x_i,x_0,D),D).
```

It returns `E` on equality and `D` on difference. A width-c physical control
costs at most `3(2^c-1)` nodes and depth `2c+1`; the `2q` controls are shared
by all routers at that level. On the representative `x_0=0` orientation the
network is ordinary branch selection. Global complement complements all
payloads and physical controls, while Boolean `d` is self-dual and `sigma` is
invariant, proving the other orientation.

If `I` is the number of router instances, residual-first ordering gives
`I<2^(r-1)`. Therefore

```text
B_router  = ((3q-1)/2)I         < U/4,
B_control = sum_j 6q(2^c_j-1)   < U/4.
```

The sufficient inequalities are `3rq2^r<3^r` and
`24r^2q^2<3^r`. After `q<=3^sqrt(r)`, their base-three logarithmic differences
are

```text
F_1(r)=(1-log_3 2)r-sqrt(r)-log_3(3r),
F_2(r)=r-2sqrt(r)-log_3(24r^2).
```

Both are positive at 64. Their derivatives are respectively
`1-log_3 2-1/(2sqrt(r))-1/(r ln 3)` and
`1-1/sqrt(r)-2/(r ln 3)`, both positive for `r>=64`.

For `m` chunks the intrinsic depth is

```text
D_B<=(k+1)m+2w+1.
```

For `k>=8`, `3k/2<=w<8k/5`; the integer comparisons `2^19<3^12` and
`3^5<2^8` give the required logarithmic bounds and enough lower fractional
margin. Thus

```text
D_B < 2r/3+(73/15)sqrt(r)+8/3 <= r+4C+7.
```

For the final inequality, replace `C` by the smaller `log_2 r`; the resulting
difference is positive at 64 and has derivative at least
`1/3-73/(30sqrt(r))>0`. The displayed upper ledger is
`log_3(2)r+O(sqrt r)`.

## Union and glue

The local and prefix vectors are each installed once; different consumers use
free fan-out. The anchor is installed once. The node `u(x_0)` is already an
anchor subnode. Put

```text
Glue(A,B,N)=d(d(zero,A,B),d(zero,A,N),N).
```

It returns the binary result on the Boolean cube and the nonbinary result off
it, costs three nodes, and adds two levels. Consequently

```text
size/U < 32+1/27+1/2+1/4+1/4 < 34,
depth  <= r+4ceil(log_2 r)+9.
```

The earlier unconditional compiler handles `r<64`.

## Evidence and boundaries

Independent evidence is frozen under

`research/tournaments/2026-08-13-program-vector-optimization/audits/compiler_bridge/`.

The checker reconstructs the algebra and construction without importing an
author implementation, rejects effective mutations, and emits byte-identical
normal and optimized receipts. The report SHA-256 is

`a8fbc93efb852ee07b83f65a6de74cc7ba7efd5d23448d76ea6ecd0d1e82826f`.

The theorem does not establish an optimal additive depth term, formula or
bounded-fanout complexity, an exact global size constant, novelty, FTO,
license rights, or practical speed. The integrated DAG is not yet formalized
end to end in Lean.

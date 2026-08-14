# Canonical-rank Boolean libraries for the fixed-Q compiler

**Status:** exact manuscript strengthening, 2026-08-14. This note is stacked
on the plane-shared compiler. It preserves the signed router, sibling-shared
program vectors, pivot-normalized anchor, complement-relative binary branch,
decoder, and final glue. It changes how Boolean local-table roots are shared
between different groups.

Two independently written standalone reconstructions check the semantic
factorization, exact charged ledgers through arity 16,384, effective mutations,
normal/optimized equality, and the analytic tail. The result is not yet
formalized end to end in Lean or externally peer reviewed. Novelty and legal
conclusions remain **UNKNOWN**.

## 1. Result and Pareto boundary

For every `r>=64` and every `f in CT_r(Q)`, there is one parameter-free
original-signature free-fanout scalar DAG with

```text
size < (12/5)*3^r/r.
```

Put `C=ceil(log_2 r)`. The same construction has

```text
depth
 <= r+C+ceil(2(C+1)/3)+2ceil(log_2(C+4))+23.
```

The exact checked size ratio is maximal at `r=64`:

```text
2.391548842960882081...
```

This is a size-focused Pareto strengthening. The preceding plane-shared
compiler retains the smaller explicit additive-depth coefficient. The present
DAG should not be described as simultaneously inheriting that different
construction's sharper depth bound.

The local fixed-sign program-vector theorem is unchanged: for `q=3^w` its
size is `(4/3+o(1))q`, its depth is at most
`3+ceil(log_2 w)`, and its declared scalar-output leading lower constant is
`4/3`.

## 2. The remaining duplication

The plane-shared construction observes that all high and low coordinates of
Q-valued tables come from one family of Boolean functions. It nevertheless
builds one Boolean-function library for every local group because the groups
have different physical rows.

That duplication is removable. Let the local address cube be partitioned into
balanced groups

```text
G_0,...,G_(g-1),
```

and let

```text
M=max_i |G_i|.
```

For a local row `y`, define

```text
gamma(y) = its group index,
rho(y)   = its zero-based rank inside that group.
```

For a Boolean table `beta_i:G_i->{0,1}`, choose an arbitrary padded extension

```text
hat(beta_i):{0,...,M-1}->{0,1}.
```

Then, on group `G_i`,

```text
beta_i(y)=hat(beta_i)(rho(y)).
```

Thus all groups draw their scalar roots from one universal family of exactly
`2^M` Boolean functions on canonical ranks. A Q-valued group table is an
ordered pair of roots from that family. Pairing existing roots is wiring and
adds no operation node.

## 3. Original-signature realization

Work on the nonbinary branch, where `A=2` supplies the charged names

```text
one=u(A), zero=u(one).
```

### 3.1 Rank and group digits

Let

```text
w=ceil(log_3 M), R=3^w,
e=ceil(log_3 g), G=3^e.
```

Write `rho` in `w` ternary digits and `gamma` in `e` ternary digits. Every
such digit is a Q-valued function of the original local address. Encode one
digit on the two legal Boolean planes, realize the two planes by capacity-N
positive signed routers, and decode once.

Two capacity-N router skeletons cost `3N-1` discriminator nodes; the decoder
costs two. Hence all rank and group digits jointly cost at most

```text
(w+e)(3N+1)
```

nodes. Every digit and both planes share the same width-t sibling-shared
program vector.

### 3.2 One Boolean rank library

For each Boolean function

```text
F:{0,...,M-1}->{0,1},
```

pad its leaf word to the capacity `R=3^w` and use one positive signed router
controlled by the rank digits. The `2^M` roots share one width-w program
vector. The complete charged upper count is

```text
((3R-1)/2)*2^M.
```

For each prefix assignment and group, the desired Q table supplies two
references into this common library: its high root and low root.

### 3.3 Prefix and final group selection

For every group and Boolean plane, one capacity-P positive router selects the
rank-library root belonging to the current prefix. The `2g` routers cost

```text
g(3P-1)
```

nodes and share one width-s vector.

Finally two capacity-G routers, controlled by the group digits, select the
active group's high and low prefix roots. They cost `3G-1` nodes and share one
width-e vector. Decode once and apply the established binary/nonbinary glue
once.

The rank-library values outside the active group are irrelevant because the
last selector is controlled by `gamma(y)`.

## 4. Schedule

For `r>=64`, let `J` be the largest integer satisfying

```text
9r^2*2^J <= 3^r,
```

and put

```text
K=J-3.
```

Let `m=3^b` be the largest power of three at most `K`, and set

```text
t=b+5,
d=9,
u=3^(t-d)=m/81.
```

The nine splitter coordinates have `3^9=19683` words. Put

```text
h=floor(K/u),
g=ceil(19683/h).
```

Partition the splitter words into `g` consecutive balanced groups. Their
largest live-row count is

```text
M=ceil(19683/g)*u <= K.
```

Finally put

```text
s=r-t, P=3^s,
w=ceil(log_3 M), R=3^w,
e=ceil(log_3 g), G=3^e.
```

For all arities in scope, `b>=4`, so the displayed `u=m/81` is integral.

## 5. Exact charged ledger

Let `S_P(z)` denote the exact positive sibling-vector count, including its two
name nodes. An inclusive upper ledger is

```text
(w+e)(3N+1)                       rank/group digit maps
+((3R-1)/2)2^M                    universal Boolean rank library
+g(3P-1)                           group-specific prefix routers
+S_P(t)+S_P(w)+S_P(s)+S_P(e)-6    four vectors, shared names
+(3G-1)                            final group selector
+(2r-1)                            fast anchor
+2+3+1                             decoder, glue, separate u(x_0)
+B_router+B_control.               complement-relative binary branch
```

Here `N=3^t`. Every scalar root, map digit, program vector, decoder, selector,
and generated name is charged. No Q-table pair is counted as an operation.

## 6. Size proof

Write

```text
U=3^r/r.
```

Exact integer replay proves the theorem for every `64<=r<=267`. The maximum
in that finite interval occurs at `r=64` and equals the displayed
`2.391548842960882081...` ratio.

For `r>=268`, the budget satisfies

```text
K>=3r/2.
```

It is enough to check `r=268,269`; increasing `r` by two multiplies the
relevant power of two by four and the power of three by nine, while

```text
4*270^2 < 9*268^2.
```

Since `m<=K<3m`,

```text
81<=h<=242,
g=ceil(19683/h).
```

The inequality `h<81K/m<h+1` gives

```text
r/m < 2(h+1)/243.
```

Therefore the prefix routers and the leading `4P/3` part of the width-s
vector contribute less than

```text
2(9g+4)(h+1)/177147
```

Shannon units. Direct evaluation of the 162 possible values of `h` gives the
maximum

```text
361982/177147
```

at `h=240`, `g=83`.

For the rank library, `M<=K`, `R<3M<6r`, and

```text
2^K <= 3^r/(72r^2).
```

Hence

```text
((3R-1)/2)2^M < U/8.
```

The rank/group maps, fixed nonprefix nodes, prefix half-width error, binary
routers, and binary controls are each below `U/1000` from `r=268` onward.
The base inequalities are recorded in the executable proof. Consequently

```text
size/U
 < 361982/177147 + 1/8 + 5/1000
 < 12/5.
```

This proves the all-arity claim.

## 7. Depth proof

The rank and group digits have depth at most

```text
D_map <= C+2+D_P(t)+t+3.
```

The Boolean rank roots, prefix roots, and final group roots then satisfy

```text
D_rank   <= D_map+D_P(w)+w+1,
D_prefix <= max(D_rank,C+2+D_P(s))+s+1,
D_group  <= max(D_prefix,D_map+D_P(e))+e+1.
```

Decoder and glue add four levels. Substituting
`D_P(z)<=3+ceil(log_2 z)` gives the exact schedule-dependent ceiling

```text
r+C+w+e+ceil(log_2 t)+ceil(log_2 w)+18.
```

Now `e<=5`, `b<=C-1`, `t<=C+4`, and

```text
w<=ceil(2(C+1)/3).
```

The last inequality follows from `M<2r<=2^(C+1)` and `3^(2/3)>2`. Therefore

```text
D
 <= r+C+ceil(2(C+1)/3)
      +2ceil(log_2(C+4))+23.
```

## 8. Evidence

Primary lane:

`research/tournaments/2026-08-14-canonical-rank-library/`

Independent no-import audit:

`research/tournaments/2026-08-14-canonical-rank-library/audits/independent/`

The primary checker covers canonical-rank factorization, Q-plane pairing,
rank/group mutations, 1,728 selector reconstruction rows, exact finite and
tail arithmetic, and every charged row through arity 16,384. The independent
checker exhausts all 512 coordinate-selector tables on `Q^2` and independently
reimplements the recurrences and proof ledger.

## 9. Boundaries

This theorem proves no matching global lower constant, exact global optimum,
optimal additive-depth term, formula or bounded-fanout theorem, publication
novelty, or legal clearance. The canonical-rank construction is not yet
formalized end to end in Lean.
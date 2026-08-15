# Hierarchical order-pair compiler below `49/5`

Date: 2026-08-15  
Status: **explicit construction, bounded semantic reconstruction, exact finite replay, and analytic tail**

## 1. Result

The residual prefix multiplexer need not be one giant signed router with one giant order-pair vector. Split its address into two consecutive blocks, share one vector across every bottom router, and share a second vector across the two top routers.

For every compatible coordinate selector and every `r>=64`, this produces one parameter-free original-signature shared DAG satisfying

```text
size  <(49/5)*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Thus the explicit constant is below

```text
49/5=9.8.
```

The exact finite maximum of the audited ledger is

```text
9.777777777777862...
```

at arity 88. The construction-specific normalized size has asymptotic limsup exactly `9`.

This is a fresh-room improvement of the reconstruction branch. It is not asserted to be part of the byte-exact local packet `01ddf456…`.

## 2. Construction

Retain the adaptive local block

```text
ell=ceil(log_3(r^2)),
H=r+1-ell,
M=3^floor(log_3 H),
b=log_3 M.
```

The core local block has `b` coordinates and `M=3^b` assignments. As before, build all `3^M` `Q`-valued local tables as two Boolean-plane signed-router roots, sharing one width-`b` order-pair vector.

Let the residual width be

```text
n=r-b.
```

Split it into

```text
a=floor(n/2),
c=ceil(n/2),
U=3^a,
V=3^c,
P=UV=3^n=3^r/M.
```

### Bottom stage

For each of the `V` top-block assignments and for each Boolean plane, build one positive capacity-`U` signed router. Its branch for bottom address `z` points directly to the already-existing local-table root determined by the full residual address.

All `2V` bottom routers share one width-`a` order-pair vector. Their router skeletons use exactly

```text
V(3U-1)
```

nodes.

### Top stage

The `V` high-plane bottom roots are the payloads of one positive capacity-`V` router. The `V` low-plane roots are the payloads of a second router. These two top routers share one width-`c` order-pair vector and use

```text
3V-1
```

skeleton nodes.

One decoder then recovers the `Q` value. The binary branch and final glue are unchanged.

### Semantic proof

On a nonbinary input:

1. the bottom vector programs every bottom router to select the actual bottom address;
2. in the router indexed by the actual top assignment, this returns the two existing plane roots for the correct local table;
3. the top vector selects exactly that top-assignment pair;
4. the local vector selects the actual core-local assignment inside that table; and
5. the decoder returns the required coordinate value.

The order-pair vectors depend only on their own address blocks and the shared anchor. The bottom vector is adjoined once for all `2V` bottom routers, and the top vector once for both top routers.

The companion hash-consed constructor checks 64 independent arity-three selectors and 16 independent arity-four selectors, comprising 3,024 complete input rows.

## 3. Exact residual count

Let `C_+(w)` be the exact positive-root order-pair vector count from PR #15. The two-stage residual union is

```text
R_2(n)
 =V(3U-1)+C_+(a)+(3V-1)+C_+(c)
 =3P+2V-1+C_+(a)+C_+(c).
```

The leading residual term is therefore `3P`, rather than

```text
3P+C_+(n)
```

from the single-stage compiler. Both additional vectors now have widths approximately `n/2`, so their contribution is exponentially lower-order relative to `P=3^n`.

The complete node ledger is

```text
N(r)
 =(3M-1)3^M
  +C_+(b)
  +R_2(r-b)
  +4r+3
  +B(r),
```

where `B(r)` is the explicit residual-first binary upper count.

## 4. Depth

Put

```text
L=ceil(log_2 r).
```

The anchor has depth at most `3L`. The local table roots have depth at most

```text
3L+b+ceil(log_2 b)+4.
```

The bottom stage has depth at most

```text
max(
  3L+b+ceil(log_2 b)+4,
  3L+3+ceil(log_2 a)
)+a+1.
```

This dominates the top-vector preprocessing depth, so the top stage adds `c+1` levels. Since `b+a+c=r`, `2b<r`, and hence

```text
ceil(log_2 b)+1<=L,
```

the top-stage output has depth at most

```text
r+4L+5.
```

One two-level decoder and the two-level final glue give

```text
depth<=r+4L+9.
```

The extra routing stage does not change the leading depth coefficient.

## 5. Finite range

Exact integer replay proves

```text
5*N(r)*r <49*3^r
```

for every `64<=r<1024`. The maximum occurs at `r=88`:

```text
N(88)*88/3^88
 =9.777777777777862...
 <49/5.
```

The depth inequality is checked over the same range.

## 6. Analytic tail

Assume `r>=1024` and write

```text
x=r/M,
g=r-M.
```

The adaptive-parameter proof gives

```text
64(ell-1)<=r,
50(ell-1)<=M,
x<151/50.
```

### 6.1 Lower residual terms

The uniform PR #15 bound gives

```text
C_+(w)<(5/2)3^w.
```

Therefore

```text
R_2(n)-3P
 <(9/2)V+(5/2)U.
```

After normalization,

```text
[R_2(n)-3P]r/3^r
 <x(7/U).
```

Here `a>=8`, so the right side is below `1/100`.

The local vector plus anchor, names, decoder, and glue also contributes below `1/100`, and the explicit binary branch contributes below `1/100`.

### 6.2 Local universal library

Its normalized count is strictly below

```text
3Mr/3^g.
```

There are three cases.

#### Transition case: `g=ell-1`

The inequalities above imply

```text
r/M<=51/50.
```

Moreover

```text
M^2<r^2<3M^2,
```

so `ell=2b+1` and `3^(ell-1)=M^2`. Hence the local library is below `3x`, while the leading residual skeleton is exactly `3x`. Their sum is below

```text
6(51/50)=153/25=6.12.
```

#### Nontransition case with `x<=2`

Now `g>=ell` and `3^g>=r^2`. The local library is below `3/x`. Together with the leading residual skeleton,

```text
3x+3/x<=15/2=7.5.
```

#### Nontransition case with `x>2`

Now `g>M` and `M>=729`. Exponential domination gives

```text
3Mr/3^g<1/100.
```

The leading residual term is below

```text
3x<453/50=9.06.
```

### 6.3 Tail sum

Including the three lower-order hundredths:

```text
transition case  <6.15,
x<=2 case        <7.53,
x>2 case         <9.10.
```

Thus every `r>=1024` is below `91/10`, and therefore below `49/5`.

## 7. Architecture-specific limsup

For this power-of-three local-block schedule,

```text
limsup_(r->infinity) N(r)r/3^r =9.
```

The upper bound follows from the tail analysis: away from a block transition the local library vanishes and the leading residual term is `3r/M`, with `r/M<3+o(1)`; at a transition the combined local and residual terms are at most `6+o(1)`.

For the lower bound, take arities immediately before successive changes from `M` to `3M`. Then

```text
r/M=3+o(1),
```

the local library and all vector/fixed terms are negligible, while the two-stage residual skeleton alone contributes

```text
3r/M=9+o(1).
```

This is a lower bound for the declared compiler architecture, not for arbitrary `{d,u}` DAGs computing the same operation class.

## 8. Consolidated theorem

**Theorem.** For every complement-invariant selector table and every `r>=64`, the explicit hierarchical compiler produces one parameter-free original-signature shared DAG with

```text
size  <(49/5)*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Together with the selector representation theorem, the same bound holds for every conservative `r`-ary term operation of `Q`.

## 9. Evidence boundary

The companion audit records:

```text
80 bounded selector tables,
3,024 complete semantic rows,
960 exact finite arities,
122,888 analytic-tail assertions,
all three tail cases with nonzero witnesses.
```

Normal and optimized receipts are byte-identical.

This result is independent of the local `01ddf456…` packet, its 65-source portfolio gate, and its Research Kernel object. Publication novelty and global leading-constant optimality remain unknown.

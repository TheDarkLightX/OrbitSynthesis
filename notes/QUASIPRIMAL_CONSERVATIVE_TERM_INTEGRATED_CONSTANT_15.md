# A total integrated compiler constant below `15`

Date: 2026-08-15  
Status: **fresh-room sharpening: exact finite replay plus analytic tail**  
Base theorem: explicit compiler reconstruction and PR #15 order-pair recurrence

## 1. Statement

For every complement-invariant coordinate selector and every `r>=64`, the explicit compiler in

```text
notes/QUASIPRIMAL_CONSERVATIVE_TERM_INTEGRATED_COMPILER_RECONSTRUCTION.md
```

has one parameter-free original-signature shared DAG satisfying

```text
size  <15*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

This strengthens the deliberately coarse constant `34`. It is independent of the byte-exact local packet identified by `01ddf456…`.

The proof consists of an exact check of the 448 arities `64<=r<512` and a closed analytic bound for every `r>=512`.

## 2. A sharper order-pair vector bound

Let `A(w)` be the PR #15 summary-node recurrence, excluding the two shared names:

```text
A(1)=4,
A(w)=A(a)+A(b)+3^w+3^a(3^b-1)/2,
a=floor(w/2), b=ceil(w/2).
```

Let `X(w)` be the partial-upper recurrence:

```text
X(1)=0,
X(w)=X(ceil(w/2))+2*3^(w-1).
```

For a positive root and `q=3^w`, the exact complete vector count is

```text
C_+(w)=2+A(w)+X(ceil(w/2))-(q+3)/6
```

for `w>=2`, with `C_+(1)=6`.

### Lemma 2.1

For every `w>=1`,

```text
2A(w) <=3*3^w+9*3^ceil(w/2).
```

**Proof.** Direct calculation handles `w<=8`. For the strong-induction step put `a=floor(w/2)` and `b=ceil(w/2)`. Multiplying the recurrence by two and applying induction gives

```text
2A(w)
 <=3*3^w
   +2*3^a+3*3^b
   +9(3^ceil(a/2)+3^ceil(b/2)).
```

If `a=b>=4`, then

```text
18*3^ceil(a/2) <=4*3^a,
```

so the extra terms are at most `9*3^b`. If `b=a+1` with `a>=4`, then

```text
9(3^ceil(a/2)+3^ceil((a+1)/2)) <=16*3^a,
```

and again the extra terms are at most `9*3^b`. `square`

PR #15 proves

```text
X(t)<=3^t-3.
```

### Lemma 2.2

For every `w>=7`,

```text
C_+(w)<=3*3^w/2.
```

**Proof.** Width seven is direct. For `w>=8`, put `a=floor(w/2)>=4`, `b=ceil(w/2)`, and `q=3^(a+b)`. Lemma 2.1 and the bound on `X` give

```text
C_+(w)
 <=4q/3+(11/2)3^b-3/2.
```

Since `3^a>=81`,

```text
33*3^b-9 <=3^(a+b)=q,
```

which is exactly the remaining inequality needed for `C_+(w)<=3q/2`. `square`

The finite audit checks the exact recurrence through width 500. Its largest ratio in the asserted range is

```text
C_+(7)/3^7 = 1.455875628715135...
```

## 3. Finite arities `64<=r<512`

The committed exact-integer audit evaluates the complete reconstructed ledger—local library, both order-pair vectors, prefix routers, global anchor, decoder, glue, and explicit binary branch—for all 448 arities.

It proves

```text
N_total(r)r/3^r <15.
```

The maximum is at arity 93:

```text
14.925925925925938...
```

No floating-point comparison is used to establish the inequality.

## 4. Analytic tail `r>=512`

Retain

```text
ell=ceil(log_3(r^2)),
H=r-4-ell,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b),
s=r-b.
```

### 4.1 Reserve and block lower bound

For `r>=512`,

```text
32(ell+4)<=r.
```

For `ell=12` this follows from `r>=512`. For `ell=m>=13`, the inequality

```text
[32(m+4)]^2 <=3^(m-1)
```

holds at `m=13` and propagates because the right side triples while the squared linear factor grows by less than three. Since `ell=m` implies `r^2>3^(m-1)`, the displayed reserve follows.

Hence

```text
H>=31r/32.
```

Maximality of the power `M` gives `H<3M`, and therefore

```text
M>31r/96,
r/M<96/31.
```

### 4.2 Prefix contribution

The prefix width is far larger than seven. Lemma 2.2 gives

```text
C_+(s)<=3P/2.
```

The two prefix router skeletons use `3P-1` nodes, so their normalized union with the shared vector is strictly below

```text
(3+3/2)P*r/3^r
 =(9/2)r/M
 <432/31.
```

### 4.3 Local universal library

Since `M<=r-4-ell` and `3^ell>=r^2`,

```text
3^M <=3^r/(81r^2).
```

Thus

```text
(3M-1)3^M*r/3^r
 < M/(27r)
 <=1/27.
```

### 4.4 Local vector and fixed infrastructure

The uniform PR #15 bound gives `C_+(b)<(5/2)M`. As `M<=r`,

```text
C_+(b)+4r+3 <=(13/2)r+3.
```

For `r>=512`, elementary exponential domination gives

```text
[(13/2)r+3]r/3^r <1/100.
```

### 4.5 Binary branch

The retained binary proof separates its normalized count into three strict bounds:

```text
router skeletons       <1/4,
shared control tables  <6/r^2 <1/4,
fixed overhead         <1/4.
```

Consequently

```text
N_binary(r)r/3^r <3/4.
```

### 4.6 Sum

Combining the four contributions gives

```text
N_total(r)r/3^r
 <432/31+1/27+1/100+3/4
 =308278/20925
 <15.
```

This proves the tail for every `r>=512`.

## 5. Consolidated theorem

**Theorem.** For every `r>=64` and every compatible coordinate selector, the explicit reconstructed compiler has one shared original-signature DAG with

```text
size  <15*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Combining with the selector representation theorem gives the same statement for every conservative `r`-ary term operation of `Q`.

## 6. Evidence and boundary

The companion audit checks:

```text
494 vector widths,
448 finite compiler arities,
95,238 analytic-tail side conditions.
```

Normal and optimized receipts are byte-identical.

This is a stronger independent reconstruction result than the reported `<34` local theorem. It should not replace the byte-exact `01ddf456…` manuscript until the two constructions and their ledgers are compared line-by-line by a fresh referee.

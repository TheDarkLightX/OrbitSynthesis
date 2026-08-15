# Adaptive order-pair compiler with constant below `113/8`

Date: 2026-08-15  
Status: **fresh-room optimization: exact finite replay plus analytic tail**

## 1. Statement

The integrated compiler reconstruction can be sharpened by moving each power-of-three local-block transition one arity earlier. For every compatible selector and every `r>=64`, the resulting explicit shared `{d,u}` DAG satisfies

```text
size  <(113/8)*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Since

```text
113/8 = 14.125,
```

this is close to the exact finite maximum of the schedule,

```text
14.123456790123541...
```

at arity 88.

This is an independent optimization of the reconstruction branch, not a claim that the byte-exact local `01ddf456…` packet uses the same schedule.

## 2. Adaptive parameters

Put

```text
ell=ceil(log_3(r^2)),
H=r+1-ell,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b),
s=r-b.
```

Then

```text
M<=H<3M.
```

Compared with the first reconstructed schedule `H=r-4-ell`, this permits the next local-block power one arity earlier. The compiler graph and semantics are unchanged: only the local/prefix split changes.

The total ledger is

```text
N(r)
 =(3M-1)3^M
  +C_+(b)
  +(3P-1)
  +C_+(s)
  +4r+3
  +B(r),
```

where `C_+` is the positive-root order-pair vector count and `B(r)` is the explicit binary upper count.

## 3. A `27/20` prefix-vector bound

The constant-15 proof established, for `w>=8`,

```text
C_+(w)
 <=4*3^w/3+(11/2)3^ceil(w/2)-3/2.
```

### Lemma 3.1

For every `w>=10`,

```text
C_+(w)<=27*3^w/20.
```

**Proof.** Widths 10 and 11 are direct. For `w>=12`, write

```text
w=a+b,
a=floor(w/2)>=6,
b=ceil(w/2).
```

The difference between `27/20` and `4/3` is `1/60`. It is therefore enough to prove

```text
(11/2)3^b-3/2 <=3^(a+b)/60.
```

After multiplying by 60, this becomes

```text
330*3^b-90 <=3^a*3^b,
```

which follows from `3^a>=3^6=729`. `square`

The committed recurrence audit checks the exact inequality through width 500. The largest ratio in the asserted range is at width 10:

```text
1.349455536926959...
```

## 4. Finite range `64<=r<1024`

The exact integer audit evaluates the full adaptive ledger for all 960 arities. It proves

```text
8*N(r)*r <113*3^r.
```

The maximum occurs at arity 88:

```text
N(88)*88/3^88
 =14.123456790123541...
 <113/8.
```

No floating-point comparison is used in the proof check.

## 5. Analytic tail `r>=1024`

Write

```text
g=r-M,
x=r/M.
```

### 5.1 Transition offset

For `r>=1024`,

```text
64(ell-1)<=r.
```

For `ell=13`, this follows from `r>=1024`. For `ell=m>=14`,

```text
[64(m-1)]^2 <=3^(m-1)
```

holds at `m=14` and propagates because the right side triples while the squared linear factor grows by less than three. Since `ell=m` implies `r^2>3^(m-1)`, the claim follows.

Thus

```text
H=r-(ell-1)>=63r/64.
```

Because `H<3M`,

```text
M>21r/64,
r/M<64/21<4.
```

In particular `M>=729`; write `M=3^b` with `b>=6`. Since `r<4M`,

```text
r^2<16M^2<27M^2=3^(2b+3),
```

and therefore

```text
ell<=2b+3.
```

At `b=6`,

```text
50(2b+2)=700<=729=3^b,
```

and the inequality propagates because the right side triples while the left side increases by 100. Hence

```text
50(ell-1)<=M.
```

Consequently

```text
x<3+(ell-1)/M<=151/50.
```

### 5.2 Prefix contribution

The prefix width is greater than ten. Lemma 3.1 gives

```text
C_+(s)<=27P/20.
```

The prefix skeletons and vector therefore contribute less than

```text
(3+27/20)P*r/3^r
 =(87/20)x
```

normalized units.

### 5.3 Local universal library

The local-library normalized contribution is strictly below

```text
3Mr/3^g.
```

There are three cases.

#### Case A: `g=ell-1`

Since `3^(ell-1)>=r^2/3`, the local contribution is below

```text
9/x.
```

Moreover

```text
x=1+(ell-1)/M<=51/50.
```

On that interval the function

```text
9/x+(87/20)x
```

is decreasing, so its maximum is at `x=1`:

```text
9+87/20=267/20.
```

#### Case B: `g>=ell` and `x<=3`

Now `3^g>=r^2`, so the local contribution is below `3/x`. The function

```text
3/x+(87/20)x
```

is increasing for `x>=1`, and hence is at most

```text
1+261/20=281/20
```

at `x=3`.

#### Case C: `x>3`

Then `g=r-M>2M`. Since `M>=729` and `x<151/50`, elementary exponential domination gives

```text
3Mr/3^g <1/100.
```

The prefix contribution is less than

```text
(87/20)(151/50)=13137/1000.
```

### 5.4 Lower-order and binary terms

The local vector, anchor, names, decoder, and glue satisfy

```text
[C_+(b)+4r+3]r/3^r <1/100
```

for `r>=1024`.

The explicit residual-first binary upper count also satisfies

```text
B(r)r/3^r <1/100.
```

For the latter, the router term is bounded by `6r(2/3)^r`, the shared-control term by `6r^2/3^(r-2sqrt r)`, and fixed overhead by `(4r+10)r/3^r`; each is below `1/300` at 1024 and decreases thereafter.

### 5.5 Tail sum

- Case A is below `267/20+1/50=13.37`.
- Case B is below

  ```text
  281/20+1/50
   =1407/100
   =14.07
   <113/8.
  ```

- Case C is below `13137/1000+3/100=13.167`.

Thus every `r>=1024` satisfies the claimed bound.

## 6. Consolidated theorem

Combining the finite range and analytic tail gives:

**Theorem.** For every `r>=64` and every complement-invariant selector table, the adaptive explicit compiler builds one parameter-free original-signature shared DAG with

```text
size  <(113/8)*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Together with the selector representation theorem, the same bound holds for every conservative `r`-ary term operation of `Q`.

## 7. Evidence boundary

The companion audit checks:

```text
491 vector widths,
960 finite compiler arities,
184,332 analytic-tail side conditions,
all three tail cases with nonzero witnesses.
```

Normal and optimized receipts are byte-identical.

The theorem is stronger than the reported local `<34` constant. Before publication, a fresh referee should compare the adaptive reconstruction with the byte-exact `01ddf456…` construction and decide whether to place the sharper constant in the main theorem or an appendix.

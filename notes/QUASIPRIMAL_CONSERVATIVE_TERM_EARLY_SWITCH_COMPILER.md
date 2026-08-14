# Early switching for the two-slice fixed-Q compiler

**Status:** exact manuscript strengthening, 2026-08-14. This note is stacked
on the fast-anchor and two-slice compiler theorems. It changes only the
schedule deciding when to use the ordinary local block and when to use the
wide/residual two-slice block. The signed router, sibling-shared program
vector, pivot-normalized anchor, binary complement-relative branch, decoder,
and final glue are unchanged.

A standalone reconstruction checks the decomposition, exact ledgers through
arity 16,384, effective mutations, the analytic base inequalities, and
normal/optimized equality. The result is not yet formalized end to end in Lean
or externally peer reviewed. Novelty and legal conclusions remain **UNKNOWN**.

## 1. Result

For every `r>=64` and every `f in CT_r(Q)`, there is one parameter-free
original-signature free-fanout scalar DAG with

```text
size  < (46/5)*3^r/r,
depth <= r+ceil(7*ceil(log_2 r)/5)+12.
```

The previous clean size bound was `(21/2)3^r/r`. The local fixed-sign program
vector is unchanged: for `q=3^w` it still has size
`(4/3+o(1))q`, matched leading scalar-output lower constant `4/3`, and depth
at most `3+ceil(log_2 w)`.

The new global size constant comes from switching to the two-slice compiler
slightly *before* the reserve contains all `2m` local rows. The wide table may
then exceed the old tiny-library allowance, but its temporary cost is more
than offset by reducing the prefix exponent by one.

## 2. Schedule

Put

```text
L=4+ceil(log_3(r^2)),
H=r-L,
m=3^b, the largest power of three not exceeding H.
```

Use the following complete integer partition:

```text
Mode 1: H <= 2m-5.  Use the ordinary m-point block Q^b.
Mode 2: H >= 2m-4.  Use the 2m-point wide slice plus m-point residual.
```

The former sufficient switch was `H>=2m`. The new threshold is not used as an
unproved exact optimality assertion. Exact replay happens to select the
smaller of the two charged ledgers at every `64<=r<=16384`, but the theorem
below needs only the displayed upper bounds.

## 3. Unchanged exact component ledgers

Write `S_P(w)` for the positive-root sibling-shared vector count, including
its two dynamic name nodes.

In Mode 1, with `s=r-b` and `P=3^s`, the nonbinary construction uses

```text
(3m-1)3^m                    universal local tables
+(3P-1)                       two prefix plane routers
+S_P(b)+S_P(s)-2              two vectors with shared names
+(2r-1)+2+3                   fast anchor, decoder, final glue.
```

In Mode 2, with `s=r-b-1` and `P=3^s`, it uses

```text
(9m-1)3^(2m)                 wide universal tables
+(3m-1)3^m                   residual universal tables
+(6P-2)                       four prefix routers
+S_P(b+1)+S_P(b)+S_P(s)-4    three vectors with shared names
+6                            two per-plane slice selectors
+(2r-1)+2+3                  fast anchor, decoder, final glue.
```

The complement-relative binary branch and one separately charged `u(x_0)`
node are united exactly as in the preceding compiler.

## 4. Mode 1 size proof

Write

```text
U=3^r/r.
```

The mode condition implies the sharper schedule ratio

```text
r/m <= 19/9.
```

The case `b=3`, `m=27`, is a finite base: for `r>=64` its admissible arities
all satisfy `H>=2m-4`, so Mode 1 is empty there.

Now let `b>=4`. First prove `L<=m`. If `L>m`, then `H<2m` gives
`r=H+L<3L`. Since `L>m>=81`,

```text
L=4+ceil(log_3(r^2))
 <=5+2log_3 r
 <7+2log_3 L
 <L,
```

a contradiction. Hence `L<=m`, so `r<3m` and

```text
L<=2b+6.
```

For `b>=4`,

```text
2b+1 <= 3^(b-2)=m/9;
```

this is equality at `b=4` and is preserved because the right side triples
while the left grows by two. Therefore

```text
L<=m/9+5,
r=H+L<=2m-5+m/9+5=19m/9.
```

The local universal library remains below `U/27`. The prefix routers and
width-`s` vector obey

```text
(3P-1)+S_P(s)
 < (13/3)P+5*3^ceil(s/2).
```

Since `3^r=mP`, the main term is at most

```text
(13/3)*(19/9)U = (247/27)U.
```

The half-width error, fixed linear group, binary routers, and binary controls
are each below `U/1000`, using the already proved bases

```text
5000*65<3^32,
7000*64^2<3^64,
192*2^64<3^50,
24*64^2<3^42,
```

and their monotone two-step or derivative tails. Thus

```text
size/U < 248/27+4/1000 < 46/5.
```

## 5. Mode 2 size proof

Let

```text
t=H-(2m-4)>=0,
x=r/m.
```

The unchanged schedule lemma gives

```text
x<=31/9.
```

The prefix routers and prefix vector have main contribution

```text
(22/9)x U,
```

plus a half-width error below `U/1000`. Let

```text
W=(9m-1)3^(2m)
```

be the wide universal library.

### 5.1 First exceptional boundary: `t=0`

Here `H=2m-4`. The finite `b=3` case lies below arity 64, so `b>=4`. The same
argument as in Mode 1 gives `L<=m`, and hence `2m<r<3m`. Writing
`c=ceil(log_3(r^2))`, this forces

```text
c=2b+2,
3^c=9m^2.
```

Since `r=2m+c`,

```text
x=2+(2b+2)/m <= 172/81.
```

Moreover

```text
W/U < x.
```

Therefore the wide library plus prefix main term is below

```text
(1+22/9)x U
 <= (31/9)*(172/81)U
 = (5332/729)U.
```

### 5.2 Second exceptional boundary: `t=1`

Now `H=2m-3`. Again `c=2b+2`, while

```text
x=2+(2b+3)/m <= 173/81
```

and the extra exponent gives

```text
W/U < x/3.
```

Thus the wide and prefix main terms are below

```text
(1/3+22/9)x U
 <= (25/9)*(173/81)U
 = (4325/729)U.
```

### 5.3 Tail: `t>=2`

The reserve gives `3^(L-4)>=r^2`. Since

```text
r-2m=L-4+t,
```

`t>=2` yields

```text
W/U < 1/x.
```

The function

```text
22x/9+1/x
```

is increasing for `x>=1`, so using `x<=31/9` gives

```text
W/U + prefix-main/U
 < 682/81+9/31
 = 21871/2511.
```

The residual library, prefix half-width error, fixed linear group, binary
routers, and binary controls are each below `U/1000`. All three Mode 2 cases
are therefore strictly below `(46/5)U`.

## 6. Depth

The schedule changes only which already proved Mode 1 or Mode 2 construction
is chosen. Their depth proofs are unchanged. With

```text
C=ceil(log_2 r),
```

the common ceiling remains

```text
r+ceil(7C/5)+12.
```

The early switch does not add a router level, selector level, or decoder.

## 7. Deterministic reconstruction

The standalone checker is

`research/tournaments/2026-08-14-early-switch-compiler/check_early_switch_compiler.py`.

It performs:

- 1,728 exact wide/residual reconstruction rows from 64 deterministic
  selector tables on `Q^3`;
- an effective wrong-slice mutation;
- exact Mode 1, Mode 2, binary, and united-DAG ledgers for every
  `64<=r<=16384`;
- the `19/9` Mode 1 ratio and all exceptional-boundary identities;
- every thousandth-unit and logarithmic base inequality used above;
- comparison with both exact mode ledgers at each checked arity; and
- byte-identical normal and optimized output.

Recorded hashes:

```text
checker SHA-256:
  8ae7196dc7225ed76695e330ecdb9848b15c7deb61ed9d8d9cc08f74fcb6a8f4
receipt/stdout SHA-256:
  0116a82f167cbee162b49ef452ee6b50659adcaa00f080d9e87dd97575dbb56c
semantic SHA-256:
  70d90f1d3b408565eb6602789320d6075ce3144393d75d4a3cf72c6697659140
```

The exact charged ratio in the replay range is maximal at `r=171`:

```text
9.148148148148148148...
```

This bounded maximum is validation evidence, not an all-arity optimality or
lower-bound claim.

## 8. Boundaries

This theorem does not change the local `4/3` program-vector constant, prove an
exact finite-width vector minimum, establish a global compiler lower constant,
settle the optimal additive depth term, give formula or bounded-fanout bounds,
or establish publication novelty. The new switch and integrated ledger are
not yet formalized in Lean.
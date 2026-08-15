# Recursive local library and a compiler constant below `19/2`

Date: 2026-08-15  
Status: **explicit construction, bounded complete-DAG reconstruction, exact finite replay, and analytic tail**

## 1. Result

The local universal library also contains avoidable duplication. Instead of building two full capacity-`M` signed routers separately for every local table, generate all table-plane pairs recursively. At each local coordinate, every new table is assembled from three already-existing child tables using two width-one signed routers, and one width-one order-pair vector is shared across the entire level.

Combined with the two-stage residual compiler, this gives, for every compatible selector and every `r>=64`, one parameter-free original-signature shared DAG with

```text
size  <(19/2)*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Thus the explicit constant is below `9.5`. The exact finite maximum of the audited ledger is

```text
9.444444444444720...
```

at arity 85. The construction-specific normalized limsup remains exactly `9`.

This is a fresh-room improvement of the reconstruction branch and is not asserted to be part of the byte-exact local packet `01ddf456…`.

## 2. Recursive local library

Put

```text
ell=ceil(log_3 r),
H=r-ell,
M=3^floor(log_3 H),
b=log_3 M.
```

The local block has `b` coordinates and `M=3^b` input rows.

### Base level

On zero local coordinates the three `Q`-valued constant tables have the legal Boolean-plane roots

```text
0 -> (zero,zero),
1 -> (zero,one),
2 -> (one,zero).
```

The dynamic names are supplied once by the global nonbinary anchor.

### Inductive level

Assume every `Q`-valued function on the final `j-1` local coordinates already has a pair of Boolean-plane roots. A function on `j` coordinates is uniquely a triple

```text
(F_0,F_1,F_2)
```

of child functions, selected by the first coordinate.

For every such triple:

1. build one positive width-one signed router for the high plane;
2. build one positive width-one signed router for the low plane; and
3. connect both to the same width-one order-pair controls for the current coordinate.

A width-one signed skeleton has four discriminator nodes. Thus each new table pair costs at most eight skeleton nodes, while the six-node width-one vector is shared across the entire level.

There are exactly

```text
3^(3^j)
```

`Q`-valued functions on `j` coordinates. Therefore the library count is

```text
L(b)=8*sum_(j=1)^b 3^(3^j)+6b.
```

### Size bound

For `b>=3`, put `M=3^b>=27`. The final summand is `8*3^M`. Every earlier function count is at most `3^(M/3)`, so

```text
8*sum_(j=1)^(b-1)3^(3^j)+6b
 <=8b*3^(M/3)+6b
 <3^M.
```

The final inequality holds at `M=27` and strengthens thereafter. Hence

```text
L(b)<9*3^M.
```

### Depth bound

Let `A` denote the anchor depth. The shared width-one vector for every level has depth at most `A+3`. Starting from the dynamic names at depth at most `A+2`, each local level adds two signed-router layers. Thus the final local plane roots have depth at most

```text
A+2b+3.
```

This is shallower than decoding and recomputing `Q` values at every level; the two planes remain separate until the single final decoder.

## 3. Two-stage residual selection

Retain the hierarchical residual construction from

```text
notes/QUASIPRIMAL_CONSERVATIVE_TERM_HIERARCHICAL_CONSTANT_49_5.md.
```

Let

```text
n=r-b,
a=floor(n/2),
c=ceil(n/2),
U=3^a,
V=3^c,
P=UV.
```

For each top address and each plane, one bottom capacity-`U` router selects a recursively generated local-table root. All bottom routers share one width-`a` vector. Two top capacity-`V` routers then share one width-`c` vector.

The exact residual count is

```text
R_2(n)=3P+2V-1+C_+(a)+C_+(c).
```

The complete ledger is now

```text
N(r)=L(b)+R_2(r-b)+4r+3+B(r),
```

where `B(r)` is the explicit complement-relative binary upper count.

## 4. Semantic reconstruction

The hash-consed reference implementation recursively materializes the complete local library. It checks:

```text
64 arity-three selectors with local width one,
2  arity-four selectors with local width two,
66 selector tables total,
1,890 complete input rows.
```

The arity-four cases explicitly construct all

```text
3^9=19,683
```

`Q`-valued functions on a two-coordinate local block before attaching the two residual routing stages.

## 5. Depth

Put

```text
D=ceil(log_2 r).
```

The anchor depth is at most `3D`, and the local plane roots have depth at most

```text
3D+2b+3.
```

The bottom stage has depth at most

```text
max(3D+2b+3, 3D+3+ceil(log_2 a))+a+1.
```

The top stage then adds `c+1` levels. Since `b+a+c=r` and `b<=D`, the top-stage plane roots have depth at most

```text
r+4D+5.
```

One decoder and the final glue add four levels, proving

```text
depth<=r+4D+9.
```

## 6. Finite range

Exact integer replay proves

```text
2*N(r)*r <19*3^r
```

for every `64<=r<1024`. The maximum occurs at `r=85`:

```text
N(85)*85/3^85
 =9.444444444444720...
 <19/2.
```

## 7. Analytic tail

Assume `r>=1024`. Put

```text
x=r/M,
g=r-M.
```

The parameter schedule gives

```text
50*ell<=M,
x<151/50.
```

The residual lower terms, fixed infrastructure, and binary branch each contribute less than `1/100` normalized unit.

The local library satisfies

```text
L(b)<9*3^M.
```

There are three cases.

### Transition case: `g=ell`

Here `H=M`, so `r=M+ell` and `x<=51/50`. Since

```text
M<r<3M,
```

one has `ell=b+1` and `3^ell=3M`. Therefore

```text
L(b)r/3^r
 <9r/3^ell
 =3x.
```

The leading residual skeleton contributes another `3x`, so the two main terms are below

```text
6(51/50)=153/25=6.12.
```

### Nontransition case with `x<=2`

Now `g>=ell+1`, and therefore

```text
3^g>=3^(ell+1)>=3r.
```

The local library contributes less than `3`, while the leading residual skeleton contributes at most `6`. The main terms are therefore at most `9`.

### Nontransition case with `x>2`

Now `g>M` and `M>=729`. Exponential domination gives

```text
L(b)r/3^r<1/100.
```

The leading residual skeleton is below

```text
3x<453/50=9.06.
```

### Tail sum

Including the three common lower-order hundredths:

```text
transition case  <6.15,
x<=2 case        <9.03,
x>2 case         <9.10.
```

Thus every `r>=1024` lies below `91/10`, and hence below `19/2`.

## 8. Architecture-specific limsup

The recursively shared local library is negligible at the arities immediately preceding each power-of-three block transition. The two-stage residual skeleton alone then contributes

```text
3r/M=9+o(1).
```

The tail analysis gives the matching upper bound. Consequently

```text
limsup_(r->infinity) N(r)r/3^r=9
```

for this declared compiler architecture.

This is not a lower bound for arbitrary circuits over `{d,u}`.

## 9. Consolidated theorem

**Theorem.** For every complement-invariant coordinate selector and every `r>=64`, the recursive-local/two-stage compiler constructs one parameter-free original-signature shared DAG with

```text
size  <(19/2)*3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

Combining with the selector representation theorem gives the same result for every conservative `r`-ary term operation of `Q`.

## 10. Evidence boundary

The companion audit records:

```text
66 bounded selector tables,
1,890 complete semantic rows,
960 exact finite arities,
122,888 analytic-tail assertions,
all three tail cases with nonzero witnesses.
```

Normal and optimized receipts are byte-identical.

The result remains independent of the local `01ddf456…` packet, its 65-source portfolio gate, and its Research Kernel object. Publication novelty and the globally optimal size constant remain unknown.

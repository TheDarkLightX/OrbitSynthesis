# Two-slice local coding and a smaller integrated size constant

**Status:** exact manuscript strengthening, 2026-08-14.  This note is stacked
on the fast-anchor theorem and the integrated compiler.  It changes the local
block decomposition but not the signed router, the sibling-shared program
vector, the binary complement-relative branch, the decoder, or the final
binary/nonbinary glue.  A standalone reconstruction checks the decomposition,
all integer ledgers through arity 16,384, effective mutations, and
normal/optimized equality.  The result is not yet formalized end to end in
Lean or externally peer reviewed.  Novelty and legal conclusions remain
**UNKNOWN**.

## 1. Result

For every `r>=64` and every `f in CT_r(Q)`, there is one parameter-free
original-signature free-fanout scalar DAG with

```text
size  < (21/2)*3^r/r,
depth <= r+ceil(7*ceil(log_2 r)/5)+12.
```

The local fixed-sign router control vector is unchanged: for `q=3^w` it still
has size `(4/3+o(1))q`, sharp leading scalar-output constant `4/3`, and depth
at most `3+ceil(log_2 w)`.  The present gain comes from smoothing the local
library size between consecutive powers of three.

## 2. Schedule

Retain

```text
L=4+ceil(log_3(r^2)),
H=r-L,
m=3^b, the largest power of three not exceeding H.
```

There are two modes.

```text
Mode 1: H<2m.   Use the ordinary m-point block Q^b.
Mode 2: 2m<=H.  Use a wide 2m-point slice and an m-point residual slice.
```

In Mode 2 choose one splitter coordinate `c`, `b` local coordinates `ell`,
and

```text
s=r-b-1
```

prefix coordinates.  The input domain is partitioned as

```text
c in {0,1}:  wide slice   {0,1} x Q^b,  size 2m,
c = 2:       residual     Q^b,          size m.
```

This uses the next admissible block size `2*3^b` without pretending that a
new radix-two coordinate exists globally.  The missing third value is handled
by a separate exact slice.

## 3. Wide and residual local libraries

On the nonbinary branch the fast anchor supplies legal names for `0,1,2`.
For each Q-valued table on the wide `2m`-point slice, encode its values on two
Boolean planes.  On each plane use one positive signed router of capacity

```text
3m=3^(b+1).
```

The `m` addresses whose splitter digit is `2` are padding and may be filled
arbitrarily, because the wide result is used only when `c` is `0` or `1`.
Thus one wide table uses two router skeletons and exactly

```text
9m-1
```

discriminator nodes.  There are `3^(2m)` wide tables.

For the residual slice, the ordinary two-plane capacity-m construction uses

```text
3m-1
```

router nodes per table, and there are `3^m` residual tables.

One width-`b+1` sibling-shared vector is shared by every wide table and both
planes.  One width-`b` vector is shared by every residual table and both
planes.  These are vectors of scalar control-output roots in the established
sense; they are not syntax encodings.

## 4. Prefix selection and one-shot slice glue

Let

```text
P=3^s.
```

For each prefix assignment `p`, the target operation determines:

- one wide table on `{0,1} x Q^b`; and
- one residual table on `Q^b`.

Select their high and low roots using four capacity-P positive routers:
wide-high, wide-low, residual-high, and residual-low.  All four share one
width-s program vector.  Their skeleton cost is

```text
6P-2.
```

After prefix selection, apply one equality selector per Boolean plane:

```text
EqSel(c,2; residual_plane,wide_plane).
```

This costs six nodes and two levels in total.  Decode the selected two-plane
value once, then apply the existing three-node final glue once.

Correctness is pointwise.  When `c` is `0` or `1`, the wide table indexed by
the current prefix is selected and its padded `c=2` rows are irrelevant.  When
`c=2`, the residual table is selected and the wide output is irrelevant.
Every tuple belongs to exactly one case.

## 5. Exact charged ledger

Let `S_P(w)` denote the exact fixed-positive sibling-vector count, including
its two generated anchor names.  In Mode 2 the nonbinary contribution is
bounded by

```text
(9m-1)3^(2m)                wide universal library
+(3m-1)3^m                  residual universal library
+(6P-2)                      four prefix routers
+S_P(b+1)+S_P(b)+S_P(s)-4   three vectors, names shared
+6                           slice selectors
+(2r-1)                      fast anchor
+2+3                         decoder and final glue.
```

The binary branch and one separately charged `u(x_0)` node are then united as
in the integrated theorem.  Mode 1 is exactly the fast-anchor compiler's
ordinary full-block ledger.

## 6. Size proof

Write

```text
U=3^r/r.
```

The reserve gives

```text
3^H <= 3^r/(81r^2).
```

### 6.1 Mode 1

The mode condition gives the stronger schedule ratio

```text
r/m <= 65/27.
```

For `b=3`, `r>=64` and `H<54` force `r<=65`.  For `b>=4`, first observe that
`L<=m`.  Otherwise `H<2m` would imply `r<3L`, while

```text
L<=5+2log_3 r<7+2log_3 L<L
```

for `L>=82`, a contradiction.  Hence `r<3m`, so

```text
L<=6+2b<=m/6+1.
```

The last inequality holds at `b=4` and is preserved when `b` increases because
the right side triples while the left side grows by two.  Since `H<=2m-1`,

```text
r=H+L<=13m/6<65m/27.
```

The prefix routers and vector satisfy

```text
(3P-1)+S_P(s)
 < (13/3)P+5*3^ceil(s/2).
```

Therefore their main term is at most

```text
(13/3)*(65/27)U = (845/81)U.
```

The local universal library is below `U/27`.  The half-width vector error,
the fixed linear group, the binary routers, and the binary controls are each
below `U/1000`.  Thus

```text
size/U < 845/81+1/27+4/1000
       = 848/81+4/1000
       < 21/2.
```

### 6.2 Mode 2

The unsmoothed schedule lemma `r/m<=31/9` remains valid, so

```text
r/(2m)<=31/18.
```

The four prefix routers and their vector satisfy

```text
(6P-2)+S_P(s)
 < (22/3)P+5*3^ceil(s/2).
```

Since `3^r=3mP`, their main term is at most

```text
(22/9)*(31/9)U = (682/81)U.
```

Because `2m<=H`, the wide library is below `U/18`.  The residual library is
below `U/1000`; it is enough that

```text
1500r^2<3^floor(r/2),
```

which holds at the two parity bases `64,65` and is preserved on adding two to
`r`.  The prefix half-width error, fixed linear group, and two binary groups
contribute four further thousandths.  Hence

```text
size/U < 682/81+1/18+5/1000 < 21/2.
```

Mode 1 is the larger of the two clean bounds.

## 7. Depth proof

Put

```text
C=ceil(log_2 r),
D_P(w)<=3+ceil(log_2 w).
```

Mode 1 retains the sharper bound

```text
r+ceil(7C/5)+11.
```

In Mode 2 the wide local roots have depth at most

```text
C+2+D_P(b+1)+b+2,
```

and the residual roots have depth at most

```text
C+2+D_P(b)+b+1.
```

The four prefix routers add `s+1` levels after the maximum of their leaf depth
and the width-s control-vector depth.  The final slice selector, decoder, and
glue add six levels.  Therefore

```text
D_2
 <= r+C+max(ceil(log_2(b+1))+13,
             ceil(log_2 s)-b+11).
```

The fast-anchor schedule already gives

```text
b>=C-ceil(2C/5)-1,
ceil(log_2 s)<=C.
```

Mode 2 also gives `2*3^b<2^C`, hence `3^b<2^(C-1)`.  Since
`log_3 2<2/3`,

```text
b+1<=ceil(2(C-1)/3)
    <=2^(ceil(2C/5)-1).
```

The second inequality is checked for `C=6,...,10`; increasing `C` by five
multiplies the right side by four while the left side grows by at most four.
Thus

```text
ceil(log_2(b+1))<=ceil(2C/5)-1.
```

Both branches of the maximum are now at most `ceil(2C/5)+12`, and

```text
D_2<=r+ceil(7C/5)+12.
```

The existing binary depth proof remains below this ceiling.  Combining both
modes proves the displayed global depth bound.

## 8. Deterministic reconstruction

The standalone checker

`research/tournaments/2026-08-14-two-slice-compiler/check_two_slice_compiler.py`

performs:

- 1,728 wide/residual reconstruction rows from 64 deterministic selector
  tables on `Q^3`;
- an effective slice-routing mutation;
- exact component and united-DAG integer ledgers for every
  `64<=r<=16384`;
- every schedule inequality used above;
- normal/optimized byte equality against a committed receipt; and
- boundary samples at every first schedule transition.

The replayed exact size ratio on that range is maximized at `r=65`:

```text
10.432098765711843541...
```

This bounded maximum is validation evidence, not an all-arity optimality
statement.  The all-arity theorem uses the inequalities in Sections 6 and 7.

This replay reconstructs slice-table lookup and evaluates charged ledger
formulas. It does not materialize and count the complete universal-library
compiler DAG. On 2026-09-21 the checker was tightened to use integer ceiling
arithmetic, compare expected receipt bytes exactly, and apply the wrong-slice
mutation to the same routing helper used by the positive tests. The original
receipt remains byte-identical. These repairs strengthen the executable check;
they do not extend its semantic or formalization coverage.

## 9. Boundaries

This theorem does not improve the sharp local `4/3` leading constant, prove an
exact finite-width vector minimum, give a global compiler lower constant,
settle the optimal additive depth term, or cover ordinary formulas or bounded
fan-out.  The wide padded router is used only under the explicit slice guard;
no semantics are claimed for its padded third block.  Publication novelty,
patent/FTO, and license conclusions remain unestablished.

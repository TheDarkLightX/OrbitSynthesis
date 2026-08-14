# Two-slice compiler audit

Date: 2026-08-14  
Verdict: **PASS for the wide/residual decomposition, the exact integer ledger,
and the clean `<21/2` size and sharpened depth bounds.**

## Theorem candidate

For every `r>=64`, the integrated fixed-Q compiler can use either the ordinary
power-of-three block or a two-slice block and obtain one parameter-free
original-signature scalar DAG with

```text
size  < (21/2)*3^r/r,
depth <= r+ceil(7*ceil(log_2 r)/5)+12.
```

The exact local program-vector theorem is unchanged.  Its fixed-sign
`(4/3+o(1))q` size, scalar-output lower bound, and
`3+ceil(log_2 w)` depth remain the interfaces used by this compiler.

## Construction

Let `m=3^b` be the largest power of three below the established reserve `H`.
If `H<2m`, retain the ordinary `m`-point block.  If `2m<=H`, designate one
splitter coordinate `c` and partition its values into

```text
{0,1} x Q^b   (2m live local rows),
{2}   x Q^b   (m residual rows).
```

A wide table is embedded into a capacity-`3m` positive router on each Boolean
plane; its third `m`-row block is padding and is ignored under the slice guard.
A residual table uses the ordinary capacity-m pair.  Four prefix routers
select wide-high, wide-low, residual-high, and residual-low.  They share one
prefix vector.  Two equality selectors choose the correct planes, followed by
one decoder and the existing final glue.

## Charged counts

In the two-slice mode the new nonbinary terms are

```text
(9m-1)3^(2m)                wide library,
+(3m-1)3^m                  residual library,
+(6P-2)                      four prefix routers,
+S_P(b+1)+S_P(b)+S_P(s)-4   three shared-name vectors,
+6                           slice selectors,
+(2r-1)+2+3                 anchor, decoder, glue.
```

The separately charged `u(x_0)` and retained binary branch are then united as
before.

The ordinary mode has `r/m<=65/27`.  Its main prefix term is at most
`845U/81`, where `U=3^r/r`.  Adding the local library and four thousandth-unit
error groups gives

```text
size/U < 848/81+4/1000 < 21/2.
```

In two-slice mode, `r/(2m)<=31/18`.  Its main prefix term is at most
`682U/81`; the wide library is below `U/18`, and the five remaining groups are
below `U/1000` each.  This mode is strictly smaller than the ordinary-mode
clean ceiling.

## Depth

The ordinary mode retains the fast-anchor bound with additive constant 11.
In two-slice mode the exact final path is

```text
r+C+max(ceil(log_2(b+1))+13,ceil(log_2 s)-b+11),
C=ceil(log_2 r).
```

The mode condition implies `3^b<2^(C-1)`, and the schedule gives

```text
ceil(log_2(b+1))<=ceil(2C/5)-1,
b>=C-ceil(2C/5)-1,
ceil(log_2 s)<=C.
```

Both branches are therefore at most `ceil(2C/5)+12`, proving the displayed
uniform depth bound.  The retained binary branch is lower by the previous
analytic proof.

## Deterministic evidence

The checker imports no compiler implementation.  It independently verifies:

- 1,728 exact wide/residual reconstruction rows from 64 selector tables on
  `Q^3`;
- an effective wrong-slice mutation;
- every component inequality and exact total for `64<=r<=16384`;
- all mode transitions and logarithmic base cases; and
- byte-identical normal and optimized output against the committed receipt.

```text
semantic SHA-256
  7104534eb032ae49934ab1fd613f70c950ca1720ea13cd6ee622849603a140b7
```

The exact replay ratio is maximal at `r=65`:

```text
10.432098765711843541...
```

That bounded maximum is not used as an all-arity optimality claim.

## Boundary

This lane does not claim an exact finite-width vector optimum, a global lower
constant, an optimal additive depth term, ordinary formula bounds,
bounded-fanout bounds, novelty, or legal clearance.  The padded wide router is
semantically guarded; its unused third block has no claimed value.  The new
compiler decomposition and global ledger are not yet formalized end to end in
Lean or externally refereed.
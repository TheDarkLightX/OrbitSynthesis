# Early-switch two-slice compiler audit

Date: 2026-08-14  
Verdict: **PASS for the new schedule, its all-arity inequalities, and the
standalone deterministic ledger.**

## Result

Retain the fixed-Q signed routers, sibling-shared program vectors,
pivot-normalized fast anchor, two-slice local decomposition, complement-relative
binary branch, decoder, and final glue.  Let

```text
L=4+ceil(log_3(r^2)),
H=r-L,
m=3^b, the largest power of three at most H.
```

Use the ordinary `m`-point compiler exactly when `H<=2m-5`, and use the
wide/residual two-slice compiler exactly when `H>=2m-4`.

For every `r>=64`, the resulting one-DAG construction satisfies

```text
size  < (46/5)*3^r/r,
depth <= r+ceil(7*ceil(log_2 r)/5)+12.
```

The previous clean size bound was `(21/2)3^r/r`.  The local program-vector
theorem and its matched `4/3` leading scalar-output constant are unchanged.

## Why the earlier switch is legal

The old condition `2m<=H` made the wide universal library a tiny lower-order
term.  That condition was sufficient but not cost-optimal.  Switching four
rows earlier can temporarily enlarge the wide library, but it also reduces the
prefix exponent by one.  The combined cost is smaller.

The integer boundary admits a clean proof.  In ordinary mode,

```text
r/m<=19/9.
```

Thus the prefix-router/vector main term is at most `(247/27)3^r/r`; adding the
ordinary local library and four thousandth-unit error groups gives

```text
size/(3^r/r) < 248/27+4/1000 < 46/5.
```

In two-slice mode put `t=H-(2m-4)` and `x=r/m`.

- For `t=0`, `ceil(log_3(r^2))=2b+2`, `x<=172/81`, and the wide library is
  below `x` Shannon units.
- For `t=1`, the same ceiling identity gives `x<=173/81`, and the wide library
  is below `x/3` units.
- For `t>=2`, the wide library is below `1/x` units, while `x<=31/9`.

Together with the prefix main term `(22/9)x`, every case is well below the
`46/5` ceiling after the residual and four remaining thousandth-unit groups
are charged.

## Deterministic evidence

The checker independently reconstructs the exact component formulas.  It does
not import an OrbitSynthesis compiler implementation.  It checks:

- 1,728 exact wide/residual semantic rows from 64 deterministic selectors;
- an effective wrong-slice mutation;
- every exact Mode 1, Mode 2, binary, and united-DAG ledger for
  `64<=r<=16384`;
- the `19/9` ratio and the exceptional `t=0,1` ceiling identities;
- all analytic base inequalities;
- the unchanged depth bound; and
- normal/optimized byte equality against the committed receipt.

The early switch also chose the smaller of the two exact charged mode ledgers
at every arity in the replay range.  This bounded observation is not needed as
an all-arity theorem.

```text
checker SHA-256
  8ae7196dc7225ed76695e330ecdb9848b15c7deb61ed9d8d9cc08f74fcb6a8f4
receipt/stdout SHA-256
  0116a82f167cbee162b49ef452ee6b50659adcaa00f080d9e87dd97575dbb56c
semantic SHA-256
  70d90f1d3b408565eb6602789320d6075ce3144393d75d4a3cf72c6697659140
```

The exact replay ratio is maximal at `r=171`:

```text
9.148148148148148148...
```

That is validation evidence, not a claimed exact all-arity optimum.

## Boundary

This lane does not improve the local `4/3` program-vector leading constant,
prove a global lower constant, establish an exact finite-width optimum,
settle the optimal additive depth term, address formulas or bounded fan-out,
or establish novelty or legal clearance.  The schedule and integrated ledger
are not yet formalized in Lean or externally refereed.
# Fast-anchor and sharp integrated-bound lane

Date: 2026-08-13  
Verdict: **PASS for the new anchor semantics, the sharpened all-arity
inequalities, and the deterministic integrated ledger.**

## Result

The integrated fixed-Q compiler can retain the exact sibling-shared program
vectors while replacing the historical depth-`3ceil(log_2 r)` anchor by a
pivot-normalized anchor of size at most `2r-1` and depth
`ceil(log_2 r)+2`.  Sharper accounting of the unchanged schedule then gives,
for every `r>=64`,

```text
size  < 15*3^r/r,
depth <= r+ceil(7*ceil(log_2 r)/5)+11.
```

The prior `<34*3^r/r`, `r+4ceil(log_2 r)+9` theorem remains valid.  This lane
strictly strengthens its explicit constants; it does not alter the local
`(4/3+o(1))q` vector theorem or its scope.

## Anchor

Choose `y=x_1`, `z=x_2`, and put

```text
e=u(y),
e2=u(e),
rho=d(y,e2,d(z,y,e)),
delta_i=d(x_i,y,e),
mu(a,b)=d(a,e,b).
```

Use the ordered leaves `x_1,x_2,delta_3,...,delta_(r-1),x_0` in a pruned
complete tree; the first pair is represented by `rho`, and every remaining
internal node is `mu`.

If `y=2`, then `rho=2` and it absorbs every right subtree.  If `y` is binary,
`e` is its complement, `rho=e` exactly when `z` is binary, and each
`delta_i=e` exactly when `x_i` is binary.  On `{e,2}`, `mu` has identity `e`
and absorber `2`; the rightmost `x_0` is therefore returned exactly on the
Boolean cube.  The construction uses at most `2r-1` operation nodes and has
depth at most `ceil(log_2 r)+2`.

The old anchor budget is preserved after separately charging `u(x_0)`:
`2r<=4(r-1)` for `r>=4`.

## Depth

With `C=ceil(log_2 r)`, the exact nonbinary final-path ledger becomes

```text
r+C+max(ceil(log_2 b)+11,ceil(log_2(r-b))-b+10).
```

The schedule gives `M>r/6`, `b<C`,

```text
b>=C-ceil(2C/5)-1,
ceil(log_2 b)<=ceil(2C/5).
```

The first inequality follows from
`6*3^(floor(3C/5)-2)<=2^(C-1)`, proved by five base cases and a five-step
`27<32` induction.  The second follows from
`C-1<=2^ceil(2C/5)`, with the same five-step structure.  Hence the nonbinary
path is at most `r+ceil(7C/5)+11`.

The exact binary ledger is checked for `64<=r<=99`.  From `r=100` onward the
existing analytic bound is dominated by the same ceiling; the difference has
positive base value and derivative.

## Size

Writing `U=3^r/r`, the schedule satisfies `r/M<=31/9`; equality is reached at
`r=93`, `M=27`.  The charged components satisfy

```text
local routers                                      < U/27,
prefix main term                                   <= 403U/27,
prefix half-width error                            < U/1000,
local vector + anchor + decoder + glue + u(x_0)   < U/1000,
binary routers                                     < U/1000,
binary controls                                    < U/1000.
```

Thus

```text
size/U < 404/27+4/1000 < 15.
```

The proof of `r/M<=31/9` uses the exact schedule intervals through `r=104` and
a monotone logarithmic inequality from `r=105` onward.  The two binary
thousandth-unit bounds use the existing monotone margins with an additional
factor `250` certified at `r=64`.

## Replay

The standalone checker imports no OrbitSynthesis implementation.  It checks
anchor semantics, a load-bearing mutation, all component inequalities, exact
united-DAG ledgers through arity 16,384, and normal/optimized equality.

```text
check_fast_anchor_sharp_bounds.py
  07a7fa06b222c178c32359bebee6f52a22b98f59026fb174f6afb7dcc11e2039
receipt.json / generated stdout
  8df0d86fcb603043f7452be348f4e1fc4b8f66c6bcc5c770a6ec8bee4110a55c
semantic
  cd98624ac0eebd3f9a9494c34ca0865e3c9c5fef8b0fe7834e41b5e4c114f76f
```

The replayed exact ratio is maximal at `r=93`, with value
`14.925925925925929447...`; this bounded maximum is not an all-arity
optimality statement.

## Boundary

The new anchor and integrated constants are not yet Lean-formalized.  Existing
Lean coverage for the signed router and sibling-shared vector is unchanged.
This lane proves no global lower constant, exact finite-width optimum,
bounded-fanout theorem, formula theorem, novelty result, or legal conclusion.
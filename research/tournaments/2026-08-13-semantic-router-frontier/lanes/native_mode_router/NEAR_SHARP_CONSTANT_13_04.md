# A near-sharp total compiler constant below `13.04`

This appendix sharpens the adaptive ledger without changing the compiler.

Use the adaptive parameters and node count from `ADAPTIVE_BLOCK_BOUND.md`. Exact replay for every `64<=r<=740`, now including the retained binary upper count

```text
6(N+Q)+6r*3^(2floor(sqrt r))+4r+10,
```

proves

```text
(total nodes) r/3^r <326/25.
```

The maximum is at `r=88` and is approximately `13.037037037037122`.

For `r>=741`, retain

```text
x=r/M,
a=109/27.
```

The native prefix contribution is below `a*x`.

If `r-M=ell-1`, the local contribution is below `9/x`; with `1<=x<=51/50`,

```text
9/x+a*x<=352/27.
```

If `r-M>=ell` and `x<=2`, then

```text
3/x+a*x<=517/54.
```

If `x>2`, then `r-M>M>=729`, so the local term is below `1/2000`, while

```text
a*x<a*(151/50).
```

The nonbinary remainder `R(b)+4r+7` contributes below `1/2000` normalized units for `r>=741`. The explicit retained binary upper count also contributes below `1/2000`; both inequalities follow at `r=741` and propagate by elementary exponential domination.

Therefore the worst tail case is bounded by

```text
352/27+1/1000
 <326/25.
```

Consequently, conditional on the same frozen compiler interfaces, for every `r>=64` the complete original-signature DAG satisfies

```text
size  <(326/25)3^r/r,
depth <=r+4*ceil(log_2 r)+9.
```

The decimal constant `13.04` is an appendix-level sharpening. The structural theorem remains the native first-mismatch mode vector and the simultaneous `O(3^r/r)` / `r+O(log r)` compiler.

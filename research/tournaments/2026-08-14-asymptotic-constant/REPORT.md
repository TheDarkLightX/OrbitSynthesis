# Asymptotic fixed-Q compiler constant

Date: 2026-08-14  
Verdict: **PASS for the semantic factorization, exact finite portfolio,
limit calculation, depth expansion, and deterministic replay.**

## Result

The canonical-rank compiler admits a second schedule with

```text
K=floor(log_2(3^r/r^4)),
C=ceil(log_2 r),
N=3^ceil(log_3(K*C^3)),
g=ceil(N/K).
```

Balanced groups have maximum size at most `K`. The same rank/group maps,
Boolean rank library, group-specific prefix routers, final group selector,
decoder, glue, and binary branch then give

```text
limsup_(r->infinity) r*size/3^r <= 3/log_2 3
                                   = 1.892789260714372110...
```

and

```text
depth
 <= r+(1+log_3 2)log_2 r+O(log log r).
```

The finite canonical-rank construction is retained in parallel. Choosing the
smaller exact charged count at each arity preserves

```text
size < (12/5)*3^r/r
```

for every `r>=64`.

## Inner calculation

The schedule satisfies

```text
K*C^3 <= N < 3*K*C^3,
g=N/K+O(1),
M/K -> 1.
```

With `P=3^(r-t)` and `U=3^r/r`, the prefix routers contribute

```text
3gP/U = 3gr/N = 3r/K+O(1/C^3).
```

The prefix vector is `O(1/C^3)` units. Since

```text
K/r -> log_2 3,
```

the prefix term tends to `3/log_2 3`.

The rank library has `2^M<=2^K<=3^r/r^4` roots and a router multiplier
`O(r)`, so it is `O(3^r/r^3)=o(3^r/r)`. Rank/group maps cost
`O(r(log r)^4)`, and every remaining component is lower order.

## Depth

The exact critical path is

```text
r+C+w+e+ceil(log_2 t)+ceil(log_2 w)+18.
```

Here

```text
w=log_3 r+O(1),
e=O(log log r),
t=log_3 r+3log_3 log r+O(1).
```

This yields the displayed additive-depth expansion and retains leading depth
coefficient one.

## Replay

The primary checker reconstructs both schedules for every
`64<=r<=16384`, verifies the all-arity finite portfolio bound, and checks the
limit identities. In that bounded range:

- the asymptotic schedule is first selected at `r=178`;
- its own normalized count is below `2` from `r=435` onward; and
- the combined finite maximum remains the canonical-rank value at `r=64`:

```text
2.391548842960882081...
```

Diagnostic asymptotic rows are also generated at `r=32768` and `r=65536`.
Normal and optimized runs are byte-identical.

```text
primary stdout SHA-256
  e24ada921f88b27aef52ed148dd864ba2ba11fb13d1ef98591e88b4af9559c55
primary semantic SHA-256
  03bf71c94192a83481baeb8dc16d634395025c8dce3c3b8718e16003878b66a7
```

## Boundary

This proves an upper constant only. It does not establish a matching global
lower constant, exact global optimum, optimal additive depth, formula or
bounded-fanout theorem, novelty result, or legal conclusion. The construction
is not yet formalized end to end in Lean or externally refereed.
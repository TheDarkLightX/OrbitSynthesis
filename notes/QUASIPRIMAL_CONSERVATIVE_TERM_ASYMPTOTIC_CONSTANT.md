# Asymptotic global size constant for the fixed-Q compiler

**Status:** exact manuscript strengthening, 2026-08-14. This note is stacked
on the canonical-rank Boolean-library compiler. It does not replace that
compiler's finite explicit `<12/5` bound; instead it supplies a second
schedule whose normalized size converges to an explicit smaller constant.
Taking the better of the two schedules preserves the finite bound and proves
the new asymptotic theorem.

Two independently written standalone reconstructions check the semantic
factorization, both exact schedules through arity 16,384, effective mutations,
normal/optimized equality, and the limit identities. The result is not yet
formalized end to end in Lean or externally peer reviewed. Novelty and legal
conclusions remain **UNKNOWN**.

## 1. Result

Let `L_r(Q)` be the worst-case original-signature operation-node complexity in
the free-fanout scalar-DAG model of the manuscript. Then

```text
limsup_(r->infinity) r*L_r(Q)/3^r <= 3/log_2(3).
```

Numerically,

```text
3/log_2(3) = 1.892789260714372110...
```

More concretely, every `f in CT_r(Q)` has a parameter-free
original-signature DAG with

```text
size = (3/log_2(3)+o(1))*3^r/r
```

under the upper-construction interpretation of the display. The statement is
an upper bound; no matching global lower constant is claimed.

The same schedule has

```text
depth
 <= r+(1+log_3(2))*log_2(r)+O(log log r),
```

where

```text
1+log_3(2)=1.630929753571457437...
```

The canonical-rank parent construction remains available at every finite
arity and gives

```text
size < (12/5)*3^r/r.
```

Taking the smaller exact charged construction at each arity therefore retains
that all-arity bound while inheriting the asymptotic constant above.

## 2. Schedule

Put

```text
C=ceil(log_2 r),
K=floor(log_2(3^r/r^4)).
```

Choose

```text
t=ceil(log_3(K*C^3)),
N=3^t,
g=ceil(N/K).
```

Partition the `N` local address rows into `g` consecutive balanced groups. If

```text
M=ceil(N/g),
```

then `M<=K`. Define

```text
w=ceil(log_3 M), R=3^w,
e=ceil(log_3 g), G=3^e,
s=r-t, P=3^s.
```

The canonical within-group rank and group-number maps are realized exactly as
in the parent theorem. The charged construction contains:

```text
(w+e)(3N+1)                       rank/group maps
+((3R-1)/2)2^M                    one Boolean rank library
+g(3P-1)                           group-specific prefix routers
+S_P(t)+S_P(w)+S_P(s)+S_P(e)-6    four vectors, shared names
+(3G-1)                            final group selector
+(2r-1)+2+3+1                     anchor, decoder, glue, u(x_0)
+B_router+B_control.               binary branch
```

No operation node is charged merely for pairing existing high and low scalar
roots.

## 3. Prefix term and limiting constant

By construction,

```text
K*C^3 <= N < 3*K*C^3.
```

Therefore

```text
g=N/K+O(1)=Theta(C^3).
```

The balanced maximum satisfies

```text
M/K -> 1.
```

Indeed, writing `alpha=N/K`, one has `alpha>=C^3` and

```text
N/g = K*alpha/ceil(alpha)=K*(1+O(1/C^3)).
```

The `2g` prefix routers have leading count `3gP`. Since

```text
P=3^r/N,
U=3^r/r,
```

their normalized contribution is

```text
3gP/U = 3gr/N = 3r/K+O(1/C^3).
```

The width-`s` vector contributes only

```text
(4/3)P/U = O(1/C^3)
```

at leading order, and its half-width error is exponentially smaller.

Finally,

```text
K/r -> log_2 3,
```

because

```text
K = r*log_2(3)-4log_2(r)+O(1).
```

Thus the prefix contribution tends to

```text
3/log_2 3.
```

## 4. All other terms are lower order

The maximum group size obeys `M<=K`, so

```text
2^M <= 2^K <= 3^r/r^4.
```

Also `R<3M=O(r)`. Hence the universal Boolean rank library has size

```text
O(r*3^r/r^4)=O(3^r/r^3)=o(U).
```

The rank/group maps satisfy

```text
N=Theta(r*C^3),
w=Theta(log r),
e=Theta(log C),
```

and therefore cost

```text
O(r*C^4)=o(U).
```

The local, rank, and group program vectors, final group selector, anchor,
decoder, and glue are polynomial in `r`. The complement-relative binary
branch is exponentially smaller than `U`, as established by the integrated
compiler. Consequently every nonprefix contribution is `o(U)`.

Combining Sections 3 and 4 proves

```text
size/U = 3r/K+o(1)
       -> 3/log_2 3.
```

## 5. Depth

The exact schedule-dependent critical path is

```text
r+C+w+e+ceil(log_2 t)+ceil(log_2 w)+18.
```

The parameters satisfy

```text
t=log_3 r+3log_3 log r+O(1),
w=log_3 r+O(1),
e=O(log log r).
```

Since

```text
log_3 r=log_3(2)*log_2 r,
```

the depth becomes

```text
r+(1+log_3 2)log_2 r+O(log log r).
```

The leading depth coefficient remains one. This theorem does not determine
the optimal additive term.

## 6. Exact replay and finite envelope

The primary and independent checkers reconstruct both the finite
canonical-rank schedule and the new asymptotic schedule for every

```text
64<=r<=16384.
```

At each arity they choose the smaller exact charged count. The united
portfolio continues to satisfy

```text
size < (12/5)*3^r/r.
```

In the checked range the asymptotic schedule is first selected at `r=178` and
its own normalized count is below `2` from `r=435` onward. These are bounded
observations, not the generic limit proof.

Selected exact ratios for the asymptotic schedule are recorded in the lane
receipt, together with larger diagnostic rows at `r=32768` and `r=65536`.
Normal and optimized executions are byte-identical.

## 7. Evidence

Primary lane:

`research/tournaments/2026-08-14-asymptotic-constant/`

Independent no-import audit:

`research/tournaments/2026-08-14-asymptotic-constant/audits/independent/`

The primary semantic SHA-256 is

```text
03bf71c94192a83481baeb8dc16d634395025c8dce3c3b8718e16003878b66a7
```

The independent semantic SHA-256 is

```text
73602d82183a5178b46b16ea662129da6158181729179d2c3419e48fdd3ff4f7
```

## 8. Boundaries

This theorem proves no matching global lower constant, exact global optimum,
optimal additive depth, formula or bounded-fanout theorem, publication
novelty, or legal clearance. The local sibling-shared program-vector theorem
and its scoped matched leading constant `4/3` are unchanged. The integrated
asymptotic construction is not yet formalized end to end in Lean.
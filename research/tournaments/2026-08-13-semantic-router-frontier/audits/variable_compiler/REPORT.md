# Independent audit: variable-depth compiler accounting

Date: 2026-08-13

## Verdict

**`CONDITIONAL PASS AFTER REQUIRED CHUNK-ORDER REPAIR`.**

Assume the exact router family stated by the author lane:

```text
q_h=3^(h-1) Boolean branches,
dependency depth h,
2q_h Boolean control leaves,
(3^h-1)/2 discriminator nodes.
```

That premise is not reproved here. Under it, a legal original-signature
compiler with

```text
size=O(3^r/r),
depth=r+O(sqrt(r))
```

survives independent accounting, provided every short residual chunk is
routed **first**, or the prefix is represented by an equivalent balanced
`q`-ary address tree. Residual-last sequential chunking does not establish the
claimed size bound and has an explicit large counterexample at `r=512`.

The audit charges both Boolean planes, growing router size, every program bit,
control compilation, local library, prefix instances, binary branch, anchor,
decoder, padding, and final gluing on one DAG. It found no fatal control-depth
dependence once program decoding is made explicit.

## 1. Repaired parameter choice

For `r>=64`, choose

```text
k=floor(sqrt(r)), h=k+1, q=3^k,
R=(3^h-1)/2.
```

Thus `R<3q/2`, and a router layer adds `h=k+1` dependency levels. Choose

```text
H=r-ceil(log_3(rq)),
M=3^b, where b=floor(log_3 H).
```

Then `M<=H`, so

```text
q*3^M <= 3^r/r.
```

Use `b` input coordinates for the local block, which has `M=3^b`
assignments, and route the remaining `s=r-b` ternary coordinates in chunks of
width at most `k`.

## 2. Residual-last flaw and exact repair

Let `s=ak+t`, with `0<t<k`. If full chunks are routed before the residual,
the prefix instance count contains

```text
1+q+...+q^(a-1)+q^a,
```

while every instance costs `Theta(q)` router nodes. The last residual does not
cancel this final `q` factor. At `r=512`:

```text
k=22, b=5, s=507=23*22+1.
```

Residual-last widths give prefix cost logarithm

```text
log_3(prefix nodes)=529.000...,
```

while the target `3^r/r` exponent is only

```text
r-log_3 r=506.321....
```

The normalized bound `size*r/3^r` exceeds `6.61*10^10` in the independent
model. This is coefficient-breaking accounting for the stated order, not a
mere constant loss.

Route the residual first. Then the instance count is

```text
1+3^t+3^t q+...+3^t q^(a-1),
```

so multiplication by `R=Theta(q)` telescopes to `O(3^s)`. At the same
`r=512`, the normalized total drops below `6.321`. A balanced address tree has
the same effect. The binary chunks require the same residual-first convention.

## 3. Local function library

Encode each `Q` output as two Boolean planes and decode only once. At a local
router node representing `t` block assignments, every one of the `3^t`
`Q`-valued functions receives two router outputs. With `R<3q/2`, the new-node
term is at most `3q*3^t` plus child libraries. A conservative geometric
recurrence is therefore `O(q*3^M)`.

The choice of `H` included the growing `q` factor:

```text
q*3^M*r <= 3^r.
```

Hence the entire encoded local library is `O(3^r/r)`. Padding short router
nodes with an existing child changes only constants; padded branches are never
selected.

## 4. Controls are not free

There are `2q` program bits per router level, shared globally at that level.
Two valid accounting routes are available.

First, a generic address-digit table over at most `k` ternary coordinates can
be compiled with `O(q)` selector nodes and depth `O(k)` per bit. Thus one level
costs `O(q^2)`, and all `O(r/k)` levels cost

```text
O((r/k)q^2)=exp(O(sqrt(r))),
```

which is negligible relative to `3^r/r`.

Second, the recursive program is much more structured. Express a target in
base three. For a fixed physical control leaf, the program recursion follows
the target's digit path until the first mismatch, at which point that subtree
receives a constant mode. Each program bit is consequently constant or a
prefix-conditioned decision list of at most `h-1=k` route digits. It can be
compiled with `O(k)` size and depth per bit. This confirms there is no hidden
free ROM or uncharged program decoder. The audit nevertheless uses the larger
generic `O(q^2)` size bound.

All controls at one router depth depend on the same current address chunk and
are shared by every router instance at that depth. Their depths run in
parallel with the routed branches. They do not add once per physical router.

## 5. Nonbinary depth

There are

```text
L_3 <= 1+ceil((r-b)/k)
```

routing levels including the local block. Router contribution is

```text
(k+1)L_3 = r+O(r/k+k)=r+O(sqrt(r)).
```

The balanced nonbinary anchor costs `O(log r)` depth. Generic control
compilation costs `O(k)` depth, the two planes run in parallel, decoding occurs
once, and final branch gluing is constant depth. Thus

```text
D_nonbinary=r+O(sqrt(r)).
```

Repeated per-level decoding would destroy this bound; it is not used.

## 6. Binary branch

On the Boolean cube, use relative names `x_0,u(x_0)` and the same Boolean
router. Choose binary chunk width

```text
w=floor(log_2 q)=Theta(k).
```

There are `O(r/w)=O(r/k)` levels. The binary routing depth is

```text
(k+1)O(r/k)=O(r),
```

with asymptotic leading coefficient `1/log_2 3<1`, so it does not dominate
the nonbinary branch. Generic relative-binary control tables cost
`exp(O(sqrt(r)))` total nodes. Binary router instances cost `O(q*2^r/q)=O(2^r)`
under residual-first telescoping, also negligible relative to `3^r/r`.

The relative controls preserve complement legality; absolute constants are not
assumed on the Boolean cube.

## 7. Exact arithmetic replay

The independent checker evaluates every integer arity `64<=r<=10000`. It uses
conservative node counts and verifies:

```text
size_upper <= 11*3^r/r,
depth_upper <= r+10*floor(sqrt(r))+50.
```

The largest checked normalized size is `10.444799` at `r=94`. The largest
checked `(depth-r)/sqrt(r)` is `9.580158` at `r=68`. These finite inequalities
are replay evidence; the asymptotic proof is the term-by-term analysis above.

Checker:

`research/tournaments/2026-08-13-semantic-router-frontier/audits/variable_compiler/check_variable_compiler.py`

Checker SHA-256:

`d88cd24a6f324dfe84d3972cd65fa8061770991ff060eb0d4587d66750d1eb4e`

Normal and optimized runs exit zero with identical semantic SHA-256

`d81d0bd6b979ec0df4270fd60f04468884de6e286aea450ba28eed9897e51870`.

## 8. Common falsifiers

| Falsifier | Verdict |
|---|---|
| `F-grammar` | Conditional: router family is a premise; all compiler-side nodes are charged original-signature selectors/routers/anchor/decoder. |
| `F-control` | PASS: `2q` controls per level are compiled and shared; generic `O(q^2)` and structured decision-list bounds are explicit. |
| `F-size` | PASS only after residual-first/balanced repair; residual-last is refuted by an exact arithmetic counterexample. |
| `F-depth` | PASS: router, controls, anchor, one decoder, binary branch, and gluing are included. |
| `F-degenerate` | PASS: short residuals and padding are explicitly handled; residual ordering is mutation-tested. |
| `F-transfer` | Conditional on the separately checked two-plane alphabet lift and router premise. |
| `F-boundary` | Not a proof of the router family, an optimal lower-order term, novelty, patent/FTO, practical performance, or Tau capability. |

## 9. Scope-accurate conclusion

The growing-router compiler implication is mathematically sound after a
specific required repair:

> Route every short residual chunk first, or use a balanced address tree.

With that correction, the exact router-family premise conditionally yields
same-DAG `O(3^r/r)` size and `r+O(sqrt(r))` depth. Program-control decoding is
not a fatal bottleneck. Without the chunk-order correction, the claimed size
bound is not established and fails on explicit arities.


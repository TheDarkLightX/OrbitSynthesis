# Direct-Q Pareto compiler report

Date: 2026-08-15  
Status: **post-referee explicit construction and deterministic audit**

## Result

A five-node native `Q` multiplexer is used on the logarithmically many local and inner-prefix coordinates. The remaining long address block is routed once by the exact sibling-shared signed Boolean construction.

For every complement-invariant selector and every `r>=64`, the resulting shared `{d,u}` DAG has

```text
size  <8*3^r/r,
depth <=r+6*ceil(log_2 r)+9.
```

The exact finite maximum is

```text
7.925011431184678...
```

at arity 84. The construction-specific normalized limsup is exactly `15/2`.

This creates a second size-depth Pareto point alongside the immutable referee theorem:

```text
size <(19/2)*3^r/r, depth <=r+4ceil(log_2 r)+9,
size <8*3^r/r,      depth <=r+6ceil(log_2 r)+9.
```

## Exact gadgets

The direct multiplexer is

```text
Mux_Q(x;b0,b1,b2)
 =d(d(0,x,b0),0,d(d(1,x,b1),1,d(x,2,b2))).
```

It uses five discriminator nodes and payload depth three.

The rail code is

```text
p(y)=d(0,y,1),
q(y)=d(y,2,0),
0->10, 1->01, 2->00,
Dec(p,q)=d(q,p,2).
```

Thus encoding costs two nodes per direct root and decoding one node after the long signed stage.

## Evidence

The executable audit checks:

```text
81      complete mux valuations,
66      compatible selector tables,
2,214   complete integrated input rows,
960     exact finite arities,
199,693 analytic-tail assertions.
```

The width-two local tests explicitly construct all `3^9=19,683` native local table roots.

Normal and optimized receipts are byte-identical.

```text
schema
  orbit-synthesis/direct-q-pareto-size-8/v1

semantic SHA-256
  9a121cea2251c4039dde487bddf3b7477d434f4134e2c63d1515639143182a41
```

## Boundaries

- The theorem is not part of the immutable external-referee commit `4c88add7…`.
- The `15/2` limsup is for this declared architecture, not a lower bound for arbitrary `{d,u}` DAGs.
- The five-node mux is proved correct and exhaustively checked; finite-size optimality is not claimed here.
- Publication novelty, freedom to operate, and global size-depth optimality remain unknown.

## Reproduction

```bash
bash research/tournaments/2026-08-15-direct-q-pareto/check.sh
```

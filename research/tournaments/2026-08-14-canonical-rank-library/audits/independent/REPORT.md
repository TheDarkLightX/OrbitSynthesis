# Independent canonical-rank compiler audit

Date: 2026-08-14  
Verdict: **PASS.**

This audit independently reconstructs the signed-vector count recurrences,
canonical rank/group schedule, Boolean rank library, prefix and final group
routers, binary branch ledger, and critical path. It imports neither the
primary checker nor an OrbitSynthesis compiler implementation.

For every `64<=r<=16384`, it verifies

```text
5*size*r < 12*3^r
```

and

```text
depth
 <= r+C+ceil(2(C+1)/3)+2ceil(log_2(C+4))+23.
```

It independently exhausts all 512 coordinate-selector tables on `Q^2`, checks
4,608 selector rows through canonical group/rank references, and applies an
effective shifted-rank mutation. It separately reconstructs the `h=81..242`
prefix table and finds the same maximum `361982/177147` at `h=240`, `g=83`.

The checked maximum is again at `r=64`:

```text
2.391548842960882081...
```

Normal and optimized executions are byte-identical.

```text
checker SHA-256
  5acb536724c6d66115891c62ef4bd97e7e0f88576062b61749161c5cd7464dbc
stdout SHA-256
  a19121dd1a3efc5f069a290891ab6c0e3242a0773e4cbc02a90a835ad441963d
semantic SHA-256
  7fdf7f1854771fea568d2e72a02835ec91f6d7a011fd14312e7a4a2402572f66
```

This is internal executable evidence for the generic manuscript proof. It is
not a Lean proof, external peer review, novelty result, or exact global
optimality theorem.
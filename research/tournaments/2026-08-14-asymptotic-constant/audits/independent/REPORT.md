# Independent asymptotic-constant audit

Date: 2026-08-14  
Verdict: **PASS.**

This audit independently reimplements the signed-vector recurrences, binary
branch ledger, finite canonical-rank schedule, asymptotic schedule, canonical
rank/group factorization, and depth ledger. It imports neither the primary
checker nor an OrbitSynthesis compiler implementation.

For every `64<=r<=16384`, it verifies that choosing the smaller of the finite
and asymptotic charged constructions preserves

```text
5*size*r < 12*3^r.
```

It independently obtains

```text
limsup r*size/3^r <= 3/log_2 3
```

from

```text
K/r -> log_2 3,
K*C^3<=N<3*K*C^3,
g=N/K+O(1),
M/K->1,
3gP/U=3r/K+O(1/C^3).
```

The audit exhausts all 512 coordinate-selector tables on `Q^2`, checks 4,608
selector rows through canonical group/rank references, and applies an
effective shifted-rank mutation.

The checked finite portfolio maximum is again at `r=64`:

```text
2.391548842960882081...
```

The asymptotic schedule is first selected at `r=178`, and its normalized count
is below `2` from `r=435` onward in the checked interval. Diagnostic rows are
also reconstructed at `r=32768` and `r=65536`.

Normal and optimized executions are byte-identical.

```text
independent stdout SHA-256
  dd7af892fb230e20928eaf55fc4a4c1148ac1a2936cc9853b03903464bade0b7
independent semantic SHA-256
  73602d82183a5178b46b16ea662129da6158181729179d2c3419e48fdd3ff4f7
```

This is internal executable evidence for the generic manuscript proof. It is
not a Lean proof, external peer review, novelty result, or exact global
optimality theorem.
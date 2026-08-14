# Independent plane-shared portfolio audit

Date: 2026-08-14  
Verdict: **PASS.**

This lane independently reimplements the Boolean plane factorization, signed
program-vector recurrences, local group ledgers, four-candidate portfolio,
complement-relative binary branch, exact finite proof, analytic tail, and
depth accounting. It imports neither the primary checker nor an
OrbitSynthesis compiler implementation.

For every checked integer `64<=r<=16384`, it confirms

```text
25*size*r < 67*3^r,
depth <= r+ceil(7*ceil(log_2 r)/5)+20.
```

It separately checks the exact finite range `64..966` and reconstructs every
component of the analytic `r>=967` proof. Its exact maximum is again the
`r=64` value

```text
2.679666803224281973...
```

The independent plane closure contains exactly `2^M` Boolean roots at each
checked width and reconstructs every Q table from its high/low pair.

```text
checker SHA-256
  9c0900bfb2d7a72e4be5c0b3b8bc0509da9e1b3b54c6b2abb7766d68cc3a6b04
stdout SHA-256
  bdade906dc2e92049019157d611e5f4d27deb5590316ecb0a8578160a23f0f9b
semantic SHA-256
  b96a891f6e94a5d5d4aefa1b1efd20ebe31583347244746c225329b3fca7ab95
```

This is independent deterministic evidence for the manuscript proof. It is
not a Lean formalization, external peer review, novelty result, exact global
optimality theorem, or legal finding.
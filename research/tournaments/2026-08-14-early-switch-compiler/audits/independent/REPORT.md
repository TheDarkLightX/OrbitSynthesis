# Independent early-switch arithmetic audit

Date: 2026-08-14  
Verdict: **PASS.**

This audit independently reimplements the sibling-vector recurrences, binary
branch ledger, ordinary and two-slice totals, early-switch schedule, and depth
ledger. It imports neither the primary early-switch checker nor an
OrbitSynthesis compiler implementation.

For every `64<=r<=16384`, it confirms

```text
5*size*r < 46*3^r,
depth <= r+ceil(7*ceil(log_2 r)/5)+12.
```

It separately materializes both candidate mode ledgers at every arity and
finds that the rule

```text
use Mode 2 iff H>=2m-4
```

selects the smaller charged ledger throughout the replay range. The checked
maximum occurs at `r=171` with ratio

```text
9.148148148148148148...
```

The script also checks the exceptional-boundary ceiling identities and the
five base inequalities used to control lower-order terms.

```text
audit_early_switch_arithmetic.py SHA-256
  3db0467715990f1269934da416de9dca02af61e6470b9d0ff55110c57db59a15
receipt/stdout SHA-256
  36776e149d298e3b6a7e6d0864a2480e1b7be374c5b3a2fce3ff6921f0b5ccd9
semantic SHA-256
  cfda24e43cdecd950d61cf1cf0dbbac6818f82722b4edae37aa01022ebe923a0
```

The audit is bounded executable evidence for the generic proof recorded in
the source note. It is not a Lean proof, external peer review, novelty result,
or exact all-arity optimality theorem.
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
  8075699a955380152ce146ab56a5147445f34f5ff3fc05b4f88d111c704bcbb9
receipt/stdout SHA-256
  7e9b407e4e85b9db7b7a05f5028966366f59ee342ec228a65e4c566ea729ee8e
semantic SHA-256
  cfda24e43cdecd950d61cf1cf0dbbac6818f82722b4edae37aa01022ebe923a0
```

The receipt binds the exact audit-source hash, both replay commands, and the
required equality of normal output, optimized output, and committed receipt.

The audit is bounded executable evidence for the generic proof recorded in
the source note. It is not a Lean proof, external peer review, novelty result,
or exact all-arity optimality theorem.

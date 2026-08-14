# Independent external-optimization audit

Date: 2026-08-14  
Verdict: **PASS on the committed 20-instance no-import corpus.**

This audit imports no OrbitSynthesis module. It independently implements:

- candidate-rule feasibility over state domains;
- exact signed state utility;
- the component-selector CNF/WCNF construction;
- exhaustive optimization over state domains;
- exhaustive optimization over all WCNF variables; and
- parsing of the external reference process's `o`, `s`, and `v` output.

Four rule families are tested under five scenarios:

```text
unique powers-of-two utilities
mixed positive and negative utilities
required states
forbidden states
all-zero utility with ties
```

For every instance, the audit verifies:

1. domain feasibility agrees with WCNF hard-clause feasibility;
2. the signed-utility optimum gives the same WCNF cost after the fixed negative
   offset is included;
3. the independent subprocess reports `OPTIMUM FOUND` with that exact cost; and
4. the process returns one complete signed-literal assignment.

The corpus contains

```text
4 families x 5 scenarios = 20 instances.
```

Recorded hashes:

```text
rows
  c2634bf96dd934f4210d6d9b418d1fec25900c1818dcac582f62297593384672
semantic
  3295548451c93286c56971ee27d304ff3a3b50601809f16e542486d39162bd87
```

The audit is bounded semantic evidence. It is not a performance result, a proof
of the algebraic quasi-primal premise, a proof-producing MaxSAT certificate,
or a large-instance optimality theorem.

# Independent role-orbit rank audit

Date: 2026-08-15  
Verdict: **PASS in the independently reconstructed three-element scope.**

The script imports no OrbitSynthesis module. It independently reconstructs:

- finite subalgebras and internal isomorphisms;
- graph-maximal nonextendable partial symmetries;
- generating tuples modulo diagonal subalgebra automorphisms;
- the exact three-role orbit rank;
- the critical/dead-orbit converse witness;
- exact fixed-domain quasi-primal feasibility;
- orbitwise generated-value one-equation separators; and
- eager component-rule/CNF censuses.

It exhausts all 27 unary expansions of the three-element discriminator and
recovers

```text
15 demi-semi-primal
12 non-demi-semi-primal.
```

Every non-demi expansion has exact three-role rank three. For each one the
audit verifies:

- fewer than three generating-tuple orbits at every smaller arity;
- three pairwise orbit-separated source roles that individually generate the
  obstructing subalgebra;
- feasible left and right domains;
- infeasible union;
- exact one-equation separation on every flattened row;
- generated-subalgebra preservation and groupoid equivariance of the
  separator; and
- exact eager-domain model counts.

The aggregate model census drops from 101,436 generator-tag candidate rules to
19,392 role-orbit candidate rules.

Hashes from the locally executed normal/optimized replay:

```text
script
bbadcf6a15c81e5d8f75889520dda33a24057855a8d2ecc9c872eaa7c51c9f44

output
21197585ddd61f960f943309badfcf7146a1bd5eb32e4d8a899eff4ee422b4f9

semantic
a33f884a4da2882f850a1b131c438133bcde355ecac5aa0bd2892fe0090b746f
```

This is deterministic finite evidence. It is not a Lean proof, external
referee report, or publication-novelty determination.

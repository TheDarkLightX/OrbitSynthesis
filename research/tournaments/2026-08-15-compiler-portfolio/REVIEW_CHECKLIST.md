# Compiler portfolio review checklist

Review target:

```text
base  research/original-signature-dag-bundles
head  research/compiler-portfolio
```

## Portfolio policy

- [ ] exact semantic closure is limited to explicitly small tables;
- [ ] tiers execute as an ordered fallback rather than all running eagerly;
- [ ] the fixed-Q backend checks the exact carrier and complete `d/u` tables;
- [ ] structural search has both a row limit and scalar-work budget;
- [ ] MDD and original-signature artifacts remain different implementation kinds;
- [ ] the Shannon attempt is diagnostic-only and cannot receive a score;
- [ ] deterministic tier selection is recomputed during bundle verification;
- [ ] unsupported is rejected when the policy has an eligible compiled attempt;
- [ ] disabled or policy-excluded backends cannot become selected.

## Fixed-Q structural recognizer

- [ ] projections and `u(projection)` are correct;
- [ ] one-layer `d` terms are evaluated with the exact discriminator semantics;
- [ ] the nested router inserts the inner term in the intended argument;
- [ ] candidate limits fail as unsupported, not nondefinability;
- [ ] controllers above the structural row threshold bypass recognition;
- [ ] output coordinates share emitted operation nodes;
- [ ] successful DAGs pass the existing exhaustive table certificate.

## MDD construction

- [ ] the table is complete before compilation;
- [ ] vector outputs are terminals rather than independent scalar diagrams;
- [ ] variable orders are deterministic and deduplicated;
- [ ] children are constructed before parents;
- [ ] all-equal children collapse to one child;
- [ ] identical `(variable,children)` nodes are hash-consed;
- [ ] variable ranks increase strictly along node edges;
- [ ] every serialized node and terminal is reachable;
- [ ] the selected order is one of the recorded candidate orders;
- [ ] graph validation happens once before linear row replay;
- [ ] every input row is replayed against the semantic table.

## Portable artifacts

- [ ] attempt backend IDs agree with fixed tiers and implementation kinds;
- [ ] attempt metrics contain no untrusted executable payload;
- [ ] selected original-signature implementations bind DAG and certificate;
- [ ] selected MDD implementations bind diagram and certificate;
- [ ] noncompiled artifacts contain no hidden implementation;
- [ ] inner proof-bundle verification runs before compiler verification;
- [ ] portfolio and outer manifest hashes are recomputed.

## Evidence

- [ ] tiny discriminator chooses exact closure;
- [ ] exact-disabled discriminator chooses one structural `d` node;
- [ ] MDD-only discriminator verifies;
- [ ] nested router compiles to three shared nodes;
- [ ] the repeated-subcube case compresses below raw table rows;
- [ ] a 6,561-row projection skips structural recognition and selects one-node MDD;
- [ ] infeasible synthesis contains no implementation;
- [ ] lower-priority, false-unsupported, duplicate, and research-tier selections fail;
- [ ] the independent no-import audit checks reachability and all emitted rows;
- [ ] normal and optimized runs are byte-identical;
- [ ] GitHub runner status is reported separately from source evidence.

## Nonclaims

- [ ] no optimal MDD ordering claim;
- [ ] no complete structural-recognition claim;
- [ ] no implication that an MDD is an original-signature term;
- [ ] no practical claim for the unmaterialized Shannon backend;
- [ ] no production performance, hardware, gas, or timing claim;
- [ ] no novelty, FTO, or external-review claim.

# Original-signature DAG bundle review checklist

Review refs:

```text
base: research/portable-proof-bundles
head: research/original-signature-dag-bundles
```

## Original-signature boundary

- [ ] every node operation appears in the embedded finite-algebra signature;
- [ ] operation arity is checked against the embedded operation table;
- [ ] no named carrier constants, selectors, or lookup nodes are introduced;
- [ ] nullary nodes are accepted only when they are declared basic operations;
- [ ] input and node references are range checked;
- [ ] node references are strictly topological;
- [ ] every serialized operation node is reachable from an output root.

## Semantic equivalence

- [ ] the controller table is total over the complete carrier input power;
- [ ] every controller output has the declared output arity and stays in the carrier;
- [ ] the DAG is evaluated on every finite input row;
- [ ] every DAG result equals the serialized controller result;
- [ ] algebra, strategy, DAG, and evaluation hashes are recomputed;
- [ ] recorded node count and dependency depth equal the executable DAG.

## Proof-bundle integration

- [ ] the inner semantic proof bundle verifies first;
- [ ] the controller table is reconstructed from selected groupoid rules;
- [ ] the table/DAG certificate is bound to that reconstructed table;
- [ ] the outer manifest binds the complete inner proof and DAG artifact;
- [ ] infeasible results contain no executable DAG or equivalence certificate;
- [ ] compiled/unsupported/not-applicable status envelopes fail closed;
- [ ] `required` compilation policy fails at generation when no DAG is found.

## Bounded compiler

- [ ] semantic closure begins only from input projections;
- [ ] depth accounting is exact for operation composition;
- [ ] the first retained representative of a semantic function is deterministic;
- [ ] multi-output roots share common intermediate nodes;
- [ ] unreachable exploration nodes are removed from the emitted DAG;
- [ ] resource exhaustion yields `unsupported`, not a false impossibility claim;
- [ ] compiler statistics are described as provenance rather than proof authority.

## Calibration and mutations

- [ ] `d(x,y,z)` compiles to one `d` node at depth one;
- [ ] `(d,u(d))` compiles to two shared nodes;
- [ ] a projection emits zero operation nodes;
- [ ] a bounded constant-table miss is reported as unsupported;
- [ ] wrong semantics are rejected;
- [ ] forward references and unreachable nodes are rejected;
- [ ] altered strategy/DAG/evaluation hashes are rejected;
- [ ] hidden executable data on infeasible/unsupported artifacts is rejected;
- [ ] native and HiGHS semantic controllers yield the same executable artifact.

## Claim boundary

- [ ] no minimum-size or minimum-depth claim is made;
- [ ] no nondefinability conclusion is drawn from bounded exhaustion;
- [ ] no polynomial compilation or certificate-size claim is made;
- [ ] no machine-code, hardware timing, gas, or deployment-safety claim is made;
- [ ] GitHub runner status is reported separately from source implementation and
      independent reconstruction.

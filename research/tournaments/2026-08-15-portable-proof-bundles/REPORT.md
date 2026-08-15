# Portable proof-bundle milestone

Date: 2026-08-15  
Status: **portable format, synthesis CLI, proof verifier, semantic gate, and
no-import example audit committed.** The integrated runner has not yet executed.

## Result

OrbitSynthesis can now consume an explicit user JSON problem and emit one
portable artifact containing:

```text
canonical finite algebra and safety problem
compiled internal-groupoid model fingerprint
optimal domain or infeasibility verdict
complete controller table
selected component-rule indices
backend provenance
exact state-search optimum/infeasibility certificate
bundle manifest
```

A separate command rebuilds and verifies the artifact without rerunning the
optimizer.

## New modules

```text
src/orbitsynthesis/problem_io.py
src/orbitsynthesis/proof_bundle.py
tools/orbit_synthesize.py
```

Schemas:

```text
schemas/finite_safety_problem_v1.schema.json
schemas/proof_bundle_v1.schema.json
```

Examples:

```text
examples/proof_bundle/discriminator_policy.json
examples/proof_bundle/coupled_required_infeasible.json
```

## Canonical problem semantics

The v1 input supports:

- finite carriers of JSON integers or strings;
- complete operation tables;
- positive state arity and arbitrary finite input arity;
- allowed- or forbidden-transition encodings;
- signed integer state utility;
- required and forbidden states;
- explicitly acknowledged quasi-primal internal-groupoid semantics.

Canonical output sorts operation names, state weights, hard state sets, and the
semantic safe-transition allowlist. The problem SHA-256 is therefore tied to
the finite mathematical object rather than incidental input ordering or
allowlist/denylist presentation.

## Synthesis backends

### Native

The dependency-free path uses the exact pointed-kernel weighted branch-and-
bound solver. The returned domain is replayed through the independently
compiled component model before entering a bundle.

### HiGHS

The external path emits the exact CNF/WCNF model, runs SciPy/HiGHS, decodes the
Boolean assignment, and reconstructs a complete controller. The backend result
remains provenance; a separate state-search certificate supplies final
optimality authority.

### Auto

The current policy selects native search through 18 states and HiGHS above
that threshold. This is an engineering default, not a complexity theorem.

## Verification theorem

For an optimal bundle, verification checks:

1. the canonical problem hash;
2. the complete component-model hash;
3. all component candidate indices;
4. domain acceptance of every selected candidate;
5. exact reconstruction of the total strategy table;
6. signed domain utility;
7. the target domain and target score in the state-search certificate;
8. every conflict, objective bound, and branch in the proof tree;
9. the bundle manifest.

For an infeasible bundle, the strategy and domain fields must be empty, and the
state-search certificate must contain only branches and valid component
conflicts.

Therefore verification does not trust the native search trace, HiGHS status,
or a serialized controller table in isolation.

## Exact examples

### Optimal discriminator controller

The first input has three states, two inputs, and the unique safe policy

```text
x'=d(x,i_0,i_1).
```

The expected bundle contains:

```text
status: optimal
domain: {0,1,2}
score: 3
strategy rows: 27
certificate: one root bound
```

The native and HiGHS paths are required to agree on domain and score.

### Internal-symmetry infeasibility

The second input requires states `0` and `1` while safety asks both states to
map to `0`. The internal complement of `{0,1}` forces unary term tables to
satisfy `f(1)=1-f(0)`. No original-signature shared term controller exists.

The expected bundle contains:

```text
status: infeasible
no domain
no strategy
certificate: one component-conflict leaf
```

## Gate

The primary gate is designed to check:

- problem canonical round-trip;
- native optimal and infeasible synthesis;
- HiGHS agreement;
- bundle JSON round-trip;
- complete controller semantics;
- immediate proof replay;
- manifest, problem, model, strategy, component-choice, and score mutations;
- normal and optimized Python byte equality;
- CLI canonicalize/synthesize/verify cycle.

The independent audit imports no OrbitSynthesis modules. It:

- reconstructs the exact `d` and `u` operation tables;
- checks all 27 discriminator policy rows;
- checks the one-node optimum proof arithmetic;
- enumerates all six unary Q-term tables;
- checks both possible domains containing the required states for each table;
- establishes infeasibility independently;
- recomputes problem, certificate, and manifest hashes.

## Practical significance

This is the first branch that makes OrbitSynthesis results portable between
processes and potentially between implementations.

The artifact can support:

- offline controller verification;
- optimizer regression testing;
- archival research receipts;
- third-party solver comparison;
- policy/controller review workflows;
- future Tau or temporal frontends that emit the same finite problem schema;
- future original-signature compiler artifacts added to the bundle.

## Claim boundary

The source format is explicit and finite. Quasi-primality is an acknowledged
premise, not inferred. Proof trees may be exponential. No claim is made that
arbitrary policy languages, temporal objectives, or infinite structures are
already supported end to end. Original-signature DAG emission is not yet part
of the portable artifact.

The complete GitHub gate should not be marked passed until a runner actually
executes it. Previous jobs have been rejected before runner allocation by the
account payment/spending-limit condition.

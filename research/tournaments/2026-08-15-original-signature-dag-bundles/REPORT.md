# Executable original-signature controller bundles

Date: 2026-08-15  
Status: **implementation, proof format, source-grounded gates, and independent
no-import reconstruction committed. Integrated GitHub execution is pending
runner availability.**

## Result

OrbitSynthesis now emits a portable executable artifact containing:

```text
certified finite safety problem
optimal clone-compatible winning domain or infeasibility
complete controller table
optimum/infeasibility proof
original-signature shared controller DAG
complete table-to-DAG equivalence receipt
one outer manifest binding every layer.
```

The DAG compiler is generic over an explicit finite algebra. It begins with the
input projections and explores the bounded semantic closure of the declared
basic operations. A successful node may use only:

```text
an input reference, or
a prior node labelled by one declared basic operation.
```

No named carrier constants, selectors, truth-table nodes, or foreign operations
are introduced. Nullary basic operations remain legal because they belong to
the original signature.

## Portable formats

```text
orbit-synthesis/controller-dag-artifact/v1
schemas/controller_dag_artifact_v1.schema.json

orbit-synthesis/executable-proof-bundle/v1
schemas/executable_proof_bundle_v1.schema.json
```

The executable bundle wraps the existing stable semantic proof bundle. This
keeps semantic controller certification separate from implementation
certification while binding both with an outer SHA-256 manifest.

## Artifact states

### Compiled

Contains one original-signature DAG and one exhaustive equivalence certificate.

### Unsupported

A semantic controller exists, but bounded search did not find a term under the
recorded limits. This is not a nondefinability result.

### Not applicable

The problem is infeasible or DAG compilation was explicitly disabled. The
artifact contains no executable nodes or equivalence certificate.

## Soundness

For a verified compiled bundle:

1. the inner proof bundle verifies the problem, domain, controller, objective,
   and optimum/infeasibility proof;
2. the DAG signature equals the embedded algebra signature exactly;
3. every node uses a declared basic operation with the correct arity;
4. every node reference is topologically prior;
5. every serialized operation node is reachable from a distinguished output;
6. each DAG output is evaluated on every input in the finite carrier power;
7. each evaluation equals the serialized complete controller table;
8. the table and DAG hashes agree with the equivalence certificate;
9. the outer manifest binds the inner proof bundle and executable artifact.

Therefore the DAG implements exactly the controller whose safety and
optimality were certified.

## Fixed-Q calibration

For the source example

```text
x' = d(x,i_0,i_1)
```

over Quackenbush `Q`, the bounded compiler returns:

```text
nodes: 1
depth: 1
node 0: d(input 0,input 1,input 2)
rows checked: 27
```

The deterministic direct-reference hashes are:

```text
algebra
  9a7dfd548e00a03abe5fb84b2167295c1ab06448e042d8f51424d4a3127b0044
strategy table
  de61c47305aad7394e517c9884e943c82bf1f36307a1ff24e92b3068494c86c8
DAG
  e206643659457d8f03b44cb2fab2605cb320f8883760d620b7ef4c50034c54ba
evaluation transcript
  3f89e4a34c60b77080a11ad613b6e4af7a200d7bc4e217a6477566fea72e2441
equivalence certificate
  062a5d2a9725897d1a900f27fea20855631ceffc609736b5b0e1b3fa37db9c30
compiled artifact with max-depth one
  a641a3401bf84db9fb55c332c5b3e6050529665d288ca86f1eae6f4bbc1456ef
```

The bounded semantic search reaches the result after:

```text
7 distinct semantic functions
9 operation combinations
4 exploration nodes
1 dependency layer.
```

A two-output calibration

```text
(d(x,y,z),u(d(x,y,z)))
```

returns two reachable nodes and shares the discriminator root. A projection
returns a zero-operation DAG. A constant scalar table over the parameter-free
conservative algebra is explicitly reported as bounded-search unsupported.

## Primary gate

The source-grounded gate checks:

- native optimal synthesis through executable DAG emission;
- infeasibility with no spurious executable data;
- HiGHS/native controller and DAG agreement;
- exact one-node discriminator form;
- exact multi-output sharing;
- zero-node projection roots;
- bounded unsupported receipts;
- deterministic JSON round-trip;
- normal versus optimized Python byte identity;
- CLI synthesis and verification;
- schema syntax;
- table/DAG equivalence on every finite input.

Effective mutations reject:

```text
wrong DAG semantics
forward/self references
unreachable hidden nodes
wrong strategy hash in the certificate
wrong outer manifest
wire-level DAG mutation
infeasible result carrying a hidden DAG
infeasible result carrying a hidden certificate
unsupported status retaining executable data
optimal result downgraded to not-applicable
untrusted compiler identifier.
```

## Independent reconstruction

The no-import audit reads only the emitted executable JSON artifacts. It
independently:

- parses the embedded operation tables;
- reconstructs the declared signature;
- rejects unknown operations and forward references;
- checks that every operation node is output-reachable;
- evaluates all 27 input rows;
- recomputes algebra, strategy, DAG, evaluation, certificate, artifact, proof,
  and outer-manifest hashes;
- checks the infeasible artifact contains no executable data;
- compares the result with the frozen direct one-node discriminator reference.

The independent semantic receipt is generated by the gate and intentionally
is not predeclared as a substitute for executing the emitted artifacts.

## CLI

```bash
python3 tools/orbit_synthesize.py synthesize-executable \
  --input examples/proof_bundle/discriminator_policy.json \
  --out executable.json \
  --backend native \
  --dag-policy required \
  --dag-max-depth 1

python3 tools/orbit_synthesize.py verify-executable \
  --input executable.json
```

## Practical relevance

This completes the first full OrbitSynthesis chain:

```text
finite declarative problem
  -> optimal symmetry-compatible domain
  -> complete semantic controller
  -> original-signature executable DAG
  -> independently checkable evidence bundle.
```

A downstream system can now consume a compact operation DAG instead of a raw
truth table while retaining a complete semantic fallback for verification.
Potential uses include policy/controller review, compiler regression, formal
methods benchmark artifacts, Tau or code-generation adapters, and deployment
pipelines that require offline replay.

## Boundary

The generic compiler is bounded and intended for small controllers or shallow
terms. The fixed-Q asymptotic compiler is not yet integrated as a specialized
large-instance backend. Search statistics are compiler provenance rather than
an independently verified claim that every possible term within a succinct
representation was explored.

This result does not establish:

- nondefinability after an unsupported search;
- minimum DAG size or depth;
- polynomial compilation time;
- bounded-fanout or formula complexity;
- machine-code, hardware, gas, or timing correctness;
- end-to-end Lean verification;
- external review, novelty, product-market fit, patent/FTO, or legal clearance.

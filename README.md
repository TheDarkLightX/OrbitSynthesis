# OrbitSynthesis

Mathematical research on reactive synthesis over infinite logical structures, beginning from Ohad Asor's work on Tau, atomless Boolean algebras, and `ocLTL` over effectively presented omega-categorical structures.

## Research rule

This repository separates **proved**, **computationally checked**, **conjectured**, **refuted**, and **unknown** claims. Literature claims must have provenance. Failed conjectures and minimal counterexamples are first-class research outputs.

## Proof philosophy

Prefer proofs that expose the structural reason a statement is true: symmetry, quotient, invariant, universal property, canonical representation, or another mechanism that explains the result rather than merely certifying it. This is the project's Noether-style criterion for explanatory proofs.

## Initial frontier

The first program studies three questions that arise directly from the current literature:

1. **Exact type-space structure.** Understand complete type spaces and their growth in concrete omega-categorical theories, starting with the countable atomless Boolean algebra.
2. **Direct fixed points.** Determine when synthesis fragments can be solved directly by first-order fixed-point iteration over an omega-categorical structure, avoiding full type enumeration and propositionalization.
3. **Specification-generated compression.** Quantify exactly how much of a complete type a given specification actually needs, following the optimization in Asor's `ocLTL` construction.

The repository will not assume that a Myhill-Nerode-style minimization theorem for synthesis exists. That connection remains a candidate conjecture to test against the adjacent register/nominal-automata literature.

## Practical finite-algebra kernel

The standalone research kernel also studies safety controllers constrained to be one shared term operation of a finite algebra. It can compile internal partial-symmetry constraints to exact domain models, optimize a winning domain, reconstruct a complete controller, emit independently replayable evidence, and produce a checked executable implementation.

### Portable semantic proof bundle

```bash
python3 tools/orbit_synthesize.py canonicalize \
  --input examples/proof_bundle/discriminator_policy.json \
  --out problem.json

python3 tools/orbit_synthesize.py synthesize \
  --input problem.json \
  --out bundle.json \
  --backend native

python3 tools/orbit_synthesize.py verify \
  --input bundle.json
```

The semantic bundle verifier rebuilds the finite algebra and internal-groupoid component model, reconstructs the complete controller, recomputes the signed objective, and verifies a finite optimum or infeasibility proof.

### Executable original-signature bundle

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

A successful executable bundle additionally contains a shared DAG whose nodes are only declared basic operations of the embedded finite algebra. The verifier evaluates the DAG on the complete finite input space and checks exact equality with the certified controller table. Bounded compiler exhaustion is reported as `unsupported`; it is not treated as a nondefinability proof.

### Practical compiler portfolio

```bash
python3 tools/orbit_synthesize.py synthesize-portfolio \
  --input examples/proof_bundle/discriminator_policy.json \
  --out portfolio.json \
  --backend native \
  --portfolio-policy practical

python3 tools/orbit_synthesize.py verify-portfolio \
  --input portfolio.json
```

The portfolio records four distinct tiers:

```text
tiny       exact semantic closure
medium     fixed-Q structural signed-router recognition
practical  reduced ordered vector MDD
research   fixed-Q Shannon diagnostic only
```

The Shannon/Lupanov lane is never automatically selected. A portfolio result either contains a verified original-signature DAG or a separately typed MDD implementation. The verifier recomputes the deterministic selection from the recorded attempts and policy.

See:

```text
notes/PORTABLE_PROOF_BUNDLES.md
notes/ORIGINAL_SIGNATURE_DAG_BUNDLES.md
notes/COMPILER_PORTFOLIO.md
schemas/finite_safety_problem_v1.schema.json
schemas/proof_bundle_v1.schema.json
schemas/controller_dag_artifact_v1.schema.json
schemas/executable_proof_bundle_v1.schema.json
schemas/mdd_artifact_v1.schema.json
schemas/compiler_portfolio_v1.schema.json
schemas/portfolio_proof_bundle_v1.schema.json
```

The current v1 interface is explicit and finite, assumes the caller has justified quasi-primal interpolation, and does not yet provide a temporal or omega-categorical frontend. The original-signature compilers are incomplete by design; MDD output is exact executable behavior but is not claimed to be an algebra term.

## Status

Research program bootstrapped August 2026. See the research branch / draft pull requests for active claims and experiments.

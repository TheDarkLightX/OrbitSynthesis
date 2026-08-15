# Portable finite-safety problems and proof bundles

**Status:** v1 source format and proof-carrying synthesis interface. The parser,
solver, controller replay, and optimum/infeasibility proof gates are committed;
the integrated GitHub job remains subject to the repository's runner billing
block.

## 1. Goal

A user should not need to edit Python or trust an optimization process. The v1
workflow is:

```text
problem.json
    |
    v
finite algebra and safety-table validation
    |
    v
internal-isomorphism component compilation
    |
    v
native branch-and-bound or HiGHS search
    |
    v
complete controller reconstruction
    |
    v
state-search optimum/infeasibility certificate
    |
    v
bundle.json
```

A separate verification command rebuilds the model and checks the entire
bundle.

## 2. Commands

Canonicalize and validate a user problem:

```bash
python3 tools/orbit_synthesize.py canonicalize \
  --input problem.json \
  --out canonical-problem.json
```

Synthesize with the dependency-free native backend:

```bash
python3 tools/orbit_synthesize.py synthesize \
  --input canonical-problem.json \
  --out bundle.json \
  --backend native
```

Use SciPy/HiGHS for the Boolean optimization search:

```bash
python3 tools/orbit_synthesize.py synthesize \
  --input canonical-problem.json \
  --out bundle.json \
  --backend highs
```

Verify without trusting the backend result:

```bash
python3 tools/orbit_synthesize.py verify \
  --input bundle.json
```

Examples live under:

```text
examples/proof_bundle/
```

## 3. Finite-safety problem v1

Schema identifier:

```text
orbit-synthesis/finite-safety-problem/v1
```

The formal JSON Schema is:

```text
schemas/finite_safety_problem_v1.schema.json
```

### Carrier and operations

Carrier elements are JSON integers or strings. Each basic operation supplies
its outputs in product order over the declared carrier.

For carrier `[0,1,2]`, a binary operation table is ordered as

```text
(0,0),(0,1),(0,2),(1,0),...,(2,2).
```

OrbitSynthesis checks completeness, arity, carrier closure, distinct operation
names, and the exact output count.

### Safety relation

The relation may be an explicit allowlist or denylist:

```json
{
  "mode": "allowed",
  "transitions": [
    {"state": [0], "input": [1], "output": [2]}
  ]
}
```

Canonical serialization always emits the semantic allowlist, so different
input encodings of the same finite problem receive one semantic problem hash.

### Objective

The primary objective is signed state utility:

```text
sum_(s in selected domain) weight(s).
```

The input can provide:

- a default integer state weight;
- per-state integer overrides;
- required states;
- forbidden states.

### Semantic premise

The v1 controller mode is

```text
quasi_primal_internal_groupoid.
```

The caller must explicitly acknowledge the quasi-primal premise. This is not a
mere license checkbox: the interpolation theorem is the mathematical bridge
from internal-isomorphism-compatible tables to original-signature term
operations. The current parser does not attempt to decide quasi-primality for
arbitrary finite operation tables.

## 4. Proof bundle v1

Schema identifier:

```text
orbit-synthesis/proof-bundle/v1
```

The formal JSON Schema is:

```text
schemas/proof_bundle_v1.schema.json
```

A bundle contains:

```text
canonical input problem
problem semantic SHA-256
compiled component-model SHA-256
backend name and semantic result hash
selected domain and signed utility
one component-rule choice per internal-groupoid component
complete controller table on every observation
state-search optimum or infeasibility certificate
bundle manifest SHA-256
```

The bundle intentionally excludes machine-dependent timing from all semantic
hashes.

## 5. Independent verification

Verification performs the following steps:

1. parse and canonicalize the finite algebra and game;
2. recompute the problem hash;
3. enumerate subalgebras and internal isomorphisms;
4. rebuild every observation component and candidate rule;
5. recompute the component-model hash;
6. verify every selected rule accepts the returned domain;
7. reconstruct the complete controller table from those rule choices;
8. compare it with the serialized controller;
9. recompute signed domain utility;
10. verify the complete state-search proof tree;
11. recompute the bundle manifest.

The optimizer is not used during verification.

## 6. Optimal and infeasible examples

### Discriminator policy

```text
examples/proof_bundle/discriminator_policy.json
```

The uniquely safe transition is

```text
x' = d(x,i_0,i_1).
```

All three states form the optimum domain of score `3`. The emitted controller
has `27` total observation rows and is exactly the discriminator table.

Because all three state weights are positive and the full domain is feasible,
the exact optimum proof is a one-node root bound.

### Coupled required policy

```text
examples/proof_bundle/coupled_required_infeasible.json
```

States `0` and `1` are required. Safety asks for

```text
f(0)=0,
f(1)=0.
```

But every unary term of Quackenbush `Q` obeys

```text
f(1)=1-f(0)
```

on the proper Boolean subalgebra. Hence no shared term controller satisfies the
required states. The emitted certificate is a component conflict, not a
backend-only `UNSAT` status.

## 7. Trust boundary

The following statements remain separate:

```text
backend found a model
controller witness verified
primary optimum/infeasibility proved
```

A backend semantic hash is provenance, not mathematical authority. The final
authority comes from the model-bound state-search certificate.

## 8. Limitations

The v1 format is deliberately finite and explicit:

- carrier elements are integers or strings;
- operation tables are complete;
- safety transitions are explicitly tabulated;
- only quasi-primal internal-groupoid semantics are integrated;
- the state-search proof may be exponential;
- no user-supplied succinct term/equation language is parsed yet;
- original-signature DAG emission is not yet included in the portable bundle;
- no temporal or omega-categorical frontend is included;
- no quasi-primality decision procedure is claimed.

These restrictions create a fail-closed, interoperable foundation rather than
a vague universal input language.

## 9. Next software increments

1. serialize compiled component models as an optional verifier cache;
2. include original-signature DAG artifacts when a supported compiler exists;
3. add action preferences and secondary objective certificates;
4. add user-supplied equation-defined safety relations;
5. compress state-search trees into proof DAGs with learned conflicts;
6. add VeriPB/LRAT translation for general optimization backends;
7. add stable package entry points and versioned release artifacts;
8. connect finite quotients produced by orbit/type frontends.

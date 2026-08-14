# Practical clone-constrained synthesis vertical slice

Date: 2026-08-14  
Verdict: **PASS for the first end-to-end practical OrbitSynthesis pipeline.**

## Result

The new pipeline connects the repository's previously separate finite-algebra,
safety, groupoid, maximal-domain, and term-compilation components behind one
deterministic interface:

```text
finite algebra + explicit safety relation + initial states
  -> ordinary / semi-primal / automorphism / internal-groupoid comparison
  -> maximal compatible invariant domain
  -> total strategy table
  -> original-signature Q DAG when the strategy is conservative
  -> replayable JSON certificate.
```

This is the first project artifact aimed primarily at a usable synthesis
workflow rather than another fixed-Q compiler constant.

## Public API

`src/orbitsynthesis/practical.py` supplies:

- deterministic JSON model loading and normalization;
- side-by-side controller-semantics analysis;
- exact quasi-primal domain search via the existing pointed/nogood kernel;
- an explanatory internal-isomorphism conflict trace;
- conservative-table extraction as coordinate-selector tables;
- a parameter-free `{d,u}` backend for exact Quackenbush Q;
- canonical multi-root DAG serialization;
- exhaustive DAG replay; and
- complete certificate verification.

The v1 compiler is deliberately fail-closed. Arbitrary finite algebras can be
analyzed, but original-signature compilation is reported as unsupported unless
the algebra is exactly Q and every output coordinate is conservative. It does
not silently replace original-signature terms by illegal named constants.

`tools/orbit_synthesize.py` exposes the pipeline as a CLI over model JSON or two
built-in examples.

## Positive example

The model has one Q-valued state, two Q-valued inputs, and the unique safe
controller

```text
next = d(state,input_0,input_1).
```

All four semantic levels retain all three states:

```text
ordinary = semi-primal = demi-semi-primal = quasi-primal = 3 states.
```

The compiler recognizes the table structurally and emits exactly

```text
d(x_0,x_1,x_2)
```

with one operation node, depth one, and exhaustive replay over all 27
observations.

## Negative example

The 13-transition Quackenbush-Q coupling instance retains the three-state
relaxation

```text
{(0,0),(1,0),(1,1)}
```

under ordinary, generated-subalgebra, and global-automorphism semantics. Yet no
nonempty domain is compatible with the internal automorphism of `{0,1}`.

The practical diagnostic identifies the critical component

```text
source observation (0,0,1)
target observation (1,1,0)
forced source output (1,0)
transported output (0,1)
target allows only (1,0).
```

The instance is therefore rejected before compilation with a structured
`groupoid_component_unsatisfiable` certificate.

## Evidence

The primary checker verifies:

- JSON model roundtrip;
- bitset-nogood versus exhaustive domain-search agreement;
- all four semantic modes on both examples;
- positive one-node compilation and all 27 semantic rows;
- negative ordinary/semi/demi separation from quasi-primal realizability;
- presence of a transported-output conflict;
- complete certificate replay; and
- rejection of an effective compiled-DAG mutation.

A no-import audit independently parses the generated JSON artifacts, validates
the Q operation tables, replays the serialized DAG, recomputes the ordinary and
semi-primal fixed points, exhausts all 512 state domains of the negative
instance, and reconstructs the explicit internal-isomorphism contradiction.

Primary semantic SHA-256:

```text
11e7d5a7161e852c63f77ff646b7ae2ecb4987f28b24aa7b9b4e3224225a4807
```

Independent semantic SHA-256:

```text
2d7e394e5c4254d2e5dc95cbb147e87fa01feb07fee4be7051c3928966717c20
```

## Boundary

This v1 artifact is a practical research kernel, not a claim that arbitrary
finite term clones can already be compiled. Its exact original-signature
backend is restricted to conservative Q strategies. The next implementation
steps are a general controller IR, weighted maximal-domain optimization,
minimal symmetry-conflict cores, compiler portfolios, and external
BDD/MDD/logic-synthesis benchmarks.

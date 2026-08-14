# Greatest-region and list-subpower frontier

Date: 2026-08-14  
Verdict: **the greatest-region conjecture is closed in the one-equation
fragment, list-constrained quasi-primal subpowers are tractable, and the same
component structure now compiles domain optimization to CNF/MaxSAT.**

## Results

### 1. Exact greatest-region boundary

For finite quasi-primal algebras, demi-semi-primality is equivalent to the
following universal property:

> every finite shared-term safety instance whose safe relation is defined by
> one original-signature equation has a greatest term-winning invariant
> domain.

Equivalently, the same holds for every relation invariant under the full
internal-isomorphism groupoid.

The positive direction is the existing orbit/stabilizer greatest-fixed-point
theorem. The converse constructs a no-greatest game from every graph-maximal
nonextendable internal isomorphism.

The generic witness has two term-winning domains, an infeasible union, and no
term-winning common upper bound. Two partial-symmetry images are made dead
outside the source/codomain subalgebras; maximal nonextendability prevents
those dead observations from propagating back into either one-sided winner.

The relation is principal. Flatten a transition to `x`, let `p(x)` be its
first coordinate, and define

```text
g(x)=x_1 on safe tuples,
g(x)=x_2 on unsafe tuples.
```

Every unsafe tuple carries two distinct tagged subalgebra coordinates. Safety
is groupoid invariant, so `g` preserves every internal isomorphism; both
branches are projections, so `g(x)` remains in the generated subalgebra.
Quasi-primal interpolation makes `g` a term, and safety is exactly the single
equation `p=g`.

### 2. Quasi-primal list-subpower tractability

For a fixed finite quasi-primal algebra `A`, generators in `A^n`, and arbitrary
unary coordinate lists, deciding

```text
Sg_(A^n)(G) intersect Product_i L_i != empty
```

is polynomial-time.

Transpose the generators into evaluation rows. Rows split into connected
components under internal isomorphisms. A value at one component
representative propagates uniquely because the row generates its subalgebra.
The instance is feasible exactly when every component has one propagated value
meeting all lists.

The implementation returns a generated evaluation vector and finite groupoid
certificate, or one component obstruction recording why every representative
value failed.

### 3. Practical fixed-domain safety backend

`src/orbitsynthesis/safety_components.py` exposes the same component solver for
vector-valued safety outputs. It returns either a complete compatible strategy
table or one `StrategyComponentObstruction` containing:

- the failing groupoid component;
- any locally empty observations; and
- the first transport/cycle reason rejecting every representative output.

This turns fixed-domain infeasibility into a reusable nogood rather than only a
Boolean verdict.

### 4. Exact CNF and weighted-MaxSAT compilation

For each observation component and each compatible transported output table,
compile:

```text
F = states forbidden by an unsafe forced transition,
E = safe closure implications source -> selected successor.
```

Introduce state variables `X_s` and component-rule selectors `Y_(C,tau)`.
The hard clauses are

```text
OR_tau Y_(C,tau),
not Y_(C,tau) or not X_s                   for s in F,
not Y_(C,tau) or not X_s or X_t            for (s,t) in E.
```

Required initial states are hard unit clauses. A state assignment extends to a
satisfying selector assignment exactly when it is a term-winning domain.
Selected rules reconstruct the controller table.

Adding soft units `(X_s,w_s)` gives an exact weighted partial-MaxSAT model for
a maximum-value term-winning domain. The direct explicit encoding has
polynomial size in the game table and internal groupoid; it is an exact
reduction to an NP optimization backend, not a polynomial algorithm for the
NP-hard variable-domain problem.

Implementation:

```text
src/orbitsynthesis/domain_model.py
notes/QUASIPRIMAL_DOMAIN_MAXSAT_COMPILATION.md
```

It emits DIMACS CNF and weighted DIMACS without requiring a SAT package.

## Deterministic evidence

Core frontiers:

```text
check_frontiers.py
audits/independent/audit_frontiers_independent.py
```

Principal-equation strengthening:

```text
check_principal_equation.py
audits/independent/audit_principal_equation_independent.py
```

Practical component and domain compilation:

```text
check_component_backend.py
check_domain_model.py
```

Together they check:

- `27,510` exact primary list-subpower instances against explicit closure;
- `14,280` independently reconstructed list instances, including all
  `13,755` Quackenbush-Q cases in scope;
- `400` additional deterministic randomized list instances;
- all `27` unary expansions of the three-element discriminator;
- exactly `15` extension-property expansions and `12` nonextendable ones;
- a generic no-greatest witness for every one of the `12`;
- `236,196` flattened transition rows in each principal-equation
  reconstruction;
- exact `safe iff p=g`, generated-subalgebra preservation, and groupoid
  equivariance for every one-equation separator;
- `768` randomized fixed-domain safety comparisons for the obstruction API;
- `768` independently seeded randomized domain/CNF comparisons: `145`
  feasible and `623` infeasible;
- exact maximal-domain agreement on every three-state random game;
- direct replay of satisfying CNF witnesses and failing component clauses;
- DIMACS and WCNF format/weight checks;
- the principal witness pattern `left/right/union = true/true/false`; and
- byte-identical normal and optimized output for all six implementations.

For the principal one-equation witness the compiled domain model has

```text
81 states,
243 observations,
227 groupoid components,
17,174 deduplicated candidate rules,
17,255 CNF variables,
17,405 hard clauses.
```

Semantic SHA-256 values:

```text
principal primary
  7ccb90edc475b0555f6272829390f3a4bed51a3c7d965353a9b5a9b900c5a1a4
principal independent
  a7ce96dc6a723c905a8725b98498bd4aa8c52138e50919006623f7948ee0cbdd
component backend
  81adf6174b06191b96a03bd42a70c692eb79162792dfc88a7a04dbf95e555498
domain CNF/MaxSAT
  d12b80867b60303ba80b079800f8ca8ff36aedf0a20637776fcdae10f9c18a46
```

The lane gate compiles every involved Python module, runs all six
reconstructions under ordinary Python and `python -O`, compares their bytes,
asserts the exact censuses and load-bearing verdicts, and prints source/output
SHA-256 values from the checked tree. No stale precomputed receipt is accepted
as a substitute for replay.

## Boundaries

- The list, safety, and domain-model backends assume quasi-primality is
  established independently.
- The broader cube-term/Mal'cev list-intersection frontier remains open.
- The universal state-arity cost of the converse has not been minimized.
- An external SAT/MaxSAT solver has not yet been integrated or benchmarked.
- Incremental rule generation and obstruction minimization remain open.
- Neither theorem is yet Lean-formalized or externally peer reviewed.
- No novelty, patent/FTO, or legal conclusion is asserted.

## Next actions

1. Formalize the groupoid-component interpolation lemma once in Lean; it
   supports the converse, list solver, safety backend, and domain encoding.
2. Formalize the maximal-nonextendable orbit separation and principal
   equation.
3. Add external MaxSAT adapters and model-to-controller certificate decoding.
4. Benchmark eager CNF, incremental component learning, exhaustive search,
   BDD/MDD, and generic CSP baselines.
5. Minimize and reuse component obstructions across specification updates.

# Greatest-region, list-subpower, and proof-carrying domain synthesis

Date: 2026-08-14  
Verdict: **the one-equation greatest-region conjecture is closed at
manuscript-proof level; quasi-primal list subpowers are tractable; and the
component mechanism now supports eager CNF/MaxSAT, verified solver adapters,
and lazy state-conflict learning.**

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

Required initial states are hard units. A state assignment extends to a
satisfying selector assignment exactly when it is a term-winning domain.
Selected rules reconstruct the controller table.

Adding soft units `(X_s,w_s)` gives an exact weighted partial-MaxSAT model for
a maximum-value term-winning domain. The direct explicit encoding has
polynomial size in the game table and internal groupoid; it is an exact
reduction to an NP optimization backend, not a polynomial algorithm for the
NP-hard variable-domain problem.

### 5. Solver-neutral proof-carrying boundary

`src/orbitsynthesis/domain_solver.py` and
`src/orbitsynthesis/solver_adapter.py` treat SAT/MaxSAT output as untrusted
search evidence.

The boundary:

- parses conventional `s`, `o`, and `v ... 0` output;
- rejects contradictory and out-of-range literals;
- rechecks every hard clause;
- recovers the state domain;
- requires an accepted rule in every groupoid component;
- reconstructs the complete controller table;
- checks weighted objective arithmetic; and
- distinguishes a solver's optimum claim from independently verified
  optimality.

The process adapter is shell-free, uses an explicit argv template containing
`{input}`, applies a timeout, kills the process group on timeout where
supported, limits accepted output, checks return codes, and records hashes of
the problem and solver streams.

A fake-solver adversarial audit covers valid CNF/WCNF decoding, false objective,
UNSAT, timeout, output limit, bad return code, missing placeholder, and inert
shell metacharacters. A real Open-WBO/MaxHS/RC2 performance run is still
pending.

### 6. Verified state-literal conflict learning

`src/orbitsynthesis/domain_nogood.py` translates one
`CompiledDomainFailure` into candidate violation conditions:

```text
X_s                             included forbidden state,
X_s and not X_t                 missing closure successor.
```

A conflict core contains at least one complete violation for every candidate
rule of the failing component. Negating that conjunction gives a sound
state-only CNF clause. A deterministic deletion pass makes the core
subset-minimal, though not necessarily minimum-cardinality.

`src/orbitsynthesis/domain_learning.py` turns those cores into an exact lazy
optimization loop:

```text
best unblocked state assignment
  -> component model
  -> witness or verified conflict core
  -> learned blocking clause
  -> repeat.
```

Because learned clauses exclude only component-infeasible domains, the first
feasible proposal from an exact best-state oracle is globally optimal.

The bundled oracle is bounded exhaustive search and serves as a reference. A
production loop can replace it with incremental MaxSAT while retaining the
same conflict certificates.

## Deterministic evidence

Established frontier and backend checkers:

```text
check_frontiers.py
audits/independent/audit_frontiers_independent.py
check_principal_equation.py
audits/independent/audit_principal_equation_independent.py
check_component_backend.py
check_domain_model.py
check_domain_solver.py
check_solver_adapter.py
```

New conflict-learning checkers:

```text
check_domain_nogood.py
check_domain_learning.py
audits/independent/audit_domain_learning_independent.py
```

The established packet checks:

- `27,510` exact primary list-subpower instances against explicit closure;
- `14,280` independently reconstructed list instances, including all
  `13,755` Quackenbush-Q cases in scope;
- `400` additional deterministic randomized list instances;
- all `27` unary expansions of the three-element discriminator;
- exactly `15` extension-property expansions and `12` nonextendable ones;
- a generic no-greatest witness for every one of the `12`;
- `236,196` flattened transition rows in each principal-equation
  reconstruction;
- `768` randomized fixed-domain safety comparisons;
- `768` randomized domain/CNF comparisons with exact maximal-domain agreement;
- 64 weighted solver-certificate instances; and
- the principal pattern `left/right/union = true/true/false`.

The new conflict-core checker is designed to:

- minimize a synthetic three-candidate failure to one shared literal;
- learn from every failed domain in 96 deterministic Q games;
- verify subset-minimality from the raw failure;
- exhaust every complete domain matching every learned core; and
- confirm that none is globally feasible.

The new lazy-search checker compares exact weighted optima on 24 deterministic
nine-state Q games. An independent reconstruction of the same deterministic
corpus obtained:

```text
12,288 exhaustive component-model checks,
54 lazy component-model checks,
30 learned clauses,
57 learned state literals,
4,544 complete domains matching learned cores, all infeasible.
```

The synthetic 12-state family requires two component checks instead of 4,096:
the first failure learns the one-literal clause excluding the shared forbidden
state, and the second proposal is optimal.

The no-import core audit exhausts `30,625` two-candidate condition families and
checks `2,000` larger deterministic random families.

The workflow now runs the established gate and `check_learning.sh`, with normal
versus optimized byte equality required for every new checker. GitHub-hosted
execution remains subject to the repository account's documented
payment/spending-limit block.

## Established semantic receipts

```text
principal primary
  7ccb90edc475b0555f6272829390f3a4bed51a3c7d965353a9b5a9b900c5a1a4
principal independent
  a7ce96dc6a723c905a8725b98498bd4aa8c52138e50919006623f7948ee0cbdd
component backend
  81adf6174b06191b96a03bd42a70c692eb79162792dfc88a7a04dbf95e555498
domain CNF/MaxSAT
  d12b80867b60303ba80b079800f8ca8ff36aedf0a20637776fcdae10f9c18a46
solver certificate decoder
  2fefedfe42c1ebdd5110df4793fc511a0c0e2a6d3b7b92b332e4a70ef531c3ee
external process adapter
  1d9baa61591736042271826ad4f036688cca8489e8bb9183582cdab4db86f4d8
```

New learning receipts are emitted by the checked branch at replay time rather
than copied into this report before the integrated gate runs.

## Boundaries

- The list, safety, domain-model, and learning backends assume quasi-primality
  is established independently.
- The broader cube-term/Mal'cev list-intersection frontier remains open.
- The universal state-arity cost of the converse has not been minimized.
- The lazy reference oracle still enumerates state assignments; it is a
  correctness oracle, not a scalability claim.
- No real external MaxSAT backend has yet been benchmarked in this environment.
- Minimum-cardinality conflict cores, proof traces for global MaxSAT
  optimality, and cross-update core reuse remain open.
- Neither main theorem is yet Lean-formalized or externally peer reviewed.
- No novelty, patent/FTO, or legal conclusion is asserted.

## Next actions

1. Replace the exhaustive state oracle with an incremental MaxSAT adapter and
   feed verified learned clauses back under assumptions.
2. Benchmark eager selector CNF against lazy state-only learning on antichain,
   initial-set-hardness, and random instances.
3. Compare subset-minimal cores with exact minimum-cardinality cores.
4. Cache learned conflicts across small specification updates.
5. Formalize the groupoid-component interpolation and conflict-soundness lemmas
   in Lean.
6. Obtain external universal-algebra, games, and MaxSAT review.

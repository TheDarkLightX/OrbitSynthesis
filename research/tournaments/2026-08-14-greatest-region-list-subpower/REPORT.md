# Greatest-region and list-subpower frontier

Date: 2026-08-14  
Verdict: **two source-grounded frontiers advanced; the main converse now holds
inside the one-equation fragment.**

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
outside the source/codomain subalgebras; maximal nonextendability guarantees
that those dead observations cannot propagate back into the one-sided winning
domains.

The relation can always be made principal. Flatten a transition to `x`, let
`p(x)` be its first coordinate, and define

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
- effective groupoid-edge, dead-state, and equation-branch mutations; and
- byte-identical normal and optimized output for all four implementations.

The primary principal-equation semantic SHA-256 is

```text
7ccb90edc475b0555f6272829390f3a4bed51a3c7d965353a9b5a9b900c5a1a4
```

The independent principal-equation semantic SHA-256 is

```text
a7ce96dc6a723c905a8725b98498bd4aa8c52138e50919006623f7948ee0cbdd
```

The lane gate compiles every involved Python module, runs all four
reconstructions under ordinary Python and `python -O`, compares their bytes,
asserts the exact censuses and load-bearing Quackenbush-Q verdicts, and prints
source/output SHA-256 values from the checked tree. No stale precomputed
receipt is accepted as a substitute for replay.

## Boundaries

- The list solver assumes quasi-primality is established independently.
- The broader cube-term/Mal'cev list-intersection frontier remains open.
- The universal state-arity cost of the converse has not been minimized.
- Neither theorem is yet Lean-formalized or externally peer reviewed.
- No novelty, patent/FTO, or legal conclusion is asserted.

## Next actions

1. Formalize the groupoid-component interpolation lemma once in Lean; it
   supports both the converse witness and the list solver.
2. Formalize the maximal-nonextendable orbit separation and principal
   equation.
3. Integrate the list solver into the practical finite-algebra safety kernel
   as a fixed-domain backend with obstruction learning.
4. Benchmark learned component nogoods in maximal-domain search.

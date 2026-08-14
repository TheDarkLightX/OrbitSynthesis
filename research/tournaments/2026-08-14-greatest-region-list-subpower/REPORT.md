# Greatest-region and list-subpower frontier

Date: 2026-08-14  
Verdict: **two source-grounded frontiers advanced.**

## Results

### 1. Exact greatest-region boundary

For finite quasi-primal algebras, demi-semi-primality is equivalent to the
following universal property:

> every finite internal-isomorphism-groupoid-invariant shared-term safety
> instance has a greatest term-winning invariant domain.

The positive direction is the existing orbit/stabilizer greatest-fixed-point
theorem. The new converse constructs a no-greatest game from every
graph-maximal nonextendable internal isomorphism.

The generic witness has two term-winning domains, an infeasible union, and no
term-winning common upper bound. Two partial-symmetry images are made dead
outside the source/codomain subalgebras; maximal nonextendability guarantees
that those dead observations cannot propagate back into the one-sided winning
domains.

The theorem is exact for groupoid-invariant relations. A universal
single-equation version remains open.

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

Primary checker:

```text
research/tournaments/2026-08-14-greatest-region-list-subpower/check_frontiers.py
```

Independent no-import checker:

```text
research/tournaments/2026-08-14-greatest-region-list-subpower/audits/independent/audit_frontiers_independent.py
```

Together they check:

- `27,510` exact primary list-subpower instances against explicit closure;
- `14,280` independently reconstructed list instances, including all
  `13,755` Quackenbush-Q cases in scope;
- the pure three-element discriminator and Quackenbush `Q`;
- all `27` unary expansions of the three-element discriminator;
- exactly `15` extension-property expansions and `12` nonextendable ones;
- a valid generic no-greatest witness for every one of the `12`;
- effective groupoid-edge and dead-state mutations;
- `400` additional deterministic randomized list instances; and
- byte-identical normal and optimized output for both implementations.

The lane gate compiles every involved Python module, runs both reconstructions
under ordinary Python and `python -O`, compares their bytes, asserts the exact
censuses and load-bearing Quackenbush-Q verdicts, and prints source/output
SHA-256 values from the checked tree. No stale precomputed receipt is accepted
as a substitute for replay.

## Boundaries

- The greatest-region equivalence currently covers all finite
  internal-groupoid-invariant relations, not necessarily one principal
  equation in every algebra.
- The list solver assumes quasi-primality is established independently.
- The broader cube-term/Mal'cev list-intersection frontier remains open.
- Neither theorem is yet Lean-formalized or externally peer reviewed.
- No novelty, patent/FTO, or legal conclusion is asserted.

## Next actions

1. Formalize the groupoid-component interpolation lemma once in Lean; it
   supports both the converse witness and the list solver.
2. Attack the single-equation converse specialization.
3. Integrate the list solver into the practical finite-algebra safety kernel
   as a fixed-domain backend with obstruction learning.
4. Benchmark learned component nogoods in maximal-domain search.

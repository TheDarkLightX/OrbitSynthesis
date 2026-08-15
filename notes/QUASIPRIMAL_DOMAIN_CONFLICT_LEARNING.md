# Exact conflict learning for quasi-primal winning-domain optimization

**Status:** implemented exact reference architecture, 2026-08-14. The learned
clauses are verified consequences of one failed internal-groupoid component.
The current candidate-state oracle is bounded exhaustive search; replacing it
with incremental SAT/MaxSAT is an engineering step, not a change to the
mathematical certificate boundary. External review and Lean formalization are
pending.

## 1. Motivation

The eager compiler in `QUASIPRIMAL_DOMAIN_MAXSAT_COMPILATION.md` materializes
all compatible component rules and all selector clauses at once. That gives a
clean polynomial-size reduction, but a large component portfolio may contain
many rules irrelevant to the optimum actually requested.

The dual architecture is lazy:

```text
best state assignment not yet excluded
  -> exact component feasibility check
  -> controller witness, or one failed component
  -> subset-minimal state-literal conflict
  -> learned blocking clause
  -> repeat.
```

The first feasible proposal is optimal whenever the outer state oracle returns
the best assignment satisfying all accumulated hard and learned clauses.

## 2. Candidate-rule violations

For one fixed candidate domain `W`, a component rule `tau` can fail in only two
ways.

### Forbidden-state violation

A state `s` is included although the forced transition selected by `tau` is
unsafe:

```text
X_s.
```

### Missing-closure violation

A source state `s` is included but its forced safe successor `t` is excluded:

```text
X_s and not X_t.
```

`CompiledDomainFailure` records every such violation for every candidate rule
of the first failing component.

## 3. Conflict core

Choose at least one complete violated condition for every candidate rule. The
union of their signed literals is a conjunction `K` with the property:

> every state assignment satisfying `K` defeats every candidate rule in that
> component.

Therefore every such assignment is globally infeasible. Negating `K` gives a
sound state-only CNF clause.

If

```text
K = X_a and not X_b and X_c,
```

then the learned clause is

```text
not X_a or X_b or not X_c.
```

`minimize_domain_failure` starts with a deterministic violation per candidate
and deletes every literal whose removal preserves coverage of all candidates.
The result is subset-minimal: no proper sub-conjunction remains a valid
component conflict. It is not claimed to have globally minimum cardinality.

## 4. Soundness theorem

### Theorem 1 — learned clause soundness

Let `F` be a `CompiledDomainFailure` for component `C`, and let `K` be a
verified conflict core produced from `F`. Every domain satisfying all literals
of `K` is rejected by every candidate rule of `C`; hence it is not a
term-winning domain.

**Proof.** For each candidate, the core contains one complete recorded
violation condition. A domain satisfying the core therefore either includes a
state forbidden by that candidate or includes a closure source while excluding
its selected successor. Thus no candidate accepts the domain. Since a total
term controller must select one compatible rule in every component, the domain
is infeasible. QED.

This proof is independent of which outer SAT, MaxSAT, BDD, or exhaustive oracle
proposed the state assignment.

## 5. Exact lazy optimization

`maximum_weight_domain_with_learning` uses a bounded exhaustive state oracle as
a reference implementation.

At each round it chooses the maximum-weight state set satisfying:

- required states;
- forbidden states; and
- every learned blocking clause.

The exact component model then returns either:

- `CompiledDomainWitness`, in which case the proposal is globally optimal; or
- `CompiledDomainFailure`, which is minimized, verified, and learned.

### Theorem 2 — first feasible proposal is optimal

Every learned clause excludes only infeasible domains by Theorem 1. Therefore
no feasible domain is ever removed. When the exact outer oracle proposes the
best remaining domain and it is feasible, no better feasible domain exists.

The algorithm is complete on its bounded state space because every failed
proposal is excluded and there are finitely many assignments.

## 6. Public implementation

```text
src/orbitsynthesis/domain_nogood.py
src/orbitsynthesis/domain_learning.py
```

Public objects include:

```text
SignedStateLiteral
CandidateConflictWitness
DomainConflictCore
candidate_violation_conditions
minimize_domain_failure
verify_domain_conflict_core
LearnedDomainSearchStats
LearnedDomainSearchResult
maximum_weight_domain_with_learning
```

Conflict cores can be translated directly to the state-variable numbering of
`CNFEncoding` through `DomainConflictCore.blocking_clause`.

## 7. Evidence design

The primary conflict-core checker:

- constructs a synthetic three-candidate failure sharing one literal and
  confirms reduction to a one-literal core;
- learns cores from every failed domain in 96 deterministic random Q games;
- checks subset-minimality against the raw failure;
- checks every complete domain matching each learned core and confirms that it
  is globally infeasible; and
- extracts a principal no-greatest-union conflict.

The lazy-search checker:

- uses a 12-state synthetic model where one learned literal reduces expensive
  component checks from 4,096 reference checks to two;
- compares exact weighted optima on 24 deterministic nine-state Q games;
- checks every domain matching every learned core in that corpus; and
- verifies fail-closed input and round-limit mutations.

A separately written no-import checker exhausts 30,625 two-candidate violation
families, checks 2,000 larger deterministic random families, and reconstructs
the two-check synthetic optimization.

The lane requires byte-identical normal and optimized Python output.

## 8. Interpretation and boundary

The exhaustive outer oracle is not itself the scalability claim. Its purpose is
to establish the exact lazy protocol and provide an oracle for future solver
differentials.

The production architecture is:

```text
incremental state-only MaxSAT
  -> proposed domain
  -> exact component checker
  -> verified learned state clause
  -> add clause incrementally.
```

This can avoid eagerly materializing every component selector while retaining a
proof-carrying controller boundary.

Still open:

1. benchmark eager selector CNF against a real incremental MaxSAT loop;
2. compare subset-minimal and minimum-cardinality cores;
3. cache conflicts across specification updates;
4. derive assumption-based unsatisfiable cores from external solvers;
5. formalize the signed-literal soundness lemma in Lean; and
6. measure performance on antichain and initial-set hardness families.

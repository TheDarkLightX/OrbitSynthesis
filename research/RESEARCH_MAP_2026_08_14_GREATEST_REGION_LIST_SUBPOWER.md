# OrbitSynthesis frontier reset — 2026-08-14

**Research base:** `research/fixed-q-asymptotic-constant` / PR #23.

**Decision:** the fixed-Q constant lane is frozen except for lower bounds,
formalization, or a broader model. The main program returns to shared-term
reactive synthesis and practical controller search.

## 1. Promoted results

### R1 — exact greatest-region characterization

For finite quasi-primal algebras, demi-semi-primality is equivalent to
universal existence of a greatest shared-term winning region for finite safety
relations defined by one original-signature equation. Equivalently, it is the
boundary for all internal-groupoid-invariant finite safety relations.

The generic non-demi converse uses a graph-maximal nonextendable internal
isomorphism, critical and dead observation orbits, and a principal separator

```text
g(x)=first projection  on safe tuples,
g(x)=second projection on unsafe tuples.
```

The unsafe tuples carry distinct tagged subalgebra coordinates. Groupoid
invariance and quasi-primal interpolation make `g` a term, and safety is the
single equation `first=g`.

Status:

```text
DERIVED_GENERIC_PROOF
PRINCIPAL_EQUATION_CONVERSE
PRIMARY_EXECUTABLE_RECONSTRUCTION
INDEPENDENT_NO_IMPORT_RECONSTRUCTION
236,196_FLATTENED_ROWS_PER_RECONSTRUCTION
LEAN_PENDING
EXTERNAL_REVIEW_PENDING
```

### R2 — quasi-primal list-subpower algorithm

For every fixed finite quasi-primal algebra, generated-subpower intersection
with arbitrary explicit unary coordinate lists is polynomial-time. Rows factor
over internal-isomorphism groupoid components.

Status:

```text
DERIVED_GENERIC_PROOF
WITNESS_AND_OBSTRUCTION_API
27,510_PRIMARY_EXACT_DIFFERENTIALS
14,280_INDEPENDENT_DIFFERENTIALS
LEAN_PENDING
PRIOR_ART_TERMINOLOGY_PENDING
```

### R3 — exact domain optimization model

For an explicit finite quasi-primal safety game, compile every observation
component into finitely many candidate rules. A rule consists only of:

```text
forbidden states,
source -> successor closure implications.
```

State and rule-selector variables yield a polynomial-size CNF whose state
assignment extends to a model exactly when it is a term-winning domain.
Weighted state units give an exact weighted partial-MaxSAT formulation of the
maximum-value domain problem.

Status:

```text
EXACT_CNF_THEOREM
DIMACS_AND_WCNF_EMITTERS
CONTROLLER_CERTIFICATE_RECOVERY
768_RANDOM_DOMAIN_DIFFERENTIALS
EXACT_MAXIMAL_DOMAIN_DIFFERENTIALS
SOLVER_NEUTRAL_DECODER
SHELL_FREE_PROCESS_ADAPTER
REAL_SOLVER_BENCHMARK_PENDING
```

### R4 — verified lazy conflict learning

A failed component rule set yields signed state conditions of the form

```text
X_s,
X_s and not X_t.
```

Selecting one complete violation per candidate and minimizing their union gives
a subset-minimal conjunction that defeats every candidate in that component.
Its negation is a sound state-only learned clause.

The exact reference loop repeatedly asks for the best state assignment not yet
blocked, checks it against the component model, and learns from failure. The
first feasible proposal is optimal because every learned clause removes only
infeasible domains.

Status:

```text
CONFLICT_CORE_SOUNDNESS_PROOF
SUBSET_MINIMAL_CORE_CONSTRUCTION
STATE_ONLY_BLOCKING_CLAUSES
BOUNDED_EXACT_LAZY_OPTIMIZER
30,625_INDEPENDENT_CONDITION_FAMILIES
24_NINE_STATE_WEIGHTED_DIFFERENTIALS
INCREMENTAL_MAXSAT_ORACLE_PENDING
LEAN_PENDING
```

An independent reconstruction of the deterministic nine-state corpus found:

```text
12,288 exhaustive component checks,
54 lazy component checks,
30 learned clauses,
57 learned literals.
```

This is a reduction in expensive component checks on the calibration corpus,
not yet a wall-clock scalability claim.

## 2. Principal mathematical lane

Develop the greatest-region equivalence into the reactive paper spine:

1. formalize the groupoid-component interpolation lemma;
2. formalize the positive orbit/stabilizer fixed point;
3. formalize graph-maximal nonextendability and orbit separation;
4. formalize the principal-equation separator;
5. formalize state-literal conflict soundness;
6. minimize the universal state arity or prove a lower bound;
7. relate the theorem to categorical demi-semi-primality without overstating
   novelty.

The main construction frontier is closed; the remaining work is proof
hardening, compression, prior-art comparison, and stronger lower/optimality
statements.

## 3. Principal algorithmic lane

The practical kernel now has six layers:

```text
subpower_lists.py
  fixed table/list interpolation

safety_components.py
  fixed-domain strategy or component obstruction

domain_model.py
  eager all-domain CNF / weighted-MaxSAT compilation

domain_solver.py
  solver-neutral model verification and controller recovery

solver_adapter.py
  bounded shell-free external process boundary

domain_nogood.py + domain_learning.py
  verified lazy state-conflict learning
```

End-to-end eager pipeline:

```text
explicit finite algebra and safety relation
  -> internal-isomorphism groupoid
  -> component candidate rules
  -> required-state CNF or weighted MaxSAT
  -> selected domain and component rules
  -> compatible controller table
  -> original-signature DAG compiler
  -> verification receipt
```

End-to-end lazy pipeline:

```text
state-only optimization oracle
  -> proposed domain
  -> exact component check
  -> controller witness or verified conflict clause
  -> incremental refinement
```

Next implementation targets:

1. connect a real incremental SAT/MaxSAT backend under assumptions;
2. benchmark eager selector CNF against lazy state-only learning;
3. compare subset-minimal and minimum-cardinality conflict cores;
4. cache cores across incremental specification changes;
5. add maximal-domain enumeration through blocking clauses;
6. benchmark against existing nogood search, BDD/MDD, and generic CSP;
7. classify broader cube-term/Mal'cev list languages.

## 4. Frozen lane

No further fixed-Q upper-constant PR is justified unless it proves one of:

- a matching or stronger global lower constant;
- a bounded-fanout or formula separation;
- a theorem for a broad class of finite algebras;
- an end-to-end Lean DAG theorem; or
- a measured practical compiler improvement.

## 5. Paper decomposition

### Reactive paper

Working center:

```text
shared-term safety
greatest-region iff demi-semi-primal
single-equation nonextendable-symmetry obstruction
maximal-domain antichains and initial-set complexity
component obstruction, eager MaxSAT, and lazy conflict algorithms
```

### Complexity paper

Freeze around:

```text
exact fixed-Q census
local 4/3 program-vector theorem
size-depth compiler
canonical-rank library
3/log_2(3) asymptotic upper constant
```

## 6. Evidence boundary

The promoted theorems and backends are source-grounded and executable. They
are not yet:

- externally peer reviewed;
- Lean-formalized;
- publication-novelty determinations;
- patent/FTO conclusions;
- real external-solver performance benchmarks;
- checked MaxSAT optimality proofs; or
- evidence of scalability beyond the explicit calibration instances.

# Exact CNF and weighted-MaxSAT compilation of quasi-primal winning domains

**Status:** derived algorithmic theorem and executable backend, 2026-08-14.
The construction is exact for an explicitly presented finite safety game over
a finite quasi-primal algebra.  Differential validation covers every domain of
96 deterministic random three-state games and the principal no-greatest
witness.  The reduction is not yet Lean-formalized or benchmarked against an
external SAT/MaxSAT solver.  Publication novelty remains **UNKNOWN**.

## 1. Setting

Fix a finite quasi-primal algebra `A` and an explicit safety game with

```text
states       S=A^k,
inputs       I=A^m,
observations Z=S x I,
outputs      S,
safe relation R subseteq S x I x S.
```

One coordinatewise original-signature term controller must serve every
observation.  A domain `W subseteq S` is term-winning when one total compatible
controller is safe on every observation whose state lies in `W` and always
returns a state in `W`.

The fixed-domain component algorithm decides one supplied `W`.  The present
result compiles **all possible domains at once**.

## 2. Groupoid component rules

Decompose the observation set into connected components under the internal
isomorphisms of `A`.

For a component `C`, choose a representative `z`.  Every admissible output

```text
o in S intersect Sg_A(z)^k
```

propagates uniquely through `C`.  Discard candidates whose transport is
inconsistent or leaves an internal-isomorphism domain.

For one surviving transported table `tau:C->S`, define two finite objects.

### Forbidden states

```text
F_tau={s in S :
       some (s,i) in C has (s,i,tau(s,i)) notin R}.
```

If `s in F_tau`, the domain cannot contain `s` while this component table is
selected.

### Closure edges

```text
E_tau={(s,tau(s,i)) :
       (s,i) in C,
       (s,i,tau(s,i)) in R,
       s != tau(s,i)}.
```

If the domain contains `s`, it must also contain the selected successor.

Hence `tau` is compatible with a domain `W` exactly when

```text
F_tau intersect W = empty
```

and

```text
(s,t) in E_tau and s in W  =>  t in W.
```

Candidate tables with identical `(F_tau,E_tau)` signatures may be merged.

## 3. CNF encoding

Introduce:

- one Boolean variable `X_s` for every state `s`, meaning `s in W`;
- one selector variable `Y_(C,tau)` for every surviving component rule.

For every component add

```text
OR_tau Y_(C,tau).
```

No at-most-one clause is required.  If several rules are selected, all their
constraints hold; a feasible domain always has a model selecting just one
witness rule per component.

For every forbidden state add

```text
not Y_(C,tau) or not X_s.
```

For every closure edge add

```text
not Y_(C,tau) or not X_s or X_t.
```

A required initial state is the unit clause

```text
X_s.
```

### Theorem 1 — exact domain encoding

For every `W subseteq S`, the state assignment

```text
X_s=1 iff s in W
```

extends to a satisfying selector assignment iff `W` is term-winning.

**Forward direction.**  A satisfying model selects at least one rule in each
component.  Its clauses say precisely that no included state is forbidden and
that every selected safe successor remains inside `W`.  Combining the selected
component tables gives a total generated-subalgebra-preserving,
internal-isomorphism-compatible table, hence a term controller.

**Reverse direction.**  A term-winning controller restricts to one surviving
rule on every component.  Select those rules.  Safety and invariance of `W`
make every forbidden and closure clause true.

The selected rules reconstruct the complete strategy table, so the SAT model
is a synthesis certificate rather than only a domain certificate.

## 4. Weighted partial MaxSAT

Give each state a positive integer value `w_s` and add the soft unit clause

```text
(X_s, weight w_s).
```

Keep all component and required-state clauses hard.

### Corollary 2 — maximum-value shared-term domain

An optimal weighted partial-MaxSAT model yields a term-winning domain
maximizing

```text
sum_(s in W) w_s.
```

Unit weights give maximum cardinality.  Hard units enforce a required initial
set.  Different weights support risk, utility, coverage, or priority-aware
domain selection.

This does not contradict the NP-completeness of required-initial feasibility
in the variable-domain setting.  It is an exact polynomial-size reduction to
a standard NP optimization backend, not a polynomial-time algorithm for the
NP-hard outer search.

## 5. Size

Let

```text
N_S=|S|,
N_Z=|Z|,
N_O=|S|.
```

Each component has at most `N_O` representative outputs, and all components
partition `Z`.  Candidate propagation and rule extraction therefore take
polynomial time in the explicit game and internal-groupoid presentation.

Before signature merging, the clause count is bounded by

```text
number of components
+ sum over candidate rules of
    (number of forbidden states + number of closure edges),
```

and is `O(N_Z*N_O)` in the direct explicit representation.  The number of
variables is

```text
N_S + number of candidate rules.
```

For a fixed finite algebra this is polynomial in the explicit transition
relation.

## 6. Implementation

```text
src/orbitsynthesis/domain_model.py
```

Public objects:

```text
ComponentCandidateRule
ComponentRuleSet
QuasiPrimalDomainModel
CompiledDomainWitness
CompiledDomainFailure
CNFEncoding
WeightedCNFEncoding
compile_quasi_primal_domain_model
```

The encodings emit standard DIMACS CNF and weighted DIMACS text.  The module
has no SAT-solver dependency.

A fixed domain can also be checked directly without serialization.  Failure
returns the first component where every rule either hits a forbidden state or
has a missing closure edge.

## 7. Deterministic evidence

The checker

```text
research/tournaments/2026-08-14-greatest-region-list-subpower/
  check_domain_model.py
```

performs:

- all eight domains of a targeted complement-coupled Q game;
- exact maximal-domain comparison with the established reference solver;
- CNF witness and failure-clause replay;
- DIMACS and WCNF format checks;
- 96 deterministic random safety relations and all eight domains each;
- 768 exact fixed-domain comparisons;
- 145 feasible and 623 infeasible instances in that corpus;
- exact maximal-domain comparison for every random relation; and
- the principal one-equation counterexample with
  `left/right/union = feasible/feasible/infeasible`.

For the principal witness the compiled structure has

```text
81 states,
243 observations,
227 groupoid components,
17,174 deduplicated candidate rules,
17,255 CNF variables,
17,405 clauses.
```

The normal and optimized Python receipts are byte-identical.  Recorded
semantic SHA-256:

```text
d12b80867b60303ba80b079800f8ca8ff36aedf0a20637776fcdae10f9c18a46
```

## 8. Next engineering steps

1. add adapters for Open-WBO, MaxHS, RC2, and generic DIMACS solvers;
2. decode external models into controller certificates;
3. add blocking clauses for maximal-domain enumeration;
4. learn component rules incrementally rather than compiling all candidates;
5. minimize failure cores and reuse them across specification updates;
6. compare against exhaustive search, the existing nogood engine, BDD/MDD,
   and generic CSP encodings.

# State-search optimality and infeasibility certificates

Date: 2026-08-14  
Status: **new proof-carrying optimization layer; source gate and independent
reconstruction committed.** The complete repository/HiGHS gate has not yet
executed on a GitHub runner.

## Result

OrbitSynthesis now has a backend-independent finite certificate for the
primary signed-utility claim returned by an external MaxSAT or MILP solver.
The certificate is a binary decision tree over state-membership variables.
Each leaf is one of:

1. **component conflict:** every internal-groupoid-compatible candidate rule
   for one observation component is already impossible under the partial state
   assignment; or
2. **objective bound:** even including every positive-weight undecided state
   cannot exceed the claimed optimum score.

For an infeasibility certificate, objective-bound leaves are prohibited: every
complete branch must end in a component conflict.

The verifier checks the tree without rerunning the optimizer that found the
controller. It recomputes every partial candidate conflict, every signed
upper bound, the complete branch partition, the target-domain score, and one
compatible controller witness.

## Soundness theorem

Let a partial assignment be a pair `(I,E)` of included and excluded states.
It represents all complete domains `D` satisfying

```text
I subseteq D,
D cap E = empty.
```

For a component candidate `tau`, the only ways it can already be impossible
are:

```text
F_tau cap I != empty,
```

or

```text
(s,t) in E_tau, s in I, t in E.
```

Both conditions persist under every completion of `(I,E)`. Therefore if every
candidate of one component is impossible, no completion is a term-winning
domain.

For weights `w`, every completion has score at most

```text
sum_(s in I) w(s)
+ sum_(s undecided) max(0,w(s)).
```

Thus a bound leaf with value at most `S` proves that no represented completion
beats score `S`.

A branch on one undecided state partitions its cylinder into the disjoint
included and excluded subcylinders. Induction over the finite certificate tree
therefore proves:

```text
all feasible domains have score <= S.
```

If the certificate also replays one feasible target domain of score `S`, that
domain is globally optimal for the primary signed objective.

If no target score is supplied and every leaf is a component conflict, the
problem is infeasible.

## Trust boundary

A certificate is bound to:

- the complete component-model SHA-256;
- the exact ordered state-weight vector;
- required-state mask;
- forbidden-state mask;
- target score and target domain;
- every proof-tree node.

The external result is promoted only after:

- its controller witness replays against the same component model;
- its domain respects the hard state constraints;
- its signed utility equals the certified optimum;
- the proof tree verifies completely.

The resulting authority labels are:

```text
state_search_certificate
state_search_infeasibility
```

## Structural theorem-family gate

The primary gate applies the proof format to two source-grounded families.

### Exact fixed-Q antichain, state arity 3

The family has two independent orientation pairs, four incomparable maximal
domains, and a unique weighted optimum of score `30`. The certificate proves
the optimum directly from the full compiled component model and then promotes
a HiGHS result.

### Principal one-equation witness

The full eager model has:

```text
81 states
243 observations
227 groupoid components
17,174 candidate rules
```

The four-state union restriction has `16` possible subsets, `8` feasible
subsets, and a unique binary-place optimum of score `13`. A separate
infeasibility certificate proves that forcing the entire four-state union is
impossible.

The committed gate also checks JSON round-trip and rejects mutated bounds,
invalid component indices, cyclic proof graphs, cross-model use, altered target
scores, and an infeasibility certificate containing a bound leaf.

## Independent reconstruction

The no-import audit reimplements the proof calculus from scratch. It checks:

```text
abstract antichain with 2 pairs:
  18 feasible domains
  unique optimum score 9
  11 proof nodes

abstract antichain with 6 pairs:
  1,458 feasible domains
  unique optimum score 133
  47 proof nodes

random exact corpus:
  240 models
  210 optimality certificates
   30 infeasibility certificates
  1,182 total proof nodes
     59 maximum proof nodes
```

All exhaustive objective verdicts agree. Four effective proof mutations are
rejected.

Independent semantic SHA-256:

```text
d0788afe189c8db59c2b24719cc940b805ca5bafa278a2710217e4ef279e91a1
```

## Practical relevance

This closes a specific proof-carrying gap:

```text
external solver model
    -> checked feasible controller
    -> finite independently checkable optimum proof.
```

The verifier is much smaller than the optimizer and does not depend on the
solver's search heuristics, floating-point branch-and-bound state, or
`OPTIMUM FOUND` status line.

The format is useful for:

- auditable controller deployment;
- regression testing across optimization backends;
- archival scientific evidence;
- cross-checking HiGHS, RC2, and command-line MaxSAT solvers;
- small or structurally compressible safety instances;
- eventual proof-object exchange with a Tau or formal-methods frontend.

## Boundary

The certificate may be exponential. This lane does not prove polynomial-size
optimality certificates, coNP containment under a succinct input model,
proof-producing unrestricted MaxSAT, or a wall-clock advantage. It does not
replace LRAT/VeriPB-style proof systems; rather, it supplies a domain-specific
state/component proof format whose leaves can later be compressed, shared, or
translated to a general proof checker.

Lean formalization, external review, and unrestricted large-instance proof
traces remain open.
# Independent unary weighted-domain audit

Date: 2026-08-14  
Verdict: **frozen exact ground truth for the declared unary corpus.**

## Scope

This script imports no OrbitSynthesis implementation. It independently uses
the complete unary original-signature term clone of Quackenbush's algebra

```text
Q=({0,1,2};d,u).
```

Internal complement on the proper subalgebra `{0,1}` forces

```text
f(1)=1-f(0),
```

while the observation `2` generates all of `Q`. Hence the unary term functions
are exactly

```text
(f(0),f(1),f(2))
with f(0) in {0,1} and f(2) in {0,1,2},
```

for a total of six functions.

## Exhaustion

The audit enumerates:

```text
512 directed unary safety relations,
8 candidate state domains,
6 weighted/hard-constraint scenarios,
6 unary term functions.
```

For a candidate domain `W`, it accepts exactly when one of the six term
functions maps every active source to an active target through an allowed
transition.

It then maximizes

```text
(weight sum, cardinality, canonical mask)
```

by direct enumeration.

The resulting corpus contains

```text
3,072 instances,
2,880 feasible,
192 infeasible,
```

with SHA-256

```text
ab589ba21f07278b82308c9a79dbc90b6846b882345764efb66df72c7e3e4346
```

The independent preference check assigns score `13` uniquely to

```text
(1,0,2),
```

the unary table that complements `0/1` and fixes `2`.

## Receipt

Committed receipt:

```text
receipt.json
```

Semantic SHA-256:

```text
1893ead79ed69ff556dde90596d453df5bf3314677b6992f3b59d3dfd6d61aba
```

The lane gate requires normal and optimized Python outputs to be byte-identical
and equal to that receipt.

## Boundary

This audit is complete for unary `Q` instances only. It does not independently
verify the generic branch-and-bound implementation on unbounded state spaces,
the algebraic characterization of higher-arity term tables, or the emitted
WCNF syntax. Those are covered by separate primary/component checks.

It is deterministic validation evidence, not Lean formalization, external peer
review, novelty evidence, or a practical performance benchmark.
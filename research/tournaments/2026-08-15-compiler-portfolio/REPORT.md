# Practical compiler portfolio

Date: 2026-08-15  
Status: **implementation, exact finite replay lane, and independent JSON audit
committed. Integrated repository execution remains pending an available
runner.**

## Result

OrbitSynthesis now treats controller compilation as a portfolio rather than
promoting the asymptotic fixed-Q compiler to the default practical backend.

```text
tiny       exact semantic closure
medium     fixed-Q structural signed-router recognizer
practical  reduced ordered vector MDD
research   fixed-Q Shannon diagnostic, never auto-selected
```

The portfolio can be restricted to original-signature implementations or to
MDD-only execution. The practical policy uses the fixed tier order above and
records diagnostic size/depth metrics without allowing them to override the
semantic-strength hierarchy.

## Structural backend

The fixed-Q recognizer checks the exact carrier and complete `d/u` operation
tables before applying any special rule. It recognizes projection/unary rails,
one discriminator layer, unary postprocessing, and one nested router layer.

The calibration

```text
(d(x0,x1,d(x2,x3,x4)),
 u(d(x0,x1,d(x2,x3,x4))))
```

must compile as exactly three shared nodes and depth three.

## MDD backend

The MDD is vector-output, reduced, ordered, and multi-terminal. It tries
natural, reverse, and output-influence variable orders and selects the smallest
reduced diagram. A successful artifact carries an exhaustive table-equivalence
certificate.

Graph validation occurs once per certification. Row replay then uses a
precomputed carrier index, avoiding repeated whole-diagram validation for each
truth-table row.

The MDD is deliberately typed separately from an original-signature DAG. The
portfolio does not erase that semantic distinction.

## Research backend boundary

The fixed-Q Shannon attempt is a diagnostic receipt only:

```text
materialized: false
automatic_selection: false
```

It cannot receive a selection priority or become the selected backend. This
preserves the circuit-complexity theorem without claiming that its explicit
construction is the best implementation for a table already containing `3^r`
rows.

## Selection binding

A second verifier recomputes the selected backend from:

```text
policy
compiled attempts
fixed tier order
```

A portfolio bundle is rejected if it selects a lower-priority tier while a
higher tier compiled, claims unsupported despite an eligible candidate,
selects a policy-excluded implementation, duplicates a backend attempt, or
promotes the research diagnostic to executable status.

Attempt size and depth scores remain diagnostic evidence only.

## Primary gate

`check_compiler_portfolio.py` is designed to check:

- exact closure selected for the 27-row discriminator example;
- one-node fixed-Q structural compilation when exact closure is disabled;
- an MDD-only executable bundle for the same certified controller;
- three-node nested signed-router compilation;
- MDD compression of a 729-row repeated-subcube table;
- explicit unsupported behavior when every materialized backend is disabled;
- no implementation on an infeasible synthesis result;
- normal/optimized JSON determinism;
- bundle and portfolio round-trip;
- Shannon-selection, selected-attempt, and manifest mutations.

`check_portfolio_selection.py` separately checks fixed tier ordering,
unsupported-status consistency, duplicate attempts, policy filtering, and the
fact that diagnostic score changes do not alter tier priority.

## Independent audit

The no-import audit consumes only emitted portfolio JSON files. It independently:

- recomputes outer, inner, and portfolio hashes;
- parses the embedded finite algebra operation tables;
- validates and evaluates original-signature DAG references;
- validates MDD reduction, ordering, and references;
- checks every emitted controller row;
- confirms the research Shannon attempt is diagnostic and unselected;
- confirms infeasible bundles contain no implementation.

## Practical meaning

The compiler can now make a different decision from the mathematics paper:

```text
small exact term            -> semantic-closure DAG
medium recognized Q term    -> structural signed-router DAG
larger repeated table       -> MDD
asymptotic theorem lane     -> recorded research evidence only
```

This is the correct separation between:

- a theorem about worst-case term complexity;
- a practical compiler for explicit finite artifacts;
- a runtime representation suitable for downstream code generation.

## Boundary

No claim is made that:

- the retained diagnostic scores predict wall-clock or hardware cost;
- the structural recognizer is complete;
- MDD output is a term operation in the original signature;
- the MDD orders are optimal;
- the Shannon compiler is materialized;
- the portfolio beats BDD packages, e-graphs, logic synthesis, or mature
  compiler toolchains;
- the integrated GitHub gate has passed;
- the work is Lean formalized or externally reviewed.

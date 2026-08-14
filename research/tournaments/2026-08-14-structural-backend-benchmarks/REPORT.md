# Structural theorem-family backend benchmark

Date: 2026-08-14  
Status: **implemented; independent structural receipt fixed; full optional-backend gate pending executable runner.**

## Purpose

The first external-backend lane used small synthetic component-rule families to
validate the adapter boundary.  This lane instead exercises the exact reactive
objects that motivate OrbitSynthesis:

1. the fixed-Q exponential maximal-domain antichain; and
2. the generic principal one-equation no-greatest-region witness.

The goal is not merely to ask whether HiGHS or RC2 returns a model.  Every
returned controller is checked by OrbitSynthesis, and its optimality or
infeasibility claim is promoted only after agreement with a separate exact
authority.

## 1. Antichain family

At state arity `k`, the construction has

```text
n=2^(k-1)-2
```

independent complement-pair orientation choices.  Hence it has exactly

```text
2^n
```

incomparable maximal winning domains, each of size

```text
3^k-2^(k-1)+1.
```

The gate materializes and replays:

| `k` | choices | maxima | size | unique weighted score |
|---:|---:|---:|---:|---:|
| 3 | 2 | 4 | 24 | 30 |
| 4 | 6 | 64 | 74 | 200 |

All maximal domains are replayed through the compiled internal-groupoid model.
A positive binary-place orientation objective gives one unique optimum.
HiGHS and, when installed, PySAT RC2 must return that domain and score.  The
arity-three case is also compared with the native weighted branch-and-bound
optimizer.

The authority label is

```text
closed_form_antichain
```

rather than the weaker `backend_status`.

## 2. Principal one-equation family

The principal witness retains its complete component formula:

```text
81 states,
243 observations,
227 components,
17,174 candidate rules,
17,255 base CNF variables.
```

Its two one-sided domains are replayed as feasible and their union as
infeasible.

For exact optimization, states outside the four-state union are fixed absent.
All 16 permitted subsets are enumerated independently while the external
backend still receives the full component-selector formula.  Binary-place
state weights give every subset a distinct primary score.  The exact restricted
census is:

```text
16 assignments checked,
8 feasible domains,
unique optimum score 13,
forced four-state union infeasible.
```

The corresponding authorities are

```text
bounded_principal_union
bounded_principal_union_infeasible
```

## 3. Independent reconstruction

The no-import audit reconstructs:

- binary complement pairs;
- the antichain maxima and closed forms at arities three and four;
- the unique weighted orientation optima;
- the Quackenbush-Q specialization of the generic principal witness;
- all 16 restricted principal domains;
- the 8/16 feasibility split;
- the unique score-13 optimum; and
- forced-union infeasibility.

It imports no OrbitSynthesis code.

Recorded semantic SHA-256:

```text
cd26a2b1b9576957615028aa44dfc1e7eb4debe4b3b33b81080bc4ddb73a23bf
```

## 4. Public implementation

```text
src/orbitsynthesis/optimization_authority.py
src/orbitsynthesis/structural_benchmarks.py
```

Public authority API:

```text
ObjectiveAuthority
closed_form_objective_authority
bounded_domain_objective_authority
certify_external_result
```

Structural family API:

```text
ExactAntichainFamily
PrincipalBackendFamily
build_exact_antichain_family
build_principal_backend_family
```

## 5. Gates and diagnostics

Semantic gate:

```text
check_structural_backends.py
check.sh
```

Independent audit:

```text
audits/independent/audit_structural_families_independent.py
audits/independent/receipt.json
```

Diagnostic timing only:

```text
benchmark_structural_backends.py
```

The semantic gate runs ordinary and optimized Python and compares output bytes.
The GitHub workflow installs SciPy and `python-sat`, requires the RC2 lane,
runs the semantic gate, and uploads a separate timing artifact.

## 6. Claim boundary

This lane establishes a stronger *validation architecture*: a checked external
controller model plus a named exact optimum authority.  It does not establish
that any external backend is asymptotically or practically fastest.

Still pending:

- execution of the complete HiGHS/RC2 structural gate on an available runner;
- wall-clock comparison on larger antichain and initial-set-hardness corpora;
- proof-producing MaxSAT or independently checkable optimality traces;
- incremental lazy-MaxSAT comparison;
- BDD/MDD, CSP, and knowledge-compilation baselines;
- Lean formalization; and
- external mathematical and systems review.

# External exact optimization backends

**Status:** practical backend and trust-boundary note, 2026-08-14.

This lane connects the exact quasi-primal domain model and the native weighted
branch-and-bound optimizer to real external optimization engines. It does not
change the algebraic characterization, the domain semantics, or the fixed-Q
term compiler.

## 1. Backend portfolio

OrbitSynthesis now exposes four complementary paths:

```text
native pointed-rule branch-and-bound
SciPy/HiGHS mixed-integer optimization
PySAT RC2 weighted MaxSAT
arbitrary Open-WBO-style command-line solver
```

The existing bounded exhaustive optimizer remains the small-instance semantic
oracle.

The public API is in

```text
src/orbitsynthesis/external_optimization.py
```

and exports

```python
solve_weighted_cnf_highs(...)
solve_weighted_cnf_pysat_rc2(...)
solve_weighted_cnf_command(...)
parse_maxsat_output(...)
weighted_soft_reward(...)
weighted_unsatisfied_cost(...)
domain_signed_utility(...)
```

## 2. Trust boundary

An external solver is treated as an **untrusted search oracle**.

For every returned feasible assignment OrbitSynthesis independently:

1. validates variable ranges and contradictory literals;
2. fills omitted Boolean variables deterministically;
3. checks every hard CNF clause;
4. recovers the selected state domain;
5. checks every selected component rule against that domain;
6. reconstructs one total internal-groupoid-compatible controller table;
7. recomputes the soft-clause reward and unsatisfied cost; and
8. recomputes the signed state utility.

A returned model is therefore a checkable feasibility/controller certificate.
A model alone is not a compact proof that no better model exists. Global
optimality and infeasibility remain backend claims unless one of the following
is also supplied:

- a solver proof accepted by a proof checker;
- bounded exhaustive verification;
- exact native OrbitSynthesis replay;
- or agreement with an independent exact backend.

`ExternalOptimizationResult` records this distinction explicitly:

```text
certificate_verified
optimality_authority
```

## 3. Signed WCNF objective

For a state variable `X_s` and integral utility `w(s)`, the existing domain
model emits

```text
w(s)>0  -> soft unit  X_s  with weight  w(s)
w(s)<0  -> soft unit -X_s  with weight -w(s)
w(s)=0  -> no soft clause
```

The soft reward is

```text
sum_{w(s)<0} -w(s) + sum_{s in W} w(s).
```

The first term is independent of the selected domain. Thus maximizing WCNF
reward is exactly equivalent to maximizing signed domain utility.

Required states are positive hard units. Forbidden states are negative hard
units.

The external backends optimize the primary signed utility. The native solver
additionally applies deterministic tie-breaking by domain cardinality and then
canonical state mask, and can optimize action preferences after the domain is
fixed. External and native domains therefore need not coincide when the
primary utility has several maximizers. They must coincide when the primary
score uniquely identifies a domain.

## 4. HiGHS translation

SciPy's `milp` interface is a wrapper around HiGHS. For one hard clause

```text
x_1 or ... or x_p or not y_1 or ... or not y_q
```

OrbitSynthesis emits the exact binary linear inequality

```text
x_1+...+x_p-y_1-...-y_q >= 1-q.
```

All variables have bounds `[0,1]` and integral type. A positive soft unit of
weight `a` contributes `-a*x` plus a fixed constant `a` to unsatisfied cost; a
negative soft unit contributes `a*x`.

HiGHS stores coefficients as binary64 values. The adapter therefore rejects a
total soft weight above `2^53-1`, the largest integer exactly representable by
binary64. Larger exact objectives should use an integer MaxSAT backend.

## 5. PySAT RC2

When `python-sat` is installed, the adapter constructs a PySAT `WCNF`, appends
all OrbitSynthesis hard clauses, appends every signed soft unit with its
weight, and calls `pysat.examples.rc2.RC2`.

The returned model and `RC2.cost` are then replayed through the same
OrbitSynthesis certificate checker used by every other backend.

Reference implementation:

- https://github.com/pysathq/pysat
- https://pysathq.github.io/docs/api/examples/rc2.html

## 6. Generic command adapter

The command backend accepts an argument vector, never a shell string.

```python
solve_weighted_cnf_command(
    model,
    cnf,
    wcnf,
    ["open-wbo", "{wcnf}"],
)
```

`{wcnf}` or `{input}` is replaced by a temporary input path. If no placeholder
appears, the path is appended. The adapter supports a working directory,
environment additions, and a hard timeout.

Expected output follows the conventional MaxSAT Evaluation/Open-WBO form:

```text
o <unsatisfied-soft-cost>
s OPTIMUM FOUND
v <signed model literals> 0
```

The objective line is checked against the returned model. A nonzero process
exit, timeout, missing model, non-optimal status, malformed literal, violated
hard clause, incompatible component rule, or objective mismatch is rejected.

Open-WBO-style format reference:

- https://github.com/sat-group/open-wbo

## 7. Evidence

### Locally executed smoke

The exact adapter source was exercised in the current execution environment
against:

- SciPy 1.17 / HiGHS; and
- the independent subprocess WCNF reference implementation in this lane.

Both returned the same checked domain, unsatisfied cost, and signed utility.
The smoke also rejected wrong-cost, non-optimal-status, missing-model, and
timeout mutations.

Receipt:

```text
research/tournaments/2026-08-14-external-maxsat-benchmark/
  local_smoke_receipt.json
```

### No-import reconstruction

The independent audit imports no OrbitSynthesis code. It compiles four finite
candidate-rule families under five objective/hard-constraint scenarios,
exhausts domains and WCNF assignments separately, invokes the reference solver
as an external process, and compares feasibility and objective values.

Recorded semantic SHA-256:

```text
3295548451c93286c56971ee27d304ff3a3b50601809f16e542486d39162bd87
```

### Full differential gate

The full lane gate compares:

- exact exhaustive component semantics;
- the native weighted optimizer;
- SciPy/HiGHS;
- the external command adapter; and
- PySAT RC2 when installed.

It checks unique-primary domain agreement, signed-primary score agreement,
required/forbidden states, zero-weight ties, parser behavior, objective
mutation, status mutation, missing models, timeouts, and the HiGHS exactness
guard.

The full gate requires the repository source tree plus SciPy; the PySAT portion
requires `python-sat`. GitHub Actions has repeatedly been rejected before
runner allocation by the repository billing/spending-limit condition, so no
CI-pass claim is made until that infrastructure block is removed.

## 8. Benchmark discipline

The benchmark harness reports backend timings, formula sizes, and semantic
results. Timing output is diagnostic and machine-dependent; it is deliberately
excluded from semantic receipts.

No practical performance superiority is claimed from the current small
synthetic corpus. The next benchmark tranche should include:

- the exact antichain family;
- principal-equation no-greatest witnesses;
- random groupoid-component models;
- sparse and dense closure graphs;
- and application-level policy/synthesis instances.

## 9. Boundaries

This lane does not prove polynomial-time domain optimization, approximation
bounds, compact optimum certificates, proof-producing MaxSAT, a minimal
conflict core, or superiority over mature SAT/MaxSAT systems. It does not
establish the algebraic premise for an arbitrary supplied algebra. Lean
formalization, external performance review, publication novelty, and legal
conclusions remain separate tasks.

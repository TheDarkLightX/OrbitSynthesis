# External exact-optimization backend report

Date: 2026-08-14  
Status: **core adapter smoke PASS; independent semantic audit PASS; full
repository differential gate pending executable runner access.**

## Result

OrbitSynthesis now has three external optimization adapters over its exact
quasi-primal WCNF/domain model:

```text
SciPy/HiGHS MILP
PySAT RC2
Open-WBO-style command process
```

Every feasible model crosses the existing solver-neutral certificate boundary:
hard clauses are replayed, the selected domain is recovered, each component
rule is checked, and a complete internal-groupoid-compatible controller table
is reconstructed. Objective cost and signed utility are recomputed from the
returned assignment.

The native weighted optimizer, bounded exhaustive component semantics, and
external backends are compared by

```text
check_external_optimization.py
```

A diagnostic timing harness is provided in

```text
benchmark_external_optimization.py
```

## Trust result

The implementation makes a deliberate distinction:

```text
model/controller certificate: independently checked
optimality or infeasibility: backend status unless separately cross-checked
```

This avoids treating a feasible model as a proof that no better model exists.
The differential gate supplies such a cross-check on its bounded test corpus.

## Locally executed evidence

The exact adapter code was executed in the current container against:

- SciPy 1.17 / HiGHS; and
- the lane's independent WCNF subprocess reference.

Both returned the same checked domain

```text
{(0,)}
```

with

```text
unsatisfied cost = 3
signed utility   = 5.
```

The smoke rejected:

- a false objective line;
- a merely satisfiable rather than optimal status;
- an optimal status with no model; and
- a process timeout.

Receipt:

```text
local_smoke_receipt.json
```

Receipt SHA-256 from the executed local artifact:

```text
817f04ee78bcef5a3643be07bb1f34a2f813715df1a456e513316ca202839b82
```

## Independent audit

The no-import audit separately implements:

- candidate-rule domain feasibility;
- signed-utility optimization;
- exact hard/soft WCNF construction;
- exhaustive Boolean assignment optimization; and
- external-process output validation.

It covers four rule families and five scenarios each:

```text
20 total optimization instances.
```

The scenarios include unique positive weights, mixed signed weights, required
states, forbidden states, and all-zero ties.

Recorded hashes:

```text
rows
  c2634bf96dd934f4210d6d9b418d1fec25900c1818dcac582f62297593384672
semantic
  3295548451c93286c56971ee27d304ff3a3b50601809f16e542486d39162bd87
```

## Full gate

When its dependencies are available, `check.sh`:

1. byte-compiles all adapter and audit modules;
2. runs primary normal and optimized Python and requires byte equality;
3. runs the independent audit in both modes and compares its frozen receipt;
4. compares native branch-and-bound with exhaustive component semantics;
5. compares HiGHS and command-process primary utility with the exact optimum;
6. requires unique-primary domain agreement;
7. runs PySAT RC2 when installed, or requires it under `--require-pysat`;
8. checks parser and mutation controls; and
9. emits source and output hashes.

The dedicated GitHub workflow installs SciPy and `python-sat`, invokes the gate
with `--require-pysat`, runs the diagnostic benchmark, and uploads its JSON.
The repository account billing/spending-limit condition has prevented runner
allocation elsewhere in this project, so a workflow that executes zero steps
must not be represented as a test failure or a pass.

## Exactness boundaries

- The command adapter never invokes a shell.
- Solver output is untrusted until certificate replay succeeds.
- HiGHS objectives above `2^53-1` total soft weight are rejected because its
  binary64 coefficient representation cannot preserve every larger integer.
- The command adapter requires an objective line by default and checks it
  against the returned model.
- Infeasibility has no model certificate; it remains a backend claim unless
  independently checked.
- External backends optimize primary signed utility. Native cardinality/mask
  tie-breaking and action-preference optimization remain separate secondary
  objectives.

## Next benchmark frontier

The next practical campaign should run the external backends on:

1. the exact maximal-domain antichain family;
2. principal-equation no-greatest witnesses;
3. random sparse/dense groupoid-component models;
4. incremental specification changes; and
5. application-level access-control or protocol-policy examples.

No performance superiority claim is made from the present synthetic gate.

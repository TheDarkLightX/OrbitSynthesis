# Shell-free external SAT/MaxSAT adapter and trust boundary

**Status:** implemented portable adapter, 2026-08-14. It runs explicit solver
commands without a shell, bounds time/output, verifies every returned hard
clause, checks weighted-objective arithmetic, and decodes the model into a
complete groupoid-compatible controller certificate. No particular SAT or
MaxSAT package is bundled or benchmarked.

## 1. Design rule

An external solver is an untrusted search oracle.

OrbitSynthesis does not accept a model merely because the process exits
successfully or prints

```text
s OPTIMUM FOUND.
```

For every returned assignment it independently:

1. validates variable ranges and contradictory literals;
2. rejects an UNSAT status when a controller model was requested;
3. rechecks every hard CNF clause;
4. reconstructs the selected state domain;
5. requires at least one accepted rule in every internal-groupoid component;
6. rechecks each selected rule's forbidden-state and closure constraints; and
7. reconstructs the complete compatible controller table.

For WCNF, the reported objective is recomputed from the decoded state
assignment.

## 2. Optimality is a separate claim

A feasible MaxSAT model certifies a correct controller and its exact objective
value. It does **not** by itself certify that no better model exists.

Therefore the receipt distinguishes:

```text
solver_claimed_optimum
optimality_verified
```

The first records solver metadata. The second is true only when the caller
supplies an independently established optimum cost, for example from:

- the bounded exhaustive reference optimizer;
- a separately checked lower bound;
- or a future proof-trace verifier.

This prevents a solver's status string from being silently promoted into a
mathematical proof.

## 3. Process isolation

`SolverCommand` accepts an argv tuple containing `{input}`. The adapter:

- never invokes a shell;
- substitutes only the temporary CNF/WCNF path;
- passes all other arguments literally;
- uses a fresh temporary working directory;
- supplies no stdin;
- applies an explicit timeout;
- kills the process group on timeout where supported;
- enforces an output-size ceiling; and
- accepts only configured return codes.

Shell metacharacters inside an argument are inert.

## 4. Public API

Implementation:

```text
src/orbitsynthesis/solver_adapter.py
```

Objects:

```text
SolverCommand
SolverExecutionReceipt
VerifiedExternalModel
SolverAdapterError
SolverTimeoutError
```

Entry points:

```text
run_cnf_solver
run_weighted_maxsat_solver
parse_solver_status
parse_solver_objective
```

The adapter is solver-neutral. A caller may use Open-WBO, MaxHS, RC2, or any
other program producing conventional `s`, `o`, and `v ... 0` lines.

## 5. Deterministic audit

The audit creates a temporary fake solver process and checks:

- valid CNF model decoding;
- valid WCNF model decoding;
- exact objective recomputation;
- non-promotion of an unproved `OPTIMUM FOUND` claim;
- promotion when the independently known optimum cost is supplied;
- rejection of a wrong objective;
- rejection of UNSAT output;
- timeout termination;
- output-limit enforcement;
- rejection of an unexpected return code;
- rejection of a command without `{input}`; and
- inert shell metacharacters.

The targeted optimum is

```text
required state: 0
weights:        w(0)=5, w(1)=3, w(2)=1
optimal domain: {0,2}
value:          6
MaxSAT cost:    3.
```

Normal and optimized output are byte-identical. Recorded semantic SHA-256:

```text
1d9baa61591736042271826ad4f036688cca8489e8bb9183582cdab4db86f4d8
```

## 6. Remaining proof-carrying work

To certify optimality rather than only feasibility/objective arithmetic, add
one of:

1. a MaxSAT proof-trace checker;
2. an independently verified bound certificate;
3. a second exact backend plus a checked disagreement protocol; or
4. a SAT-based improvement query accompanied by a verifiable UNSAT proof.

Until then, external optimality remains a solver claim, while controller
correctness remains independently verified.

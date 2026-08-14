# Solver-neutral certificates for quasi-primal domain optimization

**Status:** implemented interoperability layer, 2026-08-14. This note sits on
top of the exact CNF/weighted-MaxSAT domain compilation. It does not assert
that any external solver has been benchmarked or trusted; every imported model
is rechecked and decoded into an algebraic controller certificate.

## 1. Boundary

OrbitSynthesis emits ordinary DIMACS CNF or weighted DIMACS. A deployment may
choose any compatible backend, including Open-WBO, MaxHS, RC2, a generic SAT
solver, or a hosted optimization service.

The solver is treated only as an untrusted search oracle.

Its output must be converted back to:

```text
winning state set,
one selected rule per internal-groupoid component,
complete compatible controller table.
```

All hard clauses and algebraic rule conditions are checked before the result is
accepted.

## 2. Model parser

`parse_dimacs_model` accepts conventional output such as

```text
s OPTIMUM FOUND
o 17
v 1 -2 3 ... 0
v ... 0
```

It concatenates model literals while ignoring status, objective, and comment
lines. `normalize_boolean_model` rejects:

- variables outside the declared range; and
- contradictory positive/negative literals.

Unspecified variables are treated as false; the hard-clause verifier will
reject any incomplete assignment that fails to select a component rule.

## 3. Certificate decoding

Given the original `QuasiPrimalDomainModel`, its `CNFEncoding`, and a model:

1. verify every hard clause;
2. read `X_s` variables to recover the domain;
3. require at least one true candidate selector in every component;
4. recheck that every selected candidate's forbidden/closure rules accept the
   recovered domain;
5. choose one accepted rule per component; and
6. unite their transported assignments into a total controller table.

The result is the same `CompiledDomainWitness` used by the direct component
solver.

Thus a SAT/MaxSAT output is not accepted merely because it satisfies a Boolean
file. It is translated into a finite groupoid-compatible strategy certificate.

## 4. Witness serialization

`literals_for_witness` performs the reverse transformation. Given a known
compiled witness, it produces one complete signed-literal assignment:

- true exactly on included-state variables; and
- true on exactly one selected candidate per component.

This supports:

- differential tests;
- certificate archival;
- independent SAT-model replay; and
- future proof-carrying solver adapters.

## 5. Exact reference optimizer

`maximum_weight_domain_exhaustive` is a bounded oracle for small state spaces.
It enumerates domains, calls the exact component model, and returns a
`WeightedDomainOptimum`.

It is intentionally disabled above a caller-specified state limit. Its purpose
is to validate external optimizers and benchmark encodings, not to compete
with MaxSAT on large instances.

## 6. Implementation

```text
src/orbitsynthesis/domain_solver.py
```

Public API:

```text
ParsedBooleanModel
WeightedDomainOptimum
parse_dimacs_model
normalize_boolean_model
clause_satisfied
decode_cnf_model
literals_for_witness
maximum_weight_domain_exhaustive
```

No external solver package is imported.

## 7. Deterministic evidence

`check_domain_solver.py` validates:

- a targeted weighted game with required state `0`;
- exact optimum weight `6` and domain `{0,2}`;
- multi-line solver-output parsing;
- domain and complete strategy recovery;
- rejection of contradictory literals;
- rejection when all selectors of one component are forced false;
- 64 deterministic random weighted games;
- exact agreement with direct exhaustive optimization;
- 37 decoded optimal certificates;
- 27 correctly infeasible required-state sets; and
- decoding of the 81-state principal one-equation witness's left domain.

The principal certificate contains

```text
17,255 signed variable literals,
17,174 candidate-rule variables,
17,407 hard clauses after the two required-state units.
```

Normal and optimized Python output is byte-identical. Recorded semantic
SHA-256:

```text
2fefedfe42c1ebdd5110df4793fc511a0c0e2a6d3b7b92b332e4a70ef531c3ee
```

## 8. Next step

An external adapter should remain thin:

```text
write WCNF
run configured command
capture stdout
parse model
decode and verify certificate
```

Timeouts, process isolation, and solver-specific status codes belong in the
deployment layer. The mathematical kernel should continue to depend only on
the portable certificate interface above.

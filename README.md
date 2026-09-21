# OrbitSynthesis

Mathematical research on reactive synthesis over infinite logical structures, beginning from Ohad Asor's work on Tau, atomless Boolean algebras, and `ocLTL` over effectively presented omega-categorical structures.

## Research rule

This repository separates **proved**, **computationally checked**, **conjectured**, **refuted**, and **unknown** claims. Literature claims must have provenance. Failed conjectures and minimal counterexamples are first-class research outputs.

## Proof philosophy

Prefer proofs that expose the structural reason a statement is true: symmetry, quotient, invariant, universal property, canonical representation, or another mechanism that explains the result rather than merely certifying it. This is the project's Noether-style criterion for explanatory proofs.

## Initial frontier

The first program studies three questions that arise directly from the current literature:

1. **Exact type-space structure.** Understand complete type spaces and their growth in concrete omega-categorical theories, starting with the countable atomless Boolean algebra.
2. **Direct fixed points.** Determine when synthesis fragments can be solved directly by first-order fixed-point iteration over an omega-categorical structure, avoiding full type enumeration and propositionalization.
3. **Specification-generated compression.** Quantify exactly how much of a complete type a given specification actually needs, following the optimization in Asor's `ocLTL` construction.

The repository will not assume that a Myhill-Nerode-style minimization theorem for synthesis exists. That connection remains a candidate conjecture to test against the adjacent register/nominal-automata literature.

## Status

The finite research kernels and formal checks are on `main`. Ongoing research
claims retain their stated hypotheses and bounded evidence.

## Check and run a finite controller

The [controller examples](examples/controllers/README.md) provide a callable
checker, a finite-safety producer bridge, and the OSMC table runtime used by the
TauFold adapter. The caller independently pins the contract; every admitted
environment input is checked for safety and recurring progress. A rejected
strategy comes with a finite counterexample or a repeating starvation cycle.

```bash
python3 -B research/prototypes/2026-09-12-strategy-checker/check.py
python3 -B examples/controllers/synthesize_tau_net_gate.py --output-dir /tmp/orbit-controller-demo
python3 -B scripts/run_controller.py /tmp/orbit-controller-demo/contract.json /tmp/orbit-controller-demo/strategy.json /tmp/orbit-controller-demo/controller.osmc --contract-pin /tmp/orbit-controller-demo/contract.sha256 --inputs 0 1 2 3 --json
```

The checker verifies the explicit finite model. The runtime compares every
declared memory/input step with the accepted strategy before execution.
Native Tau syntax translation, native generated-code verification, network
activation, and host authorization remain separate integration work. This
original MIT implementation does not distribute the Tau framework.

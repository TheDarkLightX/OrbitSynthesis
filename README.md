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

Research program bootstrapped August 2026. See the research branch / draft pull requests for active claims and experiments.

# Formal manuscript repairs

Date: 2026-08-13

## Verdict

**PASS for the exact declarations below.** This additive lane leaves every
frozen predecessor unchanged and closes three manuscript-facing formal gaps:

1. `Digit`, `Slot`, address, control, and depth-indexed capacity cardinalities
   are re-proved with kernel-reduced `decide` and induction; the exact printed
   dependencies are only `propext`, `Classical.choice`, and `Quot.sound`;
2. the constant-free grammar fact is stated as exhaustive constructor catalogs
   for `DTerm` and `QTerm`, instead of treating the historical
   `OriginalSignature` predicate as substantive evidence; and
3. the anchor cell, outer three-node glue, and two-plane decoder identities are
   proved directly over the original three-element algebra.

## Checked declarations

```text
card_digit_kernel
card_slot_kernel
card_address_kernel
card_control_kernel
capacity_at_depth_kernel
dterm_constructor_catalog
qterm_constructor_catalog
anchorFoldCell_semantics
anchorFoldCell_binary_left
glue_binary_zero
glue_binary_one
glue_nonbinary
twoPlaneDecode_zero
twoPlaneDecode_one
twoPlaneDecode_two
twoPlaneDecode_unused
```

`DTerm` has only branch, control, and discriminator constructors. `QTerm` has
only variable, unary, and discriminator constructors. This is the relevant
no-nullary-constant fact; a proposition true of every well-typed term adds no
extra certificate.

The decoder's unused codeword `(1,1)` maps to `2`; the claimed two-plane
compiler uses only `00`, `01`, and `10`. The anchor theorem here is the exact
two-input cell law. The ordered balanced all-arity fold and its charged DAG
ledger remain manuscript-level unless separately cited.

## Replay

```text
research/tournaments/2026-08-13-program-vector-optimization/lanes/formal_manuscript_repairs/check.sh
```

The checker compiles with warnings as errors, prints axioms for the named
declarations, rejects proof placeholders, user axiom declarations, unsafe
declarations, and native-evaluator proofs in the new source.

Source hashes:

```text
ManuscriptRepairs.lean  4b082559f9bdcea0dc8518992c9c9a87960f2a33a289a0d3cf7ad55347b3ced7
AxiomAudit.lean         1a358591415c181d8c68b109c50166cc1e14543d3c764a8747ca62a622a9e4f4
check.sh                a38c6f8fabb04bca4d5297b841c6dcfb91ecee5ef8f82e557bf2c51afa506328
```

## Nonclaims

This lane does not formalize the full ordered balanced anchor DAG, the local
and prefix table compiler, the binary residual-first compiler, the global
size/depth substitution theorem, program-vector lower bound, novelty, patents,
FTO, license rights, or practical performance.

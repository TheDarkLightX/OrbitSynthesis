# Lean checkpoint: exact strong-router program vectors

Date: 2026-08-13

Verdict: **PASS for the exact address-only projection-program formula.**  The
new lane imports the frozen `StrongSignedRouter` definitions through a
source-hash-checked, lane-local build artifact.  Lean checks the new file at
trust level zero with warnings treated as errors, and the strict declaration
and proof-placeholder scan is clean.

## Exact statement proved

For a target ternary word `t` and a base-branch word `p` of the same length,
the file defines a two-bit summary

```text
(E(t,p), G(t,p)).
```

Lean proves:

```text
E(t,p) = 1  iff  t = p,
G(t,p) = 1  iff  the first mismatch has t digit middle and p digit right.
```

Following `p` through the frozen recursive mode program therefore produces
exactly one of the following base modes:

```text
E = 1                  -> project
E = 0 and G = 1        -> constant 1
E = 0 and G = 0        -> constant 0.
```

These are the theorems `descendMode_project_iff`, `descendMode_one_iff`, and
`descendMode_zero_iff`.  The auxiliary theorem `addressSummary_disjoint`
checks that equality and a first mismatch cannot both occur.

## Sign and control bits

Let `N` be the Boolean indicator that the selected base router has negative
sign.  `descendSign_eq_signXor` proves the exact rule

```text
base sign = root sign xor parity(number of middle digits in p).
```

This `xor` is an address-program calculation, not a term constructor.  The
imported discriminator grammar is unchanged and still has no free NOT node.

For the frozen slot ordering `(first, second)`, Lean proves:

```text
first  = (!E) && (G == N)
second = (N && E) || ((!E) && G).
```

`projection_program_first` and `projection_program_second` prove the two
coordinates separately.  `projection_program_pair` proves their ordered-pair
equality simultaneously for every length, root sign, target, and branch word.
The proof reduces the recursive lookup to `baseProgram` itself, rather than
restating an independent truth table as an assumption.

## Composable segment summary

For consecutive segments `A` and `B`, the checked composition law is

```text
E_AB = E_A && E_B,
G_AB = G_A || (E_A && G_B).
```

Lean proves left and right identity and associativity for this operation.
`summarizePairs_append` then proves the exact concatenation theorem for aligned
digit-pair lists.  `addressSummary_eq_summarizePairs` binds that list-level
summary back to the typed router addresses.  Associativity justifies balanced
parenthesization of summaries; it does not by itself establish a charged
balanced decoder circuit.

## Import and acceptance boundary

The frozen source is outside the package's normal `formal/` module root.  The
lane therefore uses this reproducible bridge:

1. verify the frozen source SHA-256;
2. compile that exact source to `StrongSignedRouter.olean` inside this lane;
3. place only this lane on `LEAN_PATH`; and
4. compile `ProgramVector.lean` and its output with Lean trust level zero.

The checker command is:

```text
research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/check.sh
```

It returned exit code zero and printed only:

```text
No proof placeholders found.
```

Two consecutive runs regenerated identical build-artifact hashes.  The source
of truth remains the two Lean source files; the generated `.olean` files are
recorded only to make the import bridge and its deterministic replay visible.

## Evidence hashes

```text
ProgramVector.lean
  c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd
check.sh
  73f61cfd038ea9269766bfa9336da42ce3ccc318a46f6cddfcfa07fcce9ff67a
StrongSignedRouter.olean
  18830428c6e488e61c490b0ee38e297efc2c2829c91e9a03043f10ebbe9f2c16
ProgramVector.olean
  880d7eda2d4bd787fa0d13eb7703fc69217ae1f15f302f2a18095a97803ab429
tool_receipt.json
  15ee954c97e494012795be9743503f82d1b0923e0563ebf6b46f16592c93fab1
receipt.json
  5e79e4eb49af361fbed1c8962a67583a48e532526698da584b8825d55136cffa
frozen StrongSignedRouter.lean
  687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a
```

The receipt also records unchanged hashes for the frozen formal report,
formal receipts, fused summary, R27 witness, fused report, and tournament
state.

## Scope boundary

This checkpoint does **not** formalize or claim:

- `O(q)` materialization of all program bits;
- a shared circuit realizing a balanced segment evaluation with charged size
  and depth;
- an `r+O(log r)` compiler or any other asymptotic compiler theorem;
- the Q two-plane encoder/decoder bridge;
- extraction equality with generated witness JSON;
- novelty, patent/FTO, license, or performance conclusions.

The result is a precise control-vector theorem and an associative semantic
summary.  Any later compiler theorem must still provide and charge a concrete
shared implementation of these Boolean functions.

# Lean checkpoint: balanced program-vector cost

Date: 2026-08-13

Verdict: **PASS at the requested combinatorial/cost scope.**  Lean checks the
balanced E/G recurrence, the complete shared-DAG node ledger, the logarithmic
depth ledger, and the nonbinary `A=2` original-signature primitives.  No
requested theorem remains open.

## Main theorem

For either router root sign and every width `w>=1`, the theorem
`balanced_materialization_bounds` proves

```text
totalSharedDAGNodes(root,w) <= 7*3^w,
vectorDepth(w) <= 6+2*Nat.clog(2,w).
```

For positive `w`, `Nat.clog(2,w)` is the natural-number ceiling of
`log_2(w)`.  Unlike the earlier informal ledger, the first inequality here
charges the two shared name nodes `u(A)` and `u(u(A))` inside the displayed
`7*3^w` bound.  At width zero, Lean separately checks depth two and the same
size inequality.

## Balanced recurrence

Let `S(w)` count all E/G-state nodes beyond the two shared names.  The checked
definition and recurrence are

```text
S(0) = 0,
S(1) = 5,
S(w) = S(floor(w/2)) + S(ceil(w/2)) + 3*3^w   for w>=2.
```

The two child vectors occur once each.  Every one of the `3^w` concatenated
physical words adds exactly three composition nodes:

```text
E = E_A and E_B,
guarded_G_B = E_A and G_B,
G = G_A or guarded_G_B.
```

`half_width_sum` and `ternary_cross_product` prove that the two child output
sets have product exactly `3^w`.  `stateNodes_le_five_mul_pow` proves

```text
S(w) <= 5*3^w.
```

Widths 0 through 3 are discharged exactly.  For `w>=4`, both halves are at
most `w-2`; monotonicity of powers then leaves enough slack to close the
induction.

The final vector adds one active-OR node per physical word and a complement
node exactly at positive bottom cells.  Lean derives the even/odd
middle-parity counts and proves that either root sign needs at most

```text
(3^w+1)/2
```

such complements.  Adding the two name nodes yields the main `7*3^w` theorem.
This is a recurrence-level shared-DAG certificate: it specifies one copy of
each child vector and the newly allocated nodes at every merge.  It does not
serialize the result into a node-indexed graph or certify a particular
hash-cons implementation.

## Depth

The term-level lemmas prove:

```text
one-digit state depth <= 4,
one guarded composition adds <= 2 layers,
final pair formation adds <= 2 layers.
```

The balanced state recurrence is

```text
D(0)=0,
D(1)=4,
D(w)=max(D(floor(w/2)),D(ceil(w/2)))+2.
```

Using the exact `Nat.clog` recurrence, Lean proves

```text
D(w) <= 4+2*Nat.clog(2,w),
vectorDepth(w) <= 6+2*Nat.clog(2,w).
```

## Original-signature legality on `A=2`

`QTerm` has only these constructors:

```text
variable, unary u, ternary discriminator d.
```

There is no constant constructor.  Evaluation uses the exact three-element
operations

```text
d(x,y,z) = z if x=y, otherwise x,
u(0)=1, u(1)=0, u(2)=1.
```

Under the explicit premise `A=2`, Lean proves

```text
two  = A,
one  = u(A),
zero = u(u(A)),

delta_0(x) = u(d(x,two,one)),
delta_1(x) = d(x,two,zero),
delta_2(x) = u(d(x,zero,one)),

x and y = d(x,one,y),
x or y  = d(x,zero,y),
not x   = u(x)
```

for Boolean intermediate values.  The digit-state terms realize the imported
one-digit E/G summaries; `composeTerms_correct` realizes the guarded segment
composition; and `finalPairTerms_match_frozen_program` proves that the final
two Q-valued outputs equal the exact frozen Boolean program slots.

All digit, composition, and final-pair terms carry the structural
original-signature certificate.  This legality theorem is intentionally only
for the nonbinary `A=2` slice.  It does not reuse absolute constants on the
binary branch.

## Falsifiers

Two load-bearing mutations are machine-checked:

- `unguarded_gain_counterexample` shows that replacing
  `G_A or (E_A and G_B)` by `G_A or G_B` lets a later gain override an earlier
  non-gain mismatch.
- `anchor_one_mutation` shows that at `A=1`, the two shared zero/one names swap;
  the `A=2` premise cannot be erased.

## Acceptance evidence

The lane checker verifies both frozen Lean source hashes, recompiles them into
this new lane, checks every file with trust level zero and warnings treated as
errors, and runs the strict proof-placeholder/declaration scan:

```text
research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/check.sh
```

It returned exit code zero and printed only:

```text
No proof placeholders found.
```

Repeated replays regenerated identical `.olean` hashes.

```text
ProgramVectorCost.lean
  ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2
check.sh
  df1b7fdf0fcb73df331efd85cd94520a19ae70293b7cdef1a967d9adf296e928
StrongSignedRouter.olean
  18830428c6e488e61c490b0ee38e297efc2c2829c91e9a03043f10ebbe9f2c16
ProgramVector.olean
  880d7eda2d4bd787fa0d13eb7703fc69217ae1f15f302f2a18095a97803ab429
ProgramVectorCost.olean
  608a350fa8953de19cfeb3364f00d3c849d76e8f888d004ec0928b4513fdf89c
tool_receipt.json
  721c3ba036f3743de24adad52730ad7844a6435592aaacf9d4d917d3282735ed
receipt.json
  4919835f32d8afdfc48f72979edf4ad4ef0b1f8b16271ed9858a60750d2b6211
```

The frozen `formal_program_vector` source, checker, receipts, report, and the
upstream strong-router source retain the hashes recorded in `receipt.json`.

## Scope boundary

This checkpoint does not prove:

- a serialized node-indexed DAG extraction or hash-cons implementation;
- the binary complement-relative construction;
- Q two-plane decoding, selector tables, padding, or final compiler glue;
- an end-to-end compiler theorem;
- `r+O(log r)` or another asymptotic compiler-depth statement;
- novelty, patent/FTO, license, or performance conclusions.

The new result is exactly the nonbinary balanced materialization and its local
cost certificate.  It may be used as a premise in a later compiler proof, but
is not itself that compiler proof.

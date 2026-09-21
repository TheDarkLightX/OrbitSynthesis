# Formal sharp-depth and census checkpoint

Date: 2026-08-13

## Verdict

**Sharp depth: PASS. Full `4q/3`, `4q/3+1` census: PARTIAL.**

For the exact sibling-shared size ledger from the frozen optimized lane, Lean
now proves the matched depth recurrence and the combined theorem

```text
3*S(root,w) <= 4*3^w + 15*3^ceil(w/2),
D(w) <= 3 + Nat.clog 2 w                     (w>=1).
```

The depth recurrence uses the same longer-left/shorter-right decomposition as
the exact BG/BGN construction: the one-digit original-signature library has
depth three, each balanced composition adds one parallel discriminator layer,
and the sign-specialized terminal merge adds no layer beyond that recurrence.

The all-width output census is not claimed complete in this lane.  The formal
checkpoint closes the following substantive components:

- a recursive ternary truth-table datatype for Boolean functions on target
  addresses;
- injectivity of truth-table evaluation, so structural equality is exactly
  extensional function equality;
- exact equality of `gainTable`, `badTable`, and `notBadTable` evaluation with
  the frozen `addressSummary` semantics;
- exact Boolean complementation of bad/not-bad tables;
- injectivity of the all-width bad family and all-width not-bad family;
- therefore each pure family has exactly `q=3^w` distinct structural and
  actual Boolean functions by `Finset.card_image_of_injective` and
  `card_address`;
- explicit witnesses separating bad/not-bad members from constant tables.

The remaining full-census obligations are explicit:

1. quotient the gain family by the trailing physical `{0,1}` equivalence and
   prove exactly `(q+1)/2` classes;
2. prove the only gain/not-bad cross-family equalities are the canonical
   sibling identities in the orientation induced by the chosen address order;
3. restrict those overlaps by signed middle parity and count
   `(q/3+1)/2` for P versus `(q/3-1)/2` for N;
4. apply inclusion-exclusion to the actual frozen first/second control
   function image.

Accordingly, this artifact does **not** certify the final `4q/3` or
`4q/3+1` formula.  Those counts remain supported by the independent informal
all-width proof and executable checks, not by this Lean checkpoint.

## Scope and nonclaims

- One fixed root sign; address-only scalar same-DAG/free-fanout construction.
- Depth is operation depth above raw anchor/address terminals.
- The arithmetic `S` ledger and semantic construction were frozen in the
  imported optimized lane; this file proves the sharp matched depth recurrence.
- No exact optimum, integrated compiler, formula/bounded-fanout transfer,
  novelty, patent, or FTO claim.
- No manuscript, manifest, or prior lane was edited.

## Replay

`check.sh` hash-binds the frozen formal dependency chain, compiles every
theorem module with explicit `LEAN_PATH`, compiles the new module under
`-EwarningAsError=true`, and scans for placeholders/custom axiom declarations.
`AxiomAudit.lean` prints dependency sets separately.

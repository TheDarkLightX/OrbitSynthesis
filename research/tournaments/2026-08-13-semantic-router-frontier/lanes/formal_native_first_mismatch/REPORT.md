# Native first-mismatch theorem layer

Date: 2026-08-13

Status: **UNDER TEST**. The three Lean sources contain no `sorry`, `admit`, or declared `axiom`, but this runtime does not contain the pinned Lean toolchain and GitHub-hosted runners have been blocked at startup by the repository account's Actions billing limit. No new result is labeled Lean-checked until `check.sh` produces a compiler receipt.

## Source layers

- `NativeFirstMismatch.lean`: the first-non-equal monoid, its exact discriminator encoding, whole-address semantics, and pairwise distinct native roots.
- `NativeModeBridge.lean`: legal one-digit `d/u` terms, one-node segment composition, fused positive/negative bottom cells, and the complete signed-tree induction for projection and constant modes.
- `NativeModeCost.lean`: balanced shared-DAG recurrences, mode-vector size and depth, and the complement-closed complete-router bound.

## Stated exact bounds

For width `w>=1` and `q=3^w`, the recurrence layer proves

```text
mode-vector size <= 17q/9,
mode-vector depth <= 3+ceil(log_2 w),
complement-closed complete router size <= 10q/3.
```

The separate paper argument and executable oracle strengthen the mode-vector lower bound to `q` operation nodes for `w>=2`, because all `q` outputs are pairwise distinct and every output depends on every target coordinate.

## Reproduction

Run `./check.sh` from this directory with the pinned repository toolchain. The script hash-checks the three frozen upstream sources, compiles all six Lean layers in dependency order, and rejects placeholders or new declared axioms in the native sources.

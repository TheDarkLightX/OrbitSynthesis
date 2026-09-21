# Abstraction note

The reusable idea is to replace unreachable Boolean flag combinations by their actual semantic states, derive the associative state product, and then search for an operation-preserving embedding into the algebra's native carrier.

Here the states are `equal`, `gain`, and `loss`. Encoding them as `2`, `1`, and `0` makes their first-non-equal product exactly `d(left,2,right)`.

This pattern should be reused for lexicographic summaries, earliest-witness summaries, and other finite-state folds before introducing additional control bits.

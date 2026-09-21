# Extension geometry of atomless-Boolean-algebra types

**Status:** DERIVED paper proof; finite exhaustive checks pending integration into the reference oracle; Lean pending.

The support representation of complete ABA types gives more than the total count. It gives the exact fibers of every coordinate-forgetting map.

## Setup

A complete k-type is represented by a nonempty support

`S subseteq {0,1}^k`

of nonzero Boolean minterm cells. Let `s=|S|`.

Suppose we add `r>=1` new variables. Each old k-cell has `2^r` refinements, one for every valuation of the new variables.

## Theorem: exact number of extensions

A complete k-type with support size `s` has exactly

`(2^(2^r) - 1)^s`

complete `(k+r)`-type extensions.

For one new variable (`r=1`), this is simply

`3^s`.

## Proof

Take one old coarse cell `c`.

- If `c` is zero in the k-type, every one of its `2^r` refined cells must remain zero.
- If `c` is nonzero, at least one of its `2^r` refinements must be nonzero. Every nonempty subset of the refinements is realizable in an atomless Boolean algebra by splitting the nonzero element represented by `c` into the requested finite number of nonzero pieces.

Therefore each nonzero old cell has

`2^(2^r)-1`

independent choices of refined support. There are `s` nonzero old cells, so the product rule gives

`(2^(2^r)-1)^s`.

## Corollary: the global type-count identity has an inner explanation

There are `binom(2^k,s)` k-types whose support has size `s`. Summing the extension fiber sizes over all nonempty supports gives

`|T_(k+r)| = sum_{s=1}^{2^k} binom(2^k,s) (2^(2^r)-1)^s`.

By the binomial theorem,

`= (1 + (2^(2^r)-1))^(2^k) - 1`

`= (2^(2^r))^(2^k) - 1`

`= 2^(2^(k+r)) - 1`.

This is a Noether-style explanation of why the double-exponential type-count formula composes correctly under extension: **each nonzero old region independently chooses a nonempty refined support**.

## Examples

### Restriction `T_2 -> T_1`

A 1-type with support size 1 (`x=0` or `x=1`) has `3` extensions to two variables.

The interior 1-type `0<x<1` has support size 2 and therefore `3^2=9` extensions.

Total:

`3 + 3 + 9 = 15 = |T_2|`.

### Restriction `T_3 -> T_2`

A 2-type support can have size `s=1,2,3,4`. Its extension fiber has size `3^s`. Hence

`sum_{s=1}^4 binom(4,s) 3^s = 4^4 - 1 = 255`.

## Synthesis relevance

The extension proposition in `ocLTL` is existential and model-theoretic for a general omega-categorical structure. In ABA, extension branching is completely explicit.

This suggests two implementation strategies to compare:

1. **explicit support refinement:** enumerate only the nonempty refinements of currently relevant cells;
2. **symbolic refinement:** keep the splitting choices compressed in a formula/BDD/ZDD and materialize witnesses only when required.

The fiber formula also supplies exact benchmark expectations. Any ABA type-extension implementation that returns a different number of complete extensions for a support of size `s` is wrong.

## Next questions

1. Can predecessor operations be expressed directly as transforms on families of supports without enumerating all extensions?
2. Which compressed family representation makes the independent-per-cell product structure explicit?
3. Can the extension map be factored as a tensor/product construction useful for symbolic synthesis?
4. How does the picture change when only the specification-generated algebra `B_Delta` is observed rather than the full type support?

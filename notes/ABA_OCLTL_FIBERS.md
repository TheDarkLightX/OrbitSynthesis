# Exact ocLTL compatibility fibers for atomless Boolean algebra

**Status:** DERIVED paper proof; exact enumeration checked independently in Python; Lean pending.

This note specializes the three-variable ocLTL picture `(m,x,y)` to the countable atomless Boolean algebra (ABA).

A complete ABA 3-type is a nonempty support on the 8 cells of `{0,1}^3`. The ocLTL compatibility information already exposes two projections before any specification predicates Delta are considered:

1. the complete 2-type of `(m,x)`;
2. the complete 1-type of `y`, which becomes successor memory.

Define

`p : T_3 -> T_2 x T_1`

by these projections.

## Theorem 1 — all 45 projection pairs are realizable

ABA has `|T_2|=15` and `|T_1|=3`, and every pair `(sigma,rho)` occurs as the projections of at least one 3-type. Hence

`|image(p)| = 15*3 = 45`.

### Inner reason

View the eight `(m,x,y)` cells as a `4 x 2` zero/nonzero matrix:

- the four rows are the `(m,x)` cells;
- the two columns are the `y=0` and `y=1` cells.

The `T_2` type says exactly which rows are nonzero. The `T_1` type says exactly which columns are nonzero. Given any nonempty chosen row set and nonempty chosen column set, one can choose a support matrix with no zero selected row or selected column, then realize that finite support by atomless splitting.

## Theorem 2 — exact fiber size

Suppose the `(m,x)` support has `r` nonzero rows and the `y` support has `c` nonzero columns. The fiber `p^{-1}(sigma,rho)` is the set of `r x c` binary matrices having no zero row and no zero column.

Its size is

`N(r,c) = sum_{j=0}^c (-1)^j * binom(c,j) * (2^(c-j)-1)^r`.

Equivalently by symmetry,

`N(r,c) = sum_{i=0}^r (-1)^i * binom(r,i) * (2^(r-i)-1)^c`.

This is simply inclusion-exclusion over forbidden empty columns or rows.

### For ocLTL, c is only 1 or 2

If `y=0` or `y=1`, then `c=1`, so

`N(r,1)=1`.

If `0<y<1`, then `c=2`, so each selected row has three nonempty refinement choices `{left}`, `{right}`, `{both}`, but we must exclude the all-left and all-right choices:

`N(r,2)=3^r-2`.

There are `binom(4,r)` `(m,x)` types with support size `r`. Therefore the complete fiber distribution is:

- fiber size `1`: `30` pairs from the two one-column y-types, plus `4` pairs with `r=1,c=2`, total **34**;
- fiber size `7 = 3^2-2`: **6** pairs;
- fiber size `25 = 3^3-2`: **4** pairs;
- fiber size `79 = 3^4-2`: **1** pair.

Check:

`34*1 + 6*7 + 4*25 + 1*79 = 255 = |T_3|`.

## Corollary 3 — exact information threshold for Delta

Let Delta be a family of `d` arbitrary parameter-free ABA data predicates on `(m,x,y)`. Consider the joint feature map

`q_Delta(tau) = ( tau|_(m,x), tau|_y, truth_Delta(tau) )`.

Inside a fixed projection fiber, the `d` predicate truth values can create at most `2^d` distinguishable signatures.

The largest projection fiber has size 79. Therefore:

- if `d <= 6`, `2^d <= 64 < 79`, so `q_Delta` **cannot** be injective on `T_3`; at least two complete types are necessarily merged;
- at least `ceil(log2 79)=7` predicate bits are necessary for injectivity.

Seven are also sufficient **in principle** when arbitrary ABA-definable predicates are allowed: ABA is omega-categorical with quantifier elimination, so every subset of the finite type space is definable. Assign a local 7-bit code to the types inside each projection fiber and let each predicate be the union of the types whose corresponding bit is 1.

Hence the exact minimum number of arbitrary definable Delta predicates needed to recover all complete `T_3` information **given the `(m,x)` and `y` projection types** is

`7`.

This is not a statement about formula size: the seven predicates constructed abstractly may be huge.

## Corollary 4 — Delta alone needs at least 8 generators for the full type algebra

Without the projection features, a family of `d` predicates yields at most `2^d` truth-vector atoms. Distinguishing all 255 complete 3-types therefore requires

`2^d >= 255`,

so `d >= 8`.

Because every subset of `T_3` is ABA-definable, eight arbitrary definable predicates suffice in principle. Thus the full Boolean algebra of parameter-free definable 3-ary ABA relations has minimum Boolean generating-set size 8.

## Why this matters

Asor's §5.2 says that full `T_3` enumeration is unavoidable in the worst case but can be avoided when the specification-generated algebra is coarser. This note quantifies the three-variable ABA case exactly:

- compatibility features alone reduce 255 complete types to 45 observable projection signatures;
- the unresolved information is highly nonuniform, with one fiber containing 79 types;
- six or fewer additional data predicates guarantee some merging;
- seven predicates are the exact information-theoretic threshold at which the compatibility-aware abstraction can become as fine as full `T_3`.

The next question is algorithmic: real specifications do not choose arbitrary enormous definable predicates. What syntactic classes of Boolean equations produce small fiber refinements, and can that be predicted before enumeration?

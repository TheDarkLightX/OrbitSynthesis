# The complete type space of the countable atomless Boolean algebra

**Status:** DERIVED paper proof; exact finite sanity checks implemented; not yet Lean-checked.

Let `ABA` denote the complete first-order theory of atomless Boolean algebras in the usual Boolean-algebra language. Let `T_k` denote the set of complete parameter-free k-types.

## Theorem

For every integer `k >= 0`,

`|T_k| = 2^(2^k) - 1`.

For `k=0`, this is `1`, as expected. For positive k:

- `|T_1| = 3`
- `|T_2| = 15`
- `|T_3| = 255`
- `|T_4| = 65535`

## Structural proof

### Step 1: the `2^k` Venn/minterm cells

For each bit-vector `a in {0,1}^k`, define the Boolean minterm

`C_a(x_1,...,x_k) = intersection_i x_i^(a_i)`

where `x_i^(1)=x_i` and `x_i^(0)=complement(x_i)`.

The `2^k` cells are pairwise disjoint and their join is `1`.

Every Boolean term in the variables is the join of exactly those cells on which its two-element-Boolean-algebra truth function is `1`. This is the minterm normal form / Boole normal form perspective.

### Step 2: a tuple gives a nonempty support

Given a tuple `b=(b_1,...,b_k)` in an atomless Boolean algebra, define

`Supp(b) = { a in {0,1}^k : C_a(b) != 0 }`.

Because the join of all cells is `1`, `Supp(b)` cannot be empty.

### Step 3: the support determines the quantifier-free type

Let `t(x)` be any Boolean term. Write `A_t` for the set of cells appearing in the minterm normal form of `t`. Since the cells are disjoint,

`t(b)=0  iff  A_t intersection Supp(b) = empty`.

Any atomic equality `t=u` is equivalent to `(t XOR u)=0`. Therefore the truth value of every atomic formula is determined by `Supp(b)`, and hence so is every quantifier-free formula.

### Step 4: quantifier elimination upgrades this to the complete type

The theory of atomless Boolean algebras has quantifier elimination. Hence two tuples with the same quantifier-free type have the same complete type. Thus `Supp(b)` determines `tp(b)`.

Conversely, if two supports differ, choose a cell `a` belonging to exactly one of them. The formula `C_a(x)=0` distinguishes the tuples. Therefore distinct nonempty supports give distinct complete types.

So complete k-types inject into, and are distinguished by, the nonempty subsets of the `2^k` cells.

### Step 5: every nonempty support is realizable

Take a nonempty set `S subseteq {0,1}^k` with `r=|S|`.

In an atomless Boolean algebra, `1` can be split into `r` pairwise disjoint nonzero pieces whose join is `1`: split nonzero elements recursively until there are `r` pieces.

Index those pieces by `a in S`, writing them `p_a`. Define

`x_i = join { p_a : a_i = 1 }`.

Then the minterm cell `C_a(x)` is exactly `p_a` for `a in S`, and `0` for `a notin S`. Hence the tuple has support exactly `S`.

Therefore complete types are in bijection with nonempty subsets of a `2^k`-element set, giving

`|T_k| = 2^(2^k) - 1`.

## Why this is useful for synthesis

This identifies the exact reason complete types explode for ABA. A k-type is not an opaque model-theoretic object: it is a **nonempty support pattern on the Boolean Venn cells**.

That means restriction maps between type spaces can be computed combinatorially. If a type on k variables has support `S`, then forgetting some variables maps each nonzero source cell to the corresponding coarser cell; a coarse cell is nonzero iff at least one of its refinements is nonzero.

For the three-variable ocLTL presentation `(m,x,y)`:

- `T_3` has 255 elements;
- restriction to `(m,x)` lands in the 15 elements of `T_2`;
- restriction to `y` lands in the 3 elements of `T_1`.

No general-purpose model search is needed to compute those maps.

## Corollary: number of parameter-free definable relations

Because ABA is omega-categorical, every complete k-type is isolated and every subset of the finite type set is definable. Therefore the number of parameter-free definable k-ary relations up to theory equivalence is

`2^|T_k| = 2^(2^(2^k)-1)`.

This is a triple-exponential count in k. It also gives the exact height bound relevant to monotone fixed-point iteration: a strictly increasing chain of definable k-ary relations can have at most `|T_k|` strict inclusions.

## Noether-style reading

The theorem is not best understood as a cardinality trick. Its inner mechanism is:

`tuple -> generated finite Boolean subalgebra -> its Venn cells -> zero/nonzero support`.

The support is the invariant. Quantifier elimination says there is no hidden first-order information beyond it.

## Formalization plan

The formal proof should be split into two layers:

1. **finite combinatorial layer:** nonempty subsets of `Fin (2^k)` have cardinality `2^(2^k)-1`; restriction is projection of support patterns;
2. **model-theoretic layer:** prove/instantiate quantifier elimination for ABA and the realization of every finite support pattern.

Mathlib currently exposes first-order model-theory infrastructure and definable-set Boolean algebras, but this bootstrap has not established that ABA quantifier elimination is already formalized. Do not claim Lean verification until CI checks it.

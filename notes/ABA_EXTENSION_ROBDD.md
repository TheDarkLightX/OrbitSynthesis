# Exact ROBDD size of ABA extension relations

**Status:** DERIVED paper proofs; the one-variable construction is implemented and differentially checked; the multi-variable formula is a proved generalization pending direct code coverage; Lean/formal BDD proof pending.

## 1. One new Boolean-algebra variable

Let there be `n` coarse ABA minterm cells. When one new Boolean-algebra variable is introduced, use Boolean support variables

- `z_i` — coarse cell `i` is nonzero;
- `a_i` — its `y=0` refinement is nonzero;
- `b_i` — its `y=1` refinement is nonzero.

The exact atomless extension relation is

`Ext_n = AND_{i=1}^n [ z_i <-> (a_i OR b_i) ].`

Under the variable order

`z_1 < a_1 < b_1 < z_2 < a_2 < b_2 < ... < z_n < a_n < b_n`,

the reduced ordered BDD has exactly

`5n`

nonterminal nodes.

For `n=2^k`, this is exactly

`5*2^k`.

### Proof

For one local block

`h(z,a,b) := [z <-> (a OR b)]`,

- the `z=0` branch is `NOT a AND NOT b`;
- the `z=1` branch is `a OR b`.

The reduced BDD has one `z` node, two distinct `a` nodes, and two distinct `b` nodes: five in total.

Independent later blocks splice into the accepting terminals. Since their variables occur strictly later, none of the five leading nodes can merge with a tail node, and the five local nodes remain pairwise distinct. Hence the recurrence

`N(n)=N(n-1)+5`, `N(0)=0`,

gives `N(n)=5n`.

## 2. Add r BA variables at once

Now add a block of `r>=1` new Boolean-algebra variables at once.

Each coarse minterm cell has

`m=2^r`

fine refinements, one for each valuation of the new variables. Write their support bits as

`w_(i,1),...,w_(i,m)`.

The exact extension condition for one coarse cell is

`h_m(z,w_1,...,w_m) := [ z <-> (w_1 OR ... OR w_m) ].`

The whole extension relation over `n` coarse cells is

`Ext_(n,m) = AND_{i=1}^n h_m(z_i,w_(i,1),...,w_(i,m)).`

Use the block-local variable order

`z_1 < w_(1,1) < ... < w_(1,m) < z_2 < w_(2,1) < ...`.

### Theorem 1 — exact local ROBDD size

For `m>=1`, the ROBDD of

`z <-> OR_{j=1}^m w_j`

under order `z<w_1<...<w_m` has exactly

`1+2m`

nonterminal nodes.

### Proof

At the root:

- if `z=0`, the remaining function is `AND_j NOT w_j`;
- if `z=1`, the remaining function is `OR_j w_j`.

Each is a length-m decision chain under the given order.

The two chains share no nonterminal node:

- on the zero branch, every node sends `high` to rejection and continues on `low`;
- on the one branch, every node sends `high` to acceptance and continues on `low`.

At every level their child pairs differ; they therefore cannot merge in a reduced BDD. Together with the root this gives exactly `1+2m` nodes.

### Theorem 2 — exact multi-variable extension ROBDD size

For `n` coarse cells and `m=2^r` refinements per cell,

`ROBDDsize(Ext_(n,m)) = n(1+2m)`.

For `k` retained BA variables, `n=2^k`, hence

`ROBDDsize = 2^k (1+2^(r+1)).`

### Proof

Exactly as in the one-variable case, independent local blocks are placed consecutively in the variable order. Replacing each accepting terminal of one local block by the tail relation preserves all `1+2m` local nodes, and no local node can merge with a tail node because the tail's variables are later. Additivity over the n blocks gives the formula.

## 3. Compare with explicit extension branching

A complete k-type whose support has `s` nonzero coarse cells has

`(2^(2^r)-1)^s`

complete extensions after adding r BA variables.

For a maximally supported type, `s=2^k`, so explicit branching is

`(2^(2^r)-1)^(2^k)`.

Yet the relation describing **all** such extensions for all coarse types has only

`2^k(1+2^(r+1))`

ROBDD nodes under the block order.

This is the central representation gap:

> extension enumeration is enormous, while extension compatibility factorizes into one local OR relation per coarse cell.

## 4. ocLTL product-structure corollary

Asor's three-variable presentation packs multiple streams and bounded lookback into a product structure. For ABA, if one packed element contains `d` original BA coordinates, then:

- the partial state `(m,x)` corresponds to `2d` BA variables and has `2^(2d)` support coordinates;
- the full state `(m,x,y)` corresponds to `3d` BA variables and has `2^(3d)` support coordinates;
- passing from the partial to the full state adds `r=d` BA coordinates at once.

Therefore the exact support restriction/extension relation has ROBDD size

`2^(2d) * (1 + 2^(d+1)).`

Asymptotically this is less than

`3 * 2^(3d)`

for every `d>=1`, i.e. linear in the number `2^(3d)` of fine support coordinates.

By contrast, explicit complete full-state types number

`2^(2^(3d)) - 1`.

Thus the compact-extension phenomenon survives the product-structure reduction; it is not a coincidence of the literal three-variable `d=1` example.

## 5. Interpreted constants

If a finite interpreted-constant set C induces `rho(C)` nonzero constant regions, every region carries an independent copy of the same variable-minterm refinement geometry.

For k retained and r added BA variables, the extension relation therefore has exact block-local ROBDD size

`rho(C) * 2^k * (1+2^(r+1))`

when only the extension relation is represented.

The validity condition that every nonzero constant region has at least one active variable minterm is a separate constraint.

## 6. Minimum-width context

For pure ABA, a complete k-type needs at least

`ceil(log2(2^(2^k)-1)) = 2^k`

binary coordinates, and the Venn-support encoding uses exactly that many.

So for one-variable extension (`r=1`), the relation has exactly five ROBDD nodes per coordinate of a minimum-width type code.

For general r, the relation remains linear in the number of fine support coordinates:

`2^k(1+2^(r+1)) = 2^k + 2*2^(k+r)`.

The fine code itself has width `2^(k+r)`.

## 7. What these theorems do and do not say

They prove that the **structural relation introduced by ABA quantification / type extension** has a compact canonical BDD under a natural ordering.

They do **not** prove that:

- arbitrary translated formulas have small BDDs;
- repeated quantifier elimination cannot cause BDD blowup;
- this ordering is optimal for full Tau specifications;
- validity constraints or interpreted coefficients are always small;
- BDDs dominate Tau's current representation on runtime or memory.

Those remain experimental/theoretical questions.

## 8. Connection to symbolic model checking

Classical symbolic model checking represents state sets and relations as BDDs and computes fixed points symbolically instead of enumerating a state graph. The ABA support translation has the same operational primitives:

- Boolean conjunction/disjunction/negation;
- a compact transition/extension relation;
- existential abstraction;
- fixed-point equality.

Burch, Clarke, McMillan, Dill, and Hwang, *Symbolic model checking: 10^20 states and beyond*, LICS 1990, is the classical reference for this representation/fixed-point pattern.

The OrbitSynthesis question is whether the ABA support encoding has enough additional structure to make symbolic synthesis effective for Tau-style infinite-data specifications.

## 9. Reproducibility

`experiments/aba_support_bdd.py` currently:

- constructs the one-variable ROBDD from scratch;
- asserts the exact `5n` count for `n=1,2,4,8,16`;
- checks semantic identities such as `exists y. y=0`, existence of a nontrivial split, `exists y. y=x_0`, and an inconsistent pair;
- performs randomized formula comparisons for `k=1,2` against exhaustive enumeration of all ternary refinements of every nonzero coarse support.

Next code task: extend the reference implementation to add r variables at once and assert `n(1+2^(r+1))` on bounded `(k,r)` pairs.

# Exact ROBDD size of the ABA one-variable extension relation

**Status:** DERIVED paper proof; exact ROBDD construction checked for `2^k <= 16` coarse cells and used in randomized semantic differential tests; Lean/formal BDD proof pending.

Let there be `n` coarse ABA minterm cells. When one new Boolean-algebra variable is introduced, use Boolean support variables

- `z_i` — coarse cell `i` is nonzero;
- `a_i` — its `y=0` refinement is nonzero;
- `b_i` — its `y=1` refinement is nonzero.

The exact atomless extension relation is

`Ext_n = AND_{i=1}^n [ z_i <-> (a_i OR b_i) ].`

Consider the ROBDD variable order

`z_1 < a_1 < b_1 < z_2 < a_2 < b_2 < ... < z_n < a_n < b_n`.

## Theorem

The reduced ordered BDD for `Ext_n` has exactly

`5n`

nonterminal nodes.

For `n=2^k`, this is exactly

`5 * 2^k`.

## Proof

### One local block

For

`h(z,a,b) := [z <-> (a OR b)]`

under order `z<a<b`:

- if `z=0`, we require `a=0` and `b=0`, i.e. `NOT a AND NOT b`;
- if `z=1`, we require `a=1 OR b=1`.

The reduced BDD therefore consists of:

1. one `z` node;
2. two distinct `a` nodes, one for the `z=0` branch and one for the `z=1` branch;
3. two distinct `b` nodes, implementing `NOT b` and `b` respectively.

No pair can merge because either its variable or its ordered pair of children differs. Thus `h` has exactly five nonterminal nodes.

### Induction over independent blocks

Write

`Ext_n = h_1 AND Ext_{n-1}^{tail}`,

where every variable of `h_1` precedes every variable of the tail relation.

The ROBDD for `Ext_n` is obtained from the five-node local BDD of `h_1` by replacing every accepting terminal `1` with the root of the tail ROBDD. Rejecting terminal `0` remains `0`.

Because the tail function is neither constantly `0` nor constantly `1`, the five local nodes remain distinct and unreduced:

- their variables are the three new leading variables;
- the two `b_1` nodes have child pairs `(tail,0)` and `(0,tail)` up to the fixed low/high convention;
- the two `a_1` nodes have different descendants;
- the `z_1` node joins the two cases.

No new local node can merge with a tail node because all tail variables occur later in the ordering.

Hence, if `N(n)` denotes the number of nonterminal nodes,

`N(n)=N(n-1)+5`, with `N(0)=0`.

Therefore

`N(n)=5n`.

## Corollary for k retained BA variables

There are

`n=2^k`

coarse minterm cells, so the relation describing **all complete-type extensions by one new BA variable** has an ROBDD of exactly

`5*2^k`

nonterminal nodes.

Compare this with explicit enumeration:

- coarse complete types: `2^(2^k)-1`;
- fine complete types after adding one variable: `2^(2^(k+1))-1`;
- extension relation ROBDD: `5*2^k` nodes.

This is an exponential-size representation in the arity `k`, but exponentially smaller in the exponent than explicit type enumeration.

## What this theorem does and does not say

It proves that the **structural relation introduced by ABA quantification** has a compact canonical BDD under a natural ordering.

It does **not** prove that:

- arbitrary translated formulas have small BDDs;
- repeated quantifier elimination cannot cause BDD blowup;
- the same ordering is optimal for full Tau specifications;
- interpreted constants preserve this exact relation;
- BDDs dominate Tau's current representation on runtime or memory.

Those are experimental/theoretical questions.

## Connection to symbolic model checking

Classical symbolic model checking represents state sets and relations as BDDs and computes fixed points symbolically instead of enumerating a state graph. The ABA support translation has the same operational primitives:

- Boolean conjunction/disjunction/negation;
- a compact transition/extension relation;
- existential abstraction;
- fixed-point equality.

Burch, Clarke, McMillan, Dill, and Hwang, *Symbolic model checking: 10^20 states and beyond*, LICS 1990, is the classical reference for this representation/fixed-point pattern.

The new OrbitSynthesis question is whether the support-level ABA encoding has enough additional structure to make symbolic synthesis practical beyond the classical finite-state setting.

## Reproducibility

`experiments/aba_support_bdd.py`:

- constructs the ROBDD from scratch;
- asserts the exact `5n` count for `n=1,2,4,8,16`;
- checks several semantic identities (`exists y. y=0`, existence of a nontrivial split, `exists y. y=x_0`, and an impossible equation pair);
- performs 200 randomized formula comparisons for each of `k=1,2` against exhaustive enumeration of all `3^s` fine refinements of every nonzero coarse support.

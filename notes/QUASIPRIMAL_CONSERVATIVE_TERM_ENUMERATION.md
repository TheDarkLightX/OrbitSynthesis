# Exact enumeration and baseline compilation of conservative Q-terms

**Status:** manuscript theorem and baseline algorithmic bound with deterministic finite calibration. The proof is human-checkable but not Lean-checked or peer-reviewed. A separate Lupanov-style construction in `QUASIPRIMAL_CONSERVATIVE_TERM_SHANNON_COMPLEXITY.md` closes the shared-DAG order to `Theta(3^r/r)`. The universal-algebraic characterization and local-coding method are classical; publication novelty is **UNKNOWN**.

This note studies the parameter-free conservative fragment of the fixed algebra

`Q=({0,1,2};d,u)`,

where `d` is the ternary discriminator and `u(0)=1`, `u(1)=0`, `u(2)=1`. It sharpens `QUASIPRIMAL_ORBIT_SELECTOR_TERM_COMPILER.md` in two ways:

1. it counts the conservative `r`-ary term operations exactly; and
2. it removes unreachable classifier branches, reducing the simple low-depth compiler DAG from `O(r*3^r)` to `O(3^r)`.

## 1. Exact object

Let `CT_r(Q)` be the set of parameter-free `r`-ary `Q`-term operations `f` that are conservative:

`f(x_0,...,x_(r-1)) in {x_0,...,x_(r-1)}`

for every input tuple.

The qualifier “conservative” is essential. The basic operation `u` itself is not conservative because `u(2)=1`.

For `r>=2`, Pixley's classical internal-isomorphism characterization implies that a conservative function belongs to `CT_r(Q)` exactly when it commutes with complement on the binary subalgebra `B={0,1}`. Conservativity already preserves `B` and `Q`, nonbinary tuples generate `Q`, and the only nontrivial internal automorphism is complement on `B`.

For `r=1`, the sole conservative function is the identity projection, which is a term directly.

## 2. Exact count

### Theorem 1 — conservative term-operation count

For every `r>=1`,

`|CT_r(Q)| = 2^(5*2^(r-1)-5) * 3^(3^r-3*2^r+3)`.

### Binary tuples

The `2^r` binary tuples form `2^(r-1)` complement pairs.

- On the constant pair `{0^r,1^r}`, conservativity and equivariance force the output, so there is one choice.
- Every other pair contains both binary values. Choosing either value on one representative determines the complement value on its partner, so each of the remaining `2^(r-1)-1` pairs contributes two choices.

The binary factor is therefore

`2^(2^(r-1)-1)`.

### Nonbinary tuples with two distinct values

A nonbinary tuple using exactly `{0,2}` or exactly `{1,2}` has two conservative output choices. Each alphabet contributes `2^r-2` nonconstant tuples, for a total factor

`2^(2*(2^r-2))`.

The all-`2` tuple contributes one forced choice.

### Tuples using all three values

By inclusion-exclusion, the number of tuples using `0`, `1`, and `2` is

`3^r-3*2^r+3`.

Every such tuple has three conservative output choices. This contributes

`3^(3^r-3*2^r+3)`.

Multiplying the independent orbitwise choices and combining the powers of two gives Theorem 1.

For example,

- `|CT_1(Q)|=1`;
- `|CT_2(Q)|=32`; and
- `|CT_3(Q)|=23,887,872`.

## 3. Selector representation is complete for this fragment

Let `f in CT_r(Q)`. At every tuple `x`, choose an index `j(x)` with

`f(x)=x[j(x)]`.

On a binary complement pair, choose the index on one representative and reuse the same index on its complement. Equivariance guarantees that this index realizes the required output on both tuples. Nonbinary internal-isomorphism orbits are singletons.

Thus every conservative term operation has a complement-invariant coordinate-selector table. Conversely, every such selector compiles to a term by the explicit construction. The selector compiler is therefore complete for `CT_r(Q)`, not merely a source of examples.

## 4. Removing unreachable classifier branches

The compiler first finds the least coordinate `a` with `x_a=2`. Reaching that branch proves

- `x_0,...,x_(a-1)` are binary; and
- `x_(a+1),...,x_(r-1)` are unrestricted.

The earlier compiler nevertheless gave every earlier coordinate a third `2` branch. Those branches were unreachable.

The repaired classifier uses two branches before `a` and three branches after `a`. Its leaf count for anchor `a` is

`2^a*3^(r-a-1)`.

Summing over all possible first-`2` positions gives

`sum_(a=0)^(r-1) 2^a*3^(r-a-1) = 3^r-2^r`,

exactly the number of nonbinary tuples. No nonbinary classifier leaf is now wasted.

## 5. Constructive upper bounds

### Shared DAG

A binary decision creates three discriminator nodes; a ternary decision is two nested selectors and creates six. For anchor `a`, the earlier binary tree has `2^a-1` internal nodes, while its `2^a` leaves each carry a ternary tree with `(3^(r-a-1)-1)/2` internal nodes. Including the three dynamic `u` nodes for that anchor, the mixed classifier uses at most `3*2^a*3^(r-a-1)` distinct nodes.

Summing over anchors and accounting for reachable dynamic names, first-nonbinary tests, the binary-orbit classifier, and shared variables gives the exact emitted-DAG profile

`D_1=6`,

and, for `r>=2`,

`D_r=3*3^r-3*2^(r-1)+6r-4 < 4*3^r`.

Hence every operation in `CT_r(Q)` has a parameter-free term DAG with fewer than `4*3^r` total nodes. The formula counts this compiler's reachable syntax; it is not an exact minimum for each operation.

### Ordinary term tree

For the normal selector `N`,

`|N(x,y,a,b)| <= 11+|a|+2|b|`

when its equality-test terms have size at most three.

A ternary classification level obeys `T_t=29+7T_(t-1)`, while a binary level obeys `B_t=11+3B_(t-1)`. Solving the recurrences and summing the mixed classifiers over all anchor positions gives the exact expanded size of the emitted term:

`(35*7^r-9*3^r-50)/12`.

Thus ordinary syntax size is `O(7^r)`. The construction depth is exactly

`4r+1`.

If the explicit selector table has `M=3^r` rows, the DAG is `O(M)` and the emitted ordinary tree is

`O(M^(log_3(7)))`.

## 6. Information-theoretic lower bound

### Theorem 2 — worst-case DAG lower bound

Some operation in `CT_r(Q)` requires

`Omega(3^r/r)`

operation nodes in every original-signature term DAG.

### Counting proof

Theorem 1 gives

`log_2 |CT_r(Q)| = Theta(3^r)`.

Consider a topologically ordered term DAG with `s` operation nodes and `r` variable nodes. At operation position `i`, there are at most

`(r+i)+(r+i)^3`

choices for a unary-`u` or ternary-`d` node and its predecessors. Choosing the root adds at most `r+s` possibilities. Even after summing over all sizes up to `s`, the number of DAG descriptions is

`exp(O(s*log(r+s)))`.

If `s<3^r`, then `log(r+s)=O(r)`. Covering all `exp(Theta(3^r))` conservative term operations therefore requires `s=Omega(3^r/r)`. If `s>=3^r`, the claimed lower bound is immediate.

The count alone leaves an `O(r)` gap between this simple `O(3^r)` compiler and the information lower bound. That historical gap is now closed by the separate construction in `QUASIPRIMAL_CONSERVATIVE_TERM_SHANNON_COMPLEXITY.md`, which gives

`L_r(Q)=Theta(3^r/r)`

for operation-node shared-DAG complexity. The local-coded compiler has a substantially different depth profile and does not improve the ordinary-tree bound proved here.

## 7. Deterministic calibration

The checker is

`experiments/quasiprimal_conservative_term_count.py`.

It performs the following independent checks.

- It directly enumerates and compiles all `1` and `32` semantic conservative term operations at arities `1` and `2`.
- It directly classifies every tuple through arity `8` and matches all three closed-form category counts.
- It checks `|CT_3(Q)|=23,887,872`.
- It computes finite pigeonhole lower bounds by explicitly overcounting all topologically ordered term-DAG descriptions.
- It catches mutations that forget the binary complement quotient or give the all-`2` tuple spurious choices.

The optimized compiler campaign additionally compiles all `128` compatible arity-2 selector-index tables and checks every row of an arity-9 reduction table.

Normal and optimized Python executions of the count checker agree at semantic hash

`f7f1758972b68abd8aba60ae547cb899c5d9376cced7cba449c34a2697e001b8`.

These computations validate bounded instances and the implementation. They do not prove Theorems 1 or 2.

## 8. Prior-art and originality boundary

The following ingredients are not claimed as new:

- Pixley's characterization of quasi-primal term operations;
- conservative-function counting by independent tuple/orbit choices;
- discriminator decision trees; or
- information-theoretic circuit-counting lower bounds.

The potentially useful contribution is the exact conjunction for this reactive-synthesis fragment: a closed-form census, a transparent no-wasted-leaf low-depth compiler, and the separate order-optimal local-coded DAG compiler. Lupanov local coding itself is prior art and is not part of any originality claim.

Database and expert review are required before calling that conjunction novel.

## 9. Explicit nonclaims

Do not currently claim

- an optimal constant or exact minimum term size;
- an `Omega(3^r)` lower bound;
- a near-optimal ordinary term tree;
- an optimal leading DAG constant or a depth improvement from local coding;
- the same formula or compiler for every quasi-primal algebra;
- Lean verification;
- publication novelty; or
- patent freedom to operate.

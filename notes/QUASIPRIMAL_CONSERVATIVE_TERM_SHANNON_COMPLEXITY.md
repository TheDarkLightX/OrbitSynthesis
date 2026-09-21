# Shannon complexity of conservative terms over the fixed Quackenbush algebra

**Status:** manuscript theorem with an explicit parameter-free construction and deterministic bounded calibration. The upper bound is a specialization of the classical Lupanov local-coding principle, not a claimed new circuit-synthesis paradigm. The proof is not Lean-checked, independently reviewed, or publication-cleared. Novelty and patent/FTO status are **UNKNOWN**.

## 1. Object and size model

Fix

`Q=({0,1,2};d,u)`,

where `d(x,y,z)=z` when `x=y` and `d(x,y,z)=x` otherwise, while

`u(0)=1`, `u(1)=0`, and `u(2)=1`.

Let `CT_r(Q)` be the conservative parameter-free `r`-ary term operations of `Q`, as counted in `QUASIPRIMAL_CONSERVATIVE_TERM_ENUMERATION.md`.

A term DAG has `r` designated input nodes and operation nodes labelled by `u` or `d`; fan-out is free. Write `C_r(f)` for the minimum number of operation nodes in a rooted original-signature term DAG computing `f`, and define the Shannon function

`L_r(Q)=max_{f in CT_r(Q)} C_r(f)`.

The executable reports all distinct reachable nodes, including variables. This differs from `C_r` by at most `r` and therefore does not affect the asymptotic theorem.

## 2. Main result

### Theorem 1 — worst-case Shannon complexity

As `r` tends to infinity,

`L_r(Q)=Theta(3^r/r)`.

### Theorem 2 — Shannon effect at order level

There is a constant `c>0` such that the fraction of operations `f in CT_r(Q)` satisfying

`C_r(f) >= c*3^r/r`

tends to one. Since Theorem 1 supplies an `O(3^r/r)` upper bound for every member, a uniformly chosen conservative term operation has complexity `Theta(3^r/r)` with probability tending to one.

Neither theorem identifies an optimal leading constant.

## 3. Counting lower bound

The exact census is

`|CT_r(Q)| = 2^(5*2^(r-1)-5) * 3^(3^r-3*2^r+3)`,

so

`log |CT_r(Q)| = (log 3)*3^r + O(2^r)`.

Consider a topologically ordered DAG with `s` operation nodes. At operation position `i`, a unary node and its predecessor have at most `r+i` descriptions, while a ternary node and its ordered predecessors have at most `(r+i)^3`. Choosing a root and summing over sizes at most `s` changes only the constant in

`exp(O(s*log(r+s)))`.

For `s=c*3^r/r`, this is `exp(O(c*3^r))`. Choosing a sufficiently small fixed `c` leaves exponentially fewer descriptions than the `exp((log 3+o(1))*3^r)` semantic operations in `CT_r(Q)`. Therefore some operation needs `Omega(3^r/r)` nodes, and the proportion describable below that threshold tends to zero. This proves the lower halves of Theorems 1 and 2.

The count alone does not supply the matching compiler.

## 4. Mixed-domain local-coding lemma

The upper bound uses the following circuit lemma.

### Lemma 3 — local coding over binary/ternary rectangles

Let

`D=A_1 x ... x A_n`,

where every `|A_i|` is `2` or `3`, and put `N=|D|`. Suppose the circuit language has constants `0,1,2` and a constant-size conditional selector. Then every table `F:D->Q` has a shared circuit of size

`O(N/n)`.

The constants in the `O` bound are uniform over the mixture of binary and ternary coordinates. Small `n` can be absorbed into the constant.

### Proof construction

For large `n`, set

`H=floor(log_3(N/n))`.

Because `N>=2^n`, one has `H=Theta(n)`. Choose a block of coordinates whose number of assignments

`M=product_(i in block) |A_i|`

is maximal subject to `M<=H`. The unused-coordinate factor is at most three, so maximality gives `M>H/3`; hence `M=Theta(n)`. Also

`3^M <= 3^H <= N/n`.

There are only `O(log M)` block coordinates. Precompute the equality tests and the Boolean point indicators `chi_y` for all `M` block assignments `y`. This costs `O(M log M)` nodes.

Now enumerate all `3^M` functions from the block assignments to `Q` along a reflected ternary Gray path. Start with the constant-zero function. Consecutive truth tables differ at one block point `y`; if the new value there is `c`, update the previous circuit `g` by

`if chi_y=1 then c else g`.

One constant-size selector therefore creates the next library member. The entire shared library costs `O(3^M)=O(N/n)` nodes.

Finally, classify the assignments to the nonblock coordinates. There are `N/M=O(N/n)` prefix assignments, and each leaf points to the already shared library circuit for the required block subfunction. The mixed binary/ternary decision tree has `O(N/M)` nodes. The indicator overhead is also `O(N/n)` because `N>=2^n`. Summing the three costs proves the lemma.

This is a Lupanov-style local-coding argument. The ternary Gray library is the concrete specialization used here; the general local-coding principle is classical.

## 5. Parameter-free compilation in `Q`

The obstacle to applying Lemma 3 directly is that the original signature has no named constants. The compiler obtains them only on a branch where an input is known to be `2`.

Partition all nonbinary tuples by their first `2`. On the slice with anchor position `a`,

`x_0,...,x_(a-1) in {0,1}`, `x_a=2`,

and the later coordinates are unrestricted. The slice has

`N_a=2^a*3^(r-a-1)`

rows and `n=r-1` free coordinates. On this branch,

- `u(u(x_a))=0`;
- `u(x_a)=1`; and
- `x_a=2`.

These are dynamic branch-local names, not global constant terms. The normal conditional selector is expressible with three discriminator nodes. Lemma 3 therefore compiles an arbitrary `Q`-valued table on this slice using `O(N_a/r)` operation nodes.

The slices partition the nonbinary tuples and satisfy

`sum_(a=0)^(r-1) N_a = 3^r-2^r`.

Their total cost is `O(3^r/r)`. The all-binary branch is compiled by complement-orbit classification in `O(2^r)` nodes, and the first-`2` dispatcher costs `O(r)`. Both are `o(3^r/r)`. This proves the upper half of Theorem 1.

Every conservative `Q`-term operation has a complement-invariant coordinate-selector table, but the slice compiler is stronger than needed: after the anchor supplies the three values, it can realize an arbitrary `Q`-valued slice table.

## 6. Executable construction and finite evidence

The bounded materialization is implemented in

- `src/orbitsynthesis/orbit_term_compile_local.py`; and
- `experiments/quasiprimal_local_coding_compiler.py`.

The checker:

- validates reflected ternary Gray paths of lengths zero through four;
- compiles and evaluates all `128` compatible arity-two selector-index tables;
- evaluates fixed-seed tables through arity seven;
- checks the slice-partition and asymptotic plan inequalities through arity `64` without materializing the large circuits;
- evaluates all `19,683` rows of the arity-nine reduction selector; and
- rejects corrupted-Gray-path, complement-asymmetry, and invalid-cap mutations.

For the arity-nine reduction selector, the simple classifier has `58,331` distinct DAG nodes. The bounded Gray-scheduled local-coding compiler uses `19,329`, saving `39,002` nodes (`66.86%`). Its depth is `179`, compared with `37` for the simple classifier.

That depth is not inherent. `QUASIPRIMAL_CONSERVATIVE_TERM_LINEAR_DEPTH.md` first replaced the Hamiltonian Gray dependency chain by a zero-reusing layered prefix library. `QUASIPRIMAL_CONSERVATIVE_TERM_SUBCUBE_DEPTH.md` recursively indexes the library by block coordinates and proves the explicit operation-depth bound `4r` without changing the `O(3^r/r)` size order; on the same bounded selector it uses `18,135` nodes at executable depth `37`. `QUASIPRIMAL_CONSERVATIVE_TERM_GLOBAL_ANCHOR_DEPTH.md` then replaces the first-`2` dispatcher by one balanced absorbing anchor and a branch-depth-three router, improving the asymptotic upper bound to `3r+3*ceil(log_2 r)+4` while remaining larger on that arity-nine calibration.

Normal and optimized Python executions agree at semantic hash

`4aaf27d678847aa0455ae8be552a165c3e9ec08c007031878f6aa40b0794ed89`.

These executions validate the implementation and finite arithmetic. They do not prove the asymptotic theorem.

## 7. Prior-art and originality boundary

The following are established prior art and are not claimed here:

- Lupanov's local-coding principle and asymptotically efficient circuit synthesis;
- the general theory of functional constructions in `k`-valued logic;
- Shannon functions for functionally complete finite-valued bases;
- ternary/reflected Gray codes;
- discriminator decision trees; and
- circuit-description counting lower bounds.

The located multivalued Shannon literature includes V. A. Orlov's 2004 analysis of functionally complete `k`-valued bases. The present basis is not functionally complete without parameters because every term preserves the binary subalgebra `{0,1}`. Thus that abstract does not directly state Theorem 1, but the classical literature is close enough that this theorem may be a specialization or an expected corollary. A full-text Russian/international review is required before any novelty claim.

Public Chinese-index searches on 2026-08-13 located multivalued-logic circuit implementations and multivalued temporal-logic model checking, but no direct result for this fixed clone, its conservative fragment, or the `Theta(3^r/r)` Shannon function. This is weak negative evidence only: native CNKI/Wanfang coverage, translation variance, and expert review remain missing.

The strongest paper-safe framing at present is:

> a classical local-coding method closes the order-level compiler gap for a newly isolated reactive fixed-clone fragment; any originality must come from the exact fragment/semantics/construction conjunction, not from local coding itself.

## 8. Explicit nonclaims and next gates

Do not currently claim

- an optimal leading constant or exact minimum DAG size;
- an ordinary-term-tree bound or an optimal linear-depth constant;
- the same theorem for every quasi-primal algebra;
- novelty over Russian, Chinese, or international closed-class complexity literature;
- Lean verification or peer review;
- a result derived from Tau private materials or an unsigned Tau license; or
- patent freedom to operate.

The Boolean-R9 construction has since narrowed the depth-coefficient interval to `[1,3/2]`. The highest-leverage continuations are an exact leading-size-constant audit, closing that narrower interval, an ordinary-tree complexity bound, and a classification of which fixed finite clones admit the same local-coding closure.

# Linear-depth, order-optimal DAGs for conservative terms over fixed Q

**Status:** manuscript theorem with an explicit parameter-free compiler and deterministic bounded calibration. This layered construction removed the Gray dependency chain; `QUASIPRIMAL_CONSERVATIVE_TERM_SUBCUBE_DEPTH.md` sharpened it to `depth<=4r`, and `QUASIPRIMAL_CONSERVATIVE_TERM_GLOBAL_ANCHOR_DEPTH.md` now gives `depth<=3r+3*ceil(log_2 r)+4`. Lupanov local coding and finite-basis Shannon-depth theory are classical; novelty of this fixed-clone simultaneous specialization is **UNKNOWN**. The proof is not Lean-checked, independently reviewed, or publication-cleared.

## 1. Complexity measures

Fix the Quackenbush algebra

`Q=({0,1,2};d,u)`

and its conservative parameter-free `r`-ary term operations `CT_r(Q)`.

For `f in CT_r(Q)`, let

- `C_r(f)` be its minimum operation-node count over original-signature term DAGs; and
- `D_r(f)` be its minimum operation depth, with variables at depth zero.

The executable depth counter puts variables at depth one, an additive convention difference only. Define the worst-case depth function

`Delta_r(Q)=max_{f in CT_r(Q)} D_r(f)`.

## 2. Main results

### Theorem 1 — simultaneous size and depth

Every `f in CT_r(Q)` has one parameter-free original-signature term DAG satisfying both

`size = O(3^r/r)`

and

`depth = O(r)`.

Thus the order-optimal Shannon-size compiler need not pay the exponential depth of the first Gray-scheduled implementation.

### Theorem 2 — worst-case depth order

`Delta_r(Q)=Theta(r)`.

More sharply, for a uniformly chosen `f in CT_r(Q)`,

`D_r(f) >= r-log_3(log r)-O(1)`

with probability tending to one.

The result does not identify the optimal leading depth constant.

## 3. Why the Gray depth is avoidable

On one first-`2` anchor slice, let

`y_1,...,y_M`

be the assignments to the selected local-code block, and let `chi_j` be their pairwise-disjoint Boolean point indicators. The preceding compiler enumerated the `3^M` truth vectors along one ternary Gray path. Every new library root depended on its predecessor, creating `3^M-1` selector dependency edges and depth `Theta(3^M)`.

The number of selectors was good; only their dependency schedule was bad.

## 4. Layered prefix library

For each prefix word `w in Q^j`, build a term `g_w` with the invariant:

1. `g_w(y_i)=w_i` for `i<=j`; and
2. `g_w(y_i)=0` for `i>j`.

At level zero, `g_empty=0`. Given `g_w` at level `j`, define its three extensions at point `y_(j+1)`:

- `g_(w0)=g_w`;
- `g_(w1)=if chi_(j+1)=1 then 1 else g_w`;
- `g_(w2)=if chi_(j+1)=1 then 2 else g_w`.

Pairwise disjointness of the indicators proves the invariant inductively. In particular, the zero extension is free because the parent is already zero on every unprocessed point.

There are `3^(j-1)` parents before level `j`, and each creates two selectors. Hence the exact selector census is

`2*sum_(j=0)^(M-1) 3^j = 3^M-1`,

exactly the same as the Gray path. The dependency depth, however, is only `M` selector levels. The normal selector expands to constant many discriminator nodes, so library depth is `O(M)`.

## 5. Simultaneous compiler proof

Use the same first-`2` partition as in `QUASIPRIMAL_CONSERVATIVE_TERM_SHANNON_COMPLEXITY.md`. Anchor slice `a` has

`N_a=2^a*3^(r-a-1)`

rows and supplies branch-local names for `0,1,2` through `u(u(x_a))`, `u(x_a)`, and `x_a`.

For the `n=r-1` free coordinates, choose a local-code block with `M=Theta(r)` assignments and

`3^M=O(N_a/r)`.

The layered library has `O(3^M)` nodes and depth `O(M)=O(r)`. The decision tree on the remaining coordinates has `O(N_a/M)=O(N_a/r)` nodes and depth `O(r)`. Point-indicator construction costs polynomially many nodes and depth `O(log r)` under the existing sequential conjunction, which is lower order here.

Summing over slices gives

`sum_a O(N_a/r)=O(3^r/r)`.

The all-binary complement-orbit classifier and the first-`2` dispatcher each have depth `O(r)` and lower-order size. Therefore the final composed DAG simultaneously has size `O(3^r/r)` and depth `O(r)`, proving Theorem 1.

## 6. Depth lower bound

Any depth-`h` term DAG can be recursively unshared into a term tree without increasing depth. Let `A_h(r)` overcount the number of original-signature term trees of operation depth at most `h` on `r` variables. Then

`A_0(r)=r`

and, for `r>=2`,

`A_(h+1)(r) <= r+A_h(r)+A_h(r)^3 <= 3*A_h(r)^3`.

Consequently,

`log A_h(r) <= 3^h*(log r+(log 3)/2)`.

The exact conservative-term census gives

`log |CT_r(Q)|=(log 3)*3^r+O(2^r)`.

If

`h <= r-log_3(log r)-K`

for a sufficiently large fixed `K`, then `A_h(r)/|CT_r(Q)|` tends to zero exponentially in `3^r`. Thus almost every conservative operation has depth at least the stated threshold, and in particular `Delta_r(Q)=Omega(r)`. Theorem 1 supplies the matching `O(r)` upper bound.

This argument counts semantic candidates by syntactic depth; it does not assume a size bound.

## 7. Bounded evidence

The implementation exposes `library_schedule="gray"` and `library_schedule="layered"` in

`src/orbitsynthesis/orbit_term_compile_local.py`.

The checker

`experiments/quasiprimal_layered_local_coding_compiler.py`

performs:

- the exact selector-census recurrence through `M=8`;
- the logarithmic shallow-term count against the exact semantic census through arity `64`;
- exhaustive evaluation of all `128` compatible arity-two selector tables;
- fixed-seed evaluation through arity seven;
- full evaluation of all `19,683` arity-nine reduction rows;
- normal/optimized replay comparison; and
- invalid-schedule, wrong-selector-recurrence, and dropped-`log log r` mutation controls.

On the arity-nine reduction selector:

| schedule | distinct DAG nodes | reported depth |
|---|---:|---:|
| Gray | 19,329 | 179 |
| layered | 18,327 | 45 |
| recursive subcube | 18,135 | 37 |

The layered schedule saves `1,002` reachable nodes because unused library branches are no longer forced reachable through one Hamiltonian chain. It saves `134` depth levels. The later recursive-subcube schedule saves another `192` nodes and `8` levels on this target. These are bounded implementation facts, not proofs of the generic theorems.

Normal and optimized executions agree at semantic hash

`b42fa56c1e78e670e2a436181337957309a0b2a658b6f539486b85cedc482d54`.

## 8. Prior-art and exact-constant boundary

Lupanov's local-coding principle is established prior art. Kochergin proves linear Shannon-depth behavior for `k`-valued functions over arbitrary complete finite bases. Orlov studies basis-sensitive coefficients for circuit and formula Shannon functions in functionally complete `k`-valued bases and notes that coefficient determination is a separate algorithmic problem.

The parameter-free basis here is incomplete because every term preserves `{0,1}`. Its conservative fragment nevertheless has full ternary-table entropy to leading order. That makes the present result adjacent to, and possibly an expected specialization of, classical theory. The layered dependency schedule should not be advertised as novel until the full Russian and multivalued synthesis literature is reviewed.

The exact size-leading-constant lane is therefore paused, not solved. A credible continuation must first translate Orlov/Lupanov reduced-weight or automaton-basis coefficients to the anchored incomplete-clone model.

## 9. Explicit nonclaims

Do not currently claim

- an exact leading coefficient for size or depth;
- novelty of layered local coding;
- an improved ordinary unshared-term-tree bound;
- the same simultaneous theorem for every quasi-primal algebra;
- Lean verification, peer review, or publication novelty;
- reliance on Tau private materials or an unsigned Tau license; or
- patent freedom to operate.

The global-anchor router first lowered the explicit depth-coefficient interval to `[1,3]`; the later Boolean-R9 construction narrows it to `[1,3/2]`. The next mathematical targets are closing that interval, the exact size coefficient, and ordinary-tree complexity. Each requires a separate prior-art and proof campaign.

# Explicit depth four for order-optimal conservative Q-term DAGs

**Status:** manuscript sharpening with an explicit parameter-free compiler and deterministic bounded calibration. This `4r` construction remains the better bounded compiler at small tested arities, while `QUASIPRIMAL_CONSERVATIVE_TERM_GLOBAL_ANCHOR_DEPTH.md` now improves the asymptotic upper bound to `3r+O(log r)`. The proof is not Lean-checked or independently reviewed. Recursive Shannon expansion, Lupanov local coding, and linear Shannon depth over complete finite bases are prior art; novelty of this fixed incomplete-clone specialization is **UNKNOWN**.

## 1. Model and result

Fix the Quackenbush algebra

`Q=({0,1,2};d,u)`

and let `CT_r(Q)` be its conservative parameter-free `r`-ary term operations. Count only original-signature operation nodes, and put variables at operation depth zero.

### Theorem — one size-optimal DAG with explicit depth

Every `f in CT_r(Q)` has one parameter-free original-signature term DAG with

`size=O(3^r/r)`

and

`depth<=4r`.

Combining this construction with the exact semantic census and the existing depth count gives

`r-log_3(log r)-O(1) <= Delta_r(Q) <= 4r`,

where `Delta_r(Q)` is the worst-case minimum operation depth. The lower inequality holds for almost every uniformly chosen operation, not merely for one worst case.

The theorem does not assert that the coefficient `4` is optimal.

## 2. First-2 slices and the local block

Partition nonbinary tuples by their first coordinate `a` equal to `2`. On that slice,

- `u(u(x_a))` names `0` at depth two;
- `u(x_a)` names `1` at depth one; and
- `x_a` names `2` at depth zero.

The slice contains

`N_a=2^a*3^(r-a-1)`

tuples. Choose a local block of coordinates whose alphabet sizes are

`q_1,...,q_b in {2,3}`

and whose number of assignments is

`M=product_j q_j=Theta(r)`.

As in the preceding local-coding proof, choose it so that

`3^M=O(N_a/r)`.

The remaining prefix has `P=N_a/M` assignments.

## 3. Recursive subcube library

The layered library processes the `M` block points one at a time. The new library instead recurses over the `b=O(log r)` block coordinates.

Let

`M_j=product_(i=j)^b q_i`.

At the base, the three constant local functions are represented by the anchor-derived names of `0,1,2`. Suppose every function on the suffix beginning at coordinate `j+1` has been built. A function on the suffix beginning at `j` is uniquely a `q_j`-tuple of those suffix functions, one for each value of coordinate `j`. Combine that tuple with

- one normal selector when `q_j=2`; or
- two nested normal selectors when `q_j=3`.

This constructs all `3^(M_j)` functions on the current subcube. Concatenating the suffix truth vectors in coordinate-value order makes the indexing exact; it is not a sampled or heuristic library.

## 4. Library-size bound

The exact number of normal-selector calls made while materializing every recursive library level is

`S(q_1,...,q_b)=sum_(j=1)^b (q_j-1)*3^(M_j)`.

Since `M_(j+1)<=M_j/2`, the top level dominates. For every nonempty block,

`S(q_1,...,q_b)<3*3^M`.

Each normal selector expands to three discriminator nodes. Thus the complete local library has `O(3^M)` original-signature nodes.

A full mixed-radix prefix tree with `P` leaves makes exactly `P-1` normal-selector calls when each `q`-way node is weighted by `q-1`. Therefore one anchor slice costs

`O(3^M+P)=O(N_a/r)`.

Summing over all first-`2` slices and adding the lower-order all-binary classifier gives

`O((3^r-2^r)/r)+O(2^r)=O(3^r/r)`.

## 5. Exact depth accounting

The normal selector adds at most two operation-depth levels above its tests and branches. Hence a binary coordinate costs two levels and a ternary coordinate costs four levels in this explicit compiler.

The recursive library and the prefix tree partition all free coordinates. On anchor slice `a`, their combined depth is at most

`2 + 2a + 4(r-a-1)`.

The leading `2` is the maximum depth of the anchor-derived value names. Reaching slice `a` through the first-nonbinary dispatcher crosses `a+1` normal selectors and adds `2(a+1)` levels. The sum is exactly

`2+2a+4(r-a-1)+2(a+1)=4r`.

The all-binary branch has depth at most `4r-2`. Thus every root has operation depth at most `4r`.

The executable helper counts variables at depth one, so its corresponding bound is `4r+1`.

## 6. Deterministic evidence

The implementation adds `library_schedule="subcube"` to

`src/orbitsynthesis/orbit_term_compile_local.py`.

The checker

`experiments/quasiprimal_subcube_local_coding_compiler.py`

performs:

- exact recursive selector-census checks for representative mixed binary/ternary blocks;
- structural size and `4r+1` executable-depth arithmetic for every slice at arities `8,12,16,24,32,48,64`;
- exhaustive evaluation of all `128` compatible arity-two selector tables;
- fixed-seed evaluation through arity seven;
- full evaluation of all `19,683` arity-nine reduction rows;
- normal and optimized replay; and
- invalid-schedule, wrong-census, omitted-level, and sequential-depth mutation controls.

On the arity-nine reduction selector:

| schedule | distinct DAG nodes | executable depth |
|---|---:|---:|
| Gray | 19,329 | 179 |
| layered | 18,327 | 45 |
| recursive subcube | 18,135 | 37 |

The new schedule saves `192` nodes and `8` depth levels relative to the layered schedule on this bounded target. The depth equals `4*9+1`. These measurements validate the implementation, not the generic proof.

Normal and optimized executions agree at semantic hash

`f9d89ec9829c3abef05d1cdc17ef811330674bd056d90c3579a8f32b0b2eb7b8`.

## 7. Prior-art boundary

The following are established prior art and are not originality claims here:

- recursive Shannon expansion of truth tables;
- Lupanov local coding and asymptotically efficient circuit synthesis;
- linear Shannon depth for full `k`-valued function classes over complete finite bases;
- multivalued formula depth-versus-complexity parallelization; and
- simultaneous Boolean size/depth synthesis.

Kochergin's complete-basis result directly lowers the novelty of any generic linear-depth claim. Safin studies formula depth versus complexity inside precomplete multivalued classes, and Lozhkin gives simultaneous near-Shannon size/depth synthesis in the standard Boolean basis. Their public statements do not directly supply this parameter-free incomplete-basis compiler or its same-DAG `4r` accounting, but full-text comparison and expert review remain required.

Public Chinese-index searches again returned physical ternary-circuit and multivalued model-checking work, not this fixed-clone Shannon-depth statement. That is weak negative evidence only.

TheoremSearch did not contribute a retrieval result: local network calls failed, and an external query containing the unpublished theorem shape was rejected at the approval boundary and was not retried.

## 8. Explicit nonclaims

Do not currently claim

- that the coefficient `4` is optimal;
- novelty of recursive subcube enumeration or linear depth;
- an improved ordinary unshared-term-tree bound;
- the same coefficient for arbitrary quasi-primal algebras;
- Lean verification, peer review, or publication novelty;
- reliance on Tau private materials or an unsigned Tau license; or
- patent freedom to operate.

The global-anchor construction first lowered the explicit asymptotic interval to `[1,3]`; the later Boolean-R9 construction narrows it to `[1,3/2]`. The remaining question is whether higher-capacity or nonserial routing can beat that ceiling, or whether a basis-sensitive lower bound can raise the coefficient-one floor.

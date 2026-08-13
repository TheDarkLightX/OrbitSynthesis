# Global-anchor routing for order-optimal conservative Q-term DAGs

**Status:** manuscript sharpening with an explicit parameter-free compiler, exhaustive primitive checks, and a deterministic finite solver gate. The proof is not Lean-checked or independently reviewed. Multiplexer depth, recursive Shannon expansion, Lupanov local coding, and linear Shannon depth over finite bases are established prior art. Novelty of this fixed incomplete-clone specialization is **UNKNOWN**.

## 1. Result

Fix the Quackenbush algebra

`Q=({0,1,2};d,u)`,

where `d(x,y,z)=z` if `x=y` and `d(x,y,z)=x` otherwise, and

`u(0)=1`, `u(1)=0`, `u(2)=1`.

Let `CT_r(Q)` be its conservative parameter-free `r`-ary term operations. Operation depth puts variables at depth zero and counts only original-signature `d` and `u` nodes.

### Theorem — same Shannon-size DAG with depth coefficient three

Every `f in CT_r(Q)` has one parameter-free original-signature term DAG with

`size=O(3^r/r)`

and

`depth<=min(4r, 3r+3*ceil(log_2 r)+4)`.

Combining this construction with the exact semantic count and the preceding syntax-depth lower bound gives

`r-log_3(log r)-O(1) <= Delta_r(Q) <= 3r+O(log r)`,

where `Delta_r(Q)` is the worst-case minimum operation depth. The lower bound holds for almost every uniformly selected member of `CT_r(Q)`.

Thus the explicit asymptotic coefficient interval improves from `[1,4]` to `[1,3]`. This theorem does **not** assert that coefficient `3` is optimal.

## 2. A global nonbinary anchor

Define

`h(x,y)=d(x,u(u(x)),d(y,u(x),x))`.

### Lemma 1 — absorbing value two

For `x,y in Q`,

`h(x,y)=2` iff `x=2` or `y=2`;

otherwise `h(x,y)=x`.

If `x=2`, the outer discriminator returns `x=2` because `u(u(2))=0`. If `x` is binary, then `u(u(x))=x`, so the outer discriminator exposes `d(y,u(x),x)`. That inner term is `2` exactly when `y=2` and is `x` for both binary values of `y`.

Balanced-fold `h` over all input variables and call the result `A`. Then

- `A=2` exactly on tuples containing at least one `2`;
- `A=x_0` on all-binary tuples;
- the fold uses `O(r)` operation nodes; and
- `depth(A)<=3*ceil(log_2 r)`.

The last bound follows because an occurrence in the left child of `h` gains at most three operation levels and one in the right child gains at most two.

On the nonbinary branch, therefore,

`u(u(A))=0`, `u(A)=1`, and `A=2`.

These are branch-local dynamic names, not global constants. On the binary branch `A=x_0`; this is precisely what keeps the construction parameter-free and compatible with the preserved binary subalgebra.

The complete binary-function depth closure has sizes

`2, 4, 20, 270`

at operation depths at most `0,1,2,3`. The target semantics of `h` first occur at depth three, so this particular absorbing operation has minimum operation depth three.

## 3. A branch-depth-three ternary router

On a branch where terms named `0,1,2` have those values, define

```text
mux(x,b0,b1,b2)
 = d(
     d(0,d(x,2,b0),d(0,x,b0)),
     0,
     d(d(1,x,b1),1,d(x,2,b2))
   ).
```

### Lemma 2 — shallow routing

For all `x,b0,b1,b2 in Q`,

`mux(x,b0,b1,b2)=b_x`.

Every occurrence of every branch argument is exactly three discriminator nodes below the root. A direct three-case reduction proves the identity:

| selector | left root | right root | final output |
|---:|---|---|---|
| `0` | `b0` | `0` | `b0` |
| `1` | `0` | `b1` | `b1` |
| `2` | `0` | `b2` | `b2` |

With `0=u(u(A))`, `1=u(A)`, and `2=A`, the materialized router has operation depth five relative to an input anchor and fifteen distinct nodes including its five variables. Its routing cost, however, is three branch-dependency levels rather than the four levels used by two nested normal selectors.

### Finite optimality scope

An exact Z3 `QF_BV` search rules out branch depth at most two in the following deliberately generous grammar:

- all `27` unary functions of the selector are admitted as free terminals, so arbitrarily complicated selector-only subterms have already been collapsed;
- `b0,b1,b2` are the other terminals;
- internal nodes may be `u` or `d`;
- the complete ternary syntax tree has depth two and `13` grammar nodes; and
- all `81` valuations of `(x,b0,b1,b2)` are constrained simultaneously.

The result is `UNSAT`. Together with the displayed term, branch depth three is optimal for this branch-scoped selector-only routing model.

This is **not** a lower bound on arbitrary global `Q`-term depth, on other decompositions, or on the leading coefficient of `Delta_r(Q)`. The solver result is a finite, source-auditable gate and currently has no separately checked proof certificate.

## 4. One global local-coding library

Every conservative term operation can be represented by a compatible coordinate-selector table: at every input tuple choose an input coordinate carrying the output value, using the same coordinate for complementary all-binary tuples. It is therefore enough to compile such selector tables.

Set

`H=floor(log_3(3^r/r))`.

Choose `b` ternary coordinates so that their number of assignments

`M=3^b`

is maximal subject to `M<=H`. Apart from finitely many small arities,

`H/3<M<=H`,

so `M=Theta(r)`,

`3^M<=3^H<=3^r/r`,

and the remaining prefix has `3^r/M=O(3^r/r)` assignments.

Build every `Q`-valued function on the block recursively by block coordinate. At each level, combine three suffix functions with the router from Lemma 2. If `M_j` is the suffix-domain size at level `j`, that level creates `3^(M_j)` router roots. Since successive suffix sizes fall by a factor of three, the sum over levels is `O(3^M)`.

At each prefix node, use the same router to choose the required block function. The full prefix tree uses `O(3^r/M)` nodes. The global anchor adds `O(r)` nodes. Hence the nonbinary branch has size

`O(3^M+3^r/M+r)=O(3^r/r)`.

The complement-orbit classifier on the all-binary branch has size `O(2^r)`, which is lower order. A final normal selector compares `u(u(A))` with `A`: they agree on binary tuples and differ on nonbinary tuples. It therefore selects the binary classifier exactly on the binary cube and the global library everywhere else.

## 5. Exact depth accounting

The recursive block library and the prefix tree partition the `r` routed coordinates. Every routed coordinate contributes three branch-dependency levels. The deepest base name is `u(u(A))`, at depth

`3*ceil(log_2 r)+2`.

The nonbinary branch therefore has operation depth at most

`3r+3*ceil(log_2 r)+2`.

The outer normal selector adds two branch levels, giving

`3r+3*ceil(log_2 r)+4`.

The binary branch and the outer comparison inputs are no deeper than this bound. Taking the better of this construction and the preceding first-`2` recursive-subcube compiler proves

`depth<=min(4r,3r+3*ceil(log_2 r)+4)`.

The executable counter puts variables at depth one, so its structural bound is one larger.

## 6. Deterministic evidence

The implementation is in

`src/orbitsynthesis/orbit_term_compile_local.py`,

and the checker is

`experiments/quasiprimal_global_anchor_routing.py`.

The checker performs:

- complete binary-function depth closure through depth three for the absorber;
- all nine absorber input rows;
- all `81` router valuations;
- the Z3 branch-depth-two `UNSAT` search over all `81` valuations;
- balanced-anchor semantics for arities one through seven;
- all `128` compatible arity-two selector tables;
- fixed-seed full-table evaluation through arity seven;
- all `19,683` rows of the arity-nine reduction selector;
- structural depth arithmetic through arity `256`;
- constant-swap, wrong-absorber, incomplete-table, and binary-anchor scope controls; and
- normal and optimized replay.

Normal and optimized executions agree at semantic hash

`fb5ca7bf56d9aba9fdb0f69d1f1355c92d56d4f9306ee08a922bfc770ef60501`.

The global compiler is an asymptotic improvement, not a bounded arity-nine improvement:

| compiler | distinct DAG nodes | executable depth |
|---|---:|---:|
| first-`2` recursive subcube | 18,135 | 37 |
| global anchor | 23,807 | 41 |

The structural operation-depth bounds cross at arity `16`; the global bound improves on `4r` from arity `20` onward. At arities `32,64,128,256`, the proven arithmetic saves respectively `13,42,103,228` operation levels.

These finite measurements validate the implementation and arithmetic. They do not prove the generic compiler theorem or novelty.

## 7. Prior-art boundary

The following are not originality claims:

- recursive Shannon expansion and multiplexer decomposition;
- Lupanov local coding;
- linear Shannon depth over complete finite bases;
- depth/complexity parallelization in multivalued precomplete classes; or
- exact or asymptotic multiplexer-depth analysis in other bases.

Lozhkin's 2024 paper determines exact Boolean multiplexer formula depth in the standard basis over broad ranges. It does not use this incomplete parameter-free algebra, but it confirms that basis-sensitive multiplexer depth is a mature lane requiring direct comparison.

Chinese public-index review found Wu and Chen's 1985 ternary-circuit decomposition identity and Xu, Guan, and Zhang's 2013 ternary reversible-logic synthesis algorithm. Both use different algebras and cost models; neither public record supplies this `Q`-term router or coefficient-three compiler. This is weak negative evidence only, not novelty evidence.

Research Kernel retrieval and Morph reformulation supplied no direct prior-art match or proof. They remain discovery lanes, not promotion authority. TheoremSearch was not sent an unpublished theorem-shaped external query after the approval boundary rejected that operation.

## 8. Explicit nonclaims and next target

Do not currently claim

- that coefficient `3` is globally optimal;
- that the router identity is publication-novel;
- that Z3 proved a lower bound outside the stated finite grammar;
- an improved ordinary unshared-term-tree bound;
- the same coefficient for arbitrary quasi-primal algebras;
- Lean verification, independent review, or publication novelty;
- reliance on Tau private materials or an unsigned Tau license; or
- patent freedom to operate.

The next high-leverage mathematical target is to decide whether global coordinate routing can spend fewer than three branch levels amortized per coordinate, or instead to prove a basis-sensitive global lower bound above coefficient one. Any claimed improvement must preserve the `O(3^r/r)` size bound on the same DAG and survive direct Russian, international, and native Chinese prior-art review.

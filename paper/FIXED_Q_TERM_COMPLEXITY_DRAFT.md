# Exact Census and Simultaneous Shannon Size--Depth Bounds for Conservative Terms over a Fixed Three-Element Algebra

**Living manuscript draft — 2026-08-13**

**Status.** The statements below are manuscript theorems supported by human-checkable proofs and deterministic bounded checks. The recursive signed-router family and the exact parallel address-program vector have independent no-author-import audits and Lean proofs, including the latter's complete `7q` shared-DAG cost and logarithmic-depth ledger. The integrated `r+O(log r)` arithmetic has an independent conditional pass, but the all-arity compiler remains explicitly conditional on the named selector, anchor, representation, binary-branch, decoder, finite-fallback, and glue lemmas. The manuscript has not been peer reviewed or cleared by a complete prior-art search. Mathematical novelty and patent freedom to operate are **UNKNOWN**. The local-coding and Shannon-counting methods are classical and are credited accordingly.

**Authorship gate.** Creator names, order, affiliations, and ORCIDs have not yet
been fixed by the human collaborators. This working draft must not be deposited
as an archival preprint until that metadata is supplied and approved.

## Abstract

Fix the three-element algebra

`Q=({0,1,2};d,u)`,

where `d(x,y,z)=z` when `x=y` and `d(x,y,z)=x` otherwise, and where `u(0)=1`, `u(1)=0`, and `u(2)=1`. We study the parameter-free `r`-ary term operations of `Q` that are conservative. Their number is exactly

`|CT_r(Q)| = 2^(5*2^(r-1)-5) * 3^(3^r-3*2^r+3)`.

For an operation `f`, let `C_r(f)` be the minimum number of original-signature operation nodes in a rooted term DAG computing `f`, with free fan-out, and let `D_r(f)` be the corresponding minimum operation depth. We give a parameter-free Lupanov-style compiler and prove

`max_(f in CT_r(Q)) C_r(f) = Theta(3^r/r)`.

The lower bound holds for almost every uniformly selected member of `CT_r(Q)`. A sequence of depth refinements now includes an exact recursive signed-router family and an exact parallel program-vector construction. Conditional on the named upstream compiler lemmas, they culminate in one and the same DAG having

`size=O(3^r/r)`

and

`depth <= r+O(log r)`.

Writing `Delta_r(Q)=max_(f in CT_r(Q)) D_r(f)`, syntax counting also gives the almost-all lower bound

`D_r(f) >= r-log_3(log r)-O(1)`,

and therefore, **conditional on the compiler interface clauses (I1)--(I7) in
Section 6.9**, the worst-case interval

`r-log_3(log r)-O(1) <= Delta_r(Q) <= r+O(log r)  (conditional upper bound)`.

The displayed upper bound and hence the leading-coefficient-one conclusion are conditional in exactly that sense; the independently audited growing-router schedule already supports the weaker conditional bound `r+O(sqrt(r))` after a required residual-first repair. Historical R6/R7 and R9 bounds remain visible as prior compiler stages. The construction combines an exact conservative-clone census, dynamic value names, classical local coding, recursive subcube libraries, a balanced absorbing anchor, signed discriminator routers, and parallel address programs. Deterministic experiments check finite semantics, compiler schedules, mutations, and structural arithmetic. They are validation evidence, not substitutes for the generic proofs. No publication novelty, legal conclusion, practical performance, or relationship to private Tau work is claimed.

**Keywords:** finite algebra; conservative operation; discriminator; term DAG; Shannon complexity; local coding; multivalued logic; circuit depth.

## 1. Introduction

Shannon complexity asks how large a circuit must be in the worst case, and typically for almost every function, when the function class and basis are fixed. Classical work treats Boolean circuits, `k`-valued functional constructions, functionally complete bases, and local-coding synthesis. The object here differs in two linked respects:

1. the original signature `{d,u}` is parameter-free and preserves the proper subalgebra `{0,1}`, so it is not functionally complete on `Q`; and
2. the semantic class is the conservative part of the term clone of one fixed algebra.

The first issue prevents us from simply naming constants. The second makes the semantic entropy slightly smaller than that of all ternary functions while retaining the leading term `(log 3)3^r`. The parameter-free obstacle is handled constructively: a nonbinary input supplies dynamic names for `0,1,2`, first locally and later through one balanced global anchor.

The contribution stack established in this draft is:

1. an exact closed-form census of the conservative `r`-ary term operations;
2. a complete coordinate-selector representation of that fragment;
3. worst-case and almost-all operation-node lower bounds of order `3^r/r`;
4. a matching parameter-free shared-DAG compiler obtained by specializing classical Lupanov local coding;
5. worst-case and almost-all depth lower bounds of order `r`;
6. an explicit compiler progression from exponential Gray dependency depth to linear depth, then to `4r`, `3r+O(log r)`, the historical R9 bound `(3/2)r+O(r/log r)`, an independently audited conditional signed-router bound `r+O(sqrt(r))`, and finally the conditional parallel-program bound `r+O(log r)`, always preserving `O(3^r/r)` size on the same DAG;
7. exact six-way ternary, seven-way Boolean, and nine-way Boolean projection gadgets, retained as historical stages;
8. an exact d-only signed family `P_h,N_h` with `3^(h-1)` programmable branches at dependency depth h, independently audited and Lean-checked;
9. an exact balanced `E/G` address summary that materializes all controls for a capacity-q signed router in `O(q)` shared-DAG nodes and `O(log log q)` preprocessing depth, with both semantics and the full cost/depth recurrence Lean-checked; and
10. source-auditable bounded checks with mutation controls, replay hashes, two independent program-vector specifications, and explicit conditional boundaries.

The local-coding principle, recursive Shannon expansion, discriminator interpolation, and general Shannon-counting methodology are not contributions of this work. The paper-worthy candidate, subject to full prior-art review, is their exact specialization and simultaneous realization for this fixed parameter-free incomplete clone.

## 2. Algebra, semantic class, and cost model

### 2.1 The fixed algebra

Let

`Q=({0,1,2};d,u)`

with

```text
d(x,y,z) = z,  if x=y,
           x,  otherwise,

u(0)=1,  u(1)=0,  u(2)=1.
```

The binary set `B={0,1}` is a proper subalgebra. Its nontrivial automorphism is complement, written `bar(0)=1` and `bar(1)=0`. Notice that `u` is not conservative because `u(2)=1`.

An `r`-ary operation `f:Q^r->Q` is **conservative** if

`f(x_0,...,x_(r-1)) in {x_0,...,x_(r-1)}`

for every input tuple. Let `CT_r(Q)` be the set of conservative `r`-ary operations induced by parameter-free terms over `{d,u}`.

### 2.2 Shared term DAGs

A rooted original-signature term DAG has:

- `r` designated input nodes `x_0,...,x_(r-1)`;
- operation nodes labelled by unary `u` or ternary `d`;
- ordered incoming edges matching the operation arity; and
- one designated output node.

Fan-out is free. Input nodes are not charged. For `f in CT_r(Q)`, define:

- `C_r(f)`: the minimum number of operation nodes in such a DAG computing `f`;
- `D_r(f)`: the minimum operation depth, with every input at depth zero and every operation one plus the maximum depth of its arguments;
- `L_r(Q)=max_(f in CT_r(Q)) C_r(f)`; and
- `Delta_r(Q)=max_(f in CT_r(Q)) D_r(f)`.

The executable compiler reports all distinct reachable nodes, including the `r` inputs, and puts inputs at depth one. Its node count differs from `C_r` by at most `r`, and its depth differs from `D_r` by exactly one. All asymptotic theorems and displayed analytic depth bounds use the operation-node convention.

Ordinary unshared term trees are not the main cost model. The baseline compiler also has an expanded-tree analysis, but no order-optimal ordinary-tree theorem is claimed here.

## 3. Semantic characterization and exact enumeration

### 3.1 Pixley specialization

Pixley's internal-isomorphism characterization of quasi-primal term operations [1,2] implies the following specialization for the fixed algebra.

**Proposition 3.1 (conservative term criterion).** For `r>=2`, a conservative operation `f:Q^r->Q` belongs to `CT_r(Q)` exactly when its restriction to the binary cube commutes with simultaneous complement:

`f(bar(x_0),...,bar(x_(r-1))) = bar(f(x_0,...,x_(r-1)))`

for every `x in B^r`.

**Proof sketch.** Conservativity already preserves each generated subalgebra relevant to a tuple. A nonbinary tuple generates `Q`, while the only nontrivial internal automorphism on the proper binary subalgebra is complement. Pixley's criterion therefore leaves precisely the displayed binary equivariance condition. For `r=1`, the only conservative operation is the identity projection. This is an application of classical theory, not a new interpolation theorem. `square`

### 3.2 Exact census

**Theorem 3.2 (exact conservative term count).** For every `r>=1`,

`|CT_r(Q)| = 2^(5*2^(r-1)-5) * 3^(3^r-3*2^r+3)`.

**Proof.** Partition `Q^r` by the set of values appearing in the tuple.

On the binary cube, the `2^r` tuples form `2^(r-1)` complement pairs. The constant pair `{0^r,1^r}` is forced by conservativity and equivariance. Every other pair contains both values; choosing the value on one representative determines the complementary value on its partner. This contributes

`2^(2^(r-1)-1)`.

A nonconstant tuple over `{0,2}` has two conservative output choices, as does a nonconstant tuple over `{1,2}`. Each alphabet supplies `2^r-2` such tuples. These independent choices contribute

`2^(2*(2^r-2))`.

The all-`2` tuple is forced. Inclusion--exclusion gives

`3^r-3*2^r+3`

tuples using all three values, and each has three conservative output choices. Their contribution is

`3^(3^r-3*2^r+3)`.

Multiplication and collection of the powers of two give the formula. The `r=1` instance equals one. `square`

The first values are

```text
|CT_1(Q)| = 1,
|CT_2(Q)| = 32,
|CT_3(Q)| = 23,887,872.
```

In particular,

`log |CT_r(Q)| = (log 3)3^r + O(2^r)`.

### 3.3 Coordinate-selector completeness

**Proposition 3.3.** Every member of `CT_r(Q)` has a complement-invariant coordinate-selector table.

**Proof.** For every tuple `x`, choose an index `j(x)` such that `f(x)=x_(j(x))`. On each binary complement pair choose the index on one representative and reuse it on its complement. Proposition 3.1 guarantees that the reused index produces the required complementary value. Nonbinary internal-isomorphism orbits are singletons. Conversely, the compilers below realize every such compatible selector table. `square`

Selector tables need not be unique: a tuple can contain the desired output in several coordinates. The statement is semantic completeness, not a canonical encoding claim.

## 4. Counting lower bounds

### 4.1 Shared-DAG size

**Theorem 4.1 (worst-case and almost-all size lower bound).** There is a constant `c>0` such that

`C_r(f) >= c*3^r/r`

for a fraction tending to one of the operations `f in CT_r(Q)`. Consequently,

`L_r(Q)=Omega(3^r/r)`.

**Proof.** Topologically order a term DAG with `s` operation nodes. At operation position `i`, the number of choices for a unary node and its predecessor is at most `r+i`; the number for a ternary node and its ordered predecessors is at most `(r+i)^3`. Choosing the output and summing over all sizes at most `s` changes only constants, so the number of descriptions is

`exp(O(s*log(r+s)))`.

For `s=c*3^r/r`, the exponent is `O(c*3^r)`. Theorem 3.2 gives `exp((log 3+o(1))*3^r)` semantic operations. A sufficiently small fixed `c` leaves an exponentially vanishing fraction covered by the short descriptions. `square`

This is a standard Shannon counting argument. It neither gives an optimal leading constant nor an `Omega(3^r)` lower bound.

### 4.2 Operation depth

Let `A_h(r)` overcount the number of original-signature term trees of operation depth at most `h` on `r` variables. Unsharing a DAG does not increase depth, and

```text
A_0(r) = r,
A_(h+1)(r) <= r + A_h(r) + A_h(r)^3 <= 3*A_h(r)^3
```

for `r>=2`. Therefore

`log A_h(r) <= 3^h*(log r+(log 3)/2)`.

**Theorem 4.2 (almost-all depth lower bound).** For a uniformly selected `f in CT_r(Q)`,

`D_r(f) >= r-log_3(log r)-O(1)`

with probability tending to one. In particular,

`Delta_r(Q)=Omega(r)`.

**Proof.** If `h<=r-log_3(log r)-K` for a sufficiently large fixed `K`, the logarithm of the number of depth-`h` syntactic candidates is a sufficiently small constant multiple of `3^r`, whereas Theorem 3.2 gives semantic log-cardinality `(log 3+o(1))3^r`. The fraction representable at that depth tends to zero exponentially in `3^r`. `square`

The depth lower bound does not assume a bound on DAG size.

## 5. Parameter-free local coding

### 5.1 First-`2` slices and dynamic value names

Partition the nonbinary tuples by the least coordinate `a` at which `x_a=2`. On this slice,

```text
x_0,...,x_(a-1) are binary,
x_a=2,
x_(a+1),...,x_(r-1) are unrestricted.
```

The slice has

`N_a=2^a*3^(r-a-1)`

rows. Within it, the terms

```text
u(u(x_a)),  u(x_a),  x_a
```

name `0,1,2`, respectively. These are branch-local dynamic names, not parameter-free constant terms on all of `Q^r`.

The reachable first-`2` slices exactly partition the `3^r-2^r` nonbinary tuples because

`sum_(a=0)^(r-1) 2^a*3^(r-a-1) = 3^r-2^r`.

This already yields a no-wasted-leaf classifier. In the executable's total-node convention, writing `T_r^base` for its emitted node count, it gives

```text
T_1^base=6,
T_r^base=3*3^r-3*2^(r-1)+6r-4 < 4*3^r  for r>=2.
```

The corresponding fully expanded emitted term has recorded syntax size

`(35*7^r-9*3^r-50)/12`

and depth `4r+1` in the executable convention. These are properties of that compiler, not exact minima.

### 5.2 Mixed-domain local-coding lemma

**Lemma 5.1 (mixed binary/ternary local coding).** Let

`D=A_1 x ... x A_n`,

where each `|A_i|` is two or three, and set `N=|D|`. In a circuit language with names for `0,1,2` and a constant-size conditional selector, every table `F:D->Q` has a shared circuit of size `O(N/n)`, uniformly over the mixture of coordinate alphabets.

**Construction.** For sufficiently large `n`, put `H=floor(log_3(N/n))`; the finitely many smaller cases are absorbed into the uniform constant. Choose a block of coordinates whose number `M` of assignments is maximal subject to `M<=H`. Maximality gives `H/3<M<=H`, while `N>=2^n` implies `M=Theta(n)`. Only `O(log M)` block coordinates are needed.

Precompute the point indicators for the `M` block assignments. There are `3^M` functions from these assignments to `Q`. A reflected ternary Gray order changes one table entry at a time, so one constant-size conditional update creates each successive library member from the preceding one. Thus the shared library costs `O(3^M)`, and

`3^M <= 3^H <= N/n`.

The remaining coordinates have `N/M=O(N/n)` assignments. A mixed-radix decision tree classifies them and lets each leaf point into the shared block-function library. Point indicators, the library, and the prefix tree together cost `O(N/n)`. `square`

This is a concrete specialization of Lupanov's classical local-coding principle [6], not a new general synthesis method.

### 5.3 Size-optimal parameter-free compilation

Apply Lemma 5.1 separately on every first-`2` slice, using the anchor-derived value names. The total nonbinary cost is

`sum_(a=0)^(r-1) O(N_a/r) = O(3^r/r)`.

The all-binary branch is classified modulo complement in `O(2^r)` nodes, and the first-`2` dispatcher costs `O(r)`. Both are lower order. Together with Theorem 4.1 this proves:

**Theorem 5.2 (Shannon complexity).**

`L_r(Q)=Theta(3^r/r)`.

Moreover, for some constant `c>0`, a uniformly selected member of `CT_r(Q)` has complexity at least `c*3^r/r` with probability tending to one, while the compiler supplies the matching order for every member.

The first executable realization uses a Gray-scheduled library. Its size has the desired order, but the Hamiltonian dependency chain gives poor depth. The next sections remove that scheduling artifact.

## 6. Simultaneous size and depth

### 6.1 Layered prefix library

Order the `M` block assignments as `y_1,...,y_M`, with disjoint point indicators `chi_1,...,chi_M`. For every word `w in Q^j`, build `g_w` so that it equals `w_i` at `y_i` for `i<=j` and equals zero at all unprocessed points. The zero extension reuses its parent; the one and two extensions each add one selector. Hence the exact selector census is

`2*sum_(j=0)^(M-1) 3^j = 3^M-1`,

the same as for the Gray library, but the dependency depth is only `M` selector levels. Combining this library with the prefix decision tree proves that one DAG can simultaneously have

`size=O(3^r/r)` and `depth=O(r)`.

Together with Theorem 4.2, this already establishes `Delta_r(Q)=Theta(r)`.

### 6.2 Recursive subcube library and the `4r` bound

The layered construction is sharpened by recursively indexing the library by its actual mixed-radix block coordinates. If their alphabet sizes are `q_1,...,q_b in {2,3}`, let

`M_j=product_(i=j)^b q_i`.

At a binary level, one normal selector combines each pair of suffix functions. At a ternary level, two nested normal selectors combine each triple. The exact number of normal-selector calls is

`S(q_1,...,q_b)=sum_(j=1)^b (q_j-1)*3^(M_j) < 3*3^M`.

The top level dominates because `M_(j+1)<=M_j/2`. The library remains `O(3^M)`, while a full mixed-radix prefix tree with `P` leaves uses exactly `P-1` weighted selector calls.

The explicit depth accounting on first-`2` slice `a` is

`2 + 2a + 4(r-a-1) + 2(a+1) = 4r`.

The four terms are, respectively, the deepest anchor-derived name, binary and ternary coordinate routing inside the slice, and the first-`2` dispatcher. The all-binary branch has depth at most `4r-2`.

**Theorem 6.1 (same-DAG `4r` construction).** Every `f in CT_r(Q)` has one parameter-free original-signature DAG with

`size=O(3^r/r)` and `depth<=4r`.

### 6.3 One global nonbinary anchor

Define

`h(x,y)=d(x,u(u(x)),d(y,u(x),x))`.

**Lemma 6.2.** For all `x,y in Q`, `h(x,y)=2` exactly when `x=2` or `y=2`; otherwise `h(x,y)=x`.

Balanced-fold `h` over all input variables and call the result `A`. Then

```text
A=2 exactly on nonbinary tuples,
A=x_0 on the binary cube,
size(A)=O(r),
depth(A)<=3*ceil(log_2 r).
```

On the nonbinary branch, `u(u(A)),u(A),A` are global dynamic names for `0,1,2`. On the binary branch they deliberately are not global constants. This is what keeps the construction parameter-free and compatible with the preserved subalgebra `B`.

An exhaustive closure of binary-arity term functions through operation depth three has cumulative sizes `2,4,20,270`; the absorber's target semantics first occurs at depth three. This finite fact concerns this absorber, not the optimal depth of the final global compiler.

### 6.4 A branch-depth-three ternary router

On a branch where terms named `0,1,2` have the indicated values, define

```text
mux(x,b0,b1,b2)
 = d(
     d(0,d(x,2,b0),d(0,x,b0)),
     0,
     d(d(1,x,b1),1,d(x,2,b2))
   ).
```

**Lemma 6.3.** For every `x,b0,b1,b2 in Q`,

`mux(x,b0,b1,b2)=b_x`.

Every branch argument lies exactly three discriminator nodes below the root. Direct substitution for `x=0,1,2` proves the identity. With `0=u(u(A))`, `1=u(A)`, and `2=A`, the materialized router has operation depth five relative to an input anchor and fifteen distinct nodes including its five terminals.

A finite Z3 `QF_BV` search reports `UNSAT` for branch depth at most two in a deliberately generous selector-only grammar: all 27 unary functions of the selector are admitted as free terminals; `b0,b1,b2` are branch terminals; internal nodes are `u` or `d`; and all 81 valuations are imposed on the complete depth-two syntax tree. Together with the displayed term, this makes depth three optimal only for that finite branch-scoped grammar. It is not a global depth lower bound and currently has no separately checked proof certificate.

### 6.5 Global library and final depth theorem

Put

`H=floor(log_3(3^r/r))`.

Choose `b` ternary coordinates so that their number of assignments `M=3^b` is maximal subject to `M<=H`. Apart from finitely many small arities, `H/3<M<=H`, and therefore

```text
M=Theta(r),
3^M<=3^r/r,
3^r/M=O(3^r/r).
```

Build every `Q`-valued function on the local block recursively, using the router of Lemma 6.3 at each coordinate. The library costs `O(3^M)`. Route the remaining prefix coordinates with the same router; the prefix tree costs `O(3^r/M)`. Add the `O(r)` global anchor and the lower-order `O(2^r)` complement-orbit classifier for the binary branch. A final normal selector chooses that binary classifier exactly when `u(u(A))=A` and otherwise chooses the global nonbinary library.

The block and prefix partition the `r` routed coordinates. Each routed coordinate adds three branch-dependency levels. The deepest dynamic name has depth `3*ceil(log_2 r)+2`, and the final binary/nonbinary selector adds two levels. Hence:

**Theorem 6.4 (simultaneous Shannon size and explicit depth).** Every `f in CT_r(Q)` has one parameter-free original-signature term DAG with

`size=O(3^r/r)`

and

`depth<=min(4r,3r+3*ceil(log_2 r)+4)`.

Combining Theorems 4.2 and 6.4 gives

`r-log_3(log r)-O(1) <= Delta_r(Q) <= min(4r,3r+3*ceil(log_2 r)+4)`,

and in particular

`r-log_3(log r)-O(1) <= Delta_r(Q) <= 3r+O(log r)`.

Thus this historical compiler already proves `Delta_r(Q)=Theta(r)` with
leading-coefficient interval `[1,3]`. Theorem 6.5 below strictly narrows the
current upper endpoint. Neither endpoint is claimed optimal.

### 6.6 Historical R6/R7 programmable projection routing

The coordinate-by-coordinate compiler spends three branch-dependency levels
to expose three projections. A fixed router can amortize those levels over
more branches, provided its program controls are compiled and shared without
destroying the Shannon-size bound.

There are two exact original-signature gadgets:

- `R6`, with 13 discriminator nodes and dependency depth three, realizes each
  of six ternary branch projections from one of six fixed 18-slot programs;
  and
- `R7`, with 12 discriminator nodes and dependency depth three, realizes each
  of seven Boolean branch projections from one of seven fixed 16-slot
  programs.

The complete skeletons and program words appear in
`notes/QUASIPRIMAL_CONSERVATIVE_TERM_PROGRAMMABLE_DEPTH.md`. The `R6` identity
is checked on all `6*3^6` target/branch cases. On the binary cube, `R7` is
interpreted relative to `x_0`: program bits are represented by `x_0` and
`u(x_0)`. Since `d` commutes with simultaneous Boolean complement, the same
selected coordinate is returned on both members of a complement pair. No
global Boolean constants are assumed.

For `N` points and fan-out `q`, recursively split every nonsingleton node into
`min(q,N)` nonempty balanced parts. The code tree has height at most
`ceil(log_q N)` and at most `N-1` internal nodes. At each level, the active
nodes partition the points, so their local child labels combine into one total
digit function. This permits one shared family of program controls per level.
For sequential chunks, with `P_j=product_(i<=j)N_i`, the router count
telescopes exactly:

`sum_j P_(j-1)(N_j-1)=P_m-1`.

Use the global anchor from Lemma 6.2. Put

```text
H=max(1,floor(log_3(3^r/r))),
M=3^b, the largest power of 3 not exceeding H,
P=3^(r-b).
```

On the nonbinary branch, a balanced six-way library contains all `3^M`
functions on the block. If `G(t)` counts its discriminator nodes, balanced
splitting gives

```text
G(0)=G(1)=0,
G(t)=13*3^t+sum_i G(t_i),
G(t)<=26*3^t.
```

The prefix adds at most `13(P-1)` nodes. Compile ternary control functions on
chunks of width `g_3=ceil(log_3 r)`; there are `O(r)` code levels, and each of
the 18 controls per level costs `O(3^g_3)=O(r)`. Hence controls add only
`O(r^2)`. The binary branch uses relative bits, width
`g_2=ceil(log_2 r)`, seven-way routing, and `O(2^r+r^2)` nodes. These are lower
order, so the whole shared DAG still has size `O(3^r/r)`.

Let `L_6` and `L_7` be the sums of balanced-code heights over the ternary and
binary chunks, including the local block in `L_6`. Then

```text
L_6 <= log_6(3)*r+O(r/log r),
L_7 <= log_7(2)*r+O(r/log r).
```

All controls at a route level are precomputed in parallel, and each router
adds at most three dependency levels. Including the anchor and outer selector,

```text
D_nonbinary <= (3*log_6(3))*r+O(r/log r),
D_binary    <= (3*log_7(2))*r+O(r/log r).
```

The first coefficient is `1.839441578296...`; the second is
`1.068621561324...`. The nonbinary branch dominates.

**Theorem 6.5 (programmable same-DAG depth).** Every `f in CT_r(Q)` has one
parameter-free original-signature term DAG with

`size=O(3^r/r)`

and

`depth <= (3*log_6(3))*r+O(r/log r)`.

Consequently,

`r-log_3(log r)-O(1) <= Delta_r(Q) <= (3*log_6(3))*r+O(r/log r)`.

The generic proof has passed one independent internal audit conditional on the
upstream selector-existence and global-anchor lemmas. It is not Lean-checked or
peer reviewed. The fixed routers are not claimed projection-capacity-optimal,
and the leading depth coefficient is not claimed optimal.

### 6.7 Historical Boolean-plane R9 routing

The R6/R7 construction is not the current ceiling. There is an exact Boolean
router `R9` consisting of one full depth-three `d` tree: 13 discriminator
nodes, 18 program slots, and nine branch leaves `b0,...,b8`, each appearing
once. Nine fixed 18-bit programs realize all nine projections. Exhaustive
replay checks `9*2^9=4,608` Boolean cases; an independent no-solver audit also
checks simultaneous-complement semantics and an effective mutation for every
target.

On the nonbinary branch, encode the three dynamic value names by

```text
0->00, 1->01, 2->10
```

and run the same R9 program on the two Boolean planes in parallel. Decode once
after all route levels by

```text
Dec(high,low)=d(d(high,one,two),zero,low).
```

This is an ordinary pair of original-signature sub-DAGs followed by an
original-signature decoder, not a new multi-output primitive. Exhaustive replay
checks all `9*3^9=177,147` target/payload cases. On the binary branch, R9 uses
the complement-relative names `x_0,u(x_0)` exactly as R7 did.

Replace fan-out six by fan-out nine in the balanced block and prefix codes.
Two R9 copies charge 26 discriminator nodes per code node. If `G(t)` counts
the local encoded library, then

```text
G(1)=0,
G(t)=26*3^t+sum_i G(t_i),
G(t)<=78*3^t.
```

The prefix costs at most `26(P-1)` router nodes. One shared family of 18
address-only controls per route level serves both planes; compiling those
controls on chunks of width `ceil(log_3 r)` remains `O(r^2)`. Thus the anchor,
encoded library, prefix, controls, decoder, binary branch, and outer selector
still total `O(3^r/r)` nodes on one DAG.

Writing `L_9^Q` and `L_9^B` for the sums of code heights gives

```text
L_9^Q <= log_9(3)*r+O(r/log r)=r/2+O(r/log r),
L_9^B <= log_9(2)*r+O(r/log r).
```

The bit planes are parallel, each router level adds three dependency layers,
and the decoder is applied once. Therefore the nonbinary coefficient is
`3*log_9(3)=3/2`, while the binary coefficient is
`3*log_9(2)=0.9463946303...`.

**Theorem 6.6 (Boolean-plane R9 same-DAG depth).** Every `f in CT_r(Q)` has
one parameter-free original-signature term DAG with

```text
size  = O(3^r/r),
depth <= (3/2)r+O(r/log r).
```

Consequently,

`r-log_3(log r)-O(1) <= Delta_r(Q) <= (3/2)r+O(r/log r)`.

The complete proof ledger and frozen witness are in
`notes/QUASIPRIMAL_CONSERVATIVE_TERM_BOOLEAN_R9_DEPTH.md`. The R9 identity and
bounded composed compiler are computationally checked; the all-arity theorem
is a manuscript proof awaiting formal verification and peer review. A
radius-one search found no R10 by one-leaf insertion into the frozen R9. That
is a bounded `NO_HIT`, not a global R10 impossibility theorem.

### 6.8 Recursive signed discriminator routers

The fixed R9 is not the final routing object. On the Boolean subalgebra define
positive and negative depth-one cells

```text
P_1(x;c0,c1)=d(x,c0,c1),
N_1(x;c0,c1)=d(c0,x,c1).
```

The exact programs are

| cell | projection mode | constant 0 | constant 1 |
|---|---|---|---|
| `P_1` | `(0,0)` returns x | `(1,0)` | `(0,1)` |
| `N_1` | `(0,1)` returns `1-x` | `(0,0)` | `(1,1)` |

Recursively set

```text
P_h=d(P_(h-1),N_(h-1),P_(h-1)),
N_h=d(N_(h-1),P_(h-1),N_(h-1)).
```

For a target in the left, middle, or right branch group, program the three
children respectively as

```text
(projection,constant 0,constant 0),
(constant 0,projection,constant 1),
(constant 0,constant 0,projection).
```

At a positive parent the resulting expressions are

```text
d(x,0,0)=x,
d(0,1-x,1)=x,
d(0,0,x)=x.
```

The same transitions at a negative parent return `1-x`. Constants lift by
`d(c,c,c)=c`.

**Theorem 6.7 (exact strong signed-router family).** For every `h>=1`, there
are d-only full trees `P_h,N_h` with

```text
capacity                 q_h=3^(h-1),
branch leaves             q_h,
address-control leaves    2q_h,
discriminator nodes       (3^h-1)/2,
dependency depth          h.
```

For every target, `P_h` returns the target branch and `N_h` its Boolean
complement; both signs also have constant-zero and constant-one modes. Every
branch path in `P_h` has even middle-edge parity, while every branch path in
`N_h` has odd parity.

**Proof.** The semantic modes follow from the preceding induction. The
recurrences

```text
q_h=3q_(h-1),
C_h=3C_(h-1),
S_h=1+3S_(h-1),
D_h=1+D_(h-1)
```

start at `q_1=1,C_1=2,S_1=D_1=1` and give the displayed counts. The middle
child swaps P and N, while the outer children preserve the sign, proving the
path-parity statement. No NOT or signed-leaf constructor occurs in the tree.
`square`

Thus depth four already gives an exact R27 with 40 d nodes, 27 branches, and
54 controls; depth six gives R243. At fixed h the routing coefficient is
`h/(h-1)`, tending to one. The family theorem has been independently derived
and replayed and has also been formalized in Lean in the exact d-only grammar.

The representation bridges must still be charged. On a nonbinary slice,
`A=2` supplies legal names `u(A)` and `u(u(A))`; two sibling copies of the
router carry the Boolean planes and are decoded once. On the binary cube a
logical relative program bit p is address-only, but its physical
representative is `x_0` when `p=0` and `u(x_0)` when `p=1`. Those physical
wires are payload-relative. Their legality comes from simultaneous-complement
equivariance, not from treating them as absolute constants or literally
payload-independent controls.

Choosing `k=floor(sqrt(r))`, `h=k+1`, and `q=3^k`, and routing every short
residual chunk first, gives the following audited compiler implication.

**Conditional Corollary 6.8 (growing-router compiler).** Assume the
coordinate-selector, global-anchor, two-plane representation, binary-orbit,
decoder, and outer-glue lemmas used by the preceding compiler. Then every
`f in CT_r(Q)` has one original-signature shared DAG with

```text
size  = O(3^r/r),
depth = r+O(sqrt(r)).
```

The residual-first qualification is necessary for this ledger. A
residual-last schedule has an explicit coefficient-breaking counterexample at
`r=512`. An independent accounting audit checks the repaired integer schedule
for every `64<=r<=10000`, including all controls, both planes, padding, the
binary branch, anchor, decoder, and glue. This is an audited conditional
composition, not a Lean proof of the end-to-end compiler.

### 6.9 Parallel program vectors and logarithmic overhead

The signed family exposes a second bottleneck: compiling `2q` program slots
one at a time would cost `Theta(q log q)` for a capacity-q router. The slots
instead admit one balanced shared summary.

A **multi-output shared DAG** is an acyclic original-signature operation graph
with a finite ordered list of distinguished roots. Its size is the number of
operation nodes in the union of the ancestors of those roots, counted once;
inputs are free and fan-out is unrestricted. Substituting such a vector into a
larger DAG means adjoining this union once and wiring arbitrary references to
its distinguished roots. Consequently, a vector shared by every local table,
both Boolean planes, or every physical router is charged once, not once per
consumer. The final compiler has one distinguished output root and is measured
by the single-output convention of Section 2.

Write a physical branch and the requested target as ternary words
`p,t in {0,1,2}^w`, so `q=3^w`. Define

```text
E_p(t)=[t=p],
G_p(t)=[the first mismatch j has (t_j,p_j)=(1,2)].
```

Following the recursive mode program down branch p remains in projection mode
while the digits agree. At the first mismatch it enters constant-one mode
exactly in the case recorded by G and constant-zero mode otherwise. Hence the
bottom cell projects exactly when `E=1` and otherwise returns G. If the bottom
cell is positive, its ordered program pair is

```text
(not(E or G),G),
```

while a negative cell uses

```text
(G,E or G).
```

The sign is the root sign xor the parity of the number of middle digits in p.
For a requested constant c, the positive and negative pairs are respectively
`(1-c,c)` and `(c,c)`.

For consecutive word blocks A and B, first-mismatch semantics gives the
associative composition law

```text
E_AB=E_A and E_B,
G_AB=G_A or (E_A and G_B).
```

On the nonbinary branch put `two=A`, `one=u(A)`, and `zero=u(u(A))`. Exact
one-digit indicators and Boolean connectives in the original signature are

```text
delta_0(x)=u(d(x,two,one)),
delta_1(x)=d(x,two,zero),
delta_2(x)=u(d(x,zero,one)),
x and y=d(x,one,y),
x or y=d(x,zero,y),
not x=u(x).
```

Let `S(w)` count the shared operation nodes needed for all E/G states under a
balanced split. Then

```text
S(1)=5,
S(w)=S(floor(w/2))+S(ceil(w/2))+3*3^w,
S(w)<=5*3^w.
```

Forming `E or G` and the needed complements adds fewer than `2q` nodes.

**Theorem 6.9 (exact parallel program vector).** Let the anchor input satisfy
`A=2`. For either root sign and every width `w>=1`, all `2q` controls of the
capacity-`q=3^w` signed router, in every projection or constant mode, are
realized simultaneously by legal d/u terms depending only on that anchor and
the target-address digits,
with

```text
size  <= 7q shared operation nodes including the two shared anchor names,
depth <= 6+2*ceil(log_2 w)
```

above the raw anchor and address inputs. Thus preprocessing depth is
`O(log w)=O(log log q)`, not one decision-list depth per control.
The width-zero base router uses only the two shared name levels.

The term grammar in the construction is globally constant-free, but the
displayed Boolean meanings of `u(A)` and `u(u(A))` are asserted only under
`A=2`. The theorem is therefore the nonbinary program-vector interface; it
does not supply absolute Boolean controls on the all-binary cube.

The exact E/G meaning, sign parity, ordered pair, disjointness, associative
segment law, balanced materialization recurrence, `7q` size ledger including
the shared names, and logarithmic-depth ledger are Lean-checked. The cost
formalization is a recurrence-level shared-DAG certificate; it does not extract
a serialized node-indexed graph or certify a particular hash-consing program.

To apply this vector to the compiler, fix `C=4` and, for `r>=64`, set

```text
L=4+ceil(log_3(r^2)),
H=r-L,
M=3^floor(log_3 H),
b=log_3 M,
P=3^(r-b).
```

The local block has M assignments. Build all `3^M` Q-valued local tables with
two capacity-M routers per table and share one width-b program vector among
all tables and both planes. This costs at most

```text
(3M-1)3^M+7M.
```

One capacity-P prefix router per plane, with one shared width-`r-b` vector,
costs at most `(3P-1)+7P`. Since `M>r/6` and the two-logarithm reserve gives

```text
3M*3^M <= (1/27)*3^r/r,
10P < 60*3^r/r,
```

the anchor, names, decoder, glue, and lower-order terms fit within the explicit
nonbinary bound `62*3^r/r`. Retaining the separately audited
complement-relative square-root binary branch gives one additional unit. The
nonbinary depth ledger is

```text
depth <= r+5*ceil(log_2 r)+12.
```

The retained binary depth is below r from the checked arity 339 and has
asymptotic coefficient `log_3(2)<1`; finitely many smaller arities use the
retained finite ledger when `64<=r<339`, while `r<64` uses the earlier
compiler.

The final branch glue is explicit. Put `s=u(u(A))`, let `B` be the binary
branch result, and let `N` be the nonbinary result. Then

```text
Glue(A,B,N)=d(d(s,A,B),d(s,A,N),N)
```

has three new discriminator nodes and adds two operation levels. Since
`s=A` exactly on the all-binary cube and `A=2,s=0` otherwise, it returns `B`
on binary inputs and `N` on nonbinary inputs.

For a precise conditional statement, use the following compiler interface for
each arity `r` and every compatible selector table `sigma:Q^r->{0,...,r-1}`.

- **(I1) Selector representation.** Every `f in CT_r(Q)` has such a total
  complement-invariant `sigma` with `f(x)=x_(sigma(x))`.
- **(I2) Anchor.** One original-signature DAG supplies `A` with
  `A=2` exactly off the binary cube and `A=x_0` on it, using at most
  `4(r-1)` nodes and depth at most `3*ceil(log_2 r)`.
- **(I3) Encoded nonbinary compiler and inclusive ledger.** For `r>=64`, with
  the displayed `M,b,P`, two Boolean planes, the exact program vector of
  Theorem 6.9, and one final two-node decoder jointly realize
  `x_(sigma(x))` whenever `A=2`.  The union of those nodes with the anchor of
  (I2), its two shared value-name nodes, and the three glue nodes reserved in
  (I6) has fewer than `62*3^r/r` nodes.  Before the two glue levels, the
  nonbinary output has depth at most `r+5*ceil(log_2 r)+10`.
- **(I4) Binary compiler.** One complement-equivariant original-signature DAG
  realizes `x_(sigma(x))` on the binary cube using physical relative controls
  `x_0,u(x_0)`, size below `3^r/r` for `r>=64`, and depth
  `log_3(2)r+O(sqrt r)`; its checked explicit ledger is below r for `r>=339`.
- **(I5) Same-DAG substitution.** The local and prefix program vectors in
  (I3) are each adjoined once and shared across all tables, routers, and both
  planes according to the multi-output convention above; the two branch DAGs
  and anchor are united once before gluing.
- **(I6) Glue.** The displayed three-node term `Glue(A,B,N)` combines (I2)--
  (I4) with two additional depth levels.
- **(I7) Finite fallback.** For every `1<=r<64`, a named earlier
  original-signature compiler from Theorems 6.4--6.8 supplies a finite
  size/depth value.  The finitely many values of the binary ledger in (I4) for
  `64<=r<339` are likewise absorbed into the additive depth constant. No
  explicit `63`-constant claim is made below arity 64.

**Conditional Theorem 6.10 (parallel-program compiler).** Conditional on the
interface propositions (I1)--(I7), every `f in CT_r(Q)` has one parameter-free
original-signature term DAG with

```text
size  = O(3^r/r),
depth = r+O(log r).
```

For `r>=64`, the inclusive nonbinary ledger in (I3) and the binary ledger in
(I4) give fewer than `63*3^r/r` nodes; the nonbinary branch has depth at most
`r+5*ceil(log_2 r)+12`, while (I4) is asymptotically smaller.
Clause (I7) supplies the finite remainder. Together with Theorem 4.2 this
conditionally matches the leading depth coefficient one. It does not
establish an optimal additive term, an ordinary-tree bound, or an
unconditional integrated theorem without (I1)--(I7). A no-author-import audit
independently passes the exact vector and the displayed compiler ledger through
arity 16,384, but does not re-prove every interface proposition; a fully
integrated independent reconstruction remains open.

## 7. Compiler progression and bounded validation

### 7.1 One common arity-nine target

The compilers were compared on the same fixed arity-nine reduction selector, evaluating all `3^9=19,683` input rows. The reported node counts include variables, and reported depths put variables at depth one.

| compiler schedule | distinct reachable DAG nodes | reported depth |
|---|---:|---:|
| no-wasted-leaf first-`2` classifier | 58,331 | 37 |
| Gray local coding | 19,329 | 179 |
| layered prefix library | 18,327 | 45 |
| recursive subcube library | 18,135 | 37 |
| global anchor and depth-three router | 23,807 | 41 |

The table illustrates different goals. Gray local coding produces the first large size reduction but serializes the library. Layering removes that chain. Recursive subcubes give the best bounded result in this test. The global-anchor compiler is asymptotically shallower but is worse at arity nine.

The structural analytic bounds are equal at arity `16`; the global bound is smaller than `4r` from arity `20` onward. At arities `32,64,128,256`, the recorded depth-bound savings are `13,42,103,228`, respectively. These are arithmetic consequences of the proved formulas, not performance claims about a materialized large circuit.

The later routing stages are theorem-level schedule comparisons, not additions
to the materialized arity-nine benchmark above:

| routing stage | same-DAG size | depth ceiling | evidence status |
|---|---:|---:|---|
| historical R6 | `O(3^r/r)` | `(3*log_6(3))r+O(r/log r)` | manuscript proof plus bounded replay and audit |
| historical Boolean-plane R9 | `O(3^r/r)` | `(3/2)r+O(r/log r)` | manuscript proof plus bounded replay and audit |
| recursive signed family | `O(3^r/r)` | `r+O(sqrt(r))` | exact family independently audited and Lean-checked; compiler conditional and independently audited after repair |
| parallel E/G vector | `O(3^r/r)` | `r+O(log r)` | exact vector independently audited and Lean-checked through its full `7q` cost/depth ledger; compiler arithmetic independently conditionally passed, with frozen integration bridges still assumed |

R9 is therefore a preserved historical stage, not the current conditional
ceiling.

### 7.2 Finite checks

The deterministic checkers currently establish the following bounded facts.

- The exact category census agrees with the formula through arity eight.
- All `1` and `32` semantic conservative operations at arities one and two are directly enumerated and compiled.
- The arity-three formula evaluates to `23,887,872`.
- All `128` compatible arity-two selector-index tables are compiled and checked; the larger number reflects nonunique selector representations, not additional semantic operations.
- Fixed-seed full-table evaluation is performed through arity seven.
- Every row of the arity-nine reduction selector is evaluated.
- Gray paths through block length four, layered selector censuses through `M=8`, representative recursive-subcube censuses, and asymptotic plan arithmetic through arity `64` are checked.
- The absorber is checked on all nine input pairs; the router is checked on all 81 valuations; balanced anchors are checked through arity seven; and global structural depth arithmetic is checked through arity `256`.
- The programmable routers are checked on all 4,374 six-way cases, 896 seven-way cases, and 896 complement-relative cases. The composed compiler covers all 128 compatible arity-two selector tables plus fixed-seed tables through arity five, and its library and structural recurrences are checked through 128 points and arity 4,096, respectively.
- The Boolean R9 is checked on all 4,608 projections and 9,216 relative-orientation cases; the two-plane transfer is checked on all 177,147 target/payload cases. Its composed compiler covers 135 tables and 1,641 complete tuples through arity five, with the library recurrence checked through 256 points and structural depth arithmetic through arity 4,096.
- The recursive signed family is proved by induction, independently checked through direct truth tables and discriminator ROBDDs, mutation-tested on every R27 target, and Lean-checked for every depth, sign, mode, target, and Boolean branch valuation. The independent compiler audit checks every integer arity `64..10000` after the residual-first repair.
- The parallel E/G vector is checked on 1,200,114 target/physical/sign pairs, 18 dependency sets, 11,356 concrete router cases, 262 direct-discriminator ROBDD modes, and 232 padding cases. Its author ledger checks every integer arity `64..4096`; an independent no-author-import audit extends the arithmetic replay through arity 16,384 and independently materializes both signs through width nine. Normal and optimized receipts are byte-identical.
- Lean proves the E/G first-mismatch meaning, disjointness, sign parity, ordered program pair, associative segment composition, balanced shared-DAG recurrence, `7q` node bound including both generated names, logarithmic depth, and nonbinary original-signature legality. It does not prove a serialized DAG extraction or the end-to-end `r+O(log r)` compiler.
- Mutation controls detect omitted complement quotienting, spurious all-`2` choices, complement asymmetry, corrupted Gray paths, invalid block caps or schedules, incorrect selector censuses, dropped depth corrections, wrong absorbers, constant swaps, incomplete tables, and binary-anchor scope errors.
- Programmable-routing controls additionally reject effective gadget mutations, illegal absolute binary controls, omitted or per-node control accounting, sparse full-code accounting, omission of the binary depth branch, and a non-complement-invariant selector table.
- Boolean-plane controls additionally reject serializing the planes, repeating the decoder at every level, omitting the decoder charge, and moving from per-level to per-node controls.

These computations validate implementations, bounded identities, and arithmetic. They do not prove the all-`r` theorems or publication novelty.

### 7.3 Replay receipts

Normal and optimized Python runs agree at the following semantic hashes.

| receipt | semantic SHA-256 |
|---|---|
| `runs/quasiprimal_conservative_term_count/summary.json` | `f7f1758972b68abd8aba60ae547cb899c5d9376cced7cba449c34a2697e001b8` |
| `runs/quasiprimal_local_coding_compiler/summary.json` | `4aaf27d678847aa0455ae8be552a165c3e9ec08c007031878f6aa40b0794ed89` |
| `runs/quasiprimal_layered_local_coding_compiler/summary.json` | `b42fa56c1e78e670e2a436181337957309a0b2a658b6f539486b85cedc482d54` |
| `runs/quasiprimal_subcube_local_coding_compiler/summary.json` | `f9d89ec9829c3abef05d1cdc17ef811330674bd056d90c3579a8f32b0b2eb7b8` |
| `runs/quasiprimal_global_anchor_routing/summary.json` | `fb5ca7bf56d9aba9fdb0f69d1f1355c92d56d4f9306ee08a922bfc770ef60501` |
| `runs/quasiprimal_programmable_projection_routing/summary.json` | `e663534756cf67ffb12fd9ae3fe722c465bd70cd91b73af1fb8084af1c0706dc` |
| `runs/quasiprimal_boolean_r9_routing/summary.json` | `e4a09ef72986c1221c28e80d8227879a9e0aa0f93679e49e9f750f7e65977fce` |
| `research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/summary.json` | `4852080965ac89f54f436401950ca22ecc0dd7887593b5c01dcadcaeb883ea2a` |
| `research/tournaments/2026-08-13-semantic-router-frontier/audits/strong_family/receipt.json` | `ac566d0b716575ff693bc3a1f125283c764ef608a04c183a17293fe66adc4cb2` |
| `research/tournaments/2026-08-13-semantic-router-frontier/audits/variable_compiler/receipt.json` | `d81d0bd6b979ec0df4270fd60f04468884de6e286aea450ba28eed9897e51870` |
| `research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/receipt.json` | `9699a3fe058369ac22a4a4d8050d07825cc80112cbc4c601a85914100db13f88` |
| `research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/receipt.json` | `4922df2221b3e6195d7b1af3a3ac770ae92a8aed10843430b9cffb20959c58ea` |

The formal checkpoints are source- and receipt-hash bound:

| formal source | source SHA-256 | receipt SHA-256 |
|---|---|---|
| `lanes/formal/StrongSignedRouter.lean` | `687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a` | `e984f5cf50bc23489fe7bd832f08c075f61abf66885c6b0736735420eb934662` |
| `lanes/formal_program_vector/ProgramVector.lean` | `c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd` | `5e79e4eb49af361fbed1c8962a67583a48e532526698da584b8825d55136cffa` |
| `lanes/formal_program_vector_cost/ProgramVectorCost.lean` | `ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2` | `4919835f32d8afdfc48f72979edf4ad4ef0b1f8b16271ed9858a60750d2b6211` |

## 8. Relation to prior work

This draft intentionally separates classical ingredients, directly adjacent work, and the still-unknown originality of the exact conjunction.

### 8.1 Universal algebra

Pixley's discriminator and quasi-primal results [1,2] supply the internal-isomorphism characterization used in Proposition 3.1. Baker--Pixley interpolation [3] and Quackenbusch's extension hierarchy [4] form the wider structural background. None of those results is claimed here. Modern discriminator-clone and conservative-clone work, including [14], must also be checked in full before submission.

### 8.2 Shannon synthesis and multivalued logic

Shannon's circuit-counting method is classical [5]. Lupanov introduced the local-coding principle used in the upper bound [6]. Yablonskii's functional constructions in `k`-valued logic establish a much broader historical setting [7]. Orlov studies realization and basis-sensitive circuit and formula Shannon functions for `k`-valued bases [8,27]. Kochergin establishes linear Shannon-depth behavior for `k`-valued functions over arbitrary complete finite bases [9]. Safin studies depth versus complexity in precomplete multivalued classes [10]. Korshunov's survey maps local coding, Shannon effects, leading coefficients, formulas, and depth [13]. Gashkov's primary 1978 theorem gives Boolean formulas over `{AND,OR,NOT}` with depth `n-log_2(log_2 n)+O(1)` while retaining formula-Shannon size `Theta(2^n/log n)` [28].

The present parameter-free basis is incomplete because every term preserves `B={0,1}`. Therefore the scopes are not textually identical. That difference is not novelty evidence: the present theorems, including the signed recurrence and parallel E/G vector, may still be expected specializations or consequences of older closed-class complexity, local-code decoding, switching-term, multiplexer, or universal-circuit machinery. Dual-rail or two-rail representations are also classical in logic synthesis; Ishiura gives a two-rail-input/two-rail-output BDD synthesis construction in a different basis and objective [19], and Backes uses dual-rail encodings of ternary semantic values for verification-oriented circuit transformations [20]. These do not establish or refute the fixed-`Q` theorem, but they prevent claiming the representation change itself as novel. Full-text Russian and international review is required. Tarasov's work on depth versus complexity for many-valued functional systems is another nearby line that must be compared directly before submission [17,18].

### 8.3 Simultaneous size and depth, and multiplexer depth

Lozhkin gives Boolean results on formulas simultaneously approaching Shannon size and depth [11] and, more recently, exact basis-sensitive depth results for multiplexers with few selector lines [12]. McColl and Paterson give a classical leading-one depth shape for all Boolean functions in a richer basis [24]. Gashkov's source proof uses a Lupanov parallel-series representation, but a checked transfer ledger shows that dense Booleanization gives leading depth `log_2(3)r` and source-witness size `Theta(3^r/log r)`, so it does not directly supply the present same-DAG order `O(3^r/r)` or coefficient one [28]. This nontransfer is not novelty evidence: a native Q-valued Lupanov--Gashkov construction remains open, and Lupanov's separate delayed-circuit model still requires a primary-source model comparison. Valiant's universal circuits and Cook--Hoover depth-universal circuits establish programmable control and joint size/depth routing as classical themes [21,22]. Holmgren and Rothblum give modern linear-size shared multiselection circuits in a different Boolean model [23]. Those models do not immediately translate to this incomplete ternary term clone, but they make broad novelty claims about programmable controls, shared selection, simultaneous synthesis, or leading-one depth unsafe. The unresolved comparison is the exact conjunction of the fixed no-nullary signature, signed P/N counts, charged E/G materialization, and same-DAG compiler.

### 8.4 Chinese-language adjacency

The public-index search located Wu and Chen's 1985 ternary sequential-circuit
work with three-rail output [15] and Xu, Guan, and Zhang's 2013 ternary
reversible-logic synthesis algorithm [16]. A focused follow-up also located
Zhang, Chen, and Wang's BDD-to-MUX area/delay optimization [25] and He, Gong,
and Wei's shared multi-output BDD construction [26]. Their algebras,
reversibility conditions, and physical, empirical, or gate-cost objectives
differ from original-signature `Q`-term DAGs, but the latter two are direct
adjacency for shared selector structures.

No direct match was verified in the bounded search for the exact fixed-`Q` census, the d-only signed `P_h/N_h` family, the charged E/G vector, or their conditional same-DAG `O(3^r/r)` and `r+O(log r)` conjunction. This is only weak negative evidence. Native CNKI/Wanfang full-text coverage, translation variance for clone-theoretic terminology, Russian citation-chain review, paywalled many-valued sources, and expert comparison remain missing.

### 8.5 Paper-safe positioning

The strongest currently supportable positioning is:

> Classical interpolation, counting, local-coding, and programmable-selection tools are specialized to one fixed parameter-free conservative term fragment. The resulting exact census, signed-router family, and parallel address summary support an explicit conditional same-DAG compiler at the counting-scale size and leading-one depth.

Whether that exact specialization or conjunction is publication-novel remains **UNKNOWN**.

## 9. Provenance, Tau boundary, and explicit nonclaims

The mathematics in this draft concerns one public classical finite algebra and public circuit-complexity methods. The recorded implementations were independently written for OrbitSynthesis and do not rely on Tau source, Tau specifications, private communications, private materials, or an unsigned developer license. This is a provenance statement only. It is not a novelty finding, a patent analysis, a license interpretation, or a noninfringement opinion.

This draft does **not** claim:

- an optimal leading constant for shared-DAG size;
- an unconditional end-to-end `r+O(log r)` theorem independent of the named upstream compiler lemmas;
- an exact or optimal additive term beyond the conditional leading-depth coefficient one;
- that the finite Z3 result applies outside its selector-only depth-two grammar;
- an `Omega(3^r)` size lower bound;
- an order-optimal ordinary unshared-term-tree bound;
- novelty of Pixley interpolation, Shannon counting, Lupanov local coding, Gray codes, recursive Shannon expansion, layered scheduling, or generic linear depth;
- the same count or bounds for every quasi-primal algebra or every incomplete clone;
- Lean extraction of a serialized materialized DAG or verification of the integrated compiler, a complete external independent proof review, or peer review;
- publication novelty over Russian, Chinese, or international closed-class complexity literature;
- use of, conclusions about, or limitations of Tau private work;
- rights under the unsigned Tau developer license; or
- patent freedom to operate.

Any commercial implementation, patent filing, categorical novelty statement, or claim-adjacent Tau integration requires separate legal/license review and a current prior-art search.

## 10. Remaining and quarantined work

The mathematical next steps are:

1. independently reconstruct the complete parallel-vector compiler, including
   the selector table, global anchor, two-plane bridge, binary branch, finite
   fallback, decoder, and outer glue, rather than importing frozen premises;
2. extract or serialize the recurrence-certified program-vector DAG and
   formalize the residual schedule and integrated original-signature theorem
   in Lean;
3. determine whether Lupanov's delayed-circuit model, Orlov--Lupanov,
   Kochergin, multiplexer, universal-circuit,
   or closed-class results already subsume the exact fixed-signature
   conjunction;
4. determine the optimal additive term between the counting lower bound and
   the conditional `r+O(log r)` upper bound;
5. determine ordinary-tree complexity and basis-sensitive leading-size
   constants; and
6. classify fixed finite clones for which parameter-free local coding gives
   the same order closure.

Boolean-plane R9 remains Theorem 6.6 and a fully visible historical stage. The
exact signed family and `7q` E/G materialization are independently audited and
Lean-checked. The compiler ledger has an independent conditional pass, but the
complete `r+O(log r)` composition has not been independently reconstructed
without its frozen premises. Novelty, formal integration, practical value,
and FTO remain quarantined.

Negative knowledge also remains active: naive ordinary-monotone two-extreme
reasoning is false for d's antitone middle input; residual-last growing-router
chunking breaks the size ledger; sequential `Theta(qw)` program generation
loses the target order; and reserving only one logarithm can make the local
library exceed the claimed bound. Solver timeouts, bounded `NO_HIT` results,
and grammar-specific UNSAT results are not upper bounds, lower bounds, or
optimality evidence.

## 11. Reproducibility map

The mathematical source notes for this version are:

- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_ENUMERATION.md`;
- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_SHANNON_COMPLEXITY.md`;
- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_LINEAR_DEPTH.md`;
- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_SUBCUBE_DEPTH.md`;
- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_GLOBAL_ANCHOR_DEPTH.md`;
- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_PROGRAMMABLE_DEPTH.md`;
- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_BOOLEAN_R9_DEPTH.md`; and
- `notes/QUASIPRIMAL_CONSERVATIVE_TERM_PARALLEL_PROGRAM_DEPTH.md`.

The frozen theorem, audit, and prior-art packets for the new stages are:

- `research/tournaments/2026-08-13-semantic-router-frontier/STATE.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/REPORT.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/audits/strong_family/REPORT.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/audits/variable_compiler/REPORT.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/audits/variable_compiler/PRIOR_ART.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/REPORT.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/REPORT.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/classical_depth_transfer/REPORT.md`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/REPORT.md`; and
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/REPORT.md`; and
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/REPORT.md`.

The implementation and deterministic checkers are:

- `src/orbitsynthesis/orbit_term_compile_local.py`;
- `experiments/quasiprimal_conservative_term_count.py`;
- `experiments/quasiprimal_local_coding_compiler.py`;
- `experiments/quasiprimal_layered_local_coding_compiler.py`;
- `experiments/quasiprimal_subcube_local_coding_compiler.py`;
- `experiments/quasiprimal_global_anchor_routing.py`;
- `experiments/quasiprimal_programmable_projection_routing.py`; and
- `experiments/quasiprimal_boolean_r9_routing.py`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/fused/check_strong_router_family.py`;
- `research/tournaments/2026-08-13-semantic-router-frontier/audits/strong_family/audit_strong_family.py`;
- `research/tournaments/2026-08-13-semantic-router-frontier/audits/variable_compiler/check_variable_compiler.py`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/program_vector/check_parallel_program_vector.py`;
- `research/tournaments/2026-08-13-semantic-router-frontier/audits/program_vector/audit_program_vector.py`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/classical_depth_transfer/check_transfer_barriers.py`;
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean`; and
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean`; and
- `research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean`.

The twelve semantic JSON receipts listed in Section 7 are the bounded-evidence
authority for numerical claims. The three Lean checkpoint receipts bind the
formal sources and toolchain; they do not carry the asymptotic compiler claim.
The exact program-vector replay commands and frozen hashes are in
`lanes/program_vector/manifest.json`; the independent family commands and
hashes are in `audits/strong_family/audit_manifest.json`. The source ledger is
`research/SOURCES.md`; the provenance/legal separation is
`research/IP_BOUNDARY.md`; and the current status map is
`research/RESEARCH_MAP_2026_08_13.md`.

Reproduction must preserve both the normal Python run and the optimized `python -O` run and require equal semantic hashes. A passing receipt validates only the finite scope named in that receipt.

## 12. Living-draft update contract

This file is intended to evolve with the mathematics under the following contract.

1. **Source freeze.** Every revision records its date and is derived from named manuscript notes, source-ledger entries, and checked receipts. Unlogged scratch results do not alter theorem statements.
2. **Status separation.** Use exactly distinguishable labels for manuscript theorem, bounded computational result, conjecture, refuted branch, timeout/`UNKNOWN`, and literature inference. Never promote one category by prose alone.
3. **Coupled update.** A stronger bound requires a simultaneous update to the abstract, formal theorem statement, proof, compiler description, finite comparison, receipt table, prior-art boundary, and explicit nonclaims. Partial headline upgrades are prohibited.
4. **Same-DAG discipline.** A size/depth claim must identify whether both bounds hold on one DAG. Combining the size of one compiler with the depth of another is not allowed.
5. **Cost-model discipline.** State whether nodes include inputs and whether inputs have depth zero or one. Analytic and executable conventions must never be silently mixed.
6. **Fail-closed receipts.** Normal and optimized semantic hashes must agree. Mutation controls remain part of the evidence. A timeout, solver `UNKNOWN`, missing dependency, or failed replay leaves the claim unpromoted.
7. **Generic-proof boundary.** Bounded enumeration and solver results validate instances only. An all-`r` theorem requires a written generic proof and, when available, independent or formal review.
8. **Negative knowledge.** Preserve failed constructions, counterexamples, invalid encodings, and corrected solver bugs in their source notes or receipts. Do not rewrite them as if they never occurred.
9. **Literature synchronization.** Every material theorem improvement triggers a focused Russian/international and native Chinese search. Search non-detection remains weak negative evidence, never proof of novelty.
10. **Provenance and legal separation.** Do not import Tau-private information or unsigned-license assumptions. Keep mathematical novelty, legal/FTO status, and Tau relationship as separate labels.
11. **Future-router quarantine.** Do not strengthen the programmable-projection or compiler depth bound without the same coupled theorem, proof, evidence, audit, and prior-art gates used through Theorem 6.10.
12. **Changelog.** Append a dated entry summarizing theorem, evidence, and boundary changes. Do not erase superseded bounds; mark them as historical compiler stages.

### Changelog

- **2026-08-13:** Initial living draft assembled from the exact-census, Shannon-size, layered-depth, recursive-subcube, and global-anchor manuscript notes and their five deterministic receipts. Current manuscript interval: `[1,3]`. Programmable-projection improvements remain quarantined.
- **2026-08-13:** Added the independently audited R6/R7 programmable-routing manuscript theorem and sixth receipt. Its same-DAG depth ceiling is `(3*log_6(3))*r+O(r/log r)`, narrowing the then-current coefficient interval to approximately `[1,1.839441578296]`. Novelty, optimality, formal verification, practical performance, and FTO remain unresolved.
- **2026-08-13:** Added the independently audited Boolean-R9 two-plane theorem and seventh receipt. The historical R6 ceiling remains `(3*log_6(3))*r+O(r/log r)`, while the then-current same-DAG ceiling became `(3/2)r+O(r/log r)`. The dual-rail idea is treated as classical adjacency; exact fixed-`Q` novelty, R9 optimality, formal verification, practical performance, and FTO remain unresolved.
- **2026-08-13:** Preserved R9 as a historical stage and added the exact signed `P_h/N_h` family, its independent audit and Lean proof, the repaired conditional `r+O(sqrt(r))` compiler, and the exact balanced E/G program vector. The current `O(3^r/r)` / `r+O(log r)` same-DAG bound is explicitly conditional on the named upstream compiler lemmas and awaits independent end-to-end audit; only the E/G semantics, not the charged `7q` circuit or integrated compiler, are Lean-checked. Logical binary programs are address-only, while physical `x_0,u(x_0)` controls are correctly recorded as payload-relative. Novelty, FTO, unsigned-license rights, practical performance, and an optimal additive term remain unresolved.
- **2026-08-13:** Added an independent no-author-import audit of the exact program vector and conditional compiler ledger, plus a trust-zero Lean proof of the balanced recurrence, original-signature legality, `7q` shared-DAG bound including both names, and logarithmic depth. A primary-source Gashkov transfer audit found that the classical Boolean formula construction does not directly preserve this paper's fixed-Q same-DAG size/depth target; native Q-valued adaptation and Lupanov's separate delayed-circuit model remain open. The all-arity compiler is still conditional on frozen integration premises, and novelty, FTO, license rights, practical performance, and an optimal additive term remain unresolved.
- **2026-08-13:** Repaired the manuscript after a fresh-room internal-agent referee pass: the abstract now labels the upper interval itself conditional; Theorem 6.9 states the `A=2` and multi-output shared-DAG scopes; the exact three-node glue is displayed; and Conditional Theorem 6.10 is an explicit implication from propositions (I1)--(I7), with an inclusive nonbinary ledger and finite fallback. The post-repair mathematical/text gate passes. Archival deposit remains forbidden until human authorship metadata is approved; this internal review is not external peer review.

## References

1. A. F. Pixley, “Functionally Complete Algebras Generating Distributive and Permutable Classes,” *Mathematische Zeitschrift* 114 (1970), 361--372. <https://eudml.org/doc/171324>
2. A. F. Pixley, “The Ternary Discriminator Function in Universal Algebra,” *Mathematische Annalen* 191 (1971), 167--180. <https://eudml.org/doc/162131>
3. K. A. Baker and A. F. Pixley, “Polynomial Interpolation and the Chinese Remainder Theorem for Algebraic Systems,” *Mathematische Zeitschrift* 143 (1975), 165--174. <https://eudml.org/doc/172222>
4. R. W. Quackenbusch, “Demi-Semi-Primal Algebras and Mal'cev-Type Conditions,” *Mathematische Zeitschrift* 122 (1971), 166--176. <https://eudml.org/doc/171592>
5. C. E. Shannon, “The Synthesis of Two-Terminal Switching Circuits,” *Bell System Technical Journal* 28 (1949). <https://www.nokia.com/bell-labs/publications-and-media/publications/the-synthesis-of-two-terminal-switching-circuits/>
6. O. B. Lupanov, “On the Principle of Local Coding and the Realization of Functions in a Certain Class of Networks Composed of Functional Elements,” *Doklady Akademii Nauk SSSR* 140(2) (1961), 322--325. <https://www.mathnet.ru/eng/dan25510>
7. S. V. Yablonskii, “Functional Constructions in a k-Valued Logic,” *Trudy Matematicheskogo Instituta imeni V. A. Steklova* 51 (1958), 5--142. <https://www.mathnet.ru/eng/tm1275>
8. V. A. Orlov, “Complexity of Implementing Functions of k-Valued Logic by Circuits and Formulas in Functionally Complete Bases,” *Discrete Applied Mathematics* 135(1--3) (2004), 223--233. <https://doi.org/10.1016/S0166-218X(02)00306-2>
9. A. V. Kochergin, “On the Depth of k-Valued Logic Functions Over Arbitrary Bases,” *Journal of Mathematical Sciences* 233(1) (2018), 100--102. <https://doi.org/10.1007/s10958-018-3927-5>
10. R. F. Safin, “On a Relation Between Depth and Complexity in Precomplete Classes of k-Valued Logic,” *Mathematical Problems of Cybernetics* 13 (2004), 223--278 [Russian]. <https://keldysh.ru/papers/2004/mvk/mvk2004_223.pdf>
11. S. A. Lozhkin, “On Synthesis of Formulas Whose Complexity and Depth Do Not Exceed Asymptotically Best Estimates of High Accuracy,” *Moscow University Mathematics Bulletin* 62(3) (2007), 93--100. <https://www.mathnet.ru/eng/vmumm1048>
12. S. A. Lozhkin, “On the Depth of a Multiplexer Function with a Small Number of Select Lines,” *Mathematical Notes* 115(5) (2024), 748--754. <https://www.mathnet.ru/eng/mzm14190>
13. A. D. Korshunov, “Computational Complexity of Boolean Functions,” *Russian Mathematical Surveys* 67(1) (2012), 93--165. <https://www.mathnet.ru/eng/rm9459>
14. E. Lehtonen and A. Szendrei, “Equivalence of Operations with Respect to Discriminator Clones,” *Discrete Mathematics* 309 (2009), 673--685. <https://arxiv.org/abs/0706.0195>
15. 吴训威 and 陈偕雄, “具有三轨输出的三值触发器及其在三值时序电路中的应用,” *中国科学 A辑* 1985(7), 643--653. <https://www.sciengine.com/doi/pdf/39cfd4607c82435d895d35165b3b28c0>
16. 徐明强, 管致锦, and 张海豹, “基于最小混乱度的三值可逆逻辑综合算法,” *电子学报* 41(7) (2013), 1352--1357. <https://sns.wanfangdata.com.cn/sns/perio/dianzixb/?isSync=0&issueNum=07&page=2&publishYear=2013&tabId=article>
17. P. B. Tarasov, “Uniformity of Certain Systems of Functions of Many-Valued Logic,” *Moscow University Mathematics Bulletin* 68(2) (2013), 99--102. <https://m.mathnet.ru/eng/vmumm398>
18. P. B. Tarasov, “Several Conditions for Uniformity of a Finite System of Many-Valued Logic,” *Uchenye Zapiski Kazanskogo Universiteta. Seriya Fiziko-Matematicheskie Nauki* 156(3) (2014), 123--131. <https://www.mathnet.ru/eng/uzku1272>
19. N. Ishiura, “Synthesis of Multilevel Logic Circuits from Binary Decision Diagrams,” *IEICE Transactions on Information* E76-D(9) (1993), 1085--1092. <https://globals.ieice.org/en_transactions/information/10.1587/e76-d_9_1085/_p>
20. J. Backes, *Algorithms and Data Structures for Logic Synthesis and Verification*, Ph.D. dissertation, University of Minnesota (2013), dual-rail ternary encoding discussion. <https://loonwerks.com/publications/pdf/backes2013phd.pdf>
21. L. G. Valiant, “Universal Circuits (Preliminary Report),” *Proceedings of STOC 1976*, 196--203. <https://doi.org/10.1145/800113.803649>
22. S. A. Cook and H. J. Hoover, “A Depth-Universal Circuit,” *SIAM Journal on Computing* 14(4) (1985), 833--839. <https://doi.org/10.1137/0214058>
23. J. Holmgren and R. Rothblum, “Linear-Size Boolean Circuits for Multiselection,” *CCC 2024*, 11:1--11:20. <https://doi.org/10.4230/LIPIcs.CCC.2024.11>
24. W. F. McColl and M. S. Paterson, “The Depth of All Boolean Functions,” *SIAM Journal on Computing* 6(2) (1977), 373--380. <https://doi.org/10.1137/0206026>
25. 张会红, 陈治文, and 汪鹏君, “二叉决策图映射电路的面积和延时优化,” *电子与信息学报* 41(3) (2019), 725--731. <https://doi.org/10.11999/JEIT180443>
26. 何新华, 宫云战, and 魏道政, “面向多输出电路的BDD拼接构造,” *电子与信息学报* 19(3) (1997), 356--360. <https://jeit.ac.cn/article/id/85665992-ae08-49a4-83ca-1381a6d4735f>
27. V. A. Orlov, “Realization of k-Valued Functions by Circuits of Functional Elements,” *Mathematical Notes* 64 (1998), 371--376. <https://doi.org/10.1007/BF02314847>
28. S. B. Gashkov, “On the Depth of Boolean Functions,” *Problemy Kibernetiki* 34 (1978), 265--268 [Russian]. <https://publ.lib.ru/ARCHIVES/P/%27%27Problemy_kibernetiki%27%27_%28seriya%29/%cf%f0%ee%e1%eb%e5%ec%fb%20%ea%e8%e1%e5%f0%ed%e5%f2%e8%ea%e8.%20%c2%fb%ef%f3%f1%ea%2034.(1978).pdf>

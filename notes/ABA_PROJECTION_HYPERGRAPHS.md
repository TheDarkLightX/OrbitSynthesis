# ABA projection fibers as multipartite hypergraphs

**Status:** DERIVED paper proof; finite checks for small cases completed separately; Lean pending.

This is the multi-block generalization of `ABA_OCLTL_FIBERS.md` and `ABA_GROUP_TESTING.md`.

## 1. Split the variables into blocks

Partition the Boolean-algebra variables into `b` disjoint blocks of sizes

`k_1,...,k_b`.

For block `i`, fix a complete ABA `k_i`-type with minterm support

`R_i subseteq {0,1}^{k_i}`

and write

`r_i = |R_i| >= 1`.

A complete type on all `k_1+...+k_b` variables has a fine support

`S subseteq R_1 x ... x R_b`.

Its restriction to block `i` is exactly the prescribed type iff the coordinate projection of `S` onto `R_i` is all of `R_i`.

Therefore the projection fiber is precisely

`F(R_1,...,R_b) = { S subseteq product_i R_i : pi_i(S)=R_i for every i }`.

## 2. Hypergraph interpretation

Regard the sets `R_i` as vertex parts of a `b`-partite `b`-uniform hypergraph. A fine minterm cell

`(v_1,...,v_b) in R_1 x ... x R_b`

is one possible hyperedge.

Then a support `S` in the projection fiber is exactly a spanning multipartite hypergraph with **no isolated vertex**.

This is the inner combinatorial object behind ABA type restriction.

For `b=2`, the supports are bipartite graphs with no isolated vertices; the ocLTL `(m,x)` versus `y` calculation is the case `r_1 in {1,2,3,4}` and `r_2 in {1,2}`.

## 3. Exact fiber cardinality

Let

`F(r_1,...,r_b)`

be the number of subsets of the complete multipartite edge set whose projection onto every part is surjective.

By inclusion-exclusion over isolated vertices,

`F(r_1,...,r_b)
 = sum_{a_1=0}^{r_1} ... sum_{a_b=0}^{r_b}
   (-1)^(a_1+...+a_b)
   * product_i binom(r_i,a_i)
   * 2^( product_i (r_i-a_i) ).`

### Proof

For every vertex, let `E_v` be the event that the vertex is isolated. If `a_i` vertices are forced isolated in part `i`, then only

`product_i (r_i-a_i)`

possible hyperedges remain, and any subset of them may be chosen. There are

`product_i binom(r_i,a_i)`

ways to choose the isolated vertices. Inclusion-exclusion gives the formula.

### Bipartite form

For two parts of sizes `r,c`, summing over one side first gives the equivalent formula

`F(r,c)=sum_{j=0}^c (-1)^j binom(c,j) (2^(c-j)-1)^r.`

For `c=2`,

`F(r,2)=3^r-2`,

recovering the ocLTL fiber formula.

## 4. Exact atomic-predicate complexity of every projection fiber

Let the possible fine cells be

`U = R_1 x ... x R_b`,

so

`|U| = N = product_i r_i`.

Atomic ABA equation tests are intersection queries on `U` by `ABA_GROUP_TESTING.md`.

### Degenerate case

If at most one `r_i` exceeds 1, then the projection fiber contains exactly one support.

Reason: every vertex of the only nontrivial part must appear, while all other coordinates are forced. Hence every possible edge is required.

So zero tests are needed inside such a fiber.

### Nondegenerate case

Assume at least two of the `r_i` are greater than 1.

Then for every vertex in every part, its degree in the complete multipartite hypergraph is at least 2. Therefore deleting any single hyperedge leaves every vertex incident to at least one edge.

Hence the projection fiber contains

`U`

and

`U \ {e}`

for every fine cell/hyperedge `e in U`.

By the co-atom obstruction from `ABA_GROUP_TESTING.md`, every exact atomic identification procedure—adaptive or non-adaptive—must query every singleton hyperedge.

Therefore:

`AtomicGT(F(R_1,...,R_b)) = product_i r_i`

whenever at least two block supports have size greater than 1.

Singleton fine-minterm tests attain this bound.

## 5. Dichotomy theorem

For every ABA projection fiber determined by block-support sizes `r_1,...,r_b`:

- if at most one `r_i>1`, the fiber is a singleton and requires **0** atomic tests;
- if at least two `r_i>1`, exact identification requires **all `product_i r_i` fine-cell singleton tests**.

There is no intermediate atomic-test count for full identification of a projection fiber.

This is considerably stronger than the information-theoretic lower bound.

## 6. Arbitrary definable predicates versus atomic equations

Because ABA is omega-categorical and has quantifier elimination, every subset of the finite complete-type fiber is definable by some formula. Thus unrestricted definable predicate bits can encode the fiber using exactly

`ceil(log2 F(r_1,...,r_b))`

bits in principle.

Atomic equations, by contrast, need

`product_i r_i`

bits in every nondegenerate fiber.

So the exact syntactic expressiveness gap is

`product_i r_i - ceil(log2 F(r_1,...,r_b))`.

For two parts `(r,2)`, this compares

`2r`

with

`ceil(log2(3^r-2))`.

As `r -> infinity`, the multiplicative overhead tends to

`2 / log2(3) ~= 1.26186`.

For larger balanced parts, almost every sufficiently dense random support has no isolated vertex, so the fiber occupies a much larger fraction of the full powerset and the information gap becomes smaller; this asymptotic statement should be proved quantitatively before being promoted beyond intuition.

## 7. Consequence for synthesis representations

Projection information is powerful semantically—it can collapse an enormous global type space to one fiber—but **it does not buy worst-case full-type compression if the only added observations are atomic BA equations**.

That suggests a change in objective:

> do not try to recover the complete fine type using a small set of atomic predicates; instead compute the synthesis/fixed-point operation directly on families of fine supports or on a richer symbolic representation.

This supports the direct fixed-point research line rather than an atomic type-encoding strategy.

## 8. Generalization target

For a synthesis construction, full identification may be unnecessary. Let `~_Phi` identify two supports when they induce the same predecessor/fixed-point behavior for a particular operator `Phi`.

The next mathematically meaningful question is not whether arbitrary complete types can be compressed atomically—they cannot in the nondegenerate fibers above—but:

> Which behaviorally sufficient partitions of these hypergraph fibers are preserved by the synthesis operators, and what representation computes those partitions without enumerating every edge support?

This question is deliberately weaker than a global Myhill-Nerode minimality claim.

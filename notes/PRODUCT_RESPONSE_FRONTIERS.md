# Product laws for positive response frontiers

**Status:** DERIVED finite-order theorem. This explains how fragment-relative response branching scales under product structures and how coordinate symmetry can convert exponential product width into polynomial histogram width.

This note builds on `POSITIVE_RESPONSE_FRONTIER.md`.

## 1. Independent product setup

For coordinates `i=1,...,d`, let

- `E_i` be a finite response fiber;
- `Delta_i` be a finite positive predicate family;
- `S_i={sigma_i(e_i):e_i in E_i}` be the realized positive signature family;
- `F_i=Max_subset(S_i)` be its maximal-signature frontier;
- `w_i=|F_i|`.

Assume the global positive predicate universe is the **disjoint union**

`Delta = Delta_1 disjoint-union ... disjoint-union Delta_d`

and the product response fiber is

`E=E_1 x ... x E_d`.

A product response has signature

`sigma(e_1,...,e_d)=sigma_1(e_1) union ... union sigma_d(e_d)`,

with each coordinate signature living in its disjoint Delta_i block.

This is the exact situation for coordinate-local observations/constraints over an independent product structure.

## 2. Maximal signatures factor coordinatewise

### Theorem 1 — product frontier theorem

The maximal global signatures are exactly products of maximal coordinate signatures:

`Front_Delta(E)
 = { f_1 union ... union f_d : f_i in F_i for every i }`.

### Proof

If a coordinate signature `s_i` is not maximal, choose a realized `t_i` with

`s_i proper-subset t_i`.

Replacing only coordinate i strictly enlarges the global signature because the Delta_i blocks are disjoint. Hence a globally maximal signature must use a maximal coordinate signature everywhere.

Conversely, suppose all coordinates are maximal and a realized global signature t contains

`f_1 union ... union f_d`.

Restriction to each disjoint coordinate predicate block gives

`f_i subseteq t_i`.

Maximality of f_i forces `f_i=t_i` for every i. Hence the global signature is maximal.

## 3. Width multiplicativity

### Corollary 2

`w_Delta(E)=product_i w_i`.

In particular:

- if every coordinate has a dominant response (`w_i=1`), the product has a dominant response;
- if every coordinate has the same width w, raw product width is `w^d`.

Thus dominant-response collapse is stable under finite independent products, but even small unresolved response choice can multiply exponentially with packed dimension.

## 4. Relation to ocLTL product constructions

Asor's product-structure reduction packs multiple streams / bounded lookback coordinates into finite products.

The theorem here does **not** say every packed specification factors: cross-coordinate predicates can couple the product and destroy independence.

It does say:

> when the selected positive observation fragment and legal response constraints factor coordinatewise, positive response width multiplies exactly.

This gives a precise baseline against which cross-coordinate coupling can be measured.

## 5. Symmetric identical coordinates

Assume now all d coordinates have the same frontier

`F={f_1,...,f_w}`

of size w, and the specification/objective is invariant under permuting the d coordinates.

Before symmetry quotient there are

`w^d`

frontier tuples.

The diagonal action of `S_d` permutes coordinate positions. Two frontier tuples lie in the same orbit iff each frontier label `f_j` occurs the same number of times.

Thus an orbit is determined by a histogram

`(n_1,...,n_w)`

with

`n_j>=0`, `sum_j n_j=d`.

### Theorem 3 — symmetric frontier orbit count

The number of response-frontier orbits is

`binom(d+w-1,w-1)`.

### Proof

This is the number of weak compositions of d into w parts (stars and bars).

## 6. Exponential-to-polynomial collapse

For fixed local width w:

- explicit product frontier: `w^d`;
- symmetric quotient frontier: `binom(d+w-1,w-1)=Theta(d^(w-1))`.

Examples:

### w=1

One dominant local response gives one global response orbit.

### w=2

`2^d` explicit product choices collapse to

`d+1`

orbits, indexed only by how many coordinates use frontier response 1.

### w=3

`3^d` choices collapse to

`binom(d+2,2)`.

This is the same combinatorial mechanism behind the earlier ABA histogram quotient, now stated at the abstract response-frontier level.

## 7. Partial symmetry

Suppose coordinates split into symmetry blocks of sizes

`d_1,...,d_r`

with block j having local response width `w_j` and full permutation symmetry inside that block.

Then the quotient response-frontier count is

`product_j binom(d_j+w_j-1,w_j-1)`.

So replicated subsystem architectures can remain tractable even when the full product is not globally symmetric.

## 8. Different local widths

For non-identical coordinates, exact orbit counting depends on which coordinates are isomorphic under the specification's symmetry group.

Group coordinates by identical local frontier/action structure. Apply the histogram formula independently to each orbit class of coordinates.

This suggests a compiler architecture:

1. compute local positive response frontiers;
2. construct the coordinate dependency/coupling graph;
3. detect automorphisms among uncoupled/identical coordinates;
4. quotient product frontiers by the detected permutation group before building the reactive game.

## 9. Cross-coordinate coupling parameter

If global response feasibility does not factor, the product theorem fails.

A useful next parameter is the interaction hypergraph on coordinates:

- vertices = product coordinates;
- a hyperedge joins coordinates appearing together in one feasibility/positive predicate.

Questions:

- bounded component size: frontier factors over components;
- bounded treewidth: use dynamic programming over local frontier states;
- full permutation symmetry: quotient components by orbit histograms;
- affine/XOR coupling: use linear-algebra backend instead of frontier enumeration.

This connects response-frontier synthesis to `SOURCE_LEVEL_SYMBOLIC_GAME.md` and the structure-aware backend program.

## 10. Examples from standard structures

### Equality, positive equalities

One coordinate with b existing equality classes has width b. d independent coordinates therefore have raw width

`b^d`.

Under complete coordinate symmetry, only

`binom(d+b-1,b-1)`

frontier orbits remain.

### DLO, mixed left/right positive inequalities

One coordinate over k ordered parameters has width `k+1`. d independent coordinates have raw width `(k+1)^d`; full coordinate symmetry reduces this to

`binom(d+k,k)`.

### Rado graph with r contradictory-polarity positions

Local width is `2^r`. Product dimension d gives `2^(rd)` raw frontier choices. Symmetry across product coordinates gives

`binom(d+2^r-1,2^r-1)`.

### Dominant fragments

ABA support-positive fibers and one-polarity Rado/equality/DLO fragments have local width 1, so arbitrary independent products remain width 1 without needing symmetry.

## 11. Research consequence

The correct product-complexity invariant is not just the complete type count of `M^d`.

It is a combination of:

- local positive response frontier width;
- interaction/coupling structure;
- coordinate symmetry group.

This gives a reusable route from model-theoretic type fibers to parameterized reactive synthesis algorithms.

## 12. Next targets

1. Prove tree-decomposition dynamic programming bounds for bounded interaction width using local response-frontier states.
2. Extend the symmetry quotient from full S_d to arbitrary permutation groups using cycle/orbit methods.
3. Measure frontier widths/coupling graphs on real packed Tau specifications.
4. Determine whether response frontier width composes cleanly with bounded lookback memory windows.
5. Relate local frontier width to polymorphism/forbidden-pattern parameters of homogeneous structures.

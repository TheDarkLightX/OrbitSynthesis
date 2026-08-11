# Symmetry quotient for permutation-invariant packed ABA games

**Status:** DERIVED finite-group quotient theorem specialized to the ABA cell arena. Symmetry reduction of finite games is classical; the specific histogram counts and their use as a Tau/ABA backend regime are the candidate contribution. Implementation pending.

This note applies the symmetry-reduction tactic explicitly.

For d packed BA coordinates, the unsymmetrized cell arena from `ABA_CELL_GAME.md` has widths

`2^d`, `2^(2d)`, `2^(3d)`

in the common packed case with d state, d input, and d next/output coordinates.

If the specification treats the d coordinate positions symmetrically, the diagonal action of the symmetric group `S_d` collapses these cell sets to polynomially many orbit types.

## 1. Diagonal coordinate action

Write a state cell as a bit-vector

`x=(x_1,...,x_d) in {0,1}^d`.

For `g in S_d`, act by permuting coordinate positions:

`(g.x)_j = x_(g^{-1}(j))`.

On a partial cell `(x,i)` and full cell `(x,i,y)`, apply the **same** coordinate permutation simultaneously to every block.

The cell projections

`state:P->V`,

`partial:U->P`,

`next:U->V`

are equivariant under this diagonal action.

## 2. Invariant specification assumption

Assume the cell masks produced by the specification are invariant:

- Step forbidden mask Z_T is a union of S_d-orbits in U;
- Safe forbidden mask Z_S is a union of S_d-orbits in V;
- every Step positive obligation is an invariant union of U-orbits;
- every Safe positive obligation is an invariant union of V-orbits.

This holds, for example, when the source formula is invariant under simultaneous renaming of the d packed coordinate positions.

The condition can be tested syntactically when the symmetry is declared or semantically on the compiled cell masks.

## 3. Orbit counts are weak compositions

### State cells

Two bit-vectors in `{0,1}^d` are in the same S_d orbit iff they have the same Hamming weight.

Therefore

`|V/S_d| = d+1`.

Orbit label: number of 1 coordinates.

### Partial cells

At each coordinate j, the pair `(x_j,i_j)` is one of four patterns

`00,01,10,11`.

A diagonal S_d orbit is determined exactly by the histogram

`(n_00,n_01,n_10,n_11)`

of those four patterns, with nonnegative entries summing to d.

Hence

`|P/S_d| = binom(d+3,3)`.

### Full cells

At each coordinate j, the triple `(x_j,i_j,y_j)` is one of eight patterns in `{0,1}^3`.

An orbit is determined by the eight-pattern histogram

`(n_000,...,n_111)`,

nonnegative and summing to d.

Thus

`|U/S_d| = binom(d+7,7)`.

These are the standard stars-and-bars counts of weak compositions.

## 4. Projections descend to histogram marginals

The quotient cell projections are explicit marginalization maps.

For a full histogram `n_(a,b,c)`:

- partial histogram:

  `m_(a,b)=sum_c n_(a,b,c)`;

- next-state Hamming weight:

  `w_next=sum_(a,b,c) c*n_(a,b,c)`;

- current-state Hamming weight:

  `w_state=sum_(a,b,c) a*n_(a,b,c)`.

For a partial histogram `m_(a,b)`:

`w_state=sum_(a,b) a*m_(a,b)`.

No representative bit-vectors are needed to compute the quotient maps.

## 5. Exact quotient-game theorem

Let brackets `[v]`, `[p]`, `[u]` denote group orbits.

Because the projections are equivariant, they induce well-defined maps

`state_bar : P/G -> V/G`,

`partial_bar : U/G -> P/G`,

`next_bar : U/G -> V/G`.

Invariant forbidden/positive masks descend to subsets of the orbit sets.

### Theorem 1 — predecessor commutes with quotient

For every invariant target set `A subseteq V`,

`Pre(A)` is invariant, and

`[v] in Pre(A)/G`

iff

for every partial orbit `[p]` with

`state_bar([p])=[v]`,

there exists an Allowed full orbit `[u]` with

`partial_bar([u])=[p]`

and

`next_bar([u]) in A/G`.

### Proof

Invariance of Step makes Allowed a union of full orbits. Equivariance gives invariance of the predecessor.

For exactness, suppose a full orbit [u] maps to partial orbit [p]. Pick any concrete p' in [p]. Starting from a representative u with partial(u)=p, choose g carrying p to p'. Then gu lies in the same full orbit, is still Allowed, and lies over p'. Thus existence of an allowed full-orbit transition is uniform across every representative of the partial orbit.

The same argument handles all representatives of a state orbit.

Therefore the ordinary finite safety predecessor can be computed entirely on orbit nodes.

## 6. Zero safety becomes polynomial-size in d

Instead of a state arena of `2^d` cells and full incidence universe `2^(3d)`, the quotient has

`d+1`

state nodes,

`binom(d+3,3)`

partial nodes, and

`binom(d+7,7)`

full nodes.

For fixed three-block arity, these are polynomial in d; the full-node count has degree 7.

The queue/counter safety attractor from `ABA_CELL_GAME_ALGORITHMS.md` therefore runs on a polynomial-size explicit quotient arena **once invariant orbit membership of Step/Safe is available**.

This is an exponential-to-polynomial collapse in the cell dimension for the symmetric regime.

## 7. Positive obligations also remain invariant

Let G be an invariant state-cell target.

The cell predecessor `barL(G)` is invariant by equivariance.

Likewise every invariant Step seed transforms to an invariant robust-witness set.

Therefore the entire Bekić positive phase stays inside subsets of

`V/S_d`,

which has only d+1 orbit nodes.

The target-mask universe for invariant obligations has size

`2^(d+1)`

rather than

`2^(2^d)`

possible arbitrary cell masks.

This does not make every symmetric positive fixed point polynomial-time—monotone dynamics on d+1 quotient bits can still have exponential orbit behavior—but it removes one exponential layer.

## 8. Invariant masks are histogram predicates

An invariant state-cell set is simply a set of Hamming weights

`W subseteq {0,...,d}`.

An invariant partial/full set is a set of histogram vectors.

Thus a support backend need not materialize bit masks of width `2^d` / `2^(3d)` in this regime. It can store:

- bitsets over d+1 state weights;
- indexed sets/bitsets of four-way histograms;
- indexed sets/bitsets of eight-way histograms.

This is especially attractive for repeated replicated resources/agents/streams governed by one symmetric specification template.

## 9. Concrete complete supports need not themselves be invariant

Important limitation:

the theorem says the **game masks and winning predicates** are unions of cell orbits. An actual complete ABA state type is an arbitrary nonempty subset of the `2^d` concrete Venn cells and need not be fixed by S_d.

Winning membership nevertheless depends on it through the invariant masks:

- zero condition: no active concrete cell may belong to a forbidden orbit;
- positive condition: the support must contain at least one concrete cell from each required invariant orbit union.

Do not confuse quotienting the invariant cell game with quotienting every complete type to a mere Hamming-weight set.

## 10. Strategy equivariance

The maximal-support response construction is equivariant:

if a concrete partial support is permuted by g, the set of all allowed safe full refinements is permuted by the same g.

Thus the type-level strategy commutes with the declared coordinate symmetry.

This is desirable for both implementation sharing and explanatory synthesis.

## 11. More general symmetry groups

Nothing in Theorem 1 requires the full symmetric group.

Let a finite group G act compatibly on state/input/next cells, with:

- equivariant projections;
- invariant Step/Safe masks.

Then the cell game descends to the G-orbit quotient.

The full S_d case is valuable because its orbits have a closed-form histogram representation.

For a subgroup induced by the actual specification automorphism group, use standard finite-group orbit algorithms.

## 12. Burnside/Pólya direction

For more complicated packed structures, orbit counts and representative enumeration can use Burnside's lemma / cycle indices rather than explicit cell enumeration.

In the S_d diagonal bit-block case, stars-and-bars is simpler and gives exact representatives immediately.

This is where classical combinatorial group action techniques can materially improve the Tau backend rather than merely beautify the proof.

## 13. Tau integration

Potential workflow:

1. detect or accept a declared coordinate permutation symmetry;
2. verify Step/Safe invariance syntactically or on symbolic terms;
3. construct histogram orbit nodes rather than concrete Venn cells;
4. compile term truth values on one histogram representative (invariance makes the value orbit-constant);
5. solve zero and positive cell dynamics on the quotient;
6. use equivariant witness reconstruction for concrete runtime values.

## 14. Next theorem/experiment targets

1. Implement histogram quotient construction and compare against full concrete cell games for small d.
2. Prove the cell-mask compiler evaluates symmetric BA terms directly on histogram counts without choosing full representatives for common formula templates.
3. Combine with interpreted constants and determine when constant regions preserve/break S_d symmetry.
4. Explore other groups: cyclic, block-permutation/wreath-product, graph automorphism groups of replicated components.
5. Measure whether real Tau specifications expose enough repeated-coordinate symmetry for this optimization to matter.

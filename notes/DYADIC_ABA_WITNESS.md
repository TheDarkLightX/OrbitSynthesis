# A concrete effective witness model: dyadic interval ABA

**Status:** DERIVED constructive reference model; Python implementation accompanies this note. This is not claimed as a new Boolean-algebra construction.

## 1. The Boolean algebra

Let B be the family of finite unions of half-open dyadic intervals in `[0,1)`:

`[m/2^D, (m+1)/2^D)`

for integers D>=0 and `0<=m<2^D`, allowing finite unions and arbitrary refinement to a common dyadic depth.

Under union, intersection, and complement relative to `[0,1)`, B is a countable Boolean algebra.

It is atomless: every nonzero element contains at least one nonempty dyadic interval, and that interval splits into its left and right dyadic halves, producing two strictly smaller nonzero elements.

This gives a convenient explicit presentation of the unique countable atomless Boolean algebra up to isomorphism.

## 2. Finite representation

At depth D, represent an element by a `2^D`-bit mask. Bit m denotes inclusion of

`[m/2^D,(m+1)/2^D)`.

Refinement from depth D to D+t replaces each active bit by `2^t` consecutive active bits.

Boolean operations are bitwise operations after refinement to a common depth.

The finite mask is only a representation at one grid; the algebra itself permits unbounded refinement and is therefore atomless.

## 3. Computing the complete support type of a tuple

Given k elements `a_1,...,a_k` represented on a common depth-D grid, each dyadic atom m has a valuation

`v(m) in {0,1}^k`

recording membership in every a_i.

The complete ABA support type is

`S={v(m): some dyadic atom m has valuation v(m)}`.

This is exactly the Venn-cell support representation of `ABA_TYPE_SPACE.md`.

## 4. Constructing an arbitrary compatible extension type

Suppose the current k-tuple has support S and we are given a target complete `(k+r)`-type S' whose restriction to the first k coordinates is S.

For every active coarse cell `v in S`, define

`R_v={u in {0,1}^r : (v,u) in S'}`.

Compatibility says every R_v is nonempty, and inactive coarse cells have no requested refinement.

Let

`M=max_v |R_v|`.

Choose

`t=ceil(log2 M)`

(with t=0 when M=1).

Refine the dyadic grid by t levels. Every old dyadic atom now contains `2^t >= M` smaller dyadic atoms.

For each active coarse Venn cell v:

1. enumerate its refined dyadic atoms deterministically from left to right;
2. assign the first `|R_v|` refined atoms to the distinct requested values `u in R_v` in lexicographic order;
3. assign all remaining refined atoms to the first requested u.

Then define each new BA element `y_j` as the union of all refined dyadic atoms assigned to a value u whose j-th bit is 1.

## Theorem 1 — exact realization

The tuple

`(a_1,...,a_k,y_1,...,y_r)`

constructed above has complete support exactly S'.

### Proof

Every refined atom stays inside its original coarse Venn cell, so no inactive coarse cell becomes active and the old tuple's type is preserved.

For an active coarse cell v:

- every requested u in R_v receives at least one nonempty dyadic atom;
- no unrequested u receives any atom.

Thus the nonzero fine Venn cells above v are exactly R_v. Doing this independently for every v yields S'.

## 5. Determinism and effectivity

The algorithm is deterministic after fixing:

- left-to-right dyadic atom order;
- lexicographic requested-refinement order;
- the rule sending leftovers to the first requested refinement.

All operations are finite bit operations. Therefore it gives an explicit computable witness for the extension property required in Asor's ocLTL effective-presentation assumption.

## 6. Maximal-support strategy specialization

For the clause safety strategy, the requested full type is

`Q_max(P)=all fine cells above P that are not forbidden`.

For every active partial cell v, the requested R_v is simply the set of all locally allowed output valuations.

The dyadic witness algorithm therefore realizes the direct safety strategy with no search over candidate complete types.

## 7. Refinement depth bound

If r BA output variables are added, there are at most `2^r` requested fine valuations above each active coarse cell. Hence

`M<=2^r`

and

`t<=r`.

So one strategy step needs at most r additional dyadic refinement levels beyond the common depth of the current tuple to realize **any** compatible complete extension type.

This is a useful constructive bound:

> adding r ABA coordinates never requires more than r dyadic grid refinements in this presentation.

The total number of represented dyadic atoms can still grow by up to `2^r` per old atom per step if representations are never compressed; implementation should canonicalize/merge adjacent intervals where possible.

## 8. Caveat for repeated reactive execution

If every time step permanently increases the grid depth, a naive concrete representation may grow with time even though the logical strategy is finite-state at the type level.

Possible mitigations:

1. merge adjacent dyadic intervals whenever they carry identical membership across all retained state components;
2. implement witnesses in Tau's native symbolic BA representation rather than literal interval grids;
3. use the dyadic model only as a correctness oracle, not the production runtime.

The reference model's purpose is to prove constructivity and provide executable differential tests.

## 9. Next tests

1. Implement type computation and compatible-extension realization.
2. Generate random tuples/types and verify exact target support.
3. Feed `Q_max` from the safety strategy into the witness constructor and verify Step/W support clauses concretely.
4. Test repeated execution and measure representation-depth growth.
5. Compare with Tau's actual effective witness mechanism once the relevant API is identified.

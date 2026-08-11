# A compact exponential lower bound from maximal-length LFSR dynamics

**Status:** DERIVED reduction using the classical existence/properties of primitive polynomials over GF(2). The finite-field/LFSR fact is standard; the result here is its embedding into the ABA support-clause safety fixed point. Small dimensions should be pinned by executable tests.

`ABA_MONOTONE_DYNAMICS_UNIVERSALITY.md` gives a Sperner-tight worst case as a function of the number N of state support cells, but its transition description may itself be huge.

This note gives a much more compact adversarial family:

> an O(d)-size pure-ABA safety specification whose ordinary positive fixed-point iteration and final canonical support-clause output require `2^d-1` distinct irredundant obligations.

## 1. Maximal-length linear recurrence

Fix `d>=1` and choose a primitive polynomial over GF(2)

`p(t)=t^d + a_(d-1)t^(d-1)+...+a_1 t+a_0`.

A primitive polynomial exists for every d, and `a_0=1`.

Let the companion linear map

`pi : {0,1}^d -> {0,1}^d`

be

`pi(x_0,...,x_(d-1))
 = (x_1,...,x_(d-1),
    a_0 x_0 XOR a_1 x_1 XOR ... XOR a_(d-1) x_(d-1)).`

Classical maximal-length LFSR theory gives:

1. `pi(0)=0`;
2. pi is invertible;
3. the `2^d-1` nonzero vectors form one cycle under pi.

Equivalently, the companion matrix has multiplicative order `2^d-1`.

## 2. Encode pi as a pure ABA Step

Use d BA state/memory variables

`x_0,...,x_(d-1)`

and d BA output/next variables

`y_0,...,y_(d-1)`.

Write the conjunction of equations

`y_j = x_(j+1)` for `0<=j<d-1`,

and

`y_(d-1)
 = XOR_{j:a_j=1} x_j`.

At every Boolean Venn cell/point, BA operations act as ordinary Boolean operations on the membership bits. Therefore the only full `(x,y)` minterm cells permitted by Step are those satisfying

`y=pi(x)`.

The next-cell relation is deterministic.

All d zero-equations can, if desired, be merged into one zero-equation by taking the join of their normalized XOR differences. This does not change the support semantics.

### Source size

- d-1 copy equations have constant size;
- the feedback XOR mentions at most d state variables;
- the total Step syntax is O(d) operator/variable occurrences up to ordinary binary nesting and fixed equation syntax.

If a particular concrete syntax expands shared wrappers differently, the bound remains at worst a small polynomial; the semantic parameter is linear in the LFSR description.

A dummy environment input may be added and ignored if the reactive framework requires at least one input stream; every environment refinement then sees the same deterministic next-cell map.

## 3. Cell predecessor is inverse permutation

Let G be a set of state cells.

Because each current cell v has exactly one allowed next cell pi(v),

`Pre(G) = pi^{-1}(G)`.

There are no zero-unsafe cells, so

`A*=V={0,1}^d`

and

`barL(G)=pi^{-1}(G)`.

Thus the positive obligation transformer is a Boolean-lattice automorphism induced by the LFSR permutation.

## 4. One compact Safe disequation seeds the long orbit

Choose any fixed nonzero cell

`v_0 in {0,1}^d`.

Let `C_(v_0)(x)` be its Boolean minterm.

Use the single Safe disequation

`C_(v_0)(x) != 0`.

Its positive support mask is the singleton

`H_0={v_0}`.

The propagated obligation orbit is

`H_t={pi^{-t}(v_0)}`.

Since all nonzero cells lie on one pi-cycle, these are pairwise distinct for

`t=0,...,2^d-2`

and then repeat.

## Theorem 1 — exponential obligation orbit

The positive obligation orbit has exact period

`2^d-1`.

All orbit masks are distinct singletons and hence pairwise incomparable.

Therefore canonical antichain minimization removes none of them.

## 5. Exact fixed-point iteration lower bound

Starting from positive top, after n positive iterations the accumulated canonical obligation family is

`H^(n)={ {pi^{-t}(v_0)} : 0<=t<n }`

until `n=2^d-1`.

By the canonical entailment theorem, a new singleton is not entailed by the previous distinct singleton obligations.

Hence every one of the first `2^d-1` additions is a **strict semantic strengthening**.

### Theorem 2 — compact exponential iteration family

The ordinary support-clause greatest-fixed-point iteration requires exactly

`2^d-1`

strict positive-strengthening steps before stabilization (up to the indexing convention for the initial/top approximation).

The source Step plus Safe description has O(d) Boolean structure.

Thus there is an exponential lower-bound family in the natural number d of BA state coordinates even for:

- deterministic zero-safe dynamics;
- no essential environment choice;
- Step containing equations only;
- Safe containing one disequation only.

## 6. Final winning support family

The fixed positive antichain is

`H* = { {v} : v != 0 }`.

A complete state support S is winning iff it hits every singleton in H*, i.e.

`{0,1}^d \ {0} subseteq S`.

Therefore exactly two complete state types are winning:

1. every nonzero Venn cell active and zero cell inactive;
2. every Venn cell active.

The zero cell is unconstrained because it is a fixed point of the LFSR and never enters the nonzero orbit seeded by v_0.

## 7. Canonical output-size lower bound

Within the canonical support-clause representation, H* has exactly

`2^d-1`

irredundant positive masks.

No singleton obligation can be removed: the complete support missing exactly that nonzero cell while containing every other cell satisfies all other singleton obligations but violates the omitted one.

Thus the final canonical clause itself has exponential size in d.

This is an **output-size** lower bound for the chosen clause representation, not a proof that every possible logical/circuit representation of the same winning family must be exponential.

## 8. Bekić/orbit solver consequence

The two-phase solver from `ABA_SAFETY_BEKIC.md` does not make this family disappear.

The zero phase terminates immediately (`Z*=empty`).

The positive phase must account for the entire nonzero LFSR orbit if it materializes the canonical antichain, because every orbit member is irredundant.

The decomposition is still useful—it identifies exactly where the complexity resides—but cannot compress an inherently large requested output in this representation.

## 9. Why this is stronger than the unrestricted Sperner construction

The Sperner-tight construction can yield roughly

`2^N/sqrt(N)`

period for N cells, but may require a correspondingly large transition description.

The LFSR family gives the smaller period

`N-1=2^d-1`,

but does so from a compact algebraic transition description of size O(d).

It therefore establishes a genuine source-compact exponential family.

## 10. Possible symbolic escape hatch

The orbit has a compact generator: the linear map pi plus one seed singleton.

A solver that is permitted to retain an **orbit descriptor** instead of materializing H* could represent the final constraint symbolically as

`the support hits every point of the nonzero pi-orbit`.

For a primitive LFSR that orbit is simply all nonzero cells.

This suggests a richer output representation can beat the canonical-clause materialization cost on structured dynamics.

That is not a contradiction: the lower bound is for the explicit antichain representation.

It motivates looking for algebraic orbit summarization before enumerating a long cycle.

## 11. Next research direction

The LFSR example suggests importing finite-group/linear-dynamics techniques:

1. detect when the cell predecessor is induced by a permutation or linear map;
2. compute orbit closures algebraically instead of step-by-step;
3. summarize whole orbits by invariant subspaces/cosets/cycle decompositions;
4. only materialize individual support obligations when the downstream backend requires them.

This is another Tao-style representation change: a long logical fixed-point iteration may be a short algebraic orbit computation in the right coordinates.

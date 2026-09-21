# Hypergraph duality for upward ABA support properties

**Status:** DERIVED representation equivalence using classical hypergraph blocker/transversal duality. General dualization complexity is established literature; the research contribution under test is when/how to switch representations inside the ABA synthesis backend.

The canonical positive-clause antichain from `CANONICAL_SUPPORT_CLAUSES.md` is a hypergraph.

This gives a second exact antichain representation of the same upward winning family: its minimal transversals, i.e. the minimal winning complete supports.

The two forms can differ exponentially in size.

## 1. Prime-hit / CNF representation

Fix a nonempty allowed cell arena A.

A normalized positive property is represented by an antichain

`H subseteq P(A)`

of nonempty proper hit masks, with semantics

`Phi_H
 = { nonempty S subseteq A :
     for every h in H, S intersects h }.`

H is the hypergraph of prime positive clauses / irredundant hit obligations.

If H is empty, Phi_H is top: every nonempty support in A.

## 2. Add validity as one implicit hyperedge

Hypergraph transversal theory normally allows the empty candidate set unless excluded by an edge.

Define the validity-augmented clutter

`C_H := Min_subset(H UNION {A}).`

Then:

- if H is nonempty, every h is a proper subset of A, so A is redundant and `C_H=H`;
- if H is empty, `C_H={A}`, whose transversals are exactly the nonempty subsets of A.

Thus validity is handled uniformly.

## 3. Minimal-winning-support / DNF representation

Let

`M_H := Tr(C_H)`

be the hypergraph of inclusion-minimal transversals of C_H.

### Theorem 1

`M_H`

is exactly the antichain of inclusion-minimal complete supports satisfying Phi_H.

Hence

`S in Phi_H`

iff

`exists m in M_H, m subseteq S`.

So the same upward family has a monotone DNF representation by its minimal winning supports.

## 4. Blocker involution

For a finite clutter C, classical blocker duality gives

`Tr(Tr(C))=C`.

Therefore the two antichains determine each other exactly:

`M=Tr(C_H)`,

`C_H=Tr(M)`.

Recover normalized H from C_H by dropping the sole edge A only in the top case.

This is standard hypergraph transversal/blocker theory, not a new theorem.

## 5. Dual lattice operations

### H / prime-CNF side

For upward properties represented by H,K:

- AND:

  `H_meet = Min(H UNION K)`;

- OR:

  `H_join = Min({h UNION k : h in H, k in K})`.

CPre/box is also structurally simple on this side because it preserves intersections and maps each prime hit obligation independently.

### M / minimal-DNF side

For minimal winning supports M,N:

- OR:

  `M_join = Min(M UNION N)`;

- AND:

  `M_meet = Min({m UNION n : m in M, n in N})`.

Thus H and M exchange which Boolean lattice operation is cheap.

This is the usual CNF/DNF duality for monotone Boolean functions, expressed directly on support antichains.

## 6. LFSR example: exponential H, singleton M

In `ABA_LFSR_LOWER_BOUND.md`, the final prime-hit family is

`H = { {v} : v is every nonzero cell }`.

A support wins iff it contains every nonzero cell.

Therefore

`M = { V\{0} }`

(up to whether the zero cell belongs to A and is optional).

So:

- H size: `2^d-1`;
- M size: `1`.

The earlier exponential canonical-clause output lower bound is therefore **not** a representation-independent lower bound on the winning set.

This is exactly the kind of case where representation switching is essential.

## 7. Sperner worst case stays hard on both sides

Take H to be all m-subsets of an N-cell universe.

Its minimal transversals are all `(N-m+1)`-subsets.

Near `m=N/2`, both H and M have central-binomial/Sperner size.

Thus dualization does not magically compress every hard family.

The general monotone Boolean function can be large in both prime CNF and prime DNF form.

## 8. Graph-CNF / vertex-cover example

If H consists of two-cell edges of a graph, then M is the family of minimal vertex covers.

The expander-derived OBDD lower-bound families from `ABA_OBDD_LOWER_BOUNDS.md` therefore map on the dual side to minimal-vertex-cover enumeration.

This illustrates the three-way representation tradeoff:

- graph/hypergraph H may be linear size;
- OBDD may be exponential;
- minimal-transversal M may also be large.

No representation dominates universally.

## 9. Dualization is itself a nontrivial frontier

Computing M=Tr(H) is the hypergraph transversal / monotone Boolean dualization problem.

Known landscape:

- Fredman–Khachiyan gave quasi-polynomial-time duality testing / incremental techniques for monotone dualization;
- Boros, Elbassioni, Gurvich, Khachiyan and others developed quasi-polynomial and practical transversal-generation methods;
- Eiter–Gottlob–Makino and later work identify many polynomial/output-polynomial structured cases;
- Arnaud Mary (arXiv:2407.00694, 2024) proves polynomial duality / incremental polynomial transversal enumeration for bounded-VC-dimension hypergraphs, generalizing many prior tractable classes;
- Martin Schirneck (arXiv:2603.06402, 2026) studies transversal rank, conformality, degree-sensitive enumeration, and related parameterized barriers.

The existence of a general polynomial-time dualization algorithm remains a long-standing open question according to these sources.

This means representation switching must itself be structure-aware.

## 10. VC dimension becomes a measurable OrbitSynthesis parameter

For an obligation hypergraph H on support cells, measure

`VCdim(H)`.

If the hypergraphs generated by a Tau specification family have bounded VC dimension, recent transversal results make conversion H -> M substantially more tractable.

This creates a new empirical/theoretical question:

> What VC dimension is induced by common Tau Boolean-term / recurrence / symmetry patterns?

There is no general bounded-VC theorem: the ABA monotone-dynamics universality construction can realize arbitrary positive CNFs and hence arbitrary hypergraph complexity.

## 11. Transversal rank is another useful parameter

Let

`trank(H)=max{|m|: m in Tr(H)}`.

Small transversal rank means every minimal winning support is small.

The 2026 transversal-rank literature gives parameterized enumeration bounds in terms of rank/degree and identifies barriers to stronger algorithms.

For synthesis, small trank can make the DNF/minimal-support side attractive even when H has many clauses.

## 12. A bidirectional antichain backend

Maintain a property object with optional cached views:

`UpwardProperty:
  allowed arena A
  prime-hit antichain H? 
  minimal-support antichain M?
  other representations (BDD/ZDD/orbit descriptor)?`

Choose operations by view:

- CPre / box: prefer H;
- AND: prefer H;
- OR: prefer M;
- witness of membership: M can supply a minimal contained support;
- explanation of violated property: H supplies an unhit prime obligation;
- deterministic/permutation orbit: retain algebraic orbit descriptor instead of expanding either side.

Convert H<->M only when a size/structure predictor justifies dualization.

## 13. Strategy relevance

The maximal-response system strategy does not require M: it always takes the greatest zero-feasible response.

M is useful for:

- compact representation of objective/winning sets;
- reachability OR operations;
- minimal certificates that a concrete support is winning (`m subseteq S`);
- potentially computing progress ranks with smaller intermediate objects.

H remains useful for CPre because box distributes over its conjunction of hit obligations.

## 14. New falsification benchmarks

Add benchmark families where the two views separate sharply:

1. LFSR: huge H, tiny M;
2. all-small-hitting constraints where H tiny, M huge;
3. Sperner middle layer: both huge;
4. graph/expander clauses;
5. symmetric quotient hypergraphs;
6. random Tau-generated obligation families.

Measure:

- |H|, |M|;
- VC dimension;
- transversal rank;
- dualization time;
- downstream CPre/OR costs.

## 15. Paper-level implication

A more credible algorithmic story is no longer

> "support clauses are compact."

It is:

> "ABA positive synthesis exposes a monotone hypergraph semantics; different logical/game operations are efficient in different dual representations, and the relevant conversion problem is exactly monotone hypergraph dualization with known structural tractability parameters."

That connects OrbitSynthesis to a substantial existing combinatorial frontier without claiming the frontier itself as new.

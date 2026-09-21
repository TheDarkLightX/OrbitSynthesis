# Dual antichain calculus for upward ABA support properties

**Status:** DERIVED finite-lattice/hypergraph duality; blocker/transversal duality itself is classical. The synthesis-specific contribution under investigation is how the two canonical forms interact with ABA `CPre` and temporal fixed-point structure.

Work inside one fixed nonempty zero-safe cell arena A.

Let

`Sigma_A = P(A) \ {empty}`.

Every upward-closed winning family W on `Sigma_A` has two natural canonical antichain representations.

## 1. H-form: prime hit obligations

Let H be an inclusion-minimal family of nonempty subsets of A such that

`W = {S in Sigma_A : forall h in H, S intersect h != empty}`.

H is the prime positive-CNF / hyperedge representation already used throughout the repository.

## 2. M-form: minimal winning supports

Let

`M = Min_subset(W)`

be the inclusion-minimal members of W.

Then

`W = Up(M)
   = {S in Sigma_A : exists m in M, m subseteq S}`.

M is the prime monotone-DNF / minimal-model representation.

## 3. Hypergraph blocker duality

A set S belongs to W_H exactly when S is a transversal/hitting set of hypergraph H.

Therefore the minimal winning supports are exactly the minimal transversals:

`M = Tr(H)`.

Conversely, H is the blocker of M:

`H = Tr(M)`

for Sperner/canonical hypergraphs on A.

Thus H and M are exact dual canonical forms.

The general computational problem of switching between them is monotone Boolean dualization / hypergraph transversal enumeration.

## 4. OR/AND operations in H-form

For canonical H,K:

### AND

`W_H intersect W_K = W_Min(H union K)`.

So conjunction is cheap: concatenate obligations and remove redundant supersets.

### OR

`W_H union W_K`

has H-form

`Min({h union k : h in H, k in K})`.

So disjunction can take a Cartesian product before minimization.

These are the formulas proved in `ABA_POSITIVE_MU_CALCULUS.md`.

## 5. OR/AND operations in M-form

The dual formulas are immediate from upward closures.

### OR

`Up(M) union Up(N) = Up(M union N)`.

Hence

`Join_M(M,N)=Min(M union N)`.

Disjunction is cheap in M-form.

### AND

A support S lies in both Up(M) and Up(N) iff it contains some m in M and some n in N, equivalently it contains `m union n` for some pair.

Therefore

`Meet_M(M,N)
 = Min({m union n : m in M, n in N}).`

Conjunction is the Cartesian-product operation in M-form.

This is the exact De Morgan-like computational dual of the H-form table.

## 6. Bottom and top

On nonempty supports:

- Bottom / False: `M=empty`; in H-form use the distinguished False state.
- Top: `M={{a}: a in A}` (every nonempty support contains some singleton), while `H=empty`.

Thus H-form is extremely compact for Top, whereas M-form can require |A| minimal supports.

This asymmetry matters for greatest-fixed-point initialization.

## 7. ABA CPre is naturally H-oriented

Freeze Step and the zero-safe arena A*.

Let B be the fixed positive Step seed obligations and let

`L:P(A*)->P(A*)`

be the cell robust predecessor.

For H-form,

`CPre_H(H)=Min(B union {L(h):h in H})`,

with False if a required transformed mask becomes empty.

So CPre acts independently on H hyperedges.

This follows from the dominant/maximal-response theorem and from CPre preserving arbitrary intersections in the upward fragment.

## 8. There is no comparable generic clausewise M-form CPre

Since M=Tr(H), the exact M-form after predecessor is

`Tr(CPre_H(Tr(M)))`.

Unless additional transition structure exists, this requires blocker/dualization work.

This is not a proof that no simpler formula exists for every special class; deterministic/permutation and symmetry cases may admit one.

It does show why H-form is the natural default for predecessor-heavy greatest-fixed-point calculations.

## 9. Temporal representation strategy

This suggests a representation-aware interpretation of positive fixed points.

### Safety / nu-heavy

Safety is built from repeated AND + CPre, both cheap in H-form.

Keep H.

### Reachability / mu-heavy

Reachability repeatedly forms

`Target OR CPre(X)`.

OR is cheap in M-form but CPre is cheap in H-form.

There is no globally best representation. One should compare:

1. stay in H and pay the H-form OR Cartesian product;
2. switch to M around OR and dualize back for CPre;
3. keep both forms incrementally if structured dualization is cheap;
4. use a third representation (BDD/d-DNNF/ZDD) when both antichains become large.

### General positive mu-calculus

The syntax tree itself provides hints about which canonical form is locally favorable:

- AND/CPre nodes favor H;
- OR nodes favor M;
- representation switches cost hypergraph dualization.

This turns backend selection into a dynamic-programming/compilation problem on the temporal formula.

## 10. LFSR example: representation-specific exponential blowup

In the compact LFSR family from `ABA_LFSR_LOWER_BOUND.md`, safety iteration in H-form eventually collects one singleton obligation for every nonzero state cell:

`|H|=2^d-1`.

But hitting every nonzero singleton means that a winning support must contain every nonzero cell.

Hence

`M={A_nonzero}`

has one element.

So the final upward property has:

- exponentially many prime CNF clauses;
- one prime DNF/minimal-support generator.

This proves that large H output does not imply representation-independent semantic output complexity.

## 11. Conversely, M-form can be exponentially worse

Top already gives a simple finite example:

- H-form: `H=empty`;
- M-form: all singletons of A, size |A|.

More extreme monotone functions can have exponentially many minimal true supports but few prime clauses.

Therefore both directions of dualization can cause substantial growth.

## 12. Current hypergraph-dualization frontier

General monotone Boolean dualization / transversal enumeration has no known polynomial-time algorithm.

Fredman-Khachiyan gives the classical quasi-polynomial/subexponential frontier. Recent structural results are directly useful for OrbitSynthesis:

- bounded VC dimension admits polynomial-time duality / incremental-polynomial transversal enumeration;
- bounded conformality gives another polynomial case, even when VC dimension is unbounded;
- current work studies transversal rank, conformality, and maximum degree as finer parameters.

Primary/current references:

- Arnaud Mary, *Enumeration of minimal transversals of hypergraphs of bounded VC-dimension*, arXiv:2407.00694 (updated 2026).
- Martin Schirneck, *Transversal Rank, Conformality and Enumeration*, arXiv:2603.06402 (2026).
- classic dualization literature cited in `research/SOURCES.md`.

## 13. Backend-selection parameters

For every canonical H/M pair that arises during synthesis, measure at least:

- `|H|` and `|M|` when both are available;
- maximum/minimum edge size;
- VC dimension estimates/bounds;
- conformality;
- transversal rank;
- maximum vertex degree;
- group symmetry/orbits;
- incidence/pathwidth;
- whether transition dynamics are deterministic/permutation/linear.

These parameters tell us whether blocker conversion is likely to be cheap or catastrophic.

## 14. Research target: bidirectional incremental maintenance

Rather than repeatedly dualizing from scratch, investigate maintaining H and M together under the exact operations:

- insert/delete/minimize an H obligation;
- apply one cell predecessor L to all H edges;
- union/minimize M under OR;
- update transversals incrementally after structured H changes.

The ABA safety/Bekić dynamics are especially structured: each seed edge follows a unary orbit under L. That may allow specialized incremental dual maintenance far cheaper than general hypergraph dualization.

## 15. Falsification target

Construct small ABA games where:

1. H stays tiny but M grows to a maximum antichain;
2. M stays tiny but H grows to a maximum antichain;
3. both H and M are simultaneously large;
4. one representation alternates between easy and hard across successive reachability/Buchi approximants.

These examples will tell us whether a simple local switching heuristic can ever be robust or whether a more global compiler cost model is needed.

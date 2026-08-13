# Graph coloring is nonzero row-list interpolation over F3

**Status:** DERIVED exact reduction. Graph 3-colorability NP-completeness is classical prior art. The purpose of this note is explanatory: isolate the smallest mechanism causing the easy-SMP/hard-row-list separation. Tau-independent.

## 1. Fixed algebra

Let

`A=(F_3; +, -, 0)`.

Every n-ary A-term is a homogeneous linear form

`t_alpha(x)=alpha dot x`

for `alpha in F_3^n`.

Ordinary SMP for this algebra is linear-subspace membership.

## 2. One fixed row list

Consider row-list interpolation instances in which **every** observation uses exactly the same list

`L={1,2}=F_3 \ {0}`.

Thus each constraint merely says

`t_alpha(z) != 0`.

No singleton/equality rows and no varying list language are needed.

## 3. Reduction from graph 3-colorability

Let

`G=(V,E)`

be a graph with

`V={1,...,n}`.

Associate coefficient

`alpha_i in F_3`

with vertex i. Interpret the three field elements as the three colors.

For every edge `{i,j}` add one observation

`z_(ij)=e_i-e_j in F_3^n`

with the fixed list L.

Then

`t_alpha(z_(ij))
 = alpha_i-alpha_j`.

Therefore

`t_alpha(z_(ij)) in {1,2}`

iff

`alpha_i != alpha_j`.

### Theorem 1

G is 3-colorable iff the resulting fixed-list F3 row-interpolation instance is feasible.

The reduction is linear in the number of edges and every observation contains exactly two nonzero coordinates, `+1` and `-1`.

Since graph 3-colorability is NP-complete, row-list term interpolation for `(F_3;+,-,0)` is NP-hard even under all of the following restrictions simultaneously:

- one fixed finite algebra;
- one fixed allowed row list `{1,2}`;
- every constraint is a single linear disequality;
- every observation has support size exactly two.

NP membership follows from the coefficient-vector witness, so this restricted problem is NP-complete.

## 4. Inner ground

This is a cleaner explanation than the positive-1-in-3 reduction in `F3_ROW_LIST_REACTIVE_HARDNESS.md`.

Gaussian elimination answers:

> does a specified target vector belong to this linear subspace?

The row-list problem asks:

> does the subspace contain a point that avoids all these forbidden coordinate hyperplanes?

In the graph construction, each edge forbids the hyperplane

`alpha_i-alpha_j=0`.

The complement choices are exactly graph-color choices.

So the complexity jump is caused by **hyperplane avoidance**, not by expensive subpower membership.

## 5. Relation to equations and disequations

A two-element list in F3 is the complement of one field value.

Thus F3 row-list interpolation can be viewed as a system of linear equations and linear disequations in the unknown term coefficients.

The graph reduction uses only homogeneous disequations

`alpha_i-alpha_j != 0`.

This places the result near classical CSPs over finite fields and means OrbitSynthesis should not claim novelty for the static hardness phenomenon itself.

The independent research value is the way this static obstruction appears inside a shared original-signature term controller and the solver architecture derived from `SUBPOWER_ROW_LIST_SYNTHESIS.md`.

## 6. Reactive comparison

The graph reduction is the best **static explanation**, but it does not by itself give the strongest sparse safety-game bound because helper-state closure can require three safe successors.

`F3_ROW_LIST_REACTIVE_HARDNESS.md` therefore retains the positive-1-in-3 reduction, which proves NP-complete sparse input-free fixed-domain term safety with at most **two** safe successors per state.

The two reductions have different purposes:

- graph coloring: minimal explanation of row-list hardness;
- positive 1-in-3: stronger next-state-list-width bound for the reactive embedding.

## 7. Exact calibration

`experiments/f3_nonzero_row_graph_coloring.py` exhausts all labelled simple graphs on up to five vertices and checks equivalence between:

1. brute-force 3-colorability; and
2. existence of an F3 coefficient vector satisfying every nonzero edge-row constraint.

For n=5 this includes all `2^10=1024` labelled graphs.

The computation is a calibration; Theorem 1 is the proof.

## 8. Prior-art boundary

Graph 3-colorability NP-completeness is classical; Garey, Johnson, and Stockmeyer proved strong restricted versions in the 1970s.

Systems of linear constraints with disequalities and finite-domain CSPs are also established topics.

Current targeted searches did not locate the exact phrase "row-list term interpolation" for this formulation. Keep that phrase provisional and descriptive, not a claimed standard problem name.

## 9. Next use

This reduction suggests solver features independent of Tau:

- detect sparse nonzero-row constraints as graph coloring / graph homomorphism subproblems;
- extract a conflict graph from hyperplane-avoidance constraints;
- use specialized coloring/CSP algorithms rather than generic term-table search;
- in a mixed equality/disequality instance, Gaussian-eliminate equalities first and build the conflict constraints on a basis of the remaining solution space.

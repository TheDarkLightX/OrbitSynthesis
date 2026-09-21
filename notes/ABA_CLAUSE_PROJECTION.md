# Closed-form projection of ABA equation/disequation clauses

**Status:** DERIVED paper theorem; exhaustive bounded checks completed independently for small support universes; Tau differential testing and Lean pending.

This note identifies a formula class where support-level ABA quantifier elimination has a closed form and a parameterized ROBDD bound. The semantic elimination of such clauses is classical territory; the candidate contribution is the support-geometric formulation, the exact projection rule, and its symbolic-complexity consequences for Tau/ocLTL.

## 1. Fine support setup

Let a block of `r>=1` Boolean-algebra variables be existentially quantified. Let `V` be the set of coarse support cells determined by the retained variables and any fixed interpreted-constant regions. Each coarse cell `v in V` has a finite refinement fiber

`F_v`

of size `2^r`, one fine cell for each valuation of the eliminated BA variables.

Let

`U = disjoint_union_{v in V} F_v`

be the fine-cell universe.

A coarse support is a bit-vector `z in {0,1}^V`. A fine support `W subseteq U` extends z iff

- if `z_v=0`, then `W intersect F_v = empty`;
- if `z_v=1`, then `W intersect F_v != empty`.

Atomlessness realizes every such finite refinement.

## 2. Support form of a conjunction of equations and disequations

Consider a conjunction

`C = (AND_i f_i=0) AND (AND_j g_j!=0)`.

After minterm/support translation:

- each equation `f_i=0` forbids every fine cell in a set `A_i subseteq U`;
- each disequation `g_j!=0` requires the support to hit a set `G_j subseteq U`.

All zero-equations combine into one forbidden set

`Z := union_i A_i`.

Write

`A := U \ Z`

for the allowed fine cells.

Thus the fine-support condition is simply

`W subseteq A`

and

`W intersect G_j != empty` for every j.

## 3. Maximal-witness lemma

Fix a coarse support z and define its maximal allowed refinement

`W_max(z) := A intersect union_{v:z_v=1} F_v`.

### Lemma

There exists some fine support W extending z and satisfying C iff `W_max(z)` itself extends z and satisfies C.

### Proof

If `W_max(z)` works, existence is immediate.

Conversely suppose a witness W exists. Since W avoids Z,

`W subseteq W_max(z)`.

Because W extends z, every active coarse fiber contains at least one element of W, hence also at least one element of `W_max(z)`. So `W_max(z)` extends z.

Every disequation condition is monotone upward in W: if `W intersect G_j != empty` and `W subseteq W_max(z)`, then `W_max(z) intersect G_j != empty` as well.

Therefore the maximal allowed refinement is a witness whenever any witness exists.

### Noether-style mechanism

There is no combinatorial search because the positive obligations are monotone and the equations only delete cells. Once illegal fine cells are removed, **taking all remaining cells is the universal witness**.

## 4. Exact projection theorem

For each coarse cell v define its allowed fiber

`A_v := A intersect F_v`.

Call v **dead** if

`A_v = empty`.

For each disequation j define its coarse witness set

`H_j := { v in V : A_v intersect G_j != empty }`.

### Theorem 1 — closed-form existential elimination

On valid coarse supports,

`exists quantified_block . C`

is equivalent to the support formula

`Proj(C)(z)
 = (AND_{v dead} NOT z_v)
   AND
   (AND_j OR_{v in H_j} z_v).`

If some `H_j` is empty, the result is false.

### Proof

By the maximal-witness lemma, feasibility is exactly:

1. every active coarse cell has at least one allowed refinement, which is equivalent to `z_v=0` for every dead v;
2. each disequation's set `G_j` intersects `W_max(z)`, which is equivalent to at least one active v having `A_v intersect G_j != empty`, i.e. `OR_{v in H_j} z_v`.

No other condition is needed.

## 5. The projected class is structurally simple

The output has only:

- negative unit clauses `NOT z_v`; and
- positive monotone clauses `OR_{v in H_j} z_v`.

So existential elimination of a conjunction of ABA equations/disequations lands in a **monotone-CNF-plus-negative-units** support normal form.

This statement holds for eliminating an arbitrary block of r BA variables at once; r affects only the fine fibers used to compute `A_v` and `H_j`, not the logical shape of the projected formula.

It also extends to finitely many interpreted constants by taking V to be the retained-variable minterms refined by the `rho(C)` nonzero constant regions from `ABA_INTERPRETED_CONSTANTS.md`.

## 6. ROBDD bound parameterized by disequations

Let

`n := |V|`

be the coarse support width and let q be the number of disequation clauses after removing duplicates/trivialities.

Consider any fixed ordering of the n coarse support variables.

### Theorem 2 — ROBDD upper bound

The reduced ordered BDD of `Proj(C)` has at most

`n * 2^q`

nonterminal nodes.

### Proof

Process the support variables in the chosen order. After assigning the first t variables:

- if a forbidden/dead variable was set to 1, the residual function is false;
- otherwise, each of the q positive clauses is either already satisfied or still unsatisfied.

For a fixed level t, the unassigned suffix of every `H_j` is fixed by the variable order. Therefore a non-false residual function is completely determined by the subset of positive clauses not yet satisfied.

There are at most `2^q` such subsets. Hence at most `2^q` distinct nonterminal residuals can occur at any of n variable levels, giving at most `n 2^q` nonterminal nodes before reduction; a reduced BDD can only be smaller.

### Consequence

For fixed q, clause projection has ROBDD size linear in the support width n.

With k retained pure-ABA variables,

`n=2^k`.

With finite interpreted constants,

`n=rho(C) 2^k`.

So this clause class is fixed-parameter tractable in the number q of disequations at the representation level:

`ROBDD size <= rho(C) 2^k 2^q`.

This is a genuine protected symbolic class, unlike the unrestricted BDD proposal.

## 7. DNF-level corollary

Existential quantification distributes over disjunction:

`exists y. (C_1 OR ... OR C_L)
 = (exists y.C_1) OR ... OR (exists y.C_L)`.

If each `C_l` is a conjunction of equations/disequations with at most q disequations, each projected clause admits the bound above.

If the implementation retains the result as a Boolean DAG/disjunction of projected clause DAGs rather than immediately forcing one global ROBDD or expanding another normal form, an unreduced circuit representation has size bounded by the sum of the clause representations.

This does **not** imply that the single canonical ROBDD of the disjunction has the same additive bound; APPLY can create additional states.

## 8. Relationship to Tau's current quantifier code

Tau's current `anti_prenex_block` already contains special handling for clause-shaped atomless formulas and a separate `push_ex_block_into_clause` path before general Boole/Shannon decomposition. It also has fast paths for all-positive/all-negative atom profiles.

Therefore we do **not** claim that semantic elimination of an ABA clause is new or absent from Tau.

The proposed contribution is narrower:

1. expose the clause's semantics as forbidden fine support cells plus monotone hit obligations;
2. compute the projection by fiber incidence without recursively decomposing formula atoms;
3. retain the projected result as a support DAG/BDD with the explicit `n 2^q` representation bound;
4. use the current Tau path as an independent differential oracle/fallback.

A code-level comparison is still required to determine whether `push_ex_block_into_clause` is algorithmically equivalent after normalization or whether support incidence removes work that Tau currently performs on term syntax.

## 9. Bounded falsification completed

An independent exhaustive checker compared the closed-form theorem against explicit enumeration of all legal fine refinements for random instances with:

- 1 to 4 coarse cells;
- 1 or 2 eliminated BA variables;
- random forbidden fine-cell sets;
- 0 to 3 random positive hit obligations.

All tested coarse supports agreed.

This validates the implementation idea on the exhausted finite domain; the proof above is the universal justification.

## 10. Implementation fast path

For a homogeneous atomless-BA existential block whose matrix is a conjunction of equality/disequality atoms:

1. determine the retained support coordinates and fine refinement fibers;
2. compile all equalities into one forbidden fine-cell mask Z;
3. for each coarse fiber, compute whether any allowed refinement survives;
4. for each disequality, project its allowed fine witnesses to a coarse set H_j;
5. emit negative unit clauses for dead coarse fibers and positive clauses H_j;
6. preserve current Tau elimination as a differential oracle and fallback until the fast path has exhaustive bounded agreement.

No BDD is needed to perform the elimination itself. A BDD/ZDD can be used only as the retained symbolic representation afterward.

## 11. Next theorem targets

1. Determine whether Tau's Chapter-5 clause path is exactly equivalent to this support projection after term-minterm compilation, or whether there are source shapes where one asymptotically dominates the other.
2. Extend the ROBDD bound from clauses to syntactic classes produced by common Tau recurrence/safety formulas.
3. Characterize when alternation of existential/universal BA blocks preserves Horn/dual-Horn or bounded-width support structure.
4. Study whether q—the number of surviving disequation obligations—is small on real Tau workloads.
5. Derive an analogous closed-form projection for other homogeneous structures with factorized one-point extension relations.

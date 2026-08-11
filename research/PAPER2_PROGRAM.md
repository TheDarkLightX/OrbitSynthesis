# Paper 2 program — fragment-relative extremal synthesis over infinite structures

**Working title:** Positive Response Frontiers for Reactive Synthesis over Infinite Structures

**Status:** research program / candidate second paper. Several finite-order theorems are derived; full novelty search and reactive-game generalization remain.

## 1. Motivation

Complete response-type count can badly overstate actual system branching.

For a finite response fiber E and a finite family Delta of predicates used positively by a specification, define the positive signature

`sigma(e)={delta in Delta : delta(e)}`.

A response whose signature is contained in another response signature can never be uniquely needed for a monotone positive objective.

Therefore reactive system choice should be measured by the maximal positive signatures, not by all complete response types.

## 2. Core invariant

Define

`Front_Delta(E)=Max_subset({sigma(e):e in E})`

and

`w_Delta(E)=|Front_Delta(E)|`.

### Exact one-step theorem

For every monotone Boolean objective F in Delta:

`exists e in E. F(sigma(e))`

iff

`exists s in Front_Delta(E). F(s)`.

So `w_Delta(E)` is the exact nondominated branching width for the positive fragment.

## 3. Dominance as width one

The system has a fragment-dominant response iff

`w_Delta(E)=1`.

Equivalently, the union of all realized positive signatures is itself realized.

This recovers ABA's maximal-support response but also gives fragment-sensitive results in other structures.

## 4. Standard structure classification

### Pure equality

- positive equalities `y=a_i`: width = number of distinct parameter equality classes;
- positive disequalities `y!=a_i`: width 1 via a fresh element.

### Dense linear order

- all right-facing inequalities `a_i<y`: width 1;
- all left-facing inequalities `y<a_i`: width 1;
- both directions positive: width `k+1`, corresponding to the open cuts.

### Rado graph

- one chosen adjacency polarity per parameter: width 1;
- both adjacency and nonadjacency positive on r parameter positions: width `2^r`.

### Henson K_n-free graph

Positive adjacency signatures are K_(n-1)-clique-free parameter subsets. The frontier is the family of maximal such subsets.

For H_3 this is the maximal-independent-set family. Matchings give width `2^(k/2)`.

For general H_n, disjoint K_(n-1) components give width `(n-1)^(k/(n-1))` on the divisible sequence.

Thus homogeneity / omega-categoricity alone does not bound response frontier width polynomially.

## 5. Hypergraph duality

When feasibility of positive signatures is downward closed and described by minimal forbidden feature sets H, maximal feasible positive signatures are complements of minimal transversals of H.

Thus fragment-relative response compression can be a hypergraph-dualization problem.

This links response selection to the same blocker/transversal machinery already used for ABA upward state properties.

## 6. Product theorem

For independent coordinate-local product fibers with disjoint positive predicate blocks:

`w(E_1 x ... x E_d)=product_i w(E_i)`.

Dominance (`w=1`) is stable under finite independent products.

## 7. Symmetry theorem

For d identical coordinate fibers each of width w, with full coordinate permutation symmetry, the `w^d` product frontier tuples collapse to

`binom(d+w-1,w-1)`

frontier orbits.

For fixed local w, this is polynomial in d.

This gives a general abstract explanation of the ABA histogram quotient.

## 8. Partially collapsed games

In a reactive arena, different partial/environment types p can have different widths

`w_Delta(E_p)`.

Compile the game by replacing each response fiber with one representative per maximal positive signature.

Then:

- width 1 fibers become deterministic system moves;
- small-width fibers become bounded branching;
- large-width fibers retain explicit/symbolic frontiers.

This yields a spectrum between full synthesis and model-checking collapse.

## 9. Semilattice / polymorphism sufficient conditions

A semilattice operation preserving legal response constraints is a sufficient structural source of union-realizability and therefore width one for suitable positive primitive fragments.

For omega-categorical CSP theory, polymorphism clones are known to control primitive-positive definability and tractability phenomena, but no claim should be made that one semilattice identity characterizes all infinite-domain tractability.

Research target:

> identify polymorphism / amalgamation conditions that imply bounded response frontier width, not merely width one.

## 10. Dynamic extension problem

The finite one-step theorem is exact. The deeper reactive question is when a selected signature abstraction is closed under temporal predecessor and fixed-point operations.

Needed conditions may involve:

- next-state observation sufficiency;
- monotonicity of the transition abstraction;
- closure of frontier representatives under composition;
- finite memory / bounded lookback products;
- objective positivity.

ABA satisfies an unusually strong version because its signature is the full support code and `CPre` becomes a box modality.

## 11. Candidate general theorem schema

Let a theory/plugin provide for each partial type p:

1. a finite response signature poset `S_p`;
2. a sound/complete mapping from response types to signatures;
3. positive monotone objective atoms over signatures;
4. effective representatives for maximal signatures;
5. an abstraction of next-state signatures preserved by the transition semantics.

Then reactive system branching can be quotient by maximal response signatures rather than complete response types.

If every `S_p` has a greatest element, the system-choice layer collapses completely.

This is the generalization to prove carefully.

## 12. Complexity parameters

Candidate semantic parameters:

- maximum positive response width `max_p w(E_p)`;
- number of distinct frontier orbits under stabilizer groups;
- forbidden-pattern rank;
- transversal rank;
- response interaction treewidth;
- polarity-conflict count;
- dominance deficit;
- product symmetry block sizes.

The research goal is parameterized synthesis algorithms in these quantities rather than in raw complete-type cardinality.

## 13. Why this is mathematically deeper than a Tau optimization

This program studies the interaction of:

- model-theoretic type extension;
- polarity/positive logic;
- Pareto antichains;
- homogeneous structures;
- polymorphism clones;
- hypergraph duality;
- symmetry/orbit quotienting;
- reactive games and fixed points.

Tau/ABA becomes one extreme case (`width=1` globally for the support-positive fragment), not the definition of the theory.

## 14. Immediate proof targets

1. formalize the maximal-signature theorem in Lean;
2. prove the equality/DLO/Rado/Henson examples formally on finite parameter structures;
3. prove the product and symmetry laws formally;
4. derive an exact bounded-width reactive-game quotient theorem;
5. characterize the positive signature frontier of additional Fraisse limits / finitely bounded homogeneous structures;
6. search for polymorphism conditions implying bounded frontier width;
7. relate frontier width to orbit growth and the CSL omega-regular satisfiability route.

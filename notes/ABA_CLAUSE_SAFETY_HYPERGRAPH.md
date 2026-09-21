# Direct safety synthesis for ABA clauses via support hypergraphs

**Status:** DERIVED one-step closure theorem and canonical representation; randomized bounded one-step and fixed-point differential checks completed; Lean pending; novelty not established.

This extends `EQUATIONAL_SAFETY_CUBE_GAME.md` from pure equations to normalized atomless-Boolean-algebra clauses

`f=0 AND AND_i g_i!=0`.

Unlike the equation-only theorem, **atomlessness matters here** because several inequations may require distinct nonzero refinements of the same coarse region.

## 1. Clause regions are allowed sets plus hitting hypergraphs

Fix k BA state variables and let

`U={0,1}^k`

be their Venn-cell labels.

A normalized clause

`f(s)=0 AND AND_i g_i(s)!=0`

corresponds to:

- an allowed cell set `A subseteq U`, the complement of the minterm support of f;
- hit sets `H_i subseteq U`, the minterm supports of the g_i.

It holds on a complete support S exactly when

`empty != S subseteq A`

and

`S intersect H_i != empty` for every i.

Write this region as `R(A;H)`.

First replace every H_i by `H_i intersect A`. If any becomes empty, the region is empty.

## 2. Canonical antichain representation: nonemptiness matters

If `H_i subseteq H_j`, then hitting H_i implies hitting H_j, so H_j is redundant.

There is one additional redundancy specific to complete ABA types:

`H_i=A`

is tautological, because every realized support is already required to be **nonempty** and contained in A. Thus it must be deleted even when no smaller hit set is present.

Define `Canon(A,H)` by:

1. intersect every hit with A;
2. if A is empty or some hit is empty, return the empty region;
3. delete every hit equal to A;
4. delete duplicates;
5. delete every hit that strictly contains another retained hit.

The result is an inclusion antichain of proper nonempty subsets of A.

### Proposition — semantic canonical form

For every nonempty clause region, the pair

`(A, CanonHits(A,H))`

is semantically canonical over the domain of **nonempty** supports:

- A is the union of all supports in the region;
- the retained hits are the unique nontrivial prime positive support clauses.

`ABA_CLAUSE_SUPPORT_LATTICE.md` gives the precise maximal-loser/blocker proof and treats nonemptiness as an implicit hit on A when standard hypergraph duality is desired.

## 3. Transition clause

Let:

- state labels `a in S={0,1}^k`;
- input labels `u in I={0,1}^p`;
- output/next-state labels `v in V={0,1}^k`.

Represent the normalized transition clause by:

- allowed full cells `L subseteq S x I x V`;
- transition hit sets `G_1,...,G_q subseteq S x I x V`.

A full support Q satisfies it iff

`Q subseteq L`

and

`Q intersect G_j != empty` for every j.

Let the target winning approximation be `R(A;H)` on the next-state support.

## 4. Lift the target to full cells

The target allowed condition restricts full cells to

`L* := L intersect preimage_y(A)`.

Each target hit H_t lifts to `preimage_y(H_t)`.

Collect all full hit sets

`K = {G_1,...,G_q} union {preimage_y(H_t) : H_t in H}`.

The inner controller problem for a fixed `(s,x)` support is exactly one ABA clause with allowed full cells L* and hit family K.

## 5. Existential controller projection

Define

`E := { (a,u) : exists v . (a,u,v) in L* }`

and, for every K_j,

`E_j := { (a,u) : exists v . (a,u,v) in L* intersect K_j }`.

### Lemma — existential projection

For an actual `(s,x)` support P, there exists a controller output satisfying the transition clause and target region iff

`P subseteq E`

and

`P intersect E_j != empty` for every j.

### Proof

Necessity is immediate. For sufficiency, inside every active `(a,u)` region realize **all allowed output labels** v with `(a,u,v) in L*`. Atomlessness realizes every such finite nonempty refinement. If P hits E_j, the maximal allowed refinement automatically includes a K_j witness. Hence all hit constraints hold simultaneously.

This is the support form of `ABA_BLOCK_QE.md`.

## 6. Universal environment projection

Define

`A' := { a : for every u, (a,u) in E }`

and

`H'_j := { a : for every u, (a,u) in E_j }`.

### Theorem 1 — controllable predecessor closure

For atomless BA,

`CPre(R(A;H)) = Canon( A'; {H'_j}_j ).`

### Proof

Every input extension P of state support S0 is contained in E iff each active state cell a has **all** input labels `(a,u)` in E, i.e. `S0 subseteq A'`.

For a fixed E_j, every input extension P must intersect E_j iff at least one active state cell a has its entire input fiber inside E_j. Otherwise the environment independently picks, in every active state region, one input label outside E_j and constructs an extension avoiding E_j. Thus the universal hit condition is exactly

`S0 intersect H'_j != empty`.

Canonicalization then removes semantic redundancies, including the implicit-nonemptiness tautology H'=A'.

## 7. Direct CPre algorithm

One predecessor step on canonical `(A,H)` is:

1. `L* = L intersect preimage_y(A)`;
2. append `preimage_y(H_t)` to the transition hit family;
3. `E = exists_y L*`;
4. `E_j = exists_y(L* intersect K_j)`;
5. `A' = forall_x E`;
6. `H'_j = forall_x E_j`;
7. canonicalize on nonempty supports:
   - restrict hits to A';
   - empty hit => empty region;
   - hit equal to A' => delete as tautological;
   - remove duplicates and inclusion-nonminimal hits.

All operations are finite set projection/intersection and antichain minimization on Boolean-cell masks. No complete ABA type is enumerated.

## 8. Equation-only fragment

If there are no transition inequations and no target hits, the operator reduces to

`A -> {a : forall u exists v in A . (a,u,v) in L}`,

exactly the Boolean-cube predecessor of `EQUATIONAL_SAFETY_CUBE_GAME.md`.

Thus the cube theorem is the zero-hyperedge special case.

## 9. Smallest inequation counterexample to principal ideals

Take one BA state variable s and static condition

`s != 0`.

Its accepted complete supports are

`{{1},{0,1}}`,

while `{0}` is rejected. This is not a principal ideal `Supp(s) subseteq A`.

It is represented by

`A={0,1}` and `H={1}`.

So one inequation already forces the larger upward-closed/hypergraph carrier.

## 10. Strategy reconstruction

For equations alone, one finite output label per `(a,u)` cell suffices and glues into ordinary Boolean terms.

With inequations, one nonzero `(a,u)` region may need several output labels simultaneously. The maximal-witness proof splits that region into finitely many nonzero pieces and assigns the allowed y-labels.

Therefore concrete synthesis has two layers:

1. a finite support policy;
2. an effective atomless split/witness procedure realizing requested refinements.

`ABA_CLAUSE_SAFETY_RECURRENCE.md` proves that the **maximal allowed response** is a memoryless winning support policy at the fixed point.

## 11. Worst-case antichain size

Let `n=|U|=2^k`.

The nontrivial canonical hit family is an antichain of proper subsets of A. By Sperner's theorem its size is at most

`binom(n, floor(n/2))`.

This scale is attainable by static clauses for n large enough: choose one inequation term for every set in a maximum Sperner antichain (none of which equals A at the middle level).

Hence the hypergraph representation can still be doubly exponential in k. It is structural/parameterized, not a universal polynomial compression theorem.

## 12. Practical parameters

Measure:

- allowed-cell count |A|;
- nontrivial prime-hit count h;
- hit-set density;
- subsumption eliminated per step;
- fixed-point iterations;
- predecessor-orbit repetition;
- maximal response split arity.

These are better candidates than raw `|T_k|` for predicting the clause backend's actual cost.

## 13. Relation to established symbolic/antichain methods

Generic antichain representations are established in verification and games. That is not claimed as a contribution.

The ABA-specific result candidate is the derivation that normalized ABA clauses are support-upsets of this precise form and that `forall input / exists output` predecessor has the closed projection transform above.

## 14. Validation

`experiments/aba_clause_safety_hypergraph.py` now checks:

- 5,000 randomized one-step instances against explicit enumeration of all relevant complete supports in the one-state/one-input/one-output-bit universe;
- 2,000 randomized **whole fixed-point trajectories**, comparing the canonical hypergraph pair with the explicit complete-support winning approximation at every iteration;
- edge cases including the tautological `H=A` canonicalization bug found by the end-to-end test.

A larger private run of 10,000 random whole trajectories also found no divergence after the canonicalization correction.

## 15. Next research directions

1. Search for structural subclasses with provably small prime-hit antichains.
2. Import trie/SAT/ZDD antichain machinery rather than implement naive subsumption at scale.
3. Formalize the atomless split strategy construction.
4. Extend the transform to interpreted constants via `rho(C)` regions.
5. Compare direct hypergraph synthesis with Tau's atom-level Boole decomposition and the general support-BDD backend.
6. Continue novelty search against older negative-set-constraint and algebraic-control literature.

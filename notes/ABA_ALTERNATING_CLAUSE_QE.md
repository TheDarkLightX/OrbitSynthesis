# Alternating-block quantifier elimination for one ABA clause

**Status:** DERIVED paper theorem in support representation; existential rule subsumes/re-expresses classical atomless-BA clause elimination such as Asor TABA Theorem 3.2; direct universal rule and the representation-complexity consequences are candidate implementation contributions, not yet established as literature-novel. Exhaustive bounded checks of existential and universal projection completed independently; Tau differential tests and Lean pending.

## 1. Support-clause normal form

Fix a finite support universe U (variable minterms, refined by interpreted-constant regions when present).

Write

`C(Z; G_1,...,G_q)`

for the support clause

`(AND_{u in Z} NOT z_u)
 AND
 (AND_{j=1}^q OR_{u in G_j} z_u).`

Semantically:

- Z is the set of support cells forced to zero by the combined equality constraint;
- each `G_j` is the minterm support of one disequation, which must contain at least one nonzero cell.

Every conjunction of ABA equations/disequations can be put in this form:

- merge all equations `f_i=0` into one equation `(join_i f_i)=0`, hence one forbidden support Z;
- retain each disequation `g_j!=0` as one positive support obligation G_j.

Conversely every support clause corresponds to one ABA equation plus q ABA disequations by joining the appropriate minterms.

## 2. Projection geometry

Let a quantified BA block induce a projection

`pi : U -> V`

from fine support cells U to retained coarse cells V. The fiber over `v in V` is

`F_v = pi^{-1}(v)`.

For r eliminated BA variables, every fiber has size `2^r` within each constant region.

A fine support extends a coarse support exactly when every active coarse fiber contains at least one active fine cell and every inactive fiber contains none.

## 3. Existential block transform

For

`exists block . C(Z;G_1,...,G_q)`,

define

`Z_exists := { v in V : F_v subseteq Z }`

and

`G_j_exists := { v in V : F_v intersect (G_j \ Z) != empty }`.

### Theorem 1

On valid coarse supports,

`exists block . C(Z;G_1,...,G_q)`

is equivalent to

`C(Z_exists; G_1_exists,...,G_q_exists)`.

### Mechanism

After deleting the forbidden fine cells Z, take **all** remaining fine cells inside every active coarse fiber. This maximal allowed support is an existential witness iff any witness exists. A coarse fiber is impossible exactly when all its refinements were forbidden; a disequation is satisfiable exactly when some active coarse fiber retains an allowed fine cell belonging to its G_j.

This is the support-geometric form of the atomless clause-elimination phenomenon behind Asor's Theorem 3.2.

## 4. Universal block transform

For

`forall block . C(Z;G_1,...,G_q)`,

define

`Z_forall := { v in V : F_v intersect Z != empty }`

and

`G_j_forall := { v in V : F_v subseteq G_j }`.

### Theorem 2

On valid coarse supports,

`forall block . C(Z;G_1,...,G_q)`

is equivalent to

`C(Z_forall; G_1_forall,...,G_q_forall)`.

### Proof

An active coarse cell v permits every nonempty subset of its fiber as a fine refinement.

**Equations.** For the zero constraint to hold for *every* refinement, no forbidden fine cell may lie in an active fiber. Thus every v whose fiber intersects Z must be inactive, giving `Z_forall`.

**Disequation j.** We require every fine extension to hit G_j. If some active fiber is entirely contained in G_j, every extension must choose at least one cell from that fiber and therefore hits G_j. Conversely, if no active fiber is contained in G_j, each active fiber has at least one cell outside G_j; choose one such outside cell from every active fiber. The resulting legal extension avoids G_j completely, violating the disequation.

Hence the universal obligation is exactly

`OR_{v:F_v subseteq G_j} z_v`.

## 5. Closure under arbitrary quantifier alternation

Both Theorem 1 and Theorem 2 map a support clause

`C(Z;G_1,...,G_q)`

to another support clause with **the same q indexed disequation slots** (possibly some become trivial, impossible, or duplicates and can be removed).

Therefore a prenex formula

`Q_1 X_1 ... Q_b X_b . C`

where each `Q_i` is existential or universal and C is a conjunction of ABA equations/disequations can be eliminated from the innermost block outward while remaining in the same support-clause representation at every stage.

### Corollary 3 — no disequation proliferation

The number of positive support obligations never increases during quantifier elimination of this fragment.

This is stronger algorithmically than merely knowing the theory admits quantifier elimination.

## 6. Direct universal projection versus Tau's current dualization

At the inspected Tau commit `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`, `process_quantifier_block` handles a universal block by computing the existential elimination of the negated matrix and then negating the result.

For a conjunction of equation/disequation atoms, that dualization changes the Boolean shape before the anti-prenex machinery processes it.

Theorem 2 supplies a direct universal fast path that stays conjunctive throughout:

`conjunctive ABA clause -> conjunctive ABA clause`.

This is a concrete implementation hypothesis to benchmark. It is not yet evidence that the current Tau path is asymptotically worse on its internal DAG representation, because Tau has simplification and clause-specific fast paths of its own.

## 7. Linear-in-support-table elimination algorithm

Assume the initial atom supports Z and `G_1,...,G_q` have already been compiled as bitsets on a universe of size N.

One quantifier-block transform can be computed by scanning the fine fibers:

- existential: test `F_v subseteq Z` and, for each j, whether `F_v intersect (G_j\Z)` is nonempty;
- universal: test whether `F_v intersect Z` is nonempty and, for each j, whether `F_v subseteq G_j`.

This costs

`O((q+1) N)`

scalar cell-incidence operations for that stage.

If at least one BA variable is removed at each stage, support width drops by at least a factor 2. For successive widths

`N=N_0 > N_1 > ...`,

we have

`sum_i N_i < 2N`.

### Theorem 4 — prefix elimination complexity in explicit support coordinates

Given the initial support masks, an arbitrary alternating quantifier prefix over a single conjunction of ABA equations/disequations can be eliminated in

`O((q+1) N)`

cell-incidence work up to a constant factor independent of the number of alternation blocks, with

`O((q+1)N)`

bitset storage.

For pure ABA with K total BA variables,

`N=2^K`.

With finitely many interpreted constants C,

`N=rho(C) 2^K`.

Thus the fragment has a deterministic singly-exponential support-table algorithm in the total BA-variable count, while the full first-order theory of Boolean algebras has much higher known alternating-exponential complexity.

This does not contradict full-theory lower bounds: the restriction to a single conjunctive equation/disequation matrix is substantial.

## 8. Compiling the initial support masks

A Boolean term on K BA variables can be evaluated on every minterm valuation to obtain its support bitset. Straightforward compilation costs proportional to

`term_size * rho(C) * 2^K`

before machine-word parallelism.

Once all atoms are compiled, quantifier elimination uses only bitset projection operations; term syntax need not be revisited.

The output can remain as masks rather than materializing the potentially large join-of-minterms terms after every block.

## 9. ROBDD bound survives alternation stage-by-stage

At every stage the support clause has q or fewer positive clauses. By `ABA_CLAUSE_PROJECTION.md`, its ROBDD under any fixed support-variable order has at most

`N_i * 2^q`

nonterminal nodes at stage i.

Thus fixed q gives a protected family whose canonical support ROBDD remains linear in the current support width throughout arbitrary quantifier alternation.

This is a stronger statement than compactness of the extension relation alone.

## 10. Relation to existing theory

Asor's TABA chapter explicitly states that the atomless case is conceptually and algorithmically easy and gives an existential clause-elimination theorem of the form

`f(x)=0 AND AND_i g_i(x)!=0`.

So the existence of efficient atomless clause elimination is not new and must not be presented as an OrbitSynthesis discovery.

The research questions here are instead:

1. whether the support transforms are the most efficient executable form of those theorems inside Tau;
2. whether direct universal projection avoids real work compared with dualization;
3. whether retaining support masks across successive blocks and temporal/fixed-point operations yields a measurable advantage;
4. whether the `N_i 2^q` protected ROBDD bound can be leveraged to choose this backend automatically.

## 11. Falsification tests

1. Differential-test existential and universal transforms against Tau for generated prenex conjunctive formulas.
2. Compare direct universal projection against Tau's universal dualization on formulas designed to maximize negation/disjunction growth.
3. Search for a conjunctive formula that violates closure; any such example kills the theorem immediately.
4. Measure whether q remains small on real Tau specifications after normalization.
5. Benchmark materialized Tau terms versus retained support masks to ensure the speedup is not erased at the representation boundary.

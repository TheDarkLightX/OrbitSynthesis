# Universality and worst-case dynamics of ABA cell predecessors

**Status:** DERIVED embedding theorem plus classical monotone-map orbit bounds. The monotone-network results are classical; the contribution under investigation is the exact embedding into the ABA clause cell game and its consequences for OrbitSynthesis complexity.

This note supplies the adversarial counterpart to `ABA_CELL_GAME.md` and `ABA_SAFETY_BEKIC.md`.

The positive obligation transformer of the ABA safety fragment is not merely capable of small cycles seen in random tests. With enough environment coordinates it can implement **any monotone Boolean self-map** of the state-cell powerset that preserves the top element.

Therefore no representation trick can make the unrestricted fragment uniformly easy.

## 1. Abstract cell predecessor

Let V be a finite state-cell set, `|V|=N`.

For each current cell `v in V`, let `I_v` be its possible environment refinements. For every environment refinement `i in I_v`, let

`R_(v,i) subseteq V`

be the nonempty set of next-state cells that the system is allowed to choose.

The controllable predecessor on target sets is

`Pre(G)
 = { v : for every i in I_v,
         R_(v,i) intersect G != empty }.`

Each output coordinate `1[v in Pre(G)]` is a monotone positive CNF in the membership bits of G:

`AND_{i in I_v} OR_{w in R_(v,i)} 1[w in G].`

## 2. Every monotone coordinate predicate has this form

Let

`phi : P(V) -> {0,1}`

be monotone and satisfy `phi(V)=1`.

Take the inclusion-maximal false sets

`M(phi) = { X subset V : phi(X)=0 and no strict superset of X is false }`.

For each maximal false set X define the nonempty clause

`C_X := V \ X`.

### Lemma 1 — canonical positive CNF from maximal false sets

For every G subseteq V,

`phi(G)=1`

iff

`for every X in M(phi), G intersect C_X != empty`.

### Proof

If G is false, extend it to a maximal false set X. Then `G subseteq X`, so `G` misses `V\X=C_X`.

Conversely, if G misses C_X for some maximal false X, then `G subseteq X`; monotonicity implies G is false.

Since `phi(V)=1`, no maximal false set is V, so every C_X is nonempty.

Thus every top-preserving monotone Boolean predicate is exactly a robust-intersection condition of the ABA cell-predecessor form.

## 3. Universality theorem

Let

`F : P(V) -> P(V)`

be any monotone map with

`F(V)=V`.

For each output cell v, define

`phi_v(G)=1 iff v in F(G)`.

By Lemma 1, choose a positive CNF

`phi_v(G)=AND_j [G intersect C_(v,j) != empty]`.

Let

`m = max_v number_of_clauses(phi_v)`.

Choose e with

`2^e >= m`.

Use `2^e` environment refinements for every state cell. Assign the actual clauses C_(v,j) to distinct environment refinements; give every unused refinement the tautological allowed-next set V.

### Theorem 1 — monotone predecessor universality

There is a pure-ABA Step formula consisting of a **single equation** whose cell-level controllable predecessor satisfies

`Pre(G)=F(G)`

for every target set `G subseteq V`.

### ABA realization

Choose d with `N=2^d` for the pure no-constant case (or embed a smaller V into a power-of-two cell universe / use interpreted constant regions when desired).

Full Venn cells correspond to triples

`(current-cell v, environment refinement i, next-cell w)`.

Declare a full cell allowed exactly when

`w in C_(v,i)`.

Let Z_T be the set of all disallowed full cells. Since **every subset of the finite minterm-cell universe is the minterm support of a Boolean term**, take a term f whose support is Z_T and use the single Step equation

`f(state,input,next)=0`.

The equation forbids exactly Z_T. Every environment clause is nonempty, so the zero safety arena is all of V.

Then

`v in Pre(G)`

iff every environment refinement i has some allowed next w in G

iff every positive-CNF clause C_(v,i) intersects G

iff `phi_v(G)=1`

iff `v in F(G)`.

## 4. Consequence: ABA obligation dynamics contain arbitrary monotone Boolean networks

For the resulting zero-safe game, the OrbitSynthesis obligation transformer is simply

`barL=Pre=F`.

Thus any phenomenon possible for a synchronous monotone Boolean network on N bits can occur as positive-obligation dynamics inside a pure-ABA one-equation safety Step, subject only to the top-preserving condition `F(V)=V` (which is natural for a zero-safe arena).

This sharply limits what can be proved for the unrestricted fragment.

## 5. Periodic orbits are antichains

Let F be any monotone self-map of `P(V)` and suppose

`X_0,X_1,...,X_(p-1)`

is a periodic orbit of distinct sets.

### Theorem 2 — cycle antichain

The sets in a periodic orbit are pairwise incomparable by inclusion.

### Proof

Suppose `X_i proper-subset X_j`. Let k be the positive cyclic distance from i to j, so

`F^k(X_i)=X_j`.

Monotonicity gives

`F^k(X_i) subseteq F^k(X_j)`.

Because F acts as a permutation on the finite cycle, `F^k` is injective on its cycle points; distinct comparable points therefore remain **strictly** comparable after applying `F^k`.

Iterating `F^k` produces a strict inclusion chain around a finite orbit. Some positive power returns to X_i, yielding

`X_i proper-subset ... proper-subset X_i`,

a contradiction.

Hence a cycle is an antichain.

This fact is classical in monotone Boolean-network theory.

## 6. Sperner period bound

By Sperner's theorem, the largest antichain in `P(V)` has size

`binom(N, floor(N/2))`.

Therefore:

### Corollary 3

Every periodic orbit of an ABA obligation transformer satisfies

`period <= binom(N, floor(N/2))`.

Asymptotically,

`binom(N,N/2) = Theta(2^N / sqrt(N))`.

This improves the crude `2^N` bound on the **periodic part** of an obligation orbit.

It does not by itself bound the transient before the cycle by the same quantity.

## 7. The period bound is tight for general monotone maps

Let

`m=floor(N/2)`

and let

`A = {X subseteq V : |X|=m}`

be a middle layer, of size `binom(N,m)`.

Choose one cyclic permutation pi of all members of A.

Define F by

- `F(X)=empty` if `|X|<m`;
- `F(X)=pi(X)` if `|X|=m`;
- `F(X)=V` if `|X|>m`.

### Lemma 4

F is monotone and `F(V)=V`.

The only comparable distinct cardinality cases go from below the middle layer to the middle/upper layers or from the middle layer to above it; the images `empty`, a middle-layer set, and V preserve inclusion. Distinct middle-layer sets are incomparable, so pi is unconstrained there.

Hence the middle layer is one periodic orbit of exact length

`binom(N,m)`.

By Theorem 1, this F can be realized as an ABA cell predecessor with enough environment refinements.

### Corollary 5 — tight ABA period bound as a function of cell width

Allowing unrestricted Step term size and enough environment coordinates, the maximum possible periodic orbit length of ABA obligation dynamics on N state cells is exactly

`binom(N, floor(N/2))`.

## 8. Maximum canonical antichain and long fixed-point iteration

Take the tight construction above and add one Safe disequation whose initial positive mask is one middle-layer set `A_0`.

Its orbit under barL visits every middle-layer set.

All middle-layer sets are pairwise incomparable, so canonical normalization removes none of them.

After one full orbit, the fixed positive antichain is exactly the entire middle layer:

`H* = {X subseteq V : |X|=m}`.

Therefore the canonical support-clause representation reaches Sperner's maximum antichain size.

Moreover, ordinary positive fixed-point iteration adds a genuinely new nonredundant obligation at every step of the cycle until the full orbit has been collected.

So the clause safety solver can require

`binom(N, floor(N/2))`

strict positive-strengthening iterations in the unrestricted cell-width model.

For pure ABA with d state BA coordinates,

`N=2^d`,

so this worst case is essentially

`2^(2^d) / 2^(d/2)`,

which is double-exponential in d.

## 9. Input-size caveat

The tight monotone map above may require a very large positive-CNF representation and hence:

- many environment refinements;
- a large Step minterm term.

Thus Corollary 5 is a **state-cell-width worst case**, not automatically a matching lower bound in the compact Tau source-formula length.

This distinction is essential.

The next lower-bound question is to construct compact Step formulas whose cell predecessor has provably long obligation orbits.

Simple deterministic permutations already yield nontrivial long cycles with much smaller descriptions, but their sharp source-size/orbit-length tradeoff remains to be analyzed.

## 10. Backend consequence

No single universal polynomial-time algorithm in N can solve the positive orbit phase for arbitrary explicitly represented monotone dynamics unless it exploits a representation that can summarize these long orbit closures without enumerating the antichain—and the final canonical clause itself can require Sperner-width output.

Therefore the correct OrbitSynthesis objective is structural classification:

- detect easy transition classes;
- retain compact symbolic representations when possible;
- accept unavoidable large outputs in adversarial cases;
- avoid blaming implementation when the semantic target itself is huge.

## 11. Literature positioning

The antichain bound and existence of long periodic orbits in monotone/cooperative Boolean networks are classical; modern reviews explicitly note that periodic orbits of monotone Boolean systems are antichains and appeal to Sperner's theorem.

Relevant modern sources include work on cooperative/monotone Boolean networks and the interaction-graph literature. The exact reduction of arbitrary top-preserving monotone dynamics to the ABA cell predecessor is the part that must be compared against prior Tau/Boolean-algebra synthesis literature before any novelty claim.

## 12. Next targets

1. Find compact Tau/ABA Step formulas with provably superpolynomial obligation periods.
2. Characterize Step syntax that makes barL extensive or contractive, forcing <=N-step convergence.
3. Use monotone-network interaction graphs to bound period/orbit complexity from transition locality.
4. Determine transient-length bounds in addition to periodic-length bounds.
5. Compare interaction-graph parameters with support-CNF crossing width from `SUPPORT_OBDD_WIDTH.md`.

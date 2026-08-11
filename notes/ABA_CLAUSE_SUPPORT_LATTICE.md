# ABA clause regions as canonical upward-closed support families

**Status:** DERIVED finite support characterization; standard monotone-Boolean / hypergraph blocker duality is used and not claimed novel. The relevance is to identify the exact semantic carrier preserved by the ABA clause safety recurrence.

## 1. Support universe

Fix k Boolean-algebra variables and let

`U={0,1}^k`

be their n=`2^k` Venn-cell labels.

A complete ABA k-type is a nonempty support

`S subseteq U`.

A normalized ABA clause

`f=0 AND AND_i g_i!=0`

has support semantics

`R(A;H)
 = { nonempty S subseteq A : S intersects H for every H in H }`,

where

- A is the complement of the minterm support of f;
- H is the family of minterm supports of the inequation terms, restricted to A.

## 2. Exact semantic characterization

### Theorem 1

A nonempty family

`F subseteq P(U) \ {empty}`

is definable by one normalized ABA equation-plus-inequations clause iff, with

`A := union F`,

it is upward closed inside A:

`S in F and S subseteq T subseteq A  ==>  T in F`.

### Proof: clause to upset

If `S in R(A;H)` and `S subseteq T subseteq A`, then every hit witnessed by S is also witnessed by T. Thus T satisfies the same clause.

### Proof: upset to clause

Let

`L := P(A) \ F`

be the losing support family. Because F is upward closed, L is downward closed.

Let

`MaxLose(F)`

be the inclusion-maximal elements of L. Since F is nonempty, A itself is winning and no maximal losing set equals A.

For each maximal losing set M define

`H_M := A \ M`,

which is nonempty.

Then a nonempty support S contained in A is winning iff it is not contained in any losing maximal set M, iff

`S intersects (A\M) != empty`

for every M in `MaxLose(F)`.

Thus

`F = R(A; {A\M : M in MaxLose(F)}).`

Every subset of U is the minterm support of some Boolean term, so these hit sets are represented by ordinary ABA inequations.

## 3. Unique prime hit antichain

The maximal losing supports form an antichain. Taking complements inside A reverses inclusion, so

`PrimeHit(F) := { A\M : M in MaxLose(F) }`

is also an antichain.

### Theorem 2

For nonempty F, the pair

`(A, PrimeHit(F))`

is the unique irredundant equation-plus-positive-hit CNF representation of F at the support level.

Equivalently:

- A is uniquely recovered as `union F`;
- each prime hit set is uniquely the complement of one maximal losing support.

This justifies canonical equality testing of clause regions by comparing A and the sorted inclusion-minimal hit antichain.

## 4. Dual minimal-winning representation

Let

`MinWin(F)`

be the inclusion-minimal supports in F.

Because F is upward closed, it is also uniquely determined by this antichain:

`F = { T subseteq A : exists W in MinWin(F), W subseteq T }.`

The two canonical antichains are transversal/blocker duals:

`MinWin(F) = Tr(PrimeHit(F))`

and, for the Sperner hypergraph `PrimeHit(F)`,

`PrimeHit(F) = Tr(MinWin(F))`.

Here `Tr(H)` denotes the family of inclusion-minimal hitting sets (minimal transversals) of H.

Thus every clause region has two dual extremal descriptions:

1. **prime-hit CNF:** what every support must hit;
2. **minimal-winning DNF:** which minimal supports suffice to win.

## 5. Maximal-losing representation

A third equivalent antichain is

`MaxLose(F) = { A\H : H in PrimeHit(F) }`.

This can be useful when losing supports are structurally simpler than hit sets.

The semantic test is

`S in F iff S subseteq A and for every M in MaxLose(F), S not subseteq M`.

## 6. Representation portfolio

The three canonical antichains can have very different sizes.

A solver should not assume one is always best:

- prime hits are natural for `ABA_CLAUSE_SAFETY_RECURRENCE.md` because predecessor transports each hit independently;
- minimal winners may be better for witness search or enumeration;
- maximal losers may be better for counterexample generation and exclusion checks.

Converting prime hits to minimal winners is the classical hypergraph transversal/dualization problem and can itself be expensive. Representation switching therefore needs a cost model; it is not a free optimization.

## 7. Relation to monotone Boolean functions

Fix A. Introduce support variables `z_a` for `a in A`.

The region is the monotone CNF

`AND_{H in PrimeHit(F)} OR_{a in H} z_a`.

Its minimal true assignments are `MinWin(F)`.

Therefore clause regions over a fixed A are exactly monotone Boolean functions on the support bits, excluding the all-zero support when necessary.

This explains both:

- why antichains are the correct finite representation; and
- why worst-case compression cannot be guaranteed: arbitrary monotone Boolean functions can have very large prime or minimal-model antichains.

## 8. Dedekind/Sperner warning

For n=|A| support bits, the number of possible upward-closed families is the Dedekind-number scale: the same combinatorial universe as monotone Boolean functions.

A largest single antichain has size

`binom(n, floor(n/2))`

by Sperner's theorem.

Since n=`2^k`, this can already be enormous as a function of BA arity k.

Thus the hypergraph carrier is semantically exact but not universally succinct.

## 9. Why the safety recurrence is special despite this worst case

`ABA_CLAUSE_SAFETY_RECURRENCE.md` does not manipulate an arbitrary monotone Boolean function by generic Boolean operations.

Its prime-hit recurrence is structured:

`A_(t+1)=P(A_t)`

and

`H_(t+1)=Min( J(A_t) union P[H_t] )`.

Each old prime hit is transported independently by the same finite cube predecessor P; transition inequations inject only q new candidate hits per iteration before subsumption.

That additional dynamical structure is the place to seek parameterized bounds beyond generic Dedekind/Sperner worst cases.

## 10. Connection to established antichain algorithms

Antichain representations are standard in verification, automata, and games when winning/configuration sets are monotone under a partial order. Recent work also combines antichains with SAT and efficient subset/subsumption data structures.

OrbitSynthesis should import those implementation techniques rather than claim antichains themselves as a contribution.

The ABA-specific contribution candidate is the derivation that normalized ABA clauses land exactly in this support-upset lattice and that the reactive predecessor has the closed support-hypergraph transform proved in the companion notes.

## 11. Useful implementation operations

For the prime-hit representation:

- membership: subset-of-A plus one intersection test per hit;
- implication/inclusion between regions: monotone-CNF subsumption tests;
- canonicalization: remove duplicate and inclusion-nonminimal hits;
- counterexample support: use a maximal losing set A\H when one prime clause is violated;
- witness minimization: compute minimal transversals only on demand.

For large antichains, import trie/SAT/ZDD techniques rather than storing naive Python/C++ vectors.

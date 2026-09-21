# Canonical support-clause representation

**Status:** DERIVED finite-set theorem; exhaustive small-universe checks are straightforward and will be included with the safety prototype. This is a representation theorem, not a claim about all first-order ABA formulas.

## 1. Support clauses over a finite cell universe

Let V be a finite set of support cells. A valid ABA support is a nonempty subset

`S subseteq V`.

Represent a conjunctive equation/disequation formula by

`C(Z; H_1,...,H_q)`

with semantics

`S models C`

iff

1. `S intersect Z = empty`; and
2. `S intersect H_j != empty` for every j.

Z is the forbidden/zero support mask; each H_j is a positive nonzero obligation.

## 2. Normalization

Let

`A := V \ Z`

be the allowed support cells.

Normalize as follows.

1. If A is empty, return `False`.
2. Replace every H_j by

   `H_j := H_j intersect A`.

   Forbidden cells can never witness a disequation.
3. If any H_j becomes empty, return `False`.
4. Drop every H_j equal to A: validity already says the support is a nonempty subset of A and therefore hits A.
5. Remove duplicates.
6. If `H_i subset H_j`, drop H_j. Hitting the smaller set already implies hitting the larger set.

The surviving family H is an antichain of nonempty proper subsets of A.

Call `(Z,H)` a **normalized support clause**.

## 3. Satisfiability becomes trivial after normalization

### Theorem 1

Every normalized support clause other than `False` is satisfiable.

### Proof

Take the support `S=A`. It is nonempty, avoids Z, and intersects every nonempty H_j contained in A.

This explains why there is no additional Hall/matching condition at the level of the already-expanded support clause: all fine-cell compatibility has been compiled into the cell universe and projection rules.

## 4. Entailed positive clauses

Fix a normalized `(Z,H)` and work inside the allowed universe A.

For a subset `K subseteq A`, let

`Hit(K)`

mean the positive clause `S intersect K != empty`.

### Theorem 2 — entailment criterion

If `K != A`, then

`C(Z,H) entails Hit(K)`

iff

there exists `G in H` with

`G subseteq K`.

### Proof

**If.** Hitting G implies hitting every superset K.

**Only if.** Suppose no G is contained in K. Since K is proper, the support

`S=A\K`

is nonempty. Every G has some element outside K, so S intersects every G. Thus S satisfies C. But S is disjoint from K, so it falsifies `Hit(K)`.

The exceptional clause `Hit(A)` is entailed solely from support validity and is why normalization drops H_j=A.

## 5. Recovering the forbidden mask from semantics

### Theorem 3

For a satisfiable normalized support clause,

`Z = {v in V : no satisfying support contains v}`.

### Proof

No satisfying support contains a forbidden v by definition. Conversely the satisfying support A from Theorem 1 contains every v not in Z.

Thus Z is semantically unique.

## 6. Recovering the positive antichain from semantics

By Theorem 2, the inclusion-minimal proper positive clauses entailed by C are exactly the members of H.

Because H is an antichain, no member contains another. Every other entailed proper positive clause contains some member of H.

Therefore H is also semantically unique.

## Theorem 4 — canonicality

Two satisfiable normalized support clauses define the same family of valid supports iff their forbidden masks Z are equal and their positive antichains H are equal.

Together with a unique `False` representation, normalized support clauses form a canonical representation of this fragment.

### Consequence

Semantic equivalence testing for the clause fragment requires no theorem prover, BDD, or explicit type enumeration:

`normalize(C1) == normalize(C2)`

iff

`C1` and `C2` are equivalent on complete ABA support types.

## 7. Logical ordering between normalized clauses

For normalized clauses C1=(Z1,H1), C2=(Z2,H2), C1 semantically implies C2 iff:

1. `Z2 subseteq Z1`; and
2. for every `K in H2` not made automatically true by C1's validity restriction, C1 entails `Hit(K)` after restricting K to `V\Z1`.

Using Theorem 2 this reduces to subset tests between masks.

A specialized implementation can therefore test inclusion of winning-region approximants without enumerating supports.

The exact formula should be coded and exhaustively checked before being promoted as an API contract; equality/canonicality is the first required operation.

## 8. Size of the canonical family

The antichain H can itself be large. By Sperner's theorem, an antichain of subsets of an N-element allowed universe can have size as large as

`binom(N, floor(N/2))`.

So canonicality does not magically make the full fragment small.

However:

- quantifier projection never multiplies the number of positive obligations;
- conjunction adds the two obligation families and then antichain normalization removes redundant supersets;
- many structured Tau formulas may therefore remain compact even though worst-case antichains are huge.

This is another reason to keep a representation portfolio and explicit cost measurements.

## 9. Data structure

For support width N, a practical canonical clause can be represented as:

- one N-bit forbidden mask Z;
- a sorted/deduplicated list of N-bit positive masks H;
- a distinguished False bit.

Normalization is dominated by subset-minimization of H. Naively this is quadratic in |H|; tries, ZDDs, bitset indexes, or width-aware methods may be appropriate for large families.

## 10. Noether-style mechanism

The canonical representation exists because the fragment has two one-sided semantic forces:

- equations can only **forbid** support cells;
- disequations can only require the support to **hit** specified sets.

Once forbidden cells are removed, adding more allowed nonzero cells can never break the formula. The semantics is therefore an upward-closed family inside a fixed allowed Boolean cube, and its minimal positive hitting obligations are exactly the irredundant clauses.

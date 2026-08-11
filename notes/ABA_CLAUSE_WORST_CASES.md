# Worst-case lower bounds for the ABA clause safety recurrence

**Status:** DERIVED extremal constructions; bounded constructions checked computationally; Landau asymptotic is classical. These are negative results: they delimit what the direct hypergraph backend can promise.

Let

`n=2^k`

be the number of Boolean Venn-cell labels of a k-variable ABA state.

`ABA_CLAUSE_SAFETY_RECURRENCE.md` represents a winning approximation by an allowed set A and a canonical antichain H of nontrivial hit sets.

This note shows that neither **one inequation** nor **deterministic dynamics** is enough to make H small in general.

## 1. Every suitable monotone set map is a cube predecessor

Let S be an n-element finite state-label set.

### Lemma 1 — predecessor representation

Let

`F : P(S) -> P(S)`

be any monotone map with

`F(empty)=empty`.

Then there is a finite environment-label set I and an allowed relation

`L subseteq S x I x S`

such that the ordinary cube predecessor

`P_L(B) = {a : for every u in I, exists v in B . (a,u,v) in L}`

satisfies

`P_L(B)=F(B)`

for every B.

Moreover I can be padded to power-of-two size, hence encoded by finitely many Boolean input variables.

### Proof

Fix a state a. The coordinate predicate

`phi_a(B) := [a in F(B)]`

is a monotone Boolean function of the membership bits of B and is false at the all-zero assignment.

Every such function has a positive CNF representation

`phi_a(B) = AND_{C in C_a} [B intersects C != empty]`.

One canonical choice takes C to be complements of inclusion-maximal false assignments. The identically-false coordinate is represented by one empty clause.

Let m be the largest number of clauses needed by any coordinate and choose a common input set I of power-of-two size at least m. For coordinate a, assign each input u one clause-neighborhood C; pad unused positions by S, whose clause is tautological on every nonempty B and does not disturb the required false-at-empty behavior.

Put

`(a,u,v) in L iff v belongs to the assigned clause-neighborhood.`

Then the `forall u exists v in B` condition is exactly the positive CNF above.

## 2. A maximum-antichain cycle

Let

`r=floor(n/2)`

and enumerate every r-subset of S as

`C_0,...,C_(M-1)`,

where

`M=binom(n,r)`.

Define

`F(B) := union { C_(i+1 mod M) : C_i subseteq B }`.

### Lemma 2

F is monotone, `F(empty)=empty`, `F(S)=S`, and

`F(C_i)=C_(i+1 mod M)`.

### Proof

Monotonicity is immediate. No C_i is empty, so F(empty)=empty. Every element of S belongs to some middle-layer C_i, so F(S)=S.

Because the C_i form an antichain of equal size, the only enumerated C_j contained in C_i is C_i itself. Hence F(C_i)=C_(i+1).

By Lemma 1, realize F as a cube predecessor P_L of one finite Boolean game.

## 3. One transition inequation generates a full Sperner antichain

Choose one transition hit relation G that, along the allowed relation L, is enabled exactly on current state labels in C_0:

`G := { (a,u,v) in L : a in C_0 }`.

Because `P_L(S)=S`, its transition-hit injection at the top allowed set is

`J_G(S)=C_0`.

Start the ABA clause safety iteration from

`A_0=S`, `H_0=empty`.

Since P_L(S)=S, the allowed set never changes. The hit recurrence is

`H_(t+1)=CanonHits(S, {C_0} union P_L[H_t]).`

### Theorem 1 — Sperner-width dynamic blowup

For `0<=t<=M`,

`H_t = {C_0,...,C_(t-1)}`

(up to cyclic enumeration convention).

Therefore:

- the canonical hit antichain reaches exactly
  `binom(n,floor(n/2))` members;
- there are that many strict winning-region refinements before stabilization;
- this happens with **one transition inequation**.

### Proof

Induct using P_L(C_i)=C_(i+1). Every C_i has the same proper size r, so no distinct one contains another and canonical subsumption deletes none.

Each newly added clause is semantically strict. To satisfy all earlier hits while violating new C_t, use support

`S \ C_t`.

For every earlier C_i != C_t, equal cardinality implies `C_i` has an element outside C_t, so `S\C_t` hits C_i. It misses C_t. Hence the new hit is not implied by the previous family.

After all M middle-layer sets are present, cyclic transport plus reinjection reproduces the same family.

## 4. Scale relative to complete ABA types

The ABA state has

`2^n-1`

complete support types.

The Sperner lower bound is

`binom(n,floor(n/2)) = Theta(2^n/sqrt(n)).`

With `n=2^k`, this is

`2^(2^k - k/2 + O(1))`.

Thus even the normalized one-equation/one-inequation safety fragment can force fixed-point refinement at essentially the same double-exponential scale as the full complete-type space, up to a polynomial factor in n.

This kills any universal polynomial or singly-exponential-in-k bound for the explicit hit-antichain backend.

## 5. Stronger natural restriction: deterministic and input-free

The previous construction may need many environment labels to realize an arbitrary monotone F. Perhaps determinism and no environment would force small hit dynamics.

It does not.

Let

`delta : S -> S`

be a permutation. Use a transition equation that forces the next Boolean state label to be exactly `delta(a)`.

There is no input. The cube predecessor is simply

`P(B)=delta^(-1)(B)`.

Choose a subset C whose orbit under delta has the full permutation order. For example, choose one distinguished element in every cycle of delta; the orbit period of their union is the least common multiple of the cycle lengths, exactly the order of delta.

Use one transition inequation whose state-label support is C.

Then A stays equal to S and the canonical hit family after t rounds is

`{ C, delta^(-1)(C), ..., delta^(-(t-1))(C) }`

until the orbit closes.

All orbit sets have equal cardinality, so distinct sets are incomparable and no subsumption occurs.

## 6. Landau lower bound

Let g(n) be Landau's function: the maximum order of a permutation of n elements.

Choose delta of order g(n) and C as above.

### Theorem 2 — deterministic one-inequation lower bound

There exists an input-free deterministic ABA clause safety game with one transition inequation whose canonical hit family and strict Kleene refinement length are at least

`g(n)`.

Classically,

`log g(n) ~ sqrt(n log n)`.

Therefore, for `n=2^k`, the lower bound is

`exp(Theta(2^(k/2) sqrt(k)))`.

So even deterministic input-free one-inequation games do not admit a polynomial-in-n fixed-point/antichain bound.

## 7. Formula size of the deterministic construction

An arbitrary permutation delta on `n=2^k` Boolean labels can be encoded by k Boolean truth functions. A direct DNF representation uses O(kn) minterm occurrences, and the k output equalities can be squeezed into one BA equation.

The single hit set C is one Boolean term.

Thus the Landau construction gives superpolynomial fixed-point growth even against a straightforward singly-exponential-in-k truth-table/DNF description of the deterministic transition.

This is stronger algorithmically than the unrestricted Sperner construction, whose positive-CNF realization may require many input labels.

## 8. Concrete bounded checks

`experiments/aba_clause_worst_cases.py` contains:

1. n=4 (`k=2`) Sperner construction cycling all six 2-subsets;
   - the derived positive-CNF predecessor uses four input labels;
   - the hit family grows 0,1,...,6 and then stabilizes;
2. n=8 (`k=3`) deterministic permutation with cycle lengths 5 and 3;
   - permutation order 15;
   - one two-element hit set has orbit size 15;
   - all 15 hits are incomparable and persist.

## 9. Research consequence

Do **not** use any of the following as a proposed sufficient condition for efficient clause synthesis:

- one inequation;
- bounded inequation count alone;
- deterministic transition alone;
- input-free transition alone.

Positive theorems must restrict the structure of P more substantially, e.g. by a class with bounded orbit complexity, bounded-width invariant families, special graph structure, or measured Tau-specific incidence properties.

## 10. Next positive targets

The lower bounds suggest looking for assumptions that explicitly kill the constructions above:

1. acyclic equation-safe cell transition graphs;
2. bounded DAG depth after quotienting SCCs;
3. predecessor maps whose iterates are eventually nested rather than cyclic;
4. laminar hit families preserved by P;
5. bounded treewidth/pathwidth of the support transition incidence structure;
6. symmetry quotients in which P-orbits collapse to few classes.

Each candidate should first be tested against the permutation and Sperner adversaries in this note.

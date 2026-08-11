# Structure-preserving support encoding for ocLTL over atomless Boolean algebra

**Status:** DERIVED equirealizability-preserving re-encoding for the pure ABA three-variable presentation; the outer reduction follows Asor's ocLTL Theorem 10, while the support formulas are derived here. Not yet Lean-checked or integrated with an LTL synthesizer.

## 0. What is and is not new in this direction

Asor's ocLTL paper already gives a generic binary encoding (§5.1): instead of one proposition per complete type, encode a `T_2` or `T_3` type by its binary index. For ABA,

`|T_2|=15` and `|T_3|=255`,

so the generic information counts are already 4 and 8 bits.

The point of the ABA support encoding is **not** to beat those bit counts. In fact it attains the same optimal counts for a structural reason.

The difference is that the bits have semantics:

- a `T_2` code bit says a particular `(m,x)` Venn cell is nonzero;
- a `T_3` code bit says a particular `(m,x,y)` Venn cell is nonzero.

Restriction, temporal memory shift, data predicates, and type extension then become direct Boolean operations on the code bits rather than lookup tables on arbitrary type numbers.

## 1. The support codes are information-theoretically optimal

For pure ABA,

`|T_k|=2^(2^k)-1`.

For `k>=1`, any injective binary code for all complete k-types needs at least

`ceil(log2 |T_k|) = ceil(log2(2^(2^k)-1)) = 2^k`

bits.

The Venn-support code uses exactly one bit for each of the `2^k` minterm cells, hence exactly `2^k` bits.

### Theorem 1 — minimum-width binary type code

The ABA support representation is a minimum-width binary encoding of complete k-types.

Its only invalid bit pattern is the all-zero vector; every nonzero vector is a realized complete type.

For the ocLTL three-variable presentation:

- `T_1`: 2 support bits, 3 nonzero codes;
- `T_2`: 4 support bits, 15 nonzero codes;
- `T_3`: 8 support bits, 255 nonzero codes.

Thus it achieves exactly the generic binary lower bound while retaining the minterm geometry.

## 2. Full-state support reduction

Use variable order `(m,x,y)`.

### Input propositions

For each `(a,b) in {0,1}^2`, let

`P_ab`

mean that the `(m=a,x=b)` Venn cell is nonzero. The four input bits encode the complete `T_2` type of `(m,x)`.

Input validity is simply

`Valid_P := OR_{a,b} P_ab`.

### Output propositions

For each `(a,b,c) in {0,1}^3`, let

`Q_abc`

mean that the `(m=a,x=b,y=c)` Venn cell is nonzero. The eight output bits encode the complete `T_3` type of `(m,x,y)`.

Output validity is

`Valid_Q := OR_{a,b,c} Q_abc`.

When the output is required to extend a valid input, `Valid_Q` follows automatically from the row-projection equations below.

## 3. Type restriction becomes four local OR equations

The full `(m,x,y)` type restricts to the declared `(m,x)` type exactly when

`RowCompat(P,Q)
 := AND_{a,b} [ P_ab <-> (Q_ab0 OR Q_ab1) ].`

This is the same local ABA extension relation studied in `ABA_EXTENSION_ROBDD.md`, with four coarse cells.

No list of the 255 complete 3-types is required.

## 4. Successor-memory compatibility becomes two OR equations

The current output `y_t` becomes the next memory `m_(t+1)`.

The current y-support is

`Y_0(Q) := OR_{a,b} Q_ab0`

`Y_1(Q) := OR_{a,b} Q_ab1`.

The memory component of the next `(m,x)` input support is

`M_0(P') := P'_00 OR P'_01`

`M_1(P') := P'_10 OR P'_11`.

Hence Asor's temporal compatibility condition `Psi_I` becomes exactly

`MemoryCompat :=
   [Y_0(Q) <-> X M_0(P)]
   AND
   [Y_1(Q) <-> X M_1(P)].`

Here `X` is LTL next.

Again, no `T_1`, `T_2`, or `T_3` restriction table is needed.

## 5. Data formulas compile directly to support formulas

Let a data formula `delta(m,x,y)` be reduced to the ABA support Boolean function

`hat(delta)(Q_000,...,Q_111)`

using `ABA_SUPPORT_BOOLEANIZATION.md` (including its quantified projection procedure if delta itself has first-order quantifiers).

Then the ocLTL substitution is simply

`delta  -->  hat(delta)(Q)`.

For an atomic Boolean term equation `f=0`, if `A_f subseteq {0,1}^3` is its minterm support, this is especially simple:

`hat(f=0) = AND_{v in A_f} NOT Q_v`.

Thus evaluating a data formula does not require a disjunction over the complete 3-types satisfying it.

## 6. Full support-coded LTL translation

Let `phi^supp` be the original ocLTL formula with each data formula replaced by its support Boolean translation.

Define

`Assume := G(Valid_P AND MemoryCompat)`

and

`Guarantee := phi^supp AND G(RowCompat(P,Q))`.

Then use

`hat(phi)_supp := Assume -> Guarantee`.

The `P_ab` propositions are environment inputs and the `Q_abc` propositions are system outputs.

### Theorem 2 — equirealizability

For pure ABA in Asor's three-variable setup, the original ocLTL specification is realizable iff `hat(phi)_supp` is realizable.

### Proof

The support code is a bijection between complete ABA k-types and nonzero `2^k`-bit vectors.

- `RowCompat` is exactly the complete-type restriction condition `tau|_(m,x)=sigma`.
- `MemoryCompat` is exactly equality of the current y 1-type and the next m 1-type.
- `hat(delta)` has the same truth value as delta on every realized tuple.

Therefore replacing Asor's type names by their support codes preserves every condition in the proof of ocLTL Theorem 10. Concrete witness reconstruction follows from the same extension property; in ABA it can additionally be realized explicitly by splitting the nonzero `(m,x)` cells according to the selected `Q` refinements.

## 7. Variable count versus Asor's generic binary encoding

The full support-coded three-variable reduction uses

- 4 input propositions;
- 8 output propositions;

for a total of 12 type-code propositions.

This is exactly the same count as Asor's generic binary encoding:

`ceil(log2 15) + ceil(log2 255) = 4+8 = 12`.

So the advantage is **structural constraint complexity**, not proposition count.

An arbitrary numerical binary code still needs Boolean logic implementing:

- which 3-type numbers restrict to which 2-type numbers;
- which y 1-type each 3-type induces;
- which type numbers satisfy each data formula.

The support code computes these by fixed OR/projection formulas and minterm-support formulas.

## 8. Support implementation of the §5.2 T3-avoidance optimization

Asor §5.2 uses outer variables consisting of:

- an input `T_2` code `sigma`;
- a successor-memory `T_1` code `rho`;
- one Boolean `D_i` for each data formula `delta_i`.

It then precomputes whether every combination `(sigma,rho,D-pattern)` is feasible by asking whether some complete 3-type witnesses it.

For ABA the same feasibility relation can be written **without enumerating T_3 or enumerating all outer combinations**.

Let:

- `P_ab` be the four support bits for sigma;
- `R_c` be the two support bits for rho (c=0,1);
- `D_i` be the declared truth bit for delta_i;
- `Q_abc` be eight *existential auxiliary support bits* for a possible complete 3-type.

Define

`Feas(P,R,D)
 := exists Q .
      RowCompat(P,Q)
      AND ColCompat(R,Q)
      AND AND_i [D_i <-> hat(delta_i)(Q)]`,

where

`ColCompat(R,Q)
 := [R_0 <-> OR_{a,b}Q_ab0]
    AND [R_1 <-> OR_{a,b}Q_ab1].`

When the outer `P` and `R` codes are valid nonzero support codes, every satisfying `Q` is a realizable complete ABA 3-type, and every concrete witness produces such a `Q`.

### Theorem 3 — exact feasibility equivalence

For every valid support codes `P,R` and truth pattern `D`,

`Feas(P,R,D)`

holds iff Asor's precomputed formula

`exists m,x,y . sigma(m,x) AND rho(y) AND Delta^D(m,x,y)`

holds in ABA.

### Proof

A satisfying `Q` is exactly a nonzero support of a tuple `(m,x,y)` whose row projection is sigma, whose y-column projection is rho, and on which each `delta_i` has the declared truth value. Realizability of every valid ABA support provides the concrete tuple. The converse takes the tuple's support.

## 9. Why Theorem 3 matters computationally

Asor's displayed §5.2 guard is written as a conjunction over

`(sigma,rho,A) in T_2 x T_1 x {false,true}^|Delta|`,

with each infeasible combination becoming a forbidden-pattern clause.

For pure ABA that index set has size

`45 * 2^|Delta|`.

The support formulation instead starts from a quantified Boolean circuit with:

- 4 `P` bits;
- 2 `R` bits;
- `|Delta|` D bits;
- 8 existential `Q` bits;
- four local row equations;
- two column equations;
- `|Delta|` data-link equations.

One can existentially abstract the eight Q bits offline using an ROBDD, ZDD, SAT/QBF elimination, or another Boolean DAG, obtaining exactly the same outer feasibility Boolean function.

This **does not contradict** Asor's observation that full `T_3` information can be necessary in the worst case. An arbitrary Boolean function of the eight support bits can still encode all 255 type distinctions and can still have large symbolic representations. The gain is avoiding mandatory explicit type/table enumeration when the support circuit stays compact.

## 10. A representation portfolio rather than one encoding

The two ABA-specific reductions have complementary regimes:

### Full-support reduction

Outer type variables: `4+8=12`.

Pros:
- no feasibility elimination;
- data predicates evaluate directly;
- compatibility is local;
- output support can be used directly for witness construction.

### T3-avoiding support reduction

Outer type/data variables: `4+2+|Delta| = 6+|Delta|`, matching Asor's optimized binary count.

Pros:
- fewer outer variables when `|Delta|<6`;
- full type hidden behind symbolic existential abstraction.

Cost:
- `Feas(P,R,D)` must be symbolically projected.

Thus a compiler can choose based on the measured symbolic cost rather than committing to one normal form.

## 11. Generalization to interpreted constants

For a finite interpreted-constant set C with constant-partition rank `rho(C)`, refine every support bit by a constant region as in `ABA_INTERPRETED_CONSTANTS.md`.

Then:

- `(m,x)` input support width: `4 rho(C)`;
- `(m,x,y)` full support width: `8 rho(C)`;
- all projection constraints remain local inside each constant region;
- each constant region must have at least one active variable minterm.

The same two reductions therefore extend to Asor's interpreted-constant ABA setting.

The cost is governed by `rho(C)`, not merely by the number of named constants.

## 12. Next tests

1. Build both support-coded ocLTL reductions for generated ABA specifications.
2. Differentially compare feasibility against explicit enumeration of all 255 `T_3` supports for the pure three-variable case.
3. Compare the BDD size of `Feas(P,R,D)` against the explicit `45*2^|Delta|` forbidden-pattern table.
4. Compare against generic numerical binary coding using identical LTL synthesis backends.
5. Search for formula classes where the support feasibility BDD has provably polynomial size in the support-bit dimension and `|Delta|`.
6. Integrate the support reduction with the direct safety fixed-point engine so the same representation serves both ocLTL compilation and direct fixed-point fragments.

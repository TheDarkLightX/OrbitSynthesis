# Atomic ABA predicates as generalized group testing

**Status:** structural equivalence DERIVED; exact fiber theorem DERIVED; finite checks implemented separately; not yet Lean-checked.

This note refines `ABA_OCLTL_FIBERS.md` by distinguishing two very different notions of a "predicate bit":

1. an **arbitrary ABA-definable predicate** on complete types; versus
2. an **atomic Boolean-algebra equation/inequation**, such as `f=0`, `f!=0`, `f=g`, or `f<=g`.

The first can realize an arbitrary subset of the finite type space. The second has a much more rigid structure.

## 1. Minterm support turns equations into intersection tests

Fix `k` Boolean-algebra variables and let

`U_k = {0,1}^k`

be the set of `2^k` Boolean minterm cells.

A complete ABA k-type is a nonempty support `S subseteq U_k`, where `v in S` means the minterm cell `C_v` is nonzero.

Every Boolean term `f` has a unique minterm support

`A_f subseteq U_k`

such that `f` is the join of the cells in `A_f`.

Because distinct minterm cells are disjoint,

`f(S) = 0  iff  S intersect A_f = empty`.

Equivalently,

`f(S) != 0  iff  S intersect A_f != empty`.

Thus an atomic equation is exactly a **group test** on the unknown support.

Common atomic relations reduce to the same form:

- `f = g` iff `(f XOR g)=0`;
- `f <= g` iff `f & complement(g)=0`;
- a finite conjunction `f_1=0 and ... and f_m=0` iff `(f_1 join ... join f_m)=0`.

So grouping several zero-equations conjunctively does not escape the group-testing model.

## 2. Exact equivalence with generalized non-adaptive group testing

Let `E subseteq P(U_k) \ {empty}` be any finite family of candidate complete types.

Choose atomic tests `A_1,...,A_d subseteq U_k`. The signature of an unknown support `S in E` is

`sig(S)_j = 1[S intersect A_j != empty]`.

The tests identify every candidate exactly iff `sig` is injective on `E`.

This is precisely the generalized non-adaptive group-testing problem for hypergraph `(U_k,E)`: the unknown "defective set" is one of the supports in `E`, and a test returns whether it intersects the tested pool.

Reference: Gonen, Langberg, Sprintson, *Group Testing on General Set-Systems*, arXiv:2202.04988 (2022), Definition 2.

### Complexity corollary

Define `ABA-ATOMIC-SEPARATION`:

> Input: an explicitly listed finite candidate family `E` of ABA support types and integer `d`. Decide whether `d` atomic Boolean-term zero/nonzero tests separate all candidates.

This problem is NP-complete under the explicit-support encoding.

**Reason.** Membership in NP is immediate from a list of `d` query supports. For hardness, embed any generalized group-testing instance `(V,E)` into minterm cells of `U_k` with `2^k >= |V|`; candidate supports use only the embedded cells. Every group test is represented by the Boolean term equal to the join of the corresponding minterms, and every Boolean term induces exactly one group test after restricting to the embedded cells. Therefore the optimum is preserved. Gonen-Langberg-Sprintson prove the generalized optimization problem NP-hard.

This is a complexity transfer, not claimed as an independent hardness technique.

## 3. Join-semilattice form: the inner algebraic mechanism

Given `d` atomic tests, assign each cell `v in U_k` a column code

`c(v) in {0,1}^d`,

where coordinate `j` is 1 exactly when `v in A_j`.

Then the signature of a support is

`sig(S) = OR_{v in S} c(v)`

(coordinatewise Boolean OR).

So atomic-predicate compression is exactly the problem of finding a low-dimensional Boolean join-semilattice homomorphism

`Phi : P(U_k) -> {0,1}^d`

whose restriction to the candidate family `E` is injective.

This is the same algebra underlying separable / union-free group-testing codes: a test outcome vector is the Boolean sum (OR) of the columns corresponding to the unknown support.

Reference for separable/union-free code terminology: Goshkoder, Polyanskii, Vorobyev, *Efficient Combinatorial Group Testing: Bridging the Gap between Union-Free and Disjunctive Codes*, arXiv:2401.16540 (2024).

## 4. A general co-atom obstruction

Let `U` be a finite ground set with `n=|U|`. Suppose a candidate family `E` contains

`U`

and, for every `v in U`, also contains

`U \ {v}`.

### Theorem — exact adaptive and non-adaptive complexity

Any exact intersection-query identification scheme for `E`, even an adaptive one, has worst-case depth at least `n`. Testing every singleton gives an upper bound `n`. Therefore the exact adaptive and non-adaptive complexity is

`n`.

### Proof

Follow the transcript when the unknown set is `U`. Every nonempty query has positive outcome.

Fix `v in U`. To distinguish `U` from `U\{v}` somewhere along this transcript, a queried set `A` must satisfy

`A intersect U != empty`

but

`A intersect (U\{v}) = empty`.

Since `A subseteq U` without loss of generality, this forces

`A = {v}`.

Thus the all-positive transcript for `U` must contain the singleton query `{v}` for every `v in U`. These `n` queries are distinct, so the depth is at least `n`. The `n` singleton queries plainly identify every subset, proving equality.

### Noether-style interpretation

The obstruction is not entropy. It is **local indistinguishability at the top element**. Each co-atom `U\{v}` differs from `U` in exactly one cell, and OR/intersection tests can expose that missing cell only by isolating it. Every cell therefore needs a private coordinate.

## 5. Exact theorem for the ocLTL ABA fibers

Fix a coarse `(m,x)` support having `r` nonzero rows and take the interior successor-memory type `0<y<1`, so both `y` columns must be nonzero.

The candidate 3-types in that projection fiber are

`F_r = { S subseteq [r] x {0,1} : every row is nonempty and both columns are nonempty }`.

For `r>=2`:

`|F_r| = 3^r - 2`.

The full `2r`-cell set belongs to `F_r`, and deleting any single cell still leaves every row nonempty and both columns nonempty. Hence `F_r` contains the full set and all `2r` co-atoms.

By the co-atom theorem,

`GT(F_r) = 2r`

for both adaptive and non-adaptive atomic ABA tests.

The complete cases are therefore:

- `r=1`: `|F_1|=1`, zero tests needed inside the fiber;
- `r=2`: `|F_2|=7`, exactly 4 atomic tests;
- `r=3`: `|F_3|=25`, exactly 6 atomic tests;
- `r=4`: `|F_4|=79`, exactly 8 atomic tests.

For the hardest ocLTL ABA fiber (`r=4`) the information bound is only

`ceil(log2 79)=7`,

but atomic Boolean equations require

`8`.

Thus the earlier 7-bit threshold has to be read carefully:

- **7 arbitrary definable predicate bits** can distinguish the 79 candidates in principle;
- **8 atomic Boolean-equation/inequation tests** are necessary and sufficient.

The gap is caused by the OR-homomorphism constraint on atomic tests.

## 6. General asymptotic family

For the largest one-new-variable refinement of a coarse ABA type with `r` nonzero cells,

- candidate count: `3^r-2`;
- information lower bound: `ceil(log2(3^r-2)) ~ r log2 3`;
- atomic ABA test complexity: exactly `2r`.

Hence the asymptotic overhead of atomic tests relative to unrestricted information bits is

`2 / log2(3) ~= 1.26186`.

For a maximally supported coarse p-type, `r=2^p`, so the hardest refinement fiber needs exactly

`2^(p+1)`

atomic equations to recover every fine complete type.

## 7. Consequences for OrbitSynthesis

### A. Do not optimize only the number of predicate bits

Two encodings with the same number of logical bits can have radically different definitional complexity. Arbitrary definable bits may beat atomic equations in count while requiring large Boolean combinations.

The natural cost model becomes multi-objective:

- number of predicates;
- Boolean/formula size of each predicate;
- normalization / QE cost;
- decoding / witness-reconstruction cost.

### B. Atomic-predicate selection is a known hard combinatorial problem

For unrestricted candidate families, minimum test selection is generalized group testing / test cover and is computationally hard. The research opportunity is therefore to exploit the **special geometry of ABA type families generated by restrictions, recurrence, and specifications**, not to seek a polynomial optimum for arbitrary families.

### C. Sparse and well-separated candidate families may admit compression

The generalized group-testing literature gives substantially smaller schemes when the candidate family has bounded support size or large pairwise symmetric differences. These parameters should be measured on real Tau-generated type families.

### D. The semilattice view may be the right abstraction

Instead of treating each predicate as an opaque formula, study the join-code columns `c(v)` and the candidate-support hypergraph. This exposes exactly which distinctions an atomic Boolean predicate can and cannot express.

## 8. Next theorem targets

1. Classify the minimum atomic-test complexity of all ABA projection fibers obtained by adding more than one variable.
2. Add formula-size constraints: what is the best tradeoff between 7 arbitrary definable bits and 8 simple minterm tests in the 79-state fiber?
3. Measure group-testing parameters (`max support`, minimum symmetric difference, co-atom structure) on Tau-generated candidate families.
4. Determine which fixed-point/predecessor operations preserve candidate-family classes with efficient separating codes.
5. Study whether the join-semilattice representation supports symbolic predecessor computation directly, instead of using the tests only as an encoding layer.

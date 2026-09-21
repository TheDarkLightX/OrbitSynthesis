# Fixed-domain term safety as subpower row-list intersection

**Status:** DERIVED exact equivalence from the definition of a term operation and the standard subpower/SMP evaluation representation. The subpower membership problem, compact subpower representations, and their complexity theory are classical prior art. The reactive row-list intersection packaging and controller-hierarchy consequences remain under prior-art review. Tau-independent.

## 1. Representation shift

`TERM_SYNTHESIS_COMPLEXITY_BOUNDARIES.md` identified the Subpower Membership Problem (SMP) as the static interpolation problem hidden inside original-signature controller synthesis.

The sharper representation is not "run an SMP oracle after guessing a strategy".

For one fixed candidate invariant domain, **all term-expressible controller columns already form one generated subpower**. Reactive safety then asks whether a Cartesian product of those subpowers intersects the product of the allowed output lists.

This separates the two mechanisms exactly:

- algebraic expressibility = a generated subpower;
- reactive safety/invariance = row-wise output constraints.

## 2. Fixed candidate domain

Let A be a finite algebra.

Fix:

- state arity `k>=1`;
- input arity `m>=0`;
- a candidate invariant domain `W subseteq A^k`;
- safety relation `R subseteq A^k x A^m x A^k`.

Let

`Z = W x A^m`

be the set of observations at which a winning controller is constrained.

Write

`n=k+m`

for observation arity and

`N=|Z|`.

Choose an ordering

`Z={z_1,...,z_N}`.

For each observation z=(s,u), define its allowed next-state list

`L_z = { v in W : R(s,u,v) }`.

A fixed-domain positional controller is winning exactly when it chooses one value

`sigma(z) in L_z`

for every z in Z.

The extra requirement is that every coordinate function of sigma is an n-ary term operation of A.

## 3. The term-evaluation subpower

For each observation coordinate

`i=1,...,n`,

define the evaluation column

`c_i = ( z_1[i], ..., z_N[i] ) in A^N`.

Let

`P_Z = Sg_(A^N)({c_1,...,c_n})`.

The closure is taken under A's basic operations coordinatewise, including nullary operations when they belong to the signature.

### Lemma 1 -- evaluation vectors are exactly P_Z

`P_Z` is exactly the set

`{ (t(z_1),...,t(z_N)) : t is an n-ary term operation of A }`.

### Proof

The coordinate columns c_i are the evaluation vectors of the n projection terms.

Closing those columns under a basic r-ary operation f of A maps evaluation vectors of terms t_1,...,t_r to

`( f(t_1(z_j),...,t_r(z_j)) )_(j=1..N)`,

which is exactly the evaluation vector of the composite term f(t_1,...,t_r).

Thus every generated element of P_Z is the evaluation vector of a term.

Conversely every term is built from projections and basic operations, so structural induction puts its evaluation vector in P_Z. QED.

This is the ordinary subpower/SMP representation of term interpolation.

## 4. Transpose the controller table

A k-coordinate controller over Z can be viewed in two equivalent ways.

### Row view

For each observation z_j choose

`y_j = sigma(z_j) in A^k`.

### Column view

For each output coordinate `ell=1,...,k`, form

`b_ell = ( y_1[ell],...,y_N[ell] ) in A^N`.

Every controller coordinate is a term operation iff

`b_ell in P_Z`

for every ell.

The safety condition is exactly

`y_j in L_(z_j)`

for every row j.

## 5. Exact intersection theorem

Use the canonical transpose bijection

`tau:(A^N)^k -> (A^k)^N`.

### Theorem 2 -- subpower row-list synthesis

The candidate domain W is winning under one positional controller whose k coordinates are original-signature A-terms iff

`tau(P_Z^k) intersection Product_(z in Z) L_z` 

is nonempty.

Equivalently, there exist

`b_1,...,b_k in P_Z`

such that for every observation row z_j,

`(b_1[j],...,b_k[j]) in L_(z_j)`.

### Proof

If a term controller exists, Lemma 1 puts each coordinate evaluation vector b_ell in P_Z and safety/invariance puts every transposed row in its list.

Conversely, take a point of the intersection. Lemma 1 supplies an n-ary term t_ell whose evaluation vector on Z is b_ell for each output coordinate ell. The controller

`sigma=(t_1,...,t_k)`

therefore takes exactly the selected row value at every constrained observation, hence stays safe and in W. Its values outside Z are irrelevant to winning from W but are automatically supplied because the terms are total. QED.

## 6. SMP is a special case

Ordinary partial term interpolation prescribes one output value for each selected observation.

For `k=1`, singleton lists

`L_z={f(z)}`

reduce Theorem 2 to asking whether the prescribed evaluation vector belongs to P_Z.

That is precisely SMP / partial term interpolation.

So reactive term safety is not merely analogous to SMP:

> it is a row-list intersection problem over the same generated subpower that SMP queries by membership.

## 7. Why this formulation is better than full truth-table synthesis

The complete controller truth table has `k |A|^(k+m)` entries.

The fixed-domain formulation only needs the observation set

`Z=W x A^m`.

More importantly, algebraic structure can represent P_Z without enumerating all of it.

Known SMP/compact-representation algorithms therefore become candidate backends for OrbitSynthesis rather than mere complexity references.

The question changes from

> guess a complete term table and verify it

into

> represent the generated subpower P_Z compactly, then decide whether k elements of it satisfy row-wise list constraints.

## 8. Existing controller hierarchy reappears as geometry of P_Z

### Primal

Every function is a term operation.

`P_Z=A^N`.

The intersection factors completely by rows, yielding the ordinary finite safety condition `L_z != empty`.

### Semi-primal

Any subalgebra-preserving total function is a term.

For each observation z, the value may be selected independently from `Sg_A(z)`.

Thus

`P_Z = Product_(z in Z) Sg_A(z)`

under the row coordinate ordering.

The row-list intersection again decouples observation by observation, giving `TPre`.

### Demi-semi-primal

Values couple only along global automorphism orbits.

One orbit representative value must lie in its generated subalgebra and be fixed by the observation stabilizer; the rest of the orbit is determined equivariantly.

Hence P_Z factorizes over global-automorphism observation orbits. This is the `DPre` algorithm.

### Quasi-primal

Values couple along the full internal-isomorphism groupoid.

P_Z factorizes over groupoid connected components, subject to cycle consistency. The existing `quasi_primal_strategy_for_domain` implementation in `src/orbitsynthesis/safety.py` is exactly a specialized symbolic representation of this P_Z geometry.

### General finite algebra

P_Z is an arbitrary generated subpower.

SMP/compact-subpower algorithms become the natural algebra-specific representation layer.

## 9. Compact-representation opportunity

Bulatov--Mayr--Szendrei show, for finite algebras with cube terms, that SMP and construction of compact representations of generated subpowers are polynomial-time interreducible; under residual-smallness hypotheses SMP is polynomial-time.

Kompatscher gives further polynomial-time SMP algorithms for a broad class of 2-nilpotent Mal'cev algebras.

These results do **not** automatically solve Theorem 2's row-list intersection problem.

They do, however, supply a compact representation of the exact algebraic carrier on which the remaining reactive constraints live.

This suggests a new solver architecture:

1. construct/maintain compact representation of P_Z;
2. impose row lists L_z;
3. propagate list restrictions through the representation;
4. if inconsistent, extract a compact obstruction when the backend supports one;
5. if W is variable, use the obstruction to prune domain search.

The difficult step is 2--4, not SMP membership alone.

## 10. Incremental SMP-oracle fallback

Even without a direct list-intersection algorithm, an SMP decision oracle is useful.

Search over selected row outputs. For a partial selection T subseteq Z and each coordinate ell, maintain the partial target vector

`f_ell:T->A`.

Before extending the search, ask whether f_ell is term-interpolable for every ell.

If any coordinate fails, the branch can be pruned immediately.

If the SMP backend can return a smaller non-interpolable restriction, store it as a nogood.

This yields a verifier-gated CEGIS/backtracking architecture:

`row choice -> interpolation check -> obstruction/nogood -> refine`.

The subpower intersection theorem explains what this incremental process is approximating globally.

## 11. Reactive complexity is still separate

Easy SMP does not imply easy reactive synthesis.

Even when membership in P_Z is polynomial:

- selecting k compatible columns under row lists may be difficult;
- variable-domain synthesis adds state-selection variables;
- one shared controller may not exist for the union of separately controllable domains;
- `QUASIPRIMAL_NO_GREATEST_REGION.md` proves that a greatest domain can fail to exist.

So keep at least three complexity axes separate:

1. constructing/representing P_Z;
2. intersecting P_Z^k with row lists;
3. searching/optimizing the invariant domain W.

## 12. Exact finite calibration

`experiments/subpower_row_list_calibration.py` uses the two-element meet-semilattice

`A=({0,1}; meet)`.

For `k=1,m=1` it exhausts every candidate domain and every possible row list:

- 265 instances total;
- subpower-intersection feasibility agrees with brute enumeration of all term controllers in every case.

The script also runs a deterministic randomized `k=2,m=1` differential test with 1,000 instances.

The computation validates the implementation of the representation; Theorem 2 is the proof.

## 13. Prior-art boundary

Classical/source-bound:

- generated-subpower representation of term interpolation;
- SMP and its complexity;
- compact representations of subpowers;
- few-subpowers/cube-term/Mal'cev algorithms.

Derived here:

- the exact transpose formula `tau(P_Z^k) intersect Product L_z` for fixed-domain reactive term safety;
- using the known controller hierarchy as special factorizations of P_Z;
- the proposed compact-subpower/list-intersection backend for OrbitSynthesis.

Current searches have not found a paper presenting this exact clone/term-constrained reactive-safety formulation. That remains a bounded search result, not a novelty conclusion.

## 14. Next questions

1. Give the row-list intersection problem a literature-safe name only after checking CSP/SMP terminology; for now use **subpower row-list intersection** as repository terminology.
2. Determine complexity for fixed quasi-primal, semi-primal, and Mal'cev algebras.
3. Determine whether compact cube-term representations support polynomial-time row-list intersection for fixed output arity k.
4. Relate row-list intersection to CSP over a generated subpower supplied succinctly by generators/compact representation.
5. Extract minimal non-interpolability cores from known SMP algorithms and measure pruning power in domain search.
6. Add a reference implementation that computes P_Z explicitly only for tiny finite algebras and differentially checks specialized solvers.

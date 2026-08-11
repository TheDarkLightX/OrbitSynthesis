# Direct safety synthesis for ABA clauses via support hypergraphs

**Status:** DERIVED one-step closure theorem and canonical representation; randomized bounded explicit-game differential checks completed; fixed-point/strategy implementation pending; Lean pending; novelty not established.

This extends `EQUATIONAL_SAFETY_CUBE_GAME.md` from pure equations to the normalized atomless-Boolean-algebra clause class

`f=0 AND AND_i g_i!=0`.

Unlike the equation-only theorem, **atomlessness matters here** because several inequations may require distinct nonzero refinements of the same coarse region.

## 1. Clause regions are allowed sets plus hitting hypergraphs

Fix `k` BA state variables and let

`U = {0,1}^k`

be their Venn-cell labels.

A normalized quantifier-free ABA clause

`f(s)=0 AND AND_{i=1}^m g_i(s)!=0`

corresponds to:

- an allowed cell set `A subseteq U`, namely the complement of the minterm support of `f`;
- hit sets `H_i subseteq U`, namely the minterm supports of the `g_i`.

The clause holds on a complete support `S` exactly when

`empty != S subseteq A`

and

`S intersect H_i != empty` for every i.

Write this region as

`R(A; H_1,...,H_m)`.

After replacing each `H_i` by `H_i intersect A`, an empty hit set makes the region empty.

## 2. Canonical antichain representation

If

`H_i subseteq H_j`,

then hitting `H_i` implies hitting `H_j`, so `H_j` is redundant.

Therefore retain only the inclusion-minimal nonempty hit sets. They form an antichain in `P(A)`.

### Proposition — canonical form

For every nonempty region of the form `R(A;H)`, the pair

`(A, Min(H))`

where `Min(H)` is the inclusion-minimal hit-set antichain, is semantically canonical:

- `A` is the union of all supports in the region;
- `Min(H)` is the unique prime monotone-CNF clause family over the support bits.

Thus equality of canonical clause regions reduces to equality of one allowed-set mask and one antichain of hit-set masks.

## 3. Transition clause

Let:

- state labels `a in S={0,1}^k`;
- input labels `u in I={0,1}^p`;
- output/next-state labels `v in Y={0,1}^k`.

A normalized ABA transition/safety clause on `(s,x,y)` is represented by:

- allowed full cells `L subseteq S x I x Y`;
- transition hit sets `G_1,...,G_q subseteq S x I x Y`.

A full support `Q` satisfies the transition clause iff

`Q subseteq L`

and

`Q intersect G_j != empty` for every j.

Let the target winning approximation be

`R(A; H_1,...,H_m)`

on the y/next-state support.

## 4. Lift the target to full cells

The target equation `Supp(y) subseteq A` restricts full cells to

`L_A := S x I x A`.

So the full allowed set becomes

`L* := L intersect L_A`.

Each target hit set `H_t subseteq Y` lifts to

`G^target_t := S x I x H_t`.

Collect all full hit sets

`K = {G_1,...,G_q} union {G^target_1,...,G^target_m}`.

The inner controller problem for a fixed `(s,x)` support is now exactly one ABA clause with allowed full cells `L*` and hit family `K`.

## 5. Existential controller projection

Project away the output label `v`.

Define an allowed `(state,input)` cell set

`E := { (a,u) : exists v . (a,u,v) in L* }`.

For every full hit set `K_j`, define

`E_j := { (a,u) : exists v . (a,u,v) in L* intersect K_j }`.

### Lemma — existential projection

For an actual `(s,x)` support `P`, there exists a controller output y satisfying the transition clause and target region iff

`P subseteq E`

and

`P intersect E_j != empty` for every j.

### Proof

This is `ABA_BLOCK_QE.md` in support form.

Necessity is immediate.

For sufficiency, within every active coarse `(a,u)` region choose **all allowed output labels** `v` with `(a,u,v) in L*`. Atomlessness realizes every such nonempty local refinement. If P hits `E_j`, then at some active `(a,u)` there is an allowed output label also lying in `K_j`, and the maximal allowed refinement includes it. Hence every hit requirement is satisfied simultaneously.

## 6. Universal environment projection

We need the existential controller clause above to hold for **every** actual input extension of a state support.

Define the new allowed state-cell set

`A' := { a : for every u, (a,u) in E }`.

For every projected hit set `E_j`, define

`H'_j := { a : for every u, (a,u) in E_j }`.

### Theorem 1 — controllable predecessor closure

For countable ABA (indeed any sufficiently atomless BA supporting the finite refinements used above),

`CPre( R(A;H) ) = R( A'; H'_1,...,H'_(q+m) ).`

### Proof

A state support `S0` passes the universal equation/allowed condition iff every possible input refinement P of S0 is contained in E. This happens exactly when every active state label `a in S0` has **all** input labels `(a,u)` in E, i.e. `S0 subseteq A'`.

For a fixed hit set `E_j`, every input refinement P of S0 must intersect `E_j`. This holds iff at least one active state label `a in S0` has its entire input fiber inside `E_j`; otherwise the environment chooses, independently in every active state cell, one input label outside `E_j` and constructs a support avoiding it. Thus the condition is

`S0 intersect H'_j != empty`.

Applying this independently to every hit constraint yields the displayed clause region.

## 7. Direct hypergraph CPre algorithm

One predecessor step on canonical `(A,H)` is:

1. **target restrict:** `L* = L intersect preimage_y(A)`;
2. **target hits:** append `preimage_y(H_t)` to the transition hit family;
3. **exists-y allowed projection:** `E = exists_y L*`;
4. **exists-y hit projection:** `E_j = exists_y (L* intersect K_j)`;
5. **forall-x allowed projection:** `A' = forall_x E`;
6. **forall-x hit projection:** `H'_j = forall_x E_j`;
7. restrict each `H'_j` to `A'`;
8. if any hit set is empty, return the empty region;
9. delete duplicates and inclusion-nonminimal hit sets.

All operations are finite set projection, intersection, and antichain minimization on Boolean-cell masks.

No complete ABA type is enumerated.

## 8. Equation-only fragment is the zero-hyperedge case

If the transition has no inequations and the target has no hit constraints, the hypergraph family is empty.

Then the operator reduces to

`A -> {a : forall u exists v in A . (a,u,v) in L}`,

which is exactly the Boolean-cube game operator in `EQUATIONAL_SAFETY_CUBE_GAME.md`.

So the cube-game theorem is the `H=empty` special case of this more general representation.

## 9. Why one inequation breaks the principal-ideal theorem

The smallest counterexample is static.

Take one BA state variable s and the safety condition

`s != 0`.

Its support region is

`{ {1}, {0,1} }`

inside the three nonempty one-variable ABA types.

This is not a principal ideal `Supp(s) subseteq A`: the support `{0,1}` is accepted even though its sub-support `{0}` is rejected.

Thus equation-only cube collapse cannot extend unchanged even to one inequation.

The hypergraph representation captures it with

`A={0,1}`

and one hit set

`H={1}`.

## 10. Strategy reconstruction changes qualitatively

For equation-only games, one finite output label per `(a,u)` cell suffices and glues into ordinary Boolean terms of `(s,x)`.

With multiple inequations, the same nonzero `(a,u)` region may need **several output labels simultaneously** to witness different hit constraints. The maximal-witness proof can split that region into several nonzero pieces and assign different y-labels.

That split is available in an atomless BA but need not be term-definable from the current `(s,x)` tuple alone.

Therefore synthesis has two layers:

1. finite hypergraph policy chooses the allowed output-label subset/refinement pattern;
2. an effective ABA extension-witness procedure realizes the requested finite split in the concrete algebra.

This is exactly where Asor's effective-presentation / witness-computation assumption becomes operationally important.

## 11. Worst-case canonical hypergraph size

Let

`n=|U|=2^k`

be the number of state Venn-cell labels.

The canonical hit family is an antichain in `P(U)`. By Sperner's theorem, its size is at most

`binom(n, floor(n/2))`.

This upper bound is attainable as a static ABA clause: for every set H in a maximum Sperner antichain, choose a Boolean term whose minterm support is H and require it to be nonzero.

Hence the clause representation can still be doubly exponential in k in the worst case:

`binom(2^k, 2^(k-1))`.

So direct hypergraph synthesis is a structural/parameterized algorithm, not a universal polynomial compression theorem.

## 12. A natural practical parameter

The relevant dynamic parameter is not raw complete-type count but

`h = |Min(H)|`,

the number of inclusion-minimal active hit constraints in the current winning approximation.

A direct engine should measure:

- allowed-cell count `|A|`;
- canonical hit count h;
- hit-set density;
- inclusion pruning after every predecessor step;
- number of fixed-point iterations.

This is a falsifiable candidate predictor of practical complexity.

## 13. Comparison with generic symbolic-game work

General first-order safety games and recent symbolic infinite-state synthesis retain formulas and use solver/QE machinery. The ABA clause theorem identifies a much smaller domain-specific carrier for one fragment: a finite cell set plus a hit-set antichain.

This follows the same broad principle emphasized in recent infinite-state synthesis work—preserve the semantic structure of first-order constraints rather than flattening them to Boolean state IDs—but the concrete hypergraph transform here is specific to atomless Boolean support geometry.

## 14. Validation completed

A private randomized differential checker used the bounded instance:

- one state BA variable;
- one environment BA input;
- one output/next-state BA variable;
- arbitrary transition allowed mask on the 8 full cells;
- zero, one, or two random transition hit sets;
- arbitrary target allowed set on the two state cells;
- zero, one, or two target hit sets.

For each instance it compared:

1. explicit `forall (s,x)-type / exists (s,x,y)-type` enumeration; and
2. the closed-form hypergraph predecessor transform above.

Two thousand randomized instances showed no divergence.

A reproducible checker should be committed next.

## 15. Next research directions

1. Prove and implement canonical antichain fixed-point iteration end-to-end.
2. Benchmark hit-family growth on generated Tau safety clauses.
3. Identify syntactic classes where hit antichains remain polynomially bounded.
4. Use BDD/ZDD only when the explicit antichain itself becomes large; ZDDs are especially plausible for sparse set families.
5. Formalize the boundary between term-definable equation strategies and atomless-splitting strategies required by inequations.
6. Extend the transform to interpreted constants by product with the `rho(C)` constant regions.
7. Compare the direct hypergraph backend against Tau's current atom-level Boole decomposition and against generic support-BDD projection.

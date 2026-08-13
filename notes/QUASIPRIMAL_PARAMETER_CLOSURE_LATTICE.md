# Parameter-closure lattice for quasi-primal controller languages

**Status:** exact abstraction theorem derived; fixed-algebra synthesis and patchability consequences derived; exhaustive three-element calibrations pass; publication novelty unverified; not Lean-checked.

## 1. Result

A raw set of named carrier parameters is not the semantic controller language. The exact state is its **definable-constant closure**.

For an algebra `A` and `C subseteq A`, let `Pol_C(A)` be the positive-arity polynomial operations obtained from the original operations, variables, and named constants from `C`. Define

`K(C) = {a in A : the constant unary function x |-> a belongs to Pol_C(A)}`.

Then, for all `C,D subseteq A`,

`Pol_C(A)=Pol_D(A)  iff  K(C)=K(D)`.

Thus `C |-> K(C)` is a full, minimum-sufficient abstraction of parameter sets for every positive-arity polynomial-operation query. It removes false splits between different raw parameter sets that define the same constants, while different closures are separated by a constant-function query.

This applies Morph's `minimum-sufficient-abstraction` contract:

- raw domain: parameter sets `C`;
- query family: polynomial membership, sparse interpolation, and fixed-domain controller feasibility;
- abstraction: `K(C)`;
- decoder: replace each named parameter by a constant polynomial over any generator of the same core;
- hard gates: zero false merges, zero false splits, and descent of retained operations.

## 2. Algebraic form and proof

Let `K_0=K(empty)` be the parameter-free definable constants. Then

`K(C)=Sg_A(K_0 union C)`,

allowing the generated subuniverse to be empty when `K_0=C=empty` and no constant is definable.

One inclusion follows by composing original terms with constant polynomials for elements already in `K_0 union C`. Conversely, if a `C`-polynomial term is constantly `a`, evaluate its variables at any element of `Sg_A(K_0 union C)`; closure forces `a` into that generated subuniverse. The empty case would otherwise create a parameter-free definable constant, contradicting `K_0=empty`.

If `K(C)=K(D)`, every parameter named by `C` has a constant polynomial over `D`. Substitution translates every `C`-polynomial operation into a `D`-polynomial operation, and conversely. If the closures differ, a constant unary operation belonging to only one clone separates them.

Consequently `K` is a closure operator. The parameter-language lattice is exactly

`L_K(A)={K(C):C subseteq A}`,

with meet given by intersection and join by `K(K union L)`. Strict core inclusion gives strict language inclusion.

## 3. Patchability factors through closure

For any algebra `A`, the pointed expansions by `C` and by `K(C)` have the same nonempty pointed subalgebras, pointed internal isomorphisms, global pointed automorphisms, and positive-arity polynomial language.

Every nonempty subalgebra containing `C` contains `K(C)`, because each element of `K(C)` is the value of a constant polynomial over `C`. Every internal isomorphism fixing `C` fixes `K(C)` by term preservation. The converses follow from `C subseteq K(C)`.

Hence, for the patchability invariant developed in `QUASIPRIMAL_PARAMETER_PATCHABILITY.md`,

`kappa_patch(Q)=min_(closed good K) rank(K)`,

where

`rank(K)=min{|C|:K(C)=K}`.

Raw parameter sets with the same closure should be tested once, with a minimum generating witness retained for the core.

### Closed obstruction form

Let `phi:S->T` be a nonextendable internal isomorphism between nontrivial subalgebras, and put

`F_phi=Fix(phi)={a in S intersection T:phi(a)=a}`.

`F_phi` is a closed core: it is closed under the basic operations because `phi` is a homomorphism, and it contains every parameter-free definable constant. Thus `K(F_phi)=F_phi`.

Let `MaxFix_patch(A)` be the inclusion-maximal distinct fixed cores of nonextendable internal isomorphisms. Then the pointed extension property holds for `A_C` iff

`K(C) not_subseteq F` for every `F in MaxFix_patch(A)`.

The obstruction survives naming `C` exactly when `C subseteq F_phi`; closedness makes this equivalent to `K(C) subseteq F_phi`. Only maximal fixed cores matter. Therefore

`kappa_patch(A)
 = min {rank(K): K closed and K not_subseteq F for every F in MaxFix_patch(A)}`.

This is the closure-lattice dual of `PATCHABILITY_OBSTRUCTION_HYPERGRAPH.md`: its minimal hyperedges are the complements `A\F` of the maximal fixed cores. The hypergraph formulation uses raw anchors; the closure formulation quotients language-equivalent anchors and attaches exact generator-rank costs.

## 4. Fixed-core factorization for finite quasi-primal algebras

Let `Q` be finite quasi-primal, let `K=K(C)`, and expand `Q` by constants naming `K`. This expansion remains quasi-primal and has positive-arity term clone `Pol_C(Q)`.

For `z=(z_1,...,z_n)`, define

`G_K(z)=Sg_Q(K union {z_1,...,z_n})`.

For `n>1`, identify `z` and `z'` when an isomorphism `G_K(z)->G_K(z')` fixes `K` pointwise and maps every coordinate of `z` to the corresponding coordinate of `z'`. Choose one representative `r_E` for each class `E` and put `G_E=G_K(r_E)`. The pointed-orbit theorem gives

`Pol_C^(n)(Q) ~= product_E G_E`.

One seed in each `G_E` reconstructs the entire operation table by unique pointed transport. At `K=K_0` this recovers the original term clone; at `K=Q`, every tuple is its own class and every finite table is representable.

Sparse scalar or vector list interpolation reduces to one pulled-back list intersection per active class. For fixed `Q`, preprocessing the finite core lattice and internal-isomorphism catalog yields:

- dense arity-`n` table scan: `O(n |Q|^n)` in the coordinate-expanded input;
- sparse explicit tuple/list input: linear time in total encoded tuple/list length;
- fixed-domain controller feasibility: the same explicit-observation bound.

These claims concern semantic orbit-seed output. Compiling that output to a minimum original-signature term or DAG remains open.

## 5. Exact parameter thresholds

For finite quasi-primal `Q`, the following are equivalent:

1. `Pol_C(Q)` contains every finitary operation on `Q`;
2. `K(C)=Q`;
3. the expansion by `C` is primal.

Thus the universal parameter threshold is the relative generator rank

`rho(Q)=min{|C|:Sg_Q(K_0 union C)=Q}`,

not generally `|Q|`.

For one table `f`, let

`F(f)={K in L_K(Q):f in Pol_K(Q)}`.

This is upward-closed, and its exact minimum parameter budget is

`mu(f)=min_(K in F(f)) rank(K)`.

A target need not have a unique least feasible core; the correct output can be an antichain of incomparable minimum cores.

## 6. Exhaustive calibrations

`experiments/quasiprimal_parameter_closure.py` exhausts all eight raw parameter sets and all `3^9=19683` binary tables on two three-element quasi-primal algebras.

For the Quackenbush algebra `({0,1,2};discriminator,u)` with `u(0)=1,u(1)=0,u(2)=1`, the eight raw sets collapse to three cores:

- `empty`: `972` binary operations;
- `{0,1}`: `3888`;
- `Q`: `19683`.

`{0}` and `{1}` have the same core and language. `{0}` and `{2}` both cost one raw parameter but induce different languages, so parameter count alone is unsound. The exact minimum-budget distribution is `972` tables at budget zero and `18711` at budget one.

For the pure three-element discriminator algebra, `K(C)=C`. Binary-operation counts at core sizes `0,1,2,3` are `2,24,3888,19683`; minimum-budget counts are `2,66,9932,9683`. Among all tables, `1488` have two minimum parameter sets and `44` have three.

A no-least-core witness is

`f(x,y)=2 if (x,y)=(2,2), else 0`.

Its minimum cores are `{0,1}` and `{0,2}`, while their intersection `{0}` is infeasible.

Normal and optimized Python runs are byte-identical. Morph reports zero bounded false merges and false splits. The Quackenbush patchability obstruction compiles to the single maximal fixed core `empty`; the pure discriminator algebra has none. Morph's committed finite-corpus validator reports `PASS_EXACT_ON_BOUNDED_CORPUS` with eight raw objects, `19683` queries, three abstract states, and three semantic classes.

## 7. Scope and next targets

The closure theorem is elementary and may be standard under older polynomial-clone terminology; no publication novelty is claimed without a dedicated literature review. The finite checks are falsification certificates, not the generic proof. Lean formalization is pending.

Next targets:

1. compile the patchability hypergraph to the maximal closed fixed-core antichain and optimize generator rank over it;
2. add `parameter_core` and `parameter_budget` semantics to the standalone kernel;
3. formalize closure, full abstraction, fixed-core factorization, and the generator-rank threshold in Lean;
4. compute joint frontiers of parameter cores and winning domains for the Quackenbush safety benchmark;
5. study explicit discriminator term/DAG size and extend the abstraction search beyond quasi-primal clones.

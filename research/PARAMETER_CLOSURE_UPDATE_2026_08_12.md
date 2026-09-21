# Frontier update -- parameter-closure lattice, 2026-08-12

This update follows `POINTED_ORBIT_UPDATE_2026_08_12.md` and sharpens `QUASIPRIMAL_PARAMETERIZED_CONTROLLER_COLLAPSE.md`.

## F3-A1 -- raw parameter sets quotient exactly by definable-constant closure

**Status:** DERIVED generic full-abstraction theorem; Morph certificate complete.

For any algebra `A`, let `K(C)` be the elements whose constant unary operations are polynomially definable from parameters `C`. Then

`Pol_C(A)=Pol_D(A) iff K(C)=K(D)`.

Moreover

`K(C)=Sg_A(K(empty) union C)`

with an empty bottom allowed.

So the exact parameter-language state is a closed carrier core, not the raw set and not its cardinality.

**Files:**

- `notes/QUASIPRIMAL_PARAMETER_CLOSURE_LATTICE.md`
- `research/MORPH_PARAMETER_CLOSURE_CERTIFICATE.md`

---

## F3-A2 -- fixed-core quasi-primal term synthesis factorizes exactly

**Status:** DERIVED from the pointed product theorem applied to the constant expansion.

For a closed core `K`, define

`G_K(z)=Sg_Q(K union coordinates(z))`.

Quotient tuples by isomorphisms between these generated subalgebras that fix `K` and carry one tuple to the other. For arity `n>1`,

`Pol_K^(n)(Q) ~= product_E G_K(r_E)`.

This gives one independently selected seed per `K`-pointed class.

---

## F3-A3 -- exact functional-completeness threshold

**Status:** DERIVED.

For finite quasi-primal `Q`, parameters `C` collapse polynomial controllers to unrestricted finite tables iff

`K(C)=Q`.

The minimum universal parameter budget is the generator rank

`rho(Q)=min{|C|:Sg_Q(K(empty) union C)=Q}`,

not necessarily `|Q|`.

In the Quackenbush algebra, naming the single element `2` generates all constants and therefore all finite tables.

---

## F3-A4 -- fixed-algebra minimum-parameter synthesis reduces to a constant-core scan

**Status:** DERIVED explicit-input algorithm.

For a table, list instance, or fixed-domain controller, enumerate the constant-size closed-core lattice of fixed `Q`, apply the fixed-core pointed criterion, and minimize precomputed generator rank.

For a dense arity-`n` table, the straightforward deterministic scan is `O(n |Q|^n)`; for sparse explicit tuples/lists it is linear in total encoded tuple/list length, with constants depending on `Q`.

A unique least core need not exist; the output can be an antichain.

---

## F3-A5 -- patchability factors through the same closure

**Status:** DERIVED bridge to `QUASIPRIMAL_PARAMETER_PATCHABILITY.md`.

Raw parameter sets `C` and `D` with `K(C)=K(D)` have the same pointed subalgebras, pointed internal isomorphisms, global pointed automorphisms, and polynomial controller language. Hence

`kappa_patch(Q)=min_(good closed K) rank(K)`.

Combining this with `PATCHABILITY_OBSTRUCTION_HYPERGRAPH.md`, every nonextendable partial isomorphism has a closed fixed core `F`, and a parameter core `K` kills that obstruction exactly when `K not_subseteq F`. Therefore only the inclusion-maximal fixed cores matter:

`kappa_patch(A)
 = min {rank(K) : K closed and K not_subseteq F for every maximal obstruction core F}`.

This is the closure-lattice dual of the minimal-edge obstruction hypergraph. It quotients language-equivalent raw hitting sets while retaining a minimum generating witness for each core.

---

## F3-N1 -- parameter count alone is unsound

**Status:** NEGATIVE exact witness.

In the Quackenbush algebra:

- naming `{0}` gives core `{0,1}` and `3888` binary polynomial functions;
- naming `{2}` gives core `Q` and all `19683` binary functions.

Both use one parameter.

---

## F3-N2 -- a target table need not have a least parameter core

**Status:** NEGATIVE exact witness.

In the pure three-element discriminator algebra,

`f(x,y)=2 if (x,y)=(2,2), else 0`

has two incomparable minimum cores `{0,1}` and `{0,2}`. Their intersection `{0}` is infeasible.

---

## F3-V1 -- bounded validation

`experiments/quasiprimal_parameter_closure.py` exhausts:

- all raw parameter sets;
- all relevant parameter-fixing internal isomorphisms;
- all `19683` binary tables per closed core;
- exact language equality iff closures agree;
- every minimum parameter budget and minimum-set multiplicity;
- exact raw-to-closure and maximal-closed-obstruction descent of the pointed patchability predicate.

Quackenbush operation counts by core are `972`, `3888`, `19683`.

Pure-discriminator operation counts by core size are `2`, `24`, `3888`, `19683`; minimum-budget counts are `2`, `66`, `9932`, `9683`.

Normal and optimized Python outputs are byte-identical. Morph false merges and false splits are zero on both calibrations. The Quackenbush patchability obstruction compiles to the single maximal closed core `empty`, while the pure discriminator algebra has none. Morph's committed validator independently reports `8` raw parameter sets, `19683` queries, `3` parameter-addition operations, `3` abstract states, `3` semantic classes, and `PASS_EXACT_ON_BOUNDED_CORPUS`.

---

## Ranked next actions

1. Implement `parameter_core`, `allowed_parameters`, and `parameter_budget` in the standalone kernel; compile patchability obstructions to maximal closed fixed cores and optimize generator rank over that antichain.
2. Compute joint antichains of winning domains and minimum parameter cores for the Quackenbush reactive benchmark.
3. Formalize closure full abstraction, fixed-core factorization, and generator-rank threshold in Lean.
4. Minimize discriminator DAG size under a parameter budget.
5. Extend the closure abstraction to non-quasi-primal algebras and isolate the first irreducible relational coupling.
6. Search old polynomial-clone/discriminator literature before making novelty claims.

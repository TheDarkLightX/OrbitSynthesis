# Tau integration plan for support-level ABA elimination

**Status:** engineering design grounded in Tau commit `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`; no Tau source modification has been made from this repository.

## 1. Current normalization path inspected

At the pinned Tau commit, `normalize` / `normalize_non_temp` route first-order work through `eliminate_bv_and_quantifiers`.

That routine:

1. scopes out independent conjuncts;
2. calls `resolve_quantifiers`;
3. invokes `anti_prenex_block` on remaining quantifier blocks;
4. calls `resolve_quantifiers` again;
5. may perform another anti-prenex pass and legacy fallback if quantifiers remain.

`process_quantifier_block` groups homogeneous same-kind BA quantifiers. Existential blocks go through `anti_prenex_block`; universal blocks are dualized via

`forall X. phi == not exists X. not phi`

and then sent through the same existential pipeline.

## 2. Existing Boole/BDD machinery

Tau already performs Boole/Shannon decomposition. The source comments explicitly describe atomic formulas as BDD variables.

The general block decomposition:

- chooses an atomic formula as pivot;
- replaces it by true/false in the two branches;
- simplifies each branch;
- recurses;
- has a shared per-block split budget `block_boole_max_splits = 512`;
- re-wraps a residual quantifier block when the budget is exhausted.

Tau also has important clause/all-positive/all-negative fast paths and `push_ex_block_into_clause` before falling back to general Boole decomposition.

Therefore OrbitSynthesis must **not** claim "Tau does not use BDDs" or "Tau always converts every formula to explicit DNF". The current implementation is substantially more sophisticated than the older high-level paper presentation.

## 3. Different abstraction level proposed here

Tau's Boole pivots are whole **atomic formulas**.

The support backend instead uses one Boolean coordinate for every semantically possible nonzero minterm region of the finitely generated ABA subalgebra:

`support coordinate = (constant region, retained-variable minterm)`.

For the pure theory this is exactly `2^k` bits for k BA variables and is minimum-width among all binary complete-type encodings.

The key difference is that BA quantification is no longer implemented by recursively splitting logical atoms. It becomes a fixed local relation between support coordinates:

`z_v <-> OR_{u in refinement(v)} w_u`.

This permits block projection before deciding which formula atom would make a good Shannon pivot.

## 4. Safest initial integration point

Do **not** replace `anti_prenex_block`.

Add a guarded atomless-BA fast path immediately before the general Boole-decomposition stage for a homogeneous quantifier block.

Suggested contract:

`try_support_block_elimination(block_vars, body) -> optional<formula_or_support_dag>`

The fast path declines unless all assumptions are explicit and checked.

### Phase 1 accepted matrix

Only accept a matrix that is a conjunction of homogeneous atomless-BA equality/disequality atoms after Tau's existing atomic normalization.

Use `ABA_ALTERNATING_CLAUSE_QE.md`:

- existential block: direct `exists` support transform;
- universal block: direct `forall` support transform, avoiding dualization.

The result remains one zero-support mask plus q nonzero-support masks.

This phase does not require an ROBDD at all.

### Phase 2 accepted matrix

General Boolean formula over atomless-BA atoms.

Compile the formula to a support Boolean DAG and use the extension relation + Boolean abstraction from `ABA_SUPPORT_BOOLEANIZATION.md`.

Only attempt this when a cost predictor says the support representation is below a configured budget.

## 5. Phase-1 compiler

Input:

- homogeneous atomless BA type;
- retained free variables;
- quantified block variables;
- normalized equations/disequations;
- finite set of interpreted constants occurring in the block.

Steps:

1. compute the nonzero constant-region partition and `rho(C)`;
2. assign support coordinates to `(constant-region, full variable minterm)`;
3. evaluate every BA term on these finite coordinates, yielding bit masks;
4. combine all equality masks into forbidden mask Z;
5. retain each disequality mask G_j;
6. project the quantified variable block with the direct existential/universal transform;
7. simplify empty/full/duplicate masks;
8. either:
   - retain masks in an internal support object for subsequent blocks; or
   - materialize one BA equality and the remaining BA disequalities only at the boundary back to existing Tau syntax.

## 6. Why retaining masks across blocks matters

Materializing a projected support mask as a join of minterm terms after every quantifier block can erase the benefit.

For a prenex conjunctive matrix, the theorem says masks can remain internal through the entire alternating prefix. Support width decreases geometrically as variables are eliminated, and the number of disequality masks never grows.

So the preferred architecture is:

`Tau AST -> normalized clause -> support masks -> all BA quantifier blocks -> Tau AST`

not

`Tau AST -> support masks -> Tau AST -> support masks -> ...`.

## 7. Differential-safety mode

During research integration, every fast-path result should be checked against the existing Tau path on bounded/test workloads.

Modes:

- `support_off`: current Tau behavior only;
- `support_shadow`: run both, return current Tau result, assert/record theory equivalence;
- `support_on`: use support result, fall back to current path on unsupported/costly cases.

Divergence handling:

1. minimize the formula;
2. evaluate both outputs against exhaustive ABA support types when arity is small enough;
3. prove which output is correct before assigning blame.

## 8. Direct universal optimization

The first feature worth benchmarking independently is direct universal clause projection.

Current generic architecture:

`forall block. C`

becomes

`not exists block. not C`.

For conjunctive ABA C, support geometry gives a direct transform that remains conjunctive and preserves the number of disequality obligations.

Benchmark adversarial conjunctions where negation creates many disjuncts or prevents the existing clause fast path from firing early.

Kill the optimization if Tau's simplifier consistently makes the dual route equally small.

## 9. Cost predictors

Candidate semantic parameters:

- `N = rho(C) * 2^k`: support width;
- q: surviving disequality obligations;
- projected ROBDD bound `N*2^q` for the clause class;
- number of quantified variables in the current block;
- variable-incidence width of atom masks;
- current Tau atom count / estimated Shannon split count.

For Phase 1 the support transform cost is predictable and should usually be accepted whenever N is below a memory threshold.

For general Phase 2 BDD abstraction, use runtime node budgets and fall back safely.

## 10. Initial benchmark matrix

Compare current Tau versus support fast path on:

1. existential all-equation clauses;
2. existential mixed equation/disequation clauses;
3. universal clauses;
4. alternating prefixes over one conjunction;
5. nested/disjoint/generic interpreted constants at equal raw constant count but different `rho(C)`;
6. formulas close to the 512 Boole-split budget;
7. ocLTL §5.2 feasibility instances;
8. direct safety predecessor/fixed-point instances.

Record:

- semantic agreement;
- wall time;
- allocations / peak memory;
- AST/DAG node counts;
- Boole splits consumed;
- support width and `rho(C)`;
- number of surviving disequations.

## 11. Promotion criterion

A Tau-facing implementation should be proposed only after:

- bounded exhaustive semantic agreement;
- randomized differential agreement;
- at least one workload family with a structural explanation for the speed/memory advantage;
- no regression on unsupported formulas because fallback remains exact;
- IP/license review for any code contributed outside this private research repository.

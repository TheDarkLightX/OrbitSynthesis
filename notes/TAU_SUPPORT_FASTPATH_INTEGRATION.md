# Tau integration: what the support fast path would actually change

**Status:** SOURCE-INSPECTED design note pinned to Tau commit `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`. No Tau code has been modified or benchmarked yet.

This note corrects an important possible overclaim: the direct block rule in `ABA_BLOCK_QE.md` is **not a new logical quantifier-elimination law relative to Tau's current clause pipeline**.

## 1. What Tau already does

At the inspected commit, `anti_prenex_block` groups same-kind/same-Boolean-algebra-type quantifiers into maximal blocks and sends homogeneous atomless clauses to

`push_ex_block_into_clause`.

That function:

1. normalizes all positive equations to `f_i=0` and collects their left sides;
2. squeezes them into one positive equation by forming
   `f = f_1 OR ... OR f_m`;
3. collects each negative equation / inequation term `g_j`;
4. rewrites each negative term to
   `NOT f AND g_j`;
5. wraps the **whole existential block** back around the positive equation and every rewritten inequation;
6. returns their conjunction to the downstream quantifier resolver / lazy-BDD machinery.

So the structural identity

`(AND positive equations) + independent inequations`

and the idea of block-level handling are already explicit in Tau.

## 2. Exact overlap with ABA_BLOCK_QE.md

For a block `Y=(y_1,...,y_r)`, our support theorem says

`exists Y [f=0 AND AND_j g_j!=0]`

is equivalent to

`AND_b f_b = 0`

and

`AND_j OR_b (NOT f_b AND g_(j,b)) != 0`,

where `b` ranges over `{0,1}^r`.

Tau currently constructs the logically equivalent intermediate formulas

`exists Y . f=0`

and

`exists Y . (NOT f AND g_j)!=0`

for all j, then asks its generic quantifier machinery to eliminate the same block.

Therefore the candidate improvement is **representation and evaluation order**, not logic.

## 3. Proposed support-mask fast path

For a homogeneous atomless clause whose active block has r variables:

1. normalize exactly as Tau already does;
2. compile `f` and all `g_j` to truth-table/minterm masks over the retained variables plus the r bound variables;
3. group the fine mask by retained-cell label;
4. simultaneously compute all `2^r` cofactors:
   - positive result mask from cells on which all f-cofactors are 1;
   - j-th inequation witness mask from cells having at least one bound label b with `f_b=0` and `g_(j,b)=1`;
5. rebuild the quantifier-free equation-plus-inequations clause directly;
6. run the ordinary syntactic simplifier;
7. during development, optionally compute the existing Tau result too and require semantic agreement before enabling the fast result.

No Boole/Shannon split on whole formula atoms is needed inside this path.

## 4. Why it might help

Tau's current route retains quantified syntax after `push_ex_block_into_clause` and delegates elimination to the general resolver. That machinery is sophisticated and has important fast paths, but it can still:

- build intermediate quantified formulas;
- perform atom-level Boole decompositions;
- invoke repeated normalization/simplification passes;
- consume the block split budget on shapes outside the clause fast paths.

The support-mask route knows the complete finite semantics of an atomless BA block immediately. Its work is a direct scan / bit-parallel projection of the local truth table.

Potential advantages are therefore:

- fewer intermediate syntax nodes;
- no repeated elimination of the same block for every negative term;
- predictable cost once masks are materialized;
- reusable support representation for ocLTL feasibility and direct safety synthesis.

These are hypotheses until benchmarked.

## 5. Why it might lose

The mask representation has width exponential in total local arity. A compact Tau term may be much smaller than its full truth table.

The current symbolic/lazy-BDD path may dominate when:

- r or retained arity is large;
- terms have compact shared structure;
- cofactors simplify without expanding all minterms;
- only a small part of the truth table is relevant.

Therefore this should be a **portfolio fast path**, not a blanket replacement.

## 6. Suggested dispatch rule to test

Collect cheap features before choosing the backend:

- number r of active quantified BA variables;
- number k of retained BA variables appearing in the dependent clause;
- number of positive / negative atoms;
- estimated minterm support width `2^(k+r)`;
- current term DAG size;
- repeated-subterm sharing;
- interpreted-constant partition rank when available.

Initial experimental rule only:

> try support projection when the estimated mask footprint fits a configured small bound; otherwise retain current Tau behavior.

Do not hard-code a theoretical threshold until benchmarks justify one.

## 7. Differential-validation plan

For generated homogeneous atomless clauses:

1. run current Tau QE at the pinned commit;
2. run support-mask block projection;
3. normalize both;
4. compare by Tau satisfiability/equivalence if available;
5. for very small arity, exhaust every complete support as a third oracle;
6. minimize every divergence before assigning blame.

Include adversarial cases:

- no positive equations;
- no inequations;
- contradictory positive equation;
- inequation completely forbidden by f;
- many inequations sharing witnesses;
- each inequation requiring a different local refinement;
- nested quantifier blocks;
- interpreted constants;
- mixed BA types (support fast path must decline).

## 8. Natural code insertion point

The least invasive experiment is immediately before / inside the homogeneous removable-clause branch of `push_ex_block_into_clause`:

- reuse Tau's existing block collection, type guards, and equation normalization;
- attempt `support_project_clause(...)`;
- if it returns a validated result, use it;
- otherwise execute the current implementation unchanged.

This keeps all existing fallback and mixed-type behavior intact.

A second, more ambitious integration would preserve support objects across several downstream transformations instead of immediately reconstructing Tau syntax. Do that only after the local fast path proves useful.

## 9. Novelty discipline

Do not claim:

- block quantifier elimination is new;
- independence of inequations is new;
- Tau lacked BDD/Boole decomposition;
- squeezing positive equations is new.

Potential engineering contribution:

> a structure-preserving support-mask execution path for atomless-BA quantifier blocks that computes the already-known block semantics simultaneously and reuses the same support carrier in synthesis.

Potential mathematical contribution remains in the direct safety/Boolean-power theorems, not in rediscovering Tau's clause identity.

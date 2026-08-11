# Direct universal elimination for Boolean-algebra clauses

**Status:** DERIVED elementary theorem valid in every Boolean algebra; closely related endpoint/Boole identities are classical and appear in Asor's TABA, so mathematical novelty is not claimed. Candidate Tau implementation optimization because the inspected universal-block path currently dualizes to existential elimination.

## 1. Endpoint normal form

Let `x=(x_1,...,x_r)` be Boolean-algebra variables and let f(x,Y) be a Boolean term, with Y denoting all other variables/parameters.

For each Boolean endpoint vector

`a in {0,1}^r`,

write `f(a,Y)` for substitution of every x_i by 0 or 1.

Boole/minterm decomposition gives

`f(x,Y) = join_{a in {0,1}^r} X^a f(a,Y)`,

where the minterms `X^a` form a disjoint partition of 1.

## 2. Universal zero theorem

### Theorem 1

In every Boolean algebra,

`forall x. f(x,Y)=0`

iff

`join_a f(a,Y)=0`.

Equivalently, every endpoint coefficient is zero.

### Proof

If the universal formula holds, evaluate it at each endpoint assignment a; hence every `f(a,Y)=0`, so their join is zero.

Conversely, if every endpoint is zero, Boole decomposition makes every term `X^a f(a,Y)` zero for every x, hence f(x,Y)=0.

For r=1 this is

`forall x. f(x)=0 iff f(0) join f(1)=0`.

Asor's TABA Exercise 11.3 gives another equivalent unary identity for universal zero.

## 3. Universal nonzero theorem

### Theorem 2

In every Boolean algebra,

`forall x. g(x,Y)!=0`

iff

`meet_a g(a,Y) != 0`.

### Forward direction by contrapositive

Assume

`meet_a g(a,Y)=0`.

Then the complements

`h_a := complement(g(a,Y))`

cover 1:

`join_a h_a = 1`.

Refine this finite cover to a disjoint partition `(p_a)_a` with

`p_a <= h_a`

and

`join_a p_a=1`.

For example, enumerate the endpoint vectors and take successive differences:

`p_1=h_1`,
`p_2=h_2 complement(h_1)`, etc.

Any finite partition indexed by `{0,1}^r` is the minterm partition of some tuple x: define

`x_i := join_{a:a_i=1} p_a`.

Then `X^a=p_a`, and Boole decomposition gives

`g(x,Y)=join_a p_a g(a,Y)=0`

because `p_a <= complement(g(a,Y))` for every a.

Thus if the endpoint meet is zero, the universal nonzero formula fails.

### Reverse direction

If

`c := meet_a g(a,Y) !=0`,

then for every x,

`g(x,Y)
 = join_a X^a g(a,Y)
 >= join_a X^a c
 = c`,

so g(x,Y) is nonzero.

For r=1:

`forall x. g(x)!=0 iff g(0) meet g(1) !=0`.

## 4. Direct universal clause rule

Let

`C(x,Y) := f(x,Y)=0 AND AND_{i=1}^q g_i(x,Y)!=0`.

Universal quantification distributes over conjunction, so Theorems 1 and 2 give immediately:

### Theorem 3

In every Boolean algebra,

`forall x. C(x,Y)`

iff

`[ join_a f(a,Y) = 0 ]
 AND
 AND_i [ meet_a g_i(a,Y) != 0 ].`

The result is again **one equation plus q disequations**.

No atomlessness, Hall condition, matching, BDD split, or support-type enumeration is required.

## 5. Complexity

A block of r variables has `2^r` endpoint assignments.

A direct implementation can cofactor every atom on the block and combine:

- equation endpoint cofactors by BA join;
- each disequation's endpoint cofactors by BA meet.

The number q of disequations is unchanged.

For r=1, each source atom requires only its 0- and 1-cofactors.

For a large block, repeated one-variable universal elimination yields the same result while exposing simplification after each step and avoids materializing all `2^r` endpoint cofactors at once.

## 6. Relation to support projection

`ABA_ALTERNATING_CLAUSE_QE.md` derived, for universal projection, the support transform

`Z_forall = {coarse fibers intersecting the forbidden support}`

and

`G_j_forall = {coarse fibers fully contained in G_j}`.

The endpoint theorem is the term-level form of exactly the same operation:

- joining endpoint values of f marks every coarse minterm for which **some** fine refinement is forbidden;
- meeting endpoint values of g keeps precisely the coarse minterms for which **every** refinement lies in g's support.

Thus the direct term rule can be implemented without constructing explicit support coordinates, while the support representation remains useful when several quantifier blocks or temporal/fixed-point operations should share one symbolic state representation.

## 7. Tau integration hypothesis

At inspected Tau commit `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`, `process_quantifier_block` handles a universal block by:

1. negating the body to NNF;
2. invoking the existential block pipeline;
3. negating the result back.

For a homogeneous Boolean-algebra conjunctive clause, try Theorem 3 **before** this dualization.

Pseudo-contract:

`try_direct_universal_ba_clause(block, body)`

accepts only when:

- body is a conjunction of normalized homogeneous BA equalities/disequalities;
- all quantified variables belong to the same BA family already accepted by the block machinery;
- term cofactoring is supported exactly.

It returns the conjunctive endpoint formula and otherwise declines with no semantic change.

## 8. Falsification/benchmark plan

1. Generate universal clauses and compare direct rule against Tau's current universal dualization.
2. Exhaustively test the outputs on small atomless support type spaces.
3. Also test finite Boolean algebras because the theorem is not atomless-specific.
4. Measure AST nodes, normalization passes, Boole splits, runtime, and allocations.
5. Include alternating prefixes so a direct universal result feeds an existential clause fast path without changing formula shape.

Kill the optimization if Tau's existing simplification consistently reduces the dual route to the same form at negligible cost.

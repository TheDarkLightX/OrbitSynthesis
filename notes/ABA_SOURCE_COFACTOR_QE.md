# Source-level cofactor quantifier elimination for ABA clauses

**Status:** DERIVED closed-form recurrence; bounded support-semantic checks passed. The equation-only existential consistency condition is classical and appears explicitly in Asor's Guarded Successor work; no novelty is claimed for that special case. The mixed equation+disequation, alternating-clause compiler recurrence is the research object to compare against prior Boolean-equation literature and Tau's implementation.

The earlier clause-QE notes work on support masks. This note pushes the same mathematics back to **Tau Boolean term syntax**.

The point is that the protected clause fragment can be eliminated by repeated cofactors and Boolean term operations, without first enumerating complete types, Venn supports, DNF clauses, or a truth table.

## 1. Normalize one clause

Consider a conjunction over a countable atomless Boolean algebra:

`f_1 = 0 AND ... AND f_m = 0 AND g_1 != 0 AND ... AND g_q != 0`.

General equations/disequations `a=b` / `a!=b` are first normalized with XOR:

`a=b  <->  (a XOR b)=0`,

`a!=b <-> (a XOR b)!=0`.

Combine all zero equations into one Boolean term

`z := f_1 OR ... OR f_m`.

Since a finite join is zero iff every summand is zero, the whole clause is equivalent to

`C(z;g_1,...,g_q)
 := [z=0] AND AND_j [g_j != 0].`

Keep the disequations separate: their separate nonzero witnesses matter.

## 2. Cofactors

Let x be the next BA variable to eliminate and Y the residual variables.

For any Boolean term h(x,Y), write

`h_0(Y) := h(0,Y)`,

`h_1(Y) := h(1,Y)`.

These are ordinary Boole/Shannon cofactors obtained by syntactic substitution followed by term normalization/hash-consing.

## 3. Existential one-variable recurrence

### Theorem 1

In the countable atomless Boolean algebra,

`exists x. C(z;g_1,...,g_q)`

is equivalent to the same clause shape

`C(z_E; g_E1,...,g_Eq)`

where

`z_E = z_0 AND z_1`,

and for every disequation obligation

`g_Ej = (NOT z_0 AND g_j0) OR (NOT z_1 AND g_j1)`.

### Exact reading

- `z_E=0` says that on every active residual Venn cell, **at least one** x-side is not forbidden by the zero equation.
- `g_Ej!=0` says that somewhere in the residual support there is an x-side that is simultaneously allowed by z and witnesses `g_j!=0`.

### Proof by the support invariant

Fix one active residual minterm cell D(Y).

Adding x splits D into two possible fine cells:

`D x'` and `D x`.

If z_0=z_1=1 on that residual cell, both refinements are forbidden, so D itself cannot remain active. This is exactly the truth condition of

`z_0 AND z_1`.

For disequation g_j, the residual cell can supply a legal witness iff one of the two fine cells has

`z=0 AND g_j=1`.

That is exactly

`(NOT z_0 AND g_j0) OR (NOT z_1 AND g_j1)`.

Different active residual cells refine independently. If different disequations require different fine refinements of the same nonzero residual cell, atomlessness allows the residual BA element to be split into finitely many nonzero pieces so all required fine cells can be activated simultaneously.

Therefore the projected clause is exact.

## 4. Universal one-variable recurrence

### Theorem 2

For **every Boolean algebra** (atomlessness is not needed for this direction),

`forall x. C(z;g_1,...,g_q)`

is equivalent to

`C(z_A; g_A1,...,g_Aq)`

where

`z_A = z_0 OR z_1`,

`g_Aj = g_j0 AND g_j1`.

### Inner mechanism

For an active residual cell to satisfy `z=0` for every value of x, both endpoint refinements must make z zero. Thus the residual forbidden predicate is their OR.

For `g_j!=0` to survive **every** possible refinement of x, some active residual cell must witness g_j on both sides; otherwise an adversarial x-refinement can choose a non-witness side in every active residual cell. Thus the residual witness term is the meet of the cofactors.

This is the direct universal clause rule that avoids Tau's generic negation/existential/negation route when the protected shape is recognized.

## 5. Block formulas

For a same-kind block X of r BA variables, let

`a in {0,1}^r`

range over endpoint assignments and write `z_a`, `g_ja` for the corresponding cofactors.

### Existential block

`exists X. C(z;g_j)`

becomes

`z_E = AND_a z_a`,

`g_Ej = OR_a [(NOT z_a) AND g_ja]`.

### Universal block

`forall X. C(z;g_j)`

becomes

`z_A = OR_a z_a`,

`g_Aj = AND_a g_ja`.

The one-variable recurrences are the r=1 case and permit block elimination one variable at a time without materializing all `2^r` endpoint cofactors simultaneously.

## 6. Alternating prefixes remain closed

Take a prenex prefix

`Q_1 x_1 ... Q_r x_r . C(z;g_1,...,g_q)`

with arbitrary alternation `Q_i in {exists,forall}`.

Eliminate from the innermost variable outward using Theorem 1 or Theorem 2.

At every step the result is again:

- one zero-equation term;
- exactly q disequation terms.

Hence:

### Theorem 3 — source-clause closure

Alternating first-order quantifier elimination of a conjunctive ABA equation/disequation clause can be performed entirely by term cofactors and Boolean term operations, without logical DNF/CNF expansion, while never increasing the number of disequation obligations.

Term DAG size can still grow; this is a structural closure theorem, not a polynomial-size theorem.

## 7. Relation to Asor's equation-only theorem

When q=0, Theorem 1 reduces to

`exists x. z(x,Y)=0`

iff

`z(0,Y) z(1,Y)=0`.

For a block X this is

`exists X. z(X,Y)=0`

iff

`AND_{a in {0,1}^r} z(a,Y)=0`.

This is the classical Boolean-equation consistency condition and is explicitly used as a key quantifier-elimination step in Asor's Guarded Successor paper.

OrbitSynthesis must therefore attribute the equation-only recurrence rather than present it as new.

The added target is the **mixed-clause recurrence**, its alternating closure, and the resulting synthesis/source compiler.

## 8. Exact Tau demo derivations

Tau's pinned normalization demo contains several formulas in this fragment.

### Example A

`qelim all X (X = 0)`.

Here z=X, so

`z_A = z_0 OR z_1 = 0 OR 1 = 1`.

The result is

`1=0`, i.e. False.

### Example B

`qelim ex X (X != 0)`.

Here z=0 and g=X.

`g_E = (1 AND 0) OR (1 AND 1) = 1`.

The result is

`1!=0`, i.e. True.

### Example C

`all X ex Y (X Y' = 0)`.

Eliminate Y existentially. With z=`X Y'`:

`z_0=X`, `z_1=0`, so

`z_E=X AND 0=0`.

The matrix becomes True before the outer universal is processed. Hence the sentence is valid.

### Example D

`all x ex y (x y = 0 AND x' y != 0)`.

Normalize:

`z=xy`, `g=x'y`.

Eliminate y existentially:

- `z_0=0`, `z_1=x`, hence `z_E=0`;
- `g_0=0`, `g_1=x'`, hence
  `g_E=(1&0) OR (x'&x') = x'`.

So the sentence reduces to

`all x. x' != 0`,

which is false at x=1.

This reproduces the intended invalidity without type enumeration or DNF.

## 9. Compiler form

A protected Tau quantifier block can use a small algebraic state:

`ClauseState = (zero_term z, list positive_terms [g_1,...,g_q])`.

For each quantified variable x:

### Existential step

1. compute/hash-cons `z0,z1`;
2. set `z := z0 & z1`;
3. for each g_j compute `g0,g1` and set
   `g_j := z0' g0 | z1' g1`;
4. normalize/simplify terms.

### Universal step

1. compute `z0,z1`;
2. set `z := z0 | z1`;
3. set each `g_j := g0 & g1`;
4. normalize/simplify.

No Boolean **formula-level** branching is required.

## 10. Complexity parameters

The logical clause width stays q+1, but term DAGs may grow.

Useful source-sensitive parameters include:

- number of quantified BA variables;
- term-DAG size;
- cofactor sharing;
- support-variable incidence/treewidth;
- affine/XOR structure;
- symmetry among quantified variables;
- number q of positive obligations.

A practical implementation should use Tau's canonical term normalization and DAG sharing after each recurrence step and abort to the existing quantifier eliminator if a growth threshold is exceeded.

## 11. Validation

The support-level version is already tested by `experiments/aba_alternating_clause_qe.py`, which compares all E/A prefix patterns up to three quantified variables against explicit ABA support-extension semantics.

An additional one-variable falsification run compared the source cofactor recurrences above against explicit support refinement on 9,500 randomly generated coarse cases covering both existential and universal projection with 0..4 disequation obligations; no mismatch was found.

This remains bounded checking, not a substitute for the structural proof.

## 12. Next implementation target

At pinned Tau commit `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`, detect a homogeneous untyped/countable-ABA quantifier block whose normalized body is one conjunction of `bf_eq`/`bf_neq` atoms.

Before generic Boole decomposition:

1. collapse equations to z;
2. apply the recurrence above through the block;
3. rebuild the quantifier-free Tau clause;
4. differential-check on a research branch against current `qelim/normalize` over Tau's own demo and generated corpus;
5. preserve the existing pipeline as fallback/oracle.

The direct rule should only be enabled for BA types whose atomless semantics are verified; do not silently apply the existential recurrence to arbitrary finite/non-atomless Boolean algebras.

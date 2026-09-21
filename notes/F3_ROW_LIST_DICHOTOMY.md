# Complete scalar row-list dichotomy over F3

**Status:** DERIVED complete complexity classification for fixed nonempty row-list languages over `A=(F_3;+,-,0)`. The source NP-complete problems and Gaussian elimination are classical. This finite-domain classification is best viewed as a specialized CSP consequence / solver laboratory, not yet as a novelty claim. Tau-independent.

## 1. Problem family

Let

`A=(F_3;+,-,0)`.

For a fixed collection

`Lambda subseteq P(F_3) \ {empty}`

of allowed nonempty scalar lists, define `RLTI(Lambda)`:

**Input**

- arity n;
- finitely many rows `z in F_3^n`;
- for each row, a list `L_z in Lambda`.

**Question**

Does there exist an n-ary A-term

`t_alpha(x)=alpha dot x`

such that

`t_alpha(z) in L_z`

for every row?

The list language Lambda is fixed and not part of the instance.

There are exactly seven nonempty subsets of F_3:

- three singletons;
- three doubletons;
- the full set.

Hence there are

`2^7-1=127`

nonempty fixed list languages Lambda.

## 2. Classification theorem

### Theorem 1 -- F3 scalar row-list dichotomy

For every nonempty fixed Lambda, exactly one of the following holds.

### Class P1 -- no doubleton is allowed

If every list in Lambda has size 1 or 3, then `RLTI(Lambda)` is in P.

### Class P2 -- every allowed list contains 0

If Lambda contains a doubleton but

`0 in L`

for every `L in Lambda`, then every instance is satisfiable by the zero term and the problem is trivial.

### Class H -- all remaining cases

If Lambda contains at least one doubleton and some allowed list omits 0, then `RLTI(Lambda)` is NP-complete.

Thus among the 127 nonempty fixed list languages:

- 15 fall in P1;
- 12 additional languages fall in P2;
- 100 are NP-complete.

## 3. Proof of P1

If no doubleton is present, every nonvacuous row constraint is a singleton

`alpha dot z = b`.

Collect these into a linear system over F_3 and solve it by Gaussian elimination.

Full-set rows impose no condition.

Therefore `RLTI(Lambda)` is in P.

## 4. Proof of P2

If every allowed list contains 0, choose

`alpha=0`.

Then every row evaluates to 0 and satisfies its list.

No search is required.

## 5. NP membership in the remaining cases

For every fixed Lambda, a coefficient vector

`alpha in F_3^n`

is a polynomial-size certificate.

Evaluate every row in polynomial time.

So it remains only to prove NP-hardness.

## 6. Hard case A -- the nonzero doubleton is available

Suppose

`{1,2} in Lambda`.

Then `F3_NONZERO_ROW_HARDNESS.md` reduces graph 3-colorability directly:

for each edge `{i,j}` use row

`e_i-e_j`

and list `{1,2}`.

The constraint is

`alpha_i-alpha_j != 0`,

exactly proper 3-coloring.

Therefore the problem is NP-hard even using only that one list type.

## 7. Hard case B -- only zero-containing doubletons are available

Now suppose `{1,2}` is not in Lambda, but Lambda contains a doubleton and some list omits 0.

Every available doubleton must then be

`D={0,a}`

for some nonzero `a in F_3`.

Since some allowed list omits 0 and the only doubleton omitting 0 was excluded, Lambda must contain a nonzero singleton

`{b}`

with `b in {1,2}`.

Reduce positive 1-in-3-SAT.

### Boolean-variable row

For variable i use row

`a e_i`

with list

`{0,a}`.

Because

`t_alpha(a e_i)=a alpha_i`,

and a is invertible,

`a alpha_i in {0,a}`

iff

`alpha_i in {0,1}`.

### Clause row

For clause `(i,j,k)` use row

`b(e_i+e_j+e_k)`

with list

`{b}`.

Then

`b(alpha_i+alpha_j+alpha_k)=b`

iff

`alpha_i+alpha_j+alpha_k=1 mod 3`.

For Boolean coefficients this holds iff exactly one coefficient is 1.

Thus positive 1-in-3-SAT reduces polynomially to `RLTI(Lambda)`.

So every remaining language is NP-hard.

Together with NP membership, every Class H language is NP-complete. QED.

## 8. Count the languages

### P1 count

If no doubleton is allowed, Lambda may use any nonempty subset of the four lists

`{0},{1},{2},F_3`.

Hence

`2^4-1=15`.

### P2-only count

The lists containing 0 are

`{0},{0,1},{0,2},F_3`.

There are `2^4=16` subfamilies. Four of them use neither doubleton, so they were already counted in P1.

Thus P2 contributes

`16-4=12`

additional languages.

### Hard count

`127-15-12=100`.

## 9. Noether-style inner ground

The dichotomy is controlled by two questions.

### Can the row language create a choice?

A singleton fixes one linear value; a full list does nothing. Neither creates disjunction.

A doubleton is the first place a local alternative appears.

### Can the zero solution escape all choices?

If every allowed list contains 0, all local alternatives collapse globally to the zero term.

If some list excludes zero, the zero escape is blocked. Then a doubleton supplies Boolean/color choice and a nonzero condition couples those choices across rows.

This is why the criterion is exactly:

`doubleton present` **and** `not every list contains 0`.

## 10. Relation to CSP dichotomy theory

Static `RLTI(Lambda)` can be compiled to a finite-domain CSP over F_3:

- auxiliary variables represent linear-form values;
- ternary addition constraints implement linear combinations;
- unary relations are the allowed lists in Lambda.

Therefore a general finite-domain CSP dichotomy already implies a P/NP-complete split in principle.

The theorem above is useful because this particular split has a two-line algebraic criterion and explicit reductions matching the term-interpolation representation.

Do not market it as a replacement for Bulatov/Zhuk/Schaefer-style CSP theory.

## 11. Solver consequence

For the standalone OrbitSynthesis backend over F_3, inspect the scalar row language before doing generic search.

1. **No doubletons:** Gaussian elimination.
2. **All lists contain 0:** return the zero term immediately.
3. **Otherwise:** switch to an NP-search backend (SAT/CSP/nogood learning), with specialized graph-coloring recognition when constraints normalize to nonzero pair differences.

This is an actual algorithm-dispatch theorem, not merely a complexity label.

## 12. Exact finite meta-check

`experiments/f3_row_list_language_classifier.py` enumerates all 127 nonempty fixed list languages and verifies the combinatorial partition:

- 15 P1;
- 12 P2-only;
- 100 hard-class languages.

It also checks the scaling identities used by the two hardness normalizations for every nonzero field element.

The script does not prove NP-hardness; the reductions above do.

## 13. Next frontier

1. Extend the classification from scalar output to `k>1` row lists `L_z subseteq F_3^k`.
2. Replace F_3 by F_p and determine how the criterion depends on p and the allowed unary/list relations.
3. Translate the finite-field list-language classification into a general algebraic criterion in terms of the polymorphisms preserved by the row language.
4. Determine which tractable row languages remain tractable after variable-domain/reactive closure is added.

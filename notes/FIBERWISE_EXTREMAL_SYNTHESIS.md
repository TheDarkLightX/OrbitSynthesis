# Fiberwise extremal synthesis: an abstract criterion beyond ABA

**Status:** DERIVED elementary order-theoretic criterion plus standard-structure examples. Terminology is intentionally descriptive; initial literature searches did not identify an established model-theoretic name for exactly this synthesis property.

The ABA extremal-response theorem suggests a precise question for other theories:

> When does a partial logical type admit a **greatest compatible response code** such that all formulas in the synthesis fragment are monotone upward in that code?

If it does, existential response search collapses to that greatest code exactly as in ABA.

## 1. Abstract restriction fiber

Let B be a finite set of partial logical states/types.

For each `b in B`, let

`E_b`

be the finite set of complete response codes extending b.

Assume `E_b` is equipped with a partial order `<=_b` chosen from the concrete extension representation.

Let

`Top_b in E_b`

be a greatest element when one exists.

A response predicate W on the disjoint union of the E_b is **fiber-upward** if

`e in W and e <=_b e'`

implies

`e' in W`.

## Theorem 1 — greatest-extension existential collapse

If E_b has a greatest element Top_b and W is fiber-upward, then

`exists e in E_b. W(e)`

iff

`W(Top_b)`.

### Proof

If W holds somewhere, that witness is <= Top_b, so upwardness gives W(Top_b). The converse is immediate.

This is the abstract content of ABA's maximal-support witness theorem.

## 2. Union-closed set codes give a greatest extension automatically

A particularly useful case is

`E_b subseteq P(U_b)`

ordered by set inclusion.

### Theorem 2

If E_b is nonempty and closed under finite unions, then

`Top_b := union E_b`

belongs to E_b and is its greatest element.

Since E_b is finite, repeated binary union closure is enough.

Thus:

> finite union-closed extension codes + upward predicates => no existential response search.

## 3. Zero restrictions can preserve union closure

Suppose extension codes are supports and a zero/equation constraint removes a fixed forbidden set Z.

Let

`E_b^Z = {e in E_b : e subseteq U_b\Z}`.

If E_b is union-closed, so is E_b^Z.

Its greatest element, when nonempty, is

`Top_b^Z = union E_b^Z`.

In ABA, this is exactly "take every locally allowed fine Venn cell."

## 4. Positive constraints are precisely the natural monotone fragment

Examples of inclusion-upward predicates on set codes:

- `e intersects K`;
- conjunction/disjunction of such hit predicates;
- any upward-closed family of codes;
- positive modal/fixed-point combinations when the predecessor itself preserves upwardness.

Negative requirements such as

`e avoids K`

are downward rather than upward and must be absorbed into the definition of admissible zero-safe codes before applying the theorem.

This mirrors the ABA separation:

`permanent zero restrictions + upward objective fragment`.

## 5. Universal environment reduction to minimal extensions

Now let a current state s have a finite environment-extension poset

`D_s`.

Suppose the predicate

`Good(d)`

meaning "the greatest system response above d satisfies the current upward target" is upward in d.

Let `Min(D_s)` be the inclusion/order-minimal environment extensions.

### Theorem 3 — minimal-environment universal collapse

If every element of D_s lies above some minimal element, then

`for all d in D_s. Good(d)`

iff

`for all m in Min(D_s). Good(m)`.

Every finite poset has the required minimal-element property.

Thus the ABA `minimal environment / maximal system` principle is an instance of a general extremal quantifier pattern.

## 6. ABA satisfies the criterion maximally

Fix a partial ABA support P.

Its zero-feasible full response codes are supports Q that:

- lie above P under support projection;
- use only Step-allowed, next-safe fine cells;
- hit every active partial fiber.

The union of any two such Q is again such a response support. Therefore the fiber is union-closed.

Its greatest element is exactly

`Max(P)=all allowed fine cells above P`.

Step disequations and upward next-state targets are inclusion-upward.

So ABA realizes Theorems 1–3 literally.

## 7. Equality gives an immediate failure case

Take the pure equality structure and a partial tuple containing two distinct elements a and b.

Possible one-point response types include

`y=a`

and

`y=b`.

In a natural choice-code representation these are mutually exclusive alternatives. There is no complete response type in which y is simultaneously equal to both a and b.

Thus the two extension choices have no common greatest compatible response.

The ABA union trick cannot be transported blindly to equality.

This does not make equality synthesis hard—its extension space is tiny—but it shows **omega-categoricity alone does not imply the extremal property**.

## 8. Dense order also fails the naive greatest-extension condition

For `(Q,<)` and old points `a<b`, possible y-types include:

- `y<a`;
- `y=a`;
- `a<y<b`;
- `y=b`;
- `b<y`.

These are mutually exclusive cuts/equalities. No one complete y-type combines them all.

Again, a finite type space exists, but not an ABA-style greatest response code under the obvious extension-choice order.

## 9. The Rado graph has a positive-fragment analogue

Fix distinct old vertices `a_1,...,a_k` in the countable random graph and restrict attention to a **fresh** new vertex y.

Encode y's one-point type by its adjacency set

`N_y subseteq {1,...,k}`.

The Rado extension property realizes every adjacency subset. Hence the fresh-extension code family is the whole powerset

`P({1,...,k})`,

which is union-closed with greatest element "adjacent to every old vertex."

Therefore for the positive adjacency fragment generated without negated-edge requirements:

`exists fresh y. positive_adjacency_property(y)`

can be witnessed by the all-adjacent extension whenever any fresh extension witnesses it.

This is a genuine analogue of Theorem 1, though much simpler than ABA's simultaneous refinement geometry.

### Caveats

- allowing y to equal old vertices introduces additional extension types outside the fresh-adjacency code;
- negated adjacency is not upward;
- transition/synthesis products must be analyzed, not assumed to inherit the property automatically.

## 10. Henson K_n-free graphs show how forbidden configurations destroy union closure

Consider the countable homogeneous K_n-free Henson graph.

Take old vertices containing a clique of size `n-1`.

A fresh vertex may be adjacent to a proper subset that omits one clique vertex, but it cannot be adjacent to all `n-1` clique vertices because that would create K_n.

Choose two individually admissible neighbor sets omitting different vertices. Their union can contain the whole `(n-1)`-clique and is therefore inadmissible.

Thus the one-point adjacency-code family is not union-closed in general and has no greatest adjacency response.

This gives a clean structural obstruction:

> forbidden finite configurations can turn independently good positive choices into an incompatible union.

## 11. Unrestricted generic relational structures

For the Fraisse limit of **all** finite structures in a fixed relational signature (with the appropriate irreflexive/symmetry conventions), a fresh point's incidences with a fixed old finite tuple can be chosen independently whenever the age imposes no forbidden mixed configuration.

For positive incidence codes, this often yields a full powerset/product code and therefore a greatest extension.

The precise statement depends on relation arities and identifications among tuple entries. It should be formulated per age rather than as a slogan about all free-amalgamation structures: classes defined by forbidden configurations can have free amalgamation while still breaking union closure of positive one-point codes, as Henson-type examples demonstrate.

## 12. A classification program

For an effectively omega-categorical structure M and a chosen response fragment:

1. choose a concrete finite code for complete response types over a partial type b;
2. identify a natural information order on codes;
3. test whether the admissible extension-code family is join/union closed;
4. if yes, compute the greatest extension;
5. identify which atomic predicates are upward/downward;
6. absorb downward permanent constraints into admissibility;
7. derive the positive synthesis fragment from upward predicates;
8. test whether environment extension goodness is monotone and reduces to minimal elements.

This is a much stronger criterion than counting complete types.

## 13. Connection to the type-adjoint calculus

Generic existential quantification is the direct image

`r_!`

of a subset of extension types under restriction.

Under the fiberwise-top criterion and for upward sets, this direct image becomes evaluation at one distinguished fiber element:

`b in r_!(W) iff Top_b in W`.

So a generally set-valued adjoint collapses to a deterministic section on the positive fragment.

This is the abstract reason the ABA system existential quantifier disappears from the positive cell game.

## 14. Terminology / literature caution

Initial targeted searches found extensive literature on Fraisse one-point extensions, homogeneous structures, semilattices, and positive/categorical logic, but did not identify an established term for exactly:

`finite extension codes are join-closed and positive existential synthesis is witnessed by their greatest element`.

Do not introduce a permanent branded term until a deeper model-theory/positive-logic literature review is complete.

## 15. Next targets

1. Formalize Theorems 1–3 in Lean independently of ABA.
2. Work out the Rado-graph positive reactive product case rather than only one-point formulas.
3. Search homogeneous relational structures for a classification of union-closed one-point incidence families.
4. Determine whether a polymorphism/algebraic condition characterizes the greatest-extension property.
5. Compare this criterion with CSP tractability polymorphisms and with the omega-regular-satisfiability route from CSL 2026.

# Constructive maximal-support strategy for the ABA clause safety fragment

**Status:** DERIVED strategy theorem under Asor's effective-presentation witness assumption; d=1 winning-region semantics have been differentially checked. Concrete witness implementation in Tau remains open. Patent/freedom-to-operate scope is explicitly not inferred from the mathematical representation.

## 1. Starting point

Assume the setting of `ABA_SAFETY_CLAUSE_FIXEDPOINT.md`.

Let W be a winning support clause on next-state cells and fix an actual current state/input tuple `(s,i)`. Compute its complete partial ABA support type

`P = supp(s,i)`.

Form the full-context clause

`Full_W := Step(s,i,s') AND W(s')`.

Write its fine-cell representation as

`C(Z; H_1,...,H_q)`

on the `(s,i,s')` Venn cells.

Membership of P in the existential system projection means precisely:

1. every active partial cell v of P has at least one fine refinement outside Z;
2. for every positive obligation H_j, some active partial cell has an allowed fine refinement lying in H_j.

## 2. The maximal allowed response type

Let `fiber(P)` denote all full fine cells lying above active cells of P.

Define

`Q_max(P) := fiber(P) \ Z`.

Equivalently, activate **every fine cell above the observed partial type that is not forbidden by the combined Step/W equations**.

### Theorem 1 — Q_max is a legal full complete type whenever any response exists

If P satisfies the existential projection of `Full_W`, then:

1. `Q_max(P)` is nonempty in every active partial fiber and therefore restricts exactly to P;
2. `Q_max(P)` avoids every forbidden cell in Z;
3. `Q_max(P)` intersects every positive H_j;
4. hence `Q_max(P)` satisfies `Step AND W(next)`.

### Proof

This is the maximal-witness lemma of `ABA_CLAUSE_PROJECTION.md`. Every legal witness is a subset of Q_max. Existence ensures every active coarse fiber contributes at least one allowed fine cell and every positive obligation has at least one allowed witness. Taking all allowed cells preserves both properties.

## 3. Determinism at the type level

For fixed Step and W, `Q_max(P)` is a deterministic function of the observed partial complete type P.

There is no search over complete response types and no tie-breaking among many support witnesses:

`P -> Q_max(P)`

is canonical in the support representation.

This does **not** mean the concrete BA element realizing Q_max is uniquely determined. Many concrete tuples may realize the same complete type.

## 4. Effective concrete witness

Asor's ocLTL setup assumes M is effectively presented in the following strong sense:

- the complete type of a concrete tuple is computable;
- given a concrete tuple `a` and a complete extension type tau compatible with `tp(a)`, the witness b from the extension proposition can be computed.

Under that assumption, define the concrete system step:

1. observe `(s,i)`;
2. compute `P=tp(s,i)` / its ABA support code;
3. compute `Q_max(P)`;
4. invoke the effective extension-witness procedure on `(s,i,Q_max(P))`;
5. output the resulting `s'`.

Because Q_max extends P and satisfies the full winning/step clause, the computed concrete witness does too.

## Theorem 2 — constructive memoryless safety strategy

Let W* be a fixed point satisfying

`W* = Safe AND CPre(W*)`.

For every concrete state s whose type lies in W*, the procedure above produces, for every concrete environment input i, a concrete output/next state s' such that:

- Step(s,i,s') holds;
- the next-state type lies in W*;
- Safe continues to hold.

Therefore repeatedly applying the procedure yields a concrete strategy realizing the safety objective.

The type-level strategy is memoryless: its selected extension type depends only on the current partial type `tp(s,i)`. Concrete witness computation may use the effective presentation machinery but does not require game history beyond the current concrete tuple.

## 5. Causality

At time t the response uses only:

- the current concrete state/memory s_t;
- the current environment input i_t;
- fixed precomputed Step and winning-clause data.

It does not use future inputs. Thus the reconstructed strategy is causal in the sense required by ocLTL/Tau.

## 6. Relation to Asor's ocLTL reconstruction

Theorem 10 of Asor's ocLTL paper reconstructs a concrete strategy from a propositional type strategy by:

1. computing the current partial type;
2. reading the selected full type from the propositional strategy;
3. using the effective extension procedure to produce a concrete witness.

The clause-safety backend follows the same correctness bridge, but its type strategy is computed directly:

`selected full type = Q_max(partial type, winning clause)`.

Thus the proposed contribution is not a new witness principle. It is a direct symbolic way to compute the winning type strategy for the restricted ABA safety fragment without propositional LTL synthesis or complete-type enumeration.

## 7. Concrete ABA splitting implementation

In abstract ABA, atomlessness guarantees realization of Q_max by independently splitting each active partial minterm element according to the requested nonzero refinements.

For an executable representation there are two possible interfaces:

### A. Generic effective-presentation interface

Use the witness routine already required by ocLTL:

`extend(tuple, complete_type) -> witness`.

This is representation-agnostic and safest for the initial prototype.

### B. ABA-specific split interface

Expose a primitive that, for a nonzero BA element a and integer n, returns n pairwise disjoint nonzero pieces joining to a. Q_max can then be realized cell-by-cell and output coordinates reconstructed as joins of pieces.

This may be faster but is representation-specific and must be justified for Tau's actual BA values/Lindenbaum elements.

Do not assume a first-order definable Skolem function `split(a)` exists in the pure BA language. Effective computability in a chosen presentation is the relevant requirement.

## 8. Strategy representation size

A naive table

`partial complete type -> Q_max`

would reintroduce type enumeration.

The support formula gives an implicit strategy instead:

`Q_max = ActiveFine(P) AND NOT Z_full`.

At the cell level, a fine response bit is simply

`q_u = p_{projection(u)} AND NOT forbidden_u`,

where the forbidden mask also contains the pullback of the fixed winning clause's zero mask.

Thus the response **support code** is computed by local Boolean masking, not a lookup table.

Positive disequations need no additional selection logic because maximal support automatically satisfies them whenever the predecessor test says a response exists.

This local strategy circuit is one of the strongest algorithmic simplifications in the clause fragment.

## 9. What remains for end-to-end Tau synthesis

1. Identify/implement the effective extension-witness API for Tau's concrete atomless-BA representation.
2. Compile the fixed-point winning clause from Tau safety syntax.
3. At runtime, compute the partial support code of `(state,input)`.
4. Compute Q_max by local mask operations.
5. Realize Q_max as actual output data.
6. Differentially compare output traces against Tau's existing synthesized/executed specifications.

## 10. IP / novelty boundary

Public searches did not identify this exact maximal-support clause-safety algorithm as an academic theorem. However, Asor's patent family includes broad Boolean-algebra quantifier-elimination and recurrence/fixed-point software-specification claims, including continuation material involving weakly omega-categorical base languages.

Therefore:

- do not claim that this representation avoids Asor's patents;
- do not infer freedom-to-operate from mathematical novelty;
- use the user's Tau license and obtain patent counsel on any commercial implementation scope;
- paper novelty should focus on theorem/algorithm comparisons with precise prior-art citations rather than patent-boundary speculation.

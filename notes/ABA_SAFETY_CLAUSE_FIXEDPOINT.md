# Exact safety fixed points in the ABA support-clause fragment

**Status:** DERIVED closure theorem and algorithm; executable differential prototype is the next validation step. This is a restricted synthesis fragment, not a claim about arbitrary Tau specifications.

## 1. Game shape

Consider a synchronous safety game over atomless Boolean-algebra data with:

- current state variables `s`;
- environment input variables `i`;
- system-chosen next-state/output variables `s'`.

For the basic Tau/ocLTL memory picture, `s` is previous output memory, `i` is current input, and `s'` is current output / next memory.

Let the one-step legal/safety relation be a conjunction of ABA equations/disequations

`Step(s,i,s')`.

Let an additional state-only safety condition be

`Safe(s)`.

Both are represented as normalized support clauses.

The winning-region predecessor is

`CPre(W)(s)
 := forall i. exists s'. [Step(s,i,s') AND W(s')].`

The safety winning region is

`Win = nu W. [Safe AND CPre(W)].`

## 2. Cell contexts and projections

Let:

- `V_s` be the finite support-cell universe for state variables;
- `V_si` for `(s,i)`;
- `V_sis'` for `(s,i,s')`.

Coordinate forgetting induces surjective cell projections

`p_sys : V_sis' -> V_si`

and

`p_env : V_si -> V_s`.

Projection onto the next-state coordinates is

`p_next : V_sis' -> V_s`.

For interpreted constants, every universe is additionally refined by the same nonzero constant-region partition; all maps preserve the constant-region coordinate.

## 3. Pulling a winning clause back to the full context

Let

`W = C(Z_W; H_W)`

be a normalized clause on next-state support cells.

A joint support on `(s,i,s')` has next-state projection satisfying W iff it satisfies the pullback clause

`p_next^*(W)
 = C(p_next^{-1}(Z_W);
     {p_next^{-1}(H) : H in H_W}).`

### Proof

A next-state cell is active iff at least one joint support cell above it is active. Therefore:

- forbidding a next-state cell forbids every joint cell in its inverse image;
- requiring the next-state support to hit H is exactly requiring the joint support to hit `p_next^{-1}(H)`.

So support-clause form is preserved by pullback.

## 4. Conjunction with the step relation

Write

`Step = C(Z_T; H_T)`.

Then

`Step AND p_next^*(W)`

is represented before normalization by

`Z_full = Z_T UNION p_next^{-1}(Z_W)`

and positive family

`H_full = H_T UNION {p_next^{-1}(H): H in H_W}`.

Conjunction therefore only unions forbidden masks and concatenates positive obligations.

## 5. Existential system projection

Apply `ABA_ALTERNATING_CLAUSE_QE.md` along `p_sys`.

For a fine forbidden mask Z and positive mask H:

`ExistsZero_p(Z)
 = {v in V_si : p_sys^{-1}(v) subseteq Z}`

and

`ExistsHit_p(H,Z)
 = {v in V_si : p_sys^{-1}(v) intersects (H\Z)}`.

Thus

`exists s'. [Step AND W(s')]`

is again one support clause on `V_si`, with one transformed positive obligation for every obligation in `H_full` (unless it simplifies away or becomes impossible).

No positive obligation is split into multiple obligations.

## 6. Universal environment projection

Now project the resulting `(s,i)` clause along `p_env` using the direct universal rule:

`ForallZero_p(Z)
 = {v in V_s : p_env^{-1}(v) intersects Z}`

and

`ForallHit_p(H)
 = {v in V_s : p_env^{-1}(v) subseteq H}`.

The result is again a support clause on the state universe.

Therefore:

## Theorem 1 — CPre closure

If Step is a conjunction of ABA equations/disequations and W is a support clause, then

`CPre(W)`

is exactly representable as a support clause.

This requires no explicit complete-type enumeration and no BDD representation.

## 7. Safety conjunction preserves the fragment

`Safe AND CPre(W)`

is again obtained by union of forbidden masks and concatenation of positive obligations, followed by canonical normalization.

Hence:

## Theorem 2 — fixed-point closure

Starting from `W_0=True`, every approximant

`W_(n+1)=normalize(Safe AND CPre(W_n))`

is a normalized support clause.

Because the concrete game has finitely many state types, the descending semantic sequence reaches the greatest fixed point after finitely many strict changes.

By `CANONICAL_SUPPORT_CLAUSES.md`, fixed-point equality is detected by literal equality of the normalized forbidden mask and positive antichain.

No external equivalence solver is needed inside this fragment.

## 8. Positive-obligation growth is at most linear in iteration count

Let:

- `q_T = |H_T|` for Step;
- `q_S = |H_S|` for Safe;
- `q_n = |H_(W_n)|` after canonical normalization.

Before simplification:

- pulling W back preserves q_n obligations;
- conjunction with Step adds q_T;
- existential projection preserves the number of obligation slots;
- universal projection preserves the number of slots;
- conjunction with Safe adds q_S.

Therefore:

### Theorem 3

`q_(n+1) <= q_n + q_T + q_S`.

Since `q_0=0`,

`q_n <= n(q_T+q_S)`.

Canonical antichain normalization can only reduce this count.

This rules out exponential **obligation proliferation caused by quantifier projection** in the fragment. It does not rule out many fixed-point iterations or large bit masks.

## 9. Forbidden support grows monotonically along the greatest-fixed-point chain

The semantic approximants satisfy

`W_(n+1) subseteq W_n`.

For a satisfiable canonical support clause, its forbidden mask is exactly the set of support cells that occur in no satisfying support.

Therefore:

### Theorem 4

As long as the approximants are satisfiable,

`Z_n subseteq Z_(n+1)`.

The forbidden mask can strictly grow at most `|V_s|` times.

Positive obligations may continue to strengthen after the zero mask stabilizes, so this is not a bound on the total number of fixed-point iterations.

## 10. Support-width complexity

Suppose:

- d BA coordinates of state;
- e environment BA coordinates;
- d next-state/output coordinates;
- finite interpreted constants with partition rank `rho(C)`.

Then support widths are

`N_s    = rho(C) * 2^d`

`N_si   = rho(C) * 2^(d+e)`

`N_full = rho(C) * 2^(2d+e)`.

For the ocLTL packed case with e=d:

`N_full = rho(C) * 2^(3d)`.

One CPre operation performs direct-image/right-image tests on bit masks over these cell universes. Ignoring antichain minimization, the raw cell-incidence work is linear in `N_full` times the current number of positive obligations.

Compare explicit full complete types in the pure case:

`|T_(2d+e)| = 2^(2^(2d+e)) - 1`.

Thus the fragment operates on a singly-exponential support universe rather than a double-exponential complete-type set.

This is a representation theorem, not yet an end-to-end runtime theorem.

## 11. Adjoint form of CPre

Let `pull_next` be inverse image along the next-state cell projection. Let `exists_sys` be the left adjoint along `p_sys` and `forall_env` the right adjoint along `p_env`.

At the semantic set-of-types level:

`CPre(W)
 = forall_env(
     exists_sys(
       Step INTERSECT pull_next(W)))`.

The support-clause formulas above are the concrete mask implementation of this adjoint composition.

This connects directly to `TYPE_ADJOINT_CALCULUS.md`.

## 12. Why this matters for Tau

This is a possible direct-synthesis path, not merely a faster first-order QE subroutine:

`Tau conjunctive safety spec
 -> support clause
 -> exact symbolic CPre
 -> canonical clause fixed point
 -> winning support family / strategy reconstruction`.

It bypasses:

- complete type enumeration;
- generic atom-level Shannon decomposition for the protected fragment;
- repeated materialization of arbitrary normal forms;
- BDD blowups such as the expander families in `ABA_OBDD_LOWER_BOUNDS.md`.

## 13. Required falsification

1. Implement the clause CPre operator and compare with explicit type-game enumeration for d=1 and bounded d where enumeration remains possible.
2. Generate random Step/Safe clauses and compare every fixed-point approximant semantically.
3. Construct formulas where antichain H grows rapidly; determine whether normalization dominates runtime.
4. Compare against Tau's synthesized/executable behavior on equivalent safety specifications.
5. Determine exactly how a winning clause yields a concrete system choice `s'` for every environment input—decision/witness synthesis, not only winning-region membership.

The last item is essential: realizability without a strategy extractor is not yet a synthesis backend.

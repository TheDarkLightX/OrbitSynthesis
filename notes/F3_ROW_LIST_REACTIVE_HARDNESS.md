# Easy SMP, hard reactive list synthesis over F3

**Status:** DERIVED NP-completeness theorem with an exact finite calibration. The NP-completeness of positive 1-in-3-SAT and polynomial-time linear-algebra/SMP facts are classical prior art. The reduction to sparse fixed-domain original-signature term safety is under novelty review. Tau-independent. Not Lean-checked.

## 1. Purpose

`SUBPOWER_ROW_LIST_SYNTHESIS.md` separates fixed-domain term safety into:

1. the generated subpower `P_Z`, which records which value-vectors are realizable by one term; and
2. row lists `L_z`, which record reactive safety/invariance choices.

A tempting conjecture is:

> if SMP / compact subpower representation is easy for the controller algebra, then the reactive row-list problem should also be easy.

This note refutes that conjecture with the smallest classical linear-algebra laboratory we found.

Take the fixed algebra

`A = (F_3; +, -, 0)`.

Its term operations are homogeneous linear forms over `F_3`, so its ordinary term-interpolation/SMP problem is Gaussian linear algebra.

Nevertheless, row-list term interpolation is NP-complete, and so is a sparse input-free fixed-domain safety problem whose controller coordinates are A-terms.

## 2. Term operations of the fixed algebra

Let

`A=F_3={0,1,2}`

with group addition, inverse, and the constant 0.

Every n-ary term operation has the form

`t_alpha(x_1,...,x_n) = alpha_1 x_1 + ... + alpha_n x_n`

for a coefficient vector

`alpha in F_3^n`.

Conversely every such linear form is a term operation.

This follows by structural induction on group terms, and every coefficient in F_3 is generated from repeated addition/inverse.

Thus a term is represented by n field coefficients.

## 3. Row-list term interpolation problem

For this fixed A define:

### F3-RLTI

**Input:**

- an arity n;
- an explicit finite set of observations `Z subseteq F_3^n`;
- for each `z in Z`, a nonempty allowed list `L_z subseteq F_3` of size at most 2.

**Question:**

Does there exist an n-ary A-term t such that

`t(z) in L_z`

for every `z in Z`?

Equivalently, does there exist `alpha in F_3^n` satisfying all row-list constraints?

## 4. Membership in NP

The coefficient vector

`alpha in F_3^n`

is a polynomial-size witness.

For every listed observation z, compute the dot product

`alpha dot z mod 3`

and test membership in the explicit list L_z.

Therefore F3-RLTI is in NP.

## 5. Reduction from positive 1-in-3-SAT

Positive 1-in-3-SAT asks for a Boolean assignment such that every three-variable positive clause has exactly one true variable. This problem is classically NP-complete by Schaefer's Boolean CSP dichotomy; later positive-1-in-3 work explicitly uses the same hardness baseline.

Take an instance with Boolean variables

`x_1,...,x_n`

and clauses consisting of three distinct variables.

Let

`e_i in F_3^n`

be the i-th standard basis vector.

### Variable constraints

For every variable i add observation

`e_i`

with list

`L_(e_i)={0,1}`.

Since

`t_alpha(e_i)=alpha_i`,

this forces

`alpha_i in {0,1}`.

Thus every coefficient becomes a Boolean truth value.

### Clause constraints

For a clause

`(x_i,x_j,x_k)`

add observation

`c_(i,j,k)=e_i+e_j+e_k`

with singleton list

`L_c={1}`.

Then

`t_alpha(c)=alpha_i+alpha_j+alpha_k mod 3`.

Because each alpha is 0 or 1, the integer sum is one of

`0,1,2,3`.

It is congruent to 1 modulo 3 **iff the integer sum is exactly 1**.

Therefore the clause constraint holds iff exactly one of the three variables is true.

### Theorem 1 -- F3-RLTI is NP-complete

The construction is polynomial and uses lists of size at most two.

A positive 1-in-3 assignment gives the coefficient vector alpha, and every feasible alpha is a positive 1-in-3 assignment.

Combined with NP membership, F3-RLTI is NP-complete. QED.

## 6. Why this is a genuine SMP/reactive separation

Ordinary SMP asks whether one **specified** evaluation vector lies in a generated subpower. For this A that is linear span/subspace membership and is polynomial-time by Gaussian elimination.

F3-RLTI instead asks whether the subpower contains **some** vector selected from a Cartesian product of small row lists.

The hard part is not membership in the subpower. It is choosing a compatible point of the subpower from many local alternatives.

In the terminology of `SUBPOWER_ROW_LIST_SYNTHESIS.md`:

`P_Z intersection Product_z L_z != empty`

can be NP-hard even though membership in P_Z is easy.

This is the cleanest complexity separation so far in OrbitSynthesis.

## 7. Embed F3-RLTI into a safety game

Now turn the same instance into an actual finite reactive object.

There is no environment input.

### State space

The ambient local state space is

`F_3^n`.

We are given a **fixed candidate invariant domain W explicitly**, rather than enumerating the ambient exponential state space.

Let Z contain all variable and clause observation vectors from section 5.

Define helper states

`q_a = a e_1`, `a in F_3`.

Thus

- `q_0=0`;
- `q_1=e_1`, which is already the first variable observation;
- `q_2=2e_1`.

Take

`W = Z union {q_0,q_2}`.

So all three q_a belong to W.

### Sparse safe-successor lists

For every state in W give an explicit list of safe next states.

For variable state e_i:

`Next(e_i)={q_0,q_1}`.

For clause state c:

`Next(c)={q_1}`.

For q_0:

`Next(q_0)={q_0}`.

For q_2:

`Next(q_2)={q_0,q_2}`.

Every list has size at most two.

Outside W the safety relation can be declared unconstrained, because fixed-domain feasibility only asks whether one controller keeps W safe and invariant.

## 8. Controllers are linear maps

A vector-valued positional controller

`sigma:F_3^n -> F_3^n`

whose coordinates are A-terms is exactly a linear map

`sigma(x)=M x`

for some matrix

`M in F_3^(n x n)`.

## 9. Satisfying assignment gives a winning term controller

Given a satisfying Boolean coefficient vector alpha, define

`sigma_alpha(x)=(t_alpha(x),0,...,0)`.

This is a term controller: its first coordinate is t_alpha and the remaining coordinates are the constant-zero term.

Check the state classes.

### Variable state

`sigma(e_i)=q_(alpha_i)`

and alpha_i is 0 or 1, so the successor is q_0 or q_1.

### Clause state

The 1-in-3 condition gives

`t_alpha(c)=1`,

so the successor is q_1.

### q_0

Linearity gives

`sigma(q_0)=q_0`.

### q_2

Since `q_2=2e_1`,

`sigma(q_2)=q_(2 alpha_1)`.

If alpha_1=0 this is q_0; if alpha_1=1 this is q_2.

Thus every state remains in its safe-successor list and W is invariant.

## 10. Winning term controller gives a satisfying assignment

Conversely suppose some A-term controller

`sigma(x)=Mx`

keeps W safe.

Let alpha be the first row of M.

At variable state e_i, safety requires

`sigma(e_i) in {q_0,q_1}`.

Therefore its first coordinate satisfies

`alpha_i in {0,1}`.

At clause state

`c=e_i+e_j+e_k`,

safety requires the whole next state to be q_1, in particular

`alpha_i+alpha_j+alpha_k = 1 mod 3`.

Because the three coefficients are Boolean, exactly one equals 1.

Hence alpha is a satisfying positive 1-in-3 assignment.

The other rows of M cannot evade this first-coordinate argument.

## 11. NP-complete sparse fixed-domain safety theorem

Define the following representation-sensitive problem.

### F3-SPARSE-TERM-SAFETY

**Input:**

- state arity n;
- an explicitly listed candidate invariant domain `W subseteq F_3^n`;
- for each state in W, an explicit list of at most two permitted successors in W.

There are no environment inputs.

**Question:**

Is there one positional controller `sigma:F_3^n->F_3^n` whose coordinates are terms of `(F_3;+,-,0)` and such that

`sigma(w) in Next(w)`

for every w in W?

### Theorem 2

F3-SPARSE-TERM-SAFETY is NP-complete.

### Proof

NP membership: an `n x n` matrix M over F_3 is a polynomial-size certificate; evaluate M on every explicitly listed state and check its successor list.

NP-hardness: sections 7--10 give a polynomial reduction from positive 1-in-3-SAT. QED.

The hardness holds with:

- one fixed 3-element algebra;
- no environment input;
- no temporal memory beyond the current state;
- a fixed candidate domain supplied explicitly;
- at most two allowed successors per state;
- polynomial-time ordinary SMP / term interpolation for the controller algebra.

## 12. Representation caveat

This theorem deliberately uses a **sparse fixed-domain representation**.

The ambient state space `F_3^n` has exponential size and is not explicitly enumerated. The input lists only W and the safe successors relevant on W.

Do not restate Theorem 2 as a complexity theorem for an explicitly tabulated full transition relation over all `3^n` states; that would change the input-size measure.

Likewise, the safe relation in this reduction is not claimed to be definable by one module equation. In fact, the binary coefficient lists `{0,1}` are deliberately non-affine.

This theorem concerns the general standalone finite-algebra/list-safety interface, not the narrower equation-only quasi-primal theorem.

## 13. Exact finite calibration

`experiments/f3_row_list_hardness.py` checks the reduction in three independent forms.

1. It exhausts every subset of possible positive 3-variable clauses for n=3,4,5: 1,042 formulas total.
2. It compares Boolean positive-1-in-3 satisfiability against F3 coefficient/list feasibility on every formula.
3. It constructs the sparse safety instance and checks the explicit controller embedding. For n=3 it additionally enumerates all `3^9=19683` linear controller matrices as an independent whole-controller check.

The experiment is a calibration of the reduction; the proof is Theorems 1--2.

## 14. Literature boundary

Classical/source-bound:

- T. J. Schaefer, *The Complexity of Satisfiability Problems*, STOC 1978: positive 1-in-3-SAT is an NP-complete Boolean CSP consequence of the dichotomy;
- finite vector-space/module SMP is Gaussian linear algebra; polynomial-time algorithms for finite vector spaces and related Mal'cev algebras are standard and appear explicitly in the SMP literature.

Adjacent CSP literature already emphasizes that constraints represented by generated subpowers and constraints represented by explicit allowed tuples have different algorithmic issues.

Current targeted searches did not locate this exact problem statement: a single original-signature term controller constrained by sparse per-state successor lists, with the easy-SMP/hard-reactive separation above. This is only bounded negative prior-art evidence, not a novelty conclusion.

## 15. Research consequences

### C1. SMP cannot be the only backend complexity metric

A workflow that scores an algebra merely by SMP complexity can dramatically underestimate synthesis difficulty.

We need a distinct measure for

`P_Z^k intersection row-lists`.

### C2. The semi-primal/demi special cases are genuinely special

Their row-list problems collapse because the term-evaluation subpower factorizes locally or orbitwise.

The F3 example shows that even an extremely tame linear subpower can become hard after row-list choices are imposed.

### C3. Obstruction-learning becomes useful

A solver should not just ask membership queries independently. It should learn incompatibilities among row choices, analogous to clause/nogood learning.

### C4. Complexity should be mapped by controller clone plus row language

The correct object is not only the term clone C or subpower P_Z, but the pair

`(term-evaluation subpower family, allowed row-list language)`.

This creates a bridge to CSP dichotomy machinery without reducing OrbitSynthesis to ordinary CSP syntax.

## 16. Next questions

1. Classify F3 row-list synthesis by the allowed family of row subsets; Schaefer-style dichotomy machinery may give a complete small-domain landscape.
2. Determine whether binary-list hardness survives for other fixed modules/Abelian groups, especially F_2 where modulo-2 destroys the exact-one encoding.
3. Find an equation-defined fixed algebra with easy SMP but NP-hard reactive domain/list selection, or prove a tractability boundary for equation-only module safety.
4. Determine whether fixed output arity k, rather than k growing with n as in the state-as-next-state embedding, changes the complexity.
5. Integrate a row-list/nogood backend into the standalone kernel without disturbing the specialized semi/demi/quasi solvers.

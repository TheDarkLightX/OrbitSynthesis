# Clone-constrained safety synthesis from finite relational bases

**Status:** DERIVED exact reduction. The clone/polymorphism machinery and finite-relatedness theorems are classical prior art. The controller-synthesis packaging and its algorithmic hierarchy are under novelty review. No patent/FTO claim is made.

## 1. Representation shift

The primal / semi-primal / demi-semi-primal / quasi-primal hierarchy is useful, but the deeper object is not the class name. It is the **term clone** of the controller algebra and, in particular, the relational information needed to present that clone.

Let A be a finite set and let C be a clone on A. Suppose there is a finite relational basis

`Gamma = {rho_1,...,rho_s}`

such that

`C = Pol(Gamma)`.

That is, an operation belongs to C exactly when it preserves every relation in Gamma.

For an algebra `A_alg`, take C to be its clone of term operations.

The synthesis question is then:

> Can a safe positional strategy be chosen whose coordinate functions lie in C?

This formulation is independent of Tau, Boolean algebra syntax, and omega-categorical type enumeration.

## 2. Finite safety game

Fix:

- state arity `k >= 1`;
- input arity `m >= 0`;
- local state set `A^k`;
- local input set `A^m`;
- next-state/controller output set `A^k`;
- safety relation
  `R subseteq A^k x A^m x A^k`;
- required invariant domain `W subseteq A^k`.

Write

`n = k + m`

for the observation arity.

A positional controller has coordinate functions

`f_j:A^n -> A`,  `j=1,...,k`,

and returns

`sigma(z)=(f_1(z),...,f_k(z))`.

We require each `f_j` to lie in C.

## 3. Strategy-table variables

For every observation

`z in A^n`

and output coordinate j introduce

`Y_(z,j) in A`.

The variables are the complete finite truth table of the controller.

The safety constraints for fixed W are, for every

`a in W`, `u in A^m`,

`Y_(a,u) in W`

and

`R(a,u,Y_(a,u))`.

The remaining issue is to force every coordinate table to belong to C.

## 4. Preservation constraints

Let `rho in Gamma` have arity r.

An n-ary operation f preserves rho iff for every choice of n columns

`c^1,...,c^n in rho`,

the coordinatewise output is again in rho.

Equivalently, regard those columns as an `r x n` matrix. Let

`z_1,...,z_r in A^n`

be its rows. Preservation is exactly the table constraint

`(Y_(z_1,j),...,Y_(z_r,j)) in rho`

for every output coordinate j.

Impose this for:

- every `rho in Gamma`;
- every n-tuple of columns from rho;
- every output coordinate j.

These are ordinary finite-domain CSP constraints.

## 5. Exact fixed-domain theorem

### Theorem 1 — relational-basis synthesis

For finite A, finite Gamma with `C=Pol(Gamma)`, safety relation R, and fixed candidate domain W, the CSP consisting of

1. all Gamma-preservation constraints on every controller coordinate; and
2. all safety/forward-invariance constraints on W

is satisfiable iff there exists a positional controller

`sigma:A^(k+m)->A^k`

whose coordinate functions belong to C and which keeps every state in W safe forever against all inputs.

### Proof: CSP -> controller

A satisfying assignment gives a total table for each coordinate `f_j`.

The preservation constraints are exactly the definition that each `f_j` preserves every relation in Gamma. Since

`C=Pol(Gamma)`,

we have `f_j in C`.

The game constraints say that for every state in W and every input, the chosen next state is safe and remains in W. Thus sigma wins on W.

### Proof: controller -> CSP

Take the complete table of the controller.

Every coordinate belongs to C and therefore preserves every relation in Gamma, so all preservation constraints hold. Safety and invariance on W give the remaining constraints.

No interpolation theorem beyond `C=Pol(Gamma)` is needed.

## 6. Variable-domain synthesis

One may introduce Boolean variables `W_a` and guard the safety/invariance constraints:

`W_a -> [R(a,u,Y_(a,u)) and W_(Y_(a,u))]`.

This yields an exact finite CSP for questions such as:

- does one C-controller win from a required initial set I?
- is there a C-controller with an invariant domain of size at least q?
- what are the inclusion-maximal C-controllable domains?

However, **do not assume** that these domains form a union-closed family or possess a greatest member.

`QUASIPRIMAL_NO_GREATEST_REGION.md` gives a single-equation quasi-primal game with two term-winning domains having no common term-winning superset.

So variable-domain controller synthesis is genuinely different from the ordinary unrestricted safety-game greatest-fixed-point problem.

## 7. Classical finite-relatedness gives broad exact compilers

A clone C on finite A is **finitely related** when `C=Pol(Gamma)` for some finite family Gamma of finitary relations.

Aichinger, Mayr, and McKenzie prove:

- every clone on a finite set containing an edge operation is finitely related;
- equivalently for the relevant finite-algebra setting, every finite algebra with few subpowers has a finitely related term clone;
- Mal'cev operations are 2-edge operations, so the result includes finite Mal'cev algebras.

Their examples include groups, rings, modules, loops, and other classical Mal'cev structures; edge terms also cover near-unanimity/lattice-style families.

Therefore:

### Corollary 2 — finite relational compiler for edge-term controllers

For every fixed finite algebra whose term clone contains an edge operation, fixed-arity original-signature positional safety-controller feasibility has an exact finite CSP encoding of the form in Theorem 1.

This is an existence/representation statement. It is **not** an efficiency theorem for our synthesis problem.

Reference:

E. Aichinger, P. Mayr, R. McKenzie, *On the number of finite algebraic structures*, Journal of the European Mathematical Society 16 (2014), 1673–1686, Theorem 6.1 and surrounding discussion.

## 8. Complexity accounting

Finite relatedness alone does not imply a compact practical encoding.

Let

- `q=|A|`;
- observation arity `n=k+m`;
- output arity k;
- `rho` have arity r and size `|rho|`.

The explicit controller table already has

`k q^n`

finite-domain entries.

A direct preservation expansion for rho considers

`|rho|^n`

column matrices.

Thus a finite relational basis can be exact while still giving exponential growth in observation arity.

Research targets therefore include:

1. low-arity relational bases;
2. sparse/generator representations of rho;
3. orbit compression of preservation matrices;
4. few-subpowers generating sets;
5. incremental separation: add only violated preservation constraints;
6. SAT/SMT/CSP encodings that exploit relation structure instead of materializing every matrix.

## 9. The existing hierarchy as basis geometry

The previous OrbitSynthesis cases now become special presentations of the same principle.

### Primal

`C` is the full clone.

No preservation constraints are needed.

Synthesis is the ordinary finite safety game.

### Semi-primal

The relevant preservation structure reduces to subalgebra membership.

For one observation z, the controller output is restricted to `Sg(z)`. Choices decouple observation-by-observation, yielding `TPre`.

### Demi-semi-primal

Subalgebra preservation is supplemented by global automorphism equivariance.

The relation graphs of automorphisms induce orbit/stabilizer constraints. Because all internal isomorphisms extend globally, choices can be made orbitwise and patched, yielding `DPre`.

### Quasi-primal

Graphs of arbitrary internal isomorphisms are needed.

They form a groupoid of partial symmetries. Strategy-table entries can be coupled across observations, and no local predecessor over state sets is exact in general.

### General finitely related clone

Arbitrary bounded-arity relations in Gamma couple potentially many controller-table entries simultaneously.

This is the natural next generalization.

## 10. Noether-style inner ground

The structural explanation for the hierarchy is:

> **Controller difficulty is governed by the geometry and arity of the relations that present the allowed controller clone.**

The familiar algebra labels are useful because they imply unusually simple relational presentations:

- none;
- unary/local subalgebra constraints;
- global symmetry graphs;
- partial-symmetry groupoids;
- general finite relational constraints.

This explains both why the early cases admit local/orbit fixed points and why quasi-primal coupling can destroy them.

## 11. Relation to CSP theory

The reduction runs in the opposite direction from the most familiar algebraic CSP use.

Classical CSP theory often starts with a relation language Gamma and studies the polymorphism clone `Pol(Gamma)` to classify the complexity of `CSP(Gamma)`.

Here the **controller language** is the clone C. A finite relational basis Gamma is used as a verifier/compiler for whether a complete strategy table belongs to C.

The algebraic machinery is classical; the reactive-synthesis object is different.

Prior-art searches so far have found substantial work on:

- polymorphism-based CSP complexity;
- first-order safety games;
- succinct/permissive safety strategies;
- universal safety controllers;

but no direct source yet for the exact problem "synthesize one winning strategy whose coordinate functions must lie in the term clone of a supplied finite algebra." This is a search result, not a novelty conclusion.

## 12. Falsification targets

1. Find a prior paper that already formulates clone-constrained reactive/controller synthesis in this exact sense.
2. Find a finitely related algebra where the naive full preservation encoding is unusably larger than direct term enumeration.
3. Determine whether edge-term/few-subpowers structure gives a **constructive compact** preservation checker for fixed controller arity, not merely existence of some finite basis.
4. Determine complexity of the decision problem when the algebra is part of the input versus fixed.
5. Test whether standard CSP local-consistency algorithms can operate directly on the strategy-table CSP for useful algebra classes.
6. Separate "one controller from all initial states" from "for each initial state there exists some controller"; `QUASIPRIMAL_NO_GREATEST_REGION.md` shows they differ.

## 13. Tool provenance

This direction was reached through the explicit Morph moves:

- R4 Encode/Compress: replace algebra-class labels by the relational presentation of the term clone;
- C4 Normalize/Canonicalize: quotient controller tables by preservation relations/symmetries;
- S4 Counterexample hunting: test whether a greatest controllable domain survives global coupling.

Research Kernel discipline is applied fail-closed: the reduction is DERIVED, the finite-relatedness theorem is SOURCE-BOUND classical prior art, and broader novelty remains UNKNOWN pending deeper literature review.

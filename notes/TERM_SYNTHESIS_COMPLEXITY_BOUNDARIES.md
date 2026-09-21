# Static term interpolation versus reactive controller synthesis

**Status:** DERIVED reduction plus SOURCE-BOUND complexity consequences. The Subpower Membership Problem and clone-membership results are classical prior art. The decomposition into static expressibility versus reactive/domain complexity is a research framing, not yet a novelty claim.

## 1. Why this note exists

The controller-synthesis program now uses three different finite representations that can look deceptively similar:

1. a **total controller truth table**;
2. a **partial prescribed table** that must extend to a term operation;
3. a **safety game** where controller values are not prescribed in advance but must be chosen consistently with safety, invariance, and one shared term table.

Universal algebra already has precise names and complexity theory for the first two. OrbitSynthesis should build on that literature instead of rediscovering it.

The key conclusion is:

> **term-constrained reactive synthesis contains static term interpolation as a degenerate input-free full-domain special case.**

Therefore any general solver inherits the static interpolation barriers before game dynamics enter.

## 2. Static problem A: total term-function membership

Fix a finite algebra A.

Input:

`f:A^n -> A`

by its complete truth table.

Question:

`is f a term operation of A?`

Kozik exhibited a fixed finite algebra for which this problem is EXPTIME-complete.

For algebras with few subpowers / an edge term, Aichinger, Mayr, and McKenzie prove finite relatedness and observe that total term-function membership becomes polynomial-time in the explicit truth-table size: membership can be checked by preservation of one fixed finite relation.

So the static total-table problem already has a strong algebra-dependent complexity boundary.

Sources:

- M. Kozik, *A finite set of functions with an EXPTIME-complete composition problem*, Theoretical Computer Science 407 (2008), 330--341.
- E. Aichinger, P. Mayr, R. McKenzie, *On the number of finite algebraic structures*, JEMS 16 (2014), especially Theorem 6.1, Theorem 6.2 and the concluding complexity remark.

## 3. Static problem B: partial term interpolation / SMP

Fix finite A.

Input:

- arity n;
- a finite domain `T subseteq A^n`;
- a partial function `f:T -> A`.

Question:

> is there an n-ary term operation t of A with `t|T=f`?

This is the **Subpower Membership Problem (SMP(A))**, in its partial-function interpolation presentation.

Kompatscher (STACS 2024) explicitly uses this formulation and notes:

- SMP can be EXPTIME-complete in general;
- whether every finite Mal'cev algebra has polynomial-time SMP was a long-standing question;
- the paper proves polynomial time for a large class of 2-nilpotent Mal'cev algebras.

This is more directly relevant to synthesis than total membership, because a safety specification typically constrains only some table entries or gives each entry a set of allowed outputs.

## 4. Exact reduction from SMP to term safety

Let A be any finite algebra and let

`f:T subseteq A^n -> A`

be an SMP instance.

Construct an **input-free** safety game.

### State

`a in A^n`.

Thus state arity is n.

### Controller / next state

`v in A^n`.

Each coordinate of the positional controller

`sigma:A^n -> A^n`

must be an n-ary term operation of A.

### Candidate invariant domain

Take the entire state space:

`W=A^n`.

So there is no domain-search or reachability issue.

### Safety relation

Require only

`a in T  ->  v_1=f(a)`.

When `a notin T`, every output is safe.

### Theorem 1 -- SMP embedding

The constructed full-domain safety game has an original-signature term controller iff f is interpolable by an n-ary term operation of A.

#### Proof: interpolation -> controller

Let t be a term operation extending f.

Use

`sigma(a)=(t(a), a_1, ..., a_(n-1))`,

with any n-1 projections in the remaining coordinates.

Every coordinate is a term operation. Since W is the full state space, invariance is automatic. On every a in T the first coordinate equals f(a), so sigma is safe forever.

#### Proof: controller -> interpolation

Let sigma be any winning term controller on W.

Its first coordinate `sigma_1:A^n->A` is a term operation. Safety at every a in T forces

`sigma_1(a)=f(a)`.

Hence sigma_1 interpolates f.

This is an exact equivalence, not merely a hardness analogy.

## 5. Consequence: a static lower bound for reactive synthesis

Any term-controller synthesis framework that accepts arbitrary finite/extensional safety constraints is at least as expressive as SMP.

Even more strongly, using **total** f gives a reduction from total term-function membership in which T=A^n.

For Kozik's fixed finite algebra, this yields:

### Corollary 2 -- EXPTIME-hard restricted synthesis family

There exists a fixed finite controller algebra A such that term-controller safety feasibility is EXPTIME-hard even under all of the following restrictions:

- no environment inputs;
- no temporal-memory construction beyond the current state;
- candidate invariant domain fixed to all of A^n;
- no winning-region search;
- no Boolean powers;
- no omega-categorical type abstraction;
- no Tau machinery;
- the safety relation merely prescribes the first next-state coordinate as a supplied total table f.

The reduction can be represented explicitly with polynomial blowup in the truth-table size of f. If the safety relation is stored sparsely as the graph constraint `v_1=f(a)`, the representation is essentially linear in that table.

This does **not** prove that every formulation of term-controller synthesis is EXPTIME-complete. It is a lower bound for a precise finite extensional-safety model.

## 6. Why finite relatedness does not solve sparse interpolation automatically

`RELATIONAL_BASIS_TERM_SYNTHESIS.md` says that if

`C=Pol(Gamma)`

for finite Gamma, a *complete* controller table belongs to C exactly when it satisfies finitely many preservation constraints.

For a fixed edge-term algebra this makes **total table membership** polynomial in the explicit table size, matching Aichinger--Mayr--McKenzie.

But SMP supplies only a partial table and asks whether some total C-table extension exists.

The missing values are existential variables. Once the complete truth table is not part of the input, the implicit table has size `|A|^n`, exponential in the succinct arity parameter n.

Therefore:

> **finite relatedness is a verifier for completed tables; it is not by itself a polynomial-time interpolation algorithm for sparse partial tables.**

This distinction explains why Mal'cev SMP remains nontrivial despite finite-relatedness results for Mal'cev/edge-term clones.

## 7. 2026 polynomial-interpolation paper: adjacent but different

Aichinger, Kapl, and Rossi (2026) study **polynomial** interpolation of partial functions in finite Mal'cev algebras.

Polynomial functions may use constants from A. Their preservation theory naturally uses **diagonal subalgebras** of finite powers, because all constant tuples must remain available.

OrbitSynthesis currently asks for **term** controllers in the original signature, with no arbitrary parameters/constants. That is governed by the term clone and all relevant compatible relations/subpowers, not just the polynomial clone.

So the 2026 work is highly relevant for a future **parameterized/polynomial-controller mode**, but it does not subsume the current term-controller results.

This suggests a new controller hierarchy:

1. original-signature term controller;
2. polynomial controller with finitely many allowed parameters;
3. arbitrary finite local table;
4. Boolean-power/Tau representation controller.

Each enlargement can strictly increase realizability.

## 8. Two independent complexity axes

The program should stop speaking of "the complexity of algebraic synthesis" as one number.

### Axis S -- static expressibility

How hard is it to decide or construct membership/interpolation in the allowed controller clone?

Examples:

- unrestricted fixed finite algebra: can be EXPTIME-hard;
- edge-term/few-subpowers: total truth-table membership is polynomial;
- important Mal'cev SMP subclasses: polynomial algorithms are known;
- general Mal'cev SMP remains structurally nontrivial.

### Axis R -- reactive compatibility

Even if individual table entries are locally admissible and static interpolation is easy, can **one shared controller** satisfy all safety/invariance obligations simultaneously?

Examples already proved in OrbitSynthesis:

- semi-primal: choices decouple locally;
- demi-semi-primal: choices couple only along extendable global automorphism orbits and an exact greatest region survives;
- quasi-primal: partial internal symmetries can couple observations globally;
- `QUASIPRIMAL_NO_GREATEST_REGION.md`: the controllable-domain family need not even have a greatest element.

The quasi-primal no-greatest phenomenon is therefore a **reactive/domain-selection obstruction**, not merely an SMP obstruction.

## 9. A third axis: representation size

The same mathematical instance can be presented as:

- an explicit complete controller table;
- a sparse partial table;
- an algebraic term/circuit;
- an orbit quotient;
- a finite relational-basis CSP;
- a succinct symbolic safety formula.

Complexity claims must name the representation.

In particular:

- polynomial in explicit truth-table size may still be exponential in arity n;
- a relation-preservation test with `|rho|^n` matrices is polynomial in `|A|^n` when A and rho are fixed, but exponential in n;
- an orbit quotient can be exponentially smaller than the raw state table for highly symmetric instances.

This is the correct place to apply Tao's "calibrate exponents on basic examples" rule.

## 10. Finite calibration

`experiments/smp_to_term_safety.py` uses the two-element meet-semilattice

`A=({0,1}; meet)`

with observation/state arity n=3.

Its 3-ary term operations are exactly the seven nonempty conjunctions of variables.

The checker exhausts all

`3^(2^3)=3^8=6561`

partial functions, where every input tuple is either undefined, prescribed 0, or prescribed 1.

For every one it compares:

1. direct term interpolation by the seven term operations;
2. brute-force synthesis over all `7^3=343` three-coordinate term controllers in the reduction above.

All 6561 instances agree.

This is a calibration of the reduction, not its proof.

## 11. Research consequences

### C1. Use SMP algorithms as static subroutines

For algebra classes with strong SMP algorithms, do not materialize a full relational-basis truth table unless needed. Ask whether the game constraints can be decomposed into a sequence of interpolation/extension queries.

### C2. Study list interpolation

Safety does not normally prescribe one output. It gives an allowed set

`L_z subseteq A^k`

for each observation z.

The natural static generalization is therefore **list term interpolation**:

> choose one output from each allowed list so that each controller coordinate extends to a term operation.

This appears closer to the actual synthesis kernel than ordinary SMP.

### C3. Shared-controller versus per-state controller

`QUASIPRIMAL_NO_GREATEST_REGION.md` proves that

"every state has some winning term controller"

need not imply

"one term controller wins from all those states."

This is a quantifier-order distinction:

`forall state exists controller`

versus

`exists controller forall state`.

It should be explicit in every API and complexity theorem.

### C4. Parameterized/polynomial controllers

The 2026 Mal'cev polynomial-interpolation literature motivates an optional controller mode where fixed constants/parameters are allowed. The exact gap between term and polynomial controllability could itself be studied as an expressivity theorem.

## 12. Next falsification targets

1. Determine the exact complexity of **list term interpolation** for fixed quasi-primal and fixed Mal'cev algebras.
2. Determine whether initial-set term-safety for the fixed Quackenbush quasi-primal algebra is NP-hard despite polynomial fixed-domain groupoid propagation.
3. Build a reduction from SAT using partial-internal-isomorphism table choices, or falsify this by finding a polynomial decomposition.
4. Check whether the general Mal'cev SMP literature already contains a list-interpolation variant under another name.
5. Separate sparse and truth-table representations in every future benchmark.
6. Explore whether polynomial-controller mode collapses any of the quasi-primal no-greatest obstructions.

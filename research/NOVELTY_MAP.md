# Novelty / prior-art map

**Status:** working research-positioning document, not a legal opinion and not a paper novelty claim. Update whenever a closer source appears.

## 1. Ohad Asor / Tau

### Already established / do not claim

- first-order atomless Boolean-algebra quantifier elimination and its use in GS/NSO/Tau;
- temporal software specification with infinite BA-valued data and input/output distinction;
- recurrence/fixed-point reasoning in the Tau/GS line;
- ocLTL reduction from omega-categorical data to propositional LTL using complete types;
- generic binary encoding of complete types;
- equirealizability and concrete witness reconstruction under effective presentation;
- qualitative observation that fixed-point-definable fragments may avoid explicit type enumeration / propositionalization.

Primary sources:

- Ohad Asor, *Guarded Successor: A Novel Temporal Logic*, arXiv:2407.06214.
- Ohad Asor, *ocLTL: LTL Realizability and Synthesis Modulo omega-Categorical Structures*, arXiv:2605.12539.
- Ohad Asor, *Theories and Applications of Boolean Algebras*.
- Asor/IDNI patent family, including US 12,254,082 B1 and continuation publication US 2025/0252179.

## 2. Generic reactive synthesis modulo theories

The literature already contains several general architectures:

### Boolean abstraction / dynamic solver witnesses

Rodríguez and Sánchez, *From Realizability Modulo Theories to Synthesis Modulo Theories Part 1: Dynamic approach* (arXiv:2310.07904), reconstruct a concrete controller by combining a Boolean controller with dynamic theory-solver queries that produce models of existential theory formulas.

### Static / functional synthesis

Rodríguez, Gorostiaga, Sánchez, *Predictable and Performant Reactive Synthesis Modulo Theories via Functional Synthesis* (arXiv:2407.09348) combines Boolean abstraction with functional synthesis to produce a static deterministic controller and discusses optimizing theory outputs.

### CEGAR / full LTL modulo theories

Rodríguez, Gorostiaga, Sánchez, *Counter Example Guided Reactive Synthesis for LTL Modulo Theories* (CAV 2025) uses refinement/reactive tautologies.

Azzopardi, Di Stefano, Piterman, Schneider, *Full LTL Synthesis over Infinite-state Arenas* (CAV 2025 / arXiv:2307.09776) uses Boolean abstraction, counterstrategy checking, and refinement to treat full LTL over infinite arenas.

### Logical games / CHCs

Faella and Parlato, *Reachability Games Modulo Theories with a Bounded Safety Player* (AAAI 2023), encode a class of logical infinite-state games into constrained Horn clauses and obtain strategies through CHC queries.

### Shield synthesis

Rodríguez et al., *Shield Synthesis for LTL Modulo Theories* (AAAI 2025), applies synthesis-modulo-theories techniques to expressive safety shields.

These works establish that "symbolic synthesis over theories," "solver-based witnesses," "static deterministic controllers," and "safety synthesis modulo theories" are not novelty claims available to OrbitSynthesis in the abstract.

## 3. Classical symbolic game solving

BDD/symbolic fixed-point computation for finite-state systems is classical (Burch et al., 1990 and extensive later work). Direct fixed-point algorithms for Büchi/GR(1)/parity/Emerson-Lei games are also established.

Therefore neither "use BDDs" nor "solve safety by a greatest fixed point" is novel.

## 4. Knowledge compilation

Bova–Slivovsky and later work show:

- structural CNF classes can compile to polynomial OBDDs;
- bounded degree alone does not suffice;
- expander-like positive 2-CNFs can require exponential OBDD size.

Therefore any claim of generally compact support OBDDs is false and already contradicted by standard lower-bound technology.

OrbitSynthesis's representation portfolio should be positioned as a response to this known frontier, not as discovery of it.

## 5. Categorical/algebraic logic

Quantification as the left/right adjoints of substitution/projection is classical Lawvere hyperdoctrine / algebraic-logic material.

Do not claim:

- existential direct image as a new calculus;
- universal right adjoint as a new calculus;
- cylindric/powerset quantifier algebras as novel.

The possible contribution is a **complexity-aware concrete presentation** of these operations on omega-categorical type spaces for synthesis.

## 6. OrbitSynthesis results that currently look genuinely differentiating

These require further literature review before paper-level novelty is asserted.

### Candidate A — minimum-width structural type code for ABA plus exact extension-circuit size

For pure ABA:

- complete k-types are nonempty supports on `2^k` Venn cells;
- the support code uses exactly `2^k` bits, meeting the information-theoretic minimum;
- adding r BA variables has a block-local extension relation whose ROBDD under a natural order has exact size

  `2^k(1+2^(r+1))`.

The bit count alone is not new because ocLTL already proposes generic binary coding. The differentiating fact is that the minimum-width bits are **semantic minterm-support coordinates** making restriction/extension local.

### Candidate B — exact support implementation of ocLTL ABA compatibility/feasibility

In ABA the type tables used by ocLTL can be replaced by support projection formulas:

- full-to-partial restriction is local OR;
- successor memory is local OR;
- data formulas compile directly to support Boolean functions;
- §5.2 feasibility is existential abstraction of eight structural support bits in the base 3-variable case rather than enumeration of complete types / all outer patterns.

Novelty question: has this exact structure-preserving ABA specialization been published before?

### Candidate C — closed conjunctive support calculus under arbitrary BA quantifier alternation

One conjunction of equations/disequations is represented by:

- one forbidden support mask Z;
- an antichain/list of positive nonzero obligations H_j.

Both existential and universal projection map the representation back to itself, with no disequation-slot proliferation. An alternating quantifier prefix can therefore be eliminated by repeated direct/right support images while retaining masks across blocks.

The semantic endpoint/QE identities are classical; the candidate contribution is the **canonical support representation, closure statement, representation-size bounds, and implementation architecture**.

### Candidate D — exact safety-game closure

For ABA safety games where Step and Safe are conjunctive equation/disequation clauses:

`CPre(W)=forall input. exists output,next. [Step AND W(next)]`

maps a canonical support clause W to another canonical support clause.

Therefore the greatest safety fixed point can be computed entirely in this mask/antichain representation with no complete-type enumeration and no mandatory BDD.

This is the current strongest candidate mathematical/algorithmic result.

### Candidate E — maximal-support response strategy

Whenever the existential response condition is feasible for a partial support P, the deterministic full response type

`Q_max(P)=all fine cells above P not forbidden by Step/W equations`

is a witness. Positive disequations require no choice because maximal support satisfies every hit obligation whenever any support can.

Combined with Asor's effective extension-witness assumption, this yields a direct memoryless concrete safety strategy.

The witness principle itself comes from effective presentation; the candidate contribution is the **closed-form type strategy**.

### Candidate F — semantic constant-partition parameter

For a finite interpreted-constant set C, complexity is governed by

`rho(C)=number of nonzero regions in the finite BA generated by C`,

not raw `|C|`.

Complete type count becomes

`(2^(2^k)-1)^rho(C)`

and support width becomes

`rho(C)2^k`.

Nested/disjoint constants can therefore have linear rho where generic constants have exponential rho. This looks like a useful parameterized-complexity angle.

## 7. Strong negative results that improve credibility

The project has deliberately killed several attractive overclaims:

- 7 arbitrary information bits do not mean 7 atomic BA equations; hardest ocLTL ABA fiber needs 8 atomic tests.
- complete-type projection information does not generally reduce the atomic test count in nondegenerate fibers.
- BDDs are not universally compact: positive two-minterm ABA disequation CNFs inherit expander-based exponential OBDD lower bounds.
- compact extension relation does not imply compact arbitrary fixed-point iterates.
- generic `omega`-categoricity is not the only route to decidable bounded synthesis; CSL 2026 gives non-omega-categorical examples.

These counterexamples should remain in any paper narrative.

## 8. Patent boundary

This file does not opine on patent scope.

Asor/IDNI's patent family contains broad claims around:

- BA quantifier elimination;
- software-specification logic;
- recurrence/fixed points;
- weakly omega-categorical bases in continuation material.

The user has stated they have been offered an official Tau license. Before commercializing a support/fixed-point backend, the written license should explicitly cover the relevant patent family and clarify ownership/licensing of foreground improvements.

Mathematical publication novelty and patent freedom-to-operate are separate analyses.

## 9. Current paper hypothesis

A defensible working paper title, **not yet ready for submission**, is:

> *Support Calculi for Safety Synthesis over Atomless Boolean Algebras*

Possible central theorem package:

1. structural support/type geometry;
2. quantifier adjoint calculus specialized to ABA support cells;
3. canonical conjunctive clause representation and alternating QE closure;
4. safety CPre closure;
5. direct maximal-support strategy reconstruction;
6. complexity comparison with explicit type enumeration;
7. upper/lower representation results showing when OBDDs help and when they fail;
8. implementation/differential evaluation against Tau.

Promotion requires closer prior-art reading of the synthesis-modulo-theories papers and an implementation benchmark, not just the theorem notes.

# Patent-aware boundary for independent OrbitSynthesis R&D

**Purpose:** Keep four questions separate:

1. what mathematics we are free to study;
2. what is academically novel;
3. what we can build as the independent core;
4. what claim-adjacent commercial use an eventual license / legal review permits.

This file is a research-management aid, **not legal advice**.

## 0. Foundational rule

Patents do **not** define the boundary of mathematical inquiry for this project.

OrbitSynthesis may study, prove, falsify, generalize, compare, and publish mathematics that intersects Ohad/IDNI's research area, subject to ordinary confidentiality/contract obligations if any arise later.

The patent/licensing boundary matters when choosing a product implementation, distribution model, or commercial method—not when deciding whether a mathematical theorem is worth understanding.

At present no Tau developer license has been executed for this program. Therefore the independent core assumes **zero licensed Tau rights**. If a license is later supplied, analyze it first and add permissions as an overlay; do not retroactively make the independent core depend on it.

## 1. Public patent family relevant to comparison

As of Aug 11 2026, public patent records show at least:

### Granted US patent

US 12,254,082 B1, **Using first-order theories of Boolean algebras to provide safe artificial intelligence (AI) systems and a novel software specification logic**.

Its published claims include a computer-implemented atomless-BA / extended-language workflow involving quantified expressions, equation/inequation normalization and closed-form quantifier-elimination steps in software-validation settings.

### Continuation/application family

The public patent family also identifies continuation application US19/083,375 / publication US2025/0252179 A1. Public application claims/descriptions should be treated as prosecution-sensitive and rechecked before any legal decision.

Public patent databases themselves caution that listed legal status is not a legal conclusion.

## 2. Research-overlap zones are NOT research prohibitions

The following topics are mathematically legitimate research subjects for OrbitSynthesis:

- atomless-BA quantifier elimination;
- complete-type/orbit reductions;
- weakly omega-categorical synthesis;
- recurrence/fixed-point methods;
- ocLTL translations;
- support encodings;
- Tau implementation comparisons.

We can understand them deeply, find stronger theorems, counterexamples, lower bounds, alternate proofs, and generalizations.

What changes by zone is how we treat **independent product implementation**, not whether we study the mathematics.

## 3. Claim-adjacent implementation zone

Treat these as requiring license/claim review before they become the independent commercial engine:

### I1. Tau-style atomless-BA QE implementation

Especially workflows closely tracking the published DNF equation/inequation cofactor-elimination recipe.

`ABA_BLOCK_QE.md` therefore remains valuable mathematics and comparison material. `TAU_SUPPORT_FASTPATH_INTEGRATION.md` is a potential licensed/partner engineering project unless later legal analysis says otherwise.

### I2. Reimplementation of a claimed Tau/NSO/ocLTL synthesis workflow

Do not assume that changing BDDs to support masks, antichains, SAT, or another data structure automatically changes the patent analysis.

### I3. Product features whose method substantially follows a public patent claim

Independent source code authorship does not by itself establish freedom to operate. If commercial relevance appears, do a claim chart / legal review.

## 4. Independent-core rule

The standalone OrbitSynthesis engine should not need any claim-adjacent Tau method for correctness.

It must pass the deletion test in `INDEPENDENT_RND_CHARTER.md`:

> remove Tau entirely; the theorem, IR, solver, controller semantics, and implementation still work.

This is both good research design and a strong practical independence discipline, while still not constituting a legal noninfringement opinion.

## 5. Independence-favored mathematics and software

### G1. Boolean-power causal lifting

`FINITE_BOOLEAN_POWER_SAFETY.md` studies causal safety over Boolean powers of arbitrary finite algebras:

`CPre_(M[B])(Lift(W)) = Lift(Pre_M(W)).`

The theorem and standalone local-game solver require no Tau implementation.

### G2. Clone-constrained controller synthesis

The primal / semi-primal / demi-semi-primal / quasi-primal hierarchy studies which finite strategy tables are terms of the original algebra.

Objects include:

- generated-subalgebra action filters;
- automorphism orbit/stabilizer games;
- internal-isomorphism groupoid CSPs;
- strict separation counterexamples.

This is universal algebra + game synthesis and can be built independently.

### G3. Boolean-power support geometry

Examples:

- support/type counts;
- extension geometry;
- extension relation circuits;
- support hypergraph clause semantics;
- prime-hit/maximal-loser/minimal-winner duality.

These are standalone mathematical objects.

### G4. Negative results / lower bounds

Examples:

- group-testing/co-atom lower bounds;
- Sperner-width fixed-point lower bounds;
- Landau-period lower bounds;
- primitive graph impossibility criteria;
- quasi-primal local-vs-global controller separation.

### G5. Finite-algebra safety synthesizer

A standalone engine whose input is finite algebraic/local-game data and whose output distinguishes controller semantics remains independent of Tau.

### G6. Boolean-power finite-algebra representation compiler

`TAU_FINITE_BOOLEAN_POWER_ENCODING.md` is mathematically a finite-algebra-to-Boolean-skeleton encoding. Its independent implementation should target our own IR/runtime first. Tau can become an adapter only if/when appropriate.

## 6. Capability-delta discipline

We should actively seek things that the inspected **public** Tau surface does not currently document, while avoiding claims about private/internal work.

Current high-value seams include:

- original-signature term-controller synthesis;
- clone-aware synthesis hierarchy;
- quasi-primal internal-isomorphism groupoid constraints;
- algebraic impossibility explanations;
- arbitrary finite-algebra Boolean-power synthesis;
- graph/semigroup structural diagnostics;
- Boolean-product/sheaf generalizations.

See `CAPABILITY_DELTA.md`.

## 7. Research-paper positioning

Keep three independent labels:

### Mathematical novelty

Did prior literature already prove the theorem or combination?

### Patent/legal status

Could a product implementation fall within an enforceable claim in the relevant jurisdiction?

### Tau relationship

Would a future license/partnership expressly permit a Tau-integrated implementation?

Never substitute one label for another.

## 8. Future developer-license overlay

If the Tau team sends a developer license, do not sign or architect around it before reviewing at least:

- exact licensed software and patents;
- patent-family / continuation coverage;
- field of use;
- commercial and noncommercial rights;
- deployment / hosted-service rights;
- redistribution / sublicensing;
- source modification / derivative work rights;
- confidentiality;
- publication rights;
- rights in pre-existing independent IP;
- ownership of improvements / feedback;
- license-back provisions;
- patent grants and defensive termination;
- termination and post-termination rights.

Especially protect **background IP**: the independent OrbitSynthesis mathematics, code, notes, and inventions that predate or sit outside the license should not silently become assigned "improvements" merely because they can interoperate with Tau.

If terms are favorable, define the resulting architecture as:

`independent OrbitSynthesis core + license-permitted Tau adapter/integration`.

## 9. Two engineering tracks

### Track A — independent engine

No Tau dependency.

Focus:

- finite algebra IR;
- finite local safety games;
- clone-constrained strategy synthesis;
- Boolean-power realization;
- hypergraph/orbit/groupoid algorithms;
- our own symbolic backends.

### Track B — optional Tau integration

Only after a favorable license or other adequate legal basis.

Possible work:

- Tau frontend/backend adapter;
- support-mask QE experiments;
- ocLTL support compiler;
- reuse of Tau parsing/normalization/execution;
- comparative optimization.

Track B should be deletable without damaging Track A.

## 10. Research directions may deliberately cross the patent mathematics

We should continue exploring Ohad's mathematics even when it is claim-adjacent because it can:

- reveal why the method works;
- prove better bounds;
- expose limitations;
- generate counterexamples;
- suggest generalizations beyond its assumptions;
- identify completely different mathematical carriers;
- tell us which problems to solve independently.

The project should **not** contort its mathematical questions merely to avoid reading or understanding patented material.

The design rule is instead:

> understand everything; copy nothing blindly; make the independent core stand on its own; obtain permission before using claim-adjacent implementation paths where permission is needed.

## 11. Claim-chart trigger

Before any of the following, stop and perform an actual legal/license review:

- commercial launch of a claim-adjacent method;
- paid third-party licensing;
- patent filing close to the Tau family;
- relying on a developer license for production rights;
- publication of material potentially covered by future confidentiality/improvement clauses;
- categorical statements that an implementation "does not infringe."

## 12. Current independent frontier

The leading independent research thesis is now broader than the earlier ABA optimization program:

> **Understand causal safety synthesis through the algebra of allowable controller functions and through Boolean-power patchwork, then build standalone solvers whose complexity and controller expressibility are controlled by finite-algebra symmetries, clones, support geometry, and transition dynamics.**

Tau/Ohad mathematics remains an important source of problems and comparison, but not a dependency or a ceiling.

## 13. Caveat

Patent scope, validity, infringement, territorial effect, prosecution history, and license interpretation are legal questions. Public-source technical comparison can inform counsel but cannot replace it.

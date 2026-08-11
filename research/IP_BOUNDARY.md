# Patent-aware research boundary for OrbitSynthesis

**Purpose:** Keep academic novelty, mathematical independence, and commercial freedom-to-operate as three separate questions. This file is a research-management aid, **not legal advice** and not a substitute for patent counsel.

## 1. Known Ohad/IDNI patent family relevant to this program

As of Aug 11 2026, public patent records show at least:

### Granted US patent

US 12,254,082 B1, **Using first-order theories of Boolean algebras to provide safe artificial intelligence (AI) systems and a novel software specification logic**.

Public claim 1 is specifically directed to a computer-implemented symbolic-AI method that:

- identifies an atomless Boolean algebra and extended first-order BA language;
- receives a quantified expression in that language for software-update acceptance;
- views the innermost quantified subexpression in DNF with positive equations and negative inequations;
- combines positive equations;
- constructs one of specified closed-form output clauses using 0/1 cofactors;
- eliminates the innermost quantifier;
- evaluates the result and conditionally installs the update.

The patent is assigned to IDNI AG and publicly listed as active.

### Continuation application

US 2025/0252179 A1, application 19/083,375, **Using First-Order Theories of Boolean Algebras to Provide Safe AI Systems and a Novel Software Specification Logic**.

Public claim 1 is much closer to program synthesis. It describes a computer-implemented method that:

- receives a software specification over a sliding time window in a decidable base language with finitely many equivalence classes for fixed finite symbol sets (weak omega-categoricity style condition);
- constructs a recurrence `phi_t` using alternating input/output quantification;
- determines a fixed point up to logical equivalence;
- evaluates an alternating-quantifier formula at the fixed point;
- outputs whether a program satisfying the specification exists.

This application is not the same legal object as the granted claim and may change during prosecution.

## 2. Red-zone research/implementation topics

Treat these as **overlap-risk** and do not frame them as independent commercial inventions without a claim chart / license review:

### R1. Tau-style atomless-BA DNF quantifier elimination

Especially:

- positive-equation squeezing;
- negative-inequation transformation;
- 0/1 cofactor closed forms;
- repeated innermost quantifier elimination in the patented software-validation context.

`ABA_BLOCK_QE.md` is therefore retained as explanatory mathematics / implementation comparison, not as a proposed new core invention.

### R2. General weakly-omega-categorical fixed-point program-synthesis recurrence

The continuation application's public claim is broad enough that any commercial system whose central method is:

`specification -> phi_t recurrence with forall-input/exists-output -> fixed point -> realizability decision`

should be treated as potentially overlapping until counsel/license analysis says otherwise.

### R3. Merely reimplementing ocLTL/Tau type reductions with different data structures

A support code, BDD, bitset, or antichain may be mathematically useful but changing representation alone does not establish freedom to operate if the claimed method steps remain present.

## 3. Green-field / independence-favored mathematics

These directions are intentionally framed around mathematical objects not sourced as mere restatements of Ohad's patented algorithms.

### G1. Boolean-power causal lifting theorem

`FINITE_BOOLEAN_POWER_SAFETY.md` studies when causal safety predecessor commutes with Boolean-power patchwork for arbitrary finite local algebras.

The core object is a universal-algebraic lifting theorem:

`CPre_(M[B])(Lift(W)) = Lift(Pre_M(W))`.

Historical prior art must still be checked (Wang, Even-Meyer, Boolean-product/Feferman-Vaught literature), but this is not being positioned as "Ohad's recurrence with a faster implementation."

### G2. Clone-constrained controller synthesis

The primal / semi-primal / demi-semi-primal / quasi-primal hierarchy studies **which finite positional strategy tables are original-signature term operations**.

Objects include:

- generated-subalgebra action filters;
- automorphism stabilizers/orbit games;
- internal-isomorphism groupoid CSPs;
- explicit Quackenbush counterexamples.

This is universal algebra + game synthesis, not a restatement of BA QE.

### G3. Support/type/extension geometry as pure mathematics

Examples:

- exact support type counts;
- projection-fiber hypergraphs;
- extension relation circuit/ROBDD complexity;
- group-testing lower bounds;
- orbit/type geometry of atomless Boolean powers.

These are mathematical structural results. Implementing them inside a patented application can still raise separate FTO questions.

### G4. Negative results / lower bounds

Examples:

- Sperner-width fixed-point lower bound;
- Landau-period lower bound;
- primitive-digraph unrealizability criteria;
- failure of local admissibility for quasi-primal term synthesis.

Negative/structural theorems are especially useful for academic independence because they do not amount to reproducing the claimed implementation recipe.

### G5. New finite-algebra/Tau representation layer

Encoding Boolean powers of arbitrary finite local algebras inside Tau's existing BA substrate is a distinct engineering direction, but FTO still depends on how the resulting synthesis engine decides realizability. Keep the representation theorem separate from any patented recurrence/QE pipeline.

## 4. Yellow-zone topics

These may be mathematically distinct but can become claim-adjacent depending on implementation.

### Y1. Direct safety fixed points over support hypergraphs

The carrier `(allowed cells, prime-hit antichain)` and its closed predecessor transform are mathematically different from explicit complete-type recurrence. But a product implementation that still receives a weakly omega-categorical software spec, constructs a forall/exists temporal recurrence, finds its fixed point, and returns realizability could potentially implicate the continuation claim.

Academic theorem: continue.

Commercial implementation: license/counsel gate.

### Y2. Support-symbolic ocLTL compiler

Structure-preserving support codes and closed atomic-feasibility circuits are worth researching. But if used merely as a replacement implementation of patented Tau/ocLTL synthesis steps, representation novelty alone is not an FTO conclusion.

### Y3. Tau quantifier fast path

A simultaneous support-mask implementation may be an optimization, but the granted patent expressly claims particular BA QE workflows. Treat this as Tau collaboration / licensed implementation work, not an independent product line, unless counsel concludes otherwise.

## 5. Research-paper positioning rule

Separate three claims in every draft:

### Mathematical novelty

"We prove theorem X, which was not found in prior mathematical literature after searches A/B/C."

This is a scholarship question.

### Patent novelty

Do not infer patentability from academic novelty. Patent novelty/nonobviousness uses different law and prior-art rules.

### Freedom to operate

Do not infer FTO from either of the above. A new theorem/implementation can still practice an older patent claim.

## 6. License boundary

The user reports that the Tau team has offered an official license to build on Tau.

Before commercializing anything close to the red/yellow zones, inspect the executed license for at least:

- patents/patent-family coverage;
- field of use;
- territory;
- sublicensing/deployment rights;
- rights to continuations/divisionals/future claims;
- ownership/license-back of improvements;
- publication rights;
- confidentiality constraints;
- termination consequences.

Do not assume "license to Tau" automatically covers every continuation patent or independent improvement.

## 7. Practical project split

Maintain two conceptual tracks:

### Track A — independent mathematics

Focus:

- Boolean powers of finite algebras;
- clone-constrained safety synthesis;
- support geometry;
- lower bounds;
- graph/semigroup dynamics;
- generalizations outside Tau's exact patented method.

Publishability is evaluated by mathematical novelty/prior art.

### Track B — Tau-licensed engineering

Focus:

- support-mask QE fast path;
- ocLTL support compiler;
- direct backend integration;
- differential benchmarks against Tau.

Treat patent use as governed by the Tau/IDNI relationship and executed license, not as an attempt to route around their claims.

This separation protects both collaboration and independent authorship.

## 8. Claim-chart trigger

Before any of the following, stop and perform a real legal review / claim chart:

- commercial launch;
- paid licensing to third parties;
- filing our own patent close to Tau synthesis/QE;
- publishing implementation details that the Tau agreement may treat as confidential/improvements;
- deciding that an algorithm "does not infringe" based only on technical differences.

## 9. Current safest independent frontier

The strongest independence-favored direction currently is:

> **universal-algebraic structure of causal safety synthesis over Boolean powers, especially the controller-term hierarchy from primal through quasi-primal algebras, with exact counterexamples and orbit/groupoid algorithms.**

Why this is attractive:

- it arose by abstracting the mechanism, not copying Tau syntax;
- it has classical universal-algebra foundations but a distinct synthesis question;
- it produces both positive and negative theorems;
- it generalizes beyond Boolean algebra and beyond weak-omega-categorical type enumeration as the central presentation;
- it can still later inform a Tau implementation under license.

Novelty still requires full prior-art search.

## 10. Caveat

This file summarizes public patent records and research-management choices. Claim interpretation, validity, infringement, territorial effect, prosecution status, and license scope are legal questions and should be handled by qualified patent counsel when they become decision-relevant.

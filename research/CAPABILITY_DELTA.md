# Capability delta: what OrbitSynthesis should do independently

**Status:** research roadmap based on public Tau materials/code inspected through Aug 11 2026. "Not found publicly" is not a claim that IDNI has never considered a capability.

## 1. Public Tau baseline used for comparison

Public Tau materials describe:

- a declarative logical software specification language;
- satisfiability / program synthesis from specifications;
- decidable base logics and Boolean-algebra layers;
- temporal/recurrence machinery;
- BDD-based normalization;
- bitvector support in the public implementation;
- ocLTL synthesis modulo omega-categorical structures in Asor's 2026 paper.

At the pinned public `tau-lang` commit inspected in this program, targeted searches did not reveal named implementations of:

- primal / semi-primal / quasi-primal controller synthesis;
- internal-isomorphism-groupoid strategy constraints;
- controller-term-clone classification;
- Boolean-power finite-algebra synthesis as a first-class abstraction.

This identifies a public capability seam worth exploring. It does not prove exclusivity or novelty.

## 2. Capability A — synthesis parameterized by a finite algebra, not one fixed logic

Input:

- finite carrier M;
- operation tables / equations or explicit local safe relation;
- state/input/output arities.

Output:

- local safety winning set;
- controller table;
- optional Boolean-power realization.

The solver should work without Tau and without a special-purpose decision procedure for each finite algebra.

### Why this is distinct

The central object is the finite algebra / local game itself. Boolean power is a semantic lifting layer, not a Tau language feature.

## 3. Capability B — distinguish controller semantics

OrbitSynthesis should answer several different questions that ordinary synthesis tools often conflate:

1. Does **any** finite positional controller exist?
2. Does a Boolean-power **patchwork** controller exist?
3. Does a controller exist as terms of a Boolean representation substrate?
4. Does a controller exist as terms of the **original finite algebra signature**?

The answers can differ.

The Quackenbush quasi-primal counterexample already proves a strict separation between arbitrary/encoded controllers and original-signature term controllers.

This should become a first-class product/research capability, including explanations of why the stronger controller class fails.

## 4. Capability C — clone-aware synthesis

Classify the algebraic restrictions on implementable controller tables.

Current exact hierarchy:

- **primal:** all finite tables are term operations -> ordinary safety game;
- **semi-primal:** local generated-subalgebra restriction -> filtered safety game;
- **demi-semi-primal:** generated-subalgebra + global automorphism equivariance -> orbit/stabilizer game;
- **quasi-primal:** full internal-isomorphism-groupoid constraints -> strategy-table CSP in general;
- **general finite algebra:** term-clone-constrained finite synthesis.

A solver that exposes this hierarchy is not merely a different implementation of type-based reactive synthesis.

## 5. Capability D — synthesis impossibility explanations from algebraic structure

Return structured failure certificates such as:

- no locally safe action;
- output leaves generated subalgebra;
- observation stabilizer has no fixed safe action;
- internal isomorphism couples two observations inconsistently;
- required term table lies outside the algebra's clone;
- support hit obligation becomes empty after graph mixing;
- fixed-point antichain reaches an adversarial structural lower bound.

This is useful even when another synthesis engine only returns unrealizable.

## 6. Capability E — atomless Boolean-power support synthesis

For equation+inequation clauses over an atomless Boolean skeleton:

- represent a state family as allowed local labels + a canonical prime-hit antichain;
- compute exact controllable predecessor without enumerating complete support types;
- construct maximal patchwork responses;
- switch between prime-hit / maximal-loser / minimal-winner representations when useful.

This is a standalone hypergraph game engine.

## 7. Capability F — adversarial structural complexity analyzer

Before solving, compute/estimate:

- local label count;
- support-code width;
- subalgebra lattice;
- automorphism orbits and stabilizers;
- internal-isomorphism groupoid;
- transition SCC periods / matrix-power transient;
- hit-antichain width;
- transformation-semigroup/orbit size;
- support extension circuit complexity.

Then predict which backend is likely to be effective.

This follows the research lesson that raw `|T_k|` is often the wrong complexity statistic.

## 8. Capability G — finite-algebra Boolean-power compiler

Encode an M-valued Boolean-power datum using

`ceil(log2 |M|)`

Boolean-skeleton bits plus validity constraints.

Compile:

- finite operations;
- relations;
- synthesized controller tables;

into Boolean circuits/terms.

Possible targets:

- our own BDD/AIG/SAT runtime;
- hardware/logic synthesis;
- a future Tau adapter under favorable license terms.

The core compiler should not depend on Tau.

## 9. Capability H — groupoid/orbit strategy solver

For quasi-primal and related finite algebras, treat internal isomorphisms as a finite groupoid acting partially on observations and outputs.

Research/implementation questions:

- orbit compression for partial symmetries;
- CSP decomposition by groupoid connected components;
- stabilizer constraints;
- treewidth of the coupling graph;
- minimal unsatisfiable symmetry cores;
- comparison with global-aut group quotient in demi-semi-primal cases.

This is one of the strongest independent research directions because it has no need to mention omega-categorical type enumeration at all.

## 10. Capability I — graph/semigroup diagnostics for deterministic specifications

For deterministic finite local dynamics:

- functional-graph transient/period analysis;
- union-digraph cyclic-class analysis under adversarial inputs;
- primitive-SCC unrealizability tests for persistent proper hit obligations;
- permutation/Landau lower-bound detection;
- transformation-semigroup generalization.

This can provide specialized fast algorithms and impossibility checks before generic synthesis.

## 11. Capability J — general Boolean-product / sheaf synthesis

Boolean powers use the same finite local algebra at every Stone point.

A broader independent frontier is to let local factors vary over clopen regions: Boolean products / sheaf-style finite local models.

Research question:

> Under what patchwork and finite-factor hypotheses does causal safety predecessor decompose into finitely many local games and glue back exactly?

This should be developed from Feferman-Vaught / Boolean-product / sheaf model theory, not from Tau syntax.

If successful, it would extend the current theory beyond constant-fiber Boolean powers and beyond a single finite local data domain.

## 12. Capability K — specification-language-agnostic synthesis kernel

The independent engine should accept an intermediate representation such as:

- finite local algebra;
- local transition relation/circuit;
- controller semantic class;
- Boolean-skeleton mode.

Front ends can later include:

- our own compact DSL;
- JSON/SMT-like IR;
- theorem-prover extraction;
- Tau adapter if licensed;
- other formal specification systems.

This avoids making the research hostage to any one language.

## 13. What NOT to make the independent thesis

Do not center the standalone project on:

- cloning Tau's syntax;
- cloning Tau's self-reference/NSO design;
- reproducing Tau's existing BA quantifier eliminator;
- reproducing the generic weakly-omega-categorical recurrence and calling a new data structure the invention;
- requiring Tau to parse or execute our specifications.

Those can be comparison/integration tasks, not the identity of OrbitSynthesis.

## 14. Evidence standard for "Tau does not currently do X"

Permitted phrasing:

> "We did not find X in the inspected public Tau research pages or pinned public repository."

Not permitted without direct evidence:

> "Tau cannot do X."

or

> "Ohad has never thought of X."

If the Tau team later says they have internal work in the area, update the capability map and prior-art ledger rather than defending an obsolete claim.

## 15. Top independent build target

The first standalone prototype should be:

> **a finite-algebra safety synthesizer with selectable controller semantics and explicit algebraic failure explanations.**

Minimum modes:

1. unrestricted finite positional;
2. semi-primal term mode;
3. demi-semi-primal orbit mode;
4. quasi-primal groupoid-CSP mode;
5. Boolean-power patchwork realization.

This remains useful and research-worthy with zero Tau dependency.

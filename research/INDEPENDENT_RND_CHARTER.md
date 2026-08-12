# OrbitSynthesis independent R&D charter

## 1. Core rule

OrbitSynthesis is an **independent mathematical and software R&D program**.

It must remain coherent and buildable if:

- no Tau developer license is ever signed;
- Tau source code is unavailable;
- Tau Net never ships a feature we need;
- no Ohad/IDNI patented method is used as an implementation dependency.

A future favorable Tau/IDNI license may expand what integrations, optimizations, or patented Tau machinery we can lawfully use. It is an optional capability multiplier, not the foundation of the program.

## 2. Research is broader than implementation freedom

We may study, prove, falsify, compare, and academically analyze mathematics even where it overlaps Tau/Ohad research or patent claims.

However, three questions stay separate:

1. **Mathematical question:** is the theorem true, useful, and novel?
2. **Independent-product question:** can OrbitSynthesis implement its core capabilities without reproducing Tau's protected implementation path?
3. **License/FTO question:** if a product uses claim-adjacent methods, what does the actual executed license and applicable patent law permit?

Do not let patent caution suppress legitimate mathematical exploration. Do not let mathematical independence masquerade as a legal FTO conclusion.

## 3. Independence test for every major direction

A direction counts as core independent R&D only if it passes all of these tests.

### I1 — Tau deletion test

If all Tau-specific code, papers, APIs, and licensed components are removed, the theorem and standalone algorithm still make sense and can be implemented from public mathematics.

### I2 — problem-definition test

The problem is stated in ordinary mathematical language independent of Tau syntax.

Good examples:

- safety synthesis over Boolean powers of finite algebras;
- original-signature term-controller synthesis for semi-/quasi-primal algebras;
- internal-isomorphism-equivariant strategy tables;
- orbit/hypergraph lower bounds.

Bad example for the independent core:

- "make Tau's current quantifier eliminator 20% faster."

That can be licensed engineering, not the independent thesis.

### I3 — algorithmic-substrate test

The reference implementation can run on standalone finite objects such as:

- a finite carrier and operation tables;
- a local safe-transition relation;
- a Boolean skeleton / support representation;
- a finite automorphism/internal-isomorphism structure;
- SAT/CSP/BDD/ZDD/bitset backends chosen by us.

It does not require Tau's normalizer, parser, recurrence implementation, or proprietary service.

### I4 — novelty-source test

The direction arises from its own structural theorem, counterexample, or adjacent literature frontier, not merely from replacing one data structure in an Ohad/Tau method.

### I5 — capability-delta test

At least one of the following is true:

- it solves a mathematical problem outside Tau's publicly documented scope;
- it gives a controller notion Tau does not publicly expose;
- it handles a data domain/clone/symmetry class not found in the inspected Tau public materials;
- it proves a lower bound/impossibility criterion rather than reproducing Tau functionality;
- it yields a standalone solver with different inputs/outputs/semantics.

"Not found publicly" is the permitted claim until direct team communication establishes more. Never infer "they never thought of it" from a code search.

## 4. Current independent core

### A. Boolean-power causal safety lifting

For arbitrary finite local algebra M and Boolean power M[B], equation safety satisfies

`CPre_(M[B])(Lift(W)) = Lift(Pre_M(W))`.

This is a universal-algebra/game theorem, not a Tau syntax optimization.

Standalone implementation input:

- finite local safe relation or operation tables;
- finite state/input/output dimensions.

Standalone output:

- local winning set;
- finite positional strategy;
- optional Boolean-power patchwork realization.

### B. Controller-expressibility hierarchy

The program distinguishes controller semantics rather than assuming every finite table is an original-signature term.

Current hierarchy:

- primal -> ordinary finite safety game;
- semi-primal -> generated-subalgebra filtered safety game;
- demi-semi-primal -> automorphism-orbit game with stabilizer-fixed actions;
- quasi-primal -> internal-isomorphism-groupoid strategy CSP in general;
- arbitrary finite algebra -> term-clone constrained synthesis problem.

This is a standalone universal-algebraic synthesis program.

### C. Quasi-primal strict-separation counterexample

The Quackenbush three-element example proves that locally admissible safe actions can exist everywhere in a naive fixed point while **no nonempty original-signature term-winning invariant exists**.

This is not a Tau implementation result. It establishes a new algorithmic boundary to investigate.

### D. Atomless Boolean-power support/hypergraph games

For equation+inequation clauses over an atomless Boolean skeleton, winning regions are allowed support sets plus nontrivial hitting obligations and admit a closed hypergraph predecessor transform.

This generalizes beyond the two-element Boolean local algebra.

### E. Independent lower-bound program

Examples already derived:

- co-atom/group-testing lower bounds;
- Sperner-width fixed-point blowup;
- Landau-period deterministic blowup;
- primitive strongly-connected graph impossibility for proper persistent hit obligations.

These tell us where no universal compression theorem is possible.

### F. Finite-algebra-over-BA representation

Any finite local algebra M can be encoded over a Boolean skeleton using

`ceil(log2 |M|)`

BA bit coordinates plus a validity constraint. This gives a standalone representation theorem and optional compiler target.

It can later target Tau under a favorable license, but it can equally target our own BA/BDD/SAT engine.

## 5. Standalone software architecture

The independent implementation should be designed in layers.

### Layer 0 — finite algebra model

Input:

- finite carrier;
- operation tables and optional relations;
- optional subalgebra/automorphism/internal-isomorphism data.

No Tau dependency.

### Layer 1 — local game compiler

Compile equations/relations or an explicit transition relation into a finite local safety game.

### Layer 2 — controller-semantics solver

Backends:

- unrestricted patchwork/finite positional;
- semi-primal term mode;
- demi-semi-primal orbit mode;
- quasi-primal groupoid-CSP mode;
- generic term-clone constraint mode when available.

### Layer 3 — Boolean-power realization

Represent state sets/supports and, where required, construct clopen/Boolean-region patchwork witnesses.

### Layer 4 — symbolic representation portfolio

Independent choices:

- bitsets;
- ROBDD;
- ZDD;
- SAT/QBF/CSP;
- hypergraph antichains;
- group/orbit algorithms.

### Layer 5 — adapters

Optional adapters only:

- Tau adapter if/when license terms permit;
- other theorem provers/specification languages;
- standalone CLI/library.

The Tau adapter must never be required by Layers 0–4.

## 6. What we should build that is not merely Tau again

Priority capability targets:

### C1 — finite-algebra safety synthesizer

A solver whose input is an arbitrary finite algebra / local transition system and whose output can distinguish:

- arbitrary positional realizability;
- original-signature term realizability;
- reason for separation when they differ.

### C2 — clone-aware controller compiler

Given a finite algebra, compute or accept a finite description of its term-clone constraints and synthesize a controller table satisfying them.

For quasi-primal algebras this means internal-isomorphism-groupoid constraints.

### C3 — symmetry-aware term-synthesis diagnostics

Produce counterexamples explaining why no term controller exists:

- generated-subalgebra obstruction;
- stabilizer obstruction;
- nonextendable internal-isomorphism obstruction;
- unsafe orbit coupling.

### C4 — Boolean-power patchwork synthesizer

When original-signature terms are too weak, synthesize a correct patchwork strategy over the Boolean skeleton and expose the exact extra expressive resource used.

### C5 — algebra-class discovery

Automatically classify/test finite algebras for properties relevant to synthesis:

- primal;
- semi-primal;
- quasi-primal;
- demi-semi-primal;
- automorphism group;
- subalgebra lattice;
- internal-isomorphism groupoid.

### C6 — structural complexity radar

Measure the actual predictors found by the mathematics:

- local carrier size;
- generated-subalgebra profile;
- automorphism orbit counts;
- stabilizer sizes;
- internal-groupoid coupling graph/treewidth;
- support hit-antichain width;
- transition period/SCC cyclicity;
- support extension circuit size.

This is substantially different from reporting only a complete-type count.

## 7. Public Tau capability comparison discipline

Tau's current public materials describe an expressive decidable declarative specification language able to synthesize programs, with Boolean-algebra and bitvector machinery and BDD-based normalization in the public implementation.

At the pinned public commit inspected during this program, searches did not reveal explicit quasi-primal/semi-primal controller synthesis, internal-isomorphism groupoid strategy constraints, or the finite-algebra Boolean-power synthesis hierarchy above.

This is enough to justify exploration of a **publicly unoccupied capability seam**.

It is not enough to claim:

- Tau cannot implement it;
- Ohad/IDNI never considered it;
- it is legally outside every patent claim;
- it is academically novel.

Those are separate evidentiary questions.

## 8. Role of a future Tau developer license

If a license is offered, do not reshape the independent core before reading it.

First analyze:

- exact licensed software/IP;
- patent-family and continuation coverage;
- field-of-use limits;
- commercial/noncommercial rights;
- redistribution/sublicensing;
- source-modification rights;
- publication rights;
- confidentiality;
- improvement ownership and license-back;
- patent grants / defensive termination;
- post-termination rights.

Then create a **license overlay**:

`independent core + newly permitted Tau integrations`.

Do not let the license silently convert independent work into an "improvement" owned by or exclusively licensed to another party without understanding that clause.

## 9. Research direction selection rule

Prefer directions in this order:

1. theorem/counterexample that exists independently of Tau;
2. standalone algorithm arising from that theorem;
3. independent implementation and benchmark;
4. comparison against Tau as one external baseline;
5. optional Tau integration if a favorable license permits it.

Do not reverse the order and begin from "what Tau function can we tweak?"

## 10. Success criterion

A successful OrbitSynthesis program should be able to say:

> We discovered a mathematical theory and standalone synthesis machinery that does something independently useful. Tau is one possible integration target, not the reason the work exists.

If we cannot say that about a direction, it belongs in the Tau-collaboration/engineering track rather than the independent core.

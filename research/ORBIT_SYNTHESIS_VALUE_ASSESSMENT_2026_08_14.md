# OrbitSynthesis value assessment — 2026-08-14

**Purpose:** distinguish theorem-level contributions, publication candidates,
software assets, and remaining speculation. This is not a novelty opinion,
peer review, patent/FTO analysis, or commercial valuation.

## Executive assessment

OrbitSynthesis has progressed beyond an exploratory notebook collection. It now
contains a coherent research thesis and a plausible proof-carrying synthesis
system:

```text
finite algebra + safety specification
        -> internal-symmetry constraints
        -> exact winning-domain geometry
        -> weighted controller synthesis
        -> external solver portfolio
        -> original-signature controller DAG
        -> independently replayable certificates.
```

The strongest potential contribution is not the fixed-Q circuit constant. It
is the connection between internal partial symmetries of a finite algebra and
the global geometry of winning regions controlled by one shared term
operation.

## 1. Breakthrough candidate: exact greatest-region boundary

### Candidate theorem

For finite quasi-primal algebras, universal existence of a greatest
shared-term winning region is equivalent to the internal-isomorphism extension
property, hence to demi-semi-primality.

The project has:

- the positive orbitwise patching theorem when every internal isomorphism
  extends globally;
- a generic construction from a nonextendable internal isomorphism;
- two separately winning domains with no common winning superset;
- a strengthening in which the safety relation is defined by one
  original-signature equation;
- exhaustive three-element calibrations and independent reconstruction.

### Why it matters

Ordinary finite safety games have a greatest winning region because positional
choices patch state by state. A shared term controller is one globally coupled
operation table. Internal partial symmetries can prevent those local choices
from being patched.

The result would identify an algebraic property—not state-space size, memory,
or temporal logic—as the exact boundary for a fundamental game-theoretic
lattice property.

### Current confidence

```text
mathematical coherence: high
computational calibration: strong
formal proof status: partial/source-level, not end-to-end Lean
external referee status: absent
publication novelty: unknown
```

This is the best pure-mathematics paper candidate and the result most plausibly
deserving the word “breakthrough” after external review.

## 2. Strong algorithmic result: list-constrained generated subpowers

### Problem

For a fixed finite algebra `A`, generators `G subseteq A^n`, and arbitrary
coordinate lists `L_i subseteq A`, decide whether

```text
Sg_(A^n)(G) cap (L_1 x ... x L_n) != empty.
```

### OrbitSynthesis result for quasi-primal algebras

Transpose the generator matrix into evaluation rows. Connected components
under the internal-isomorphism groupoid can be solved independently: choosing
one value at a representative transports every value in the component.
Feasibility is exactly the existence of one representative value satisfying
all transported coordinate lists in every component.

### Why it matters

This is a precise, reusable algorithmic theorem adjacent to Subpower
Membership and Subpower Intersection. It yields:

- a polynomial-time algorithm for every fixed finite quasi-primal algebra;
- explicit witnesses;
- minimal component obstruction certificates;
- a natural implementation inside the controller synthesizer.

### Publication role

This can support the structural paper or form a separate algebra/algorithms
paper if the prior-art boundary remains clean and the complexity statement is
formalized carefully.

## 3. Strong reactive result: exact antichain and hardness geometry

For the fixed Quackenbush algebra `Q`, the project has an exact family with

```text
2^(2^(k-1)-2)
```

incomparable maximal term-winning domains at state arity `k`, plus an
orientation-vector representation and an NP-complete required-initial-state
problem under explicit relation encoding.

### Why it matters

This proves that the absence of a greatest region is not a small pathological
failure. The maximal-domain output itself can be doubly exponential in the
state arity parameter, even though one optimal domain may have a compact
symbolic description.

This result justifies:

- weighted optimization rather than full maximal-domain enumeration;
- MaxSAT and branch-and-bound backends;
- obstruction learning;
- compact orientation-aware representations.

It is likely the clearest bridge between the structural theorem and practical
software.

## 4. Supporting mathematical result: fixed-Q term complexity

The fixed-Q compiler work supplies:

- exact conservative term-operation enumeration;
- a local router control vector with leading size constant `4/3` in the scoped
  scalar-output model;
- parameter-free original-signature compilation;
- shared-DAG Shannon-order size;
- leading-one depth;
- an asymptotic global upper constant `3/log_2 3`.

### Assessment

This is a substantial specialized circuit-complexity paper candidate. It also
proves that a semantically synthesized strategy can be materialized efficiently
in the original algebraic signature.

It should now be consolidated and externally reviewed rather than subjected to
further small constant reductions. Its best role in the overall program is the
verified compiler back end.

## 5. New proof-carrying optimization capability

The software can now separate three claims:

```text
1. a backend found a Boolean assignment;
2. the assignment decodes to a valid domain and complete controller;
3. the claimed optimum or infeasibility is independently justified.
```

Available authority mechanisms include:

- closed-form structural theorems;
- bounded exhaustive authorities;
- state-search optimality/infeasibility proof trees;
- cross-backend agreement;
- future proof-producing MaxSAT traces.

This is practically important because optimization engines are treated as
untrusted search oracles. The deployed controller and its optimality claim can
be checked separately from the solver that produced them.

## 6. Credible paper portfolio

### Paper A — structural theorem

**Working title:**

*Internal Symmetries and Greatest Winning Regions for Shared-Term Safety Games*

Core contributions:

1. shared-term safety model;
2. demi-semi-primal positive theorem;
3. nonextendable-isomorphism converse;
4. one-equation witness;
5. exact three-element calibration;
6. implications for patchability and permissive controllers.

This is the highest-value mathematical paper.

### Paper B — algorithms and proof-carrying synthesis

**Working title:**

*Proof-Carrying Clone-Constrained Safety Synthesis over Finite Algebras*

Core contributions:

1. internal-groupoid component compiler;
2. list-constrained subpower algorithm;
3. exact domain CNF/WCNF reduction;
4. weighted optimization and hard state constraints;
5. obstruction and conflict certificates;
6. native, HiGHS, RC2, and command backends;
7. model, controller, and optimum proof replay;
8. structural benchmark families.

This is the strongest practical/formal-methods paper.

### Paper C — fixed algebra circuit complexity

**Working title:**

*Shannon Complexity and Leading-One Depth over a Parameter-Free
Three-Element Conservative Algebra*

Core contributions:

1. exact clone census;
2. signed-router program vector;
3. matched local `4/3` leading constant;
4. shared Boolean/rank libraries;
5. `3/log_2 3` asymptotic compiler;
6. source-level and Lean evidence.

This should be separated from the reactive paper unless a venue explicitly
welcomes the full cross-layer story.

### Later paper — infinite-structure response compression

The response-frontier / obstruction-width program remains promising but is
less mature. It reconnects OrbitSynthesis to omega-categorical and homogeneous
structures through maximal positive response signatures, conflict
hypergraphs, and specification-generated quotients.

## 7. Useful software potential

### Near-term research product

**OrbitSynthesis Controller Realizability Analyzer**

Input:

```text
finite algebra operation tables
finite safety relation or equation-defined relation
required / forbidden states
state and action utilities
controller semantics level
```

Output:

```text
ordinary, automorphism, and internal-groupoid feasibility
winning domain or exact obstruction
optimal controller table
original-signature shared DAG when supported
model/controller/optimality certificate bundle
```

This would be useful today as research software for:

- universal algebra and clone theory experiments;
- controller-synthesis counterexample generation;
- comparison of ordinary versus algebraically realizable strategies;
- benchmark generation for SAT/MaxSAT/formal-methods tools;
- verified policy and protocol-controller prototypes;
- Tau-oriented finite algebra experiments without making Tau a core dependency.

### Medium-term product wedge

The strongest practical wedge is not “general AGI synthesis.” It is:

> compile a finite declarative policy into one globally consistent,
> symmetry-respecting controller and emit a certificate explaining both the
> policy decisions and their optimality.

Candidate application domains include:

- access-control and authorization policies;
- protocol state machines;
- replicated systems with symmetric roles;
- governance/DAO rule controllers;
- configuration synthesis;
- safety envelopes for small embedded or cyber-physical controllers;
- formal regression testing for policy changes.

The algebraic controller language must match the application. The current
`Q={d,u}` compiler is a model organism, not yet a universal production target.

## 8. What is genuinely differentiated

OrbitSynthesis's defensible software/research differentiation is the combined
stack:

```text
shared controller semantics
+ internal partial-symmetry reasoning
+ exact maximal-domain geometry
+ original-signature compilation
+ explanation certificates
+ backend-independent optimality evidence.
```

SAT/MaxSAT solving alone is not differentiated. Finite-algebra enumeration
alone is not differentiated. The value lies in compiling algebraic controller
semantics into standard optimization while preserving a separately checkable
mathematical certificate.

## 9. Current limitations

The software is not yet a general-purpose synthesis product:

- input is predominantly explicit finite tables;
- quasi-primality or the applicable interpolation theorem is still a premise;
- only safety objectives are integrated end to end;
- large carriers make subalgebra/isomorphism enumeration expensive;
- the original-signature compiler is strongest for the fixed algebra `Q`;
- temporal and omega-categorical frontends are not yet connected;
- certificate bundles and stable CLI ergonomics remain incomplete;
- wall-clock backend benchmarks are not yet authoritative;
- GitHub Actions remain blocked by account billing/spending limits.

## 10. Recommended allocation

```text
45%  finish Paper A and external mathematical review
35%  stabilize the proof-carrying solver/CLI and benchmark suite
15%  Paper B algorithmic theorem and experiments
 5%  high-risk generalization or lower-bound work
```

The fixed-Q constant lane should remain frozen except for proof repair,
formalization, or a structural lower bound.

## 11. Breakthrough verdict

### Already strong enough to preserve and write up

- exact antichain geometry;
- fixed-Q required-initial hardness;
- quasi-primal list-constrained subpower algorithm;
- proof-carrying component-domain optimizer;
- fixed-Q compiler theorem package.

### Most plausible breakthrough, still requiring external validation

```text
greatest shared-term winning regions for all finite instances
iff
all internal isomorphisms extend globally.
```

If the converse proof survives independent universal-algebra and game-theory
review and the prior-art search remains clear, it is the central result of the
project.

### Not yet justified

- claiming publication novelty as settled;
- claiming a commercial product-market fit;
- claiming scalable superiority over mature synthesis or MaxSAT systems;
- claiming end-to-end formal verification.

The project has crossed from speculative exploration to a credible theorem
and research-software program. The next value comes from consolidation,
independent review, and a stable end-to-end user interface—not from opening
more disconnected theorem lanes.
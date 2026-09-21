# Frontier map — independent OrbitSynthesis program, 2026-08-11

Status vocabulary:

- **KNOWN** — supported by a cited source / standard theorem.
- **DERIVED** — proved in this repo from known ingredients; machine-check status stated separately.
- **CONJECTURE** — plausible but unproved.
- **OPEN-COMPARISON** — relationship not established.
- **REFUTED** — false; preserve the smallest/strongest falsifier.

## 1. Research identity

OrbitSynthesis is not a Tau clone and does not assume a Tau developer license.

Ohad Asor/Tau is one important source of mathematical problems, especially around Boolean algebra, omega-categorical synthesis, recurrence, and decidable specification languages. But the independent core must remain meaningful and implementable if Tau is removed entirely.

See:

- `research/INDEPENDENT_RND_CHARTER.md`
- `research/CAPABILITY_DELTA.md`
- `research/IP_BOUNDARY.md`
- `research/RESEARCH_PROTOCOL.md`

## 2. Starting mathematical stimulus: ocLTL / Tau

Asor's 2026 `ocLTL` paper reduces LTL+Past realizability/synthesis modulo an effectively presented countable omega-categorical structure to propositional LTL+Past via finite complete-type/orbit spaces.

Its main structure-dependent cost is the finite type abstraction; §5.2 shows a specification may need less than the full 3-type algebra, while the worst case can recover all distinctions.

This remains an important comparison baseline.

But the research program has now moved to mathematical objects that do not require ocLTL/Tau syntax:

- Boolean powers of finite algebras;
- controller term clones;
- support hypergraph games;
- internal-isomorphism groupoids;
- automorphism orbit games;
- transition graph/semigroup complexity.

## 3. First representation breakthrough: ABA supports

For atomless Boolean algebra, a complete k-type is exactly a nonempty support on the `2^k` Boolean Venn cells:

`|T_k|=2^(2^k)-1`.

This yielded:

- exact restriction/extension geometry;
- projection fibers as multipartite hypergraphs;
- exact atomic-predicate/group-testing lower bounds;
- minimum-width support type codes;
- compact extension relations.

These results were the bridge out of opaque complete-type enumeration.

## 4. Direct clause-safety carrier over atomless BA

A normalized equation+inequation clause has support semantics

`R(A;H) = {empty != S subseteq A : S hits every H in H}`.

Thus winning regions lie in the lattice of upward-closed nonempty support families inside an allowed set.

Controllable predecessor is closed on this carrier and has a finite hypergraph recurrence:

`A_(t+1)=P(A_t)`

with hit obligations propagated/injected by the same finite Boolean-cell predecessor maps.

Important negative result:

This does **not** give a universal complexity collapse. One inequation can force a maximum Sperner antichain and essentially double-exponential refinement scale.

So the contribution candidate is structural/parameterized, not worst-case asymptotic magic.

## 5. Equation-only safety: finite local game collapse

For Boolean algebra, equation-only safety collapses to the ordinary finite Boolean cube game.

The deeper representation change generalized this:

## 6. Boolean-power causal lifting — new central theorem line

Let M be any finite algebra and B any Boolean algebra. For the Boolean power

`A=M[B]`,

equation-defined causal safety satisfies

`CPre_A(Lift(W)) = Lift(Pre_M(W))`.

The mechanism is pointwise equation semantics plus clopen patchwork of locally selected finite responses.

Consequences:

- infinite Boolean-power safety is controlled by the finite local game on `M^k`;
- no omega-categorical complete-type enumeration is needed for equation-only safety;
- a positional patchwork strategy always exists when the finite local game is winning.

This theorem no longer depends on primality.

See `notes/FINITE_BOOLEAN_POWER_SAFETY.md`.

## 7. Original-signature controller expressibility — clone hierarchy

A finite local strategy table may or may not be expressible by terms of the original finite algebra.

This produced an exact hierarchy.

### Primal

Every finite function is a term operation.

Algorithm:

- ordinary finite safety game.

### Semi-primal

Term functions are exactly subalgebra-preserving functions.

Algorithm:

- local generated-subalgebra action filter;
- ordinary greatest fixed point.

See `SEMIPRIMAL_TERM_SAFETY.md`.

### Demi-semi-primal

Every internal isomorphism extends to a global automorphism.

Derived algorithm:

- automorphism-orbit safety game;
- generated-subalgebra filter;
- observation-stabilizer-fixed action filter.

See `DEMI_SEMIPRIMAL_TERM_SAFETY.md`.

### Quasi-primal

Term functions preserve the full internal-isomorphism structure.

Generic exact algorithm:

- finite global strategy-table CSP with internal-isomorphism equivariance constraints.

A Quackenbush three-element example proves the coupling is genuinely necessary: the naive locally admissible fixed point is nonempty while no nonempty original-signature term-winning invariant exists.

See:

- `QUASIPRIMAL_TERM_SAFETY_CSP.md`
- `QUASIPRIMAL_COUPLING_COUNTEREXAMPLE.md`

### General finite algebra

Open frontier:

- constrain the strategy table by the algebra's term clone / invariant relations;
- seek tractable algebra classes and finite relational bases.

## 8. Atomless Boolean powers generalize the ABA hypergraph theory

For an atomless Boolean power M[B]:

- equation disagreement sets forbid local M-labels;
- inequations require supports to hit local disagreement sets;
- atomlessness permits finite local output refinements.

Therefore the allowed-set + hit-hypergraph safety recurrence extends beyond two-valued Boolean local labels for the term-definable local sets actually present.

For primal M, arbitrary local sets/relations are term-definable, giving the fullest form of the support geometry.

## 9. Tau-independent finite-algebra representation

Any finite M-valued Boolean-power datum can be represented using

`ceil(log2 |M|)`

Boolean-skeleton bits plus a validity equation. Finite operations and controller tables compile to Boolean circuits/terms.

This can target our own symbolic runtime; Tau is only an optional future adapter.

See `TAU_FINITE_BOOLEAN_POWER_ENCODING.md` despite the historical file name: the theorem itself is Tau-independent.

## 10. Structural lower bounds and easy/hard dynamics

The safety recurrence produced a hierarchy of calibrated examples.

### Hard

- maximum Sperner antichain -> near full support-lattice width;
- permutation of maximal order -> Landau-function-many obligations;
- quasi-primal nonextendable internal symmetry -> local action feasibility does not compose globally.

### Easy / decisive

- equation-only -> finite local safety game;
- deterministic map with small transient/period -> bounded temporal obligation horizon;
- primitive strongly-connected deterministic input graph + proper persistent hit -> eventual empty hit / unrealizability.

These examples calibrate proposed complexity theorems in the Tao sense: any claimed bound must explain both ends.

## 11. Public Tau comparison

Public Tau materials describe a declarative decidable specification/synthesis language with Boolean-algebra, BDD, temporal/recurrence, and bitvector machinery. Asor's ocLTL gives omega-categorical type-based reactive synthesis.

In targeted searches of the pinned public `tau-lang` commit, we did not find explicit named implementations of:

- primal/semi-primal/quasi-primal controller synthesis;
- internal-isomorphism groupoid strategy constraints;
- the clone-aware controller hierarchy above.

This is evidence of a public capability seam, not a claim about private IDNI research.

Tau source inspection also established that Tau already has sophisticated Boole/BDD block QE machinery, so "use BDDs" or "eliminate a BA block" is not our independent contribution.

## 12. Ranked independent frontier

### Tier 1 — strongest current program

**F1. Clone-aware finite-algebra safety synthesizer.**

Build and prove a standalone solver with selectable controller semantics:

- unrestricted finite positional;
- semi-primal original-term;
- demi-semi-primal orbit/stabilizer;
- quasi-primal internal-groupoid CSP;
- Boolean-power patchwork.

**F2. General finite-algebra term-clone synthesis.**

Find finite relational/dual descriptions of term clones that compile controller synthesis to tractable CSP/orbit problems. Determine algebraic tractability boundaries.

**F3. Boolean-power / Boolean-product lifting theory.**

Generalize from constant finite fiber M[B] to Boolean products/sheaf-like varying finite local factors. Seek the exact patchwork hypotheses under which causal predecessor decomposes and glues.

**F4. Atomless support-hypergraph synthesis.**

Implement the exact clause recurrence and identify structural classes where antichain growth is controlled. Use lower bounds to reject fake sufficient conditions early.

### Tier 2 — structural complexity

**F5. Groupoid/orbit complexity of controller tables.**

Study coupling graph/treewidth, orbit compression, stabilizer constraints, and minimal unsatisfiable symmetry cores.

**F6. Graph/semigroup dynamics.**

Extend deterministic transition period results to input-generated transformation semigroups and relate algebraic dynamics to hit-obligation growth.

**F7. Support-extension presentation complexity.**

Compare finite structures/theories by:

- local type-code width;
- extension branching;
- extension relation circuit/BDD complexity;
- orbit/groupoid structure.

Do not assume raw orbit count is the right parameter.

### Tier 3 — comparison/application tracks

**F8. ocLTL/Tau application.**

Ask which independent carriers/algorithms can improve or extend Tau under an appropriate license. This is an application target, not the core thesis.

**F9. Generic finite-data/omega-categorical comparison.**

Compare Boolean-power patchwork and clone-aware synthesis with ocLTL type abstraction and constraint-LTL omega-regular satisfiability/approximability.

**F10. Canonical synthesis residuals.**

Remain quarantined until a precise two-player residual notion earns its keep.

## 13. Next concrete independent build

Implement a standalone finite-algebra safety kernel with no Tau dependency.

Minimum data model:

- finite carrier;
- operation/relation tables or explicit safe relation;
- state/input/output dimensions;
- subalgebra lattice;
- automorphisms;
- internal isomorphisms.

Minimum solver modes:

1. unrestricted local finite game;
2. semi-primal filtered game;
3. demi-semi-primal orbit game;
4. quasi-primal strategy CSP;
5. Boolean-power patchwork realization.

The first engineering milestone is successful only if the entire test suite runs with no Tau checkout or license.

## 14. Research method

Every major theorem follows `RESEARCH_PROTOCOL.md`:

- representation first;
- Noether inner-ground explanation;
- Tao basic-example/exponent calibration;
- counterexample before proof;
- symmetry reduction;
- old + new prior-art search;
- exact computational falsification;
- formalization when tools permit;
- explicit kill conditions.

## 15. Tool truthfulness

Current session:

- GitHub: available and heavily used;
- public web/literature: available;
- Consensus: connector available but monthly search quota exhausted;
- Research Kernel / Morph / LEAP: not exposed in the current callable tool/plugin surface;
- Kurate: public web discovery can be used, but no dedicated connector is exposed;
- Lean/Julia/ESSO executables: not available in the current execution environment unless a later tool surface changes.

No result should be attributed to an unavailable tool.

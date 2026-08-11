# Paper 1 candidate: Structure-Preserving Reactive Synthesis over Atomless Boolean Algebras

**Status:** research outline, not a novelty claim. Every theorem below is labeled by current provenance.

## Working thesis

Reactive synthesis over atomless Boolean algebras can avoid explicit complete-type games by preserving the internal Venn-support geometry of finitely generated Boolean subalgebras.

For a substantial positive temporal fragment this yields:

- support-level symbolic quantification;
- a finite cell-game reduction;
- a canonical maximal system response;
- collapse of system existential choice;
- exact positive modal-mu-calculus model checking on an environment-only transition system;
- multiple structure-aware algorithms and matching lower bounds.

## 1. Background / known ingredients

### K1 — ABA quantifier elimination and minterm normal form

**Known / Asor + classical Boolean algebra.**

Use as background, not novelty.

### K2 — ocLTL finite-type reduction over omega-categorical structures

**Known / Asor 2026.**

Use as baseline whose M-dependent type enumeration we aim to avoid structurally.

### K3 — mixed equation/disequation cofactor QE recurrence

**Known / patent-sensitive.**

The existential recurrence is essentially present in IDNI's granted US patent claims and Asor's Boolean-algebra calculus. It must not be presented as our novel theorem.

Our contribution can use it as a primitive and show how it interacts with symbolic synthesis/fixed points.

## 2. Structural ABA type geometry

### T1 — support representation

Complete k-types correspond to nonempty supports on the `2^k` Boolean Venn cells:

`|T_k|=2^(2^k)-1`.

**Status:** derived baseline; likely standard consequence, not novelty by itself.

### T2 — exact extension geometry

A type with s active cells has

`(2^(2^r)-1)^s`

extensions after adding r BA variables.

**Status:** derived baseline; explanatory/combinatorial value.

### T3 — interpreted-constant partition rank

For finite constant set C with `rho(C)` nonzero regions in the generated finite subalgebra,

`|T_k(C)|=(2^(2^k)-1)^rho(C)`.

**Status:** derived parameterization; novelty to verify.

## 3. Structure-preserving support Booleanization

### T4 — minimum-width support coordinates

The `2^k` support bits are an information-theoretically minimum-width binary encoding of all ABA complete k-types.

**Status:** derived, straightforward once T1 known.

### T5 — local extension relation

Adding r variables obeys one local OR constraint per coarse cell.

Under the natural block order the exact ROBDD size is

`2^k(1+2^(r+1))`.

**Status:** derived candidate technical contribution; compare against prior BDD/QE encodings.

## 4. Exact ABA clause synthesis calculus

### T6 — clause-form closure under quantifier blocks

One equation plus finitely many disequation obligations remains in the same support-clause form under existential and universal ABA variable elimination.

**Status:** mathematical closure derived; existential algebra overlaps known/patented calculus. Novelty lies, if anywhere, in the closed alternating-block algorithm and its synthesis use, not the primitive cofactor identity.

### T7 — canonical support clause

A state property is represented by:

- forbidden support mask Z;
- inclusion-antichain H of must-hit masks.

Normalization is semantically canonical in the protected fragment.

**Status:** candidate new synthesis representation; finite antichain facts themselves classical.

## 5. Cell-game reduction

### T8 — complete-type game factors through Venn cells

For conjunctive Step/Safe clauses, the zero/equation part of the complete-type game is exactly an alternating safety game on the individual state/partial/full Venn cells.

**Status:** candidate central theorem.

This reduces the semantic state substrate from

`2^(rho(C)2^d)-1`

complete support types to

`rho(C)2^d`

cell coordinates before symbolic compression.

### T9 — source-circuit view

The cell relation is the ordinary Boolean truth function of the original Tau term on the cell-label bits; minterm expansion is unnecessary.

**Status:** candidate algorithmic observation/theorem.

## 6. Dominant maximal-response theorem

### T10 — greatest zero-feasible response type

For an observed partial support P, activate every Step-zero-allowed full cell whose next state remains in the permanent zero-safe arena.

This support is the greatest zero-feasible response.

### T11 — upward target extremality

For every upward target W,

`exists legal Q over P with next(Q) in W`

iff

`Max(P) is legal and next(Max(P)) in W`.

**Status:** candidate major new theorem.

### T12 — synthesis-to-model-checking collapse

For the upward positive fragment,

`CPre(W)=Box_max(W)`.

Hence system existential choice disappears and the same maximal response strategy works for every positive modal objective.

**Status:** candidate flagship theorem.

## 7. Positive modal mu-calculus

### T13 — upward-property antichain lattice

At fixed zero-safe arena A*, positive hit-antichains represent exactly all upward-closed nonempty support properties.

AND, OR, CPre, least fixed points, and greatest fixed points all remain in this lattice.

Abstract free-distributive-lattice facts are classical; the exact ABA CPre action is the candidate contribution.

### T14 — reachability and Buchi

Upward reachability and Buchi objectives can be solved exactly in the antichain calculus without complete-type enumeration.

**Status:** candidate theorem + strong bounded independent checks.

## 8. Constructive strategy

### T15 — effective witness realization

Use Asor's effective extension-witness assumption to realize the maximal response type concretely.

A deterministic dyadic-interval ABA reference model demonstrates constructive witness generation.

**Status:** synthesis construction built from known effective-presentation hypothesis + candidate maximal-response theorem.

## 9. Algorithms / easy subclasses

### A1 — zero safety attractor

Linear-time queue/counter algorithm on explicit cell incidence.

**Classical finite-game algorithm specialized to ABA.**

### A2 — full S_d coordinate symmetry

Histogram quotient sizes:

- state: `d+1`;
- partial: `binom(d+3,3)`;
- full: `binom(d+7,7)`.

**Candidate ABA-specific quotient theorem; generic symmetry reduction is classical.**

### A3 — affine/XOR-linear cell games

Affine targets are closed under CPre. Gaussian elimination computes predecessor; equation-only safety has at most d+1 strict nonempty affine decreases.

**Candidate substantial tractable-subclass theorem.**

### A4 — deterministic/permutation dynamics

Reduce obligation iteration to functional-graph / group-orbit computation.

**Classical dynamics specialized to the cell representation.**

## 10. Negative/lower-bound side

### L1 — OBDD blowup

Simple positive ABA disequation CNFs inherit known exponential OBDD lower bounds.

**Literature lower bound + exact ABA embedding.**

### L2 — monotone-network universality

A single Step equation can encode any bottom/top-preserving monotone cell predecessor given enough environment refinements.

**Candidate embedding theorem.**

### L3 — Sperner periodic bound

Obligation periods are bounded by middle-layer antichain size and the bound is tight at cell-width level.

**Classical monotone-network/Sperner fact + ABA embedding.**

### L4 — compact LFSR exponential family

O(d)-size affine/XOR specification can force `2^d-1` strict prime-obligation strengthenings.

**Candidate compact-source lower bound; bounded executable checks present.**

## 11. Representation duality

Positive property represented either by:

- prime hit obligations H; or
- minimal winning supports `Tr(H)`.

The two can differ exponentially in size.

Hypergraph blocker theory is classical; representation routing for ABA fixed points is candidate engineering/research contribution.

## 12. Validation requirements before submission

1. Full literature/novelty search for T8-T15 and affine/symmetry theorems.
2. Lean formalization of representation-independent extremal/adjoint lemmas.
3. Formal or independently checked ABA support-extension realization theorem.
4. Differential execution against pinned Tau for the protected QE/synthesis fragment.
5. Benchmarks against:
   - Tau current QE path;
   - explicit complete types;
   - generic binary type encoding;
   - support BDD;
   - clause antichain;
   - affine/symmetry fast paths.
6. Patent-claim mapping kept separate from theorem novelty.

## 13. Possible title alternatives

- *Reactive Synthesis without Type Enumeration over Atomless Boolean Algebras*
- *Structure-Preserving Symbolic Synthesis over Atomless Boolean Algebras*
- *From Complete Types to Cell Games: Reactive Synthesis over Atomless Boolean Algebras*

The third title best reflects the deepest conceptual reduction currently found.

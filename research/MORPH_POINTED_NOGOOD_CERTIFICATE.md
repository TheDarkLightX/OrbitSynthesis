# Morph minimum-sufficient-abstraction certificate: pointed seed rules and domain nogoods

**Certificate ID:** `orbit-synthesis/pointed-domain-nogoods/v1`  
**Date:** 2026-08-13  
**Skill provenance:** `TheDarkLightX/Morph`, `minimum-sufficient-abstraction`  
**Primary note:** `notes/POINTED_NOGOOD_DOMAIN_SEARCH.md`

## 1. Two-layer contract

This tranche separates an exact semantic quotient from a smaller rejection certificate.

### Layer A — fixed-core controller semantics

| Field | Value |
| --- | --- |
| Raw domain `X` | Complete transported controller tables for one closed parameter core `K`, together with one candidate state domain `W` |
| Declared query family `Q` | Fixed-domain feasibility, total strategy reconstruction, partial seed viability, forced-literal soundness, and inclusion-maximal feasible-domain enumeration |
| Abstraction `A` | For every pointed observation class `E` and representative seed `a`, the pair `Unsafe(E,a)` and the source-indexed successor obligations `Req(E,a)(p)` |
| Losslessness tier | `semantic_lossless` for the declared fixed-core queries |
| Decoder | Choose one validating seed in every pointed class and transport it uniquely to every observation |
| Claim domain | Finite quasi-primal algebra, closed definable-constant core, observation arity in the pointed-product theorem's scope |

A seed validates a complete domain exactly when

`W ∩ Unsafe(E,a) = empty`

and

`for every p in W, Req(E,a)(p) subseteq W`.

A domain is feasible exactly when every pointed class has at least one validating seed. Thus the rule family is not a relaxation: it is an executable normal form of the pointed product theorem.

### Layer B — one conflict cone

| Field | Value |
| --- | --- |
| Raw failure object | A partial assignment, every seed of one pointed class, and every reason each seed is killed |
| Retained decision | Whether all complete domains extending the partial assignment are infeasible because that class has no surviving seed |
| Abstraction | A class-tagged pair `N=(I,X)` of included and excluded state literals |
| Losslessness tier | `decision_lossless` for rejection of every domain covered by `N` |
| Verifier | Replay partial viability of every seed against `I` and `X` |
| Production minimality | Deterministic greedy irredundancy |
| Bounded stronger gate | Exact cardinality-minimum literal count on every learned Quackenbush certificate |

The certificate covers a domain `W` when

`I subseteq W` and `X ∩ W = empty`.

It is sound when every class seed is killed by either an included unsafe source or an included source whose required successor is excluded.

## 2. Sufficiency and reconstruction

For a pointed class `E`, a representative seed fixes all table values in that class by unique pointed transport. Compiling those transported values into unsafe-source and successor-requirement data preserves every declared fixed-domain query.

For a learned nogood, the verifier checks every seed independently. If every seed is killed, no covered completion can satisfy that class, hence no covered completion admits a global controller. The raw failure trace remains available behind the compact pair.

## 3. Minimality posture

### Exact semantic quotient

The pointed-class seed product is structurally minimal for the term-table query family: distinct classes carry independent seed choices, while positions inside one class are uniquely reconstructed from one seed.

### Conflict certificate

The production learner does **not** claim a unique global minimum certificate. It repeatedly deletes literals while preserving class conflict, yielding an irredundant pair. On the bounded benchmark, an exhaustive subset oracle independently computes a cardinality-minimum pair; every learned certificate has the same literal count.

This avoids a false promotion from bounded minimum evidence to a universal minimum-certificate theorem.

## 4. Operation descent

The retained operations descend as follows:

- extending a partial assignment becomes set or bitmask union;
- a seed remains viable by two tests: no included unsafe source and no excluded required successor;
- a learned nogood triggers by `I_N subseteq I` and `X_N subseteq X`;
- forced exclusion tests viability after adding one positive literal;
- forced inclusion intersects the requirement closures of all currently viable seeds;
- a complete strategy decodes by selecting one valid seed per class;
- dominance pruning compares the partial node's upper domain bound with known feasible domains.

The integer-mask implementation is a representation refinement only. It has the same rule semantics as the object implementation and is differentially checked against both the object solver and an independent raw-groupoid reference.

## 5. Rejected abstractions and minimized breakers

### Observation-local generated-subalgebra feasibility

Rejected by the parameter-free domain

`W={00,01,11}`.

Observations `000` and `111` are individually locally feasible, but they share one pointed class. Their pulled-back seed lists are `{01}` and `{10}`, whose intersection is empty. Dropping transport creates a false merge.

### Positive-only domain nogoods

Rejected. A state can be feasible or infeasible depending on which successor states are excluded. One benchmark certificate requires both a positive source literal and negative successor literals. Omitting the negative side either becomes unsound or loses the conflict.

### Raw object/set implementation as the optimized representation

Extensionally exact but rejected as a performance generation on the nine-state benchmark. Fewer search nodes did not compensate for repeated Python set/object work. The failed generation is retained in the ZAG archive.

### `parameter_budget` without definable closure

Rejected by the preceding parameter-closure certificate: raw sets of equal cardinality can expose different controller languages, while different raw sets can define the same closed core.

## 6. Hard-gate ledger

The committed ZAG packet records:

- exhaustive benchmark domain instances: `1,536`;
- constrained required/forbidden API comparisons: `270`;
- raw-parameter closure API comparisons: `6`;
- frontier/budget/minimum-solution API comparisons: `7`;
- deterministic-random domain instances: `24,576`;
- maximal-domain mismatches: `0`;
- pointwise feasibility mismatches: `0`;
- learned benchmark nogoods: `8`;
- covered-domain replay checks: `1,088`;
- unsound certificates: `0`;
- exact-minimum literal-count mismatches: `0`;
- normal/optimized semantic mismatch: `0`.

The exact semantic hash and raw timing samples are stored in
`runs/zag_nogood_domain_search/summary.json`.

## 7. Compression and cost ledger

On the three-core Quackenbush benchmark:

- exhaustive enumeration examines `1,536` complete domains;
- the bitset search visits `227` partial nodes in total;
- the object/set solver is exact but slower than exhaustive enumeration;
- the cached bitset solver is the ZAG performance winner on this environment.

On the structured 27-state test, exhaustive enumeration would contain
`2^27 = 134,217,728` complete domains per core. The bitset search visits `49`
nodes per core and returns one directly checked 24-state controller domain.
This scaling receipt is structured evidence, not an exhaustive 27-state proof.

## 8. Evidence and authority boundary

- General seed-product and nogood soundness arguments are written in the note.
- `formal/OrbitSynthesis/PointedProduct.lean` and
  `formal/OrbitSynthesis/DomainNogood.lean` contain no `sorry`, `admit`, or
  `axiom`, but remain `UNDER_TEST` until compiled by the pinned Lean project.
- The ZAG candidates remain `TESTED_ONLY`; no implementation is labeled
  `PROVED` from finite tests alone.
- The Research Kernel packet promotes only bounded claims to `SUPPORTED` and
  keeps generic reduction and search-completeness claims `UNDER_TEST`.
- Publication novelty is unknown; SAT/CSP nogood learning, Horn implications,
  and maximal-model enumeration are adjacent prior art.

## 9. Next abstraction frontier

The next target is cross-core reuse. If `K subseteq L`, every `K`-polynomial
controller is an `L`-polynomial controller. Therefore a semantic domain nogood
proved even for the stronger core `L` is sound for every weaker core `K`.
Turning that monotonicity into a replayable core-lattice certificate—without
pretending that the original `L` pointed-class witness literally exists in
`K`—is the next high-value Morph problem.

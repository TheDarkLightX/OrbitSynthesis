# Pointed-class nogoods and exact maximal-domain search

**Status:** DERIVED exact fixed-core reduction and search algorithm; exhaustive/differential validation complete on the three-element Quackenbush benchmark and deterministic random games; 27-state structured scale test complete; abstract Lean sources added without `sorry`, but the pinned Lean toolchain was unavailable locally and GitHub Actions remains billing-blocked. Publication novelty unverified.

## 1. Problem remaining after the two minimum abstractions

Earlier tranches removed two static redundancies:

1. raw named parameters were quotiented by their definable-constant closure `K`;
2. raw term tables were quotiented to one seed per `K`-pointed generated-subalgebra class.

For a **fixed** candidate state domain `W`, this gives an exact and inexpensive seed-intersection test. The remaining cost came from searching the domain lattice itself. Exhaustive enumeration still visited all

`2^|States|`

candidate domains.

This note compiles every pointed seed to a Boolean obligation on state membership, derives exact two-sided conflict certificates, and uses them in a branch-and-bound enumerator for inclusion-maximal controllable domains.

## 2. Seed-rule compilation

Fix:

- a finite quasi-primal algebra `Q`;
- a closed parameter core `K`;
- a finite safety game whose outputs are next states;
- one `K`-pointed observation class `E`;
- one representative vector seed `a` for `E`.

For every observation `z` in `E`, unique pointed transport reconstructs the output

`y_a(z) = theta_z(a)`.

Let `source(z)` be the current state component of `z`.

Compile the seed into:

`Unsafe_(E,a) = {p : some z in E has source(z)=p and y_a(z) is unsafe at z}`

and

`Req_(E,a)(p)
 = {y_a(z) : z in E, source(z)=p, and y_a(z) is safe at z}`.

A state domain `W` validates this seed exactly when

1. `W intersection Unsafe_(E,a) = empty`;
2. for every `p in W`, `Req_(E,a)(p) subseteq W`.

The second clause is the invariant-successor condition. Multiple environment inputs for the same source state contribute multiple required outputs.

### Exact fixed-core formula

The class `E` is feasible on `W` iff at least one of its seeds validates `W`:

`ClassFeasible_E(W)
 = OR_a [W avoids Unsafe_(E,a) AND forall p in W, Req_(E,a)(p) subseteq W]`.

The whole domain is controllable iff every pointed class is feasible:

`Feasible_K(W) = AND_E ClassFeasible_E(W)`.

This is an exact disjunction of Horn-shaped seed rules. It is not a relaxation.

## 3. Partial assignments and two-sided nogoods

A search node carries two disjoint state sets:

- `I`: states forced into every completion;
- `X`: states forced out of every completion.

A seed remains partially viable exactly when

- `I intersection Unsafe_(E,a) = empty`;
- for every `p in I`, `Req_(E,a)(p) intersection X = empty`.

If one class has no partially viable seed, every complete domain satisfying

`I subseteq W` and `X intersection W = empty`

is infeasible.

The pair

`N=(I,X)`

is therefore a replayable **two-sided domain nogood**.

### Why negative literals are necessary

The obstruction cannot in general be represented only by a forbidden included-state set. In the parameter-free Quackenbush benchmark, one learned certificate is

- include `00`;
- exclude both `01` and `10`.

The source state `00` is not intrinsically losing. It becomes impossible only when every transported successor capable of repairing its pointed class is excluded. Including either `01` or `10` breaks the conflict.

Thus the correct conflict object records both active sources and missing required successors.

## 4. Sound propagation

Let `V_E(I,X)` be the currently viable seeds of class `E`.

### Forced exclusion

For an undecided state `p`, if no seed in `V_E(I,X)` remains viable after adding `p` to `I`, then every feasible completion excludes `p`.

Adding domain states cannot resurrect a seed already killed by `I` or `X`, so this test is exact.

### Forced inclusion

For each viable seed, collect the outputs required by the current included states:

`R_a(I)=union_(p in I) Req_(E,a)(p)`.

Every state in

`intersection_(a in V_E(I,X)) R_a(I)`

is required by every possible seed choice and can be forced into `I`.

### Dominance pruning

At a partial assignment `(I,X)`, every completion lies below the upper bound

`U = States \ X`.

If an already discovered feasible domain contains `U`, every completion of the node is dominated and the branch can be discarded.

## 5. Exact maximal-domain enumerator

The search is:

1. propagate forced inclusions and exclusions to a fixed point;
2. reject a node when a learned nogood is triggered or a pointed class has no viable seed;
3. prune when the node's upper bound is contained in an existing maximal solution;
4. otherwise choose a high-impact undecided state and branch `include` first, then `exclude`;
5. at a complete assignment, reconstruct one total controller by selecting a validating seed in every class;
6. retain only inclusion-maximal domains.

The algorithm is complete because every propagation step is logically forced, both branches are explored for every remaining state, and dominance pruning removes only completions already contained in a known feasible domain.

Worst-case complexity remains exponential—the family of maximal feasible domains can itself be exponential—but the search is output-sensitive and explanation-producing.

## 6. Morph abstraction contract

The task-relative raw failure object is:

- the complete partial assignment;
- all pointed classes;
- every seed and transported output check.

The retained query is:

> Are all completions of this partial domain infeasible because one pointed class has no possible seed?

The abstraction is an irredundant pair `(I,X)` for one class.

- **Sound decoder:** replay seed viability under the two literal sets; every covered completion kills all class seeds.
- **No false success:** every learned certificate was checked against all 512 complete benchmark domains.
- **Irredundancy:** deleting any retained literal makes at least one seed partially viable.
- **Exact bounded minimality:** every learned benchmark certificate has the same literal count as an exhaustive cardinality-minimum certificate.
- **Operation descent:** extension of a partial assignment, nogood triggering, forced literals, and domain dominance all operate directly on the abstract literal pair.

This is not claimed to be a globally unique minimum certificate. The production learner computes a deterministic greedy-irredundant certificate; exhaustive minimum certificates are used as a bounded Morph gate.

## 7. Implementations and ZAG generations

`src/orbitsynthesis/domain_search.py` is the public facade.  The exact semantics are split across `domain_search_types.py`, `domain_search_rules.py`, and `domain_search_object.py`; `domain_search_bitset.py` is the bit-parallel refinement, while `domain_api.py` keeps optimization state outside the stable pointed reference kernel.

### C0 — exhaustive compiled pointed reference

Enumerates all `2^n` state domains and calls the compiled pointed seed solver.

**Correctness label:** `TESTED_ONLY`.

### C1 — object/set nogood branch-and-bound

Uses Python sets and explicit rule objects.

It visits fewer search nodes and emits exact certificates, but on the nine-state benchmark its object/set overhead makes it slower than exhaustive enumeration.

**Correctness label:** `TESTED_ONLY`.

**ZAG admission:** rejected performance generation, preserved rather than rewritten as a success.

### C2 — cached bitset nogood branch-and-bound

Compiles state sets, unsafe sets, successor requirements, partial assignments, and nogoods to arbitrary-width Python integers. For small/medium state spaces it also precomputes each seed's requirement union for every included-state mask.

The search compiler is cached inside `CompiledParameterizedKernel`, because its algebraic obligations do not change across initial-set or frontier queries.

**Correctness label:** `TESTED_ONLY` until the implementation-equivalence theorem is Lean-checked.

**ZAG admission:** current performance frontier winner.

## 8. Exact validation

`experiments/quasiprimal_nogood_domain_search.py` checks:

- all `3 * 512 = 1,536` core/domain benchmark instances;
- exact equality of exhaustive, object-nogood, and bitset-nogood maximal-domain sets;
- total reconstructed strategy safety/invariance;
- all `24,576` core/domain instances from 16 deterministic random games;
- `270` constrained required/forbidden-state API comparisons;
- `6` raw-parameter/definable-core API comparisons;
- `7` frontier, budget-frontier, and minimum-parameter API comparisons;
- zero feasibility, maximal-domain, or API mismatches;
- eight learned benchmark nogoods;
- all 1,088 covered-domain replay checks, with zero unsound certificates;
- exact cardinality-minimum literal count for every learned benchmark nogood;
- byte-identical normal and optimized semantic receipts.

The deterministic semantic hash is

`5ce7108b4d67003e80d374bd8a2f758dff3751fb9fe682afff69751d1203d32f`.

## 9. Search and performance results

Across the three benchmark cores, exhaustive enumeration considers 1,536 complete domains. The bitset search visits:

- parameter-free core: 193 nodes;
- core `{0,1}`: 17 nodes;
- full core: 17 nodes.

Total: 227 search nodes, with the same maximal domains.

Over 30 precompiled complete sweeps in the validation environment:

- exhaustive compiled pointed median: `34,431,297.5 ns`;
- object/set nogood median: `109,352,726 ns`;
- cached bitset nogood median: `19,679,635 ns`;
- bitset speedup over exhaustive: approximately `1.75x`.

These are environment-specific measurements, not universal complexity claims.

## 10. Twenty-seven-state scale test

A lifted arity-three game has 27 states. Every state beginning with `(1,0)` is dead at environment input `2`, giving three forced exclusions. Exhaustive enumeration would require

`2^27 = 134,217,728`

candidate domains **per parameter core**.

For each of the three cores, the bitset solver:

- visits 49 nodes;
- learns three one-state dead-family certificates;
- returns one 24-state maximal domain;
- reconstructs and directly checks a total safe controller;
- completes in well under one second in the validation environment.

This is a structured scale test, not an exhaustive proof over all 27-state domains. Its returned strategy and every propagation certificate are independently checked, while generic completeness rests on the theorem above and remains scheduled for Lean compilation.

## 11. Lean tranche

Two abstract formalization files were added:

- `formal/OrbitSynthesis/PointedProduct.lean`:
  - representative seed recovery;
  - injectivity of table decoding;
  - equivalence between seed assignments and coherent tables;
  - classwise list feasibility iff one global decoded table exists.
- `formal/OrbitSynthesis/DomainNogood.lean`:
  - seed validity and partial viability;
  - nogood coverage and seed killing;
  - nogood soundness;
  - forced-exclusion soundness;
  - forced-inclusion soundness.

Neither file contains `sorry`, `admit`, or `axiom`. They are not labeled `PROVED` until compiled by the pinned Lean project.

## 12. Research boundary and next steps

The fixed-core reduction is a synthesis-specific consequence of the pointed product theorem. Conflict learning and maximal-model enumeration are adjacent to SAT, CSP, Horn implication, and antichain search, so publication claims require careful prior-art comparison.

The next high-value steps are:

1. compile and repair the two Lean files, then formalize the bitset implementation refinement;
2. use learned domain nogoods across parameter cores, transporting or weakening them along the core lattice;
3. combine domain nogoods with the patchability fixed-core obstruction antichain;
4. add watched-seed/incremental viability data structures for larger games;
5. characterize when the seed-rule formula belongs to Horn, dual-Horn, or bounded-width classes;
6. run the search on broader quasi-primal families and compare output-sensitive complexity.

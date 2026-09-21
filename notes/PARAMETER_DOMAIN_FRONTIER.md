# Parameter-core × winning-domain frontiers for quasi-primal safety synthesis

**Status:** DERIVED algorithmic specialization of the parameter-closure and pointed generated-subalgebra theorems; exact reference/optimized equivalence checked on all 1,536 Quackenbush core-domain instances and 24,576 deterministic random instances; minimized false local abstraction preserved; Lean closure/obstruction layer written without `sorry` but not compiled in the current runtime; publication novelty unverified.

## 1. The next question after parameter closure

The previous tranche established two independent minimum abstractions:

1. a raw parameter set `C` should be replaced by its definable-constant core `K(C)`;
2. for a fixed core and observation arity, a raw quasi-primal strategy table should be replaced by one seed per pointed generated-subalgebra class.

The remaining reactive question is not one scalar “winning region.” It is a tradeoff:

> how much controller language must be exposed, and what invariant state domain becomes controllable with that language?

A larger parameter core can eliminate partial symmetries and enlarge the feasible domain. But a stronger language should not be used when a weaker core controls the same domain. The correct output is therefore an antichain of pairs

`(closed parameter core K, term-controllable invariant domain W)`.

## 2. Fixed-core exact kernel

Let `Q` be a finite quasi-primal algebra and let `K` be a closed definable-constant core. For an observation tuple `z`, write

`G_K(z)=Sg_Q(K union coordinates(z))`.

Two observations are equivalent when there is an isomorphism

`theta:G_K(z)->G_K(z')`

that fixes `K` pointwise and maps `z` coordinatewise to `z'`.

Because `K` together with `z` generates `G_K(z)`, such a pointed transport is unique whenever it exists.

For a candidate invariant domain `W`, define the allowed output list

`L_W(z)={v in W : Safe(state(z),input(z),v)} intersect G_K(z)^k`

on active observations. On inactive observations the only requirement is membership in `G_K(z)^k`, so the final table can be completed as a polynomial operation.

Choose a representative `r_E` for every pointed class `E`. Pull every list in the class back to the representative:

`A_E(W)=intersection_(z in E) theta_z^(-k)(L_W(z))`.

### Theorem-shaped criterion

A `K`-parameterized polynomial controller keeps `W` safe iff

`A_E(W) != empty`

for every active pointed class `E`.

One vector seed in each nonempty intersection reconstructs the whole total controller table by unique transport.

This is the fixed-core specialization of the previously proved pointed product theorem. The new implementation compiles the finite algebraic data once and reuses it across every candidate domain.

## 3. Compiled solver architecture

`src/orbitsynthesis/parameter_core.py` provides:

- `closure_with_parameters`;
- `parameter_core`;
- `parameter_core_catalog`, including exact generator rank and every minimum witness;
- `eligible_core_isomorphisms`;
- `pointed_classes` with unique transports;
- `parameterized_strategy_reference`;
- `parameterized_strategy_pointed`;
- `parameterized_strategy_for_allowed_parameters`;
- `maximal_domains_for_allowed_parameters`;
- `CompiledParameterizedKernel`;
- `maximal_parameterized_domains`;
- `parameter_domain_frontier`.

The compiled kernel freezes, once per core:

1. the core-fixing internal isomorphisms;
2. `G_K(z)` for every observation;
3. raw reference edges and connected components;
4. pointed classes and unique transports;
5. all representative seed vectors.

Domain search then changes only the row-wise safety/invariance lists.

## 4. ZAG candidate tournament

Following the ZAG contract, four algorithm candidates were kept distinct.

### C0 — raw groupoid reference

Uses every eligible internal-isomorphism edge and propagates a candidate output through the whole raw component.

**Label:** `TESTED_ONLY`.

It is independent of the pointed-class implementation and serves as the exact bounded reference.

### C1 — pointed quotient rebuilt for every domain

Uses the exact pointed-class abstraction, but reconstructs classes, transports, and seed domains for every candidate `W`.

**Label:** `TESTED_ONLY`; rejected as a performance generation.

It agrees extensionally with the raw reference on all 1,536 exact benchmark instances, but its repeated algebraic preprocessing makes it much slower. This negative result is preserved in the ZAG archive.

### C2 — compiled pointed-core seed solver

Uses one precompiled seed domain per pointed class and checks transported-list intersections.

**Label:** `TESTED_ONLY`.

No generic Lean proof of implementation equivalence exists yet, so ZAG does not permit the label `PROVED`.

### C3 — naive generated-subalgebra-local solver

Checks only whether each observation has some locally generated safe successor and ignores cross-observation transport.

**Label:** `FAILED`.

The minimized falsifier is the original parameter-free domain

`W={00,01,11}`.

At observations `000` and `111`, local checks accept output `01` on both sides, but pointed transport pulls the second list back to `{10}`. The true class intersection is

`{01} intersection {10}=empty`.

The exhaustive benchmark finds 32 false-positive core/domain instances for this naive candidate.

## 5. Exact Quackenbush frontier

Use

`Q=({0,1,2};d,u)`,

where `d` is the ternary discriminator and

`u(0)=1`, `u(1)=0`, `u(2)=1`.

There are three definable-constant cores:

| Core | Generator rank | Minimum raw witnesses |
| --- | ---: | --- |
| `empty` | 0 | `empty` |
| `{0,1}` | 1 | `{0}`, `{1}` |
| `Q` | 1 | `{2}` |

Across all `2^9=512` candidate domains, the exact feasible-domain counts are:

| Core | Feasible domains |
| --- | ---: |
| `empty` | 128 |
| `{0,1}` | 160 |
| `Q` | 253 |

The all-core maximal-domain set contains four points, but one is semantically dominated.

### Exact nondominated antichain

At rank zero, two incomparable seven-state domains remain:

`M_0 = Q^2 - {10,11}`,

`M_1 = Q^2 - {10,00}`.

At rank one, the core `{0,1}` controls the eight-state domain

`M_2 = Q^2 - {10}`.

The full core `Q` controls the same eight-state domain at the same generator rank, but is strictly stronger as a controller language. It is therefore dominated by `{0,1}` and removed from the semantic frontier.

Thus the exact joint frontier is

`{(empty, M_0), (empty, M_1), ({0,1}, M_2)}`.

This makes the cost of restoring patchability concrete: one named parameter enlarges the maximal controllable domain by exactly one state in this benchmark, and the smaller rank-one core is sufficient.

## 6. Differential and adversarial validation

`experiments/quasiprimal_parameter_domain_frontier.py` checks:

- all `3 * 512 = 1,536` exact core/domain instances;
- zero reference/rebuilt-pointed feasibility mismatches;
- zero reference/compiled-pointed feasibility mismatches;
- 16 deterministic random nine-state games at seed 1;
- `24,576` additional core/domain differential instances;
- zero random mismatches;
- the exact feasible-domain counts above;
- the exact three-point nondominated frontier;
- elimination of the full-core dominated point;
- the minimized false local abstraction;
- normal and optimized Python semantic hashes agree.

The deterministic semantic receipt is

`97f0a4d729bdd551e9efb7511ff5b5a5e08cd05f31dc364f706e0596051a6370`.

## 7. Performance result and preserved failed generation

The first pointed implementation rebuilt classes and transports for every candidate domain. It was mathematically smaller but empirically slower than the raw reference. That failed performance generation was preserved rather than rewritten as a success.

The compiled candidate fixes the actual cause: invariant algebraic structure is precomputed once per core.

Over 30 complete sweeps of all 1,536 benchmark instances:

- raw groupoid reference median: `46316529.0 ns`;
- rebuilt pointed quotient median (3 sweeps): `1411544392.0 ns`;
- compiled pointed-core median: `31911233.5 ns`;
- compiled-versus-reference median speedup: approximately `1.45x`;
- compiled-versus-reference elapsed-time reduction: approximately `31.1%`.

These are environment-specific smoke measurements, not asymptotic claims.

## 8. Morph certificate interpretation

The raw object has two independent nuisance layers:

1. parameter-set identity inside one definable-constant closure;
2. raw table positions inside one pointed generated-subalgebra class.

The composed minimum abstraction is therefore:

`raw parameters + raw table`

`-> closed definable-constant core K`

`-> one vector seed per K-pointed observation class .

The retained reactive query is fixed-domain feasibility. It factors through the abstraction by the transported-list intersections `A_E(W)`.

False merges are excluded by the reference/pointed equivalence and by the generic parameter-closure theorem. False splits are excluded by independent seed choice across pointed classes and by constant-function separation across distinct cores.

## 9. Research Kernel evidence state

A Research Kernel-compatible replay packet is generated under

`runs/research_kernel_parameter_domain_frontier/`.

The direct MCP transport was unavailable in this runtime, so the offline adapter follows the public Research Kernel SQLite, atom, edge, evidence, promotion, event-log, and report contracts.

Fail-closed status:

- exact bounded solver-equivalence claim: `SUPPORTED`;
- exact bounded three-point frontier: `SUPPORTED`;
- naive local exactness: `REFUTED`;
- generic pointed solver theorem: `UNDER_TEST`;
- generic closure/obstruction Lean theorem: `UNDER_TEST` until compiler validation;
- kernel API integration: `OPEN_PROBLEM`.

No finite experiment is promoted into an unrestricted theorem.

## 10. Lean formalization tranche

`formal/OrbitSynthesis/ParameterClosure.lean` formalizes the closure/obstruction layer:

1. closure extensivity, monotonicity, and idempotence;
2. for closed `F`,
   `S subseteq F iff cl(S) subseteq F`;
3. obstruction avoidance descends exactly to closure;
4. hitting complements is equivalent to closure avoiding the closed fixed cores;
5. a generic Morph full-abstraction theorem for any query interface that factors through closure and separates closed states.

The file contains no `sorry`, `admit`, or `axiom` and has eight theorem declarations. The current container lacks Lean, and GitHub Actions is blocked at account billing before a runner starts. Therefore this tranche is **not** labeled `PROVED` yet.

## 11. Next high-value steps

1. Decide whether the new public free-function API should also become convenience methods on `FiniteSafetyGame`; the exact `parameter_core`, raw `allowed_parameters`, `parameter_budget`, and joint-frontier semantics are now implemented.
2. Formalize the unique pointed-transport/product theorem and compiled solver equivalence in Lean.
3. Replace exhaustive domain enumeration with obstruction-guided branch-and-bound over changing class intersections.
4. Learn minimal domain nogoods from empty pointed-class intersections and combine them with the patchability obstruction hypergraph.
5. Compute parameter-core/domain frontiers on broader quasi-primal benchmark families and determine their parameterized complexity.
6. Search older discriminator-algebra and polynomial-clone terminology before publication novelty claims.

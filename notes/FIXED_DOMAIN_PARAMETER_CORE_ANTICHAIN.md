# Fixed-domain safety can require an antichain of minimum parameter cores

**Status:** generic table-to-safety reduction proved on paper and formalized in Lean source; exact three-element discriminator census complete; public API implementation added; Lean compiler replay pending.

## Exact reduction

For a finite algebra `A` and scalar operation `f : A^n -> A`, construct a safety game with state space `A`, environment input `A^(n-1)`, full candidate domain `W=A`, and exactly one safe output at each observation: the value of `f`.

A controller keeps the full domain safe exactly when its table equals `f`. Hence, for every closed parameter core `K`, full-domain controller feasibility is equivalent to membership of `f` in the `K`-polynomial language. The reduction preserves the whole feasible-core predicate, including inclusion-minimal cores, minimum generator rank, parameter witnesses, and failure of a least core.

## No-least-core witness

Use the pure three-element discriminator algebra `D=({0,1,2};d)`, where `d(x,y,z)=z` when `x=y` and `d(x,y,z)=x` otherwise. Define

`f(x,y)=2 if (x,y)=(2,2), else 0`.

The deterministic full-domain game for `f` has exactly two minimum parameter cores:

- `{0,1}`;
- `{0,2}`.

They are incomparable and both have rank two. Their intersection `{0}` is infeasible, so there is no least adequate controller language.

Concrete terms witness sufficiency:

- `d(x,d(x,y,1),0)` over `{0,1}`;
- `d(x,d(x,y,d(x,2,0)),0)` over `{0,2}`.

The core `{0}` fails because the permutation swapping `1` and `2` fixes `0` but does not preserve `f`. The core `{1,2}` fails subalgebra preservation because `f(1,1)=0` lies outside `{1,2}`.

## Exhaustive census

The oracle checks every one of the `3^9=19683` binary tables and all eight parameter cores.

Polynomial-operation counts for core sizes `0,1,2,3` are:

`2, 24, 3888, 19683`.

Minimum-budget counts are:

`2, 66, 9932, 9683`.

At the minimum budget:

- `18151` tables have one minimum core;
- `1488` tables have two minimum cores;
- `44` tables have three minimum cores.

Therefore `1532` binary targets have more than one minimum parameter core.

## Morph certificate

Returning only `minimum_parameter_budget` is not sufficient: it loses which languages work and cannot reconstruct a controller. The exact task-relative output is:

1. the antichain of minimum-rank closed cores;
2. every minimum raw generator witness for each core;
3. one total controller table per core;
4. the fixed domain and evidence binding.

The API also returns the inclusion-minimal feasible-core antichain and reports `least_core=None` unless one feasible core is below every other feasible core.

## Formal status

`formal/OrbitSynthesis/TableSafetyReduction.lean` proves equality between the original operation-membership predicate and the graph-game feasible-core predicate. The file has no `sorry`, `admit`, or `axiom`, but remains `UNDER_TEST` until the pinned Lean project compiles it.

## Next questions

1. Characterize which finite antichains occur as minimum controller-core sets.
2. Bound maximum minimum-core multiplicity by carrier size and closure-lattice structure.
3. Combine core antichains with learned domain nogoods in one product-lattice search.
4. Transfer parameterized operation-membership complexity through the exact graph-game reduction with explicit encodings.

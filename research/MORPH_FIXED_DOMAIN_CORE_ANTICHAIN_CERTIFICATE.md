# Morph certificate: fixed-domain minimum controller-core antichains

Certificate ID: `orbit-synthesis/fixed-domain-core-antichain/v1`

Losslessness tier: semantic losslessness for fixed-domain feasibility, minimum parameter cost, controller reconstruction, and least-core detection.

## Contract

- Raw object: raw named-parameter sets and feasible total controller tables for one fixed domain.
- Query family: feasibility, minimum raw parameter budget, adequate language identity, least-core existence, and controller reconstruction.
- Abstraction: closed definable-constant core plus one reconstructed controller; retain the nondominated core antichain.
- Cost: exact generator rank of each closed core.
- Decoder: a minimum raw generator witness and the stored total controller table.

## Gates

Distinct closed cores are not merged because they can expose different constant operations and different legal controller transformations. Raw parameter sets with the same definable-constant closure are not split. Each core carries exact rank and a total strategy. `least_core=None` unless one feasible core is contained in every other feasible core.

## Rejected weaker outputs

A scalar minimum budget is insufficient: it loses which controller languages work. Selecting one minimum core discards another incomparable valid language. Intersecting all minimum cores is unsound in the witness because `{0,1} ∩ {0,2} = {0}` and `{0}` is infeasible. Their union is feasible but overpowered and nonminimal.

## Bounded receipt

The pure-discriminator census checks all `19683` binary tables and all `8` cores. Exactly `18151` tables have one minimum core, `1488` have two, and `44` have three. The target witness has minimum cores `{0,1}` and `{0,2}`, no least core, and explicit terms over both languages.

## Scope

The graph-game reduction is generic and formalized in Lean source, but compiler replay is pending. The census is bounded to the pure three-element discriminator at binary arity. Publication novelty remains unverified.

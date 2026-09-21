# Frontier update — pointed seed nogoods and maximal-domain search, 2026-08-13

This update follows `PARAMETER_CLOSURE_UPDATE_2026_08_12.md` and the parameter-core/domain frontier tranche. It replaces full powerset scans with an exact, certificate-producing search while retaining exhaustive enumeration as an independent bounded oracle.

## F4-A1 — fixed-core feasibility is a conjunction of seed-rule disjunctions

**Status:** DERIVED from the pointed product theorem; bounded differential evidence complete; generic Lean refinement pending.

For every pointed observation class `E` and representative vector seed `a`, compile:

- `Unsafe(E,a)`: source states where the transported output violates safety;
- `Req(E,a)(p)`: successor states forced when source state `p` is active.

The seed is valid on `W` iff

`W ∩ Unsafe(E,a)=empty`

and

`for every p in W, Req(E,a)(p) subseteq W`.

A fixed-core controller exists iff every pointed class has at least one valid seed. The rule system is an exact normal form, not a relaxation.

## F4-A2 — empty class intersections yield replayable two-sided domain nogoods

**Status:** DERIVED sound certificate; generic Lean source written, compilation pending.

A partial search assignment consists of included states `I` and excluded states `X`. A seed is partially viable iff no included source is unsafe and no included source requires an excluded successor.

When one class has no partially viable seed, the pair

`N=(I,X)`

rejects every completion satisfying `I subseteq W` and `X ∩ W=empty`.

Negative literals are essential: some states become impossible only when all repairing successors have been excluded.

## F4-A3 — exact maximal-domain branch-and-bound

**Status:** TESTED_ONLY implementation; exhaustive equivalence complete on the bounded corpus.

The search combines:

1. forced-exclusion propagation;
2. common-required-successor propagation;
3. learned class-conflict nogoods;
4. include-first branching;
5. maximal-domain dominance pruning;
6. total strategy reconstruction at feasible leaves.

Worst-case complexity remains exponential, as the maximal-domain antichain can itself be exponential.

## F4-Z1 — ZAG tournament preserves the failed generation

| Candidate | Status | Outcome |
| --- | --- | --- |
| Exhaustive compiled pointed solver | `TESTED_ONLY` | Independent reference |
| Object/set nogood search | `TESTED_ONLY` | Exact, but rejected as a performance generation |
| Cached bitset nogood search | `TESTED_ONLY` | Current bounded performance winner |

On the final 30-sweep environment sample:

- exhaustive median: `34,431,297.5 ns`;
- object/set median: `109,352,726 ns`;
- bitset median: `19,679,635 ns`;
- bitset/exhaustive median speedup: approximately `1.75x`.

The object-level solver visits fewer nodes but loses to representation overhead. This negative result is retained.

## F4-V1 — exact bounded evidence

The committed campaign validates:

- `1,536` complete Quackenbush core/domain instances;
- `24,576` deterministic-random core/domain instances;
- `270` constrained required/forbidden-state API comparisons;
- `6` raw-parameter/closure API comparisons;
- `7` frontier/budget/minimum-solution API comparisons;
- zero feasibility, maximal-domain, or API mismatches;
- `8` learned benchmark nogoods;
- `1,088` covered-domain replays with zero unsound certificates;
- zero exact-minimum literal-count mismatches;
- normal/optimized semantic agreement.

Semantic receipt:

`5ce7108b4d67003e80d374bd8a2f758dff3751fb9fe682afff69751d1203d32f`.

## F4-V2 — structured 27-state scale receipt

**Status:** checked returned strategies and certificates; not an exhaustive 27-state proof.

For each parameter core, the bitset search visits `49` nodes, learns three dead-state certificates, and returns one checked 24-state maximal domain. The corresponding exhaustive domain lattice has `2^27=134,217,728` candidates per core.

## F4-L1 — formalization tranche

`PointedProduct.lean` formalizes seed recovery, injective decoding, coherent-table equivalence, and classwise list factorization.

`DomainNogood.lean` formalizes seed validity, partial viability, nogood soundness, and forced include/exclude rules.

The files contain no `sorry`, `admit`, or `axiom`, but remain **UNDER_TEST** until the pinned Lean build actually runs.

## F4-RK1 — Research Kernel posture

The replay packet marks only bounded claims as `SUPPORTED`:

- exact bounded solver equivalence;
- bounded nogood soundness/minimality;
- bounded API conformance;
- the structured 27-state returned-witness result.

Generic reduction and generic search completeness remain `UNDER_TEST`. The claim that structural compression is automatically faster is `REFUTED` by the preserved object-level performance generation.

## Ranked next actions

1. Formalize unique pointed transport against the finite-algebra implementation and compile both Lean files.
2. Prove the bitset compiler refines the abstract seed-rule semantics.
3. Reuse semantic domain nogoods from stronger parameter cores at weaker cores, using controller-language monotonicity rather than pretending the stronger pointed-class witness exists unchanged.
4. Combine domain nogoods with maximal closed patchability obstruction cores.
5. Add watched-seed and incremental requirement-union data structures.
6. Classify seed-rule families into Horn, dual-Horn, bounded-width, or genuinely general cases.
7. Run the search across broader quasi-primal benchmark families and review SAT/CSP/maximal-model prior art before novelty claims.

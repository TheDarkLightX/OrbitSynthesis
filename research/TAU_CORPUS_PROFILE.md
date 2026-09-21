# Tau demo corpus profile against OrbitSynthesis protected fragments

**Pinned Tau revision:** `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`

**Status:** source/profile audit, not a runtime benchmark. The purpose is to determine where the mathematical preconditions of the OrbitSynthesis fast paths actually match Tau's documented workloads.

## Legend

- **ABA-EXACT** — documented as countable atomless Boolean algebra and covered by the proven ABA cofactor/support calculus.
- **SHAPE-MATCH** — syntactic shape matches but the Boolean-algebra type requires a separate semantic proof.
- **OTHER-BA** — explicitly another Boolean algebra; ABA existential/splitting theorems must not be applied.
- **TEMPORAL-LAYER** — first-order cell/backend may apply below the temporal operator, but temporal compilation needs its own path.
- **OUT-OF-SCOPE** — current OrbitSynthesis theorem does not cover it.

## 1. `demo_1.1-basic_syntax_and_history.tau`

Tau's syntax tutorial states that an expression with no type information is assumed to be over a **countable atomless Boolean algebra**.

Representative untyped formulas:

- `X = 0`
- `X != 0`
- `X = 0 && Y = 0 || Z = 0`
- `all X ex Y X = 0 && Y = 0`
- stream equations/disequations such as `o1[t] = i1[t] || o2[t] != i2[t]`

### Coverage

- atomic untyped equations/disequations: **ABA-EXACT**;
- quantified conjunction `all X ex Y ...`: **ABA-EXACT**, source cofactor clause QE;
- formula-level disjunction/XOR/conditional: not a single-clause fast path; use positive-lattice/BDD/general Tau path according to shape;
- temporal streams: **TEMPORAL-LAYER**.

### Source

`IDNI/tau-lang/demos/demo_1.1-basic_syntax_and_history.tau`.

## 2. `demo_1.3-recurrence_relations.tau`

Definitions are expanded during normalization.

Examples:

- `h[n](x) := x ^ h[n-1](x)`
- `q[0](x) := x = 0`
- `q[n](x) := q[n-1](x) && x != 1`

### Coverage

After finite recurrence unfolding at a concrete offset:

- term recurrences become ordinary Boolean term DAGs, suitable for source-level cell/circuit handling;
- the `q[n]` example becomes a conjunction of equation/disequation atoms and therefore **ABA-EXACT** when untyped;
- recursive definitions not reduced to a finite acyclic term remain outside the current fixed formula analysis.

This suggests profiling **post-definition-expansion but pre-DNF**.

### Source

`IDNI/tau-lang/demos/demo_1.3-recurrence_relations.tau`.

## 3. `demo_1.4-normalization.tau` — primary QE benchmark

The demo explicitly states that `normalize` decides validity in the first-order theory of **countable atomless Boolean algebras** and that untyped variables are exactly variables of that theory.

Every quantified ABA example in this demo is in the protected alternating clause fragment.

### Formula A

`qelim all X (X = 0)`

**Coverage:** ABA-EXACT, direct universal cofactor rule.

### Formula B

`qelim ex X (X != 0)`

**Coverage:** ABA-EXACT, existential mixed-clause recurrence with zero term `z=0`.

### Formula C

`all X ex Y (X Y' = 0)` followed by `qelim`.

**Coverage:** ABA-EXACT, alternating clause QE.

### Formula D

`n all x ex y all v ex w x'y = 0 && v ^ w = 0`

**Coverage:** ABA-EXACT, four alternating quantifiers, conjunction of equations. The equation-only existential special case is classical/Asor; source-clause closure avoids formula-level branching.

### Formula E

`n all x ex y (x y = 0 && x' y != 0)`

**Coverage:** ABA-EXACT, mixed equation+disequation alternating clause. This is the most directly relevant regression/benchmark case for the new recurrence.

### Importance

This is not a synthetic workload invented by OrbitSynthesis: it is Tau's own annotated demonstration of its central normalization/QE procedure.

### Source

`IDNI/tau-lang/demos/demo_1.4-normalization.tau`.

## 4. `demo_2.1-solver.tau`

The solver demo contains many equation/disequation systems:

- `solve x = 0 && y = 0`
- `solve x != 0 && x' != 0`
- systems with Tau/sbf constants;
- LGRS equations.

### Coverage

The **shape** strongly overlaps the clause calculus, but this demo describes untyped solver variables as living in the Tau Boolean algebra by default.

Therefore:

- explicit `:sbf` systems: **OTHER-BA**;
- `:tau` / default solver systems: **SHAPE-MATCH**, pending a pinned theorem/implementation contract identifying the relevant atomless semantics;
- LGRS/reproductive solution construction is a different output problem from complete-type synthesis.

Do not infer eligibility only from syntax.

### Source

`IDNI/tau-lang/demos/demo_2.1-solver.tau`.

## 5. `demo_2.2-solver-min_max.tau`

This demo orders **concrete BA solutions** by inclusion and demonstrates that solvable systems need not have greatest/least concrete elements.

Example:

`x != 0 && x' != 0`.

### OrbitSynthesis relevance

This is a critical non-equivalence test:

- concrete element-level maximum can fail to exist;
- the complete support type can still have a greatest legal response code.

See `notes/ABA_TYPE_MAX_VS_ELEMENT_MAX.md`.

### Coverage

Not a replacement implementation for the dominant strategy. `solve --max` must not be used as the type-level maximal-response primitive.

### Source

`IDNI/tau-lang/demos/demo_2.2-solver-min_max.tau`.

## 6. `demo_2.3-solver-bitvectors.tau`

Explicit bitvector theory, solved via cvc5.

### Coverage

**OUT-OF-SCOPE / OTHER-BA.**

OrbitSynthesis ABA rules should never intercept this route.

## 7. `demo_3.1-interpreter_sbf.tau`

Streams are explicitly `:sbf`.

Representative specs:

- Fibonacci-style XOR recurrence;
- `o1[t] != 0 && o1[t] != 1`;
- equality with uninterpreted constants;
- source/file stream equations.

### Coverage

- Boolean/circuit syntax: potentially reusable by generic source-level symbolic backends;
- atomless support-splitting/existential recurrence: **OTHER-BA**, not licensed by the ABA theorem;
- temporal execution: **TEMPORAL-LAYER**.

This demo is an excellent negative-control corpus: a correct implementation gate should decline the ABA-specific fast path.

### Source

`IDNI/tau-lang/demos/demo_3.1-interpreter_sbf.tau`.

## 8. `demo_3.2-interpreter_tau.tau`

Streams carry Tau specifications (`:tau`).

Representative specs:

- fixed Tau-spec constant output;
- echo a Tau specification;
- complement a Tau-spec input;
- arbitrary nesting of specifications-as-values.

### Coverage

**SHAPE-MATCH / semantic contract unresolved.**

The Tau project is built around Boolean-algebra abstraction, and other project material relates its logic abstraction to countable atomless Boolean algebra, but this profile does not yet establish that every concrete `:tau` runtime operation can be treated as the exact ABA model required by the support witness theorem.

Until that relationship is pinned from the theory/implementation:

- do not enable ABA-specific witness synthesis solely because the type is `tau`;
- keep the existing Tau interpreter/solver path as oracle/fallback.

### Source

`IDNI/tau-lang/demos/demo_3.2-interpreter_tau.tau`.

## 9. Coverage conclusion

The strongest immediate integration target is **not the whole language**.

It is:

> homogeneous untyped/countable-ABA first-order blocks, especially a prenex quantifier prefix over one conjunction of equations/disequations.

This target:

- is mathematically exact;
- is explicitly exercised by Tau's central normalization demo;
- can reuse Tau's existing term cofactor/simplification machinery;
- has a safe fallback to the current generic QE path;
- avoids conflating ABA, sbf, bitvectors, and the special tau runtime algebra.

## 10. Benchmark corpus v1

Use the exact pinned demo formulas as named regressions:

- `D14-A-universal-zero`
- `D14-B-existential-nonzero`
- `D14-C-all-ex-equation`
- `D14-D-four-alternation-equations`
- `D14-E-all-ex-mixed-clause`

Then add generated families:

1. equation-only blocks;
2. fixed q=1,2,4 disequation count with growing quantifier alternation;
3. XOR-heavy terms;
4. high cofactor sharing;
5. intentionally adversarial term DAG growth;
6. same syntax under `:sbf` as a negative control where applicable.

Measure:

- semantic equivalence;
- normalized AST/DAG size;
- Boole split count;
- time;
- allocations/peak memory;
- whether fallback fired.

## 11. Required gate before implementation promotion

A source-level block may enter the ABA fast path only when all of the following hold:

1. BA type is verified to have the countable-atomless semantics required by existential support splitting;
2. body normalizes to one conjunction of equation/disequation atoms over that BA type;
3. no unresolved foreign theory/reference content is mixed into the block;
4. term cofactor construction stays below configured resource thresholds;
5. differential tests against the existing Tau path pass on the benchmark corpus.

# Morph minimum-sufficient-abstraction certificate: parameter closures

**Certificate ID:** `orbit-synthesis/quasiprimal-parameter-closure/v1`  
**Date:** 2026-08-12  
**Skill provenance:** `TheDarkLightX/Morph`, PR #10, `minimum-sufficient-abstraction`  
**Primary theorem:** `notes/QUASIPRIMAL_PARAMETER_CLOSURE_LATTICE.md`

## Contract

| Field | Value |
| --- | --- |
| Raw domain | Carrier parameter sets `C subseteq Q` |
| Declared query family | Membership of all positive-arity functions in `Pol_C(Q)`; sparse list interpolation; fixed-domain controller feasibility; pointed patchability goodness and obstruction survival |
| Candidate abstraction | `K(C)`, the elements whose constant unary operations are `C`-polynomials |
| Algebraic form | `K(C)=Sg_Q(K(empty) union C)`, allowing an empty bottom |
| Losslessness tier | Full abstraction for the declared polynomial-language query family |
| Decoder | Replace every named parameter by a constant polynomial over any generating set of the same closed core |
| Retained operations | Inclusion, union/join, generator-rank cost, fixed-core pointed transport, scalar/vector list pullback |
| Claim domain | Full-abstraction and patchability-closure theorems: arbitrary algebra (finite for obstruction enumeration); pointed product and fixed-`Q` complexity: finite quasi-primal algebra, arity `n>1` |

## Generic no-false-merge certificate

If `K(C)=K(D)`, every parameter named by `C` has a constant polynomial over `D`, and conversely. Parameter substitution translates every `C`-polynomial operation into a `D`-polynomial operation without changing its function.

Therefore

`K(C)=K(D) => Pol_C(Q)=Pol_D(Q)`.

**False-merge count on the theorem domain:** `0` by proof.

## Generic no-false-split certificate

If `K(C) != K(D)`, choose `a` in their symmetric difference. The constant unary operation `const_a` belongs to exactly one of the two polynomial clones.

Therefore

`Pol_C(Q)=Pol_D(Q) => K(C)=K(D)`.

**False-split count on the theorem domain:** `0` by proof.

## Operation-descent certificate

- Parameter inclusion descends to closed-core inclusion.
- Raw union descends to closure join: `K(C union D)=K(K(C) union K(D))`.
- Minimum raw parameter count descends to generator rank `rank(K)=min{|C|:K(C)=K}`.
- For finite quasi-primal `Q`, table reconstruction descends to one seed per `K`-pointed generated-subalgebra class.
- Sparse scalar/vector list constraints descend by pointed transport and intersection inside each class.
- Functional completeness descends to the top test `K=Q`.
- Pointed internal-isomorphism patchability descends because `C`-containing subalgebras and `C`-fixing isomorphisms are exactly those for `K(C)`.
- Every nonextendable partial isomorphism has a closed fixed core `F`; its survival descends to the test `K(C) subseteq F`, so the obstruction hypergraph descends to an antichain of maximal closed fixed cores with generator-rank costs.

**Operation-descent failure count on the theorem domain:** `0` by proof.

## Bounded falsification receipt

The oracle exhausts every binary table and every raw parameter set on two three-element quasi-primal algebras.

### Quackenbush algebra

`Q=({0,1,2}; discriminator,u)`, with `u(0)=1`, `u(1)=0`, `u(2)=1`.

| Metric | Result |
| --- | ---: |
| Raw parameter sets | 8 |
| Closed parameter cores | 3 |
| Binary tables per core scanned | 19683 |
| Parameter-free binary operations | 972 |
| `{0,1}`-core binary operations | 3888 |
| Full-core binary operations | 19683 |
| Tables requiring zero parameters | 972 |
| Tables requiring one parameter | 18711 |
| Bounded false merges | 0 |
| Bounded false splits | 0 |
| Raw-to-closure/closed-obstruction patchability mismatches | 0 |
| Nonextendable partial isomorphisms / maximal closed obstruction cores | `1 / {empty}` |

Key witnesses:

- `{0}` and `{1}` have different raw identities but the same core `{0,1}` and the same language;
- `{0}` and `{2}` have the same cardinality but different cores and operation counts (`3888` versus `19683`).

### Pure discriminator algebra

| Metric | Result |
| --- | ---: |
| Raw/closed parameter cores | 8 |
| Binary tables per core scanned | 19683 |
| Operation counts for core sizes `0,1,2,3` | `2,24,3888,19683` |
| Minimum-budget counts `0,1,2,3` | `2,66,9932,9683` |
| Tables with one minimum set | 18151 |
| Tables with two minimum sets | 1488 |
| Tables with three minimum sets | 44 |
| Bounded false merges | 0 |
| Bounded false splits | 0 |
| Raw-to-closure/closed-obstruction patchability mismatches | 0 |
| Nonextendable partial isomorphisms / maximal closed obstruction cores | `0 / none` |

No-least-core witness:

`f(x,y)=2` at `(2,2)` and `0` elsewhere has minimum cores `{0,1}` and `{0,2}`, while their intersection `{0}` is infeasible.

Commands:

```bash
python experiments/quasiprimal_parameter_closure.py
python -O experiments/quasiprimal_parameter_closure.py
```

Both modes produce byte-identical successful output. `compileall` also passes.

The Quackenbush corpus was then checked with Morph's committed validator under normal and optimized Python. The validation files were byte-identical and reported:

```text
status: PASS_EXACT_ON_BOUNDED_CORPUS
object_count: 8
query_count: 19683
operation_count: 3
abstract_state_count: 3
semantic_class_count: 3
raw_index_bits: 3
abstract_index_bits: 2
```

Reproducibility hashes:

```text
SHA256(corpus JSON)     1105da01dcda816cfaa75ff125bed180b8abd0c9eee7c37983b05da795dc7a32
SHA256(validation JSON) 7361282c1188db650f49df28d1a5719038e31299504dae058649750d47dab2b9
```

The corpus is generated on demand rather than committed as a derived 4.8 MB file:

```bash
python experiments/quasiprimal_parameter_closure.py \
  --emit-morph-corpus /tmp/quasiprimal_parameter_closure_corpus.json
```

## Rejected abstractions

### Raw parameter cardinality

Rejected by Quackenbush singletons: `{0}` reaches only the core `{0,1}`, while `{2}` reaches all of `Q`. Both cost one raw parameter but induce different controller languages.

### Raw parameter identity

Sound but nonminimal: Quackenbush `{0}` and `{1}` generate the same definable-constant core and exactly the same polynomial clone.

### Boolean `parameterized=True`

Rejected as too coarse. It merges all intermediate closed cores with the full core and can silently claim unrestricted-table expressivity.

### Output values occurring in the target table

Rejected: variables can supply unnamed values on guarded branches. The pure-discriminator no-least witness is representable from `{0,1}` even though its table outputs `2`.

### A unique least parameter core

Rejected by the same witness: two incomparable minimum cores exist and their intersection is infeasible.

## Scope and unknowns

- Publication novelty is `UNKNOWN`; the generic closure theorem is elementary and likely standard in polynomial-clone language.
- Lean formalization is pending.
- Explicit term/DAG minimization is `UNKNOWN`.
- Complexity for variable/input algebras and succinct table/list encodings is not claimed.
- Fixed-domain factorization does not solve global reactive domain selection.
- The closure-lattice obstruction form does not remove the cost of generating nonextendable partial isomorphisms.

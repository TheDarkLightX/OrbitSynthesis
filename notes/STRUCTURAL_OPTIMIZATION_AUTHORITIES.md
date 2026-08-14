# Structural optimality authorities for OrbitSynthesis

**Status:** implementation and benchmark note, 2026-08-14.

External SAT, MaxSAT, and MILP solvers are useful search engines.  A returned
model is a finite certificate that one domain/controller is feasible, but a
model alone does not certify that no better domain exists.  OrbitSynthesis now
keeps these two questions separate:

```text
certificate_verified   -- the returned domain and controller replay exactly
optimality_authority    -- why no strictly better domain exists
```

This note records two authorities used by the structural benchmark suite.

## 1. Exact antichain authority

For the fixed Quackenbush algebra

```text
Q=({0,1,2};d,u),
d(x,y,z)=z if x=y, else x,
u(0)=1, u(1)=0, u(2)=1,
```

the exact antichain construction at state arity `k>=3` divides the binary
states into complement pairs.

- Pair zero is the live/dead anchor.
- Pair one is neutral.
- The remaining

```text
n=2^(k-1)-2
```

pairs are independent orientation choices.

The dead state has no safe transition at one environment input.  Complementary
critical observations for an orientation pair are forced to complementary
anchor outputs.  Since the dead anchor cannot occur in a winning domain, a
winning domain contains at most one state from each orientation pair.

Every inclusion-maximal winning domain therefore consists of:

- every nonbinary state;
- the live anchor;
- both neutral states; and
- exactly one member of every orientation pair.

Consequently the exact number and size of maximal domains are

```text
maxima(k)=2^(2^(k-1)-2),
size(k)=3^k-2^(k-1)+1.
```

The benchmark instantiates:

| `k` | orientation pairs | maximal domains | domain size |
|---:|---:|---:|---:|
| 3 | 2 | 4 | 24 |
| 4 | 6 | 64 | 74 |

Give every state weight one and add bonus `2^(i+1)` to the first state of
orientation pair `i`.  All weights are positive, so every optimum is maximal.
The orientation bonuses make the preferred choice in every pair strict.  Thus
the unique optimum has scores

```text
k=3: 24+(2+4)=30,
k=4: 74+(2+4+8+16+32+64)=200.
```

This supplies a closed-form authority for external optimization.  The gate
still replays all 4 and 64 maximal domains through the compiled internal-
groupoid component model before accepting the theorem instance.

## 2. Principal one-equation authority

The generic non-demi-semi-primal converse over `Q` has:

```text
81 states,
243 observations,
227 internal-groupoid components,
17,174 candidate component rules,
17,255 eager CNF variables.
```

It contains two term-winning domains `W_L` and `W_R` but their union is not
term-winning.  For backend stress testing, all 81 state variables and all
component selectors remain in the formula, but states outside

```text
U=W_L union W_R
```

are fixed absent.

For this specialization `|U|=4`.  OrbitSynthesis can therefore exhaust all
`2^4=16` permitted domains while still asking HiGHS or RC2 to solve the full
17k-variable component formula.

Binary-place weights

```text
1,2,4,8
```

on the four permitted states assign every subset a different primary score.
The bounded authority finds:

```text
16 assignments checked,
8 term-winning domains,
unique optimum score 13,
forced full union infeasible.
```

This is a stronger validation pattern than checking only the solver's reported
objective.  The external model must reconstruct a compatible controller and
match the independently enumerated unique optimum.  The infeasible forced
union is likewise promoted only because the bounded authority checks the sole
permitted assignment directly.

## 3. Authority API

`src/orbitsynthesis/optimization_authority.py` provides:

```python
ObjectiveAuthority
closed_form_objective_authority(...)
bounded_domain_objective_authority(...)
certify_external_result(...)
```

An authority records:

- its name;
- deterministic state order;
- exact optimum score, or `None` for infeasibility;
- the complete accepted optimum-domain family;
- the number of assignments and feasible domains checked;
- evidence metadata; and
- a semantic SHA-256 excluding machine-dependent timing.

`certify_external_result` refuses promotion unless:

- an infeasibility authority agrees with an infeasible backend status; or
- an optimal backend result has a verified controller certificate, the exact
  authority score, and a domain in the authority optimum family.

The promoted result stores the authority hash in its metadata and replaces a
bare `backend_status` label with the precise authority name.

## 4. Benchmark separation

Semantic gates and timing benchmarks are deliberately separate.

The semantic gate checks:

- theorem-family construction;
- all closed-form antichain maxima;
- bounded principal enumeration;
- HiGHS and, when installed, RC2 agreement;
- normal versus optimized Python equality; and
- a no-import independent reconstruction.

The timing benchmark records wall-clock summaries and formula sizes but marks
the output `diagnostic_only`.  Timing never enters a semantic receipt.

## 5. Boundaries

The structural authority is only as strong as the underlying theorem or
bounded enumeration.  It does not turn arbitrary MaxSAT output into a proof.

This lane does not yet provide:

- proof traces for unrestricted large-instance MaxSAT optimality;
- a performance-superiority theorem;
- incremental lazy-MaxSAT benchmarks;
- BDD/MDD or knowledge-compilation comparisons;
- Lean formalization of the antichain or principal authority;
- external peer review; or
- a publication-novelty or legal conclusion.

# Exact weighted clone-constrained domain optimization

Date: 2026-08-14  
Status: **implementation complete; deterministic gate defined; independent
unary ground truth frozen.**  The primary checkout replay remains a required
publication gate and is not replaced by this report.

## Result

OrbitSynthesis can now select one exact best shared-term winning domain without
enumerating the entire antichain of inclusion-maximal domains.

For integer state utilities `w`, required states `R`, and forbidden states `X`,
the native solver maximizes

```text
(sum_(s in W) w(s), |W|, canonical_mask(W))
```

over every pointed internal-groupoid-compatible winning domain satisfying

```text
R subseteq W,
W intersect X = empty.
```

It returns:

- the optimal domain;
- a total clone-compatible strategy;
- exact objective values;
- a secondary action-preference optimum on the selected domain;
- minimized learned two-sided nogoods;
- search/pruning statistics;
- weight, preference, and trace digests; and
- an exact bounded verifier.

No greatest-domain assumption is used.

## Two exact backends

### Native branch-and-bound

`src/orbitsynthesis/domain_optimization.py` extends the exact bitset pointed
search with:

- arbitrary positive, zero, and negative integer weights;
- required and forbidden state masks;
- exact propagation of seed-rule implications;
- a valid additive lexicographic upper bound;
- deterministic weighted branching;
- bound and conflict pruning; and
- componentwise optimal action preferences.

The algorithm is dependency-free and returns one optimum rather than every
maximal domain.

### Solver-independent WCNF

`src/orbitsynthesis/domain_model.py` now emits the same signed objective as
weighted partial MaxSAT:

```text
w(s)>0  -> soft unit  x_s with weight w(s),
w(s)<0  -> soft unit -x_s with weight -w(s),
w(s)=0  -> no soft unit.
```

The total soft reward is

```text
sum_(w(s)<0) -w(s) + sum_(s in W) w(s),
```

so its maximizers are exactly the maximizers of the signed state utility.
Required states emit positive hard units; forbidden states emit negative hard
units.  Existing positive-weight callers retain the previous encoding.

This gives a backend portfolio:

```text
native exact search | external MaxSAT through WCNF.
```

## Correctness basis

For each pointed observation class, candidate representative outputs compile
to seed rules. A seed rule records:

- states whose inclusion makes that seed unsafe; and
- closure implications `source -> successor` forced by the transported output.

A domain is feasible exactly when every class has a seed whose unsafe states
are absent and whose closure implications hold. The native and CNF/WCNF
backends compile this same finite disjunction of exact candidate rules.

At a partial assignment `(I,E)`, native propagation removes no feasible
completion. The optimistic completion includes every nonnegative-weight
undecided state and excludes every negative-weight one, so its objective is an
upper bound on every descendant. Standard branch-and-bound therefore returns
the global optimum.

## Differential evidence

The primary gate covers every unary safety relation on Quackenbush `Q`:

```text
2^9 = 512 relations.
```

For each relation it evaluates six scenarios containing:

- unit weights;
- mixed positive and negative weights;
- all-zero weights;
- a required state; and
- a forbidden state.

Total corpus:

```text
3,072 weighted instances,
2,880 feasible,
192 infeasible.
```

The fixed objective corpus SHA-256 is

```text
ab589ba21f07278b82308c9a79dbc90b6846b882345764efb66df72c7e3e4346
```

For every relation, all eight domains are compared between:

1. compiled pointed seed rules;
2. the independent component-domain model; and
3. direct exhaustive term-function semantics.

For every weighted scenario, the gate compares:

1. exhaustive objective enumeration;
2. native branch-and-bound; and
3. signed WCNF reward accounting.

The primary verifier is invoked on all `2,880` feasible results. Additional
checks cover:

- a secondary action-preference optimum of `13`;
- an effective strategy mutation;
- nine-state pruning against `512` exhaustive masks; and
- fail-closed malformed weight and hard-state inputs.

## Independent audit

The no-import audit uses only the exact unary term clone of `Q`.

Every unary original-signature term operation has

```text
f(0) in {0,1},
f(1)=1-f(0),
f(2) in {0,1,2},
```

so there are exactly six candidate functions.  The audit independently scans
all six functions, all eight domains, all `512` relations, and the six weighted
scenarios.  Its committed receipt reproduces the exact corpus digest and has
semantic SHA-256

```text
1893ead79ed69ff556dde90596d453df5bf3314677b6992f3b59d3dfd6d61aba
```

## Gate

```text
bash research/tournaments/2026-08-14-weighted-domain-optimizer/check.sh
```

The gate:

- byte-compiles the changed Python modules;
- runs primary and independent scripts in normal and optimized modes;
- requires byte-identical outputs;
- binds the independent output to its committed receipt;
- pins the exact corpus census and digest;
- checks native/component/WCNF agreement; and
- reports source and output SHA-256 values.

## Practical significance

The greatest-region characterization explains when a canonical union exists.
This optimizer handles the complementary practical case: when no greatest
region exists, a user can ask for the best compatible region under an explicit
objective instead of receiving an exponentially large antichain.

The WCNF export also provides a direct route to mature MaxSAT solvers, while the
native backend remains deterministic, dependency-free, and useful as a
differential oracle.

## Boundary

The search is exact but worst-case exponential in the number of states.  No
polynomial-time result, approximation guarantee, minimal proof log, or external
performance claim is made.

Large-instance verification currently replays the deterministic native search;
small instances receive independent exhaustive verification. A compact
externally checkable optimality proof for large instances remains future work.

The caller remains responsible for the algebraic premise behind the chosen
controller semantics. The optimizer does not itself decide quasi-primality.
The lane is not Lean-formalized or externally peer reviewed, and establishes no
publication-novelty, patent/FTO, or legal conclusion.
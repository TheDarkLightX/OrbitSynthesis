# Fixed-Q obstruction research prototype

This additive, dependency-free prototype accompanies
[`QUACKENBUSH_INITIAL_SAFETY_COMPLEXITY.md`](../../../notes/QUACKENBUSH_INITIAL_SAFETY_COMPLEXITY.md).
It studies one total original-signature controller over Quackenbush's fixed
three-element algebra, not unrestricted lookup-table synthesis.

## Delivered result

- A written NP-completeness proof for explicit-table fixed-Q safety with one
  initial state and one Q-valued environment input.
- Semantic one-equation definability of the reduction's safety relations.
- An exact nonnegative-utility / feasibility algorithm with at most
  `2^(d+1)-1` nodes, where d counts initially viable complementary state pairs.
- A conditional `2^o(d)` lower bound assuming ETH, since the reduction has d=n.
- A separately implemented proof checker and exhaustive/seeded falsification.

The first, second and fourth items are mathematical derivations from stated
classical premises; finite testing does not replace those proofs. None is
claimed externally reviewed, Lean-verified, or publication-novel yet.

## Run the actual campaign

From this directory, using Python 3.10 or newer (executed here on 3.13.5):

```bash
python -B campaign.py > /tmp/q-frontier.normal.json
python -B -O campaign.py > /tmp/q-frontier.optimized.json
cmp /tmp/q-frontier.normal.json /tmp/q-frontier.optimized.json
```

The campaign writes `replay.json`, `example_certificate.json`, and a separate
`timing_diagnostic.json`. Timing is not part of the deterministic semantic
receipt. It uses only the Python standard library; no install or Tau checkout
is needed. Inputs are deliberately bounded research inputs, not hostile
service requests with allocation/time limits.

To independently verify the example:

```bash
python -B - <<'PY'
import json
from independent_check import Reference
b = json.load(open('example_certificate.json'))
Reference(b['game']).verify(b['result'], b['request'])
print('verified')
PY
```

In an application, the caller must independently pin the expected game and
request. Accepting both from the producer proves internal consistency only,
not that the producer solved the caller's intended problem. `verify` requires
a separate request to bind required states, forbidden states, objective and
whether the query is decision-only. The example is a replay, not authentication.

## Files and boundaries

`q_obstruction.py` implements bitset viability reclosure, scoped binary
obstruction branching, total-table completion and the SAT-to-game constructor.
`independent_check.py` imports no solver code and uses sets/tuples, exact orbit
list intersections, full-table checking, scoped proof replay and SAT assignments.
`campaign.py` compares the two and preserves counterexamples/negative cases.

States are lexicographic tuples in `Q^k`; each state has exactly three successor
rows, one per environment value. `Engine.solve` accepts integer state masks for
required/forbidden states, optional nonnegative integer weights, and a decision
flag. It emits a complete semantic controller table or an infeasibility tree.
A compatible table is term-definable by the classical quasi-primal theorem;
this prototype does NOT emit a `d/u` implementation DAG.

Negative utilities are rejected because stopping at the greatest feasible
branch-envelope need not optimize a signed objective. Existing signed-domain
optimizers are not replaced. Conflicts are valid only inside their recorded
allowed envelope: a removed repair successor can change feasibility.

## Actual bounded evidence

- 2,048 explicitly scoped unary games, 4,096 optimization requests, exhaustive
  domain oracle; not an exhaustive enumeration of every Q-game.
- 660 seeded games at arities 1-3, 1,320 optimization requests, including
  non-complement-invariant safety tables.
- 972 complete compatible scalar binary tables, cross-checked on 64 games.
- 917 SAT formulas: 459 SAT and 458 UNSAT, all verdicts and d=n checks agree.
- 40,149 flattened separator rows and 15 rejected certificate mutations.
- A structured 2,187-state UNSAT instance with d=6: 127 search nodes and a
  separately verified certificate. Its CNF has six literals per clause and
  includes live padding; it is not a production-performance comparison.
- Normal and optimized semantic output are byte-identical.

No full-repository replay, formal-prover compilation, real Tau integration,
production-readiness certification, or performance superiority is asserted.

## Frozen local replay hashes (SHA-256)

```
f6821a67dae13032be183babc6a2307baa589a8da5d2e6b4f108395ca53cb39a  q_obstruction.py
d17b0f6c7a1db975cc7e6de8ecfa5aabeaf336bde9eda36efcea36f9c614a88b  independent_check.py
f980746ec51f01ec7920db576bb3f0b05f3446dd0e9c560474396b36abcbc3be  campaign.py
957a4eb79f0d066eeb161e4681f5fb7097e3ec51d7bc7f085c717683dc4a688e  replay.json
38af3c92b47b0bd6d24d9527be777ac988e5924f60b52ec8de79ef76747d319f  example_certificate.json
```

The campaign transcript hash is
`81ef790fc49bc44f4230778e79167002dd99080c93fd272b5425d52cf8d7f162`.
The source manifest is in `provenance.json`. Mathematical and literature
limitations, the complete reduction, and the ETH assumption are stated in the
linked note. No Tau source is copied, bundled, or required.

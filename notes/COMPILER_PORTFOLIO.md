# OrbitSynthesis compiler portfolio

**Status:** implementation and exact finite replay lane. The portfolio does not
claim that one representation is universally best, that MDDs are
original-signature terms, or that the fixed-Q Shannon construction is practical
at explicit-table arities.

## 1. Motivation

The executable-bundle compiler originally used one bounded semantic-closure
search. That is exact and useful for tiny controllers, but it is not an
appropriate universal deployment strategy.

The practical compiler now separates four tiers:

```text
1. exact semantic closure          tiny tables
2. fixed-Q structural routers      medium structured controllers
3. reduced vector MDD              practical explicit-table fallback
4. fixed-Q Shannon compiler        diagnostic research lane only
```

The portfolio records every attempt and deterministically selects the first
materialized tier allowed by the requested policy.

## 2. Tier 1: exact semantic closure

The existing original-signature compiler enumerates semantic term functions
from the declared input projections and basic operations. A successful result
is a genuine shared term DAG over the exact supplied signature.

This tier is enabled only below a configurable explicit-row threshold. It is
not allowed to consume an arbitrarily large truth table merely because the
underlying asymptotic theorem is favorable.

Default threshold:

```text
243 rows
```

The search retains its independent bounds on:

```text
term depth
semantic functions
operation applications
exploration nodes
operation arity
```

## 3. Tier 2: fixed-Q structural router recognition

For the exact algebra

```text
Q=({0,1,2};d,u)
```

with

```text
d(x,y,z)=z if x=y, else x,
u(0)=1, u(1)=0, u(2)=1,
```

the structural backend recognizes a bounded family of terms without closing
the entire clone:

```text
input projections
u(input)
d(a,b,c) over projection/unary rails
u(d(a,b,c))
one nested signed-router layer in any discriminator argument
```

The payload/right argument is tried first because that is the natural
continuation position in the signed-router constructions.

The recognizer builds one shared multi-output DAG after matching the target
semantic coordinates. Intermediate terms used by multiple outputs are
hash-consed.

A miss means only:

```text
unsupported_by_structural_templates
```

or a candidate limit. It is not a lower bound or nondefinability theorem.

## 4. Tier 3: reduced ordered vector MDD

The MDD backend treats the complete output vector as one multi-terminal value.
It constructs a reduced ordered decision diagram with shared subgraphs and
tries three deterministic variable orders:

```text
natural
reverse
output-influence order
```

It selects the smallest diagram by:

```text
nodes + terminals,
then nodes,
then depth,
then variable order.
```

Every MDD is checked exhaustively against the certified controller table. The
graph is validated once; the complete truth table is then replayed in linear
row count with a precomputed carrier index. The verifier checks:

```text
carrier and arities
variable-order permutation
strict variable progress along edges
backward/topological node references
unique reduced nodes
no redundant all-equal child nodes
full reachability
complete table equivalence
```

An MDD is an exact executable decision diagram. It is **not** claimed to be an
original-signature algebra term. The semantic proof bundle still establishes
that the controller table is compatible with the quasi-primal term semantics;
the MDD is a separate runtime implementation.

## 5. Tier 4: Shannon research diagnostic

The fixed-Q Shannon/Lupanov construction is mathematically important, but the
current portfolio does not materialize it from explicit controller tables.

The attempt is recorded as:

```text
backend: fixed-q-shannon-experimental
status: diagnostic
automatic_selection: false
```

It can report whether the theorem's arity threshold is met and how many
explicit rows the input contains. It has no executable payload, no selection
priority, and cannot win deterministic selection.

This prevents an asymptotic result from being mistaken for a practical
explicit-table compiler.

## 6. Selection policies

### `practical`

Use the first materialized tier in the fixed order:

```text
exact semantic closure
fixed-Q structural router
reduced vector MDD
```

This follows the semantic-strength and intended-use hierarchy. Diagnostic size
and depth scores are retained for later benchmarking, but they do not override
the tier order before a validated cross-IR cost model exists.

### `original_signature`

Exclude MDD candidates. Use exact semantic closure when it succeeds, otherwise
the fixed-Q structural recognizer.

### `mdd_only`

Use only the reduced vector MDD backend.

The verifier recomputes the eligible first tier from the recorded attempts and
policy. A portfolio marked `unsupported` is accepted only when the policy truly
has no compiled candidate. Selection is part of the checked artifact, not
untrusted metadata.

## 7. Portable bundle

The new outer format is:

```text
orbit-synthesis/portfolio-proof-bundle/v1
```

It contains:

```text
stable semantic proof bundle
compiler portfolio config
all backend attempt receipts
one selected original-signature DAG or MDD
portfolio semantic SHA-256
outer manifest SHA-256
```

The semantic proof bundle remains unchanged. Compiler experimentation cannot
silently alter the winning domain, controller table, or optimum proof.

## 8. CLI

```bash
python3 tools/orbit_synthesize.py synthesize-portfolio \
  --input examples/proof_bundle/discriminator_policy.json \
  --out portfolio.json \
  --backend native \
  --portfolio-policy practical

python3 tools/orbit_synthesize.py verify-portfolio \
  --input portfolio.json
```

Useful controls include:

```text
--exact-max-rows
--mdd-max-rows
--structural-max-candidates
--disable-exact
--disable-structural
--disable-mdd
--no-shannon-diagnostic
--allow-unsupported
```

## 9. Calibrations

The source gate requires:

1. the 27-row discriminator policy to prefer the tiny exact backend;
2. the same policy with exact closure disabled to compile as one structural
   `d` node;
3. the same policy under `mdd_only` to emit and verify an MDD;
4. the nested vector controller

   ```text
   (d(x0,x1,d(x2,x3,x4)), u(d(x0,x1,d(x2,x3,x4))))
   ```

   to compile as three shared original-signature nodes;
5. a 729-row repeated-subcube table to compress into fewer MDD nodes than raw
   table rows;
6. an infeasible problem to contain no implementation;
7. the Shannon diagnostic never to be selected;
8. a lower-priority tier, false unsupported status, duplicate backend, or
   executable Shannon attempt to be rejected.

## 10. Next practical directions

The next portfolio improvements should be measured against real artifact size
and verification cost:

```text
MDD variable reordering and sifting
e-graph extraction from structural terms
algebra-specific MDD-to-term lowering
specialized fixed-Q signed-router libraries
incremental recompilation after policy changes
code generation from the selected IR
backend benchmarks on application-shaped policies
```

The full asymptotic fixed-Q compiler should remain an opt-in experimental lane
until it can materialize useful controllers at realistic arities and beat the
other backends under an explicit practical metric.

## 11. Nonclaims

This portfolio does not prove:

- minimum DAG or MDD size;
- polynomial compilation time;
- production scalability;
- that the retained diagnostic scores predict runtime performance;
- that an MDD is an original-signature term;
- that a structural-recognizer miss proves nondefinability;
- that the Shannon compiler is implemented as a deployment backend;
- end-to-end Lean verification;
- publication novelty or commercial product-market fit.

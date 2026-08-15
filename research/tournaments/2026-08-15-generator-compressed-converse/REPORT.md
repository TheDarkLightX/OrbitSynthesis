# Generator-compressed greatest-region converse

Date: 2026-08-15  
Verdict: **the universal converse witness can be compressed from a full
subalgebra listing to a minimum generating tuple, while retaining a
single-equation safety relation.**

## Theorem strengthening

Let

```text
phi:B -> C
```

be a graph-maximal nonextendable internal isomorphism in a finite quasi-primal
algebra. If `B` has minimum nonempty generating rank `d(B)`, then the generic
no-greatest shared-term safety witness can be constructed with state arity

```text
d(B)+2
```

rather than `|B|+2`.

Agreement on a generating tuple forces agreement on all of `B`, so the
maximal-nonextendability orbit-separation proof is unchanged.

Among graph-maximal obstructions, the implementation selects one with minimum
source generating rank before applying the construction.

## One-equation separator

Compression removes the old globally fixed pair of unequal prefix
coordinates. In the concrete `Q` witness, no single alternate coordinate
differs from the first projection on every unsafe tuple.

The new separator chooses one alternate coordinate per unsafe
internal-groupoid orbit. Every unsafe tuple is nonconstant, and injective
transport preserves the chosen coordinate inequality throughout its orbit.
The projection index is constant on the orbit, so the resulting operation
preserves all internal isomorphisms and generated subalgebras. Quasi-primal
interpolation therefore makes it a term.

Thus the compressed safe relation remains one equation:

```text
p(x)=g(x).
```

## Exact three-element calibration

Both the primary implementation and a separately written no-import
reconstruction exhaust all 27 unary expansions of the three-element
discriminator algebra. They recover

```text
15 demi-semi-primal expansions,
12 non-demi-semi-primal expansions.
```

The 12 converse witnesses have arity distribution

```text
arity 3: 6
arity 4: 6
```

whereas the historical full-list construction has arity 4 in all 12 cases.
The principal audit's flattened-row census falls from

```text
236,196
```

to

```text
131,220.
```

## Quackenbush-Q checkpoint

The proper subalgebra satisfies

```text
{0,1}=Sg(0),
```

so the compressed witness has state arity 3 instead of 4.

```text
principal flattened rows: 2,187
principal safe rows:      2,083
principal unsafe rows:      104
unsafe groupoid orbits:       98
```

No single alternate coordinate separates every unsafe row from the first
projection.

The eager domain-model census changes from

```text
historical:
  states             81
  observations      243
  components        227
  candidate rules 17,174
  CNF variables   17,255
  hard clauses    17,405
```

to

```text
compressed:
  states             27
  observations       81
  components         73
  candidate rules 1,762
  CNF variables    1,789
  hard clauses     1,817
```

This is an algebraic reduction before any SAT or MaxSAT optimization.

## Evidence

Primary checker:

```text
check_generator_compression.py
```

Independent checker:

```text
audits/independent/audit_generator_compression_independent.py
```

The independent semantic SHA-256 is

```text
3bab14c0844a2c16475746758444e3e55a901bc9e85ded9278923353131da60f
```

An equivalent no-import reconstruction was executed locally under ordinary and
optimized Python with byte-identical output. The exact new implementation was
also syntax-compiled and exercised through an API-compatible local harness on
all 27 expansions. The committed branch gate repeats normal/optimized checks
for the primary and independent repository sources; GitHub did not execute it
because the job was rejected before runner allocation by the account billing
block.

## Boundaries

- The original PR #25 builders remain unchanged; this is an additive stacked
  strengthening.
- Minimum means minimum **nonempty** generating tuple under the kernel's current
  convention for nullary operations.
- The state-arity bound `d(B)+2` is an upper construction, not a matching lower
  bound.
- The theorem is not yet Lean-formalized or externally peer reviewed.
- Publication novelty and legal conclusions remain unknown.

# Program-vector optimization state

Date: 2026-08-13

## Frozen baseline

On the nonbinary branch `A=2`, put

```text
one=u(A), zero=u(u(A)).
```

For target and physical words `t,p in {0,1,2}^w`, define

```text
E_p(t)=[t=p],
G_p(t)=[the first mismatch j has (t_j,p_j)=(1,2)].
```

The exact signed-router controls are

```text
positive cell: (not(E or G), G),
negative cell: (G, E or G),
positive constant c: (1-c,c),
negative constant c: (c,c).
```

The frozen construction has `q=3^w` physical branches and realizes the full
program vector with at most `7q` original-signature shared operation nodes,
including the two shared names, and depth at most
`6+2*ceil(log_2 w)` above raw anchor/address inputs.  This is independently
audited and Lean-checked.  Existing semantic-router artifacts are immutable.

## Candidate under test

The user supplied an external-agent progress log claiming, without formulas or
artifacts, that a gain/loss or native ternary first-mismatch encoding might:

1. compose a segment state with one or two discriminator nodes rather than the
   baseline three Boolean-composition nodes;
2. form negative controls from one complemented loss signal; and
3. improve the complete exact theorem from `7q` toward `4q`, while reducing
   balanced preprocessing depth from about `2 log_2 w` toward `log_2 w`.

This candidate is **untrusted**.  No formula from that agent was supplied.
Every lane must reconstruct or refute it from the exact baseline above.

## Acceptance contract

A stronger theorem must simultaneously establish:

- exact projection and both constant modes for every width and both P/N signs;
- legal `{d,u}` syntax with no nullary constants and absolute names only under
  `A=2`;
- all `2q` physical control outputs, not merely a compressed semantic state;
- one explicit hash-consed shared-DAG construction with free fanout;
- a node count including `one`, `zero`, indicators, state composition,
  complements, and final output conversion;
- operation depth above the raw anchor/address inputs;
- exact small-width replay, effective mutations, and normal/`python -O`
  agreement; and
- an all-width proof before any manuscript promotion.

If the claim is false, freeze the lexicographically smallest semantic mismatch
or the smallest exact cost/depth violation.  Bounded `NO_HIT` is not a global
lower bound.  Novelty, FTO, the integrated compiler, and global optimality are
out of scope for this tournament.

## Candidate representations to test

1. `(E,G)` first-mismatch state with cheaper native `d` composition.
2. `(L,R)` or gain/loss state, where the two absorbing mismatch outcomes are
   represented directly and equality is the residual state.
3. A single ternary state encoding `equal/zero/one` using `0/1/2`, followed by
   direct cell-control extraction.
4. Direct output-pair composition without materializing a generic state.
5. Exact small-width synthesis/lower bounds in a declared grammar.

Research Kernel run: `orbitsynthesis-program-vector-optimization-20260813`.

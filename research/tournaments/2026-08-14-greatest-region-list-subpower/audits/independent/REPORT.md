# Independent greatest-region and list-subpower audit

Date: 2026-08-14  
Verdict: **PASS in the independently reconstructed finite scope.**

This audit imports neither the primary frontier checker nor the new
OrbitSynthesis solver modules. It independently implements:

- finite subalgebras and internal isomorphisms;
- generated-subpower closure;
- the quasi-primal row-component list criterion;
- graph-maximal nonextendable internal isomorphisms;
- the generic critical/dead-orbit safety construction; and
- the exact quasi-primal strategy-table feasibility check.

## List-subpower differential

The audit checks `14,280` exact instances:

```text
pure three-element discriminator: 525
Quackenbush Q:                  13,755
```

Every component-algorithm verdict agrees with explicit generated-subpower
closure. The Q scope includes all generator/list instances for

```text
(1,1),(1,2),(1,3),(2,1),(2,2)
```

where each pair is `(generator count, coordinate count)` and every coordinate
list is nonempty.

The mutation `(0,1)` with lists `{0} x {0}` is rejected only after retaining
the internal complement edge; a row-local algorithm would accept it.

## Greatest-region differential

The audit exhausts all `27` unary expansions of the three-element
discriminator algebra. It independently finds:

```text
15 extension-property expansions,
12 nonextendable expansions.
```

For each of the `12`, the generic construction yields two separately feasible
term-winning domains and an infeasible union. The pure discriminator algebra
is the extendable negative control and yields no converse witness.

## Evidence boundary

The lane `check.sh` runs this implementation and the primary implementation in
normal and optimized Python modes and requires byte equality within each
implementation. It also asserts the exact counts above.

This audit is deterministic evidence for the generic proofs. It is not a Lean
formalization, external peer review, prior-art determination, or claim that
every generic witness is definable by one equation.

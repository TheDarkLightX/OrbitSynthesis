# Independent greatest-region and list-subpower audit

Date: 2026-08-14  
Verdict: **PASS in the independently reconstructed finite scope.**

The independent scripts import neither the primary frontier checkers nor the
new OrbitSynthesis solver modules. They reconstruct:

- finite subalgebras and internal isomorphisms;
- generated-subpower closure;
- the quasi-primal row-component list criterion;
- graph-maximal nonextendable internal isomorphisms;
- the critical/dead-orbit safety construction;
- exact quasi-primal strategy-table feasibility; and
- the one-equation projection separator.

## List-subpower differential

The audit checks `14,280` exact instances:

```text
pure three-element discriminator:   525
Quackenbush Q:                    13,755
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

## Greatest-region and principal-equation differential

The audits exhaust all `27` unary expansions of the three-element
discriminator algebra and independently find

```text
15 extension-property expansions,
12 nonextendable expansions.
```

For each of the `12`, they reconstruct:

- two separately feasible term-winning domains;
- an infeasible union;
- the critical and dead groupoid orbits;
- a broad invariant safe relation;
- a separator choosing the first projection on safe tuples and the second on
  unsafe tuples; and
- exact equality `safe iff first=separator`.

The principal audit checks `236,196` flattened transition rows. On every row it
verifies generated-subalgebra preservation; on every applicable internal
isomorphism it verifies relation invariance and separator equivariance.

The independent principal semantic SHA-256 is

```text
a7ce96dc6a723c905a8725b98498bd4aa8c52138e50919006623f7948ee0cbdd
```

The pure discriminator algebra is the extendable negative control and yields
no converse witness.

## Evidence boundary

The lane `check.sh` runs the primary and independent list/greatest-region
implementations and both principal-equation implementations under normal and
optimized Python, requiring byte equality within each implementation and
agreement of the complete 27-entry extension classification.

This is deterministic evidence for the generic proofs. It is not a Lean
formalization, external peer review, or prior-art determination.

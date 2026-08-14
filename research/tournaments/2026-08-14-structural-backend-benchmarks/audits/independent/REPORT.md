# Independent structural-family reconstruction

Date: 2026-08-14  
Verdict: **PASS for the no-import finite reconstruction.**

This audit imports no OrbitSynthesis package code.  It independently rebuilds
the two theorem families used by the external-backend benchmark.

## Exact antichain

For binary complement pairs at state arities three and four, it reconstructs:

```text
k=3: 2 orientation pairs, 4 maxima, size 24, preferred score 30
k=4: 6 orientation pairs, 64 maxima, size 74, preferred score 200
```

It checks the dead-state exclusion, exactly one selected member per orientation
pair, the closed-form counts, and uniqueness of the binary-place weighted
optimum.

## Principal restriction

The audit specializes the generic maximal-nonextendable construction directly
to Quackenbush Q.  It reconstructs the source/target critical observations,
the two dead observations, and the complement-coupled binary observation
components.  Exhausting all subsets of the four-state one-sided union gives:

```text
16 assignments
8 feasible domains
left feasible
right feasible
full union infeasible
unique weighted optimum score 13
```

## Frozen receipt

```text
semantic SHA-256
cd26a2b1b9576957615028aa44dfc1e7eb4debe4b3b33b81080bc4ddb73a23bf
```

The receipt is compared byte-for-byte under ordinary and optimized Python.
It does not exercise SciPy, PySAT, or the OrbitSynthesis implementation; those
are handled by the primary structural gate.

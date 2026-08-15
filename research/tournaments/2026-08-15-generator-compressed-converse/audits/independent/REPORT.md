# Independent generator-compression audit

Date: 2026-08-15  
Verdict: **PASS in the reconstructed three-element scope.**

This script imports no OrbitSynthesis module. It independently implements:

- finite subalgebras and internal isomorphisms;
- graph-maximal nonextendable-isomorphism selection;
- minimum nonempty generating tuples;
- the compressed critical/dead-orbit construction;
- exact quasi-primal fixed-domain feasibility;
- the broad principal relation; and
- the unsafe-orbit projection separator.

It exhausts all 27 unary expansions of the three-element discriminator and
recovers the same

```text
15 / 12
```

extension-property classification as the primary implementation.

For every nonextendable expansion it verifies:

- the generator prefix generates the full source subalgebra;
- state arity equals generator rank plus two;
- both one-sided domains are term-winning;
- their union is not term-winning;
- the orbitwise separator defines safety by one equality;
- the separator stays inside the generated subalgebra; and
- the separator commutes with every applicable internal isomorphism.

Exact census:

```text
arity 3 witnesses:                6
arity 4 witnesses:                6
strict reductions from listing:   6
compressed flattened rows:  131,220
baseline flattened rows:    236,196
```

For Quackenbush `Q`, the independent audit finds a one-element generator,
state arity three, 104 unsafe rows in 98 groupoid orbits, and proves that no
single alternate coordinate works globally.

Semantic SHA-256:

```text
3bab14c0844a2c16475746758444e3e55a901bc9e85ded9278923353131da60f
```

An equivalent no-import source was executed under ordinary and optimized
Python with byte-identical output before publication. The committed script is
gated to repeat that comparison when a runner is available. GitHub rejected
the current job before executing any steps because of the account billing
block. This remains deterministic finite evidence, not Lean formalization,
external peer review, or novelty determination.

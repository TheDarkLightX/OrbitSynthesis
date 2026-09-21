# PR18 review

The independent read-only review found no new mathematical or repaired-checker
blockers. It reviewed the two schedule cases, size margins, parity induction,
five-step logarithmic induction, inherited binary-tail bounds and charged
original-signature dependencies. It found no omitted dependency in the ledger.
Its wording correction, "final-depth upper bound", is applied in REPORT.md.

An independently constructed three-input d/u composition passed 891 full-table
evaluations across 11 target tables and all three padding values. Inverting its
slice guard produced counterexamples. This checks the selector, decoder and glue
handoffs on a small construction; it does not measure the large universal library.
The review also checked the decomposition, analytic bases and 12 recorded ledger
samples. Its CLI boundary controls stubbed receipt computation; the writer's
boundary-controls.json separately records actual full CLI rejection in both modes.

The writer ran the original and repaired full lane gates under ordinary and
optimized Python; the original receipt bytes are unchanged. Integer ceilings,
strict expected receipt bytes and a shared real routing helper repair the checker.
The manuscript and report now state the executed coverage explicitly.

The all-arity result rests on the manuscript proof and predecessor constructions.
The arithmetic sweep is bounded through arity 16,384. There is no full compiler
materialization, end-to-end Lean theorem, external mathematical peer review,
novelty finding or measured zkVM speedup. Source integration and combined hosted
CI remain required before merge.

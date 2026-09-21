# PR16 integration qualification and limits

The independent read-only agent review found no concrete counterexample to the
manuscript construction. It identified three evidence integration defects:
an unbound current manuscript, omitted CI paths, and historical manuscript-repair
receipts that disagree and require an absent manifest. Those historical bytes
remain unchanged and are explicitly excluded from current successful evidence.

The new subject inventory binds the reviewed current manuscript, notes, checker,
PDF/TeX/build inputs and evidence. CI includes every bound path. The actual binding
function rejected 156 mutation/missing-input/malformed-manifest cases per Python
mode in independent review. The writer's tests also copy the real subject and
reject a changed or missing manuscript.

The full local preprint replay passed: original and independent ordinary/optimized
checks, eight compiled Lean modules and three axiom audits. Local-gate source
bindings refer to local-replay-subject.json, retained byte-for-byte at its recorded
hash. Only the CI workflow changed after that full replay, to complete path
coverage and preserve the subsequently merged order-pair gate. Current subject
binding is checked separately and the final workflow runs the whole suite in CI.

The only mathematical-source edit in this integration narrows OptimalRailSemantics
from the Mathlib umbrella import to Mathlib.Tactic. Every theorem body is unchanged;
the existing pinned toolchain compiles all eight modules and three axiom audits.
The manuscript, PDF, original evidence and formal receipt hashes remain unchanged.

This is a scoped internal agent review. The independent compiler reconstruction
materializes complete semantics at arities 2-3; its higher-arity sweeps check
arithmetic ledgers. The Lean recurrence bounds are not a verified general DAG
extractor or integrated compiler theorem. The executable gate does not prove the
manuscript's unconditional all-arity theorem or establish novelty, practical
speedups, external mathematical peer review or archival publication readiness.

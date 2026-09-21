# Historical audit: not current integration evidence

This directory's original files are preserved for research history. They do
**not** establish a successful replay of the current manuscript.

- `check_manuscript_repairs.py` requires `paper/paper_manifest.json`, which is
  absent from this repository integration.
- `receipt.json` and `receipt_optimized.json` bind different manuscript bytes
  and have different semantic hashes. They are not a matching ordinary/optimized
  replay pair.
- The current gate does not run this historical checker or count those receipts
  as successful evidence. It separately compiles the scoped Lean proofs in
  `lanes/formal_manuscript_repairs`; that is a different artifact.

See `research/replays/pr16-20260921/` at the repository root for the current
manuscript binding, actual replay, review scope and remaining formal limits.
Updating a manifest alone cannot repair or retroactively qualify these records.

# Tau review refresh, 2026-09-12

The public source and API metadata were refreshed before implementation.
[`upstream_receipt.json`](upstream_receipt.json) records the exact references,
eight reviewed source hashes, issue/PR state, CI result, and license hash.

| Subject | Observed state |
| --- | --- |
| `main` | `43b480d4a5e6a553f1fa1b0514e1d27ab3e7da34` |
| `feature/plugins` | `b3964f6d7a3e2a7df94c18711e5523e85b3701be`, unchanged from the previous review |
| Issue #111 | Open, no comments at observation time |
| PR #112 | Open; head `801da5d50c8dde451f509d67364fd13687a3b19b` |
| PR #113 | Open; head `ad41b8688150d0f87df8ef3ec734174b2ee65fd4`; recorded Ubuntu CI run succeeded |

The latest main commit enables the existing per-support-component decision
factoring by default and exposes its control options. It does not establish
that the plugin feature line or its repairs were merged. Source:
[main commit](https://github.com/IDNI/tau-lang/commit/43b480d4a5e6a553f1fa1b0514e1d27ab3e7da34).

## Findings relevant to the next usable integration

`src/cpp_codegen.tmpl.h`, `src/ltl_aba_builders.tmpl.h`, and `src/ltl_aba.h`
are byte-identical between the inspected feature head and PR #113 head.
They retain, respectively:

1. type-only classification of an output as a Boolean carrier flag;
2. first-claimant selection guarded against multiple claimants only by an assert;
3. the explicit statement that general semantic negation is unimplemented.

The `pack_solve_impl` route still chooses the first type declaring the solver
capability in both inspected revisions. PR #113 changes the surrounding traits
file, so it should not be described as a byte-identical file.

The output-value failure and ownership consequences remain reported issue
findings supported by these source patterns. No Tau binary was built, executed,
or independently tested in this continuation. Passing PR CI does not close a
finding whose relevant source and tests were not changed.

Sources: [issue #111](https://github.com/IDNI/tau-lang/issues/111),
[PR #112](https://github.com/IDNI/tau-lang/pull/112),
[PR #113](https://github.com/IDNI/tau-lang/pull/113),
[CI run](https://github.com/IDNI/tau-lang/actions/runs/34472791450).

## Practical consequence

The first delivered tool checks finite candidate tables using an independent
model. It bypasses no Tau license condition and requires no Tau installation.
For an actual Tau-to-executable workflow, separately check translation and
emitted behavior. In particular, an accepted strategy table cannot justify a
compiled program whose output values or initial memory differ from that table.
The tested finite checker is useful now; those adapter and runtime gates remain
explicit implementation work.

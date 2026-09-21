# Tau Net application profile

The user selected an application solely for Tau Net. This supersedes the earlier
provisional local research/noncommercial target. The practical deliverable is
a small independent finite-controller checker and a working bridge from the
existing OrbitSynthesis finite safety solver.
The [checked table runtime](TABLE_RUNTIME.md) also verifies and executes a
compact table representation of the strategy.

## License basis and packaging

The Tau license at main commit
`43b480d4a5e6a553f1fa1b0514e1d27ab3e7da34`, reviewed on 2026-09-12, permits
commercial and noncommercial use of Tau for applications solely for deployment
and execution over Tau Net, and for the sole purpose of integration with Tau
Net. Its definition includes testnets. Creator-authored software made within
the permitted scope may use the creator's chosen license. The listed grants
exclude redistribution of Tau or portions of Tau.
Source: [pinned IDNI license](https://github.com/IDNI/tau-lang/blob/43b480d4a5e6a553f1fa1b0514e1d27ab3e7da34/LICENSE.md).

The checker, bridge, and example use OrbitSynthesis's existing
[MIT license](../../LICENSE). They package original code and finite data, with
no Tau source, binary, generated code, runtime, or automatic downloader. A native
adapter can later invoke a separately obtained Tau installation, with its own
license and version pinned. That adapter and its Tau use will be dedicated to
the Tau Net application. This scope selection does not itself implement or
prove a connection to Tau Net, and does not establish patent clearance.

## Executable example

The [generator](synthesize_tau_net_gate.py) models a gate with two actions:

- Inputs: two eligibility bits supplied by the application's trusted adapter.
- Outputs: two selection bits; choose exactly one eligible action if possible,
  otherwise choose neither.
- State: the previous output, initially `(0, 0)`.

Tuple IDs follow `(0, 0), (0, 1), (1, 0), (1, 1)`. Eligibility is observed before
selection in the same step. Every input sequence is possible. The safety solver
prefers the first allowed output in that declared order, so the example has no
fairness guarantee when both actions remain eligible.

The contract is frozen before synthesis; the exporter does not change it to
match the candidate. The checker explores all reachable state/memory pairs and
input values. Altering an output to select both actions is rejected. Replacing
the model after synthesis is rejected when the original pin is retained.
See the [commands and API](README.md#generate-a-controller-with-the-existing-orbitsynthesis-solver).

## Application integration still required

For a real Tau Net application, the owner must define how authenticated Tau Net
state determines the two eligibility bits and how selected actions map to valid
transactions. Those mappings, any Tau strategy conversion, and any generated
executable must be checked against the reviewed model before an operational
gate accepts them. The current prototype has no transaction, signing, network,
deployment or side-effect authority. Its JSON records are replay evidence, not
authenticated approvals.

The restricted OSMC table runtime now has a complete memory/input comparison
against the accepted strategy. That check does not extend to arbitrary native
executables or to these application-specific mappings and effects.

This prototype checks a finite model, not full Tau LTL/CTL* semantics. Its
general checker also supports recurring-progress goals, exercised by the fair
and starving controller examples. The existing producer bridge only exports
finite transition-safety games.

# Practical finite-controller checking

The implemented tool is [`scripts/check_controller.py`](../../../scripts/check_controller.py).
Start with the [runnable examples](../../../examples/controllers/README.md).
It checks a supplied controller against an independently pinned finite contract
and returns either acceptance, a finite safety counterexample, or a prefix and
repeating cycle showing starvation.

Implemented scope: input-first finite Mealy controllers, safety, and conjunctions
of recurring-progress goals. There is no input fairness assumption. The tool
does not synthesize a controller or establish that a rejected contract has no
solution.

## Evidence

From the repository root:

```bash
python3 research/prototypes/2026-09-12-strategy-checker/check.py
```

The gate compares every transition table with one through three plant states,
two inputs and one output against an independently written matrix-closure
oracle, including forbidden transitions and every possible single recurrence
set: 33,100 cases. It also checks 300 seeded cases with controller memory,
multiple outputs and two goals, schema and pin failures, witness validity,
immutable results, and CLI exit codes. Normal and optimized Python runs must
produce identical demo records.

Four deliberately faulty checker copies establish that the retained negatives
detect omitted contract binding, omitted safety checking, omitted recurrence
checking, and omission of the second environment input. The probe edits only
temporary copies of this independently authored checker.

The [producer bridge](../../../src/orbitsynthesis/safety_export.py) is checked
against a direct tuple-relation oracle for 8,192 combinations of two-state game,
initial state and positional candidate. All 256 two-state/two-input safety games
also compare the existing solver's winning region against exhaustive strategy
enumeration. The [application generator](../../../examples/controllers/synthesize_tau_net_gate.py)
produces byte-identical artifacts in normal and optimized Python. Changed source
contracts, altered outputs and missing reachable rows are tested as failures.

The [table runtime](../../../examples/controllers/TABLE_RUNTIME.md) checks all
declared memory/input steps against the accepted strategy, then executes that
same immutable table. Its tests cover 592 small machines, 1120 single-bit image
corruptions, 1280 stateful traces, and four controlled fault probes. Normal and
optimized runs must produce the same image and runtime replay bytes.

The fair arbiter has four reachable product states, sixteen checked transitions,
and two recurring-progress goals. The priority arbiter fails on this sequence:

```text
input 3 (both requests) -> grant request 0; request 1 stays pending
repeat input 1         -> grant request 0; request 1 stays pending forever
```

These are original fixtures. They are not Tau-produced controllers or native
reproductions of the Tau issue. See [`replay.json`](replay.json) for the source
hashes and detailed model results after running the gate.

## Remaining integration work

| Gate | Current status |
| --- | --- |
| Independently pinned finite contract and strategy | Implemented |
| Safety and recurring-progress checking | Implemented for the declared finite model |
| Actionable input/output counterexamples | Implemented |
| Tau syntax/HOA to finite-contract translation | Unimplemented; must preserve initial state, timing, domains and goals |
| Existing OrbitSynthesis solver supplying candidates | Implemented for finite transition-safety games |
| Tau supplying candidates | Unimplemented native adapter |
| OSMC table runtime versus accepted strategy | Implemented; complete memory/input comparison using the actual table step function |
| Native generated executable versus accepted strategy | Unimplemented; still required to catch native code-generation errors |
| Operational admission, side effects, deployment | Unimplemented |

The selected product target is an application solely for Tau Net. The
[application profile](../../../examples/controllers/TAU_NET_APPLICATION.md)
records the use scope and the practical generator-to-checker workflow. Any
native Tau adapter will use a separately obtained installation within that
scope. This packet uses OrbitSynthesis's existing MIT license and does not
bundle Tau. The [provenance note](PROVENANCE.md) records the exact boundary.

The previous standalone checker source packet and receipt are preserved in
[`baselines/standalone-v1.tar.gz`](baselines/standalone-v1.tar.gz). Its hashes
describe that archived version; `replay.json` describes the current files.
The solver bridge version before table execution is also preserved in
[`baselines/producer-bridge-v1.tar.gz`](baselines/producer-bridge-v1.tar.gz).

# Checked table execution

The generator now saves `controller.osmc`: a compact, original OrbitSynthesis
Mealy-machine table. The [runtime](../../src/orbitsynthesis/controller_runtime.py)
loads it only after rechecking the pinned contract, strategy safety/progress,
image bindings, initial memory, and every memory/input step. It executes data
using a fixed Python step function. This is not a native executable or a Tau
program; no candidate Python or shell code is evaluated.

## Generate, independently check, and replay

From the repository root, use a new output directory:

```bash
python3 examples/controllers/synthesize_tau_net_gate.py --output-dir /tmp/orbit-tau-net-runtime
python3 scripts/run_controller.py /tmp/orbit-tau-net-runtime/contract.json /tmp/orbit-tau-net-runtime/strategy.json /tmp/orbit-tau-net-runtime/controller.osmc --contract-pin /tmp/orbit-tau-net-runtime/contract.sha256 --inputs 0 1 2 3
```

The output IDs are `0, 1, 2, 1`: idle, action 1, action 0, then action 1 when both
are eligible. IDs follow the example's declared tuple order, not bit significance
in a packed integer. The runtime checks all twelve memory/input pairs before
replaying the four requested steps. Omit `--inputs` to check without replaying.
Add `--json` for program/model/strategy hashes, selected source hashes, the exact
runtime profile, row count, and replay trace.

Retain the model hash independently after reviewing the contract. The generated
example pin is a convenience, not approval of a replacement model. Each CLI
invocation reloads and rechecks the bytes. Exit 0 means verification and the
requested replay succeeded; exit 1 means the model, strategy or image was
rejected; exit 2 means an argument, file or runtime input was invalid. The CLI
replays at most 4096 inputs and does not perform application effects.

## Python embedding

```python
from orbitsynthesis.controller_runtime import (
    CheckedController, ControllerStep, load_controller,
)

loaded = load_controller(contract_bytes, strategy_bytes, image_bytes, trusted_model_pin)
if isinstance(loaded, CheckedController):
    memory = loaded.initial_memory
    for input_id in application_inputs:
        result = loaded.step(memory, input_id)
        if not isinstance(result, ControllerStep):
            break  # typed rejection, with no state change or output action
        memory = result.next_memory
        print(result.output)  # selection only; the application owns any effects
```

Use `PYTHONPATH=src`. The caller owns controller memory: start at
`initial_memory` and carry each successful `next_memory` forward. Restoring an
unverified checkpoint or resetting memory mid-trace breaks this execution
contract. Persistence, concurrency, authentication and atomic application
effects require an application-specific shell.

The pure runtime rejects Boolean/integer aliases, negative values, and IDs
outside the declared domains. Rejection changes no controller state. Loaded
tables, receipts and outcomes contain only immutable values. Replacing an image
file after loading does not change the already loaded table. Python objects
can still be forged or interpreter code replaced by a caller with that access;
these handles and JSON receipts are not authenticated capabilities.

## Exact image format, version 1

The [encoder](../../src/orbitsynthesis/controller_compile.py) and runtime reader
implement this layout separately. The runtime never imports the encoder.

| Byte offsets | Encoding |
| --- | --- |
| 0–7 | Magic/version, hex `4f534d4300000001` |
| 8–39 | SHA-256 of the canonical contract, raw 32 bytes |
| 40–71 | SHA-256 of the canonical strategy, raw 32 bytes |
| 72 | Number of input IDs, one unsigned byte |
| 73 | Number of output IDs, one unsigned byte |
| 74 | Number of memory states, one unsigned byte |
| 75 | Initial memory ID, one unsigned byte |
| 76 onward | `[output, next_memory]` byte pairs, memory-major then input-major |

The exact length is `76 + 2 * memory_states * inputs`, at most 2124 bytes. Both
hashes, all counts and initial memory must agree with the independently checked
JSON inputs. There are no optional fields, ignored padding bytes or trailing
data. Each runtime step must agree with the JSON strategy, including declared
unreachable memory states. Semantically equivalent machines with different
memory numbering need their own strategy; this format checks exact table
correspondence rather than discovering arbitrary machine equivalence.

## What the runtime check establishes

The loader validates the actual fixed step function on every declared
`(memory, input)` pair. The function depends only on those arguments and an
immutable byte table. The initial memory is equal to the strategy's initial
memory. Induction therefore gives identical outputs and next memory for every
finite input trace; infinite traces have the same prefixes and satisfy the
same safety/recurrence contract when execution carries state as specified.

This is an exhaustive finite runtime check and a mathematical induction
argument, not a machine-checked proof of Python. It does not verify arbitrary
generated C++, native binaries, Tau translation, Tau Net input eligibility,
transaction effects, or deployment. Records say
`table_runtime_equivalence_verified: true` only after the loader's check.
The older broad `runtime_refinement_verified` field remains false because
application effects and a deployed runtime are outside this prototype.

## Ownership, versioning and evidence

The OrbitSynthesis checker maintainer owns the format and runtime profile
`orbitsynthesis/osmc-table-runtime/v1`. Producers emit data; the loader owns
acceptance against the caller's retained model pin. Changing the format or step
semantics requires a new profile and coordinated producer/consumer validation.
There is no automatic activation, upgrade, rollback or deployment authority.

Tests enumerate all 592 machines with one or two memory states, inputs and
outputs, including each initial memory. They reject all 1120 single-bit changes
to the arbiter image, check 1280 stateful traces, and test invalid IDs, image
replacement after loading, and immutable ownership. Controlled runtime faults
ignore memory, flip output, or flip next memory; the loader rejects each. A
negative image also detects a deliberately omitted row comparison. The full
[replay gate](../../research/prototypes/2026-09-12-strategy-checker/check.py) runs
in normal and optimized Python and compares generated image and replay bytes.

The implementation uses the repository's MIT license and adds no external
dependency or Tau component. The selected [Tau Net application scope](TAU_NET_APPLICATION.md)
continues to apply to the planned application integration.

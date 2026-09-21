# Check a controller before using it

Run these commands from the OrbitSynthesis directory with Python 3.12 or later.
The tool and examples run locally using the Python standard library. No Tau
installation, online service, API key, or additional software license is used.

## A fair two-request arbiter

```bash
python3 scripts/check_controller.py examples/controllers/arbiter.contract.json examples/controllers/arbiter.strategy.json --contract-pin examples/controllers/arbiter.sha256
```

The contract records two pending request flags. Input values `0`, `1`, `2`, and
`3` add no request, request 0, request 1, or both requests. Output `0` waits;
`1` grants request 0; `2` grants request 1. Grants require a pending or arriving
request and can serve at most one flag per tick. Repeated arrivals coalesce
into those flags; this is not a queue of distinct jobs.

The supplied controller remembers the pending flags and alternates priority.
The checker verifies safety and that each pending flag is cleared infinitely
often, across every possible sequence of arrivals. It checks the finite graph
of all reachable plant/controller states, so the claim has no trace-length cap.

## Find starvation

```bash
python3 scripts/check_controller.py examples/controllers/arbiter.contract.json examples/controllers/arbiter_priority.strategy.json --contract-pin examples/controllers/arbiter.sha256
```

This controller always favors request 0. The output includes a prefix followed
by a repeating cycle that leaves request 1 pending forever. Exit status is 1.
This is a counterexample to this controller, not a proof that no controller
can satisfy the contract; the fair example satisfies the same contract.

## Check a delayed acknowledgement service

```bash
python3 scripts/check_controller.py examples/controllers/service.contract.json examples/controllers/service.strategy.json --contract-pin examples/controllers/service.sha256
```

Input `1` adds a pending request, input `0` adds none. Output `1` acknowledges a
pending or newly arriving request; output `0` waits. Requests coalesce into one
flag. The example acknowledges pending work on the following tick. The
`service_starving.strategy.json` variant fails because it never acknowledges.

`output_flip` is a synthetic negative example: the contract requires output
zero, but the controller emits one. It exercises the failure family motivating
the Tau output-classification review; it is not a native Tau reproduction.

## Use your own model and controller

The [contract specification](../../research/prototypes/2026-09-12-strategy-checker/CONTRACT.md)
defines the closed JSON schemas and exact input-first timing semantics. Build
the contract from the requirements you intend to enforce, review it, and store
its hash independently from controller candidates. Do not accept a replacement
contract and replacement hash supplied by the controller producer.

The Python authoring helper emits the required canonical bytes:

```python
from hashlib import sha256
from pathlib import Path
from orbitsynthesis.strategy_checker import canonical_bytes, verify, Accepted

contract_bytes = canonical_bytes(reviewed_contract)
expected_hash = sha256(contract_bytes).hexdigest()  # freeze after model review
Path("controller.contract.json").write_bytes(contract_bytes)
Path("controller.sha256").write_text(expected_hash + "\n")

result = verify(contract_bytes, canonical_bytes(candidate_strategy), expected_hash)
if isinstance(result, Accepted):
    print("This finite controller satisfies the reviewed model.")
```

Run Python with `PYTHONPATH=src` when using the API from this checkout. Canonical
JSON has sorted keys, no whitespace or trailing newline, and integer-only
numeric fields. Strategy rows cover every memory/input pair, including declared
unreachable controller states. The contract bounds are 64 plant states,
64 controller states, 16 inputs, 16 outputs, and 16 recurring-progress goals.

Add `--json` to save a record containing the checked contract/strategy hashes,
checker source hash, counts, and any counterexample. Exit codes are 0 for
acceptance, 1 for a semantic counterexample, and 2 for invalid input or I/O
failure. A JSON record is not an authenticated approval; rerun the checker
before relying on it.

## Current Tau use boundary

This first tool is independently authored OrbitSynthesis software under the
existing [MIT license](../../LICENSE). It does not include or invoke Tau.
The selected application scope is **solely for Tau Net**, including its testnets.
The [application profile](TAU_NET_APPLICATION.md) records how that scope relates
to the pinned Tau license and what remains to connect a real application.
Any future native adapter will use a separately obtained Tau installation.

Tau syntax, HOA conversion, generated executables, fairness assumptions and
real application effects are not checked by this tool. Each needs a separate
translation/refinement gate. The [provenance record](../../research/prototypes/2026-09-12-strategy-checker/PROVENANCE.md)
records the source exposure and license review; no patent clearance is claimed.
The additional [table runtime](TABLE_RUNTIME.md) now checks and executes the
restricted OSMC table format against an accepted strategy.

## Generate a controller with the existing OrbitSynthesis solver

The [Tau Net gate example](synthesize_tau_net_gate.py) selects one of two eligible
actions, or idles if neither is eligible. It builds a contract first, invokes
`FiniteSafetyGame.solve_ordinary`, then independently checks the resulting
controller. It uses the existing solver instead of a hand-written strategy.

```bash
python3 examples/controllers/synthesize_tau_net_gate.py --output-dir /tmp/orbit-tau-net-gate
python3 scripts/check_controller.py /tmp/orbit-tau-net-gate/contract.json /tmp/orbit-tau-net-gate/strategy.json --contract-pin /tmp/orbit-tau-net-gate/contract.sha256
```

Use a new output directory; the generator preserves any existing directory.
Its files include canonical contract/strategy JSON, the example model pin, and
a record binding the model, strategy and selected implementation source hashes.
It also saves `controller.osmc` after checking all steps of the table runtime.
Review the model and retain its pin independently before accepting a replacement
candidate. Generating a candidate and a new pin together is not model approval.

The gate checks three reachable states and twelve transitions for every input
sequence. It enforces safety only: at most one action, selection requires
eligibility, and some action is selected whenever any action is eligible.
Eligibility comes from the model input. Real eligibility, authentication,
effects, scheduling fairness, Tau execution and Tau Net deployment are outside
this example's verification claim.

For your own `FiniteSafetyGame`, use the small
[export bridge](../../src/orbitsynthesis/safety_export.py):

```python
from hashlib import sha256
from orbitsynthesis.safety_export import export_contract, export_strategy
from orbitsynthesis.strategy_checker import verify

contract = export_contract(game, initial_state)
pin = sha256(contract).hexdigest()  # freeze after reviewing the model
solution = game.solve_ordinary()
candidate = export_strategy(game, initial_state, solution.strategy, pin)
verdict = verify(contract, candidate, pin)
```

The bridge uses the game's declared tuple order as the integer wire order.
Output is the next plant state; controller memory tracks it. A candidate must
provide every row reachable under its own choices. Missing unreachable rows
are omitted rather than filled. Export does not validate safety or a producer's
winning-region claim. The bridge supports at most 16 states/outputs and 16
inputs; a zero-arity input is represented by the single empty tuple. It exports
transition safety with all states initially eligible and no recurrence goals.
Term-definability claims for the algebra are not established by this checker.

## Run the checked controller table

```bash
python3 scripts/run_controller.py /tmp/orbit-tau-net-gate/contract.json /tmp/orbit-tau-net-gate/strategy.json /tmp/orbit-tau-net-gate/controller.osmc --contract-pin /tmp/orbit-tau-net-gate/contract.sha256 --inputs 0 1 2 3
```

This reloads and independently checks the generated table before replaying
inputs. The [runtime contract](TABLE_RUNTIME.md) gives the format, API, state
ownership rule and exact verification claim. The command selects output IDs;
it does not execute Tau Net transactions or application effects.

# Finite controller verification contract, version 1

Status: independent research prototype. The acceptance claim concerns the
explicit finite model supplied by the caller. No Tau syntax translation,
generated C++ verification, deployment admission, or settlement authority is
implemented here. A rejected controller does not establish that its contract
is unrealizable.

## Semantics

The environment chooses an input at each tick. The controller observes that
current input and its own memory, emits an output, and updates its memory.
The trusted contract determines the next plant state from the current plant
state, input, and output. The controller does not directly observe plant state;
any such observation must be encoded explicitly as input in a later profile.

Every input symbol is possible at every tick, indefinitely. There are no
implicit fairness, oracle, network-delivery, or cooperative-environment
assumptions. A transition marked `-1` is a forbidden controller response,
not an unavailable environment input. Deadlock is a failure, never vacuous
success. Fairness-dependent contracts require a different, explicitly checked
assumption profile; they cannot be encoded by silently removing inputs.

The property is `G safe AND (AND_j GF goal_j)`. Goals apply to plant states.
An empty list of goals requests safety only. An empty individual goal is
impossible on an infinite execution. Initial state safety is checked.

## Wire format and trust boundary

Inputs are immutable ASCII JSON bytes with sorted object keys, no whitespace,
no duplicate keys, no floats, and no trailing newline. Exact schemas reject
unknown/missing fields. Integers exclude JSON booleans. State sets are sorted
and duplicate-free. Arrays retain their declared order.

Contract fields:

| Field | Meaning |
| --- | --- |
| `schema` | `orbitsynthesis/finite-controller-contract/v1` |
| `states`, `inputs`, `outputs` | Positive cardinalities; states <= 64, alphabets <= 16 |
| `initial` | Initial plant state, numbered from zero |
| `safe_states` | Safe plant-state IDs |
| `transitions` | Flat state/input/output-major table; successor state or `-1` |
| `recurrence` | At most 16 state sets to visit infinitely often |

Strategy fields:

| Field | Meaning |
| --- | --- |
| `schema` | `orbitsynthesis/finite-mealy-strategy/v1` |
| `contract_sha256` | Hash of the exact canonical contract bytes |
| `memory_states` | Controller memory-state count, 1 through 64 |
| `initial_memory` | Initial controller memory state |
| `rows` | Memory/input-major table of `[output, next_memory]` pairs |

Each wire input is limited to 1 MiB. Tables must be total and well-formed even
at unreachable declared controller states. Every legal initial product state
has at least one outgoing edge because the input alphabet is nonempty and a
missing/forbidden selected transition is rejected. The largest product has
4,096 states and 65,536 edges.

`verify(contract_bytes, strategy_bytes, expected_contract_sha256)` receives
the expected contract hash separately from the strategy. The caller must
obtain that pin from its own reviewed configuration. Accepting an attacker’s
replacement model and replacement hash would defeat this boundary. A hash
identifies the chosen model; it does not prove that the model expresses the
human requirements.

Decoded values are privately constructed frozen records containing immutable
values. Mutable maps/deques exist only as local graph-building scratch. The
core performs no I/O, global registration, dynamic imports, external callbacks,
plugin dispatch, solver calls, or assertion-based validation. The public
result can be constructed by ordinary Python code and is not an authenticated
capability: consumers must rerun verification on the exact pinned bytes.

## Decision procedure and argument

1. Decode and validate both artifacts, including independent contract binding.
2. Enumerate all reachable `(plant, memory)` pairs, taking every input edge.
3. Reject any unsafe initial state or selected forbidden/unsafe transition.
4. For each goal, search the reachable graph after removing vertices in that
   goal. Reject if this induced graph has a directed cycle.

Safety: induction on the number of steps shows that every finite execution
prefix follows an enumerated edge and stays safe after step 3 succeeds.

Recurrence: a violating infinite execution eventually avoids one goal. Since
the product is finite, that suffix repeats a vertex and contains a cycle
outside the goal. Conversely, a reachable cycle outside a goal supplies a
finite input prefix and a repeating input sequence that violates recurrence.
Thus step 4 is necessary and sufficient for the declared universal recurrence
property of this finite deterministic controller. Reachability is computed
before deleting goal vertices; a bad cycle reached through a goal still fails.

The graph procedure is O((k+1)(V+E)) for k goals, excluding bounded JSON decoding.
This is a mathematical argument for the procedure, not a machine-checked proof
of the Python implementation. Differential testing uses a separately written
transitive-closure oracle rather than the checker's DFS.

## Counterexamples and assurance boundaries

Safety failures carry the finite offending path. Recurrence failures carry a
prefix and a nonempty cycle, including input/output labels and both state
components. The cycle returns to its entry vertex and avoids the named goal.
These witnesses refute the supplied strategy. They are not an environment
counter-strategy against every possible controller.

The checker does not parse LTL, CTL*, HOA, or Tau; prove a theory abstraction;
model real-number arithmetic; certify a compiler; or execute a candidate.
All paths of the declared finite model are checked, not just traces up to a
chosen time limit. This does not extend the claim to an unbounded application
state space or to real executions without a refinement proof.

The separate [OSMC runtime gate](../../../examples/controllers/TABLE_RUNTIME.md)
now exhaustively checks a restricted table runtime against the strategy. This
does not change the standalone model checker's scope or certify native code.

## Pattern selection and admission implications

| Choice | Mechanical guarantee | Remaining obligation |
| --- | --- | --- |
| Caller-supplied model pin | Candidate cannot silently replace the checked contract | Authentic caller configuration and requirements review |
| Frozen finite tables | No retained mutable input aliases after decoding | Python objects are not tamper-proof capabilities |
| Explicit result variants | Malformed/unsafe candidates return no accepted result | A future caller must inspect the variant and rerun after loading |
| Full product exploration | Every reachable modeled input continuation is considered | Tau-to-model and program-to-model refinement |
| Cycle-based recurrence | Detects starvation without choosing a trace horizon | Environment assumptions must be explicit and justified |

The standalone checker module owns this contract version. No production
consumer or activation mechanism exists. No Rust implementation is mounted.
CAS, crash recovery, outbox delivery, runtime authority, rollout and rollback
remain obligations of a future admission shell, not features of this packet.

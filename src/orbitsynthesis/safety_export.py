# SPDX-License-Identifier: MIT
"""Author finite-checker inputs from an existing FiniteSafetyGame.

Export is not verification. Freeze the model before running a candidate producer
and pass the reviewed model pin separately to strategy_checker.verify().
"""

from __future__ import annotations

import re
from collections import deque
from collections.abc import Mapping

from .safety import FiniteSafetyGame, Observation, Output, State
from .strategy_checker import (
    CONTRACT_SCHEMA,
    MAX_ALPHABET,
    MAX_STATES,
    STRATEGY_SCHEMA,
    canonical_bytes,
)


def _domains(game: FiniteSafetyGame, initial: State):
    states, inputs = tuple(game.states), tuple(game.inputs)
    if not 1 <= len(states) <= min(MAX_STATES, MAX_ALPHABET):
        raise ValueError("state/output count exceeds checker bounds")
    if not 1 <= len(inputs) <= MAX_ALPHABET:
        raise ValueError("input count exceeds checker bounds")
    if len(set(states)) != len(states) or len(set(inputs)) != len(inputs):
        raise ValueError("domains must be duplicate-free")
    if tuple(game.outputs) != states:
        raise ValueError("this bridge requires output to be the next state")
    if initial not in states:
        raise ValueError("unknown initial state")
    return states, inputs


def export_contract(game: FiniteSafetyGame, initial: State) -> bytes:
    """Encode exactly the game's transition-safety relation, with no liveness.

State, input and output IDs follow the game's declared order. All states are
initially eligible: FiniteSafetyGame specifies safe edges, not a separate state
invariant. A forbidden edge is -1; it never removes an environment input.
"""
    states, inputs = _domains(game, initial)
    relation = frozenset(game.safe_relation)
    state_set, input_set = set(states), set(inputs)
    for state, event, output in relation:
        if state not in state_set or event not in input_set or output not in state_set:
            raise ValueError("relation contains an unknown domain value")
    return canonical_bytes({
        "schema": CONTRACT_SCHEMA,
        "states": len(states), "inputs": len(inputs), "outputs": len(states),
        "initial": states.index(initial), "safe_states": list(range(len(states))),
        "transitions": [index if (state, event, output) in relation else -1
                        for state in states for event in inputs
                        for index, output in enumerate(states)],
        "recurrence": [],
    })


def export_strategy(game: FiniteSafetyGame, initial: State,
                    strategy: Mapping[Observation, Output], contract_sha256: str) -> bytes:
    """Encode a supplied positional table as a self-tracking Mealy controller.

Memory stores the previous output (the current plant state). Every input row
reachable under this candidate must be supplied, even if its selected output
is unsafe. Missing unreachable rows are omitted, never filled with defaults.
The exporter does not consult the safety relation or trust a winning-region
claim; the independent checker decides whether the result satisfies the model.
"""
    states, inputs = _domains(game, initial)
    if type(contract_sha256) is not str or re.fullmatch("[0-9a-f]{64}", contract_sha256) is None:
        raise ValueError("expected a lowercase SHA-256 model pin")
    table = dict(strategy)
    observations = {state + event for state in states for event in inputs}
    state_ids = {state: index for index, state in enumerate(states)}
    for observation, output in table.items():
        if observation not in observations or output not in state_ids:
            raise ValueError("strategy contains an unknown observation or output")

    reached = {initial}
    pending = deque([initial])
    while pending:
        state = pending.popleft()
        for event in inputs:
            observation = state + event
            if observation not in table:
                raise ValueError("missing strategy row reachable under this candidate")
            output = table[observation]
            if output not in reached:
                reached.add(output)
                pending.append(output)

    memory_states = tuple(state for state in states if state in reached)
    memory_ids = {state: index for index, state in enumerate(memory_states)}
    return canonical_bytes({
        "schema": STRATEGY_SCHEMA, "contract_sha256": contract_sha256,
        "memory_states": len(memory_states), "initial_memory": memory_ids[initial],
        "rows": [[state_ids[table[state + event]], memory_ids[table[state + event]]]
                 for state in memory_states for event in inputs],
    })

# SPDX-License-Identifier: MIT
"""Independent finite Mealy-strategy checker.

Exact scope: research/prototypes/2026-09-12-strategy-checker/CONTRACT.md.

No Tau code, synthesis procedure, external solver, filesystem, or subprocess is
used by verify(). Public verdicts are observations, not unforgeable credentials.
"""

from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

CONTRACT_SCHEMA = "orbitsynthesis/finite-controller-contract/v1"
STRATEGY_SCHEMA = "orbitsynthesis/finite-mealy-strategy/v1"
MAX_BYTES = 1_048_576
MAX_STATES = 64
MAX_ALPHABET = 16
MAX_GOALS = 16


class RejectCode(str, Enum):
    INVALID_PIN = "invalid_pin"
    CONTRACT_PIN = "contract_pin_mismatch"
    CONTRACT_FORMAT = "invalid_contract"
    STRATEGY_FORMAT = "invalid_strategy"
    STRATEGY_CONTRACT = "strategy_contract_mismatch"
    RESOURCE_LIMIT = "resource_limit"
    UNSAFE_INITIAL = "unsafe_initial_state"
    UNSAFE_STEP = "unsafe_transition"
    RECURRENCE = "recurrence_counterexample"


@dataclass(frozen=True)
class Step:
    plant: int
    memory: int
    input: int
    output: int
    next_plant: int
    next_memory: int


@dataclass(frozen=True)
class Rejected:
    code: RejectCode
    detail: str
    prefix: tuple[Step, ...] = ()
    cycle: tuple[Step, ...] = ()
    recurrence_index: int | None = None


@dataclass(frozen=True)
class Accepted:
    contract_sha256: str
    strategy_sha256: str
    reachable_product_states: int
    checked_product_edges: int
    checked_recurrence_sets: int


@dataclass(frozen=True)
class _Contract:
    states: int
    inputs: int
    outputs: int
    initial: int
    safe: frozenset[int]
    transitions: tuple[int, ...]
    recurrence: tuple[frozenset[int], ...]


@dataclass(frozen=True)
class _Strategy:
    initial: int
    rows: tuple[tuple[int, int], ...]


class _Invalid(Exception):
    def __init__(self, code: RejectCode, detail: str):
        self.code = code
        self.detail = detail


def canonical_bytes(value: object) -> bytes:
    """Authoring helper; verification additionally validates the closed schema."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _fail(code: RejectCode, detail: str) -> None:
    raise _Invalid(code, detail)


def _decode(raw: bytes, code: RejectCode) -> dict:
    if type(raw) is not bytes:
        _fail(code, "expected immutable bytes")
    if len(raw) > MAX_BYTES:
        _fail(RejectCode.RESOURCE_LIMIT, "wire exceeds byte limit")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                _fail(code, "duplicate object key")
            result[key] = value
        return result

    def no_float(_text):
        _fail(code, "noninteger numeric literal")

    try:
        obj = json.loads(raw.decode("ascii"), object_pairs_hook=pairs,
                         parse_float=no_float, parse_constant=no_float)
        if type(obj) is not dict:
            _fail(code, "expected object")
        if canonical_bytes(obj) != raw:
            _fail(code, "noncanonical wire encoding")
        return obj
    except (ValueError, UnicodeError, RecursionError, TypeError):
        _fail(code, "invalid JSON encoding")


def _keys(obj: dict, expected: set[str], code: RejectCode) -> None:
    if set(obj) != expected:
        _fail(code, "unknown or missing field")


def _integer(value, lower: int, upper: int, code: RejectCode) -> int:
    if type(value) is not int or not lower <= value <= upper:
        _fail(code, "integer outside declared bounds")
    return value


def _state_set(value, count: int, code: RejectCode) -> frozenset[int]:
    if type(value) is not list or len(value) > count:
        _fail(code, "invalid state set")
    for item in value:
        _integer(item, 0, count - 1, code)
    if value != sorted(set(value)):
        _fail(code, "state sets must be sorted and duplicate-free")
    return frozenset(value)


def _contract(raw: bytes) -> _Contract:
    code = RejectCode.CONTRACT_FORMAT
    obj = _decode(raw, code)
    _keys(obj, {"schema", "states", "inputs", "outputs", "initial",
                "safe_states", "transitions", "recurrence"}, code)
    if obj["schema"] != CONTRACT_SCHEMA:
        _fail(code, "unsupported contract schema")
    states = _integer(obj["states"], 1, MAX_STATES, code)
    inputs = _integer(obj["inputs"], 1, MAX_ALPHABET, code)
    outputs = _integer(obj["outputs"], 1, MAX_ALPHABET, code)
    initial = _integer(obj["initial"], 0, states - 1, code)
    safe = _state_set(obj["safe_states"], states, code)
    transitions = obj["transitions"]
    if type(transitions) is not list or len(transitions) != states * inputs * outputs:
        _fail(code, "transition table must cover every state/input/output")
    for successor in transitions:
        _integer(successor, -1, states - 1, code)
    recurrence = obj["recurrence"]
    if type(recurrence) is not list or len(recurrence) > MAX_GOALS:
        _fail(code, "invalid recurrence objectives")
    return _Contract(states, inputs, outputs, initial, safe, tuple(transitions),
                     tuple(_state_set(goal, states, code) for goal in recurrence))


def _strategy(raw: bytes, contract: _Contract, digest: str) -> _Strategy:
    code = RejectCode.STRATEGY_FORMAT
    obj = _decode(raw, code)
    _keys(obj, {"schema", "contract_sha256", "memory_states", "initial_memory", "rows"}, code)
    if obj["schema"] != STRATEGY_SCHEMA:
        _fail(code, "unsupported strategy schema")
    if obj["contract_sha256"] != digest:
        _fail(RejectCode.STRATEGY_CONTRACT, "strategy names a different contract")
    count = _integer(obj["memory_states"], 1, MAX_STATES, code)
    initial = _integer(obj["initial_memory"], 0, count - 1, code)
    rows = obj["rows"]
    if type(rows) is not list or len(rows) != count * contract.inputs:
        _fail(code, "strategy must cover every memory/input pair")
    frozen = []
    for row in rows:
        if type(row) is not list or len(row) != 2:
            _fail(code, "strategy row must be [output, next_memory]")
        output = _integer(row[0], 0, contract.outputs - 1, code)
        successor = _integer(row[1], 0, count - 1, code)
        frozen.append((output, successor))
    return _Strategy(initial, tuple(frozen))


def _prefix(vertex: tuple[int, int], parents: dict) -> tuple[Step, ...]:
    path = []
    while parents[vertex] is not None:
        edge = parents[vertex]
        path.append(edge)
        vertex = (edge.plant, edge.memory)
    return tuple(reversed(path))


def _avoiding_cycle(graph: dict, goal: frozenset[int]) -> tuple[Step, ...]:
    """Iterative DFS in the reachable subgraph excluding one recurrence set."""
    color = {}
    for root, root_edges in graph.items():
        if root[0] in goal or color.get(root, 0):
            continue
        color[root] = 1
        stack = [(root, iter(root_edges))]
        path = []
        positions = {root: 0}
        while stack:
            vertex, edges = stack[-1]
            edge = next(edges, None)
            if edge is None:
                stack.pop()
                color[vertex] = 2
                del positions[vertex]
                if stack:
                    path.pop()
                continue
            target = (edge.next_plant, edge.next_memory)
            if target[0] in goal:
                continue
            if color.get(target, 0) == 1:
                return tuple(path[positions[target]:] + [edge])
            if color.get(target, 0) == 0:
                color[target] = 1
                path.append(edge)
                positions[target] = len(path)
                stack.append((target, iter(graph[target])))
    return ()


def verify(contract_bytes: bytes, strategy_bytes: bytes,
           expected_contract_sha256: str) -> Accepted | Rejected:
    """Check G safe AND each GF recurrence-set under ALL input sequences.

    expected_contract_sha256 must come from the caller's trusted configuration,
    separately from the candidate. Failure is not a proof of unrealizability.
    """
    if (type(expected_contract_sha256) is not str or
            re.fullmatch("[0-9a-f]{64}", expected_contract_sha256) is None):
        return Rejected(RejectCode.INVALID_PIN, "expected a lowercase SHA-256 pin")
    if type(contract_bytes) is not bytes:
        return Rejected(RejectCode.CONTRACT_FORMAT, "expected immutable bytes")
    if len(contract_bytes) > MAX_BYTES:
        return Rejected(RejectCode.RESOURCE_LIMIT, "wire exceeds byte limit")
    digest = sha256(contract_bytes).hexdigest()
    if digest != expected_contract_sha256:
        return Rejected(RejectCode.CONTRACT_PIN, "contract differs from caller pin")
    try:
        contract = _contract(contract_bytes)
        strategy = _strategy(strategy_bytes, contract, digest)
    except _Invalid as error:
        return Rejected(error.code, error.detail)

    root = (contract.initial, strategy.initial)
    if contract.initial not in contract.safe:
        return Rejected(RejectCode.UNSAFE_INITIAL, "initial state is unsafe")
    parents = {root: None}
    pending = deque([root])
    graph = {}
    while pending:
        state, memory = pending.popleft()
        edges = []
        for input_value in range(contract.inputs):
            output, next_memory = strategy.rows[memory * contract.inputs + input_value]
            index = (state * contract.inputs + input_value) * contract.outputs + output
            next_state = contract.transitions[index]
            edge = Step(state, memory, input_value, output, next_state, next_memory)
            if next_state == -1 or next_state not in contract.safe:
                return Rejected(RejectCode.UNSAFE_STEP, "selected transition is unsafe",
                                _prefix((state, memory), parents) + (edge,))
            edges.append(edge)
            target = (next_state, next_memory)
            if target not in parents:
                parents[target] = edge
                pending.append(target)
        graph[(state, memory)] = tuple(edges)

    for index, goal in enumerate(contract.recurrence):
        cycle = _avoiding_cycle(graph, goal)
        if cycle:
            entry = (cycle[0].plant, cycle[0].memory)
            return Rejected(RejectCode.RECURRENCE, "reachable cycle avoids a recurrence set",
                            _prefix(entry, parents), cycle, index)
    return Accepted(digest, sha256(strategy_bytes).hexdigest(), len(graph),
                    sum(map(len, graph.values())), len(contract.recurrence))

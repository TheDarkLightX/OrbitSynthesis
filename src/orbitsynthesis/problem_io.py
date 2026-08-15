"""Portable JSON schema for finite clone-constrained safety problems.

The v1 format deliberately restricts carrier elements to JSON integers or
strings. This keeps canonicalization, hashing, and cross-language verification
unambiguous. The safety relation may be supplied as an allowlist or denylist
of explicit transitions; canonical output always uses the semantic allowlist.

The caller explicitly acknowledges the quasi-primal interpolation premise.
OrbitSynthesis verifies the finite tables and all derived controller
certificates, but it does not infer quasi-primality from arbitrary input tables.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Mapping

from .finite_algebra import FiniteAlgebra, FiniteOperation
from .safety import FiniteSafetyGame, Transition

JsonAtom = int | str
State = tuple[JsonAtom, ...]
_SCHEMA = "orbit-synthesis/finite-safety-problem/v1"
_SEMANTICS = "quasi_primal_internal_groupoid"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _reject_extra_keys(
    payload: Mapping[str, object],
    allowed: frozenset[str],
    *,
    field: str,
) -> None:
    extras = set(payload) - allowed
    if extras:
        raise ValueError(
            f"{field} contains unknown key {min(extras)!r}"
        )


def _require_keys(
    payload: Mapping[str, object],
    required: frozenset[str],
    *,
    field: str,
) -> None:
    missing = required - set(payload)
    if missing:
        raise ValueError(
            f"{field} is missing required key {min(missing)!r}"
        )


def _atom(value: object, *, field: str) -> JsonAtom:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise TypeError(f"{field} must contain only JSON integers or strings")
    return value


def _tuple_row(
    value: object,
    *,
    length: int,
    carrier: frozenset[JsonAtom],
    field: str,
) -> tuple[JsonAtom, ...]:
    if not isinstance(value, list):
        raise TypeError(f"{field} must be a JSON list")
    if len(value) != length:
        raise ValueError(f"{field} must have length {length}")
    row = tuple(_atom(item, field=field) for item in value)
    if not set(row) <= carrier:
        raise ValueError(f"{field} contains a value outside the carrier")
    return row


def _transition_key(transition: Transition) -> str:
    return repr(transition)


@dataclass(frozen=True)
class FiniteSafetyProblem:
    """One canonical finite-algebra safety optimization problem."""

    name: str
    algebra: FiniteAlgebra
    state_arity: int
    input_arity: int
    safe_relation: frozenset[Transition]
    state_weight_items: tuple[tuple[State, int], ...]
    default_weight: int
    required_states: frozenset[State]
    forbidden_states: frozenset[State]
    semantics: str = _SEMANTICS
    quasi_primal_premise: bool = True

    @property
    def state_weights(self) -> dict[State, int]:
        return dict(self.state_weight_items)

    def game(self) -> FiniteSafetyGame:
        return FiniteSafetyGame(
            self.algebra,
            self.state_arity,
            self.input_arity,
            self.safe_relation,
        )

    def semantic_payload(self) -> dict[str, object]:
        carrier = tuple(self.algebra.values)
        operations = []
        for operation in sorted(self.algebra.operations, key=lambda row: row.name):
            outputs = [
                operation(*arguments)
                for arguments in product(carrier, repeat=operation.arity)
            ]
            operations.append(
                {
                    "name": operation.name,
                    "arity": operation.arity,
                    "outputs": outputs,
                }
            )

        transitions = [
            {
                "state": list(state),
                "input": list(input_value),
                "output": list(output),
            }
            for state, input_value, output in sorted(
                self.safe_relation,
                key=_transition_key,
            )
        ]
        weights = [
            {"state": list(state), "weight": weight}
            for state, weight in sorted(
                self.state_weight_items,
                key=lambda item: repr(item[0]),
            )
        ]
        return {
            "schema": _SCHEMA,
            "name": self.name,
            "semantics": {
                "mode": self.semantics,
                "quasi_primal_premise_acknowledged": self.quasi_primal_premise,
            },
            "algebra": {
                "carrier": list(carrier),
                "operations": operations,
            },
            "game": {
                "state_arity": self.state_arity,
                "input_arity": self.input_arity,
                "safe_relation": {
                    "mode": "allowed",
                    "transitions": transitions,
                },
            },
            "objective": {
                "default_state_weight": self.default_weight,
                "state_weights": weights,
                "required_states": [
                    list(state)
                    for state in sorted(self.required_states, key=repr)
                ],
                "forbidden_states": [
                    list(state)
                    for state in sorted(self.forbidden_states, key=repr)
                ],
            },
        }

    @property
    def semantic_sha256(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.semantic_payload())).hexdigest()

    def to_json(self) -> str:
        return json.dumps(
            self.semantic_payload(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n"

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "FiniteSafetyProblem":
        top_keys = frozenset(
            ("schema", "name", "semantics", "algebra", "game", "objective")
        )
        _reject_extra_keys(payload, top_keys, field="problem")
        _require_keys(payload, top_keys, field="problem")
        if payload.get("schema") != _SCHEMA:
            raise ValueError("unsupported finite-safety problem schema")

        name_value = payload["name"]
        if not isinstance(name_value, str) or not name_value:
            raise ValueError("problem name must be a nonempty string")

        semantics_payload = payload["semantics"]
        if not isinstance(semantics_payload, Mapping):
            raise TypeError("semantics must be a JSON object")
        semantics_keys = frozenset(
            ("mode", "quasi_primal_premise_acknowledged")
        )
        _reject_extra_keys(
            semantics_payload,
            semantics_keys,
            field="semantics",
        )
        _require_keys(semantics_payload, semantics_keys, field="semantics")
        semantics = semantics_payload["mode"]
        if semantics != _SEMANTICS:
            raise ValueError(
                "v1 supports only quasi_primal_internal_groupoid semantics"
            )
        premise = semantics_payload["quasi_primal_premise_acknowledged"]
        if premise is not True:
            raise ValueError(
                "the caller must explicitly acknowledge the quasi-primal premise"
            )

        algebra_payload = payload["algebra"]
        if not isinstance(algebra_payload, Mapping):
            raise TypeError("algebra must be a JSON object")
        algebra_keys = frozenset(("carrier", "operations"))
        _reject_extra_keys(algebra_payload, algebra_keys, field="algebra")
        _require_keys(algebra_payload, algebra_keys, field="algebra")
        carrier_payload = algebra_payload["carrier"]
        if not isinstance(carrier_payload, list) or not carrier_payload:
            raise ValueError("algebra.carrier must be a nonempty JSON list")
        carrier = tuple(
            _atom(value, field="algebra.carrier") for value in carrier_payload
        )
        if len(set(carrier)) != len(carrier):
            raise ValueError("algebra carrier values must be distinct")
        carrier_set = frozenset(carrier)

        operations_payload = algebra_payload["operations"]
        if not isinstance(operations_payload, list) or not operations_payload:
            raise ValueError("algebra.operations must be a nonempty JSON list")
        operations = []
        operation_names = set()
        operation_keys = frozenset(("name", "arity", "outputs"))
        for index, operation_payload in enumerate(operations_payload):
            if not isinstance(operation_payload, Mapping):
                raise TypeError(f"operation {index} must be a JSON object")
            _reject_extra_keys(
                operation_payload,
                operation_keys,
                field=f"operation {index}",
            )
            _require_keys(
                operation_payload,
                operation_keys,
                field=f"operation {index}",
            )
            name = operation_payload["name"]
            arity = operation_payload["arity"]
            outputs = operation_payload["outputs"]
            if not isinstance(name, str) or not name:
                raise ValueError(f"operation {index} has an invalid name")
            if name in operation_names:
                raise ValueError(f"duplicate operation name: {name!r}")
            operation_names.add(name)
            if isinstance(arity, bool) or not isinstance(arity, int) or arity < 0:
                raise ValueError(f"operation {name!r} has an invalid arity")
            if not isinstance(outputs, list):
                raise TypeError(f"operation {name!r} outputs must be a list")
            points = tuple(product(carrier, repeat=arity))
            if len(outputs) != len(points):
                raise ValueError(
                    f"operation {name!r} needs {len(points)} outputs, "
                    f"received {len(outputs)}"
                )
            table = {}
            for arguments, output in zip(points, outputs, strict=True):
                value = _atom(output, field=f"operation {name!r} outputs")
                if value not in carrier_set:
                    raise ValueError(
                        f"operation {name!r} returns a value outside the carrier"
                    )
                table[arguments] = value
            operations.append(FiniteOperation.from_mapping(name, arity, table))
        algebra = FiniteAlgebra(values=carrier, operations=tuple(operations))

        game_payload = payload["game"]
        if not isinstance(game_payload, Mapping):
            raise TypeError("game must be a JSON object")
        game_keys = frozenset(("state_arity", "input_arity", "safe_relation"))
        _reject_extra_keys(game_payload, game_keys, field="game")
        _require_keys(game_payload, game_keys, field="game")
        state_arity = game_payload["state_arity"]
        input_arity = game_payload["input_arity"]
        if (
            isinstance(state_arity, bool)
            or not isinstance(state_arity, int)
            or state_arity <= 0
        ):
            raise ValueError("game.state_arity must be a positive integer")
        if (
            isinstance(input_arity, bool)
            or not isinstance(input_arity, int)
            or input_arity < 0
        ):
            raise ValueError("game.input_arity must be a nonnegative integer")

        relation_payload = game_payload["safe_relation"]
        if not isinstance(relation_payload, Mapping):
            raise TypeError("game.safe_relation must be a JSON object")
        relation_keys = frozenset(("mode", "transitions"))
        _reject_extra_keys(
            relation_payload,
            relation_keys,
            field="game.safe_relation",
        )
        _require_keys(
            relation_payload,
            relation_keys,
            field="game.safe_relation",
        )
        relation_mode = relation_payload["mode"]
        if relation_mode not in {"allowed", "forbidden"}:
            raise ValueError(
                "safe_relation.mode must be 'allowed' or 'forbidden'"
            )
        transitions_payload = relation_payload["transitions"]
        if not isinstance(transitions_payload, list):
            raise TypeError("safe_relation.transitions must be a JSON list")
        listed: set[Transition] = set()
        transition_keys = frozenset(("state", "input", "output"))
        for index, transition_payload in enumerate(transitions_payload):
            if not isinstance(transition_payload, Mapping):
                raise TypeError(f"transition {index} must be a JSON object")
            _reject_extra_keys(
                transition_payload,
                transition_keys,
                field=f"transition {index}",
            )
            _require_keys(
                transition_payload,
                transition_keys,
                field=f"transition {index}",
            )
            state = _tuple_row(
                transition_payload["state"],
                length=state_arity,
                carrier=carrier_set,
                field=f"transition {index}.state",
            )
            input_value = _tuple_row(
                transition_payload["input"],
                length=input_arity,
                carrier=carrier_set,
                field=f"transition {index}.input",
            )
            output = _tuple_row(
                transition_payload["output"],
                length=state_arity,
                carrier=carrier_set,
                field=f"transition {index}.output",
            )
            transition = (state, input_value, output)
            if transition in listed:
                raise ValueError(f"duplicate transition at index {index}")
            listed.add(transition)

        if relation_mode == "allowed":
            safe_relation = frozenset(listed)
        else:
            universe = {
                (state, input_value, output)
                for state in product(carrier, repeat=state_arity)
                for input_value in product(carrier, repeat=input_arity)
                for output in product(carrier, repeat=state_arity)
            }
            safe_relation = frozenset(universe - listed)

        objective_payload = payload["objective"]
        if not isinstance(objective_payload, Mapping):
            raise TypeError("objective must be a JSON object")
        objective_keys = frozenset(
            (
                "default_state_weight",
                "state_weights",
                "required_states",
                "forbidden_states",
            )
        )
        _reject_extra_keys(
            objective_payload,
            objective_keys,
            field="objective",
        )
        _require_keys(objective_payload, objective_keys, field="objective")
        default_weight = objective_payload["default_state_weight"]
        if isinstance(default_weight, bool) or not isinstance(default_weight, int):
            raise TypeError("default_state_weight must be an integer")

        state_weights_payload = objective_payload["state_weights"]
        if not isinstance(state_weights_payload, list):
            raise TypeError("objective.state_weights must be a JSON list")
        weight_map: dict[State, int] = {}
        weight_keys = frozenset(("state", "weight"))
        for index, row in enumerate(state_weights_payload):
            if not isinstance(row, Mapping):
                raise TypeError(f"state weight {index} must be a JSON object")
            _reject_extra_keys(
                row,
                weight_keys,
                field=f"state weight {index}",
            )
            _require_keys(row, weight_keys, field=f"state weight {index}")
            state = _tuple_row(
                row["state"],
                length=state_arity,
                carrier=carrier_set,
                field=f"state weight {index}.state",
            )
            weight = row["weight"]
            if isinstance(weight, bool) or not isinstance(weight, int):
                raise TypeError(f"state weight {index} must be an integer")
            if state in weight_map:
                raise ValueError(f"duplicate state weight for {state!r}")
            weight_map[state] = weight

        def parse_state_list(field: str) -> frozenset[State]:
            rows = objective_payload[field]
            if not isinstance(rows, list):
                raise TypeError(f"objective.{field} must be a JSON list")
            parsed = [
                _tuple_row(
                    row,
                    length=state_arity,
                    carrier=carrier_set,
                    field=f"objective.{field}",
                )
                for row in rows
            ]
            if len(set(parsed)) != len(parsed):
                raise ValueError(f"objective.{field} contains duplicates")
            return frozenset(parsed)

        required_states = parse_state_list("required_states")
        forbidden_states = parse_state_list("forbidden_states")
        if required_states & forbidden_states:
            raise ValueError("required and forbidden states overlap")

        problem = cls(
            name=name_value,
            algebra=algebra,
            state_arity=state_arity,
            input_arity=input_arity,
            safe_relation=safe_relation,
            state_weight_items=tuple(
                sorted(weight_map.items(), key=lambda item: repr(item[0]))
            ),
            default_weight=default_weight,
            required_states=required_states,
            forbidden_states=forbidden_states,
            semantics=semantics,
            quasi_primal_premise=True,
        )
        problem.game()
        return problem

    @classmethod
    def from_json(cls, text: str) -> "FiniteSafetyProblem":
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise TypeError("problem JSON must contain one object")
        return cls.from_dict(payload)

    @classmethod
    def load(cls, path: str | Path) -> "FiniteSafetyProblem":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def write(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")

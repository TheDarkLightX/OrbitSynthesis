"""Practical proof-carrying clone-constrained safety synthesis pipeline.

This module assembles the existing standalone OrbitSynthesis components into
one deterministic API:

finite algebra + explicit safety relation
    -> controller-semantics comparison
    -> maximal internal-groupoid-compatible domain
    -> Q original-signature shared DAG when the strategy is conservative
    -> replayable JSON certificate.

The implementation is intentionally dependency-free and Tau-independent.  The
first compiler backend is deliberately scoped to conservative strategies over
Quackenbush's three-element algebra Q.  Other finite algebras still receive the
full realizability analysis and obstruction certificate, but not a false claim
of original-signature compilation.
"""

from __future__ import annotations

import hashlib
import json
from itertools import product
from typing import Hashable, Iterable, Mapping, Sequence

from .domain_api import CompiledParameterizedKernel
from .finite_algebra import FiniteAlgebra, FiniteOperation, InternalIsomorphism
from .orbit_term_compile import (
    Disc,
    Expr,
    UnaryU,
    Var,
    compile_orbit_coordinate_selector,
    evaluate as evaluate_q_expr,
)
from .safety import FiniteSafetyGame, Observation, Output, State

JSONScalar = str | int | float | bool | None

MODEL_SCHEMA = "orbit-synthesis/finite-algebra-safety/v1"
CERTIFICATE_SCHEMA = "orbit-synthesis/practical-clone-synthesis/v1"
DAG_SCHEMA = "orbit-synthesis/original-signature-dag/v1"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _as_json_scalar(value: Hashable) -> JSONScalar:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(
        "the v1 JSON model supports only scalar carrier values; "
        f"got {type(value).__name__}"
    )


def _tuple_json(values: Sequence[Hashable]) -> list[JSONScalar]:
    return [_as_json_scalar(value) for value in values]


def _ordered_subset(
    universe: Sequence[tuple[Hashable, ...]],
    subset: Iterable[tuple[Hashable, ...]],
) -> list[list[JSONScalar]]:
    selected = frozenset(subset)
    return [_tuple_json(value) for value in universe if value in selected]


def _operation_lookup(algebra: FiniteAlgebra, name: str) -> FiniteOperation | None:
    for operation in algebra.operations:
        if operation.name == name:
            return operation
    return None


def is_quackenbush_q(algebra: FiniteAlgebra) -> bool:
    """Recognize the exact fixed-Q operation tables used by the compiler."""

    if tuple(algebra.values) != (0, 1, 2):
        return False
    discriminator = _operation_lookup(algebra, "d")
    unary = _operation_lookup(algebra, "u")
    if discriminator is None or discriminator.arity != 3:
        return False
    if unary is None or unary.arity != 1:
        return False
    return all(
        discriminator(x, y, z) == (z if x == y else x)
        for x, y, z in product((0, 1, 2), repeat=3)
    ) and all(unary(value) == (1, 0, 1)[value] for value in (0, 1, 2))


def game_to_model(
    game: FiniteSafetyGame,
    initial_states: Iterable[State],
    *,
    name: str,
) -> dict[str, object]:
    """Serialize a finite-algebra safety instance deterministically."""

    initial = frozenset(initial_states)
    _require(initial <= frozenset(game.states), "initial state outside game")

    operations = []
    for operation in game.algebra.operations:
        table = [
            {
                "args": _tuple_json(args),
                "value": _as_json_scalar(operation(*args)),
            }
            for args in product(game.algebra.values, repeat=operation.arity)
        ]
        operations.append(
            {"name": operation.name, "arity": operation.arity, "table": table}
        )

    transitions = [
        {
            "state": _tuple_json(state),
            "input": _tuple_json(input_value),
            "output": _tuple_json(output),
        }
        for state in game.states
        for input_value in game.inputs
        for output in game.outputs
        if game.is_safe(state, input_value, output)
    ]

    return {
        "schema": MODEL_SCHEMA,
        "name": name,
        "algebra": {
            "carrier": [_as_json_scalar(value) for value in game.algebra.values],
            "operations": operations,
        },
        "game": {
            "state_arity": game.state_arity,
            "input_arity": game.input_arity,
            "safe_transitions": transitions,
        },
        "initial_states": _ordered_subset(game.states, initial),
    }


def game_from_model(
    model: Mapping[str, object],
) -> tuple[FiniteSafetyGame, frozenset[State], str]:
    """Validate and materialize the v1 JSON model."""

    _require(model.get("schema") == MODEL_SCHEMA, "unsupported model schema")
    name = model.get("name")
    _require(isinstance(name, str) and bool(name), "model name must be nonempty")

    algebra_json = model.get("algebra")
    _require(isinstance(algebra_json, Mapping), "missing algebra object")
    carrier_json = algebra_json.get("carrier")
    _require(isinstance(carrier_json, list) and carrier_json, "empty carrier")
    carrier = tuple(carrier_json)
    _require(len(set(carrier)) == len(carrier), "duplicate carrier value")

    operation_json = algebra_json.get("operations")
    _require(isinstance(operation_json, list), "operations must be a list")
    operations: list[FiniteOperation] = []
    for raw in operation_json:
        _require(isinstance(raw, Mapping), "operation must be an object")
        operation_name = raw.get("name")
        arity = raw.get("arity")
        table_json = raw.get("table")
        _require(isinstance(operation_name, str), "operation name must be text")
        _require(isinstance(arity, int) and arity >= 0, "invalid operation arity")
        _require(isinstance(table_json, list), "operation table must be a list")
        table: dict[tuple[Hashable, ...], Hashable] = {}
        for row in table_json:
            _require(isinstance(row, Mapping), "operation row must be an object")
            args = row.get("args")
            _require(isinstance(args, list), "operation args must be a list")
            key = tuple(args)
            _require(len(key) == arity, "operation row has wrong arity")
            _require(key not in table, "duplicate operation row")
            table[key] = row.get("value")
        operations.append(FiniteOperation.from_mapping(operation_name, arity, table))
    algebra = FiniteAlgebra(values=carrier, operations=tuple(operations))

    game_json = model.get("game")
    _require(isinstance(game_json, Mapping), "missing game object")
    state_arity = game_json.get("state_arity")
    input_arity = game_json.get("input_arity")
    transitions_json = game_json.get("safe_transitions")
    _require(isinstance(state_arity, int) and state_arity > 0, "bad state arity")
    _require(isinstance(input_arity, int) and input_arity >= 0, "bad input arity")
    _require(isinstance(transitions_json, list), "safe transitions must be a list")

    relation = set()
    for row in transitions_json:
        _require(isinstance(row, Mapping), "transition must be an object")
        state = row.get("state")
        input_value = row.get("input")
        output = row.get("output")
        _require(isinstance(state, list), "transition state must be a list")
        _require(isinstance(input_value, list), "transition input must be a list")
        _require(isinstance(output, list), "transition output must be a list")
        relation.add((tuple(state), tuple(input_value), tuple(output)))

    game = FiniteSafetyGame(algebra, state_arity, input_arity, relation)
    raw_initial = model.get("initial_states")
    _require(isinstance(raw_initial, list), "initial_states must be a list")
    initial = frozenset(tuple(state) for state in raw_initial)
    _require(initial <= frozenset(game.states), "initial state outside game")
    return game, initial, name


def _strategy_rows(
    game: FiniteSafetyGame,
    strategy: Mapping[Observation, Output],
) -> list[dict[str, list[JSONScalar]]]:
    return [
        {
            "observation": _tuple_json(observation),
            "output": _tuple_json(strategy[observation]),
        }
        for observation in game.observations
        if observation in strategy
    ]


def _mode_result(
    game: FiniteSafetyGame,
    initial: frozenset[State],
    *,
    mode: str,
    winning: frozenset[State],
    strategy: Mapping[Observation, Output],
) -> dict[str, object]:
    return {
        "mode": mode,
        "initial_realizable": initial <= winning,
        "winning_state_count": len(winning),
        "winning_states": _ordered_subset(game.states, winning),
        "strategy_rows": len(strategy),
    }


def _quasi_solution(
    game: FiniteSafetyGame,
    initial: frozenset[State],
    *,
    search: str,
    exhaustive_state_limit: int,
) -> tuple[frozenset[State], dict[Observation, Output]] | None:
    if search == "exhaustive":
        solution = game.solve_quasi_primal_from_initial(
            initial,
            exhaustive_state_limit=exhaustive_state_limit,
        )
        if solution is None:
            return None
        return solution.winning_states, solution.strategy

    if search not in {"nogood", "bitset_nogood"}:
        raise ValueError("quasi search must be exhaustive, nogood, or bitset_nogood")
    kernel = CompiledParameterizedKernel(
        game,
        frozenset(),
        internal_isomorphisms=game.algebra.internal_isomorphisms(),
    )
    rows = kernel.maximal_domains(
        solver="pointed",
        search=search,
        required_states=initial,
    )
    if not rows:
        return None

    state_positions = {state: index for index, state in enumerate(game.states)}

    def key(
        row: tuple[
            frozenset[State],
            tuple[tuple[Observation, Output], ...],
        ]
    ) -> tuple[object, ...]:
        domain, _strategy_items = row
        mask = tuple(int(state in domain) for state in game.states)
        return (len(domain), mask)

    domain, strategy_items = max(rows, key=key)
    strategy = dict(strategy_items)
    _require(set(strategy) == set(game.observations), "quasi strategy is not total")
    _require(all(state in state_positions for state in domain), "unknown domain state")
    return domain, strategy


def _allowed_outputs(
    game: FiniteSafetyGame,
    domain: frozenset[State],
) -> dict[Observation, tuple[Output, ...]]:
    result: dict[Observation, tuple[Output, ...]] = {}
    for observation in game.observations:
        state, input_value = game.split_observation(observation)
        generated = game.algebra.generated_subalgebra(observation)
        values = []
        for output in game.outputs:
            if not all(value in generated for value in output):
                continue
            if state in domain and (
                output not in domain or not game.is_safe(state, input_value, output)
            ):
                continue
            values.append(output)
        result[observation] = tuple(values)
    return result


def first_groupoid_conflict(
    game: FiniteSafetyGame,
    domain: Iterable[State],
) -> dict[str, object] | None:
    """Return one deterministic, checkable internal-isomorphism conflict.

    The result is an explanatory unsatisfiable component, not a claim of a
    minimum unsatisfiable core.
    """

    winning = frozenset(domain)
    allowed = _allowed_outputs(game, winning)
    for observation in game.observations:
        if not allowed[observation]:
            return {
                "kind": "local_no_output",
                "observation": _tuple_json(observation),
            }

    isomorphisms = game.algebra.internal_isomorphisms()
    iso_index = {
        id(isomorphism): index for index, isomorphism in enumerate(isomorphisms)
    }
    arity = game.state_arity + game.input_arity
    edges: dict[Observation, list[tuple[Observation, InternalIsomorphism]]] = {
        observation: [] for observation in game.observations
    }
    observation_set = set(game.observations)
    for isomorphism in isomorphisms:
        for source in product(tuple(isomorphism.domain), repeat=arity):
            if source not in observation_set:
                continue
            target = isomorphism.map_tuple(source)
            if target in observation_set:
                edges[source].append((target, isomorphism))

    neighbors = {observation: set() for observation in game.observations}
    for source, outgoing in edges.items():
        for target, _isomorphism in outgoing:
            neighbors[source].add(target)
            neighbors[target].add(source)

    seen: set[Observation] = set()
    for representative in game.observations:
        if representative in seen:
            continue
        component: set[Observation] = set()
        stack = [representative]
        while stack:
            source = stack.pop()
            if source in component:
                continue
            component.add(source)
            stack.extend(neighbors[source] - component)
        seen.update(component)

        rejected: list[dict[str, object]] = []
        solved = False
        for candidate in allowed[representative]:
            local = {representative: candidate}
            queue = [representative]
            failure: dict[str, object] | None = None
            while queue and failure is None:
                source = queue.pop(0)
                source_output = local[source]
                for target, isomorphism in edges[source]:
                    index = iso_index[id(isomorphism)]
                    if not all(value in isomorphism.domain for value in source_output):
                        failure = {
                            "kind": "output_outside_isomorphism_domain",
                            "source": _tuple_json(source),
                            "source_output": _tuple_json(source_output),
                            "target": _tuple_json(target),
                            "isomorphism_index": index,
                        }
                        break
                    mapped = isomorphism.map_tuple(source_output)
                    if mapped not in allowed[target]:
                        failure = {
                            "kind": "transported_output_forbidden",
                            "source": _tuple_json(source),
                            "source_output": _tuple_json(source_output),
                            "target": _tuple_json(target),
                            "transported_output": _tuple_json(mapped),
                            "target_allowed": [
                                _tuple_json(output) for output in allowed[target]
                            ],
                            "isomorphism_index": index,
                        }
                        break
                    prior = local.get(target)
                    if prior is not None and prior != mapped:
                        failure = {
                            "kind": "cycle_inconsistency",
                            "source": _tuple_json(source),
                            "target": _tuple_json(target),
                            "prior_output": _tuple_json(prior),
                            "transported_output": _tuple_json(mapped),
                            "isomorphism_index": index,
                        }
                        break
                    if prior is None:
                        local[target] = mapped
                        queue.append(target)
            if failure is None and set(local) == component:
                solved = True
                break
            rejected.append(
                {
                    "representative_output": _tuple_json(candidate),
                    "failure": failure
                    or {
                        "kind": "incomplete_component_propagation",
                        "assigned": len(local),
                        "component_size": len(component),
                    },
                }
            )

        if not solved:
            return {
                "kind": "groupoid_component_unsatisfiable",
                "representative": _tuple_json(representative),
                "component": [
                    _tuple_json(observation)
                    for observation in game.observations
                    if observation in component
                ],
                "candidate_rejections": rejected,
                "isomorphism_count": len(isomorphisms),
            }
    return None


def _selector_indices(
    game: FiniteSafetyGame,
    strategy: Mapping[Observation, Output],
) -> tuple[dict[Observation, int], ...] | None:
    output_arity = game.state_arity
    tables: list[dict[Observation, int]] = [dict() for _ in range(output_arity)]
    for observation in game.observations:
        output = strategy[observation]
        for coordinate in range(output_arity):
            matches = [
                index
                for index, value in enumerate(observation)
                if value == output[coordinate]
            ]
            if not matches:
                return None
            tables[coordinate][observation] = matches[0]
    return tuple(tables)


def _q_unary(value: int) -> int:
    return (1, 0, 1)[value]


def _q_discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def _small_q_expression(
    game: FiniteSafetyGame,
    scalar_table: Mapping[Observation, int],
    selector_table: Mapping[Observation, int],
) -> tuple[str, Expr]:
    arity = game.state_arity + game.input_arity
    observations = game.observations

    for index in range(arity):
        if all(scalar_table[point] == point[index] for point in observations):
            return "projection", Var(index)
    for index in range(arity):
        if all(
            scalar_table[point] == _q_unary(point[index]) for point in observations
        ):
            return "unary_u", UnaryU(Var(index))
    for i, j, k in product(range(arity), repeat=3):
        if all(
            scalar_table[point]
            == _q_discriminator(point[i], point[j], point[k])
            for point in observations
        ):
            return "single_discriminator", Disc(Var(i), Var(j), Var(k))
    return "orbit_coordinate_selector", compile_orbit_coordinate_selector(
        arity,
        selector_table,
    )


def serialize_q_expressions(expressions: Sequence[Expr]) -> dict[str, object]:
    """Structurally hash-cons multiple Q-term roots into one canonical DAG."""

    nodes: list[dict[str, object]] = []
    index: dict[tuple[object, ...], int] = {}
    depths: list[int] = []

    def intern(node: Expr) -> int:
        if isinstance(node, Var):
            key: tuple[object, ...] = ("var", node.index)
            payload: dict[str, object] = {"op": "var", "index": node.index}
            depth = 0
        elif isinstance(node, UnaryU):
            child = intern(node.value)
            key = ("u", child)
            payload = {"op": "u", "args": [child]}
            depth = depths[child] + 1
        elif isinstance(node, Disc):
            children = (intern(node.x), intern(node.y), intern(node.z))
            key = ("d",) + children
            payload = {"op": "d", "args": list(children)}
            depth = max(depths[child] for child in children) + 1
        else:  # pragma: no cover - closed expression hierarchy
            raise TypeError(type(node))
        prior = index.get(key)
        if prior is not None:
            return prior
        node_id = len(nodes)
        index[key] = node_id
        payload = {"id": node_id, **payload}
        nodes.append(payload)
        depths.append(depth)
        return node_id

    roots = [intern(expression) for expression in expressions]
    operation_count = sum(node["op"] in {"u", "d"} for node in nodes)
    return {
        "schema": DAG_SCHEMA,
        "nodes": nodes,
        "roots": roots,
        "operation_count": operation_count,
        "depth": max((depths[root] for root in roots), default=0),
    }


def evaluate_serialized_q_dag(
    dag: Mapping[str, object],
    arguments: Sequence[int],
) -> tuple[int, ...]:
    _require(dag.get("schema") == DAG_SCHEMA, "unsupported DAG schema")
    raw_nodes = dag.get("nodes")
    raw_roots = dag.get("roots")
    _require(isinstance(raw_nodes, list), "DAG nodes must be a list")
    _require(isinstance(raw_roots, list), "DAG roots must be a list")
    values: list[int] = []
    for expected_id, raw in enumerate(raw_nodes):
        _require(isinstance(raw, Mapping), "DAG node must be an object")
        _require(raw.get("id") == expected_id, "DAG node IDs are not canonical")
        op = raw.get("op")
        if op == "var":
            variable = raw.get("index")
            _require(isinstance(variable, int), "variable index must be integer")
            _require(0 <= variable < len(arguments), "variable outside input arity")
            value = arguments[variable]
        else:
            args = raw.get("args")
            _require(isinstance(args, list), "operation args must be a list")
            _require(
                all(
                    isinstance(arg, int) and 0 <= arg < expected_id for arg in args
                ),
                "DAG is not topologically ordered",
            )
            if op == "u":
                _require(len(args) == 1, "u has wrong arity")
                value = _q_unary(values[args[0]])
            elif op == "d":
                _require(len(args) == 3, "d has wrong arity")
                value = _q_discriminator(
                    values[args[0]], values[args[1]], values[args[2]]
                )
            else:
                raise ValueError(f"unknown DAG operation {op!r}")
        values.append(value)
    _require(
        all(
            isinstance(root, int) and 0 <= root < len(values) for root in raw_roots
        ),
        "invalid DAG root",
    )
    return tuple(values[root] for root in raw_roots)


def compile_q_strategy(
    game: FiniteSafetyGame,
    strategy: Mapping[Observation, Output],
) -> dict[str, object]:
    if not is_quackenbush_q(game.algebra):
        return {
            "status": "unsupported_algebra",
            "reason": "v1 original-signature backend supports only exact Quackenbush Q",
        }
    if set(strategy) != set(game.observations):
        return {
            "status": "unsupported_partial_strategy",
            "reason": "original-signature compilation requires a total table",
        }
    selectors = _selector_indices(game, strategy)
    if selectors is None:
        return {
            "status": "unsupported_nonconservative_table",
            "reason": "at least one output coordinate is not an observed input value",
        }

    expressions: list[Expr] = []
    backends: list[str] = []
    scalar_tables: list[dict[Observation, int]] = [
        {
            observation: int(strategy[observation][coordinate])
            for observation in game.observations
        }
        for coordinate in range(game.state_arity)
    ]
    for scalar_table, selector_table in zip(
        scalar_tables, selectors, strict=True
    ):
        backend, expression = _small_q_expression(
            game, scalar_table, selector_table
        )
        backends.append(backend)
        expressions.append(expression)

    replay_rows = 0
    for observation in game.observations:
        observed = tuple(
            evaluate_q_expr(expression, observation) for expression in expressions
        )
        _require(observed == strategy[observation], "compiled Q expression mismatch")
        replay_rows += 1

    dag = serialize_q_expressions(expressions)
    for observation in game.observations:
        _require(
            evaluate_serialized_q_dag(dag, observation) == strategy[observation],
            "serialized Q DAG mismatch",
        )

    return {
        "status": "compiled",
        "backend_per_output": backends,
        "selector_tables": [
            [
                {
                    "observation": _tuple_json(observation),
                    "index": selector[observation],
                }
                for observation in game.observations
            ]
            for selector in selectors
        ],
        "dag": dag,
        "replay_rows": replay_rows,
    }


def synthesize_model(
    model: Mapping[str, object],
    *,
    quasi_search: str = "bitset_nogood",
    exhaustive_state_limit: int = 16,
) -> dict[str, object]:
    """Run the complete practical v1 analysis and emit a certificate."""

    game, initial, name = game_from_model(model)
    ordinary = game.solve_ordinary()
    semi = game.solve_semi_primal()
    demi = game.solve_demi_semi_primal()

    quasi = _quasi_solution(
        game,
        initial,
        search=quasi_search,
        exhaustive_state_limit=exhaustive_state_limit,
    )

    modes = {
        "ordinary": _mode_result(
            game,
            initial,
            mode="ordinary",
            winning=ordinary.winning_states,
            strategy=ordinary.strategy,
        ),
        "semi_primal": _mode_result(
            game,
            initial,
            mode="semi_primal",
            winning=semi.winning_states,
            strategy=semi.strategy,
        ),
        "demi_semi_primal": _mode_result(
            game,
            initial,
            mode="demi_semi_primal",
            winning=demi.winning_states,
            strategy=demi.strategy,
        ),
    }

    selected: dict[str, object] | None = None
    compilation: dict[str, object]
    diagnostic: dict[str, object] | None = None

    if quasi is not None:
        domain, strategy = quasi
        modes["quasi_primal"] = {
            "mode": "quasi_primal",
            "initial_realizable": True,
            "winning_state_count": len(domain),
            "winning_states": _ordered_subset(game.states, domain),
            "strategy_rows": len(strategy),
        }
        selected = {
            "mode": "quasi_primal",
            "winning_states": _ordered_subset(game.states, domain),
            "strategy": _strategy_rows(game, strategy),
        }
        compilation = compile_q_strategy(game, strategy)
    else:
        modes["quasi_primal"] = {
            "mode": "quasi_primal",
            "initial_realizable": False,
            "winning_state_count": 0,
            "winning_states": [],
            "strategy_rows": 0,
        }
        compilation = {
            "status": "not_realizable",
            "reason": (
                "no internal-groupoid-compatible invariant domain contains "
                "the initials"
            ),
        }
        relaxation = (
            semi.winning_states
            if initial <= semi.winning_states
            else ordinary.winning_states
        )
        diagnostic = first_groupoid_conflict(game, relaxation)

    analysis = {
        "carrier_size": len(game.algebra.values),
        "operation_count": len(game.algebra.operations),
        "state_count": len(game.states),
        "input_count": len(game.inputs),
        "observation_count": len(game.observations),
        "safe_transition_count": len(game.safe_relation),
        "subalgebra_count": len(game.algebra.subalgebras()),
        "automorphism_count": len(game.algebra.automorphisms()),
        "internal_isomorphism_count": len(game.algebra.internal_isomorphisms()),
        "quasi_search": quasi_search,
    }

    certificate: dict[str, object] = {
        "schema": CERTIFICATE_SCHEMA,
        "model_name": name,
        "model_sha256": _sha256_json(model),
        "analysis": analysis,
        "modes": modes,
        "selected_controller": selected,
        "compilation": compilation,
        "diagnostic": diagnostic,
    }
    certificate["semantic_sha256"] = _sha256_json(certificate)
    return certificate


def verify_certificate(
    model: Mapping[str, object],
    certificate: Mapping[str, object],
    *,
    quasi_search: str | None = None,
    exhaustive_state_limit: int = 16,
) -> None:
    """Independently replay a certificate from its model."""

    _require(
        certificate.get("schema") == CERTIFICATE_SCHEMA,
        "bad certificate schema",
    )
    _require(
        certificate.get("model_sha256") == _sha256_json(model),
        "model hash mismatch",
    )
    analysis = certificate.get("analysis")
    _require(isinstance(analysis, Mapping), "missing analysis")
    selected_search = quasi_search or analysis.get("quasi_search")
    _require(isinstance(selected_search, str), "missing quasi search")

    expected = synthesize_model(
        model,
        quasi_search=selected_search,
        exhaustive_state_limit=exhaustive_state_limit,
    )
    _require(
        certificate.get("semantic_sha256") == expected.get("semantic_sha256"),
        "certificate semantic digest mismatch",
    )
    _require(dict(certificate) == expected, "certificate content mismatch")

    game, _initial, _name = game_from_model(model)
    compilation = certificate.get("compilation")
    selected = certificate.get("selected_controller")
    if (
        isinstance(compilation, Mapping)
        and compilation.get("status") == "compiled"
    ):
        _require(
            isinstance(selected, Mapping),
            "compiled certificate lacks controller",
        )
        strategy_rows = selected.get("strategy")
        _require(
            isinstance(strategy_rows, list),
            "controller strategy must be a list",
        )
        strategy = {
            tuple(row["observation"]): tuple(row["output"])
            for row in strategy_rows
            if isinstance(row, Mapping)
        }
        dag = compilation.get("dag")
        _require(isinstance(dag, Mapping), "compiled certificate lacks DAG")
        for observation in game.observations:
            _require(
                evaluate_serialized_q_dag(dag, observation)
                == strategy[observation],
                "certificate DAG replay failed",
            )

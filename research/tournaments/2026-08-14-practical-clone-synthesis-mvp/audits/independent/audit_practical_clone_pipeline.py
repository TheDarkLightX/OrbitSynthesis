#!/usr/bin/env python3
"""No-import audit of practical OrbitSynthesis model/certificate artifacts."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path

Q = (0, 1, 2)
Q0 = frozenset((0, 1))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: JSON root")
    return value


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    return (1, 0, 1)[x]


def verify_q_model(model: dict[str, object]) -> None:
    require(
        model["schema"] == "orbit-synthesis/finite-algebra-safety/v1",
        "model schema",
    )
    algebra = model["algebra"]
    require(algebra["carrier"] == [0, 1, 2], "carrier")
    operations = {row["name"]: row for row in algebra["operations"]}
    require(set(operations) == {"d", "u"}, "operation names")
    d_table = {
        tuple(row["args"]): row["value"] for row in operations["d"]["table"]
    }
    u_table = {
        tuple(row["args"]): row["value"] for row in operations["u"]["table"]
    }
    require(
        all(
            d_table[(x, y, z)] == d(x, y, z)
            for x, y, z in itertools.product(Q, repeat=3)
        ),
        "d table",
    )
    require(all(u_table[(x,)] == u(x) for x in Q), "u table")


def transition_map(
    model: dict[str, object],
) -> dict[tuple[int, ...], set[tuple[int, ...]]]:
    state_arity = model["game"]["state_arity"]
    result: dict[tuple[int, ...], set[tuple[int, ...]]] = {}
    for row in model["game"]["safe_transitions"]:
        observation = tuple(row["state"] + row["input"])
        output = tuple(row["output"])
        require(len(row["state"]) == state_arity, "state arity")
        result.setdefault(observation, set()).add(output)
    return result


def eval_dag(
    dag: dict[str, object],
    arguments: tuple[int, ...],
) -> tuple[int, ...]:
    require(
        dag["schema"] == "orbit-synthesis/original-signature-dag/v1",
        "DAG schema",
    )
    values = []
    operation_count = 0
    depths = []
    for expected, node in enumerate(dag["nodes"]):
        require(node["id"] == expected, "node ID")
        op = node["op"]
        if op == "var":
            value = arguments[node["index"]]
            depth = 0
        else:
            args = node["args"]
            require(all(0 <= child < expected for child in args), "DAG order")
            operation_count += 1
            depth = max(depths[child] for child in args) + 1
            if op == "u":
                require(len(args) == 1, "u arity")
                value = u(values[args[0]])
            elif op == "d":
                require(len(args) == 3, "d arity")
                value = d(values[args[0]], values[args[1]], values[args[2]])
            else:
                raise RuntimeError("unknown DAG op")
        values.append(value)
        depths.append(depth)
    roots = dag["roots"]
    require(operation_count == dag["operation_count"], "operation count")
    require(max(depths[root] for root in roots) == dag["depth"], "DAG depth")
    return tuple(values[root] for root in roots)


def audit_positive(
    model: dict[str, object],
    certificate: dict[str, object],
) -> dict[str, object]:
    verify_q_model(model)
    require(
        certificate["model_sha256"] == canonical_hash(model),
        "positive model hash",
    )
    require(
        certificate["compilation"]["status"] == "compiled",
        "positive compile status",
    )
    dag = certificate["compilation"]["dag"]
    relation = transition_map(model)
    strategy = {
        tuple(row["observation"]): tuple(row["output"])
        for row in certificate["selected_controller"]["strategy"]
    }
    observations = tuple(itertools.product(Q, repeat=3))
    require(set(strategy) == set(observations), "positive total strategy")
    rows = 0
    for observation in observations:
        observed = eval_dag(dag, observation)
        require(observed == strategy[observation], "positive DAG/table mismatch")
        require(relation[observation] == {observed}, "positive safety mismatch")
        require(observed == (d(*observation),), "positive discriminator mismatch")
        rows += 1
    require(
        dag["operation_count"] == 1 and dag["depth"] == 1,
        "positive profile",
    )

    mutant = deepcopy(dag)
    mutant["nodes"][-1]["args"] = [0, 1, 0]
    mutation_witness = None
    for observation in observations:
        bad = eval_dag(mutant, observation)
        if bad != strategy[observation]:
            mutation_witness = {
                "observation": list(observation),
                "mutated": list(bad),
                "expected": list(strategy[observation]),
            }
            break
    require(mutation_witness is not None, "positive mutation ineffective")
    return {
        "semantic_rows": rows,
        "operation_count": dag["operation_count"],
        "depth": dag["depth"],
        "mutation_witness": mutation_witness,
    }


def phi_value(value: int) -> int:
    require(value in Q0, "phi domain")
    return 1 - value


def phi_tuple(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(phi_value(value) for value in values)


def generated(values: tuple[int, ...]) -> frozenset[int]:
    return Q0 if all(value in Q0 for value in values) else frozenset(Q)


def negative_fixed_point(
    safe: set[tuple[tuple[int, ...], int, tuple[int, ...]]],
    *,
    generated_filter: bool,
) -> set[tuple[int, ...]]:
    states = set(itertools.product(Q, repeat=2))
    current = set(states)
    while True:
        nxt = set()
        for state in states:
            good = True
            for input_value in Q:
                observation = state + (input_value,)
                options = [
                    output
                    for output in current
                    if (state, input_value, output) in safe
                    and (
                        not generated_filter
                        or all(
                            value in generated(observation) for value in output
                        )
                    )
                ]
                if not options:
                    good = False
                    break
            if good:
                nxt.add(state)
        if nxt == current:
            return current
        current = nxt


def local_options(
    safe: set[tuple[tuple[int, ...], int, tuple[int, ...]]],
    domain: set[tuple[int, ...]],
    state: tuple[int, ...],
    input_value: int,
) -> list[tuple[int, ...]]:
    observation = state + (input_value,)
    return [
        output
        for output in itertools.product(Q, repeat=2)
        if output in domain
        and (state, input_value, output) in safe
        and all(value in generated(observation) for value in output)
    ]


def term_domain_feasible(
    safe: set[tuple[tuple[int, ...], int, tuple[int, ...]]],
    domain: set[tuple[int, ...]],
) -> bool:
    for state in domain:
        for input_value in Q:
            observation = state + (input_value,)
            if not all(value in Q0 for value in observation):
                if not local_options(safe, domain, state, input_value):
                    return False

    seen = set()
    for observation in itertools.product((0, 1), repeat=3):
        if observation in seen:
            continue
        other = phi_tuple(observation)
        seen.add(observation)
        seen.add(other)
        state = observation[:2]
        input_value = observation[2]
        other_state = other[:2]
        other_input = other[2]
        left_wins = state in domain
        right_wins = other_state in domain
        if left_wins:
            left = local_options(safe, domain, state, input_value)
        else:
            left = list(itertools.product(Q0, repeat=2))
        if right_wins:
            right = set(
                local_options(safe, domain, other_state, other_input)
            )
        else:
            right = set(itertools.product(Q0, repeat=2))
        if not any(phi_tuple(output) in right for output in left):
            return False
    return True


def audit_negative(
    model: dict[str, object],
    certificate: dict[str, object],
) -> dict[str, object]:
    verify_q_model(model)
    require(
        certificate["model_sha256"] == canonical_hash(model),
        "negative model hash",
    )
    safe = {
        (tuple(row["state"]), row["input"][0], tuple(row["output"]))
        for row in model["game"]["safe_transitions"]
    }
    require(len(safe) == 13, "negative relation census")
    ordinary = negative_fixed_point(safe, generated_filter=False)
    semi = negative_fixed_point(safe, generated_filter=True)
    expected = {(0, 0), (1, 0), (1, 1)}
    require(ordinary == expected, "ordinary fixed point")
    require(semi == expected, "semi fixed point")

    feasible = []
    states = list(itertools.product(Q, repeat=2))
    for mask in range(1 << len(states)):
        domain = {
            states[index]
            for index in range(len(states))
            if mask & (1 << index)
        }
        if term_domain_feasible(safe, domain):
            feasible.append(domain)
    require(feasible == [set()], "negative quasi-domain census")

    source = ((0, 0), 1)
    target = ((1, 1), 0)
    source_options = local_options(safe, expected, *source)
    target_options = local_options(safe, expected, *target)
    require(source_options == [(1, 0)], "source critical option")
    require(target_options == [(1, 0)], "target critical option")
    transported = phi_tuple(source_options[0])
    require(
        transported == (0, 1) and transported not in target_options,
        "transported-output contradiction",
    )

    require(
        certificate["compilation"]["status"] == "not_realizable",
        "negative certificate status",
    )
    require(
        certificate["diagnostic"]["kind"]
        == "groupoid_component_unsatisfiable",
        "negative diagnostic",
    )
    require(
        not certificate["modes"]["quasi_primal"]["initial_realizable"],
        "negative quasi claim",
    )
    return {
        "ordinary_winning_states": [list(state) for state in sorted(ordinary)],
        "semi_winning_states": [list(state) for state in sorted(semi)],
        "feasible_quasi_domains": len(feasible),
        "nonempty_quasi_domains": 0,
        "critical_source": list(source[0] + (source[1],)),
        "critical_target": list(target[0] + (target[1],)),
        "forced_output": list(source_options[0]),
        "transported_output": list(transported),
    }


def build_receipt(args: argparse.Namespace) -> dict[str, object]:
    positive_model = load(args.positive_model)
    positive_certificate = load(args.positive_certificate)
    negative_model = load(args.negative_model)
    negative_certificate = load(args.negative_certificate)
    result = {
        "schema": "orbit-synthesis/practical-clone-synthesis-independent/v1",
        "positive": audit_positive(positive_model, positive_certificate),
        "negative": audit_negative(negative_model, negative_certificate),
    }
    result["semantic_sha256"] = canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-model", type=Path, required=True)
    parser.add_argument("--positive-certificate", type=Path, required=True)
    parser.add_argument("--negative-model", type=Path, required=True)
    parser.add_argument("--negative-certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--expected", type=Path)
    args = parser.parse_args()
    result = build_receipt(args)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.expected:
        require(result == json.loads(args.expected.read_text()), "receipt drift")
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""No-import reconstruction of the state-search proof calculus."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import random


@dataclass(frozen=True)
class Candidate:
    forbidden: frozenset[int]
    edges: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class Component:
    candidates: tuple[Candidate, ...]


@dataclass(frozen=True)
class Model:
    state_count: int
    components: tuple[Component, ...]


@dataclass(frozen=True)
class Node:
    kind: str
    state_index: int | None = None
    include_child: int | None = None
    exclude_child: int | None = None
    component_index: int | None = None
    upper_bound: int | None = None


@dataclass(frozen=True)
class Certificate:
    weights: tuple[int, ...]
    required: int
    forbidden: int
    target_score: int | None
    target_mask: int | None
    root: int
    nodes: tuple[Node, ...]


def feasible(model: Model, mask: int) -> bool:
    for component in model.components:
        accepted = False
        for candidate in component.candidates:
            if any(mask & (1 << state) for state in candidate.forbidden):
                continue
            if any(
                (mask & (1 << source)) and not (mask & (1 << target))
                for source, target in candidate.edges
            ):
                continue
            accepted = True
            break
        if not accepted:
            return False
    return True


def score(mask: int, weights: tuple[int, ...]) -> int:
    return sum(
        weight
        for index, weight in enumerate(weights)
        if mask & (1 << index)
    )


def partial_viable(
    candidate: Candidate,
    included: int,
    excluded: int,
) -> bool:
    if any(included & (1 << state) for state in candidate.forbidden):
        return False
    return all(
        not (included & (1 << source)) or not (excluded & (1 << target))
        for source, target in candidate.edges
    )


def conflict(model: Model, included: int, excluded: int) -> int | None:
    for index, component in enumerate(model.components):
        if not any(
            partial_viable(candidate, included, excluded)
            for candidate in component.candidates
        ):
            return index
    return None


def upper(
    model: Model,
    weights: tuple[int, ...],
    included: int,
    excluded: int,
) -> int:
    all_mask = (1 << model.state_count) - 1
    return score(included, weights) + sum(
        max(0, weights[index])
        for index in range(model.state_count)
        if (all_mask & ~(included | excluded)) & (1 << index)
    )


def impacts(model: Model) -> tuple[int, ...]:
    values = [0] * model.state_count
    for component in model.components:
        for candidate in component.candidates:
            for state in candidate.forbidden:
                values[state] += 4
            for source, target in candidate.edges:
                values[source] += 1
                values[target] += 1
    return tuple(values)


def generate(
    model: Model,
    weights: tuple[int, ...],
    target_mask: int | None,
    required: int = 0,
    forbidden: int = 0,
    max_nodes: int = 100_000,
) -> Certificate:
    all_mask = (1 << model.state_count) - 1
    target_score = None if target_mask is None else score(target_mask, weights)
    impact = impacts(model)
    nodes: list[Node | None] = []

    def build(included: int, excluded: int) -> int:
        if len(nodes) >= max_nodes:
            raise RuntimeError("certificate limit")
        component = conflict(model, included, excluded)
        if component is not None:
            index = len(nodes)
            nodes.append(Node("conflict", component_index=component))
            return index
        bound = upper(model, weights, included, excluded)
        if target_score is not None and bound <= target_score:
            index = len(nodes)
            nodes.append(Node("bound", upper_bound=bound))
            return index
        if included | excluded == all_mask:
            raise RuntimeError("false certificate claim")
        state = max(
            (
                index
                for index in range(model.state_count)
                if not (included | excluded) & (1 << index)
            ),
            key=lambda index: (
                impact[index],
                abs(weights[index]),
                weights[index],
                -index,
            ),
        )
        node_index = len(nodes)
        nodes.append(None)
        include_child = build(included | (1 << state), excluded)
        exclude_child = build(included, excluded | (1 << state))
        nodes[node_index] = Node(
            "branch",
            state_index=state,
            include_child=include_child,
            exclude_child=exclude_child,
        )
        return node_index

    root = build(required, forbidden)
    completed = tuple(node for node in nodes if node is not None)
    if len(completed) != len(nodes):
        raise AssertionError("incomplete proof tree")
    return Certificate(
        weights=weights,
        required=required,
        forbidden=forbidden,
        target_score=target_score,
        target_mask=target_mask,
        root=root,
        nodes=completed,
    )


def verify(model: Model, certificate: Certificate) -> bool:
    all_mask = (1 << model.state_count) - 1
    if len(certificate.weights) != model.state_count:
        return False
    if certificate.required & certificate.forbidden:
        return False
    if certificate.target_score is None:
        if certificate.target_mask is not None:
            return False
    else:
        if certificate.target_mask is None:
            return False
        if score(certificate.target_mask, certificate.weights) != certificate.target_score:
            return False
        if certificate.required & ~certificate.target_mask:
            return False
        if certificate.forbidden & certificate.target_mask:
            return False
        if not feasible(model, certificate.target_mask):
            return False
    if not certificate.nodes or not 0 <= certificate.root < len(certificate.nodes):
        return False

    seen: set[int] = set()
    stack = [(certificate.root, certificate.required, certificate.forbidden)]
    while stack:
        node_index, included, excluded = stack.pop()
        if node_index in seen or not 0 <= node_index < len(certificate.nodes):
            return False
        seen.add(node_index)
        node = certificate.nodes[node_index]
        component = conflict(model, included, excluded)

        if node.kind == "conflict":
            if node.component_index is None:
                return False
            if not 0 <= node.component_index < len(model.components):
                return False
            if any(
                partial_viable(candidate, included, excluded)
                for candidate in model.components[node.component_index].candidates
            ):
                return False
            continue

        if node.kind == "bound":
            if certificate.target_score is None:
                return False
            expected = upper(model, certificate.weights, included, excluded)
            if node.upper_bound != expected or expected > certificate.target_score:
                return False
            continue

        if node.kind != "branch" or component is not None:
            return False
        if certificate.target_score is not None and upper(
            model,
            certificate.weights,
            included,
            excluded,
        ) <= certificate.target_score:
            return False
        state = node.state_index
        if state is None or not 0 <= state < model.state_count:
            return False
        bit = 1 << state
        if (included | excluded) & bit:
            return False
        if node.include_child is None or node.exclude_child is None:
            return False
        stack.append((node.exclude_child, included, excluded | bit))
        stack.append((node.include_child, included | bit, excluded))

    return len(seen) == len(certificate.nodes)


def antichain_model(pair_count: int) -> Model:
    state_count = 2 * pair_count + 2
    components = [
        Component((Candidate(frozenset({0}), frozenset()),))
    ]
    for pair in range(pair_count):
        left = 1 + 2 * pair
        right = left + 1
        components.append(
            Component(
                (
                    Candidate(frozenset({right}), frozenset()),
                    Candidate(frozenset({left}), frozenset()),
                )
            )
        )
    return Model(state_count, tuple(components))


def antichain_case(pair_count: int) -> tuple[Model, Certificate, dict[str, int]]:
    model = antichain_model(pair_count)
    weights = [1] * model.state_count
    target = 1 << (model.state_count - 1)
    for pair in range(pair_count):
        preferred = 1 + 2 * pair
        weights[preferred] += 1 << (pair + 1)
        target |= 1 << preferred
    weight_tuple = tuple(weights)
    certificate = generate(model, weight_tuple, target)
    if not verify(model, certificate):
        raise AssertionError("antichain certificate failed")
    feasible_masks = [
        mask
        for mask in range(1 << model.state_count)
        if feasible(model, mask)
    ]
    optimum = max(score(mask, weight_tuple) for mask in feasible_masks)
    optimum_count = sum(
        score(mask, weight_tuple) == optimum
        for mask in feasible_masks
    )
    return model, certificate, {
        "pairs": pair_count,
        "states": model.state_count,
        "feasible_domains": len(feasible_masks),
        "optimum_score": optimum,
        "optimum_count": optimum_count,
        "nodes": len(certificate.nodes),
        "conflicts": sum(node.kind == "conflict" for node in certificate.nodes),
        "bounds": sum(node.kind == "bound" for node in certificate.nodes),
    }


def random_corpus() -> tuple[dict[str, object], list[tuple[object, ...]]]:
    rng = random.Random(20260814)
    rows = []
    optimal = 0
    infeasible = 0
    node_total = 0
    node_max = 0

    for case in range(240):
        state_count = rng.randrange(3, 9)
        components = []
        for _ in range(rng.randrange(1, 5)):
            candidates = []
            for _ in range(rng.randrange(1, 4)):
                forbidden = frozenset(
                    state
                    for state in range(state_count)
                    if rng.random() < 0.18
                )
                edges = set()
                for _ in range(rng.randrange(0, 4)):
                    source = rng.randrange(state_count)
                    target = rng.randrange(state_count)
                    if source != target:
                        edges.add((source, target))
                candidates.append(Candidate(forbidden, frozenset(edges)))
            components.append(Component(tuple(candidates)))
        model = Model(state_count, tuple(components))
        weights = tuple(rng.randrange(-3, 6) for _ in range(state_count))
        required = 0
        forbidden = 0
        for state in range(state_count):
            draw = rng.random()
            if draw < 0.08:
                required |= 1 << state
            elif draw < 0.16:
                forbidden |= 1 << state

        feasible_masks = [
            mask
            for mask in range(1 << state_count)
            if not (required & ~mask)
            and not (forbidden & mask)
            and feasible(model, mask)
        ]
        if feasible_masks:
            best = max(score(mask, weights) for mask in feasible_masks)
            target = min(
                mask
                for mask in feasible_masks
                if score(mask, weights) == best
            )
            certificate = generate(
                model,
                weights,
                target,
                required,
                forbidden,
            )
            optimal += 1
            claim = ("optimal", best, target)
        else:
            certificate = generate(
                model,
                weights,
                None,
                required,
                forbidden,
            )
            infeasible += 1
            claim = ("infeasible", None, None)
        if not verify(model, certificate):
            raise AssertionError("random certificate failed")
        node_total += len(certificate.nodes)
        node_max = max(node_max, len(certificate.nodes))
        rows.append(
            (
                case,
                state_count,
                len(components),
                claim[0],
                claim[1],
                len(certificate.nodes),
            )
        )

    return {
        "cases": len(rows),
        "optimal": optimal,
        "infeasible": infeasible,
        "certificate_nodes_total": node_total,
        "certificate_nodes_max": node_max,
        "rows_sha256": hashlib.sha256(
            json.dumps(rows, separators=(",", ":")).encode()
        ).hexdigest(),
    }, rows


def main() -> int:
    first_model, first_certificate, first = antichain_case(2)
    _second_model, _second_certificate, second = antichain_case(6)

    infeasible_model = Model(
        3,
        (
            Component(
                (
                    Candidate(frozenset({0}), frozenset()),
                    Candidate(frozenset({1}), frozenset()),
                )
            ),
        ),
    )
    infeasible_certificate = generate(
        infeasible_model,
        (1, 2, 3),
        None,
        required=3,
    )
    if not verify(infeasible_model, infeasible_certificate):
        raise AssertionError("infeasibility certificate failed")

    mutations = {}
    bound_index = next(
        index
        for index, node in enumerate(first_certificate.nodes)
        if node.kind == "bound"
    )
    nodes = list(first_certificate.nodes)
    nodes[bound_index] = replace(
        nodes[bound_index],
        upper_bound=(nodes[bound_index].upper_bound or 0) + 1,
    )
    mutations["wrong_bound"] = not verify(
        first_model,
        replace(first_certificate, nodes=tuple(nodes)),
    )

    conflict_index = next(
        index
        for index, node in enumerate(first_certificate.nodes)
        if node.kind == "conflict"
    )
    nodes = list(first_certificate.nodes)
    nodes[conflict_index] = replace(
        nodes[conflict_index],
        component_index=len(first_model.components),
    )
    mutations["bad_component"] = not verify(
        first_model,
        replace(first_certificate, nodes=tuple(nodes)),
    )

    branch_index = next(
        index
        for index, node in enumerate(first_certificate.nodes)
        if node.kind == "branch"
    )
    nodes = list(first_certificate.nodes)
    nodes[branch_index] = replace(
        nodes[branch_index],
        include_child=branch_index,
    )
    mutations["cycle"] = not verify(
        first_model,
        replace(first_certificate, nodes=tuple(nodes)),
    )
    mutations["wrong_score"] = not verify(
        first_model,
        replace(
            first_certificate,
            target_score=(first_certificate.target_score or 0) + 1,
        ),
    )
    if not all(mutations.values()):
        raise AssertionError("one mutation survived")

    random_summary, _rows = random_corpus()
    result = {
        "schema": "orbit-synthesis/state-search-independent/v1",
        "antichain": [first, second],
        "infeasible": {
            "states": 3,
            "required_mask": 3,
            "nodes": len(infeasible_certificate.nodes),
            "conflicts": sum(
                node.kind == "conflict"
                for node in infeasible_certificate.nodes
            ),
        },
        "random": random_summary,
        "mutations": mutations,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

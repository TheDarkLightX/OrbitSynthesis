"""Exact weighted optimization over clone-constrained safety domains.

The existing pointed-domain search enumerates every inclusion-maximal feasible
domain.  That is the right semantic object for antichain theorems, but it is
not the right practical interface when a user wants one best domain under a
utility function.

This module reuses the exact bitset propagation and pointed-class rules, but
runs a branch-and-bound search for one lexicographically optimal feasible
domain.  It supports:

* arbitrary integral state weights;
* required and forbidden states;
* deterministic tie-breaking by larger cardinality and then larger canonical
  state mask;
* optional action preferences after the domain is fixed;
* replayable search digests and source-independent exhaustive verification on
  bounded instances.

The optimization is exact.  It does not assume that feasible domains are
closed under union or that a greatest domain exists.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Hashable, Iterable, Mapping

from .domain_search_bitset import BitsetNogoodDomainSearch
from .domain_search_types import DomainNogood, Observation, Output, State

Value = Hashable
ActionPreference = Mapping[tuple[Observation, Output], int]


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=repr,
    ).encode("utf-8")


def _stable_items(values: Mapping[object, int]) -> tuple[tuple[object, int], ...]:
    return tuple(sorted(values.items(), key=lambda item: repr(item[0])))


@dataclass(frozen=True, order=True)
class WeightedObjective:
    """Lexicographic domain objective.

    The primary objective is the exact sum of state weights.  Equal scores are
    resolved by larger domains and then by the larger canonical bit mask in
    the game state's deterministic order.
    """

    score: int
    cardinality: int
    mask: int


@dataclass(frozen=True)
class WeightedDomainStats:
    nodes: int
    conflict_prunes: int
    bound_prunes: int
    complete_leaves: int
    feasible_leaves: int
    incumbent_updates: int
    max_depth: int
    propagated_includes: int
    propagated_excludes: int
    learned_nogoods: int
    learned_nogood_hits: int


@dataclass(frozen=True)
class WeightedDomainResult:
    """One exact optimal domain, strategy, and replay certificate."""

    domain: frozenset[State]
    strategy_items: tuple[tuple[Observation, Output], ...]
    objective: WeightedObjective
    action_preference_score: int
    state_order: tuple[State, ...]
    weights: tuple[int, ...]
    required_states: frozenset[State]
    forbidden_states: frozenset[State]
    weight_digest: str
    preference_digest: str
    trace_sha256: str
    nogoods: tuple[DomainNogood, ...]
    stats: WeightedDomainStats

    @property
    def strategy(self) -> dict[Observation, Output]:
        return dict(self.strategy_items)

    @property
    def semantic_sha256(self) -> str:
        payload = {
            "state_order": [list(state) for state in self.state_order],
            "weights": list(self.weights),
            "required": [list(state) for state in self.state_order if state in self.required_states],
            "forbidden": [list(state) for state in self.state_order if state in self.forbidden_states],
            "domain": [list(state) for state in self.state_order if state in self.domain],
            "objective": {
                "score": self.objective.score,
                "cardinality": self.objective.cardinality,
                "mask": self.objective.mask,
            },
            "action_preference_score": self.action_preference_score,
            "weight_digest": self.weight_digest,
            "preference_digest": self.preference_digest,
            "trace_sha256": self.trace_sha256,
            "strategy": [
                {"observation": list(observation), "output": list(output)}
                for observation, output in self.strategy_items
            ],
        }
        return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


class WeightedBitsetDomainOptimizer(BitsetNogoodDomainSearch):
    """Branch-and-bound optimizer over exact pointed-domain constraints."""

    def _weight_tuple(
        self,
        state_weights: Mapping[State, int] | None,
        default_weight: int,
    ) -> tuple[int, ...]:
        supplied = {} if state_weights is None else dict(state_weights)
        unknown = set(supplied) - set(self.states)
        if unknown:
            raise ValueError(f"state weight outside game: {min(unknown, key=repr)!r}")
        if not isinstance(default_weight, int):
            raise TypeError("default_weight must be an integer")
        if any(not isinstance(weight, int) for weight in supplied.values()):
            raise TypeError("all state weights must be integers")
        return tuple(supplied.get(state, default_weight) for state in self.states)

    @staticmethod
    def _mask_score(mask: int, weights: tuple[int, ...]) -> int:
        score = 0
        remaining = mask
        while remaining:
            low = remaining & -remaining
            score += weights[low.bit_length() - 1]
            remaining ^= low
        return score

    @classmethod
    def _objective(cls, mask: int, weights: tuple[int, ...]) -> WeightedObjective:
        return WeightedObjective(
            score=cls._mask_score(mask, weights),
            cardinality=mask.bit_count(),
            mask=mask,
        )

    def _optimistic_objective(
        self,
        included: int,
        excluded: int,
        weights: tuple[int, ...],
    ) -> WeightedObjective:
        """A valid lexicographic upper bound for every completion.

        Every positive or zero-weight undecided state is included; every
        negative-weight undecided state is excluded.  This maximizes score,
        then cardinality, then mask without using any feasibility assumption.
        """

        optimistic = included
        undecided = self.all_mask & ~(included | excluded)
        remaining = undecided
        while remaining:
            low = remaining & -remaining
            index = low.bit_length() - 1
            if weights[index] >= 0:
                optimistic |= low
            remaining ^= low
        return self._objective(optimistic, weights)

    def _weighted_branch_bit(
        self,
        included: int,
        excluded: int,
        weights: tuple[int, ...],
    ) -> int:
        undecided = self.all_mask & ~(included | excluded)
        index = max(
            (index for index in range(self.n) if undecided & (1 << index)),
            key=lambda candidate: (
                abs(weights[candidate]),
                self._impact[candidate],
                weights[candidate],
                -candidate,
            ),
        )
        return 1 << index

    def _preferred_strategy_for_mask(
        self,
        domain: int,
        preferences: ActionPreference,
    ) -> tuple[dict[Observation, Output], int] | None:
        """Choose the best action table independently in every pointed class."""

        assignment: dict[Observation, Output] = {}
        total_preference = 0

        for pointed in self.classes:
            source = self._pointed_by_rep[pointed.representative]
            transports = self.kernel.pointed_transports[pointed.representative]
            best_local: dict[Observation, Output] | None = None
            best_score: int | None = None

            for rule in pointed.rules:
                if not self._valid(rule, domain):
                    continue
                local: dict[Observation, Output] = {}
                score = 0
                for observation in source.observations:
                    mapping = transports[observation]
                    output = tuple(mapping[value] for value in rule.seed)
                    local[observation] = output
                    score += preferences.get((observation, output), 0)
                if best_score is None or score > best_score:
                    best_score = score
                    best_local = local

            if best_local is None or best_score is None:
                return None
            assignment.update(best_local)
            total_preference += best_score

        if set(assignment) != set(self.game.observations):
            raise AssertionError("preferred strategy was not total")
        return assignment, total_preference

    def optimize(
        self,
        *,
        state_weights: Mapping[State, int] | None = None,
        default_weight: int = 1,
        required_states: Iterable[State] = (),
        forbidden_states: Iterable[State] = (),
        action_preferences: ActionPreference | None = None,
        learn_nogoods: bool = True,
        learn_propagation_nogoods: bool = False,
    ) -> WeightedDomainResult:
        """Return one exact lexicographically optimal feasible domain.

        Domain utility is optimized first.  ``action_preferences`` then select
        the best total strategy for that already determined domain; they do not
        alter which domain wins the primary objective.
        """

        weights = self._weight_tuple(state_weights, default_weight)
        required_set = frozenset(required_states)
        forbidden_set = frozenset(forbidden_states)
        required = self._mask(required_set)
        forbidden = self._mask(forbidden_set)
        if required & forbidden:
            raise ValueError("required and forbidden states overlap")

        preferences = {} if action_preferences is None else dict(action_preferences)
        if any(not isinstance(value, int) for value in preferences.values()):
            raise TypeError("all action preferences must be integers")

        weight_digest = hashlib.sha256(
            _canonical_bytes(
                [(repr(state), weight) for state, weight in zip(self.states, weights)]
            )
        ).hexdigest()
        preference_digest = hashlib.sha256(
            _canonical_bytes(
                [(repr(key), value) for key, value in _stable_items(preferences)]
            )
        ).hexdigest()

        self._nogoods = []
        self.stats.nodes = 0
        self.stats.complete_leaves = 0
        self.stats.feasible_leaves = 0
        self.stats.class_conflicts = 0
        self.stats.learned_nogoods = 0
        self.stats.learned_nogood_hits = 0
        self.stats.dominance_prunes = 0
        self.stats.propagated_includes = 0
        self.stats.propagated_excludes = 0
        self.stats.max_depth = 0

        trace = hashlib.sha256()
        conflict_prunes = 0
        bound_prunes = 0
        incumbent_updates = 0
        best_objective: WeightedObjective | None = None
        best_mask: int | None = None
        best_strategy: dict[Observation, Output] | None = None
        best_action_score = 0

        def event(kind: str, included: int, excluded: int, **extra: object) -> None:
            row = {"kind": kind, "included": included, "excluded": excluded, **extra}
            trace.update(_canonical_bytes(row))
            trace.update(b"\n")

        def dfs(included: int, excluded: int, depth: int) -> None:
            nonlocal conflict_prunes, bound_prunes, incumbent_updates
            nonlocal best_objective, best_mask, best_strategy, best_action_score

            self.stats.nodes += 1
            self.stats.max_depth = max(self.stats.max_depth, depth)
            included, excluded, conflict = self._propagate(
                included,
                excluded,
                learn=learn_nogoods,
                learn_propagation_nogoods=learn_propagation_nogoods,
            )
            if conflict is not None:
                conflict_prunes += 1
                event(
                    "conflict",
                    included,
                    excluded,
                    representative=repr(conflict.class_representative),
                )
                return

            optimistic = self._optimistic_objective(included, excluded, weights)
            if best_objective is not None and optimistic <= best_objective:
                bound_prunes += 1
                event(
                    "bound",
                    included,
                    excluded,
                    upper=(optimistic.score, optimistic.cardinality, optimistic.mask),
                    incumbent=(
                        best_objective.score,
                        best_objective.cardinality,
                        best_objective.mask,
                    ),
                )
                return

            if (included | excluded) == self.all_mask:
                self.stats.complete_leaves += 1
                selected = self._preferred_strategy_for_mask(
                    included,
                    preferences,
                )
                if selected is None:
                    raise AssertionError("complete propagated mask is infeasible")
                strategy, action_score = selected
                self.stats.feasible_leaves += 1
                objective = self._objective(included, weights)
                event(
                    "solution",
                    included,
                    excluded,
                    objective=(objective.score, objective.cardinality, objective.mask),
                    action_preference_score=action_score,
                )
                if best_objective is None or objective > best_objective:
                    best_objective = objective
                    best_mask = included
                    best_strategy = strategy
                    best_action_score = action_score
                    incumbent_updates += 1
                elif objective == best_objective and action_score > best_action_score:
                    # The canonical mask already fixes the domain.  Action
                    # preferences choose among valid total tables on that mask.
                    best_strategy = strategy
                    best_action_score = action_score
                    incumbent_updates += 1
                return

            bit = self._weighted_branch_bit(included, excluded, weights)
            index = bit.bit_length() - 1
            event("branch", included, excluded, bit=index, weight=weights[index])
            if weights[index] >= 0:
                dfs(included | bit, excluded, depth + 1)
                dfs(included, excluded | bit, depth + 1)
            else:
                dfs(included, excluded | bit, depth + 1)
                dfs(included | bit, excluded, depth + 1)

        dfs(required, forbidden, 0)

        if best_objective is None or best_mask is None or best_strategy is None:
            raise ValueError("no feasible clone-compatible domain exists")

        strategy_items = tuple(
            (observation, best_strategy[observation])
            for observation in self.game.observations
        )
        result_stats = WeightedDomainStats(
            nodes=self.stats.nodes,
            conflict_prunes=conflict_prunes,
            bound_prunes=bound_prunes,
            complete_leaves=self.stats.complete_leaves,
            feasible_leaves=self.stats.feasible_leaves,
            incumbent_updates=incumbent_updates,
            max_depth=self.stats.max_depth,
            propagated_includes=self.stats.propagated_includes,
            propagated_excludes=self.stats.propagated_excludes,
            learned_nogoods=self.stats.learned_nogoods,
            learned_nogood_hits=self.stats.learned_nogood_hits,
        )
        return WeightedDomainResult(
            domain=self._frozenset(best_mask),
            strategy_items=strategy_items,
            objective=best_objective,
            action_preference_score=best_action_score,
            state_order=self.states,
            weights=weights,
            required_states=required_set,
            forbidden_states=forbidden_set,
            weight_digest=weight_digest,
            preference_digest=preference_digest,
            trace_sha256=trace.hexdigest(),
            nogoods=tuple(row[2] for row in self._nogoods),
            stats=result_stats,
        )


def optimize_weighted_domain(
    kernel: object,
    *,
    state_weights: Mapping[State, int] | None = None,
    default_weight: int = 1,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    action_preferences: ActionPreference | None = None,
    learn_nogoods: bool = True,
    learn_propagation_nogoods: bool = False,
) -> WeightedDomainResult:
    """Convenience entry point for exact weighted domain optimization."""

    return WeightedBitsetDomainOptimizer(kernel).optimize(
        state_weights=state_weights,
        default_weight=default_weight,
        required_states=required_states,
        forbidden_states=forbidden_states,
        action_preferences=action_preferences,
        learn_nogoods=learn_nogoods,
        learn_propagation_nogoods=learn_propagation_nogoods,
    )


def verify_weighted_domain_result(
    kernel: object,
    result: WeightedDomainResult,
    *,
    state_weights: Mapping[State, int] | None = None,
    default_weight: int = 1,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    action_preferences: ActionPreference | None = None,
    exhaustive_state_limit: int = 18,
) -> bool:
    """Verify feasibility and exact optimality.

    Small instances are checked by an independent exhaustive mask scan.  Larger
    instances are checked by deterministic branch-and-bound replay.  The latter
    is a replay certificate, not an independent proof implementation.
    """

    engine = WeightedBitsetDomainOptimizer(kernel)
    try:
        weights = engine._weight_tuple(state_weights, default_weight)
        required_set = frozenset(required_states)
        forbidden_set = frozenset(forbidden_states)
        required = engine._mask(required_set)
        forbidden = engine._mask(forbidden_set)
        domain_mask = engine._mask(result.domain)
    except (TypeError, ValueError):
        return False

    if required & forbidden:
        return False
    if result.state_order != engine.states or result.weights != weights:
        return False
    if result.required_states != required_set or result.forbidden_states != forbidden_set:
        return False
    if required & ~domain_mask or forbidden & domain_mask:
        return False
    if result.objective != engine._objective(domain_mask, weights):
        return False

    preferences = {} if action_preferences is None else dict(action_preferences)
    preferred = engine._preferred_strategy_for_mask(domain_mask, preferences)
    if preferred is None:
        return False
    strategy, action_score = preferred
    expected_items = tuple(
        (observation, strategy[observation])
        for observation in engine.game.observations
    )
    if result.strategy_items != expected_items:
        return False
    if result.action_preference_score != action_score:
        return False

    if engine.n <= exhaustive_state_limit:
        best: WeightedObjective | None = None
        for mask in range(1 << engine.n):
            if required & ~mask or forbidden & mask:
                continue
            if not engine.is_feasible_mask(mask):
                continue
            objective = engine._objective(mask, weights)
            if best is None or objective > best:
                best = objective
        return best == result.objective

    replay = engine.optimize(
        state_weights=state_weights,
        default_weight=default_weight,
        required_states=required_set,
        forbidden_states=forbidden_set,
        action_preferences=preferences,
    )
    return (
        replay.objective == result.objective
        and replay.domain == result.domain
        and replay.strategy_items == result.strategy_items
        and replay.trace_sha256 == result.trace_sha256
    )

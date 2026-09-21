"""Object/set exact nogood search over pointed seed rules."""
from __future__ import annotations

from itertools import combinations
from typing import Any, Iterable

from .domain_search_types import (
    DomainNogood, DomainSearchResult, DomainSearchStats, Observation,
    Output, PointedClassRules, SeedRule, State,
)

class CompiledPointedRules:
    """Compile pointed seeds to exact state-domain implication rules."""

    def __init__(self, kernel: Any) -> None:
        self.kernel = kernel
        self.game = kernel.game
        self.states = tuple(self.game.states)
        self._state_index = {state: index for index, state in enumerate(self.states)}
        self.class_rules = self._compile_class_rules()
        self._impact = self._compile_impact_scores()
        self._nogoods: list[DomainNogood] = []
        self.stats = DomainSearchStats()

    # ------------------------------------------------------------------
    # Compilation
    # ------------------------------------------------------------------

    def _compile_class_rules(self) -> tuple[PointedClassRules, ...]:
        compiled: list[PointedClassRules] = []
        for pointed in self.kernel.pointed_classes:
            transports = self.kernel.pointed_transports[pointed.representative]
            rules: list[SeedRule] = []
            for seed in self.kernel.seed_vectors[pointed.representative]:
                unsafe: set[State] = set()
                requirements: dict[State, set[State]] = {}
                for observation in pointed.observations:
                    state, input_value = self.game.split_observation(observation)
                    mapping = transports[observation]
                    output = tuple(mapping[value] for value in seed)
                    if not self.game.is_safe(state, input_value, output):
                        unsafe.add(state)
                    else:
                        requirements.setdefault(state, set()).add(output)
                requirement_items = tuple(
                    (
                        state,
                        tuple(
                            target
                            for target in self.states
                            if target in requirements.get(state, set())
                        ),
                    )
                    for state in self.states
                    if state in requirements
                )
                rules.append(
                    SeedRule(
                        seed=tuple(seed),
                        unsafe_sources=frozenset(unsafe),
                        requirement_items=requirement_items,
                    )
                )
            if not rules:
                raise AssertionError("every pointed class must have at least one seed")
            compiled.append(
                PointedClassRules(
                    representative=pointed.representative,
                    observations=pointed.observations,
                    rules=tuple(rules),
                )
            )
        return tuple(compiled)

    def _compile_impact_scores(self) -> dict[State, int]:
        score = {state: 0 for state in self.states}
        for pointed in self.class_rules:
            for rule in pointed.rules:
                for state in rule.unsafe_sources:
                    score[state] += 3
                for source, targets in rule.requirement_items:
                    score[source] += 2 + len(targets)
                    for target in targets:
                        score[target] += 1
        return score

    # ------------------------------------------------------------------
    # Seed and class semantics
    # ------------------------------------------------------------------

    @staticmethod
    def _requirements_for(
        rule: SeedRule,
        included: frozenset[State],
    ) -> frozenset[State]:
        requirements = rule.requirements
        out: set[State] = set()
        for source in included:
            out.update(requirements.get(source, frozenset()))
        return frozenset(out)

    @staticmethod
    def _seed_viable_partial(
        rule: SeedRule,
        included: frozenset[State],
        excluded: frozenset[State],
    ) -> bool:
        if rule.unsafe_sources & included:
            return False
        requirements = rule.requirements
        return all(
            not bool(requirements.get(source, frozenset()) & excluded)
            for source in included
        )

    @staticmethod
    def _seed_valid_complete(
        rule: SeedRule,
        domain: frozenset[State],
    ) -> bool:
        if rule.unsafe_sources & domain:
            return False
        requirements = rule.requirements
        return all(
            requirements.get(source, frozenset()) <= domain
            for source in domain
        )

    def viable_rules(
        self,
        pointed: PointedClassRules,
        included: Iterable[State],
        excluded: Iterable[State],
    ) -> tuple[SeedRule, ...]:
        inc = frozenset(included)
        exc = frozenset(excluded)
        return tuple(
            rule
            for rule in pointed.rules
            if self._seed_viable_partial(rule, inc, exc)
        )

    def is_feasible(self, domain: Iterable[State]) -> bool:
        chosen = frozenset(domain)
        return all(
            any(self._seed_valid_complete(rule, chosen) for rule in pointed.rules)
            for pointed in self.class_rules
        )

    def strategy_for_domain(
        self,
        domain: Iterable[State],
    ) -> dict[Observation, Output] | None:
        chosen_domain = frozenset(domain)
        assignment: dict[Observation, Output] = {}
        pointed_by_rep = {
            pointed.representative: pointed
            for pointed in self.kernel.pointed_classes
        }
        for class_rules in self.class_rules:
            selected = next(
                (
                    rule
                    for rule in class_rules.rules
                    if self._seed_valid_complete(rule, chosen_domain)
                ),
                None,
            )
            if selected is None:
                return None
            pointed = pointed_by_rep[class_rules.representative]
            transports = self.kernel.pointed_transports[class_rules.representative]
            for observation in pointed.observations:
                mapping = transports[observation]
                assignment[observation] = tuple(
                    mapping[value] for value in selected.seed
                )
        if set(assignment) != set(self.game.observations):
            raise AssertionError("nogood solver did not reconstruct a total table")
        return assignment

    # ------------------------------------------------------------------
    # Conflict certificates
    # ------------------------------------------------------------------

    def _class_conflict_holds(
        self,
        pointed: PointedClassRules,
        included: frozenset[State],
        excluded: frozenset[State],
    ) -> bool:
        return not any(
            self._seed_viable_partial(rule, included, excluded)
            for rule in pointed.rules
        )

    def _greedy_irredundant_conflict(
        self,
        pointed: PointedClassRules,
        included: frozenset[State],
        excluded: frozenset[State],
    ) -> DomainNogood:
        if not self._class_conflict_holds(pointed, included, excluded):
            raise ValueError("cannot minimize a non-conflicting assignment")
        inc = set(included)
        exc = set(excluded)

        # Repeat deletion because removing one literal can make another
        # redundant.  Carrier order makes the receipt deterministic.
        changed = True
        while changed:
            changed = False
            for state in self.states:
                if state not in inc:
                    continue
                candidate = frozenset(inc - {state})
                if self._class_conflict_holds(pointed, candidate, frozenset(exc)):
                    inc.remove(state)
                    changed = True
            for state in self.states:
                if state not in exc:
                    continue
                candidate = frozenset(exc - {state})
                if self._class_conflict_holds(pointed, frozenset(inc), candidate):
                    exc.remove(state)
                    changed = True

        return DomainNogood(
            include=frozenset(inc),
            exclude=frozenset(exc),
            class_representative=pointed.representative,
            killed_seed_count=len(pointed.rules),
        )

    def exact_minimum_conflict(
        self,
        pointed: PointedClassRules,
        included: Iterable[State],
        excluded: Iterable[State],
    ) -> DomainNogood:
        """Return a cardinality-minimum conflict inside one supplied assignment.

        This exponential routine is a validation oracle for Morph minimality,
        not the production learning path.
        """

        inc = frozenset(included)
        exc = frozenset(excluded)
        if not self._class_conflict_holds(pointed, inc, exc):
            raise ValueError("assignment is not conflicting")
        literals = tuple((True, state) for state in self.states if state in inc) + tuple(
            (False, state) for state in self.states if state in exc
        )
        for size in range(len(literals) + 1):
            for selected in combinations(literals, size):
                chosen_inc = frozenset(state for positive, state in selected if positive)
                chosen_exc = frozenset(state for positive, state in selected if not positive)
                if self._class_conflict_holds(pointed, chosen_inc, chosen_exc):
                    return DomainNogood(
                        include=chosen_inc,
                        exclude=chosen_exc,
                        class_representative=pointed.representative,
                        killed_seed_count=len(pointed.rules),
                        minimization="exact_cardinality",
                    )
        raise AssertionError("the full conflicting assignment must be found")


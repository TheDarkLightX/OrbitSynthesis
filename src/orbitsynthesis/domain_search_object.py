"""Object/set branch-and-bound with learned pointed-domain nogoods."""
from __future__ import annotations

from typing import Any, Iterable

from .domain_search_types import (
    DomainNogood, DomainSearchResult, DomainSearchStats, Observation, Output, State,
)
from .domain_search_rules import CompiledPointedRules


class CompiledNogoodDomainSearch(CompiledPointedRules):
    def _record_nogood(self, nogood: DomainNogood) -> None:
        # A nogood with fewer positive and negative literals triggers on a
        # larger cone and subsumes a more specific one.
        if any(
            old.include <= nogood.include and old.exclude <= nogood.exclude
            for old in self._nogoods
        ):
            return
        self._nogoods = [
            old
            for old in self._nogoods
            if not (
                nogood.include <= old.include
                and nogood.exclude <= old.exclude
            )
        ]
        self._nogoods.append(nogood)
        self.stats.learned_nogoods += 1

    # ------------------------------------------------------------------
    # Propagation and search
    # ------------------------------------------------------------------

    def _propagate(
        self,
        included: frozenset[State],
        excluded: frozenset[State],
        *,
        learn: bool,
    ) -> tuple[frozenset[State], frozenset[State], DomainNogood | None]:
        inc = set(included)
        exc = set(excluded)
        if inc & exc:
            raise ValueError("included and excluded states overlap")

        while True:
            changed = False
            inc_f = frozenset(inc)
            exc_f = frozenset(exc)

            for nogood in self._nogoods:
                if nogood.triggered_by_partial(inc_f, exc_f):
                    self.stats.learned_nogood_hits += 1
                    return inc_f, exc_f, nogood

            for pointed in self.class_rules:
                viable = tuple(
                    rule
                    for rule in pointed.rules
                    if self._seed_viable_partial(rule, inc_f, exc_f)
                )
                if not viable:
                    self.stats.class_conflicts += 1
                    nogood = self._greedy_irredundant_conflict(
                        pointed,
                        inc_f,
                        exc_f,
                    )
                    if learn:
                        self._record_nogood(nogood)
                    return inc_f, exc_f, nogood

                required_sets = tuple(
                    self._requirements_for(rule, inc_f)
                    for rule in viable
                )
                mandatory = set(required_sets[0])
                for required in required_sets[1:]:
                    mandatory.intersection_update(required)
                new_includes = mandatory - inc - exc
                if new_includes:
                    if learn:
                        for target in tuple(new_includes):
                            conflict_inc = frozenset(inc)
                            conflict_exc = frozenset(set(exc) | {target})
                            if self._class_conflict_holds(
                                pointed, conflict_inc, conflict_exc
                            ):
                                self._record_nogood(
                                    self._greedy_irredundant_conflict(
                                        pointed, conflict_inc, conflict_exc
                                    )
                                )
                    inc.update(new_includes)
                    self.stats.propagated_includes += len(new_includes)
                    changed = True

                undecided = set(self.states) - inc - exc
                forced_out: set[State] = set()
                for source in undecided:
                    can_include = any(
                        source not in rule.unsafe_sources
                        and not bool(
                            rule.requirements.get(source, frozenset()) & frozenset(exc)
                        )
                        for rule in viable
                    )
                    if not can_include:
                        forced_out.add(source)
                        if learn:
                            conflict_inc = frozenset(set(inc) | {source})
                            conflict_exc = frozenset(exc)
                            if self._class_conflict_holds(
                                pointed, conflict_inc, conflict_exc
                            ):
                                self._record_nogood(
                                    self._greedy_irredundant_conflict(
                                        pointed, conflict_inc, conflict_exc
                                    )
                                )
                if forced_out:
                    exc.update(forced_out)
                    self.stats.propagated_excludes += len(forced_out)
                    changed = True

            if inc & exc:
                raise AssertionError("sound propagation cannot force both literals")
            if not changed:
                return frozenset(inc), frozenset(exc), None

    def _choose_branch_state(
        self,
        included: frozenset[State],
        excluded: frozenset[State],
    ) -> State:
        undecided = [
            state
            for state in self.states
            if state not in included and state not in excluded
        ]
        if not undecided:
            raise ValueError("no undecided state")
        return max(
            undecided,
            key=lambda state: (
                self._impact[state],
                -self._state_index[state],
            ),
        )

    def maximal_domains(
        self,
        *,
        required_states: Iterable[State] = (),
        forbidden_states: Iterable[State] = (),
        learn_nogoods: bool = True,
        use_propagation: bool = True,
    ) -> DomainSearchResult:
        required = frozenset(required_states)
        forbidden = frozenset(forbidden_states)
        carrier_states = frozenset(self.states)
        if not required <= carrier_states or not forbidden <= carrier_states:
            raise ValueError("required or forbidden state outside game")
        if required & forbidden:
            raise ValueError("required and forbidden states overlap")

        self._nogoods = []
        self.stats = DomainSearchStats()
        maximal: list[tuple[frozenset[State], dict[Observation, Output]]] = []

        def add_solution(
            domain: frozenset[State],
            strategy: dict[Observation, Output],
        ) -> None:
            nonlocal maximal
            if any(domain <= old_domain for old_domain, _old_strategy in maximal):
                return
            maximal = [
                row
                for row in maximal
                if not row[0] < domain
            ]
            maximal.append((domain, strategy))

        def dfs(
            included: frozenset[State],
            excluded: frozenset[State],
            depth: int,
        ) -> None:
            self.stats.nodes += 1
            self.stats.max_depth = max(self.stats.max_depth, depth)

            if use_propagation:
                inc, exc, conflict = self._propagate(
                    included,
                    excluded,
                    learn=learn_nogoods,
                )
                if conflict is not None:
                    return
            else:
                inc, exc = included, excluded
                for pointed in self.class_rules:
                    if self._class_conflict_holds(pointed, inc, exc):
                        self.stats.class_conflicts += 1
                        nogood = self._greedy_irredundant_conflict(pointed, inc, exc)
                        if learn_nogoods:
                            self._record_nogood(nogood)
                        return

            upper = frozenset(state for state in self.states if state not in exc)
            if any(upper <= old_domain for old_domain, _strategy in maximal):
                self.stats.dominance_prunes += 1
                return

            undecided = carrier_states - inc - exc
            if not undecided:
                self.stats.complete_leaves += 1
                strategy = self.strategy_for_domain(inc)
                if strategy is None:
                    raise AssertionError(
                        "complete assignment survived propagation but is infeasible"
                    )
                self.stats.feasible_leaves += 1
                add_solution(inc, strategy)
                return

            branch = self._choose_branch_state(inc, exc)
            # Inclusion first tends to discover dominating large domains early.
            dfs(inc | {branch}, exc, depth + 1)
            dfs(inc, exc | {branch}, depth + 1)

        dfs(required, forbidden, 0)

        maximal.sort(
            key=lambda row: tuple(
                int(state in row[0]) for state in self.states
            ),
            reverse=True,
        )
        return DomainSearchResult(
            maximal_domains=tuple(
                (
                    domain,
                    tuple((obs, strategy[obs]) for obs in self.game.observations),
                )
                for domain, strategy in maximal
            ),
            nogoods=tuple(self._nogoods),
            stats=self.stats,
        )


def maximal_domains_nogood(
    kernel: Any,
    *,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    learn_nogoods: bool = True,
    use_propagation: bool = True,
) -> DomainSearchResult:
    """Convenience entry point for one compiled pointed kernel."""

    return CompiledNogoodDomainSearch(kernel).maximal_domains(
        required_states=required_states,
        forbidden_states=forbidden_states,
        learn_nogoods=learn_nogoods,
        use_propagation=use_propagation,
    )


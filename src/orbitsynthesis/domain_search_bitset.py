"""Bit-parallel refinement of exact pointed-domain nogood search."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .domain_search_types import (
    DomainNogood, DomainSearchResult, DomainSearchStats, Observation, Output,
    PointedClassRules, SeedRule, State,
)
from .domain_search_object import CompiledNogoodDomainSearch

@dataclass(frozen=True)
class _BitSeedRule:
    seed: Output
    unsafe_mask: int
    requirements_by_source: tuple[int, ...]
    requirement_closure: tuple[int, ...] | None


@dataclass(frozen=True)
class _BitPointedClass:
    representative: Observation
    rules: tuple[_BitSeedRule, ...]


class BitsetNogoodDomainSearch:
    """Bit-parallel variant of :class:`CompiledNogoodDomainSearch`.

    For carriers up to ``precompute_state_limit`` states, every seed rule stores
    the union of its output requirements for all domain masks.  Partial
    viability then reduces to two integer ``&`` tests.  Larger games retain the
    same semantics and compute requirement unions on demand.
    """

    def __init__(
        self,
        kernel: Any,
        *,
        precompute_state_limit: int = 18,
    ) -> None:
        self.kernel = kernel
        self.game = kernel.game
        self.states = tuple(self.game.states)
        self.n = len(self.states)
        self.all_mask = (1 << self.n) - 1
        self._state_index = {state: index for index, state in enumerate(self.states)}
        self._state_bits = {state: 1 << index for state, index in self._state_index.items()}
        object_compiler = CompiledNogoodDomainSearch(kernel)
        self.object_classes = object_compiler.class_rules
        self._pointed_by_rep = {
            pointed.representative: pointed
            for pointed in kernel.pointed_classes
        }
        self.classes = tuple(
            self._compile_bit_class(pointed, precompute_state_limit)
            for pointed in self.object_classes
        )
        self._impact = self._compile_bit_impact()
        self._nogoods: list[tuple[int, int, DomainNogood]] = []
        self.stats = DomainSearchStats()

    def _mask(self, states: Iterable[State]) -> int:
        mask = 0
        for state in states:
            try:
                mask |= self._state_bits[state]
            except KeyError as error:
                raise ValueError(f"state outside game: {state!r}") from error
        return mask

    def _frozenset(self, mask: int) -> frozenset[State]:
        return frozenset(
            state
            for index, state in enumerate(self.states)
            if mask & (1 << index)
        )

    def _compile_bit_class(
        self,
        pointed: PointedClassRules,
        precompute_state_limit: int,
    ) -> _BitPointedClass:
        rules: list[_BitSeedRule] = []
        for rule in pointed.rules:
            unsafe = self._mask(rule.unsafe_sources)
            req_map = rule.requirements
            requirements = tuple(
                self._mask(req_map.get(state, frozenset()))
                for state in self.states
            )
            closure: tuple[int, ...] | None = None
            if self.n <= precompute_state_limit:
                rows = [0] * (1 << self.n)
                for mask in range(1, 1 << self.n):
                    low = mask & -mask
                    index = low.bit_length() - 1
                    rows[mask] = rows[mask ^ low] | requirements[index]
                closure = tuple(rows)
            rules.append(
                _BitSeedRule(
                    seed=rule.seed,
                    unsafe_mask=unsafe,
                    requirements_by_source=requirements,
                    requirement_closure=closure,
                )
            )
        return _BitPointedClass(pointed.representative, tuple(rules))

    def _compile_bit_impact(self) -> tuple[int, ...]:
        scores = [0] * self.n
        for pointed in self.classes:
            for rule in pointed.rules:
                unsafe = rule.unsafe_mask
                while unsafe:
                    low = unsafe & -unsafe
                    scores[low.bit_length() - 1] += 3
                    unsafe ^= low
                for index, targets in enumerate(rule.requirements_by_source):
                    if targets:
                        scores[index] += 2 + targets.bit_count()
                        target_mask = targets
                        while target_mask:
                            low = target_mask & -target_mask
                            scores[low.bit_length() - 1] += 1
                            target_mask ^= low
        return tuple(scores)

    @staticmethod
    def _requirements(rule: _BitSeedRule, included: int) -> int:
        if rule.requirement_closure is not None:
            return rule.requirement_closure[included]
        out = 0
        mask = included
        while mask:
            low = mask & -mask
            out |= rule.requirements_by_source[low.bit_length() - 1]
            mask ^= low
        return out

    @classmethod
    def _viable(cls, rule: _BitSeedRule, included: int, excluded: int) -> bool:
        return not (rule.unsafe_mask & included) and not (
            cls._requirements(rule, included) & excluded
        )

    @classmethod
    def _valid(cls, rule: _BitSeedRule, domain: int) -> bool:
        return not (rule.unsafe_mask & domain) and not (
            cls._requirements(rule, domain) & ~domain
        )

    def _class_conflict(
        self,
        pointed: _BitPointedClass,
        included: int,
        excluded: int,
    ) -> bool:
        return not any(self._viable(rule, included, excluded) for rule in pointed.rules)

    def _minimize_conflict(
        self,
        pointed: _BitPointedClass,
        included: int,
        excluded: int,
    ) -> tuple[int, int, DomainNogood]:
        if not self._class_conflict(pointed, included, excluded):
            raise ValueError("assignment is not conflicting")
        inc, exc = included, excluded
        changed = True
        while changed:
            changed = False
            for index in range(self.n):
                bit = 1 << index
                if inc & bit and self._class_conflict(pointed, inc ^ bit, exc):
                    inc ^= bit
                    changed = True
            for index in range(self.n):
                bit = 1 << index
                if exc & bit and self._class_conflict(pointed, inc, exc ^ bit):
                    exc ^= bit
                    changed = True
        nogood = DomainNogood(
            include=self._frozenset(inc),
            exclude=self._frozenset(exc),
            class_representative=pointed.representative,
            killed_seed_count=len(pointed.rules),
        )
        return inc, exc, nogood

    def _record(self, row: tuple[int, int, DomainNogood]) -> None:
        inc, exc, _nogood = row
        if any((old_inc & inc) == old_inc and (old_exc & exc) == old_exc
               for old_inc, old_exc, _old in self._nogoods):
            return
        self._nogoods = [
            old
            for old in self._nogoods
            if not ((inc & old[0]) == inc and (exc & old[1]) == exc)
        ]
        self._nogoods.append(row)
        self.stats.learned_nogoods += 1

    def _propagate(
        self,
        included: int,
        excluded: int,
        *,
        learn: bool,
        learn_propagation_nogoods: bool,
    ) -> tuple[int, int, DomainNogood | None]:
        inc, exc = included, excluded
        while True:
            changed = False
            for ng_inc, ng_exc, nogood in self._nogoods:
                if (ng_inc & inc) == ng_inc and (ng_exc & exc) == ng_exc:
                    self.stats.learned_nogood_hits += 1
                    return inc, exc, nogood

            for pointed in self.classes:
                viable = tuple(
                    rule for rule in pointed.rules if self._viable(rule, inc, exc)
                )
                if not viable:
                    self.stats.class_conflicts += 1
                    row = self._minimize_conflict(pointed, inc, exc)
                    if learn:
                        self._record(row)
                    return inc, exc, row[2]

                mandatory = self.all_mask
                for rule in viable:
                    mandatory &= self._requirements(rule, inc)
                new_in = mandatory & ~(inc | exc) & self.all_mask
                if new_in:
                    if learn and learn_propagation_nogoods:
                        mask = new_in
                        while mask:
                            bit = mask & -mask
                            if self._class_conflict(pointed, inc, exc | bit):
                                self._record(self._minimize_conflict(pointed, inc, exc | bit))
                            mask ^= bit
                    inc |= new_in
                    self.stats.propagated_includes += new_in.bit_count()
                    changed = True

                undecided = self.all_mask & ~(inc | exc)
                forced_out = 0
                mask = undecided
                while mask:
                    bit = mask & -mask
                    trial_inc = inc | bit
                    if not any(self._viable(rule, trial_inc, exc) for rule in viable):
                        forced_out |= bit
                        if learn and learn_propagation_nogoods:
                            self._record(self._minimize_conflict(pointed, trial_inc, exc))
                    mask ^= bit
                if forced_out:
                    exc |= forced_out
                    self.stats.propagated_excludes += forced_out.bit_count()
                    changed = True
            if inc & exc:
                raise AssertionError("propagation contradiction escaped class conflict")
            if not changed:
                return inc, exc, None

    def _branch_bit(self, included: int, excluded: int) -> int:
        undecided = self.all_mask & ~(included | excluded)
        best_index = max(
            (index for index in range(self.n) if undecided & (1 << index)),
            key=lambda index: (self._impact[index], -index),
        )
        return 1 << best_index

    def strategy_for_mask(self, domain: int) -> dict[Observation, Output] | None:
        assignment: dict[Observation, Output] = {}
        for pointed in self.classes:
            selected = next(
                (rule for rule in pointed.rules if self._valid(rule, domain)),
                None,
            )
            if selected is None:
                return None
            source = self._pointed_by_rep[pointed.representative]
            transports = self.kernel.pointed_transports[pointed.representative]
            for observation in source.observations:
                mapping = transports[observation]
                assignment[observation] = tuple(mapping[value] for value in selected.seed)
        return assignment

    def is_feasible_mask(self, domain: int) -> bool:
        return all(
            any(self._valid(rule, domain) for rule in pointed.rules)
            for pointed in self.classes
        )

    def maximal_domains(
        self,
        *,
        required_states: Iterable[State] = (),
        forbidden_states: Iterable[State] = (),
        learn_nogoods: bool = True,
        learn_propagation_nogoods: bool = False,
    ) -> DomainSearchResult:
        required = self._mask(required_states)
        forbidden = self._mask(forbidden_states)
        if required & forbidden:
            raise ValueError("required and forbidden states overlap")
        self._nogoods = []
        self.stats = DomainSearchStats()
        maximal: list[tuple[int, dict[Observation, Output]]] = []

        def add_solution(mask: int, strategy: dict[Observation, Output]) -> None:
            nonlocal maximal
            if any((mask & old) == mask for old, _ in maximal):
                return
            maximal = [(old, st) for old, st in maximal if (old & mask) != old]
            maximal.append((mask, strategy))

        def dfs(inc: int, exc: int, depth: int) -> None:
            self.stats.nodes += 1
            self.stats.max_depth = max(self.stats.max_depth, depth)
            inc, exc, conflict = self._propagate(
                inc,
                exc,
                learn=learn_nogoods,
                learn_propagation_nogoods=learn_propagation_nogoods,
            )
            if conflict is not None:
                return
            upper = self.all_mask & ~exc
            if any((upper & old) == upper for old, _ in maximal):
                self.stats.dominance_prunes += 1
                return
            if (inc | exc) == self.all_mask:
                self.stats.complete_leaves += 1
                strategy = self.strategy_for_mask(inc)
                if strategy is None:
                    raise AssertionError("complete propagated mask is infeasible")
                self.stats.feasible_leaves += 1
                add_solution(inc, strategy)
                return
            bit = self._branch_bit(inc, exc)
            dfs(inc | bit, exc, depth + 1)
            dfs(inc, exc | bit, depth + 1)

        dfs(required, forbidden, 0)
        maximal.sort(key=lambda row: row[0], reverse=True)
        return DomainSearchResult(
            maximal_domains=tuple(
                (
                    self._frozenset(mask),
                    tuple((obs, strategy[obs]) for obs in self.game.observations),
                )
                for mask, strategy in maximal
            ),
            nogoods=tuple(row[2] for row in self._nogoods),
            stats=self.stats,
        )


def maximal_domains_bitset_nogood(
    kernel: Any,
    *,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    learn_nogoods: bool = True,
    learn_propagation_nogoods: bool = False,
) -> DomainSearchResult:
    return BitsetNogoodDomainSearch(kernel).maximal_domains(
        required_states=required_states,
        forbidden_states=forbidden_states,
        learn_nogoods=learn_nogoods,
        learn_propagation_nogoods=learn_propagation_nogoods,
    )

"""Obstruction-guided maximal-domain search for compiled pointed kernels.

A fixed closed parameter core turns every pointed observation class into a
finite disjunction of *seed rules*.  When a source state is active, one seed
rule either rejects that state (the transported output is unsafe) or requires a
finite set of output states to be active.  This module searches the Boolean
state-domain lattice directly, propagates those implications, and learns
replayable two-sided nogoods when every seed in one pointed class is killed.

The implementation is exact.  It is intended to replace exhaustive ``2^n``
domain enumeration for small and medium finite games while retaining an
independent exhaustive solver as a differential oracle.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Hashable, Iterable, Mapping, Sequence

Value = Hashable
State = tuple[Value, ...]
Output = tuple[Value, ...]
Observation = tuple[Value, ...]


@dataclass(frozen=True)
class SeedRule:
    """One representative seed compiled to state-domain obligations.

    If ``p`` belongs to a candidate domain, the seed is impossible when
    ``p in unsafe_sources``.  Otherwise every state in ``requirements[p]``
    must also belong to the domain.
    """

    seed: Output
    unsafe_sources: frozenset[State]
    requirement_items: tuple[tuple[State, tuple[State, ...]], ...]

    @property
    def requirements(self) -> dict[State, frozenset[State]]:
        return {
            source: frozenset(targets)
            for source, targets in self.requirement_items
        }


@dataclass(frozen=True)
class PointedClassRules:
    representative: Observation
    observations: tuple[Observation, ...]
    rules: tuple[SeedRule, ...]


@dataclass(frozen=True)
class DomainNogood:
    """A sufficient certificate that a whole partial-domain cone is infeasible.

    Every complete domain ``W`` satisfying

    ``include <= W`` and ``exclude ∩ W = ∅``

    kills all seeds of the named pointed class.
    """

    include: frozenset[State]
    exclude: frozenset[State]
    class_representative: Observation
    killed_seed_count: int
    minimization: str = "greedy_irredundant"

    def triggered_by_partial(
        self,
        included: Iterable[State],
        excluded: Iterable[State],
    ) -> bool:
        return self.include <= frozenset(included) and self.exclude <= frozenset(excluded)

    def covers_domain(self, domain: Iterable[State]) -> bool:
        chosen = frozenset(domain)
        return self.include <= chosen and not bool(self.exclude & chosen)


@dataclass
class DomainSearchStats:
    nodes: int = 0
    complete_leaves: int = 0
    feasible_leaves: int = 0
    class_conflicts: int = 0
    learned_nogoods: int = 0
    learned_nogood_hits: int = 0
    dominance_prunes: int = 0
    propagated_includes: int = 0
    propagated_excludes: int = 0
    max_depth: int = 0


@dataclass(frozen=True)
class DomainSearchResult:
    maximal_domains: tuple[
        tuple[frozenset[State], tuple[tuple[Observation, Output], ...]], ...
    ]
    nogoods: tuple[DomainNogood, ...]
    stats: DomainSearchStats



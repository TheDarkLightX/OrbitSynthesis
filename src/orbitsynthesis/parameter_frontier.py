"""Exact parameter-core / winning-domain Pareto frontiers."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Hashable, Iterable, Sequence
from .parameter_closure import parameter_core, parameter_core_catalog
from .domain_api import CompiledParameterizedKernel
Value = Hashable
State = tuple[Value, ...]
Output = tuple[Value, ...]
Observation = tuple[Value, ...]

@dataclass(frozen=True)
class ParameterDomainPoint:
    """One semantically distinct controller-language/domain tradeoff."""

    core: frozenset[Value]
    rank: int
    parameter_witnesses: tuple[frozenset[Value], ...]
    domain: frozenset[State]
    strategy_items: tuple[tuple[Observation, Output], ...]

    @property
    def strategy(self) -> dict[Observation, Output]:
        return dict(self.strategy_items)

@dataclass(frozen=True)
class ParameterDomainFrontier:
    """All maximal per-core domains and the nondominated joint frontier."""

    all_points: tuple[ParameterDomainPoint, ...]
    nondominated: tuple[ParameterDomainPoint, ...]

def maximal_parameterized_domains(
    game: Any,
    core: Iterable[Value],
    *,
    solver: str = "pointed",
    search: str = "exhaustive",
    exhaustive_state_limit: int = 16,
    internal_isomorphisms: Sequence[Any] | None = None,
) -> tuple[tuple[frozenset[State], tuple[tuple[Observation, Output], ...]], ...]:
    """Enumerate inclusion-maximal domains using one compiled core kernel."""

    kernel = CompiledParameterizedKernel(
        game,
        core,
        internal_isomorphisms=internal_isomorphisms,
    )
    return kernel.maximal_domains(
        solver=solver,
        search=search,
        exhaustive_state_limit=exhaustive_state_limit,
    )

def _strictly_dominates(
    left: ParameterDomainPoint,
    right: ParameterDomainPoint,
) -> bool:
    """Smaller language/budget and larger domain is strictly preferable."""

    weak = (
        left.rank <= right.rank
        and left.core <= right.core
        and left.domain >= right.domain
    )
    strict = (
        left.rank < right.rank
        or left.core < right.core
        or left.domain > right.domain
    )
    return weak and strict

def parameter_domain_frontier(
    game: Any,
    *,
    solver: str = "pointed",
    search: str = "exhaustive",
    exhaustive_state_limit: int = 16,
) -> ParameterDomainFrontier:
    """Compute the exact joint closed-core / winning-domain antichain."""

    all_isos = game.algebra.internal_isomorphisms()
    points: list[ParameterDomainPoint] = []
    for info in parameter_core_catalog(game.algebra):
        kernel = CompiledParameterizedKernel(
            game,
            info.core,
            internal_isomorphisms=all_isos,
        )
        for domain, strategy_items in kernel.maximal_domains(
            solver=solver,
            search=search,
            exhaustive_state_limit=exhaustive_state_limit,
        ):
            points.append(
                ParameterDomainPoint(
                    core=info.core,
                    rank=info.rank,
                    parameter_witnesses=info.witnesses,
                    domain=domain,
                    strategy_items=strategy_items,
                )
            )

    nondominated = tuple(
        point
        for point in points
        if not any(
            _strictly_dominates(other, point)
            for other in points
            if other is not point
        )
    )
    return ParameterDomainFrontier(
        all_points=tuple(points),
        nondominated=nondominated,
    )

def parameter_budget_frontier(
    game: Any,
    budget: int,
    *,
    required_initial_states: Iterable[State] = (),
    solver: str = "pointed",
    search: str = "exhaustive",
    exhaustive_state_limit: int = 16,
) -> ParameterDomainFrontier:
    """Exact nondominated frontier subject to a raw-parameter budget.

    ``budget`` is charged by exact generator rank of the definable-constant
    core, not by a caller-supplied raw set's cardinality.  Returned domains must
    contain every required initial state.
    """

    if budget < 0:
        raise ValueError("parameter budget cannot be negative")
    required = frozenset(required_initial_states)
    all_isos = game.algebra.internal_isomorphisms()
    points: list[ParameterDomainPoint] = []
    for info in parameter_core_catalog(game.algebra):
        if info.rank > budget:
            continue
        kernel = CompiledParameterizedKernel(
            game,
            info.core,
            internal_isomorphisms=all_isos,
        )
        for domain, strategy_items in kernel.maximal_domains(
            solver=solver,
            search=search,
            exhaustive_state_limit=exhaustive_state_limit,
            required_states=required,
        ):
            if not required <= domain:
                continue
            points.append(
                ParameterDomainPoint(
                    core=info.core,
                    rank=info.rank,
                    parameter_witnesses=info.witnesses,
                    domain=domain,
                    strategy_items=strategy_items,
                )
            )
    nondominated = tuple(
        point
        for point in points
        if not any(
            _strictly_dominates(other, point)
            for other in points
            if other is not point
        )
    )
    return ParameterDomainFrontier(tuple(points), nondominated)

def minimum_parameter_solutions(
    game: Any,
    initial_states: Iterable[State],
    *,
    max_budget: int | None = None,
    solver: str = "pointed",
    search: str = "exhaustive",
    exhaustive_state_limit: int = 16,
) -> tuple[ParameterDomainPoint, ...]:
    """Return every minimum-rank semantic solution containing ``initial_states``.

    Incomparable closed cores or winning domains are retained; the API never
    invents a unique least solution when the mathematics provides an antichain.
    """

    required = frozenset(initial_states)
    catalog = parameter_core_catalog(game.algebra)
    limit = max((info.rank for info in catalog), default=0)
    if max_budget is not None:
        if max_budget < 0:
            raise ValueError("max_budget cannot be negative")
        limit = min(limit, max_budget)
    for budget in range(limit + 1):
        frontier = parameter_budget_frontier(
            game,
            budget,
            required_initial_states=required,
            solver=solver,
            search=search,
            exhaustive_state_limit=exhaustive_state_limit,
        )
        feasible = tuple(point for point in frontier.nondominated if point.rank == budget)
        if feasible:
            return feasible
    return ()

"""Fixed-domain parameter-core synthesis and table-to-safety reductions.

For finite quasi-primal algebras, the pointed kernel decides whether a closed
parameter core admits a polynomial controller on one declared invariant domain.
This module preserves every incomparable minimum core instead of inventing a
single least controller language.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from .parameter_closure import parameter_core_catalog
from .pointed_kernel import CompiledParameterizedKernel
from .safety import FiniteSafetyGame

Value = Hashable
State = tuple[Value, ...]
Input = tuple[Value, ...]
Output = tuple[Value, ...]
Observation = tuple[Value, ...]


@dataclass(frozen=True)
class DeterministicTableReduction:
    """A scalar operation table encoded as a full-domain safety game."""

    game: FiniteSafetyGame
    full_domain: frozenset[State]
    target_items: tuple[tuple[Observation, Output], ...]

    @property
    def target_strategy(self) -> dict[Observation, Output]:
        return dict(self.target_items)


@dataclass(frozen=True)
class FixedDomainCorePoint:
    """One closed parameter core that realizes a fixed invariant domain."""

    core: frozenset[Value]
    rank: int
    parameter_witnesses: tuple[frozenset[Value], ...]
    domain: frozenset[State]
    strategy_items: tuple[tuple[Observation, Output], ...]

    @property
    def strategy(self) -> dict[Observation, Output]:
        return dict(self.strategy_items)


@dataclass(frozen=True)
class FixedDomainCoreResult:
    """All feasible cores and their exact minimal antichains."""

    all_feasible: tuple[FixedDomainCorePoint, ...]
    inclusion_minimal: tuple[FixedDomainCorePoint, ...]
    minimum_rank: tuple[FixedDomainCorePoint, ...]
    least_core: FixedDomainCorePoint | None

    @property
    def minimum_parameter_budget(self) -> int | None:
        if not self.minimum_rank:
            return None
        return self.minimum_rank[0].rank


def deterministic_table_reduction(
    algebra: Any,
    arity: int,
    target: Mapping[tuple[Value, ...], Value] | Callable[..., Value],
) -> DeterministicTableReduction:
    """Encode ``target : A^arity -> A`` as a deterministic safety game.

    The first operation argument is the current one-coordinate state and the
    remaining arguments are the environment input.  Every full-domain winning
    controller must equal ``target`` pointwise, and the target table itself is
    winning.  Consequently parameter-core feasibility of the full state domain
    is exactly polynomial membership of the target operation.
    """

    if arity <= 0:
        raise ValueError("arity must be positive")
    carrier = tuple(algebra.values)
    carrier_set = frozenset(carrier)

    def value_at(args: tuple[Value, ...]) -> Value:
        if isinstance(target, Mapping):
            try:
                value = target[args]
            except KeyError as error:
                raise ValueError(f"target table omits row {args!r}") from error
        else:
            value = target(*args)
        if value not in carrier_set:
            raise ValueError(f"target leaves the carrier at {args!r}: {value!r}")
        return value

    safe_relation: set[tuple[State, Input, Output]] = set()
    target_items: list[tuple[Observation, Output]] = []
    for args in product(carrier, repeat=arity):
        state = (args[0],)
        input_value = tuple(args[1:])
        output = (value_at(tuple(args)),)
        safe_relation.add((state, input_value, output))
        target_items.append((state + input_value, output))

    game = FiniteSafetyGame(
        algebra=algebra,
        state_arity=1,
        input_arity=arity - 1,
        safe_relation=safe_relation,
    )
    target_by_observation = dict(target_items)
    ordered_items = tuple(
        (observation, target_by_observation[observation])
        for observation in game.observations
    )
    return DeterministicTableReduction(
        game=game,
        full_domain=frozenset(game.states),
        target_items=ordered_items,
    )


def minimum_cores_for_domain(
    game: Any,
    domain: Iterable[State],
    *,
    internal_isomorphisms: Sequence[Any] | None = None,
) -> FixedDomainCoreResult:
    """Return every exact minimum controller-language core for one domain.

    This uses the finite quasi-primal pointed-kernel characterization.  The
    caller is responsible for establishing that algebraic hypothesis.  The
    result distinguishes two useful notions:

    * ``inclusion_minimal``: no strictly weaker feasible closed core exists;
    * ``minimum_rank``: minimum raw parameter budget, with same-budget strict
      core supersets removed as semantically dominated.

    Either field may contain several incomparable cores.
    """

    chosen_domain = frozenset(domain)
    carrier_states = frozenset(game.states)
    if not chosen_domain <= carrier_states:
        raise ValueError("domain contains a state outside the game")
    all_isos = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else game.algebra.internal_isomorphisms()
    )

    feasible: list[FixedDomainCorePoint] = []
    for info in parameter_core_catalog(game.algebra):
        kernel = CompiledParameterizedKernel(
            game,
            info.core,
            internal_isomorphisms=all_isos,
        )
        strategy = kernel.strategy_pointed(chosen_domain)
        if strategy is None:
            continue
        feasible.append(
            FixedDomainCorePoint(
                core=info.core,
                rank=info.rank,
                parameter_witnesses=info.witnesses,
                domain=chosen_domain,
                strategy_items=tuple(
                    (observation, strategy[observation])
                    for observation in game.observations
                ),
            )
        )

    inclusion_minimal = tuple(
        point
        for point in feasible
        if not any(
            other.core < point.core
            for other in feasible
            if other is not point
        )
    )

    minimum_rank: tuple[FixedDomainCorePoint, ...] = ()
    if feasible:
        best_rank = min(point.rank for point in feasible)
        rank_candidates = tuple(
            point for point in feasible if point.rank == best_rank
        )
        minimum_rank = tuple(
            point
            for point in rank_candidates
            if not any(
                other.core < point.core
                for other in rank_candidates
                if other is not point
            )
        )

    least_core: FixedDomainCorePoint | None = None
    if len(inclusion_minimal) == 1:
        candidate = inclusion_minimal[0]
        if all(candidate.core <= point.core for point in feasible):
            least_core = candidate

    return FixedDomainCoreResult(
        all_feasible=tuple(feasible),
        inclusion_minimal=inclusion_minimal,
        minimum_rank=minimum_rank,
        least_core=least_core,
    )

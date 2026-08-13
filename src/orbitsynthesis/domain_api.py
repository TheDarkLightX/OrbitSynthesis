"""Search-enabled wrappers around the stable compiled pointed kernel.

The original :mod:`pointed_kernel` remains the independent exhaustive
reference.  This module adds exact nogood and bitset search without entangling
the proof-oriented table compiler with optimization state.
"""
from __future__ import annotations

from typing import Any, Hashable, Iterable, Sequence

from .domain_search import BitsetNogoodDomainSearch, CompiledNogoodDomainSearch
from .parameter_closure import parameter_core
from .pointed_kernel import CompiledParameterizedKernel as _ReferenceCompiledKernel

Value = Hashable
State = tuple[Value, ...]
Output = tuple[Value, ...]
Observation = tuple[Value, ...]


class CompiledParameterizedKernel(_ReferenceCompiledKernel):
    """Reference compiled kernel plus cached exact domain-search refinements."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._object_nogood_search: CompiledNogoodDomainSearch | None = None
        self._bitset_nogood_search: BitsetNogoodDomainSearch | None = None

    def maximal_domains(
        self,
        *,
        solver: str = "pointed",
        search: str = "exhaustive",
        exhaustive_state_limit: int = 16,
        required_states: Iterable[State] = (),
        forbidden_states: Iterable[State] = (),
    ) -> tuple[
        tuple[frozenset[State], tuple[tuple[Observation, Output], ...]], ...
    ]:
        """Enumerate exact maximal domains under optional partial assignments."""

        required = frozenset(required_states)
        forbidden = frozenset(forbidden_states)
        carrier = frozenset(self.game.states)
        if not required <= carrier or not forbidden <= carrier:
            raise ValueError("required or forbidden state outside game")
        if required & forbidden:
            raise ValueError("required and forbidden states overlap")

        if search in {"nogood", "bitset_nogood"}:
            if solver != "pointed":
                raise ValueError("nogood search compiles pointed seed semantics")
            if search == "nogood":
                if self._object_nogood_search is None:
                    self._object_nogood_search = CompiledNogoodDomainSearch(self)
                engine = self._object_nogood_search
            else:
                if self._bitset_nogood_search is None:
                    self._bitset_nogood_search = BitsetNogoodDomainSearch(self)
                engine = self._bitset_nogood_search
            return engine.maximal_domains(
                required_states=required,
                forbidden_states=forbidden,
            ).maximal_domains

        if search != "exhaustive":
            raise ValueError(
                "search must be 'exhaustive', 'nogood', or 'bitset_nogood'"
            )
        if len(self.game.states) > exhaustive_state_limit:
            raise ValueError("state limit exceeded")
        if solver == "pointed":
            solve = self.strategy_pointed
        elif solver == "reference":
            solve = self.strategy_reference
        else:
            raise ValueError("solver must be 'pointed' or 'reference'")
        states = tuple(self.game.states)
        feasible = []
        for mask in range(1 << len(states)):
            domain = frozenset(
                states[index]
                for index in range(len(states))
                if mask & (1 << index)
            )
            if not required <= domain or forbidden & domain:
                continue
            strategy = solve(domain)
            if strategy is not None:
                feasible.append((domain, strategy))
        return tuple(
            (
                domain,
                tuple((obs, strategy[obs]) for obs in self.game.observations),
            )
            for domain, strategy in feasible
            if not any(domain < other for other, _ in feasible)
        )


def maximal_domains_for_allowed_parameters(
    game: Any,
    allowed_parameters: Iterable[Value],
    *,
    solver: str = "pointed",
    search: str = "exhaustive",
    exhaustive_state_limit: int = 16,
    required_states: Iterable[State] = (),
    forbidden_states: Iterable[State] = (),
    internal_isomorphisms: Sequence[Any] | None = None,
) -> tuple[
    tuple[frozenset[State], tuple[tuple[Observation, Output], ...]], ...
]:
    """Compile raw parameters through closure, then search exact maximal domains."""

    core = parameter_core(game.algebra, allowed_parameters)
    kernel = CompiledParameterizedKernel(
        game,
        core,
        internal_isomorphisms=internal_isomorphisms,
    )
    return kernel.maximal_domains(
        solver=solver,
        search=search,
        exhaustive_state_limit=exhaustive_state_limit,
        required_states=required_states,
        forbidden_states=forbidden_states,
    )

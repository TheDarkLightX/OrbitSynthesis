"""Source-grounded structural benchmark families for OrbitSynthesis.

These are not synthetic random formulas.  They expose the two load-bearing
reactive constructions already proved in the repository:

* the exact fixed-Q maximal-domain antichain, with
  ``2^(2^(k-1)-2)`` incomparable maxima; and
* the principal one-equation no-greatest-region witness.

The builders return the actual finite safety games used by the component,
weighted-search, and external optimization backends.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .domain_model import QuasiPrimalDomainModel, compile_quasi_primal_domain_model
from .finite_algebra import FiniteAlgebra
from .optimization_authority import (
    ObjectiveAuthority,
    closed_form_objective_authority,
)
from .pointed_kernel import CompiledParameterizedKernel
from .principal_greatest_region import (
    PrincipalNoGreatestRegionWitness,
    build_principal_no_greatest_region_witness,
)
from .safety import FiniteSafetyGame

Q = (0, 1, 2)
State = tuple[int, ...]


def q_discriminator(x: int, y: int, z: int) -> int:
    return z if x == y else x


def q_unary(x: int) -> int:
    return (1, 0, 1)[x]


def quackenbush_q() -> FiniteAlgebra:
    return FiniteAlgebra.from_callables(
        Q,
        {"d": (3, q_discriminator), "u": (1, q_unary)},
    )


def binary_complement(state: State) -> State:
    if any(value not in (0, 1) for value in state):
        raise ValueError("binary complement requires a {0,1}-valued state")
    return tuple(1 - value for value in state)


def complement_pairs(state_arity: int) -> tuple[tuple[State, State], ...]:
    if state_arity < 1:
        raise ValueError("state arity must be positive")
    seen: set[State] = set()
    pairs: list[tuple[State, State]] = []
    for state in product((0, 1), repeat=state_arity):
        if state in seen:
            continue
        other = binary_complement(state)
        seen.add(state)
        seen.add(other)
        pairs.append((state, other))
    return tuple(pairs)


@dataclass(frozen=True)
class ExactAntichainFamily:
    """The exact orientation family underlying the antichain theorem."""

    algebra: FiniteAlgebra
    state_arity: int
    game: FiniteSafetyGame
    live: State
    dead: State
    neutral_pair: tuple[State, State]
    variable_pairs: tuple[tuple[State, State], ...]
    maximal_domains: tuple[frozenset[State], ...]

    @property
    def variable_count(self) -> int:
        return len(self.variable_pairs)

    @property
    def expected_maximal_count(self) -> int:
        return 1 << self.variable_count

    @property
    def expected_maximal_size(self) -> int:
        return 3**self.state_arity - 2 ** (self.state_arity - 1) + 1

    @property
    def preferred_domain(self) -> frozenset[State]:
        preferred = frozenset(pair[0] for pair in self.variable_pairs)
        common = self.maximal_domains[0] - frozenset(
            value
            for pair in self.variable_pairs
            for value in pair
        )
        return common | preferred

    def preferred_weights(self) -> dict[State, int]:
        """Positive weights with one unique closed-form orientation optimum."""

        weights = {state: 1 for state in self.game.states}
        for index, (preferred, _alternate) in enumerate(self.variable_pairs):
            weights[preferred] += 1 << (index + 1)
        return weights

    def preferred_score(self) -> int:
        weights = self.preferred_weights()
        return sum(weights[state] for state in self.preferred_domain)

    def component_model(self) -> QuasiPrimalDomainModel:
        return compile_quasi_primal_domain_model(self.game)

    def pointed_kernel(self) -> CompiledParameterizedKernel:
        return CompiledParameterizedKernel(
            self.game,
            frozenset(),
            internal_isomorphisms=self.algebra.internal_isomorphisms(),
        )

    def objective_authority(
        self,
        model: QuasiPrimalDomainModel | None = None,
    ) -> ObjectiveAuthority:
        compiled = self.component_model() if model is None else model
        if tuple(compiled.states) != tuple(self.game.states):
            raise ValueError("antichain authority received the wrong component model")
        weights = self.preferred_weights()
        scored = tuple(
            (
                sum(weights[state] for state in domain),
                domain,
            )
            for domain in self.maximal_domains
        )
        best = max(score for score, _domain in scored)
        optimum = tuple(domain for score, domain in scored if score == best)
        if optimum != (self.preferred_domain,):
            raise AssertionError("orientation weights did not produce one optimum")
        return closed_form_objective_authority(
            name="closed_form_antichain",
            model=compiled,
            optimum_score=best,
            optimum_domains=optimum,
            state_weights=weights,
            default_weight=0,
            evidence={
                "state_arity": self.state_arity,
                "variable_count": self.variable_count,
                "maximal_domain_count": len(self.maximal_domains),
                "closed_form_count": self.expected_maximal_count,
                "maximal_domain_size": self.expected_maximal_size,
            },
        )


def build_exact_antichain_family(state_arity: int) -> ExactAntichainFamily:
    """Build the no-clause specialization of the exact fixed-Q antichain.

    Binary states occur in complement pairs.  The first pair is a live/dead
    anchor, the second pair is neutral, and every remaining pair is an
    independent orientation choice.  The dead state has no safe transition at
    input 2.  At each orientation pair, complementary critical observations
    can be controlled only by complementary anchor outputs, so a winning domain
    contains at most one member of the pair.
    """

    if state_arity < 3:
        raise ValueError("the exact antichain family starts at state arity 3")
    algebra = quackenbush_q()
    states = tuple(product(Q, repeat=state_arity))
    inputs = ((0,), (1,), (2,))
    pairs = complement_pairs(state_arity)
    live, dead = pairs[0]
    neutral_pair = pairs[1]
    variable_pairs = pairs[2:]

    anchor_outputs = frozenset((live, dead))
    critical: dict[tuple[State, tuple[int, ...]], frozenset[State]] = {}
    for positive, negative in variable_pairs:
        critical[(positive, (0,))] = anchor_outputs
        critical[(negative, (1,))] = anchor_outputs

    safe_relation = set()
    for state in states:
        for input_value in inputs:
            for output in states:
                if state == dead and input_value == (2,):
                    continue
                required = critical.get((state, input_value))
                if required is not None and output not in required:
                    continue
                safe_relation.add((state, input_value, output))

    game = FiniteSafetyGame(
        algebra,
        state_arity,
        1,
        safe_relation,
    )
    variable_states = frozenset(
        state for pair in variable_pairs for state in pair
    )
    common = frozenset(states) - {dead} - variable_states
    maximal_domains = tuple(
        common
        | frozenset(
            pair[choice]
            for pair, choice in zip(variable_pairs, orientation, strict=True)
        )
        for orientation in product((0, 1), repeat=len(variable_pairs))
    )
    expected_count = 1 << (2 ** (state_arity - 1) - 2)
    expected_size = 3**state_arity - 2 ** (state_arity - 1) + 1
    if len(maximal_domains) != expected_count:
        raise AssertionError("antichain count disagrees with the closed form")
    if any(len(domain) != expected_size for domain in maximal_domains):
        raise AssertionError("antichain domain size disagrees with the closed form")
    if any(dead in domain for domain in maximal_domains):
        raise AssertionError("dead state entered an antichain maximum")
    if any(
        len(domain & frozenset(pair)) != 1
        for domain in maximal_domains
        for pair in variable_pairs
    ):
        raise AssertionError("orientation maximum violated one-per-pair geometry")

    return ExactAntichainFamily(
        algebra=algebra,
        state_arity=state_arity,
        game=game,
        live=live,
        dead=dead,
        neutral_pair=neutral_pair,
        variable_pairs=variable_pairs,
        maximal_domains=maximal_domains,
    )


@dataclass(frozen=True)
class PrincipalBackendFamily:
    """The generic principal-equation no-greatest-region stress instance."""

    algebra: FiniteAlgebra
    witness: PrincipalNoGreatestRegionWitness
    game: FiniteSafetyGame
    model: QuasiPrimalDomainModel

    @property
    def restricted_union(self) -> frozenset[State]:
        return self.witness.left_domain | self.witness.right_domain


def build_principal_backend_family() -> PrincipalBackendFamily:
    algebra = quackenbush_q()
    witness = build_principal_no_greatest_region_witness(algebra)
    if witness is None:
        raise AssertionError("Quackenbush Q unexpectedly had no principal witness")
    game = witness.game(algebra)
    model = compile_quasi_primal_domain_model(game)
    return PrincipalBackendFamily(
        algebra=algebra,
        witness=witness,
        game=game,
        model=model,
    )

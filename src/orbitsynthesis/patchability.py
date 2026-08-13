"""Exact small-carrier oracles for pointed internal-isomorphism extension.

The routines in this module are structural: they do not assert that an input
algebra is quasi-primal.  When quasi-primality is known independently, the
extension property computed here is exactly the demi-semi-primal condition used
by OrbitSynthesis' term-controller theorems.

The implementation is exponential/factorial and is intended as a reference
oracle, counterexample minimizer, and differential-testing backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism

Value = Hashable


@dataclass(frozen=True)
class PatchabilityResult:
    """Minimum named set restoring the internal-isomorphism extension property."""

    size: int
    parameters: frozenset[Value]


@dataclass(frozen=True)
class ExtensionFailure:
    """One pointed internal isomorphism with no pointed global extension."""

    parameters: frozenset[Value]
    isomorphism: InternalIsomorphism


def _fixes(
    isomorphism: InternalIsomorphism,
    parameters: frozenset[Value],
) -> bool:
    mapping = isomorphism.mapping
    return all(mapping.get(value) == value for value in parameters)


def _eligible_pointed_iso(
    isomorphism: InternalIsomorphism,
    parameters: frozenset[Value],
    *,
    nontrivial_only: bool,
) -> bool:
    if nontrivial_only and len(isomorphism.domain) <= 1:
        return False
    if not parameters <= isomorphism.domain:
        return False
    if not parameters <= isomorphism.codomain:
        return False
    return _fixes(isomorphism, parameters)


def _extends(
    partial: InternalIsomorphism,
    automorphism: InternalIsomorphism,
) -> bool:
    partial_mapping = partial.mapping
    auto_mapping = automorphism.mapping
    return all(auto_mapping[value] == image for value, image in partial_mapping.items())


def first_extension_failure(
    algebra: FiniteAlgebra,
    parameters: Iterable[Value] = (),
    *,
    nontrivial_only: bool = True,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> ExtensionFailure | None:
    """Return one pointed internal isomorphism that has no pointed extension.

    ``parameters`` models a pointed enrichment by named carrier constants.
    Eligible subalgebras must contain every named value and eligible internal
    isomorphisms must fix those values pointwise.

    By the standard demi-semi-primal convention, one-element subalgebras are
    ignored when ``nontrivial_only`` is true.
    """

    fixed = frozenset(parameters)
    carrier = frozenset(algebra.values)
    if not fixed <= carrier:
        raise ValueError("parameter outside carrier")

    all_isos = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    automorphisms = tuple(
        iso
        for iso in all_isos
        if iso.domain == carrier
        and iso.codomain == carrier
        and _fixes(iso, fixed)
    )

    for partial in all_isos:
        if not _eligible_pointed_iso(
            partial,
            fixed,
            nontrivial_only=nontrivial_only,
        ):
            continue
        if not any(_extends(partial, automorphism) for automorphism in automorphisms):
            return ExtensionFailure(parameters=fixed, isomorphism=partial)

    return None


def has_pointed_extension_property(
    algebra: FiniteAlgebra,
    parameters: Iterable[Value] = (),
    *,
    nontrivial_only: bool = True,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> bool:
    """Whether every eligible pointed internal isomorphism extends globally."""

    return first_extension_failure(
        algebra,
        parameters,
        nontrivial_only=nontrivial_only,
        internal_isomorphisms=internal_isomorphisms,
    ) is None


def parameter_patchability_number(
    algebra: FiniteAlgebra,
    *,
    nontrivial_only: bool = True,
    max_parameters: int | None = None,
) -> PatchabilityResult:
    """Find a smallest named set restoring the extension property exactly.

    This is the repository's provisional ``kappa_patch`` oracle.  The first
    lexicographic minimum under the carrier's declared order is returned when
    several minimum parameter sets exist.
    """

    all_isos = algebra.internal_isomorphisms()
    carrier = tuple(algebra.values)
    limit = len(carrier) if max_parameters is None else min(max_parameters, len(carrier))

    for size in range(limit + 1):
        for chosen in combinations(carrier, size):
            if has_pointed_extension_property(
                algebra,
                chosen,
                nontrivial_only=nontrivial_only,
                internal_isomorphisms=all_isos,
            ):
                return PatchabilityResult(
                    size=size,
                    parameters=frozenset(chosen),
                )

    raise ValueError(
        "no good parameter set found within max_parameters; "
        "increase the search limit"
    )

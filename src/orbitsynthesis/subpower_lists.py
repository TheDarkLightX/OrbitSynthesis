"""List-constrained generated-subpower intersection for quasi-primal algebras.

For generators ``g^1,...,g^m`` in ``A^n``, coordinate ``i`` determines the
row ``z_i=(g^1_i,...,g^m_i)``.  A generated vector is exactly
``(t(z_i))_i`` for one ``m``-ary term operation ``t``.

When ``A`` is finite quasi-primal, partial term interpolation factors over the
connected components of the internal-isomorphism groupoid on the distinct
rows.  One value at a component representative propagates uniquely through
that component, because each row generates its own subalgebra.  This module
implements that exact criterion and returns either a witness or a compact
component obstruction.

The caller is responsible for establishing quasi-primality.  The algorithm is
still a useful consistency checker on arbitrary finite algebras, but its
completeness theorem uses the classical Pixley characterization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Sequence

from .finite_algebra import FiniteAlgebra, InternalIsomorphism

Value = Hashable
Row = tuple[Value, ...]
Vector = tuple[Value, ...]


@dataclass(frozen=True)
class CandidateRejection:
    """Why one representative value cannot satisfy a groupoid component."""

    candidate: Value
    violated_positions: tuple[int, ...]
    structural_reason: str | None = None


@dataclass(frozen=True)
class ListSubpowerWitness:
    """A generated-subpower vector meeting every coordinate list."""

    evaluation_vector: Vector
    row_values: tuple[tuple[Row, Value], ...]
    component_choices: tuple[tuple[Row, Value, tuple[Row, ...]], ...]


@dataclass(frozen=True)
class ListSubpowerObstruction:
    """One groupoid component with no list-compatible representative value."""

    positions: tuple[int, ...]
    rows: tuple[Row, ...]
    candidate_rejections: tuple[CandidateRejection, ...]


@dataclass(frozen=True)
class ListSubpowerResult:
    """Exact quasi-primal list-intersection result."""

    feasible: bool
    witness: ListSubpowerWitness | None = None
    obstruction: ListSubpowerObstruction | None = None


def _stable(values: Iterable[object]) -> tuple:
    return tuple(sorted(values, key=repr))


def _build_row_groupoid(
    rows: Sequence[Row],
    internal_isomorphisms: Sequence[InternalIsomorphism],
) -> tuple[
    dict[Row, tuple[tuple[Row, InternalIsomorphism], ...]],
    dict[Row, frozenset[Row]],
]:
    distinct = tuple(dict.fromkeys(rows))
    row_set = set(distinct)
    directed: dict[Row, list[tuple[Row, InternalIsomorphism]]] = {
        row: [] for row in distinct
    }
    undirected: dict[Row, set[Row]] = {row: set() for row in distinct}

    for isomorphism in internal_isomorphisms:
        for row in distinct:
            if not isomorphism.applies_to(row):
                continue
            target = isomorphism.map_tuple(row)
            if target not in row_set:
                continue
            directed[row].append((target, isomorphism))
            undirected[row].add(target)
            undirected[target].add(row)

    return (
        {row: tuple(edges) for row, edges in directed.items()},
        {row: frozenset(neighbors) for row, neighbors in undirected.items()},
    )


def _component(
    representative: Row,
    neighbors: dict[Row, frozenset[Row]],
) -> frozenset[Row]:
    reached: set[Row] = set()
    stack = [representative]
    while stack:
        row = stack.pop()
        if row in reached:
            continue
        reached.add(row)
        stack.extend(neighbors[row] - reached)
    return frozenset(reached)


def _propagate_candidate(
    representative: Row,
    candidate: Value,
    component: frozenset[Row],
    edges: dict[Row, tuple[tuple[Row, InternalIsomorphism], ...]],
) -> tuple[dict[Row, Value] | None, str | None]:
    assigned: dict[Row, Value] = {representative: candidate}
    queue = [representative]

    while queue:
        source = queue.pop()
        source_value = assigned[source]
        for target, isomorphism in edges[source]:
            if source_value not in isomorphism.domain:
                return None, (
                    "candidate left the source row's generated subalgebra "
                    "before transport"
                )
            target_value = isomorphism.map_value(source_value)
            previous = assigned.get(target)
            if previous is not None:
                if previous != target_value:
                    return None, "inconsistent internal-isomorphism cycle"
                continue
            assigned[target] = target_value
            queue.append(target)

    if set(assigned) != set(component):
        return None, "directed groupoid traversal did not cover the component"
    return assigned, None


def quasi_primal_list_subpower_intersection(
    algebra: FiniteAlgebra,
    generators: Sequence[Sequence[Value]],
    coordinate_lists: Sequence[Iterable[Value]],
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> ListSubpowerResult:
    """Decide whether a generated subpower meets a Cartesian product of lists.

    Parameters
    ----------
    algebra:
        A finite algebra known by the caller to be quasi-primal.
    generators:
        A nonempty sequence of equally long vectors in ``A^n``.
    coordinate_lists:
        One allowed unary list for each of the ``n`` coordinates.
    internal_isomorphisms:
        Optional precomputed groupoid, useful when solving many instances.

    Returns
    -------
    ``ListSubpowerResult``
        A concrete generated evaluation vector when feasible; otherwise one
        connected component whose every possible representative value is
        rejected.

    Notes
    -----
    Empty generator sets require a separate nullary-term convention and are
    deliberately outside this first kernel.
    """

    listed = tuple(frozenset(values) for values in coordinate_lists)
    coordinate_count = len(listed)
    generator_vectors = tuple(tuple(vector) for vector in generators)
    carrier = frozenset(algebra.values)

    if not generator_vectors:
        raise ValueError("at least one generated-subpower generator is required")
    if any(len(vector) != coordinate_count for vector in generator_vectors):
        raise ValueError("every generator must have one value per coordinate")
    if any(value not in carrier for vector in generator_vectors for value in vector):
        raise ValueError("generator value outside the algebra carrier")
    if any(not values <= carrier for values in listed):
        raise ValueError("coordinate list contains a value outside the carrier")

    if coordinate_count == 0:
        return ListSubpowerResult(
            feasible=True,
            witness=ListSubpowerWitness(
                evaluation_vector=(),
                row_values=(),
                component_choices=(),
            ),
        )

    empty_positions = tuple(index for index, values in enumerate(listed) if not values)
    if empty_positions:
        return ListSubpowerResult(
            feasible=False,
            obstruction=ListSubpowerObstruction(
                positions=empty_positions,
                rows=(),
                candidate_rejections=(),
            ),
        )

    # Transpose the generators.  Row i is the input tuple at which the one
    # shared term is evaluated to obtain generated-subpower coordinate i.
    rows: tuple[Row, ...] = tuple(
        tuple(vector[index] for vector in generator_vectors)
        for index in range(coordinate_count)
    )
    distinct_rows = tuple(dict.fromkeys(rows))
    positions_by_row: dict[Row, tuple[int, ...]] = {
        row: tuple(index for index, observed in enumerate(rows) if observed == row)
        for row in distinct_rows
    }

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    edges, neighbors = _build_row_groupoid(rows, all_isomorphisms)

    assigned_rows: dict[Row, Value] = {}
    choices: list[tuple[Row, Value, tuple[Row, ...]]] = []
    seen: set[Row] = set()

    for representative in distinct_rows:
        if representative in seen:
            continue
        component = _component(representative, neighbors)
        seen.update(component)

        rejections: list[CandidateRejection] = []
        selected: dict[Row, Value] | None = None

        for candidate in _stable(algebra.generated_subalgebra(representative)):
            propagated, structural_reason = _propagate_candidate(
                representative,
                candidate,
                component,
                edges,
            )
            if propagated is None:
                rejections.append(
                    CandidateRejection(
                        candidate=candidate,
                        violated_positions=(),
                        structural_reason=structural_reason,
                    )
                )
                continue

            violated = tuple(
                sorted(
                    index
                    for row, value in propagated.items()
                    for index in positions_by_row[row]
                    if value not in listed[index]
                )
            )
            if violated:
                rejections.append(
                    CandidateRejection(
                        candidate=candidate,
                        violated_positions=violated,
                    )
                )
                continue

            selected = propagated
            break

        if selected is None:
            component_positions = tuple(
                sorted(
                    index
                    for row in component
                    for index in positions_by_row[row]
                )
            )
            return ListSubpowerResult(
                feasible=False,
                obstruction=ListSubpowerObstruction(
                    positions=component_positions,
                    rows=_stable(component),
                    candidate_rejections=tuple(rejections),
                ),
            )

        assigned_rows.update(selected)
        choices.append(
            (
                representative,
                selected[representative],
                _stable(component),
            )
        )

    evaluation = tuple(assigned_rows[row] for row in rows)
    return ListSubpowerResult(
        feasible=True,
        witness=ListSubpowerWitness(
            evaluation_vector=evaluation,
            row_values=tuple(
                sorted(assigned_rows.items(), key=lambda item: repr(item[0]))
            ),
            component_choices=tuple(choices),
        ),
    )


def verify_list_subpower_witness(
    algebra: FiniteAlgebra,
    generators: Sequence[Sequence[Value]],
    coordinate_lists: Sequence[Iterable[Value]],
    witness: ListSubpowerWitness,
    *,
    internal_isomorphisms: Sequence[InternalIsomorphism] | None = None,
) -> bool:
    """Check the finite groupoid certificate carried by a returned witness.

    Under the caller's quasi-primality premise, these checks certify generated
    subpower membership through the partial interpolation theorem.
    """

    listed = tuple(frozenset(values) for values in coordinate_lists)
    vectors = tuple(tuple(vector) for vector in generators)
    if not vectors or any(len(vector) != len(listed) for vector in vectors):
        return False
    rows = tuple(
        tuple(vector[index] for vector in vectors)
        for index in range(len(listed))
    )
    if len(witness.evaluation_vector) != len(rows):
        return False
    if any(
        value not in listed[index]
        for index, value in enumerate(witness.evaluation_vector)
    ):
        return False

    row_values = dict(witness.row_values)
    if any(row not in row_values for row in rows):
        return False
    if tuple(row_values[row] for row in rows) != witness.evaluation_vector:
        return False
    if any(
        row_values[row] not in algebra.generated_subalgebra(row)
        for row in set(rows)
    ):
        return False

    all_isomorphisms = tuple(
        internal_isomorphisms
        if internal_isomorphisms is not None
        else algebra.internal_isomorphisms()
    )
    row_set = set(rows)
    for isomorphism in all_isomorphisms:
        for row in row_set:
            if not isomorphism.applies_to(row):
                continue
            target = isomorphism.map_tuple(row)
            if target not in row_set:
                continue
            value = row_values[row]
            if value not in isomorphism.domain:
                return False
            if row_values[target] != isomorphism.map_value(value):
                return False
    return True

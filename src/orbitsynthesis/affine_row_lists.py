"""Exact Boolean-group row-list interpolation via an affine exception quotient.

Original independent implementation, MIT license. Python >= 3.10, stdlib only.
A controller is a homogeneous linear map F_2^n -> F_2^k (XOR and zero).
Matrices are packed by output row: coefficient (j, i) is bit j*n + i.
This is not a solver for arbitrary Boolean-algebra term controllers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Iterable, Literal


@dataclass(frozen=True)
class Row:
    observation: int
    allowed: tuple[int, ...]


@dataclass(frozen=True)
class Result:
    status: Literal["sat", "unsat", "unsupported"]
    witness: int | None
    solution_count: int | None
    affine_dimension: int | None
    exception_dimension: int | None
    exceptional_rows: int
    image_points_checked: int
    accepted_image_points: int | None
    instance_sha256: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def _positive(value: int, name: str) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer, not bool")


def _bits(value: int, width: int, name: str) -> None:
    if type(value) is not int or value < 0 or value.bit_length() > width:
        raise ValueError(f"{name} must be an unsigned {width}-bit integer, not bool")


def normalize(n: int, k: int, rows: Iterable[Row]) -> tuple[Row, ...]:
    """Intersect repeated-observation lists; order and duplicates are irrelevant."""
    _positive(n, "n")
    _positive(k, "k")
    merged: dict[int, set[int]] = {}
    for row in rows:
        if not isinstance(row, Row):
            raise TypeError("rows must contain Row objects")
        _bits(row.observation, n, "observation")
        allowed = set()
        for y in row.allowed:
            _bits(y, k, "allowed output")
            allowed.add(y)
        if row.observation in merged:
            merged[row.observation].intersection_update(allowed)
        else:
            merged[row.observation] = allowed
    return tuple(Row(z, tuple(sorted(ys))) for z, ys in sorted(merged.items()))


def _evaluate(n: int, k: int, matrix: int, z: int) -> int:
    return sum((((matrix >> (n*j)) & z).bit_count() & 1) << j for j in range(k))


def evaluate(n: int, k: int, matrix: int, observation: int) -> int:
    _positive(n, "n")
    _positive(k, "k")
    _bits(matrix, n*k, "matrix")
    _bits(observation, n, "observation")
    return _evaluate(n, k, matrix, observation)


def verify_controller(n: int, k: int, rows: Iterable[Row], matrix: int) -> bool:
    normalized = normalize(n, k, rows)
    _bits(matrix, n*k, "matrix")
    return all(_evaluate(n, k, matrix, r.observation) in r.allowed for r in normalized)


def _linear_solve(width: int, equations: Iterable[tuple[int, int]]) -> tuple[int, tuple[int, ...]] | None:
    """Incremental exact RREF; particular solution and a kernel basis."""
    pivots: dict[int, tuple[int, int]] = {}
    for mask, rhs in equations:
        # Eliminate ALL established pivots before choosing a new one.
        for p in sorted(pivots):
            if (mask >> p) & 1:
                old, val = pivots[p]
                mask ^= old
                rhs ^= val
        if mask == 0:
            if rhs:
                return None
            continue
        p = (mask & -mask).bit_length() - 1
        for old_p, (old, val) in tuple(pivots.items()):
            if (old >> p) & 1:
                pivots[old_p] = (old ^ mask, val ^ rhs)
        pivots[p] = (mask, rhs)
    particular = sum(rhs << p for p, (_, rhs) in pivots.items())
    kernel = []
    for f in range(width):
        if f not in pivots:
            kernel.append((1 << f) | sum(((mask >> f) & 1) << p for p, (mask, _) in pivots.items()))
    return particular, tuple(kernel)


def _hull(allowed: tuple[int, ...], k: int) -> tuple[tuple[tuple[int, int], ...], bool]:
    """Return affine-hull equations and whether the list equals its hull."""
    anchor = allowed[0]
    solved = _linear_solve(k, ((y ^ anchor, 0) for y in allowed))
    if solved is None:
        raise RuntimeError("a homogeneous linear system was inconsistent")
    _, normals = solved
    dimension = k - len(normals)
    equations = tuple((h, (h & anchor).bit_count() & 1) for h in normals)
    return equations, len(allowed) == (1 << dimension)


def _image_basis(vectors: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Independent image vectors with matching coefficient-space lifts."""
    basis: dict[int, tuple[int, int]] = {}
    for image, lift in vectors:
        for p in sorted(basis):
            if (image >> p) & 1:
                old_image, old_lift = basis[p]
                image ^= old_image
                lift ^= old_lift
        if image:
            p = (image & -image).bit_length() - 1
            basis[p] = (image, lift)
    return tuple(basis[p] for p in sorted(basis))


def solve(
    n: int,
    k: int,
    rows: Iterable[Row],
    *,
    count: bool = True,
    max_image_points: int = 1 << 20,
) -> Result:
    """Solve exactly, or fail closed as unsupported before exponential search.

    All-affine instances have zero exception dimension and need one image test.
    Counts are numbers of distinct linear maps, NOT counts of syntactic XOR terms.
    When count=False, a SAT result stops at its first independently checked witness.
    A budget miss is not evidence of infeasibility. Preprocessing itself is not
    resource-capped; bound n, k and the explicit input size at an untrusted boundary.
    """
    normalized = normalize(n, k, rows)
    if type(count) is not bool:
        raise ValueError("count must be bool")
    _positive(max_image_points, "max_image_points")
    packet = {"n": n, "k": k, "rows": [(r.observation, r.allowed) for r in normalized]}
    digest = sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if any(not r.allowed for r in normalized):
        return Result("unsat", None, 0, None, None, 0, 0, 0, digest, "empty row list")
    exceptions = []
    equations = []
    for row in normalized:
        normals, is_affine = _hull(row.allowed, k)
        if not is_affine:
            exceptions.append(row)
        for h, rhs in normals:
            mask = sum(row.observation << (n*j) for j in range(k) if (h >> j) & 1)
            equations.append((mask, rhs))
    affine = _linear_solve(n*k, equations)
    if affine is None:
        return Result("unsat", None, 0, None, None, len(exceptions), 0, 0, digest,
                      "inconsistent affine relaxation")
    particular, kernel = affine
    free = len(kernel)
    def image(v: int) -> int:
        return sum(_evaluate(n, k, v, r.observation) << (k*i) for i, r in enumerate(exceptions))
    basis = _image_basis((image(v), v) for v in kernel)
    dimension = len(basis)
    total = 1 << dimension
    if total > max_image_points:
        return Result("unsupported", None, None, free, dimension, len(exceptions), 0, None,
                      digest, "exception-image budget exceeded; feasibility unknown")
    output_mask = (1 << k) - 1
    allowed_sets = tuple(frozenset(r.allowed) for r in exceptions)
    current_image = image(particular)
    current_matrix = particular
    first_witness = None
    accepted = 0
    checked = 0
    # Gray-code traversal visits every image vector exactly once, with a lift.
    for i in range(total):
        if i:
            j = (i & -i).bit_length() - 1
            delta_image, delta_lift = basis[j]
            current_image ^= delta_image
            current_matrix ^= delta_lift
        checked += 1
        if all(((current_image >> (k*j)) & output_mask) in ys for j, ys in enumerate(allowed_sets)):
            accepted += 1
            if first_witness is None:
                if not verify_controller(n, k, normalized, current_matrix):
                    raise RuntimeError("internal witness failed direct original-list replay")
                first_witness = current_matrix
                if not count:
                    return Result("sat", first_witness, None, free, dimension, len(exceptions),
                                  checked, None, digest, "directly verified linear controller")
    solution_count = accepted << (free - dimension)
    status = "sat" if accepted else "unsat"
    return Result(status, first_witness, solution_count, free, dimension, len(exceptions), checked,
                  accepted, digest, "complete exception-image enumeration")


def solve_safety(
    dimension: int, successors: dict[int, Iterable[int]], **kwargs,
) -> Result:
    """Sparse input-free fixed-domain safety; every listed successor must lie in W."""
    _positive(dimension, "dimension")
    states = set(successors)
    rows = []
    for w, ys in successors.items():
        _bits(w, dimension, "state")
        allowed = tuple(ys)
        for y in allowed:
            _bits(y, dimension, "successor")
            if y not in states:
                raise ValueError("a successor is outside the explicitly fixed domain W")
        rows.append(Row(w, allowed))
    return solve(dimension, dimension, rows, **kwargs)


def xor_terms(n: int, k: int, matrix: int) -> tuple[str, ...]:
    """Readable original-signature controller; no AND/OR or constant one."""
    _positive(n, "n")
    _positive(k, "k")
    _bits(matrix, n*k, "matrix")
    return tuple(" xor ".join(f"x{i}" for i in range(n) if (matrix >> (n*j+i)) & 1) or "0"
                 for j in range(k))

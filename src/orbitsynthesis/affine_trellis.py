"""Exact list-constrained code-trellis backend for XOR/zero term controllers.

Independent MIT implementation. Classical trellis state complexity is prior art;
see notes/AFFINE_TRELLIS_CERTIFICATES.md. Python >= 3.10; standard library only.
The generator is not a trust boundary: verify certificates with the independent
checker and a separately supplied original problem. Counts are linear maps, not
syntactic terms. No full Boolean-algebra, general temporal, or Lean claim.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Iterable
import json

if __package__:
    from .affine_row_lists import Row, normalize, _hull, _linear_solve, _evaluate, verify_controller
else:
    from affine_row_lists import Row, normalize, _hull, _linear_solve, _evaluate, verify_controller

SCHEMA = "orbit-synthesis/affine-trellis-certificate/v1"


def problem_dict(n: int, k: int, rows: Iterable[Row]) -> dict:
    return {"n": n, "k": k, "rows": [[r.observation, list(r.allowed)] for r in normalize(n, k, rows)]}


def _digest(problem: dict) -> str:
    return sha256(json.dumps(problem, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _span(vectors: Iterable[int]) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def _member(vector: int, basis: tuple[int, ...]) -> bool:
    for b in basis:
        if vector & (1 << (b.bit_length() - 1)):
            vector ^= b
    return vector == 0


def _xor_columns(columns: tuple[int, ...], value: int) -> int:
    result = 0
    for j, col in enumerate(columns):
        if (value >> j) & 1:
            result ^= col
    return result


def produce(n: int, k: int, rows: Iterable[Row], *, order: Iterable[int] | None = None,
            max_states: int = 1 << 16, max_transitions: int = 1 << 22) -> dict:
    """Emit exact SAT/UNSAT/count certificate or an explicitly unsupported result.

    order permutes exceptional rows AFTER normalization, not raw rows. Only the
    transfer phase is budgeted; callers must bound input sizes before invocation.
    A budget miss contains no certificate/count/witness. Prefix tables may be
    exponential in cut rank; no polynomial-size general certificate is claimed.
    """
    for name, value in (("max_states", max_states), ("max_transitions", max_transitions)):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    rows = normalize(n, k, rows)
    pin = _digest(problem_dict(n, k, rows))
    common = {"schema": SCHEMA, "instance_sha256": pin}
    if any(not r.allowed for r in rows):
        return {**common, "kind": "empty", "solution_count": 0, "witness": None}
    equations, exceptions = [], []
    for row in rows:
        normals, affine = _hull(row.allowed, k)
        if not affine:
            exceptions.append(row)
        for h, rhs in normals:
            equations.append((sum(row.observation << (n*j) for j in range(k) if (h >> j) & 1), rhs))
    selected = list(range(len(exceptions))) if order is None else list(order)
    if (any(type(i) is not int for i in selected)
            or sorted(selected) != list(range(len(exceptions)))):
        raise ValueError("order must permute exactly the normalized exceptional rows")
    solution = _linear_solve(n*k, equations)
    if solution is None:
        return {**common, "kind": "linear-unsat", "solution_count": 0, "witness": None}
    anchor, kernel = solution
    exceptions = [exceptions[i] for i in selected]
    m = len(exceptions)
    width = m*k
    def project(c: int) -> int:
        return sum(_evaluate(n, k, c, r.observation) << (k*i) for i, r in enumerate(exceptions))
    images = [project(v) for v in kernel]
    parity_result = _linear_solve(width, ((v, 0) for v in images))
    if parity_result is None:
        raise RuntimeError("homogeneous image system inconsistent")
    parity_checks = parity_result[1]
    d = width - len(parity_checks)
    columns = tuple(sum(((h >> t) & 1) << j for j, h in enumerate(parity_checks)) for t in range(width))
    blocks = [columns[k*i:k*(i+1)] for i in range(m)]
    suffix: list[tuple[int, ...]] = [()] * (m+1)
    for i in range(m-1, -1, -1):
        suffix[i] = _span((*blocks[i], *suffix[i+1]))
    prefix: tuple[int, ...] = ()
    cuts = [0]
    for i in range(m):
        prefix = _span((*prefix, *blocks[i]))
        cuts.append(len(prefix) + len(suffix[i+1]) - len(parity_checks))
    packed_anchor = project(anchor)
    counts = {0: 1}
    paths = {0: 0}
    tables = [[[0, 1]]]
    steps, peak = 0, 1
    for i, row in enumerate(exceptions):
        base = (packed_anchor >> (k*i)) & ((1 << k)-1)
        deltas = [(y, _xor_columns(blocks[i], y ^ base)) for y in row.allowed]
        upcoming = len(counts) * len(deltas)
        if steps + upcoming > max_transitions:
            return {**common, "kind": "unsupported", "reason": "transition budget exceeded"}
        steps += upcoming
        nxt: dict[int, int] = {}
        next_paths: dict[int, int] = {}
        for s, number in sorted(counts.items()):
            for y, delta in deltas:
                t = s ^ delta
                if not _member(t, suffix[i+1]):
                    continue
                nxt[t] = nxt.get(t, 0) + number
                if t not in next_paths:
                    next_paths[t] = paths[s] | (y << (k*i))
                if len(nxt) > max_states:
                    return {**common, "kind": "unsupported", "reason": "live-state budget exceeded"}
        counts, paths = nxt, next_paths
        peak = max(peak, len(counts))
        tables.append([[s, c] for s, c in sorted(counts.items())])
    outputs = counts.get(0, 0)
    total = outputs << (len(kernel)-d)
    witness = None
    if outputs:
        prescribed = list(equations)
        word = paths[0]
        for i, row in enumerate(exceptions):
            for j in range(k):
                prescribed.append((row.observation << (n*j), (word >> (k*i+j)) & 1))
        lifted = _linear_solve(n*k, prescribed)
        if lifted is None or not verify_controller(n, k, rows, lifted[0]):
            raise RuntimeError("trellis witness failed original-row replay")
        witness = lifted[0]
    return {**common, "kind": "trellis", "order": selected,
            "affine_dimension": len(kernel), "exception_dimension": d,
            "cut_ranks": cuts, "tables": tables, "transition_checks": steps,
            "peak_live_states": peak, "solution_count": total, "witness": witness}

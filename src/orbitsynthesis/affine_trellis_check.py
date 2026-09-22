"""Independent, fail-closed checker for affine trellis counts and witnesses.

Stdlib only. Deliberately imports neither the producer nor affine_row_lists.
Reconstructs canonical affine semantics and checks every local count recurrence.
This is a separately authored Python checker, NOT a formally verified checker.
"""
from __future__ import annotations

from hashlib import sha256
import json

SCHEMA = "orbit-synthesis/affine-trellis-certificate/v1"


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _integer(x, low: int, high: int, name: str) -> None:
    _need(type(x) is int and low <= x <= high, f"invalid {name}")


def canonical(problem: dict, *, max_coefficients: int = 4096, max_rows: int = 2048,
              max_list_entries: int = 131072) -> dict:
    for v in (max_coefficients, max_rows, max_list_entries):
        _need(type(v) is int and v > 0, "invalid input limit")
    _need(type(problem) is dict and set(problem) == {"n", "k", "rows"}, "problem fields")
    n, k = problem["n"], problem["k"]
    _integer(n, 1, max_coefficients, "n")
    _integer(k, 1, max_coefficients, "k")
    _need(n*k <= max_coefficients, "coefficient limit")
    raw = problem["rows"]
    _need(type(raw) is list and len(raw) <= max_rows, "row limit/type")
    merged, entries = {}, 0
    for row in raw:
        _need(type(row) is list and len(row) == 2, "row shape")
        z, ys = row
        _integer(z, 0, (1 << n)-1, "observation")
        _need(type(ys) is list, "output list type")
        entries += len(ys)
        _need(entries <= max_list_entries, "list entry limit")
        for y in ys:
            _integer(y, 0, (1 << k)-1, "output")
        values = set(ys)
        merged[z] = merged[z] & values if z in merged else values
    return {"n": n, "k": k, "rows": [[z, sorted(ys)] for z, ys in sorted(merged.items())]}


def instance_pin(problem: dict) -> str:
    return sha256(json.dumps(canonical(problem), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_json(path) -> dict:
    """Reject duplicate object keys rather than silently overwriting them."""
    def pairs(items):
        answer = {}
        for key, value in items:
            _need(key not in answer, "duplicate JSON key")
            answer[key] = value
        return answer
    with open(path, encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=pairs)


def _gauss(width: int, equations) -> tuple[int, tuple[int, ...], tuple[int, ...]] | None:
    """Batch Gauss-Jordan, structurally separate from producer's incremental RREF."""
    a = [[mask, rhs] for mask, rhs in equations]
    lead, pivots = 0, []
    for col in range(width):
        selected = next((r for r in range(lead, len(a)) if (a[r][0] >> col) & 1), None)
        if selected is None:
            continue
        a[lead], a[selected] = a[selected], a[lead]
        for r in range(len(a)):
            if r != lead and (a[r][0] >> col) & 1:
                a[r][0] ^= a[lead][0]
                a[r][1] ^= a[lead][1]
        pivots.append(col)
        lead += 1
    if any(mask == 0 and rhs for mask, rhs in a):
        return None
    origin = sum(a[r][1] << p for r, p in enumerate(pivots))
    free = [j for j in range(width) if j not in set(pivots)]
    basis = tuple((1 << j) | sum(((a[r][0] >> j) & 1) << p for r, p in enumerate(pivots))
                  for j in free)
    return origin, basis, tuple(a[r][0] for r in range(lead))


def _dot(x: int, y: int) -> int:
    return (x & y).bit_count() % 2


def _output(n: int, k: int, c: int, z: int) -> int:
    out = 0
    for j in range(k):
        out |= _dot(c >> (n*j), z) << j
    return out


def _residue(v: int, basis: tuple[int, ...]) -> int:
    for b in basis:
        if v & (b & -b):
            v ^= b
    return v


def verify(problem: dict, certificate: dict, *, max_cells: int = 1 << 20,
           max_transitions: int = 1 << 23, max_code_bits: int = 8192) -> dict:
    """Check against the caller's ORIGINAL problem, not an artifact-supplied pin.

    Malformed, incomplete, altered, unsupported and resource-exceeding artifacts
    raise ValueError. Exhaustive coefficient enumeration and producer search are
    never invoked. Count-recurrence replay can cost as much as transfer generation.
    """
    for v in (max_cells, max_transitions, max_code_bits):
        _need(type(v) is int and v > 0, "invalid verification limit")
    p = canonical(problem)
    n, k, rows = p["n"], p["k"], p["rows"]
    _need(type(certificate) is dict, "certificate type")
    _need(certificate.get("schema") == SCHEMA, "certificate schema")
    _need(certificate.get("instance_sha256") == instance_pin(p), "original problem pin mismatch")
    kind = certificate.get("kind")
    _need(kind in ("empty", "linear-unsat", "trellis"), "unsupported/unknown certificate kind")
    fixed = {"schema", "instance_sha256", "kind", "solution_count", "witness"}
    extra = {"order", "affine_dimension", "exception_dimension", "cut_ranks", "tables",
             "transition_checks", "peak_live_states"}
    _need(set(certificate) == (fixed | extra if kind == "trellis" else fixed), "certificate fields")
    count = certificate["solution_count"]
    _integer(count, 0, 1 << (n*k), "solution count")
    if any(not ys for z, ys in rows):
        _need(kind == "empty" and count == 0 and certificate["witness"] is None, "empty-list proof")
        return {"verified": True, "status": "unsat", "solution_count": 0}
    _need(kind != "empty", "no empty original list")
    eqs, exceptional = [], []
    for z, ys in rows:
        hull = _gauss(k, ((y ^ ys[0], 0) for y in ys))
        _need(hull is not None, "homogeneous hull failure")
        normals = hull[1]
        if len(ys) != 1 << (k-len(normals)):
            exceptional.append((z, ys))
        for h in normals:
            rowmask = 0
            for j in range(k):
                if (h >> j) & 1:
                    rowmask |= z << (n*j)
            eqs.append((rowmask, _dot(h, ys[0])))
    affine = _gauss(n*k, eqs)
    if affine is None:
        _need(kind == "linear-unsat" and count == 0 and certificate["witness"] is None,
              "linear inconsistency proof")
        return {"verified": True, "status": "unsat", "solution_count": 0}
    _need(kind == "trellis", "affine relaxation is consistent")
    ordering = certificate["order"]
    m = len(exceptional)
    _need(type(ordering) is list and all(type(i) is int for i in ordering)
          and sorted(ordering) == list(range(m)), "incomplete/invalid exceptional-row permutation")
    exceptional = [exceptional[i] for i in ordering]
    origin, generators, _ = affine
    def projected(c):
        packed = 0
        for i, (z, _) in enumerate(exceptional):
            packed |= _output(n, k, c, z) << (k*i)
        return packed
    width = m*k
    _need(width <= max_code_bits, "code width limit")
    dual = _gauss(width, ((projected(v), 0) for v in generators))
    _need(dual is not None, "homogeneous dual failure")
    checks = dual[1]
    d = width-len(checks)
    for key, value in (("affine_dimension", len(generators)), ("exception_dimension", d)):
        _integer(certificate[key], 0, n*k, key)
        _need(certificate[key] == value, f"wrong {key}")
    cols = []
    for i in range(width):
        col = 0
        for j, h in enumerate(checks):
            col |= ((h >> i) & 1) << j
        cols.append(col)
    suffix = [()] * (m+1)
    for i in range(m-1, -1, -1):
        reduced = _gauss(len(checks), ((v, 0) for v in cols[k*i:k*(i+1)] + list(suffix[i+1])))
        suffix[i] = reduced[2]
    prefix, cuts = (), [0]
    for i in range(m):
        prefix = _gauss(len(checks), ((v, 0) for v in list(prefix) + cols[k*i:k*(i+1)]))[2]
        cuts.append(len(prefix)+len(suffix[i+1])-len(checks))
    supplied_cuts = certificate["cut_ranks"]
    _need(type(supplied_cuts) is list and all(type(v) is int for v in supplied_cuts)
          and supplied_cuts == cuts, "wrong cut ranks")
    tables = certificate["tables"]
    _need(type(tables) is list and len(tables) == m+1, "missing/extra layers")
    decoded, cells = [], 0
    for table in tables:
        _need(type(table) is list, "table type")
        cells += len(table)
        _need(cells <= max_cells, "certificate cell limit")
        result, previous = {}, -1
        for item in table:
            _need(type(item) is list and len(item) == 2, "state/count shape")
            s, number = item
            _integer(s, 0, (1 << len(checks))-1, "syndrome")
            _integer(number, 1, 1 << (n*k), "prefix count")
            _need(s > previous, "duplicate/unsorted state")
            previous = s
            result[s] = number
        decoded.append(result)
    _need(decoded[0] == {0: 1}, "initial layer")
    base = projected(origin)
    steps = 0
    for i, (_, ys) in enumerate(exceptional):
        prev = decoded[i]
        steps += len(prev)*len(ys)
        _need(steps <= max_transitions, "verification transition limit")
        required = {}
        center = (base >> (k*i)) & ((1 << k)-1)
        for s, multiplicity in prev.items():
            for y in ys:
                t = s
                for j in range(k):
                    if ((y ^ center) >> j) & 1:
                        t ^= cols[k*i+j]
                if _residue(t, suffix[i+1]) == 0:
                    required[t] = required.get(t, 0) + multiplicity
        _need(decoded[i+1] == required, f"incorrect/incomplete count flow at layer {i+1}")
        _need(len(required) <= 1 << cuts[i+1], "state-width bound")
    expected = decoded[-1].get(0, 0) << (len(generators)-d)
    _need(count == expected, "wrong final count/fiber multiplier")
    for key, expected_value in (("transition_checks", steps), ("peak_live_states", max(map(len, decoded)))):
        _integer(certificate[key], 0, max(max_transitions, max_cells), key)
        _need(certificate[key] == expected_value, f"wrong {key}")
    witness = certificate["witness"]
    if count:
        _integer(witness, 0, (1 << (n*k))-1, "witness")
        _need(all(_output(n, k, witness, z) in ys for z, ys in rows), "original-row witness failure")
    else:
        _need(witness is None, "UNSAT contains witness")
    return {"verified": True, "status": "sat" if count else "unsat", "solution_count": count,
            "affine_dimension": len(generators), "exception_dimension": d,
            "max_cut_rank": max(cuts), "peak_live_states": max(map(len, decoded)),
            "transition_checks": steps, "certificate_cells": cells}

#!/usr/bin/env python3
"""No-import audit of signed WCNF compilation and subprocess optimization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[5]
REFERENCE = (
    ROOT
    / "research/tournaments/2026-08-14-external-maxsat-benchmark"
    / "tools/reference_maxsat_solver.py"
)

FAMILIES = (
    ("split2", 2, ((0, frozenset({1})), (1, frozenset({0})))),
    (
        "choice4",
        4,
        (
            (0, frozenset({2, 3})),
            (1, frozenset({0})),
            (3, frozenset({1, 2})),
        ),
    ),
    (
        "cycle6",
        6,
        (
            (0, frozenset({3, 4, 5})),
            (2, frozenset({0, 5})),
            (4, frozenset({1, 2})),
        ),
    ),
    (
        "pruning9",
        9,
        (
            (0, frozenset({4, 5, 6, 7, 8})),
            (2, frozenset({0, 6, 7})),
            (5, frozenset({1, 2, 8})),
            (8, frozenset({0, 3, 4})),
        ),
    ),
)


def scenarios(n: int):
    return (
        ("unique", tuple(1 << index for index in range(n)), (), ()),
        (
            "signed",
            tuple(
                (index + 2) if index % 2 == 0 else -(index + 1)
                for index in range(n)
            ),
            (),
            (),
        ),
        ("required", tuple(index + 1 for index in range(n)), (0,), ()),
        ("forbidden", tuple(2 * index + 1 for index in range(n)), (), (n - 1,)),
        ("zero", (0,) * n, (), ()),
    )


def candidate_accepts(
    domain: int,
    target: int,
    forbidden: frozenset[int],
    n: int,
) -> bool:
    if any(domain & (1 << source) for source in forbidden):
        return False
    if not domain & (1 << target):
        return domain == 0
    return all(
        not domain & (1 << source) or domain & (1 << target)
        for source in range(n)
        if source not in forbidden
    )


def domain_optimum(n, candidates, weights, required, forbidden):
    required_mask = sum(1 << index for index in required)
    forbidden_mask = sum(1 << index for index in forbidden)
    best = None
    for domain in range(1 << n):
        if required_mask & ~domain or forbidden_mask & domain:
            continue
        if not any(
            candidate_accepts(domain, target, bad, n)
            for target, bad in candidates
        ):
            continue
        score = sum(
            weights[index]
            for index in range(n)
            if domain & (1 << index)
        )
        key = (score, domain.bit_count(), domain)
        if best is None or key > best:
            best = key
    return best


def build_wcnf(n, candidates, weights, required, forbidden):
    variable_count = n + len(candidates)
    hard = []
    selectors = tuple(n + index + 1 for index in range(len(candidates)))
    hard.append(selectors)
    for candidate_index, (target, bad) in enumerate(candidates):
        selector = n + candidate_index + 1
        for source in bad:
            hard.append((-selector, -(source + 1)))
        for source in range(n):
            if source in bad or source == target:
                continue
            hard.append((-selector, -(source + 1), target + 1))
    hard.extend((index + 1,) for index in required)
    hard.extend((-(index + 1),) for index in forbidden)
    soft = tuple(
        ((index + 1 if weight > 0 else -(index + 1)), abs(weight))
        for index, weight in enumerate(weights)
        if weight != 0
    )
    top = sum(weight for _literal, weight in soft) + 1
    return variable_count, tuple(hard), soft, top


def literal_value(mask: int, literal: int) -> bool:
    value = bool(mask & (1 << (abs(literal) - 1)))
    return value if literal > 0 else not value


def assignment_optimum(variable_count, hard, soft):
    best = None
    for mask in range(1 << variable_count):
        if any(
            not any(literal_value(mask, literal) for literal in clause)
            for clause in hard
        ):
            continue
        cost = sum(
            weight
            for literal, weight in soft
            if not literal_value(mask, literal)
        )
        key = (cost, -mask)
        if best is None or key < best[0]:
            best = key, mask, cost
    return None if best is None else (best[1], best[2])


def render_wcnf(variable_count, hard, soft, top):
    lines = [f"p wcnf {variable_count} {len(hard) + len(soft)} {top}"]
    lines.extend(
        f"{top} " + " ".join(map(str, clause)) + " 0"
        for clause in hard
    )
    lines.extend(f"{weight} {literal} 0" for literal, weight in soft)
    return "\n".join(lines) + "\n"


def parse_process_output(text: str):
    cost = None
    literals = []
    status = "unknown"
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("o "):
            cost = int(line.split()[1])
        elif line.startswith("s "):
            status = line[2:].strip()
        elif line.startswith("v "):
            literals.extend(
                int(value)
                for value in line.split()[1:]
                if value != "0"
            )
    return status, cost, tuple(literals)


def main() -> int:
    rows = []
    for family, n, candidates in FAMILIES:
        for scenario, weights, required, forbidden in scenarios(n):
            domain_best = domain_optimum(
                n, candidates, weights, required, forbidden
            )
            variable_count, hard, soft, top = build_wcnf(
                n, candidates, weights, required, forbidden
            )
            assignment_best = assignment_optimum(variable_count, hard, soft)
            if (domain_best is None) != (assignment_best is None):
                raise AssertionError("domain/WCNF feasibility mismatch")

            if domain_best is None:
                expected_cost = None
            else:
                expected_utility = domain_best[0]
                negative_offset = sum(-weight for weight in weights if weight < 0)
                total_soft = sum(weight for _literal, weight in soft)
                expected_cost = total_soft - (negative_offset + expected_utility)
                if assignment_best[1] != expected_cost:
                    raise AssertionError("signed utility/WCNF objective mismatch")

            with tempfile.TemporaryDirectory(
                prefix="orbit-independent-"
            ) as directory:
                path = Path(directory) / "case.wcnf"
                path.write_text(
                    render_wcnf(variable_count, hard, soft, top),
                    encoding="utf-8",
                )
                completed = subprocess.run(
                    [sys.executable, str(REFERENCE), str(path)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            status, process_cost, process_literals = parse_process_output(
                completed.stdout
            )
            if domain_best is None:
                if status != "UNSATISFIABLE":
                    raise AssertionError("reference process missed infeasibility")
            else:
                if status != "OPTIMUM FOUND" or process_cost != expected_cost:
                    raise AssertionError("reference process objective mismatch")
                if len(process_literals) != variable_count:
                    raise AssertionError("reference process returned a partial model")

            rows.append(
                (
                    family,
                    scenario,
                    domain_best,
                    expected_cost,
                    status,
                    process_cost,
                )
            )

    result = {
        "schema": "orbit-synthesis/external-optimization-independent/v1",
        "families": len(FAMILIES),
        "instances": len(rows),
        "rows_sha256": hashlib.sha256(repr(tuple(rows)).encode()).hexdigest(),
        "rows": rows,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["semantic_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

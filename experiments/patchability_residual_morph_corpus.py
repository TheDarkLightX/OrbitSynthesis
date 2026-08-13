#!/usr/bin/env python3
"""Emit the Morph finite corpus for six-element patchability residuals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.patchability_residual import build_patchability_residual_automaton  # noqa: E402


def corpus() -> dict[str, object]:
    carrier = tuple(range(6))
    machine = build_patchability_residual_automaton(
        carrier,
        ((3, 4, 5), (0, 1, 2, 5), (0, 1, 2, 3, 4)),
    )
    queries = [f"future_{mask:02d}" for mask in range(1 << 6)]
    objects = []
    for chosen in range(1 << 6):
        state = machine.run(i for i in carrier if chosen & (1 << i))
        answers = {
            query: machine.accepts(
                (i for i in carrier if extension & (1 << i)),
                start=state,
            )
            for query, extension in zip(queries, range(1 << 6), strict=True)
        }
        objects.append(
            {
                "id": f"C_{chosen:02x}",
                "abstract": f"unhit_{state:03b}",
                "answers": answers,
            }
        )
    operations = {
        f"add_{value}": {
            f"C_{chosen:02x}": f"C_{chosen | (1 << value):02x}"
            for chosen in range(1 << 6)
        }
        for value in carrier
    }
    return {
        "schema": "minimum-sufficient-abstraction/finite-corpus/v1",
        "claim_id": "patchability-residual-star-six-v1",
        "require_minimal": True,
        "queries": queries,
        "objects": objects,
        "operations": operations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(corpus(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

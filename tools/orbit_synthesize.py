#!/usr/bin/env python3
"""Command-line entry point for the practical OrbitSynthesis v1 pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from orbitsynthesis.practical import synthesize_model, verify_certificate
from orbitsynthesis.practical_examples import example_model


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze controller semantics, synthesize a clone-compatible domain, "
            "and compile a conservative Q strategy to a proof-carrying DAG."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="finite-algebra safety model JSON")
    source.add_argument(
        "--example",
        choices=("discriminator", "coupling"),
        help="built-in deterministic example",
    )
    parser.add_argument("--out", type=Path, help="write certificate JSON")
    parser.add_argument(
        "--model-out",
        type=Path,
        help="write the normalized input model JSON",
    )
    parser.add_argument(
        "--quasi-search",
        choices=("exhaustive", "nogood", "bitset_nogood"),
        default="bitset_nogood",
    )
    parser.add_argument(
        "--verify",
        type=Path,
        help="verify an existing certificate instead of emitting a new one",
    )
    args = parser.parse_args()

    model = load_json(args.input) if args.input else example_model(args.example)
    if args.model_out:
        args.model_out.write_text(
            json.dumps(model, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.verify:
        certificate = load_json(args.verify)
        verify_certificate(model, certificate, quasi_search=args.quasi_search)
        print(json.dumps({"status": "VERIFIED"}, sort_keys=True))
        return 0

    certificate = synthesize_model(model, quasi_search=args.quasi_search)
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

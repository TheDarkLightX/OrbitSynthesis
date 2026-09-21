#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check a finite controller against a separately pinned contract."""

import argparse
import json
import sys
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orbitsynthesis.strategy_checker import MAX_BYTES, Accepted, RejectCode, verify


def read_bounded(path: Path) -> bytes:
    with path.open("rb") as stream:
        return stream.read(MAX_BYTES + 1)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check finite-controller safety and recurring progress for every input sequence.")
    parser.add_argument("contract", type=Path, help="canonical contract JSON")
    parser.add_argument("strategy", type=Path, help="canonical Mealy-strategy JSON")
    pins = parser.add_mutually_exclusive_group(required=True)
    pins.add_argument("--contract-sha256", help="expected hash from your reviewed contract")
    pins.add_argument("--contract-pin", type=Path, help="text file containing your reviewed contract hash")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable verification record")
    args = parser.parse_args(argv)
    try:
        pin = args.contract_sha256
        if args.contract_pin is not None:
            with args.contract_pin.open("r", encoding="ascii") as stream:
                pin = stream.read(128).strip()
                if stream.read(1):
                    raise ValueError("contract pin file exceeds 128 characters")
        verdict = verify(read_bounded(args.contract), read_bounded(args.strategy), pin)
    except (OSError, UnicodeError, ValueError) as error:
        if args.json:
            print(json.dumps({"accepted": False, "code": "file_error", "detail": str(error)}, sort_keys=True))
        else:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    accepted = isinstance(verdict, Accepted)
    result = {"schema": "orbitsynthesis/finite-controller-check/v1", "accepted": accepted,
              "checker_sha256": sha256((ROOT / "src/orbitsynthesis/strategy_checker.py").read_bytes()).hexdigest(),
              "runtime_refinement_verified": False, "tau_execution_performed": False,
              **asdict(verdict)}
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    elif accepted:
        print("ACCEPT: the controller satisfies the finite contract for every input sequence.")
        print(f"Checked {verdict.reachable_product_states} reachable product states, "
              f"{verdict.checked_product_edges} transitions, "
              f"{verdict.checked_recurrence_sets} recurring-progress goals.")
    else:
        print(f"REJECT [{verdict.code.value}]: {verdict.detail}")
        for label, path in (("prefix", verdict.prefix), ("repeating cycle", verdict.cycle)):
            if path:
                print(f"{label}:")
                for edge in path:
                    print(f"  plant={edge.plant}, memory={edge.memory}, input={edge.input} "
                          f"-> output={edge.output}, plant={edge.next_plant}, memory={edge.next_memory}")
        if verdict.recurrence_index is not None:
            print(f"Recurring-progress goal {verdict.recurrence_index} is starved by this cycle.")
    if accepted:
        return 0
    semantic = {RejectCode.UNSAFE_INITIAL, RejectCode.UNSAFE_STEP, RejectCode.RECURRENCE}
    return 1 if verdict.code in semantic else 2


if __name__ == "__main__":
    raise SystemExit(main())

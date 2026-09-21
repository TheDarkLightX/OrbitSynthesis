# SPDX-License-Identifier: MIT
"""Recheck an OSMC controller image, then replay inputs without application effects."""

import argparse
import json
import sys
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orbitsynthesis.controller_runtime import (
    MAX_IMAGE_BYTES,
    CheckedController,
    StepRejected,
    load_controller,
)
from orbitsynthesis.strategy_checker import MAX_BYTES


def read_bounded(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        return stream.read(limit + 1)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("strategy", type=Path)
    parser.add_argument("program", type=Path, help="OSMC v1 table image")
    pins = parser.add_mutually_exclusive_group(required=True)
    pins.add_argument("--contract-sha256", help="independently retained model hash")
    pins.add_argument("--contract-pin", type=Path, help="file with the independently retained model hash")
    parser.add_argument("--inputs", nargs="*", type=int, default=[], help="up to 4096 input IDs to replay")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if len(args.inputs) > 4096:
            raise ValueError("input trace exceeds 4096 steps")
        pin = args.contract_sha256
        if args.contract_pin is not None:
            raw_pin = read_bounded(args.contract_pin, 128)
            if len(raw_pin) > 128:
                raise ValueError("model pin exceeds 128 bytes")
            pin = raw_pin.decode("ascii").strip()
        loaded = load_controller(read_bounded(args.contract, MAX_BYTES),
                                 read_bounded(args.strategy, MAX_BYTES),
                                 read_bounded(args.program, MAX_IMAGE_BYTES), pin)
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"accepted": False, "code": "file_or_argument_error", "detail": str(error)}))
        return 2
    if not isinstance(loaded, CheckedController):
        print(json.dumps({"accepted": False, **asdict(loaded)}, sort_keys=True))
        return 1
    memory, trace = loaded.initial_memory, []
    for event in args.inputs:
        outcome = loaded.step(memory, event)
        if isinstance(outcome, StepRejected):
            print(json.dumps({"accepted": False, "code": outcome.code, "input_index": len(trace)}))
            return 2
        trace.append({"memory": memory, "input": event, **asdict(outcome)})
        memory = outcome.next_memory
    source_paths = [ROOT / "src/orbitsynthesis/controller_runtime.py",
                    ROOT / "src/orbitsynthesis/strategy_checker.py", Path(__file__).resolve()]
    record = {"schema": "orbitsynthesis/table-controller-replay/v1", "accepted": True,
              "verification": asdict(loaded.receipt), "trace": trace,
              "table_runtime_equivalence_verified": True, "application_effects_executed": False,
              "native_codegen_verified": False, "tau_execution_performed": False,
              "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                for p in source_paths}}
    if args.json:
        print(json.dumps(record, sort_keys=True, indent=2))
    else:
        print(f"ACCEPT: table runtime matches all {loaded.receipt.checked_memory_input_pairs} strategy rows.")
        for row in trace:
            print(f"memory={row['memory']}, input={row['input']} -> output={row['output']}, "
                  f"memory={row['next_memory']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

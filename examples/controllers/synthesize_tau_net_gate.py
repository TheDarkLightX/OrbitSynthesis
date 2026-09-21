# SPDX-License-Identifier: MIT
"""Build and independently check a small gate intended for a Tau Net application."""

import argparse
import json
import sys
from dataclasses import asdict
from hashlib import sha256
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from orbitsynthesis.controller_compile import compile_table_image
from orbitsynthesis.controller_runtime import CheckedController, load_controller
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.safety import FiniteSafetyGame
from orbitsynthesis.safety_export import export_contract, export_strategy
from orbitsynthesis.strategy_checker import Rejected, verify


def application_game():
    """Choose exactly one eligible action if any exists; otherwise choose none.

Two input bits report eligibility determined by the application's trusted
adapter. Two output bits select actions. This model does not determine actual
eligibility, execute actions or guarantee eventual selection of both actions.
"""
    values = (0, 1)
    states = tuple(product(values, repeat=2))
    relation = ((previous, eligible, selected)
                for previous, eligible, selected in product(states, repeat=3)
                if sum(previous) <= 1 and sum(selected) <= 1
                and all(take <= allowed for take, allowed in zip(selected, eligible, strict=True))
                and any(selected) == any(eligible))
    return FiniteSafetyGame(FiniteAlgebra(values, ()), 2, 2, relation)


def build():
    game, initial = application_game(), (0, 0)
    # Freeze the application's source contract before invoking the producer.
    contract = export_contract(game, initial)
    pin = sha256(contract).hexdigest()
    solution = game.solve_ordinary()
    if initial not in solution.winning_states:
        raise RuntimeError("producer returned no candidate from the selected initial state")
    strategy = export_strategy(game, initial, solution.strategy, pin)
    verdict = verify(contract, strategy, pin)
    if isinstance(verdict, Rejected):
        # A tagged semantic rejection is a failed check, not an argument-type error.
        raise RuntimeError(f"independent checker rejected the generated strategy: {verdict}")  # noqa: TRY004
    source_paths = [Path(__file__).resolve(), ROOT / "src/orbitsynthesis/safety.py",
                    ROOT / "src/orbitsynthesis/finite_algebra.py",
                    ROOT / "src/orbitsynthesis/safety_export.py",
                    ROOT / "src/orbitsynthesis/strategy_checker.py"]
    record = {"schema": "orbitsynthesis/tau-net-controller-demo/v1", "accepted": True,
              "intended_application_scope": "solely_tau_net",
              "producer": "FiniteSafetyGame.solve_ordinary", "verification": asdict(verdict),
              "producer_winning_state_count": len(solution.winning_states),
              "source_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                                for path in source_paths},
              "domain_order": {"states_and_outputs": game.states, "inputs": game.inputs},
              "tau_execution_performed": False, "tau_net_deployed": False,
              "runtime_refinement_verified": False, "recurrence_required": False}
    return contract, strategy, pin, record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="new directory for the model, strategy, pin and verification record")
    args = parser.parse_args(argv)
    try:
        contract, strategy, pin, record = build()
        program = compile_table_image(contract, strategy, pin)
        if isinstance(program, Rejected):
            raise RuntimeError(f"compiler rejected the strategy: {program}")  # noqa: TRY004
        loaded = load_controller(contract, strategy, program, pin)
        if not isinstance(loaded, CheckedController):
            raise RuntimeError(f"table runtime check failed: {loaded}")  # noqa: TRY004
        record["table_runtime_verification"] = asdict(loaded.receipt)
        record["table_runtime_equivalence_verified"] = True
        record["native_codegen_verified"] = False
        for name in ("controller_compile.py", "controller_runtime.py"):
            source = ROOT / "src/orbitsynthesis" / name
            record["source_sha256"][str(source.relative_to(ROOT))] = sha256(source.read_bytes()).hexdigest()
        args.output_dir.mkdir(parents=True, exist_ok=False)
        (args.output_dir / "contract.json").write_bytes(contract)
        (args.output_dir / "strategy.json").write_bytes(strategy)
        (args.output_dir / "controller.osmc").write_bytes(program)
        (args.output_dir / "contract.sha256").write_text(pin + "\n", encoding="ascii")
        (args.output_dir / "record.json").write_text(
            json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="ascii")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"ACCEPT: generated and checked a controller in {args.output_dir}")
    checked = record["verification"]
    print(f"{checked['reachable_product_states']} reachable states, "
          f"{checked['checked_product_edges']} transitions, all input sequences; safety only.")
    print("Saved controller.osmc; every table runtime step matches the verified strategy.")
    print("Review and retain the contract pin separately before accepting replacement candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

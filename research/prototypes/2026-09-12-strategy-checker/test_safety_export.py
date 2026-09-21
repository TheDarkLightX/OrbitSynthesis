"""Check the producer bridge against finite exhaustive behavior and hostile candidates."""

import json
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha256
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples/controllers"))
from synthesize_tau_net_gate import application_game, build

from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.safety import FiniteSafetyGame
from orbitsynthesis.safety_export import export_contract, export_strategy
from orbitsynthesis.strategy_checker import (
    Accepted,
    RejectCode,
    canonical_bytes,
    verify,
)


def direct_safety(relation, initial, candidate, inputs):
    # The independent oracle follows original tuple-valued states and relation
    # membership, without JSON IDs, Mealy memory or solver winning regions.
    reached = {initial}
    while True:
        successors = set()
        for state in reached:
            for event in inputs:
                output = candidate[state + event]
                if (state, event, output) not in relation:
                    return False
                successors.add(output)
        if successors <= reached:
            return True
        reached.update(successors)


class SafetyExportTests(unittest.TestCase):
    def test_all_two_state_relations_and_positional_candidates(self):
        algebra = FiniteAlgebra((0, 1), ())
        states = ((0,), (1,))
        triples = tuple(product(states, repeat=3))
        observations = tuple(s + i for s in states for i in states)
        cases = 0
        for mask in range(1 << len(triples)):
            relation = frozenset(edge for bit, edge in enumerate(triples) if mask & (1 << bit))
            game = FiniteSafetyGame(algebra, 1, 1, relation)
            brute_winning = set()
            for initial in states:
                contract = export_contract(game, initial)
                pin = sha256(contract).hexdigest()
                for outputs in product(states, repeat=len(observations)):
                    candidate = dict(zip(observations, outputs, strict=True))
                    wire = export_strategy(game, initial, candidate, pin)
                    accepted = isinstance(verify(contract, wire, pin), Accepted)
                    expected = direct_safety(relation, initial, candidate, states)
                    self.assertEqual(accepted, expected, (mask, initial, outputs))
                    if expected:
                        brute_winning.add(initial)
                    cases += 1
            solution = game.solve_ordinary()
            self.assertEqual(solution.winning_states, brute_winning)
            for initial in solution.winning_states:
                contract = export_contract(game, initial)
                pin = sha256(contract).hexdigest()
                self.assertIsInstance(verify(contract, export_strategy(
                    game, initial, solution.strategy, pin), pin), Accepted)
        self.assertEqual(cases, 8192)

    def test_application_and_output_mutation(self):
        contract, strategy, pin, record = build()
        accepted = verify(contract, strategy, pin)
        self.assertIsInstance(accepted, Accepted)
        self.assertEqual((accepted.reachable_product_states, accepted.checked_product_edges), (3, 12))
        self.assertEqual(record["intended_application_scope"], "solely_tau_net")
        self.assertFalse(record["tau_execution_performed"])
        self.assertFalse(record["runtime_refinement_verified"])
        changed = json.loads(strategy)
        changed["rows"][0][0] = 3  # Both actions despite neither being eligible.
        self.assertEqual(verify(contract, canonical_bytes(changed), pin).code, RejectCode.UNSAFE_STEP)

    def test_producer_cannot_replace_the_frozen_source(self):
        game = application_game()
        contract = export_contract(game, (0, 0))
        pin = sha256(contract).hexdigest()
        game.safe_relation = frozenset(product(game.states, game.inputs, game.outputs))
        candidate = export_strategy(game, (0, 0), game.solve_ordinary().strategy, pin)
        # The unrestricted producer now chooses idle even when an action is
        # eligible. The original contract still rejects that action.
        self.assertEqual(verify(contract, candidate, pin).code, RejectCode.UNSAFE_STEP)
        replacement = export_contract(game, (0, 0))
        self.assertEqual(verify(replacement, candidate, pin).code, RejectCode.CONTRACT_PIN)

    def test_missing_reachable_rows_never_receive_a_default(self):
        game = FiniteSafetyGame(FiniteAlgebra((0, 1), ()), 1, 0, ())
        pin = sha256(export_contract(game, (0,))).hexdigest()
        with self.assertRaisesRegex(ValueError, "missing strategy row"):
            export_strategy(game, (0,), {(0,): (1,)}, pin)
        # State 1 is unreachable under this candidate, so its absent row is
        # irrelevant; the wire still covers every declared memory/input pair.
        wire = export_strategy(game, (0,), {(0,): (0,)}, pin)
        self.assertEqual(json.loads(wire)["rows"], [[0, 0]])
        # Exporting even a complete table does not attest that its edges are safe.
        self.assertEqual(verify(export_contract(game, (0,)), wire, pin).code, RejectCode.UNSAFE_STEP)

    def test_unknown_domains_and_invalid_pin(self):
        game = application_game()
        candidate = game.solve_ordinary().strategy
        pin = sha256(export_contract(game, (0, 0))).hexdigest()
        for extra in [{(9,): (0, 0)}, {(0, 0, 0, 0): (9, 9)}]:
            with self.assertRaisesRegex(ValueError, "unknown observation or output"):
                export_strategy(game, (0, 0), {**candidate, **extra}, pin)
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            export_strategy(game, (0, 0), candidate, "not-a-pin")
        with self.assertRaisesRegex(ValueError, "initial"):
            export_contract(game, (9, 9))
        game.safe_relation = frozenset({((0, 0), (9, 9), (0, 0))})
        with self.assertRaisesRegex(ValueError, "unknown domain"):
            export_contract(game, (0, 0))

    def test_declared_order_unit_input_and_memory_initialization(self):
        states = (("z",), ("a",))
        relation = frozenset((s, (), ("z",)) for s in states)
        game = FiniteSafetyGame(FiniteAlgebra(("z", "a"), ()), 1, 0, relation)
        initial = ("a",)
        contract = export_contract(game, initial)
        pin = sha256(contract).hexdigest()
        candidate = {("a",): ("z",), ("z",): ("z",)}
        wire = export_strategy(game, initial, candidate, pin)
        self.assertEqual(json.loads(wire)["initial_memory"], 1)
        self.assertEqual(json.loads(contract)["initial"], 1)
        self.assertEqual(verify(contract, wire, pin).checked_product_edges, 2)
        reordered = dict(reversed(tuple(candidate.items())))
        self.assertEqual(wire, export_strategy(game, initial, reordered, pin))
        candidate[("a",)] = ("a",)
        self.assertIsInstance(verify(contract, wire, pin), Accepted)

    def test_bridge_limits(self):
        # Next state is also the output, so the bridge has the stricter 16-state
        # output bound even though the general checker permits 64 plant states.
        for game in [FiniteSafetyGame(FiniteAlgebra(tuple(range(17)), ()), 1, 0, ()),
                     FiniteSafetyGame(FiniteAlgebra((0, 1), ()), 1, 5, ())]:
            with self.assertRaisesRegex(ValueError, "bounds"):
                export_contract(game, game.states[0])

    def test_producer_then_independent_cli_and_preserve_existing_directory(self):
        flags = ["-B", "-O"] if sys.flags.optimize else ["-B"]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "controller"
            command = [sys.executable, *flags, str(ROOT / "examples/controllers/synthesize_tau_net_gate.py"),
                       "--output-dir", str(target)]
            generated = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            original = {p.name: p.read_bytes() for p in target.iterdir()}
            repeated = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
            self.assertEqual(repeated.returncode, 2)
            self.assertEqual(original, {p.name: p.read_bytes() for p in target.iterdir()})
            checked = subprocess.run(
                [sys.executable, *flags, str(ROOT / "scripts/check_controller.py"),
                 str(target / "contract.json"), str(target / "strategy.json"), "--contract-pin",
                 str(target / "contract.sha256"), "--json"],
                capture_output=True, text=True, timeout=20, check=False)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertTrue(json.loads(checked.stdout)["accepted"])


if __name__ == "__main__":
    unittest.main()

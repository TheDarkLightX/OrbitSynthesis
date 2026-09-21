"""Requirement-derived negatives and an independent matrix-closure oracle."""

import ast
import importlib.util
import random
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError
from hashlib import sha256
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from demo import (
    arbiter_fixture,
    output_flip_fixture,
    run,
    service_fixture,
    strategy_for,
)

from orbitsynthesis import strategy_checker as checker
from orbitsynthesis.strategy_checker import (
    Accepted,
    RejectCode,
    Rejected,
    canonical_bytes,
    verify,
)


def closure_cycle(vertices, links):
    # Independent reference: transitive closure, with no reflexive identity
    # initially. A true diagonal therefore means a nonempty cycle.
    nodes = tuple(sorted(vertices))
    reach = {(a, b) for a, b in links if a in vertices and b in vertices}
    for via in nodes:
        for start in nodes:
            for end in nodes:
                if (start, via) in reach and (via, end) in reach:
                    reach.add((start, end))
    return any((v, v) in reach for v in nodes)


def reference(contract, strategy):
    root = (contract["initial"], strategy["initial_memory"])
    reached = {root}
    safe = set(contract["safe_states"])
    if root[0] not in safe:
        return False
    links = set()
    while True:
        enlarged = set(reached)
        for state, memory in reached:
            for event in range(contract["inputs"]):
                output, next_memory = strategy["rows"][memory * contract["inputs"] + event]
                next_state = contract["transitions"][
                    state * contract["inputs"] * contract["outputs"]
                    + event * contract["outputs"] + output]
                if next_state == -1 or next_state not in safe:
                    return False
                target = (next_state, next_memory)
                enlarged.add(target)
                links.add(((state, memory), target))
        if enlarged == reached:
            break
        reached = enlarged
    for goal in contract["recurrence"]:
        avoid = {v for v in reached if v[0] not in goal}
        if closure_cycle(avoid, links):
            return False
    return True


class CheckerTests(unittest.TestCase):
    def check_witness(self, contract, strategy, verdict):
        if isinstance(verdict, Accepted) or not verdict.prefix and not verdict.cycle:
            return
        vertex = (contract["initial"], strategy["initial_memory"])
        for index, edge in enumerate(verdict.prefix):
            self.assertEqual(vertex, (edge.plant, edge.memory))
            self.check_edge(contract, strategy, edge)
            if index + 1 < len(verdict.prefix) or verdict.cycle:
                self.assertIn(edge.next_plant, contract["safe_states"])
            vertex = (edge.next_plant, edge.next_memory)
        if verdict.cycle:
            entry = vertex
            goal = contract["recurrence"][verdict.recurrence_index]
            for edge in verdict.cycle:
                self.assertEqual(vertex, (edge.plant, edge.memory))
                self.check_edge(contract, strategy, edge)
                self.assertNotIn(edge.plant, goal)
                self.assertIn(edge.next_plant, contract["safe_states"])
                vertex = (edge.next_plant, edge.next_memory)
            self.assertEqual(vertex, entry)
        elif verdict.code == RejectCode.UNSAFE_STEP:
            self.assertNotIn(vertex[0], contract["safe_states"])

    def check_edge(self, contract, strategy, edge):
        self.assertEqual(strategy["rows"][edge.memory * contract["inputs"] + edge.input],
                         [edge.output, edge.next_memory])
        index = (edge.plant * contract["inputs"] + edge.input) * contract["outputs"] + edge.output
        self.assertEqual(contract["transitions"][index], edge.next_plant)

    def test_examples_and_witnesses(self):
        for fixture, accepted in [(service_fixture(), True), (service_fixture(True), False),
                                  (arbiter_fixture(), True), (arbiter_fixture(False), False),
                                  (output_flip_fixture(), False)]:
            contract, strategy = fixture
            verdict = run(contract, strategy)
            self.assertEqual(isinstance(verdict, Accepted), accepted)
            self.check_witness(contract, strategy, verdict)

    def test_all_inputs_are_checked(self):
        contract, strategy = service_fixture()
        strategy["rows"][0] = [1, 0]  # unsolicited acknowledgement at idle
        self.assertEqual(run(contract, strategy).code, RejectCode.UNSAFE_STEP)

    def test_cycle_reachable_through_goal(self):
        contract, strategy = service_fixture(True)
        result = run(contract, strategy)
        self.assertEqual(result.code, RejectCode.RECURRENCE)
        self.assertTrue(result.prefix)
        self.check_witness(contract, strategy, result)

    def test_unreachable_bad_cycle_is_irrelevant(self):
        contract = {"schema": checker.CONTRACT_SCHEMA, "states": 2, "inputs": 1,
                    "outputs": 1, "initial": 0, "safe_states": [0, 1],
                    "transitions": [0, 1], "recurrence": [[0]]}
        strategy = strategy_for(contract, 1, [[0, 0]])
        self.assertIsInstance(run(contract, strategy), Accepted)

    def test_safety_only_and_impossible_empty_goal(self):
        contract, strategy = service_fixture(True)
        contract["recurrence"] = []
        strategy = strategy_for(contract, 1, strategy["rows"])
        self.assertIsInstance(run(contract, strategy), Accepted)
        contract["recurrence"] = [[]]
        strategy = strategy_for(contract, 1, strategy["rows"])
        self.assertEqual(run(contract, strategy).code, RejectCode.RECURRENCE)

    def test_initial_safety(self):
        contract, strategy = service_fixture()
        contract["safe_states"] = [1]
        strategy = strategy_for(contract, 2, strategy["rows"])
        self.assertEqual(run(contract, strategy).code, RejectCode.UNSAFE_INITIAL)

    def test_external_contract_pin(self):
        contract, strategy = service_fixture(True)
        original_pin = sha256(canonical_bytes(contract)).hexdigest()
        contract["recurrence"] = []  # producer weakens model and rehashes it
        strategy = strategy_for(contract, 1, strategy["rows"])
        verdict = verify(canonical_bytes(contract), canonical_bytes(strategy), original_pin)
        self.assertEqual(verdict.code, RejectCode.CONTRACT_PIN)
        self.assertEqual(verify(b"{}", b"{}", "unknown").code, RejectCode.INVALID_PIN)

    def test_strategy_binding(self):
        contract, strategy = service_fixture()
        strategy["contract_sha256"] = "0" * 64
        self.assertEqual(run(contract, strategy).code, RejectCode.STRATEGY_CONTRACT)

    def test_closed_schema_and_integer_bounds(self):
        for key, value in [("states", True), ("states", 0), ("states", 65),
                           ("inputs", 0), ("outputs", -1), ("initial", "0"),
                           ("safe_states", [0, 0]), ("safe_states", [1, 0]),
                           ("transitions", [0]), ("recurrence", [[True]]),
                           ("unknown", 0), ("schema", "future")]:
            contract, strategy = service_fixture()
            contract[key] = value
            strategy = strategy_for(contract, 2, strategy["rows"])
            with self.subTest(key=key, value=value):
                self.assertEqual(run(contract, strategy).code, RejectCode.CONTRACT_FORMAT)
        for key in ("schema", "states", "transitions", "recurrence"):
            contract, strategy = service_fixture()
            del contract[key]
            self.assertEqual(run(contract, strategy).code, RejectCode.CONTRACT_FORMAT)

    def test_controller_totality_even_unreachable_rows(self):
        for key, value in [("memory_states", True), ("memory_states", 0),
                           ("initial_memory", 2), ("rows", [[0, 0]]),
                           ("rows", [[0, 0], [0, 1], [1, 0], [1, 2]]),
                           ("rows", [[0, 0], [0, 1], [1, 0], [True, 0]]),
                           ("unknown", 0), ("schema", "future")]:
            contract, strategy = service_fixture()
            strategy[key] = value
            with self.subTest(key=key):
                self.assertEqual(run(contract, strategy).code, RejectCode.STRATEGY_FORMAT)

    def test_wire_rejections(self):
        contract, strategy = service_fixture()
        raw = canonical_bytes(contract)
        pin = sha256(raw).hexdigest()
        for bad in [raw + b"\n", b'{"states":2,"states":2}', b'{"x":NaN}',
                    b'{"x":1.0}', b'{"x":1e0}', b'[]', b'\xff', b'{}junk',
                    b'[' * 2000 + b']' * 2000]:
            with self.subTest(bad=bad[:25]):
                result = verify(bad, canonical_bytes(strategy), sha256(bad).hexdigest())
                self.assertEqual(result.code, RejectCode.CONTRACT_FORMAT)
                self.assertIsInstance(verify(raw, bad, pin), Rejected)
        self.assertEqual(verify(raw, b" " * (checker.MAX_BYTES + 1), pin).code,
                         RejectCode.RESOURCE_LIMIT)
        self.assertEqual(verify(bytearray(raw), b"{}", pin).code, RejectCode.CONTRACT_FORMAT)

    def test_ownership_and_rejection_no_mutation(self):
        contract, strategy = service_fixture()
        raw, candidate = canonical_bytes(contract), canonical_bytes(strategy)
        before = (raw, candidate)
        verdict = verify(raw, candidate, sha256(raw).hexdigest())
        original = deepcopy(contract), deepcopy(strategy)
        contract["transitions"][0] = -1
        strategy["rows"][0][0] = 1
        self.assertEqual(before, (raw, candidate))
        self.assertEqual(verdict, run(*original))
        with self.assertRaises(FrozenInstanceError):
            verdict.contract_sha256 = "changed"
        rejecting = verify(raw, candidate, "0" * 64)
        self.assertIsInstance(rejecting, Rejected)
        self.assertFalse(hasattr(rejecting, "strategy_sha256"))
        self.assertEqual(before, (raw, candidate))

    def test_checker_source_boundary(self):
        tree = ast.parse(Path(checker.__file__).read_text())
        allowed = {"__future__", "collections", "dataclasses", "enum", "hashlib", "json", "re"}
        for node in ast.walk(tree):
            self.assertNotIsInstance(node, ast.Assert)
            if isinstance(node, ast.Import):
                self.assertTrue(all(alias.name in allowed for alias in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertIn(node.module, allowed)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"eval", "exec", "open", "__import__"})

    def test_exhaustive_graph_oracle(self):
        # All 1..3-state, two-input, one-output transition tables (including
        # forbidden edges), each with every possible single recurrence set.
        checked = 0
        for states in range(1, 4):
            for successors in product(range(-1, states), repeat=2 * states):
                for mask in range(1 << states):
                    contract = {"schema": checker.CONTRACT_SCHEMA, "states": states,
                                "inputs": 2, "outputs": 1, "initial": 0,
                                "safe_states": list(range(states)),
                                "transitions": list(successors),
                                "recurrence": [[s for s in range(states) if mask >> s & 1]]}
                    strategy = strategy_for(contract, 1, [[0, 0], [0, 0]])
                    verdict = run(contract, strategy)
                    self.assertEqual(isinstance(verdict, Accepted), reference(contract, strategy),
                                     (contract, strategy))
                    self.check_witness(contract, strategy, verdict)
                    checked += 1
        self.assertEqual(checked, 33100)

    def test_seeded_product_and_multiple_goals(self):
        rng = random.Random(20260912)
        for _ in range(300):
            states, inputs, outputs, memories = [rng.randrange(1, 4) for _ in range(4)]
            contract = {"schema": checker.CONTRACT_SCHEMA, "states": states,
                        "inputs": inputs, "outputs": outputs, "initial": rng.randrange(states),
                        "safe_states": [s for s in range(states) if rng.randrange(5)],
                        "transitions": [rng.randrange(-1, states)
                                        for _ in range(states * inputs * outputs)],
                        "recurrence": [[s for s in range(states) if rng.randrange(2)]
                                       for _ in range(2)]}
            strategy = strategy_for(contract, memories,
                                    [[rng.randrange(outputs), rng.randrange(memories)]
                                     for _ in range(memories * inputs)], rng.randrange(memories))
            verdict = run(contract, strategy)
            self.assertEqual(isinstance(verdict, Accepted), reference(contract, strategy))
            self.check_witness(contract, strategy, verdict)

    def test_cli_verdicts_pins_and_file_errors(self):
        root = Path(__file__).resolve().parents[3]
        cli = root / "scripts/check_controller.py"
        examples = root / "examples/controllers"
        base = [sys.executable, "-B", str(cli), str(examples / "arbiter.contract.json")]
        for candidate, expected in [("arbiter", 0), ("arbiter_priority", 1)]:
            completed = subprocess.run(base + [str(examples / f"{candidate}.strategy.json"),
                "--contract-pin", str(examples / "arbiter.sha256"), "--json"],
                capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(completed.returncode, expected, completed.stderr)
            record = checker.json.loads(completed.stdout)
            self.assertEqual(record["accepted"], expected == 0)
            self.assertFalse(record["runtime_refinement_verified"])
        wrong = subprocess.run(base + [str(examples / "arbiter.strategy.json"),
            "--contract-sha256", "0" * 64, "--json"], capture_output=True, text=True, timeout=10, check=False)
        self.assertEqual(wrong.returncode, 2)
        self.assertEqual(checker.json.loads(wrong.stdout)["code"], RejectCode.CONTRACT_PIN.value)
        with tempfile.TemporaryDirectory() as directory:
            missing = subprocess.run(base + [str(Path(directory) / "missing.json"),
                "--contract-sha256", "0" * 64, "--json"], capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(missing.returncode, 2)
            self.assertEqual(checker.json.loads(missing.stdout)["code"], "file_error")

    def test_known_faults_are_detectable(self):
        source = Path(checker.__file__).read_text()
        original_contract, original_strategy = service_fixture(True)
        pin = sha256(canonical_bytes(original_contract)).hexdigest()
        weakened = deepcopy(original_contract)
        weakened["recurrence"] = []
        weakened_strategy = strategy_for(weakened, 1, original_strategy["rows"])
        cases = [
            ("unchecked_contract_pin", "if digest != expected_contract_sha256:", "if False:",
             weakened, weakened_strategy, pin),
            ("skipped_safety", "if next_state == -1 or next_state not in contract.safe:", "if False:",
             *output_flip_fixture(), None),
            ("omitted_recurrence", "for index, goal in enumerate(contract.recurrence):",
             "for index, goal in enumerate(()):", *arbiter_fixture(False), None),
            ("ignored_second_input", "for input_value in range(contract.inputs):",
             "for input_value in range(1):", *service_fixture(True), None),
        ]
        for name, before, after, contract, strategy, expected_pin in cases:
            self.assertEqual(source.count(before), 1)
            raw, candidate = canonical_bytes(contract), canonical_bytes(strategy)
            expected_pin = expected_pin or sha256(raw).hexdigest()
            self.assertIsInstance(verify(raw, candidate, expected_pin), Rejected)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / f"{name}.py"
                path.write_text(source.replace(before, after))
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                try:
                    spec.loader.exec_module(module)
                    # The named negative distinguishes the real checker from
                    # this plausible faulty implementation. No production
                    # source file is edited by this mutation probe.
                    self.assertIsInstance(module.verify(raw, candidate, expected_pin), module.Accepted)
                finally:
                    del sys.modules[name]


if __name__ == "__main__":
    unittest.main()

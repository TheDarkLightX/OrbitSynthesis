"""Exhaustive table equivalence, damaged images, stateful replay and runtime faults."""

import ast
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from hashlib import sha256
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from demo import arbiter_fixture, service_fixture, strategy_for

from orbitsynthesis import controller_runtime as runtime
from orbitsynthesis.controller_compile import compile_table_image
from orbitsynthesis.controller_runtime import (
    CheckedController,
    ControllerStep,
    ProgramRejectCode,
    StepRejectCode,
    load_controller,
)
from orbitsynthesis.strategy_checker import (
    CONTRACT_SCHEMA,
    RejectCode,
    Rejected,
    canonical_bytes,
)


def compiled(fixture):
    contract, strategy = map(canonical_bytes, fixture)
    pin = sha256(contract).hexdigest()
    image = compile_table_image(contract, strategy, pin)
    if isinstance(image, Rejected):
        raise RuntimeError(f"invalid test fixture: {image}")  # noqa: TRY004
    return contract, strategy, image, pin


class ControllerRuntimeTests(unittest.TestCase):
    def test_every_small_table_and_initial_memory(self):
        count = 0
        for memories, inputs, outputs in product((1, 2), repeat=3):
            contract = {"schema": CONTRACT_SCHEMA, "states": 1, "inputs": inputs,
                        "outputs": outputs, "initial": 0, "safe_states": [0],
                        "transitions": [0] * (inputs * outputs), "recurrence": [[0]]}
            choices = tuple(product(range(outputs), range(memories)))
            for rows in product(choices, repeat=memories * inputs):
                for initial in range(memories):
                    strategy = strategy_for(contract, memories, [list(row) for row in rows])
                    strategy["initial_memory"] = initial
                    args = compiled((contract, strategy))
                    loaded = load_controller(*args)
                    self.assertIsInstance(loaded, CheckedController)
                    self.assertEqual(loaded.initial_memory, initial)
                    self.assertEqual(loaded.receipt.checked_memory_input_pairs, memories * inputs)
                    for memory in range(memories):
                        for event in range(inputs):
                            expected = ControllerStep(*rows[memory * inputs + event])
                            self.assertEqual(loaded.step(memory, event), expected)
                    count += 1
        self.assertEqual(count, 592)

    def test_format_golden_vector(self):
        contract = {"schema": CONTRACT_SCHEMA, "states": 1, "inputs": 2,
                    "outputs": 4, "initial": 0, "safe_states": [0],
                    "transitions": [0] * 8, "recurrence": []}
        strategy = strategy_for(contract, 3, [[0, 0], [1, 1], [2, 2], [3, 0], [1, 2], [0, 1]])
        strategy["initial_memory"] = 1
        contract, strategy, image, pin = compiled((contract, strategy))
        # Literal specification bytes, separate from the encoder's struct layout.
        expected = (bytes.fromhex("4f534d4300000001") + bytes.fromhex(pin)
                    + sha256(strategy).digest() + bytes.fromhex("02040301000001010202030001020001"))
        self.assertEqual(image, expected)
        self.assertEqual(load_controller(contract, strategy, expected, pin).initial_memory, 1)

    def test_every_single_bit_image_change_is_rejected(self):
        contract, strategy, image, pin = compiled(arbiter_fixture())
        self.assertIsInstance(load_controller(contract, strategy, image, pin), CheckedController)
        self.assertEqual(len(image) * 8, 1120)
        for index in range(len(image)):
            for bit in range(8):
                changed = bytearray(image)
                changed[index] ^= 1 << bit
                self.assertNotIsInstance(load_controller(contract, strategy, bytes(changed), pin),
                                         CheckedController, (index, bit))
        for invalid in (b"", image[:-1], image + b"\x00", bytearray(image), memoryview(image),
                        b"\x00" * (runtime.MAX_IMAGE_BYTES + 1)):
            self.assertEqual(load_controller(contract, strategy, invalid, pin).code,
                             ProgramRejectCode.FORMAT)

    def test_initial_bindings_and_unreachable_memory_rows(self):
        contract = {"schema": CONTRACT_SCHEMA, "states": 1, "inputs": 2,
                    "outputs": 2, "initial": 0, "safe_states": [0],
                    "transitions": [0] * 4, "recurrence": []}
        strategy = strategy_for(contract, 2, [[0, 0]] * 4)
        contract, strategy, image, pin = compiled((contract, strategy))
        self.assertEqual(load_controller(contract, strategy, image, "0" * 64).code,
                         RejectCode.CONTRACT_PIN)
        for position, code in [(8, ProgramRejectCode.CONTRACT), (40, ProgramRejectCode.STRATEGY),
                               (75, ProgramRejectCode.SHAPE), (80, ProgramRejectCode.STEP)]:
            changed = bytearray(image)
            changed[position] ^= 1
            result = load_controller(contract, strategy, bytes(changed), pin)
            self.assertEqual(result.code, code)
            if code == ProgramRejectCode.STEP:
                # Memory 1 is unreachable and output 1 would still satisfy this
                # permissive model. Exact strategy equivalence nevertheless fails.
                self.assertEqual((result.memory, result.input), (1, 0))
                self.assertEqual(result.expected, ControllerStep(0, 0))
                self.assertEqual(result.actual, ControllerStep(1, 0))

    def test_loader_rechecks_safety_and_progress_before_loading(self):
        contract, strategy = service_fixture(True)
        raw_contract, raw_strategy = canonical_bytes(contract), canonical_bytes(strategy)
        pin = sha256(raw_contract).hexdigest()
        self.assertEqual(compile_table_image(raw_contract, raw_strategy, pin).code, RejectCode.RECURRENCE)
        self.assertEqual(load_controller(raw_contract, raw_strategy, b"", pin).code, RejectCode.RECURRENCE)

    def test_stateful_replay_matches_strategy(self):
        traces = 0
        for fixture, length in ((service_fixture(), 8), (arbiter_fixture(), 5)):
            contract, strategy = fixture
            loaded = load_controller(*compiled(fixture))
            for inputs in product(range(contract["inputs"]), repeat=length):
                memory = loaded.initial_memory
                for event in inputs:
                    expected = strategy["rows"][memory * contract["inputs"] + event]
                    actual = loaded.step(memory, event)
                    self.assertEqual((actual.output, actual.next_memory), tuple(expected))
                    memory = actual.next_memory
                traces += 1
        self.assertEqual(traces, 1280)

    def test_immutable_loaded_image_and_reject_is_no_op(self):
        contract, strategy, image, pin = compiled(service_fixture())
        loaded = load_controller(contract, strategy, image, pin)
        saved = loaded.step(loaded.initial_memory, 0)
        for bad in (True, False, -1, 2, 1.0, "1", None):
            self.assertEqual(loaded.step(bad, 0).code, StepRejectCode.MEMORY)
            self.assertEqual(loaded.step(0, bad).code, StepRejectCode.INPUT)
            self.assertEqual(loaded.step(loaded.initial_memory, 0), saved)
        with self.assertRaises(FrozenInstanceError):
            loaded._machine.initial = 1
        with self.assertRaises(FrozenInstanceError):
            loaded.receipt.program_sha256 = "0" * 64
        changed = bytearray(image)
        changed[76] ^= 1
        self.assertEqual(loaded.step(loaded.initial_memory, 0), saved)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "controller.osmc"
            path.write_bytes(image)
            from_file = load_controller(contract, strategy, path.read_bytes(), pin)
            path.write_bytes(bytes(changed))
            self.assertEqual(from_file.step(from_file.initial_memory, 0), saved)

    def test_runtime_has_no_compiler_or_effect_dependencies(self):
        tree = ast.parse(Path(runtime.__file__).read_text())
        for node in ast.walk(tree):
            self.assertNotIsInstance(node, ast.Assert)
            if isinstance(node, ast.Import):
                self.assertTrue(all(n.name in {"json", "dataclasses", "enum", "hashlib"}
                                    for n in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertIn(node.module, {"__future__", "json", "dataclasses", "enum", "hashlib",
                                            "strategy_checker"})
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"open", "eval", "exec", "__import__", "compile"})

    def test_changed_runtime_step_is_detected_at_load(self):
        original = Path(runtime.__file__).read_text()
        mutants = [
            ("2 * (memory * self.inputs + event)", "2 * event"),
            ("ControllerStep(self.body[offset], self.body[offset + 1])",
             "ControllerStep(self.body[offset] ^ 1, self.body[offset + 1])"),
            ("ControllerStep(self.body[offset], self.body[offset + 1])",
             "ControllerStep(self.body[offset], self.body[offset + 1] ^ 1)"),
        ]
        args = compiled(arbiter_fixture())
        for index, (before, after) in enumerate(mutants):
            self.assertEqual(original.count(before), 1)
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "faulty_runtime.py"
                path.write_text(original.replace(before, after))
                name = f"orbitsynthesis._runtime_fault_{index}"
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                try:
                    spec.loader.exec_module(module)
                    result = module.load_controller(*args)
                    self.assertEqual(result.code.value, "image_step_mismatch")
                finally:
                    del sys.modules[name]

    def test_negative_detects_omitted_runtime_comparison(self):
        original = Path(runtime.__file__).read_text()
        before = "if actual != expected:"
        self.assertEqual(original.count(before), 1)
        contract, strategy, image, pin = compiled(service_fixture())
        changed = bytearray(image)
        changed[76] ^= 1
        args = contract, strategy, bytes(changed), pin
        self.assertEqual(load_controller(*args).code, ProgramRejectCode.STEP)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "faulty_runtime.py"
            path.write_text(original.replace(before, "if False:"))
            name = "orbitsynthesis._runtime_missing_comparison"
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            try:
                spec.loader.exec_module(module)
                self.assertIsInstance(module.load_controller(*args), module.CheckedController)
            finally:
                del sys.modules[name]

    def test_generate_load_execute_and_reject_cli(self):
        flags = ["-B", "-O"] if sys.flags.optimize else ["-B"]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "gate"
            generated = subprocess.run(
                [sys.executable, *flags, str(ROOT / "examples/controllers/synthesize_tau_net_gate.py"),
                 "--output-dir", str(target)], capture_output=True, text=True, timeout=20, check=False)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            base = [sys.executable, *flags, str(ROOT / "scripts/run_controller.py"),
                    str(target / "contract.json"), str(target / "strategy.json"),
                    str(target / "controller.osmc"), "--contract-pin", str(target / "contract.sha256"),
                    "--json"]
            executed = subprocess.run(base + ["--inputs", "0", "1", "2", "3"],
                                      capture_output=True, text=True, timeout=20, check=False)
            self.assertEqual(executed.returncode, 0, executed.stderr)
            record = json.loads(executed.stdout)
            self.assertEqual([step["output"] for step in record["trace"]], [0, 1, 2, 1])
            self.assertTrue(record["table_runtime_equivalence_verified"])
            self.assertFalse(record["application_effects_executed"])
            invalid = subprocess.run(base + ["--inputs", "4"], capture_output=True,
                                     text=True, timeout=20, check=False)
            self.assertEqual(invalid.returncode, 2)
            program = target / "controller.osmc"
            changed = bytearray(program.read_bytes())
            changed[76] ^= 1
            program.write_bytes(bytes(changed))
            rejected = subprocess.run(base, capture_output=True, text=True, timeout=20, check=False)
            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(json.loads(rejected.stdout)["code"], "image_step_mismatch")


if __name__ == "__main__":
    unittest.main()

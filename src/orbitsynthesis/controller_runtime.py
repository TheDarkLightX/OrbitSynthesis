# SPDX-License-Identifier: MIT
"""Load and execute a finite table only after checking its complete step function.

See examples/controllers/TABLE_RUNTIME.md. No candidate code is executed, and
the loader does not import the compiler. All controller state is explicit.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .strategy_checker import Accepted, Rejected, verify

RUNTIME_PROFILE = "orbitsynthesis/osmc-table-runtime/v1"
MAX_IMAGE_BYTES = 76 + 2 * 64 * 16


class ProgramRejectCode(str, Enum):
    FORMAT = "invalid_table_image"
    CONTRACT = "image_contract_mismatch"
    STRATEGY = "image_strategy_mismatch"
    SHAPE = "image_shape_mismatch"
    STEP = "image_step_mismatch"


class StepRejectCode(str, Enum):
    MEMORY = "invalid_memory"
    INPUT = "invalid_input"


@dataclass(frozen=True)
class ControllerStep:
    output: int
    next_memory: int


@dataclass(frozen=True)
class StepRejected:
    code: StepRejectCode


@dataclass(frozen=True)
class ProgramRejected:
    code: ProgramRejectCode
    detail: str
    memory: int | None = None
    input: int | None = None
    expected: ControllerStep | None = None
    actual: ControllerStep | StepRejected | None = None


@dataclass(frozen=True)
class ProgramReceipt:
    strategy_verification: Accepted
    program_sha256: str
    checked_memory_input_pairs: int
    runtime_profile: str = RUNTIME_PROFILE


@dataclass(frozen=True)
class _TableMachine:
    inputs: int
    memories: int
    initial: int
    body: bytes

    def step(self, memory: int, event: int) -> ControllerStep | StepRejected:
        if type(memory) is not int or not 0 <= memory < self.memories:
            return StepRejected(StepRejectCode.MEMORY)
        if type(event) is not int or not 0 <= event < self.inputs:
            return StepRejected(StepRejectCode.INPUT)
        offset = 2 * (memory * self.inputs + event)
        return ControllerStep(self.body[offset], self.body[offset + 1])


@dataclass(frozen=True)
class CheckedController:
    """Immutable checked data and the exact step implementation used at load.

Start at initial_memory and feed each successful next_memory back into step.
Python objects and receipts are not tamper-proof capabilities. A caller with
permission to replace Python code can defeat any in-process boundary.
"""
    receipt: ProgramReceipt
    _machine: _TableMachine

    @property
    def initial_memory(self) -> int:
        return self._machine.initial

    def step(self, memory: int, event: int) -> ControllerStep | StepRejected:
        return self._machine.step(memory, event)


def load_controller(contract: bytes, strategy: bytes, image: bytes,
                    contract_pin: str) -> CheckedController | Rejected | ProgramRejected:
    """Recheck model safety/progress, image bindings, initial state and all rows.

No receipt supplied by a producer is trusted. Both JSON and image must be
immutable bytes. Runtime-to-strategy equality is checked at every declared
memory/input pair, including memory states unreachable from the initial state.
"""
    checked = verify(contract, strategy, contract_pin)
    if isinstance(checked, Rejected):
        return checked
    if type(image) is not bytes or not 76 <= len(image) <= MAX_IMAGE_BYTES:
        return ProgramRejected(ProgramRejectCode.FORMAT, "expected a bounded immutable OSMC image")
    if image[:8] != b"OSMC\x00\x00\x00\x01":
        return ProgramRejected(ProgramRejectCode.FORMAT, "unknown image magic or version")
    if image[8:40].hex() != checked.contract_sha256:
        return ProgramRejected(ProgramRejectCode.CONTRACT, "image names a different model")
    if image[40:72].hex() != checked.strategy_sha256:
        return ProgramRejected(ProgramRejectCode.STRATEGY, "image names a different strategy")

    # verify() already established the closed canonical JSON schemas and bounds.
    model, candidate = json.loads(contract), json.loads(strategy)
    inputs, outputs, memories, initial = image[72:76]
    if ((inputs, outputs, memories, initial) !=
            (model["inputs"], model["outputs"], candidate["memory_states"], candidate["initial_memory"])):
        return ProgramRejected(ProgramRejectCode.SHAPE, "image domains or initial memory differ")
    if len(image) != 76 + 2 * inputs * memories:
        return ProgramRejected(ProgramRejectCode.FORMAT, "image has missing or trailing rows")

    machine = _TableMachine(inputs, memories, initial, image[76:])
    for memory in range(memories):
        for event in range(inputs):
            output, next_memory = candidate["rows"][memory * inputs + event]
            expected = ControllerStep(output, next_memory)
            actual = machine.step(memory, event)
            if actual != expected:
                return ProgramRejected(ProgramRejectCode.STEP, "runtime step differs from strategy",
                                       memory, event, expected, actual)
    receipt = ProgramReceipt(checked, sha256(image).hexdigest(), inputs * memories)
    return CheckedController(receipt, machine)

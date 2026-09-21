# SPDX-License-Identifier: MIT
"""Encode a candidate OSMC table image. Loading always independently rechecks it."""

import json
import struct

from .strategy_checker import Rejected, verify


def compile_table_image(contract: bytes, strategy: bytes, contract_pin: str) -> bytes | Rejected:
    """Compile finite strategy JSON to the closed OSMC version 1 data format.

The resulting image contains no Python, native code or Tau component. The
runtime reader implements the wire layout separately; it does not import this
encoder. A successful encoding is not an operational admission credential.
"""
    checked = verify(contract, strategy, contract_pin)
    if isinstance(checked, Rejected):
        return checked
    model, candidate = json.loads(contract), json.loads(strategy)
    header = struct.pack(
        ">8s32s32s4B", b"OSMC\x00\x00\x00\x01",
        bytes.fromhex(checked.contract_sha256), bytes.fromhex(checked.strategy_sha256),
        model["inputs"], model["outputs"], candidate["memory_states"], candidate["initial_memory"],
    )
    body = bytes(value for row in candidate["rows"] for value in row)
    return header + body

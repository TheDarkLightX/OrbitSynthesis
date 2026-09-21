"""Original finite fixtures; these are not exports from a Tau executable."""

import json
import sys
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from orbitsynthesis.strategy_checker import (
    CONTRACT_SCHEMA,
    STRATEGY_SCHEMA,
    Accepted,
    canonical_bytes,
    verify,
)


def strategy_for(contract, memory_states, rows, initial=0):
    return {"schema": STRATEGY_SCHEMA,
            "contract_sha256": sha256(canonical_bytes(contract)).hexdigest(),
            "memory_states": memory_states, "initial_memory": initial, "rows": rows}


def service_fixture(starve=False):
    transitions = []
    for pending in range(2):
        for request in range(2):
            for acknowledge in range(2):
                active = pending or request
                transitions.append(-1 if acknowledge and not active
                                   else int(bool(active) and not acknowledge))
    contract = {"schema": CONTRACT_SCHEMA, "states": 2, "inputs": 2,
                "outputs": 2, "initial": 0, "safe_states": [0, 1],
                "transitions": transitions, "recurrence": [[0]]}
    rows = [[0, 0], [0, 0]] if starve else [[0, 0], [0, 1], [1, 0], [1, 0]]
    return contract, strategy_for(contract, 1 if starve else 2, rows)


def arbiter_fixture(fair=True):
    # State bits are pending requests. Inputs add requests; grant 0 means no
    # grant, 1 serves request 0, and 2 serves request 1. Repeated requests
    # coalesce: this is a pair of pending flags, not an unbounded order queue.
    transitions = []
    for pending in range(4):
        for request in range(4):
            for grant in range(3):
                available = pending | request
                bit = 0 if grant == 0 else 1 << (grant - 1)
                transitions.append(-1 if bit and not available & bit
                                   else available & ~bit)
    contract = {"schema": CONTRACT_SCHEMA, "states": 4, "inputs": 4,
                "outputs": 3, "initial": 0, "safe_states": [0, 1, 2, 3],
                "transitions": transitions, "recurrence": [[0, 2], [0, 1]]}
    rows = []
    for memory in range(8):
        pending, turn = divmod(memory, 2)
        for request in range(4):
            available = pending | request
            if available == 0:
                grant = 0
            elif fair and available & (1 << turn):
                grant = turn + 1
            else:
                grant = 1 if available & 1 else 2
            bit = 0 if grant == 0 else 1 << (grant - 1)
            next_turn = turn if grant == 0 else 2 - grant
            rows.append([grant, 2 * (available & ~bit) + next_turn])
    return contract, strategy_for(contract, 8, rows)


def output_flip_fixture():
    contract = {"schema": CONTRACT_SCHEMA, "states": 1, "inputs": 2,
                "outputs": 2, "initial": 0, "safe_states": [0],
                "transitions": [0, -1, 0, -1], "recurrence": []}
    return contract, strategy_for(contract, 1, [[1, 0], [1, 0]])


def run(contract, strategy):
    raw = canonical_bytes(contract)
    return verify(raw, canonical_bytes(strategy), sha256(raw).hexdigest())


def report():
    fixtures = {"delayed_service": service_fixture(),
                "starving_service": service_fixture(True),
                "fair_arbiter": arbiter_fixture(),
                "priority_arbiter": arbiter_fixture(False),
                "output_bit_flip": output_flip_fixture()}
    results = {}
    for name, (contract, strategy) in fixtures.items():
        result = run(contract, strategy)
        results[name] = {"accepted": isinstance(result, Accepted), **asdict(result)}
    if (not results["delayed_service"]["accepted"] or
            not results["fair_arbiter"]["accepted"] or
            any(results[name]["accepted"] for name in
                ("starving_service", "priority_arbiter", "output_bit_flip"))):
        raise RuntimeError("fixture verdict changed")
    return {"schema": "orbitsynthesis/finite-strategy-demo/v1", "results": results,
            "tau_execution_performed": False, "compiled_artifact_verified": False,
            "production_authority": False, "patent_clearance_established": False}


if __name__ == "__main__":
    print(json.dumps(report(), sort_keys=True, indent=2))

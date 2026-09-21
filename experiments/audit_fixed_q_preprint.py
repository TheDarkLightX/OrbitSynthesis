#!/usr/bin/env python3
"""Portable, fail-closed gate for the fixed-Q preprint packet.

This gate replays the exact signed-router and parallel-program-vector evidence,
their independent audits, the conditional compiler ledger, the classical
transfer falsifiers, and all three Lean proof layers.  It intentionally does
not promote the integrated all-arity compiler beyond its stated frozen
premises, and it makes no novelty, patent, license, or performance finding.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "research/tournaments/2026-08-13-semantic-router-frontier"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], *, env: dict[str, str] | None = None) -> bytes:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        rendered = " ".join(command)
        raise RuntimeError(
            f"command failed ({completed.returncode}): {rendered}\n"
            f"stdout:\n{completed.stdout.decode(errors='replace')}\n"
            f"stderr:\n{completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def replay_file_pair(
    label: str,
    script: Path,
    arguments: list[str],
    output_flag: str,
    committed: Path,
    temp_root: Path,
) -> dict[str, str]:
    normal = temp_root / f"{label}.normal.json"
    optimized = temp_root / f"{label}.optimized.json"
    relative_script = str(script.relative_to(ROOT))
    run([sys.executable, relative_script, *arguments, output_flag, str(normal)])
    run([sys.executable, "-O", relative_script, *arguments, output_flag, str(optimized)])
    require(normal.read_bytes() == optimized.read_bytes(), f"{label}: normal/-O mismatch")
    require(normal.read_bytes() == committed.read_bytes(), f"{label}: committed receipt drift")
    receipt = json.loads(normal.read_text(encoding="utf-8"))
    semantic = receipt.get("semantic_sha256")
    require(isinstance(semantic, str), f"{label}: missing semantic_sha256")
    return {"file_sha256": sha256(normal), "semantic_sha256": semantic}


def check_lean(temp_root: Path) -> dict[str, str]:
    router = FRONTIER / "lanes/formal/StrongSignedRouter.lean"
    vector = FRONTIER / "lanes/formal_program_vector/ProgramVector.lean"
    cost = FRONTIER / "lanes/formal_program_vector_cost/ProgramVectorCost.lean"
    sources = (router, vector, cost)

    forbidden = re.compile(
        r"(^|[^A-Za-z0-9_])(sorry|admit)([^A-Za-z0-9_]|$)"
        r"|^[ \t]*(axiom|unsafe)[ \t]",
        re.MULTILINE,
    )
    for source in sources:
        text = source.read_text(encoding="utf-8")
        require(not forbidden.search(text), f"forbidden Lean placeholder/declaration: {source}")

    router_olean = temp_root / "StrongSignedRouter.olean"
    vector_olean = temp_root / "ProgramVector.olean"
    cost_olean = temp_root / "ProgramVectorCost.olean"
    base = ["lake", "env", "lean", "-t", "0", "-EwarningAsError=true"]
    run([*base, "-o", str(router_olean), str(router.relative_to(ROOT))])
    lean_env = os.environ.copy()
    lean_env["LEAN_PATH"] = str(temp_root)
    run([*base, "-o", str(vector_olean), str(vector.relative_to(ROOT))], env=lean_env)
    run([*base, "-o", str(cost_olean), str(cost.relative_to(ROOT))], env=lean_env)

    return {
        "StrongSignedRouter.lean": sha256(router),
        "ProgramVector.lean": sha256(vector),
        "ProgramVectorCost.lean": sha256(cost),
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="orbit-fixed-q-preprint-") as temporary:
        temp_root = Path(temporary)
        results: dict[str, object] = {}

        fused = FRONTIER / "lanes/fused"
        normal_summary = temp_root / "fused.normal.json"
        normal_witness = temp_root / "r27.normal.json"
        optimized_summary = temp_root / "fused.optimized.json"
        optimized_witness = temp_root / "r27.optimized.json"
        fused_script = str((fused / "check_strong_router_family.py").relative_to(ROOT))
        run(
            [
                sys.executable,
                fused_script,
                "--out",
                str(normal_summary),
                "--witness-out",
                str(normal_witness),
            ]
        )
        run(
            [
                sys.executable,
                "-O",
                fused_script,
                "--out",
                str(optimized_summary),
                "--witness-out",
                str(optimized_witness),
            ]
        )
        require(normal_summary.read_bytes() == optimized_summary.read_bytes(), "fused summary normal/-O mismatch")
        require(normal_witness.read_bytes() == optimized_witness.read_bytes(), "R27 normal/-O mismatch")
        require(normal_summary.read_bytes() == (fused / "summary.json").read_bytes(), "fused summary drift")
        require(normal_witness.read_bytes() == (fused / "r27_witness.json").read_bytes(), "R27 witness drift")
        results["signed_router_author"] = {
            "summary_sha256": sha256(normal_summary),
            "witness_sha256": sha256(normal_witness),
        }

        strong_audit = FRONTIER / "audits/strong_family"
        results["signed_router_independent_audit"] = replay_file_pair(
            "strong-family-audit",
            strong_audit / "audit_strong_family.py",
            [
                "--witness",
                str((fused / "r27_witness.json").relative_to(ROOT)),
                "--expected-witness-sha",
                "6dd402fd32bb560b341ee75805bd71c90e2fa2bd3c9274c982f908ef21c15e65",
                "--expected-author-sha",
                "07fb1d8d322e57a7af666bae5b699c072805ff1d15eef1f1e7c2d87208729ef8",
                "--expected-state-sha",
                "5304ad459b25928e14197dfb989af7dfae4d9df6b632eb79020e9f1cef812133",
            ],
            "--out",
            strong_audit / "receipt.json",
            temp_root,
        )

        vector = FRONTIER / "lanes/program_vector"
        results["program_vector_author"] = replay_file_pair(
            "program-vector-author",
            vector / "check_parallel_program_vector.py",
            [],
            "--out",
            vector / "receipt.json",
            temp_root,
        )

        vector_audit = FRONTIER / "audits/program_vector"
        results["program_vector_independent_audit"] = replay_file_pair(
            "program-vector-audit",
            vector_audit / "audit_program_vector.py",
            [],
            "--out",
            vector_audit / "receipt.json",
            temp_root,
        )

        variable_script = FRONTIER / "audits/variable_compiler/check_variable_compiler.py"
        variable_normal = run([sys.executable, str(variable_script.relative_to(ROOT))])
        variable_optimized = run([sys.executable, "-O", str(variable_script.relative_to(ROOT))])
        require(variable_normal == variable_optimized, "variable compiler normal/-O mismatch")
        require(b"CONDITIONAL_PASS_AFTER_RESIDUAL_FIRST_REPAIR" in variable_normal, "missing conditional compiler verdict")
        results["conditional_compiler_ledger"] = {
            "stdout_sha256": hashlib.sha256(variable_normal).hexdigest(),
            "semantic_sha256": "d81d0bd6b979ec0df4270fd60f04468884de6e286aea450ba28eed9897e51870",
        }

        transfer_script = FRONTIER / "lanes/classical_depth_transfer/check_transfer_barriers.py"
        transfer_normal = run([sys.executable, str(transfer_script.relative_to(ROOT))])
        transfer_optimized = run([sys.executable, "-O", str(transfer_script.relative_to(ROOT))])
        require(transfer_normal == transfer_optimized, "classical transfer normal/-O mismatch")
        transfer = json.loads(transfer_normal)
        require(transfer.get("status") == "PASS", "classical transfer falsifier failed")
        results["classical_transfer"] = {
            "semantic_sha256": transfer["semantic_sha256"],
        }

        results["lean"] = check_lean(temp_root)

    output = {
        "schema": "orbit-synthesis/fixed-q-preprint-gate/v1",
        "status": "PASS",
        "claim_boundary": (
            "Exact PASS for the signed-router and program-vector theorems and their local "
            "shared-DAG cost certificate. The all-arity r+O(log r) compiler remains conditional "
            "on its named frozen integration premises. Novelty, patent/FTO, license, practical "
            "performance, and publication readiness are not established by this gate."
        ),
        "results": results,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Portable, fail-closed gate for the fixed-Q preprint packet.

This gate replays the exact signed-router, historical E/G vector, optimized
sibling-shared vector, their independent audits, the historical conditional
ledger, the integrated compiler reconstruction, the classical-transfer
falsifiers, and the scoped Lean layers. It intentionally does not treat a
recurrence-only Lean file as extracted-DAG evidence or make a novelty, patent,
license, performance, peer-review, or publication finding.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "research/tournaments/2026-08-13-semantic-router-frontier"
OPT_FRONTIER = ROOT / "research/tournaments/2026-08-13-program-vector-optimization"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_review_binding(root: Path = ROOT) -> dict[str, object]:
    """Refuse drift from the reviewed current manuscript and replay inputs.

    This inventory is an integrity check, not an independent mathematical proof.
    Changing it requires a new source review; historical receipts stay intact.
    """
    subject = root / "research/replays/pr16-20260921/subject.json"
    record = json.loads(subject.read_text(encoding="utf-8"))
    require(record.get("schema") == "orbit-synthesis/preprint-review-subject/v1",
            "preprint review subject schema mismatch")
    files = record.get("sha256")
    require(type(files) is dict and files, "missing reviewed subject files")
    require("paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md" in files,
            "current manuscript absent from review binding")
    for name, digest in files.items():
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts,
                "review subject path escapes repository")
        require(type(digest) is str and re.fullmatch(r"[0-9a-f]{64}", digest),
                f"invalid review subject digest: {name}")
        require(sha256(root / path) == digest, f"reviewed subject changed: {name}")
    return {"subject_sha256": sha256(subject), "checked_files": len(files),
            "manuscript_sha256": files["paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md"],
            "meaning": "current source binding; mathematical coverage stays scoped"}


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


def ceil_log2(value: int) -> int:
    require(value >= 1, "ceil_log2 input")
    return (value - 1).bit_length()


def retained_binary_depth(arity: int) -> int:
    """Exact residual-first ledger used by the retained binary branch."""
    require(arity >= 2, "binary ledger arity")
    chunk = math.isqrt(arity)
    width = (3**chunk).bit_length() - 1
    levels = (arity - 1 + width - 1) // width
    return (chunk + 1) * levels + 2 * width + 3 * ceil_log2(arity) + 8


def check_binary_eventual_threshold() -> dict[str, object]:
    below = [arity for arity in range(2, 40001) if retained_binary_depth(arity) < arity]
    nonbelow = [arity for arity in range(2, 40001) if retained_binary_depth(arity) >= arity]
    require(below and nonbelow, "binary threshold corpus empty")
    require(min(below) == 273, "first isolated binary improvement drift")
    require(max(nonbelow) == 338, "last nonbelow binary arity drift")
    require(retained_binary_depth(338) == 338, "binary depth 338 drift")
    require(retained_binary_depth(339) == 338, "binary depth 339 drift")
    require(all(retained_binary_depth(arity) < arity for arity in range(339, 40001)),
            "339 is not an eventual threshold in checked range")
    return {
        "first_isolated_below_r": min(below),
        "last_nonbelow_r": max(nonbelow),
        "eventual_below_r_from": 339,
        "depth_338": retained_binary_depth(338),
        "depth_339": retained_binary_depth(339),
        "checked_through": 40000,
        "wording": "339 is the eventual threshold, not the first hit",
    }


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
    optimized = OPT_FRONTIER / "lanes/native_scan/OptimalRailSemantics.lean"
    formal_optimized = OPT_FRONTIER / "lanes/formal_optimized"
    direct = formal_optimized / "DirectRail.lean"
    sibling = formal_optimized / "SiblingShared.lean"
    axiom_audit = formal_optimized / "AxiomAudit.lean"
    formal_repairs = OPT_FRONTIER / "lanes/formal_manuscript_repairs"
    repair_source = formal_repairs / "ManuscriptRepairs.lean"
    repair_axiom_audit = formal_repairs / "AxiomAudit.lean"
    formal_gap = OPT_FRONTIER / "lanes/formal_gap_closure"
    gap_source = formal_gap / "DepthAndCensus.lean"
    gap_axiom_audit = formal_gap / "AxiomAudit.lean"
    sources = (
        router,
        vector,
        cost,
        optimized,
        direct,
        sibling,
        axiom_audit,
        repair_source,
        repair_axiom_audit,
        gap_source,
        gap_axiom_audit,
    )

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
    optimized_olean = temp_root / "OptimalRailSemantics.olean"
    direct_olean = temp_root / "DirectRail.olean"
    sibling_olean = temp_root / "SiblingShared.olean"
    repair_olean = temp_root / "ManuscriptRepairs.olean"
    gap_olean = temp_root / "DepthAndCensus.olean"
    base = ["lake", "env", "lean", "-t", "0", "-EwarningAsError=true"]
    run([*base, "-o", str(router_olean), str(router.relative_to(ROOT))])
    lean_env = os.environ.copy()
    lean_env["LEAN_PATH"] = str(temp_root)
    run([*base, "-o", str(vector_olean), str(vector.relative_to(ROOT))], env=lean_env)
    run([*base, "-o", str(cost_olean), str(cost.relative_to(ROOT))], env=lean_env)
    run([*base, "-o", str(optimized_olean), str(optimized.relative_to(ROOT))])
    run([*base, "-o", str(direct_olean), str(direct.relative_to(ROOT))], env=lean_env)
    run([*base, "-o", str(sibling_olean), str(sibling.relative_to(ROOT))], env=lean_env)
    axiom_stdout = run(
        ["lake", "env", "lean", "-t", "0", str(axiom_audit.relative_to(ROOT))],
        env=lean_env,
    )
    require(b"ofReduceBool" not in axiom_stdout, "optimized theorem depends on native_decide axiom")
    run([*base, "-o", str(repair_olean), str(repair_source.relative_to(ROOT))], env=lean_env)
    repair_axiom_stdout = run(
        ["lake", "env", "lean", "-t", "0", str(repair_axiom_audit.relative_to(ROOT))],
        env=lean_env,
    )
    require(b"ofReduceBool" not in repair_axiom_stdout, "repaired cardinality depends on native_decide axiom")
    require("native_decide" not in repair_source.read_text(encoding="utf-8"), "native_decide in repair source")
    run([*base, "-o", str(gap_olean), str(gap_source.relative_to(ROOT))], env=lean_env)
    gap_axiom_stdout = run(
        ["lake", "env", "lean", "-t", "0", str(gap_axiom_audit.relative_to(ROOT))],
        env=lean_env,
    )
    require(b"ofReduceBool" not in gap_axiom_stdout, "formal gap theorem depends on native_decide axiom")
    gap_receipt_path = formal_gap / "receipt.json"
    gap_receipt = json.loads(gap_receipt_path.read_text(encoding="utf-8"))
    require(
        gap_receipt.get("status") == "PASS_SHARP_DEPTH__PARTIAL_OUTPUT_CENSUS",
        "formal gap receipt status drift",
    )
    require(
        gap_receipt.get("source_sha256", {}).get("DepthAndCensus.lean") == sha256(gap_source),
        "formal gap receipt source binding drift",
    )

    formal_receipt_path = formal_optimized / "receipt.json"
    formal_receipt = json.loads(formal_receipt_path.read_text(encoding="utf-8"))
    require(
        formal_receipt.get("status") == "PASS_EXACT_DIRECT_RAIL_AND_SIBLING_SHARED_ENVELOPE",
        "optimized formal receipt status drift",
    )
    require(
        formal_receipt.get("lane_sha256", {}).get("DirectRail.lean") == sha256(direct)
        and formal_receipt.get("lane_sha256", {}).get("SiblingShared.lean") == sha256(sibling),
        "optimized formal receipt source binding drift",
    )

    return {
        "StrongSignedRouter.lean": sha256(router),
        "ProgramVector.lean": sha256(vector),
        "ProgramVectorCost.lean": sha256(cost),
        "OptimalRailSemantics.lean": sha256(optimized),
        "DirectRail.lean": sha256(direct),
        "SiblingShared.lean": sha256(sibling),
        "optimized_formal_receipt_sha256": sha256(formal_receipt_path),
        "optimized_axiom_audit_sha256": hashlib.sha256(axiom_stdout).hexdigest(),
        "ManuscriptRepairs.lean": sha256(repair_source),
        "manuscript_repair_axiom_audit_sha256": hashlib.sha256(repair_axiom_stdout).hexdigest(),
        "DepthAndCensus.lean": sha256(gap_source),
        "formal_gap_axiom_audit_sha256": hashlib.sha256(gap_axiom_stdout).hexdigest(),
        "formal_gap_receipt_sha256": sha256(gap_receipt_path),
        "legacy_native_decide_occurrences": str(
            sum(source.read_text(encoding="utf-8").count("native_decide") for source in (router, vector, cost))
        ),
    }


def main() -> None:
    reviewed_subject = check_review_binding()
    with tempfile.TemporaryDirectory(prefix="orbit-fixed-q-preprint-") as temporary:
        temp_root = Path(temporary)
        results: dict[str, object] = {}
        results["reviewed_current_subject"] = reviewed_subject
        results["binary_threshold_regression"] = check_binary_eventual_threshold()

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

        optimized = OPT_FRONTIER / "lanes/native_scan"
        results["optimized_program_vector_author"] = replay_file_pair(
            "optimized-program-vector-author",
            optimized / "check_optimal_scan.py",
            ["--max-width", "6"],
            "--out",
            optimized / "receipts/receipt.json",
            temp_root,
        )

        optimized_audit = OPT_FRONTIER / "lanes/referee/kuhn_boolean_rail_audit"
        results["optimized_program_vector_independent_audit"] = replay_file_pair(
            "optimized-program-vector-audit",
            optimized_audit / "audit_boolean_rails.py",
            [
                "--structural-width",
                "9",
                "--semantic-width",
                "6",
                "--arithmetic-width",
                "4096",
            ],
            "--out",
            optimized_audit / "receipt.json",
            temp_root,
        )

        algebraic = OPT_FRONTIER / "lanes/algebraic"
        algebraic_script = algebraic / "check_algebraic_program_vector.py"
        algebraic_normal = run([sys.executable, str(algebraic_script.relative_to(ROOT))])
        algebraic_optimized = run([sys.executable, "-O", str(algebraic_script.relative_to(ROOT))])
        require(algebraic_normal == algebraic_optimized, "algebraic vector normal/-O mismatch")
        algebraic_receipt = json.loads(algebraic_normal)
        require(algebraic_receipt.get("status") == "PASS", "algebraic vector audit failed")
        algebraic_committed = json.loads((algebraic / "receipt.json").read_text(encoding="utf-8"))
        require(algebraic_committed.get("status") == "PASS", "algebraic committed receipt failed")
        require(
            algebraic_committed.get("semantic_sha256") == algebraic_receipt.get("semantic_sha256"),
            "algebraic vector semantic receipt drift",
        )
        require(
            algebraic_committed.get("checker_sha256") == sha256(algebraic_script),
            "algebraic vector checker binding drift",
        )
        results["optimized_program_vector_second_reconstruction"] = {
            "receipt_sha256": sha256(algebraic / "receipt.json"),
            "stdout_sha256": hashlib.sha256(algebraic_normal).hexdigest(),
            "semantic_sha256": algebraic_receipt["semantic_sha256"],
        }

        variable_script = FRONTIER / "audits/variable_compiler/check_variable_compiler.py"
        variable_normal = run([sys.executable, str(variable_script.relative_to(ROOT))])
        variable_optimized = run([sys.executable, "-O", str(variable_script.relative_to(ROOT))])
        require(variable_normal == variable_optimized, "variable compiler normal/-O mismatch")
        require(b"CONDITIONAL_PASS_AFTER_RESIDUAL_FIRST_REPAIR" in variable_normal, "missing conditional compiler verdict")
        results["historical_conditional_compiler_ledger"] = {
            "stdout_sha256": hashlib.sha256(variable_normal).hexdigest(),
            "semantic_sha256": "d81d0bd6b979ec0df4270fd60f04468884de6e286aea450ba28eed9897e51870",
        }

        bridge = OPT_FRONTIER / "audits/compiler_bridge"
        bridge_script = bridge / "check_compiler_bridge.py"
        bridge_normal = run([sys.executable, str(bridge_script.relative_to(ROOT))])
        bridge_optimized = run([sys.executable, "-O", str(bridge_script.relative_to(ROOT))])
        require(bridge_normal == bridge_optimized, "compiler bridge normal/-O mismatch")
        require(
            hashlib.sha256(bridge_normal).hexdigest()
            == "ad2cba605d978f3e9e6c78608253a1db9b01da9366b75f70fcdc664f2df72dc1",
            "compiler bridge stdout drift",
        )
        bridge_result = json.loads(bridge_normal)
        require(
            bridge_result.get("status")
            == "PASS_I2_TO_I6__I1_AND_FINITE_FALLBACK_NOT_RECONSTRUCTED",
            "compiler bridge verdict drift",
        )
        require(
            bridge_result.get("semantic_sha256")
            == "73a43b1e4292b56824e82a471833e69252c52f212463f182a90df63703eec23e",
            "compiler bridge semantic drift",
        )
        bridge_receipt = json.loads((bridge / "receipt.json").read_text(encoding="utf-8"))
        require(
            bridge_receipt.get("semantic_sha256") == bridge_result.get("semantic_sha256"),
            "compiler bridge committed receipt drift",
        )
        results["integrated_compiler_independent_reconstruction"] = {
            "checker_sha256": sha256(bridge_script),
            "report_sha256": sha256(bridge / "REPORT.md"),
            "receipt_sha256": sha256(bridge / "receipt.json"),
            "semantic_sha256": bridge_result["semantic_sha256"],
            "stdout_sha256": hashlib.sha256(bridge_normal).hexdigest(),
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
            "Exact PASS for the signed-router and optimized local program-vector semantics, "
            "recurrence replay, and independent reconstructions. Lean coverage is scoped: the "
            "optimized semantic identities are formalized, while no serialized width-w DAG or "
            "integrated all-arity Lean theorem is certified. A separate no-author-import "
            "reconstruction passes both compiler branches, their legality, substitution, decoder, "
            "glue, and ledgers on the recorded domains. Complete compiler semantics are "
            "materialized only at arities 2-3; higher-arity sweeps check arithmetic ledgers. "
            "The current manuscript is source-bound to a separate agent review, not converted "
            "into an unconditional compiler verification by this executable gate. Historical "
            "manuscript-repair audit receipts remain excluded as mismatched and unreplayable. "
            "Novelty, patent/FTO, license, "
            "practical performance, and publication readiness are not established by this gate."
        ),
        "results": results,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

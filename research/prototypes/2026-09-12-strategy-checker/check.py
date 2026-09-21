"""Replay checker tests, CLI tests, and normal/optimized demo agreement."""

import json
import subprocess
import sys
import tempfile
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def command(args, cwd=HERE):
    completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=120, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return completed.stdout


def main():
    produced = []
    with tempfile.TemporaryDirectory(prefix="orbit-controller-replay-") as temp:
        for index, flags in enumerate((["-B"], ["-B", "-O"])):
            command([sys.executable, *flags, "-m", "unittest", "test_checker", "test_safety_export",
                     "test_controller_runtime"])
            output = Path(temp) / str(index)
            command([sys.executable, *flags, str(ROOT / "examples/controllers/synthesize_tau_net_gate.py"),
                     "--output-dir", str(output)])
            produced.append({p.name: p.read_bytes() for p in output.iterdir()})
            runtime_record = command([
                sys.executable, *flags, str(ROOT / "scripts/run_controller.py"),
                str(output / "contract.json"), str(output / "strategy.json"),
                str(output / "controller.osmc"), "--contract-pin", str(output / "contract.sha256"),
                "--inputs", "0", "1", "2", "3", "--json"])
            produced[-1]["runtime-replay.json"] = runtime_record.encode("ascii")
    if produced[0] != produced[1]:
        raise RuntimeError("normal and optimized producer artifacts differ")
    normal = command([sys.executable, "-B", "demo.py"])
    optimized = command([sys.executable, "-B", "-O", "demo.py"])
    if normal != optimized:
        raise RuntimeError("normal and optimized demo records differ")
    demo = json.loads(normal)
    paths = [ROOT / "src/orbitsynthesis/strategy_checker.py",
             ROOT / "src/orbitsynthesis/safety_export.py", ROOT / "src/orbitsynthesis/safety.py",
             ROOT / "src/orbitsynthesis/finite_algebra.py",
             ROOT / "src/orbitsynthesis/controller_compile.py",
             ROOT / "src/orbitsynthesis/controller_runtime.py", ROOT / "scripts/run_controller.py",
             ROOT / "scripts/check_controller.py", ROOT / "LICENSE", ROOT / "README.md"]
    paths += sorted(p for p in HERE.iterdir() if p.is_file() and p.name != "replay.json")
    paths += sorted(p for p in (HERE / "baselines").iterdir() if p.is_file())
    paths += sorted(p for p in (ROOT / "examples/controllers").iterdir() if p.is_file())
    result = {"schema": "orbitsynthesis/finite-controller-replay/v1", "status": "PASS",
              "exhaustive_graph_cases_per_mode": 33100, "seeded_product_cases_per_mode": 300,
              "exhaustive_producer_bridge_cases_per_mode": 8192,
              "producer_relation_models_per_mode": 256,
              "exhaustive_table_machines_per_mode": 592,
              "image_bit_corruptions_rejected_per_mode": 1120,
              "stateful_runtime_traces_per_mode": 1280,
              "table_runtime_replay": json.loads(produced[0]["runtime-replay.json"]),
              "producer_demo": json.loads(produced[0]["record.json"]),
              "intended_application_scope": "solely_tau_net",
              "normal_optimized_agree": True, "demo": demo,
              "known_faults_detected": ["unchecked_contract_pin", "skipped_safety",
                                        "omitted_recurrence", "ignored_second_input",
                                        "runtime_ignored_memory", "runtime_output_flip",
                                        "runtime_memory_update_flip", "omitted_runtime_comparison"],
              "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                for p in paths},
              "tau_execution_performed": False, "runtime_refinement_verified": False,
              "table_runtime_equivalence_verified": True, "native_codegen_verified": False,
              "patent_clearance_established": False}
    (HERE / "replay.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("PASS: 33,100 exhaustive models and 300 product cases per mode; CLI and counterexamples checked.")
    print("PASS: 8,192 producer bridge cases across 256 safety games per mode.")
    print("PASS: 592 table machines, 1,120 image bit corruptions, 1,280 runtime traces per mode.")
    print("Normal and python -O demo records agree. Wrote replay.json.")


if __name__ == "__main__":
    main()

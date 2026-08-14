#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
require_pysat=0
if [[ "${1:-}" == "--require-pysat" ]]; then
  require_pysat=1
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--require-pysat]" >&2
  exit 2
fi

primary="$lane_dir/check_external_optimization.py"
independent="$lane_dir/audits/independent/audit_external_optimization_independent.py"
independent_receipt="$lane_dir/audits/independent/receipt.json"
reference="$lane_dir/tools/reference_maxsat_solver.py"
normal="$(mktemp)"
optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized" "$independent_normal" "$independent_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/external_optimization.py \
  src/orbitsynthesis/domain_model.py \
  src/orbitsynthesis/domain_solver.py \
  src/orbitsynthesis/domain_optimization.py \
  "$reference" "$primary" "$independent"

primary_args=()
if [[ $require_pysat -eq 1 ]]; then
  primary_args+=(--require-pysat)
fi
PYTHONPATH=src python3 "$primary" "${primary_args[@]}" > "$normal"
PYTHONPATH=src python3 -O "$primary" "${primary_args[@]}" > "$optimized"
cmp "$normal" "$optimized"

python3 "$independent" > "$independent_normal"
python3 -O "$independent" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"
cmp "$independent_normal" "$independent_receipt"

python3 - "$normal" "$independent_normal" "$require_pysat" <<'PY'
import json
import sys

primary = json.load(open(sys.argv[1], encoding="utf-8"))
independent = json.load(open(sys.argv[2], encoding="utf-8"))
require_pysat = bool(int(sys.argv[3]))
corpus = primary["corpus"]
assert corpus["families"] == independent["families"] == 4
assert corpus["scenarios"] == independent["instances"] == 20
assert corpus["highs_cases"] == 20
assert corpus["command_cases"] == 20
if require_pysat:
    assert corpus["pysat_available"] is True
    assert corpus["pysat_cases"] == 20

primary_expected = {
    (row[0], row[1]): row[2]
    for row in corpus["rows"]
}
independent_expected = {
    (row[0], row[1]): row[2]
    for row in independent["rows"]
}
assert primary_expected == independent_expected
assert primary["mutations"]["rejected"] == [
    "wrong_cost",
    "non_optimal_status",
    "missing_model",
    "timeout",
    "highs_precision_guard",
]
print(json.dumps({
    "status": "PASS",
    "highs_cases": corpus["highs_cases"],
    "command_cases": corpus["command_cases"],
    "pysat_cases": corpus["pysat_cases"],
    "pysat_available": corpus["pysat_available"],
    "primary_semantic_sha256": primary["semantic_sha256"],
    "independent_semantic_sha256": independent["semantic_sha256"],
}, indent=2, sort_keys=True))
PY

sha256sum \
  src/orbitsynthesis/external_optimization.py \
  "$reference" "$primary" "$normal" \
  "$independent" "$independent_receipt" "$independent_normal"

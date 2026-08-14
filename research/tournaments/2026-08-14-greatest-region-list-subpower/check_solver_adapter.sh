#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
script="$lane_dir/check_solver_adapter.py"
normal="$(mktemp)"
optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/domain_model.py \
  src/orbitsynthesis/domain_solver.py \
  src/orbitsynthesis/solver_adapter.py \
  "$script"

python3 "$script" > "$normal"
python3 -O "$script" > "$optimized"
cmp "$normal" "$optimized"

python3 - "$normal" <<'PY'
import json
import sys

receipt = json.load(open(sys.argv[1], encoding="utf-8"))
assert receipt["reference"] == {
    "domain": [[0], [2]],
    "hard_clauses": 7,
    "optimum_cost": 3,
    "optimum_weight": 6,
    "variables": 7,
}
assert receipt["cnf"]["status"] == "SATISFIABLE"
assert receipt["cnf"]["return_code"] == 10
assert receipt["cnf"]["model_literals"] == 7
assert receipt["cnf"]["shell_metacharacters_inert"] is True
assert receipt["weighted_claim"] == {
    "claimed_optimum": True,
    "expected_cost": 3,
    "optimality_verified": False,
    "reported_cost": 3,
    "status": "OPTIMUM FOUND",
}
assert receipt["weighted_verified"] == {
    "known_optimum_cost": 3,
    "optimality_verified": True,
}
assert all(receipt["mutations"].values())
assert receipt["semantic_sha256"] == (
    "1d9baa61591736042271826ad4f036688cca8489e8bb9183582cdab4db86f4d8"
)
PY

sha256sum \
  "$script" "$normal" \
  src/orbitsynthesis/solver_adapter.py

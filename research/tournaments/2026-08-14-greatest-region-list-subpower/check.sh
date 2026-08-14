#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_frontiers.py"
independent="$lane_dir/audits/independent/audit_frontiers_independent.py"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$independent_normal" "$independent_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/finite_algebra.py \
  src/orbitsynthesis/patchability.py \
  src/orbitsynthesis/safety.py \
  src/orbitsynthesis/subpower_lists.py \
  src/orbitsynthesis/greatest_region_boundary.py \
  "$primary" \
  "$independent"

python3 "$primary" > "$primary_normal"
python3 -O "$primary" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"

python3 "$independent" > "$independent_normal"
python3 -O "$independent" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"

python3 - "$primary_normal" "$independent_normal" <<'PY'
import json
import sys

primary = json.load(open(sys.argv[1], encoding="utf-8"))
independent = json.load(open(sys.argv[2], encoding="utf-8"))

assert primary["list_subpower"]["exact_instances"] == 27510
assert primary["greatest_region"]["demi_semi_primal_count"] == 15
assert primary["greatest_region"]["non_demi_semi_primal_count"] == 12
assert primary["greatest_region"]["quackenbush_q_checkpoint"]["audit"] == {
    "groupoid_invariant": True,
    "left_feasible": True,
    "right_feasible": True,
    "union_feasible": False,
}
assert primary["randomized_lists"]["instances"] == 400

assert independent["list_subpower"]["instances"] == 14280
assert independent["greatest_region"]["demi"] == 15
assert independent["greatest_region"]["non_demi"] == 12
PY

sha256sum \
  "$primary" "$primary_normal" \
  "$independent" "$independent_normal" \
  src/orbitsynthesis/subpower_lists.py \
  src/orbitsynthesis/greatest_region_boundary.py

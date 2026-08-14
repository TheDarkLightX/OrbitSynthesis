#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_frontiers.py"
independent="$lane_dir/audits/independent/audit_frontiers_independent.py"
principal="$lane_dir/check_principal_equation.py"
principal_independent="$lane_dir/audits/independent/audit_principal_equation_independent.py"
component_backend="$lane_dir/check_component_backend.py"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
principal_normal="$(mktemp)"
principal_optimized="$(mktemp)"
principal_independent_normal="$(mktemp)"
principal_independent_optimized="$(mktemp)"
component_normal="$(mktemp)"
component_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$independent_normal" "$independent_optimized" "$principal_normal" "$principal_optimized" "$principal_independent_normal" "$principal_independent_optimized" "$component_normal" "$component_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/finite_algebra.py \
  src/orbitsynthesis/patchability.py \
  src/orbitsynthesis/safety.py \
  src/orbitsynthesis/subpower_lists.py \
  src/orbitsynthesis/greatest_region_boundary.py \
  src/orbitsynthesis/principal_greatest_region.py \
  src/orbitsynthesis/safety_components.py \
  "$primary" \
  "$independent" \
  "$principal" \
  "$principal_independent" \
  "$component_backend"

python3 "$primary" > "$primary_normal"
python3 -O "$primary" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"

python3 "$independent" > "$independent_normal"
python3 -O "$independent" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"

python3 "$principal" > "$principal_normal"
python3 -O "$principal" > "$principal_optimized"
cmp "$principal_normal" "$principal_optimized"

python3 "$principal_independent" > "$principal_independent_normal"
python3 -O "$principal_independent" > "$principal_independent_optimized"
cmp "$principal_independent_normal" "$principal_independent_optimized"

python3 "$component_backend" > "$component_normal"
python3 -O "$component_backend" > "$component_optimized"
cmp "$component_normal" "$component_optimized"

python3 - \
  "$primary_normal" "$independent_normal" \
  "$principal_normal" "$principal_independent_normal" \
  "$component_normal" <<'PY'
import json
import sys

primary = json.load(open(sys.argv[1], encoding="utf-8"))
independent = json.load(open(sys.argv[2], encoding="utf-8"))
principal = json.load(open(sys.argv[3], encoding="utf-8"))
principal_independent = json.load(open(sys.argv[4], encoding="utf-8"))
component = json.load(open(sys.argv[5], encoding="utf-8"))

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

assert principal["demi_semi_primal_count"] == 15
assert principal["non_demi_semi_primal_count"] == 12
assert principal["flattened_rows_checked"] == 236196
assert principal["quackenbush_q"]["exact_equation"] is True
assert principal["quackenbush_q"]["separator_subalgebra_preserving"] is True
assert principal["quackenbush_q"]["separator_groupoid_equivariant"] is True
assert principal["quackenbush_q"]["union_feasible"] is False

assert principal_independent["demi"] == 15
assert principal_independent["non_demi"] == 12
assert principal_independent["flattened_rows_checked"] == 236196
assert principal_independent["classifications"] == principal["classifications"]

assert component["random_differential"]["domain_instances"] == 768
assert component["random_differential"]["feasible"] == 165
assert component["random_differential"]["infeasible"] == 603
assert [
    row["feasible"] for row in component["principal_differential"]
] == [True, True, False]
assert component["targeted"]["component_size"] == 2
PY

sha256sum \
  "$primary" "$primary_normal" \
  "$independent" "$independent_normal" \
  "$principal" "$principal_normal" \
  "$principal_independent" "$principal_independent_normal" \
  "$component_backend" "$component_normal" \
  src/orbitsynthesis/subpower_lists.py \
  src/orbitsynthesis/greatest_region_boundary.py \
  src/orbitsynthesis/principal_greatest_region.py \
  src/orbitsynthesis/safety_components.py

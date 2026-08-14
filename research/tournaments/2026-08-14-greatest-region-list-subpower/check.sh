#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_frontiers.py"
independent="$lane_dir/audits/independent/audit_frontiers_independent.py"
principal="$lane_dir/check_principal_equation.py"
principal_independent="$lane_dir/audits/independent/audit_principal_equation_independent.py"
component_backend="$lane_dir/check_component_backend.py"
domain_model="$lane_dir/check_domain_model.py"
domain_solver="$lane_dir/check_domain_solver.py"
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
domain_normal="$(mktemp)"
domain_optimized="$(mktemp)"
solver_normal="$(mktemp)"
solver_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$independent_normal" "$independent_optimized" "$principal_normal" "$principal_optimized" "$principal_independent_normal" "$principal_independent_optimized" "$component_normal" "$component_optimized" "$domain_normal" "$domain_optimized" "$solver_normal" "$solver_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/finite_algebra.py \
  src/orbitsynthesis/patchability.py \
  src/orbitsynthesis/safety.py \
  src/orbitsynthesis/subpower_lists.py \
  src/orbitsynthesis/greatest_region_boundary.py \
  src/orbitsynthesis/principal_greatest_region.py \
  src/orbitsynthesis/safety_components.py \
  src/orbitsynthesis/domain_model.py \
  src/orbitsynthesis/domain_solver.py \
  "$primary" \
  "$independent" \
  "$principal" \
  "$principal_independent" \
  "$component_backend" \
  "$domain_model" \
  "$domain_solver"

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

python3 "$domain_model" > "$domain_normal"
python3 -O "$domain_model" > "$domain_optimized"
cmp "$domain_normal" "$domain_optimized"

python3 "$domain_solver" > "$solver_normal"
python3 -O "$domain_solver" > "$solver_optimized"
cmp "$solver_normal" "$solver_optimized"

python3 - \
  "$primary_normal" "$independent_normal" \
  "$principal_normal" "$principal_independent_normal" \
  "$component_normal" "$domain_normal" "$solver_normal" <<'PY'
import json
import sys

primary = json.load(open(sys.argv[1], encoding="utf-8"))
independent = json.load(open(sys.argv[2], encoding="utf-8"))
principal = json.load(open(sys.argv[3], encoding="utf-8"))
principal_independent = json.load(open(sys.argv[4], encoding="utf-8"))
component = json.load(open(sys.argv[5], encoding="utf-8"))
domain = json.load(open(sys.argv[6], encoding="utf-8"))
solver = json.load(open(sys.argv[7], encoding="utf-8"))

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

assert domain["targeted"]["components"] == 2
assert domain["targeted"]["candidate_rules"] == 4
assert domain["targeted"]["variables"] == 7
assert domain["targeted"]["clauses"] == 7
assert domain["targeted"]["weighted_top"] == 10
assert domain["random_differential"]["domain_instances"] == 768
assert domain["random_differential"]["cnf_checks"] == 768
assert domain["random_differential"]["feasible"] == 145
assert domain["random_differential"]["infeasible"] == 623
assert [
    row["feasible"] for row in domain["principal_differential"]["rows"]
] == [True, True, False]
assert domain["semantic_sha256"] == (
    "d12b80867b60303ba80b079800f8ca8ff36aedf0a20637776fcdae10f9c18a46"
)

assert solver["targeted"]["optimum_weight"] == 6
assert solver["targeted"]["optimum_domain"] == [[0], [2]]
assert solver["targeted"]["contradictory_mutation_rejected"] is True
assert solver["targeted"]["selector_mutation_rejected"] is True
assert solver["random_weighted"]["instances"] == 64
assert solver["random_weighted"]["decoded_optima"] == 37
assert solver["random_weighted"]["infeasible_required_sets"] == 27
assert solver["principal"]["states"] == 81
assert solver["principal"]["components"] == 227
assert solver["principal"]["candidate_rules"] == 17174
assert solver["principal"]["variables"] == 17255
assert solver["principal"]["clauses"] == 17407
assert solver["semantic_sha256"] == (
    "2fefedfe42c1ebdd5110df4793fc511a0c0e2a6d3b7b92b332e4a70ef531c3ee"
)
PY

sha256sum \
  "$primary" "$primary_normal" \
  "$independent" "$independent_normal" \
  "$principal" "$principal_normal" \
  "$principal_independent" "$principal_independent_normal" \
  "$component_backend" "$component_normal" \
  "$domain_model" "$domain_normal" \
  "$domain_solver" "$solver_normal" \
  src/orbitsynthesis/subpower_lists.py \
  src/orbitsynthesis/greatest_region_boundary.py \
  src/orbitsynthesis/principal_greatest_region.py \
  src/orbitsynthesis/safety_components.py \
  src/orbitsynthesis/domain_model.py \
  src/orbitsynthesis/domain_solver.py

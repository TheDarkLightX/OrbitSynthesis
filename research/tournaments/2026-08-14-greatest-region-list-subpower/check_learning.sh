#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
nogood="$lane_dir/check_domain_nogood.py"
learning="$lane_dir/check_domain_learning.py"
independent="$lane_dir/audits/independent/audit_domain_learning_independent.py"
adapter="$lane_dir/check_solver_adapter.py"
nogood_normal="$(mktemp)"
nogood_optimized="$(mktemp)"
learning_normal="$(mktemp)"
learning_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
adapter_normal="$(mktemp)"
adapter_optimized="$(mktemp)"
trap 'rm -f "$nogood_normal" "$nogood_optimized" "$learning_normal" "$learning_optimized" "$independent_normal" "$independent_optimized" "$adapter_normal" "$adapter_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/domain_nogood.py \
  src/orbitsynthesis/domain_learning.py \
  src/orbitsynthesis/solver_adapter.py \
  "$nogood" "$learning" "$independent" "$adapter"

python3 "$nogood" > "$nogood_normal"
python3 -O "$nogood" > "$nogood_optimized"
cmp "$nogood_normal" "$nogood_optimized"

python3 "$learning" > "$learning_normal"
python3 -O "$learning" > "$learning_optimized"
cmp "$learning_normal" "$learning_optimized"

python3 "$independent" > "$independent_normal"
python3 -O "$independent" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"

python3 "$adapter" > "$adapter_normal"
python3 -O "$adapter" > "$adapter_optimized"
cmp "$adapter_normal" "$adapter_optimized"

python3 - "$nogood_normal" "$learning_normal" "$independent_normal" "$adapter_normal" <<'PY'
import json
import sys

nogood = json.load(open(sys.argv[1], encoding="utf-8"))
learning = json.load(open(sys.argv[2], encoding="utf-8"))
independent = json.load(open(sys.argv[3], encoding="utf-8"))
adapter = json.load(open(sys.argv[4], encoding="utf-8"))

assert nogood["synthetic"]["candidate_count"] == 3
assert len(nogood["synthetic"]["core"]) == 1
assert nogood["random_differential"]["failed_domains"] == 591
assert nogood["random_differential"]["matching_domains_checked"] == 1781
assert nogood["random_differential"]["clauses_checked"] == 591
assert nogood["random_differential"]["minimum_core_size"] == 1
assert nogood["random_differential"]["maximum_core_size"] == 3
assert nogood["random_differential"]["total_core_literals"] == 897
assert nogood["random_differential"]["total_clause_literals"] == 897
assert nogood["principal"]["core_literals"]

assert learning["synthetic"]["states"] == 12
assert learning["synthetic"]["reference_domain_checks"] == 4096
assert learning["synthetic"]["learned_model_checks"] == 2
assert learning["synthetic"]["learned_cores"] == 1
assert learning["synthetic"]["learned_literals"] == 1
assert learning["synthetic"]["optimum_weight"] == 11
assert learning["synthetic"]["max_round_guard_rejected"] is True
assert learning["random_exact"]["relations"] == 24
assert learning["random_exact"]["states_per_relation"] == 9
assert learning["random_exact"]["reference_component_model_checks"] == 12288
assert learning["random_exact"]["learned_component_model_checks"] == 54
assert learning["random_exact"]["learned_core_count"] == 30
assert learning["random_exact"]["learned_literal_count"] == 57
assert learning["random_exact"]["matching_domains_checked"] == 4544
assert learning["random_exact"]["eager_hard_clause_total"] == 1079
assert learning["random_exact"]["lazy_learned_clause_total"] == 30
assert all(learning["mutations"].values())

assert independent["exhaustive_minimizer"]["two_candidate_condition_families"] == 30625
assert independent["exhaustive_minimizer"]["core_matching_assignments"] == 147766
assert independent["randomized_multicandidate"]["instances"] == 2000
assert independent["randomized_multicandidate"]["total_core_literals"] == 7351
assert independent["lazy_synthetic"]["state_assignments"] == 4096
assert independent["lazy_synthetic"]["component_checks"] == 2
assert independent["lazy_synthetic"]["learned_cores"] == 1
assert independent["lazy_synthetic"]["optimum_weight"] == 11

assert adapter["reference"]["optimum_weight"] == 6
assert adapter["reference"]["optimum_cost"] == 3
assert adapter["cnf"]["shell_metacharacters_inert"] is True
assert adapter["weighted_claim"]["claimed_optimum"] is True
assert adapter["weighted_claim"]["optimality_verified"] is False
assert adapter["weighted_verified"]["optimality_verified"] is True
assert all(adapter["mutations"].values())
PY

sha256sum \
  "$nogood" "$nogood_normal" \
  "$learning" "$learning_normal" \
  "$independent" "$independent_normal" \
  "$adapter" "$adapter_normal" \
  src/orbitsynthesis/domain_nogood.py \
  src/orbitsynthesis/domain_learning.py \
  src/orbitsynthesis/solver_adapter.py

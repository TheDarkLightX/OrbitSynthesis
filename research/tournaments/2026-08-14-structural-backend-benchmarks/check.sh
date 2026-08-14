#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_structural_backends.py"
authority="$lane_dir/check_authority_binding.py"
independent="$lane_dir/audits/independent/audit_structural_families_independent.py"
independent_receipt="$lane_dir/audits/independent/receipt.json"
require_pysat=0
if [[ "${1:-}" == "--require-pysat" ]]; then
  require_pysat=1
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--require-pysat]" >&2
  exit 2
fi

primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
authority_normal="$(mktemp)"
authority_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$authority_normal" "$authority_optimized" "$independent_normal" "$independent_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/optimization_authority.py \
  src/orbitsynthesis/structural_benchmarks.py \
  "$primary" "$authority" "$independent"

primary_args=()
if [[ $require_pysat -eq 1 ]]; then
  primary_args+=(--require-pysat)
fi
PYTHONPATH=src python3 "$primary" "${primary_args[@]}" > "$primary_normal"
PYTHONPATH=src python3 -O "$primary" "${primary_args[@]}" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"

PYTHONPATH=src python3 "$authority" > "$authority_normal"
PYTHONPATH=src python3 -O "$authority" > "$authority_optimized"
cmp "$authority_normal" "$authority_optimized"

python3 "$independent" > "$independent_normal"
python3 -O "$independent" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"
cmp "$independent_normal" "$independent_receipt"

python3 - "$primary_normal" "$authority_normal" "$independent_normal" "$require_pysat" <<'PY'
import json
import sys

primary = json.load(open(sys.argv[1], encoding="utf-8"))
authority = json.load(open(sys.argv[2], encoding="utf-8"))
independent = json.load(open(sys.argv[3], encoding="utf-8"))
require_pysat = bool(int(sys.argv[4]))

assert [row["closed_form_maxima"] for row in primary["antichain"]] == [4, 64]
assert [row["replayed_maxima"] for row in primary["antichain"]] == [4, 64]
assert [row["maximal_domain_size"] for row in primary["antichain"]] == [24, 74]
assert [row["preferred_score"] for row in primary["antichain"]] == [30, 200]
assert [row["closed_form_maxima"] for row in primary["antichain"]] == [
    row["maximal_domains"] for row in independent["antichain"]
]
assert [row["preferred_score"] for row in primary["antichain"]] == [
    row["preferred_score"] for row in independent["antichain"]
]
assert primary["antichain"][0]["native"]["score"] == 30
assert all(row["backends"]["highs"]["certificate_verified"] for row in primary["antichain"])
assert all(row["backends"]["highs"]["optimality_authority"] == "closed_form_antichain" for row in primary["antichain"])

principal = primary["principal"]
assert principal["states"] == 81
assert principal["observations"] == 243
assert principal["direct_pattern"] == {
    "left_feasible": True,
    "right_feasible": True,
    "union_feasible": False,
}
assert principal["weighted_restriction"]["assignments_checked"] == 16
assert principal["weighted_restriction"]["feasible_domains_checked"] == 8
assert principal["weighted_restriction"]["optimum_score"] == 13
assert principal["weighted_restriction"]["optimum_score"] == independent["principal"]["optimum_score"]
assert principal["weighted_restriction"]["backends"]["highs"]["certificate_verified"] is True
assert principal["weighted_restriction"]["backends"]["highs"]["optimality_authority"] == "bounded_principal_union"
assert principal["forced_union"]["assignments_checked"] == 1
assert principal["forced_union"]["feasible_domains_checked"] == 0
assert principal["forced_union"]["backends"]["highs"]["status"] == "infeasible"
assert principal["forced_union"]["backends"]["highs"]["optimality_authority"] == "bounded_principal_union_infeasible"

assert authority["model_hashes_distinct"] is True
assert authority["wrong_model_rejected"] is True
assert authority["forged_witness_rejected"] is True
assert authority["wrong_infeasible_model_rejected"] is True
assert authority["objective_hash_changed"] is True
assert authority["promoted_authority"] == "binding_test"
assert authority["promoted_infeasible_authority"] == "bounded_binding_infeasible"

if require_pysat:
    assert all(row["pysat_available"] is True for row in primary["antichain"])
    assert principal["pysat_available"] is True
    assert all("pysat_rc2" in row["backends"] for row in primary["antichain"])
    assert "pysat_rc2" in principal["weighted_restriction"]["backends"]
    assert "pysat_rc2" in principal["forced_union"]["backends"]

print(json.dumps({
    "status": "PASS",
    "antichain_maxima": [4, 64],
    "principal_variables": principal["base_cnf_variables"],
    "principal_candidate_rules": principal["candidate_rule_count"],
    "primary_semantic_sha256": primary["semantic_sha256"],
    "authority_semantic_sha256": authority["semantic_sha256"],
    "independent_semantic_sha256": independent["semantic_sha256"],
}, indent=2, sort_keys=True))
PY

sha256sum \
  src/orbitsynthesis/optimization_authority.py \
  src/orbitsynthesis/structural_benchmarks.py \
  "$primary" "$primary_normal" \
  "$authority" "$authority_normal" \
  "$independent" "$independent_receipt" "$independent_normal"

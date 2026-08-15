#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_role_orbit_rank.py"
independent="$lane_dir/audits/independent/audit_role_orbit_rank_independent.py"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$independent_normal" "$independent_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/role_orbit_witness.py \
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

for receipt in (primary, independent):
    assert receipt["demi"] == 15
    assert receipt["non_demi"] == 12
    assert receipt["role_rank_distribution"] == {"3": 12}
    assert receipt["strict_improvements_over_generator_tags"] == 6
    assert receipt["flattened_rows_checked"] == 26244
    assert receipt["aggregate_domain_models"]["role_orbits"] == {
        "states": 324,
        "observations": 972,
        "components": 876,
        "candidate_rules": 19392,
        "variables": 19716,
        "hard_clauses": 20010,
    }
    assert receipt["quackenbush_q"]["generating_orbit_counts"] == [1, 2, 4]
    assert receipt["quackenbush_q"]["domain_model"] == {
        "states": 27,
        "observations": 81,
        "components": 73,
        "candidate_rules": 1762,
        "variables": 1789,
        "hard_clauses": 1817,
    }

assert independent["semantic_sha256"] == (
    "a33f884a4da2882f850a1b131c438133bcde355ecac5aa0bd2892fe0090b746f"
)
assert primary["classifications"] == independent["classifications"]
PY

sha256sum \
  src/orbitsynthesis/role_orbit_witness.py \
  "$primary" "$primary_normal" \
  "$independent" "$independent_normal"

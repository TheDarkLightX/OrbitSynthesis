#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_generator_compression.py"
independent="$lane_dir/audits/independent/audit_generator_compression_independent.py"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$independent_normal" "$independent_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/generator_compressed_witness.py \
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

for result in (primary, independent):
    assert result["demi"] == 15
    assert result["non_demi"] == 12
    assert result["arity_distribution"] == {"3": 6, "4": 6}
    assert result["strict_arity_reductions"] == 6
    assert result["flattened_rows_checked"] == 131220
    assert result["baseline_flattened_rows"] == 236196
    assert result["quackenbush_q"]["state_arity"] == 3
    assert result["quackenbush_q"]["baseline_arity"] == 4
    assert result["quackenbush_q"]["principal_rows"] == 2187
    assert result["quackenbush_q"]["unsafe_groupoid_orbits"] == 98

assert primary["quackenbush_q"]["single_global_alternate_exists"] is False
assert (
    independent["quackenbush_q"]["no_single_alternate_projection_exists"]
    is True
)
assert primary["quackenbush_q"]["compressed_model"] == {
    "candidate_rules": 1762,
    "clauses": 1817,
    "components": 73,
    "observations": 81,
    "states": 27,
    "variables": 1789,
}
assert primary["quackenbush_q"]["baseline_model"] == {
    "candidate_rules": 17174,
    "clauses": 17405,
    "components": 227,
    "observations": 243,
    "states": 81,
    "variables": 17255,
}
assert independent["semantic_sha256"] == (
    "3bab14c0844a2c16475746758444e3e55a901bc9e85ded9278923353131da60f"
)
PY

sha256sum \
  src/orbitsynthesis/generator_compressed_witness.py \
  "$primary" "$primary_normal" \
  "$independent" "$independent_normal"

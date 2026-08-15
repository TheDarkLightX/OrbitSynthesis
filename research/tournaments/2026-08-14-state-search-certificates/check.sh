#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_state_search_certificates.py"
independent="$lane_dir/audits/independent/audit_state_search_independent.py"
independent_receipt="$lane_dir/audits/independent/receipt.json"
validator="$lane_dir/validate_receipts.py"
cli="$repo_dir/tools/orbit_state_certificate.py"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
cli_certificate="$(mktemp)"
cli_generate="$(mktemp)"
cli_verify="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$independent_normal" "$independent_optimized" "$cli_certificate" "$cli_generate" "$cli_verify"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/state_optimality_certificate.py \
  src/orbitsynthesis/optimization_authority.py \
  src/orbitsynthesis/structural_benchmarks.py \
  "$primary" "$independent" "$validator" "$cli"

PYTHONPATH=src python3 "$primary" > "$primary_normal"
PYTHONPATH=src python3 -O "$primary" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"

python3 "$independent" > "$independent_normal"
python3 -O "$independent" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"
cmp "$independent_normal" "$independent_receipt"

python3 "$validator" "$primary_normal" "$independent_normal"

PYTHONPATH=src python3 "$cli" generate \
  --example principal-infeasible \
  --out "$cli_certificate" > "$cli_generate"
PYTHONPATH=src python3 "$cli" verify \
  --example principal-infeasible \
  --input "$cli_certificate" > "$cli_verify"
python3 - "$cli_generate" "$cli_verify" <<'PY'
import json
import sys
left = json.load(open(sys.argv[1], encoding="utf-8"))
right = json.load(open(sys.argv[2], encoding="utf-8"))
assert left == right
assert left["verified"] is True
assert left["claim"] == "infeasible"
PY

sha256sum \
  src/orbitsynthesis/state_optimality_certificate.py \
  "$primary" "$primary_normal" \
  "$independent" "$independent_receipt" "$independent_normal" \
  "$cli" "$cli_certificate"

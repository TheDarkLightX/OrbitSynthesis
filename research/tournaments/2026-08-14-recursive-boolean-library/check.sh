#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
primary="$lane_dir/check_recursive_boolean_library.py"
primary_receipt="$lane_dir/receipt.json"
independent="$lane_dir/audits/independent/audit_recursive_boolean_library_independent.py"
independent_receipt="$lane_dir/audits/independent/receipt.json"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$independent_normal" "$independent_optimized"' EXIT

python3 "$primary" --expected "$primary_receipt" > "$primary_normal"
python3 -O "$primary" --expected "$primary_receipt" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"

python3 "$independent" --expected "$independent_receipt" > "$independent_normal"
python3 -O "$independent" --expected "$independent_receipt" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"

sha256sum \
  "$primary" "$primary_receipt" "$primary_normal" \
  "$independent" "$independent_receipt" "$independent_normal"

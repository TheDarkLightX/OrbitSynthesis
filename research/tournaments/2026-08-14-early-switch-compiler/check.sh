#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script="$lane_dir/check_early_switch_compiler.py"
receipt="$lane_dir/receipt.json"
audit_dir="$lane_dir/audits/independent"
audit_script="$audit_dir/audit_early_switch_arithmetic.py"
audit_receipt="$audit_dir/receipt.json"
normal="$(mktemp)"
optimized="$(mktemp)"
audit_normal="$(mktemp)"
audit_optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized" "$audit_normal" "$audit_optimized"' EXIT

python3 "$script" --expected "$receipt" > "$normal"
python3 -O "$script" --expected "$receipt" > "$optimized"
cmp "$normal" "$optimized"
cmp "$normal" "$receipt"

python3 "$audit_script" --expected "$audit_receipt" > "$audit_normal"
python3 -O "$audit_script" --expected "$audit_receipt" > "$audit_optimized"
cmp "$audit_normal" "$audit_optimized"
cmp "$audit_normal" "$audit_receipt"

sha256sum \
  "$script" "$receipt" "$normal" \
  "$audit_script" "$audit_receipt" "$audit_normal"

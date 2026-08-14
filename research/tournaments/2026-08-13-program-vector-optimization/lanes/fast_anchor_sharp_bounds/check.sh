#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script="$lane_dir/check_fast_anchor_sharp_bounds.py"
receipt="$lane_dir/receipt.json"
profile_script="$lane_dir/check_fast_anchor_profile.py"
profile_receipt="$lane_dir/anchor_profile_receipt.json"
normal="$(mktemp)"
optimized="$(mktemp)"
profile_normal="$(mktemp)"
profile_optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized" "$profile_normal" "$profile_optimized"' EXIT

python3 "$script" --expected "$receipt" > "$normal"
python3 -O "$script" --expected "$receipt" > "$optimized"
cmp "$normal" "$optimized"
cmp "$normal" "$receipt"

python3 "$profile_script" > "$profile_normal"
python3 -O "$profile_script" > "$profile_optimized"
cmp "$profile_normal" "$profile_optimized"
cmp "$profile_normal" "$profile_receipt"

sha256sum \
  "$script" "$receipt" "$normal" \
  "$profile_script" "$profile_receipt" "$profile_normal"

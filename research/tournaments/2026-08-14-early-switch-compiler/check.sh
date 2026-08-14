#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script="$lane_dir/check_early_switch_compiler.py"
receipt="$lane_dir/receipt.json"
normal="$(mktemp)"
optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized"' EXIT

python3 "$script" --expected "$receipt" > "$normal"
python3 -O "$script" --expected "$receipt" > "$optimized"
cmp "$normal" "$optimized"
cmp "$normal" "$receipt"
sha256sum "$script" "$receipt" "$normal"

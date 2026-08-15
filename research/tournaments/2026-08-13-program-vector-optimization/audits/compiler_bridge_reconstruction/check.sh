#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bridge_normal="$(mktemp)"
bridge_optimized="$(mktemp)"
constant_normal="$(mktemp)"
constant_optimized="$(mktemp)"
trap 'rm -f "$bridge_normal" "$bridge_optimized" "$constant_normal" "$constant_optimized"' EXIT

cd "$lane_dir"

python3 check_compiler_bridge.py --out "$bridge_normal"
python3 -O check_compiler_bridge.py --out "$bridge_optimized"
cmp "$bridge_normal" "$bridge_optimized"
cmp "$bridge_normal" receipt.json

python3 check_constant_15.py --out "$constant_normal"
python3 -O check_constant_15.py --out "$constant_optimized"
cmp "$constant_normal" "$constant_optimized"
cmp "$constant_normal" receipt_constant_15.json

python3 -m py_compile \
  compiler_bridge_model.py \
  check_compiler_bridge.py \
  check_constant_15.py

echo "compiler bridge reconstruction and constant-15 sharpening: PASS"

#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bridge_normal="$(mktemp)"
bridge_optimized="$(mktemp)"
constant_normal="$(mktemp)"
constant_optimized="$(mktemp)"
adaptive_normal="$(mktemp)"
adaptive_optimized="$(mktemp)"
hierarchical_normal="$(mktemp)"
hierarchical_optimized="$(mktemp)"
recursive_normal="$(mktemp)"
recursive_optimized="$(mktemp)"
trap 'rm -f "$bridge_normal" "$bridge_optimized" "$constant_normal" "$constant_optimized" "$adaptive_normal" "$adaptive_optimized" "$hierarchical_normal" "$hierarchical_optimized" "$recursive_normal" "$recursive_optimized"' EXIT

cd "$lane_dir"

python3 check_compiler_bridge.py --out "$bridge_normal"
python3 -O check_compiler_bridge.py --out "$bridge_optimized"
cmp "$bridge_normal" "$bridge_optimized"
cmp "$bridge_normal" receipt.json

python3 check_constant_15.py --out "$constant_normal"
python3 -O check_constant_15.py --out "$constant_optimized"
cmp "$constant_normal" "$constant_optimized"
cmp "$constant_normal" receipt_constant_15.json

python3 check_adaptive_113_8.py --out "$adaptive_normal"
python3 -O check_adaptive_113_8.py --out "$adaptive_optimized"
cmp "$adaptive_normal" "$adaptive_optimized"
cmp "$adaptive_normal" receipt_adaptive_113_8.json

python3 check_hierarchical_49_5.py --out "$hierarchical_normal"
python3 -O check_hierarchical_49_5.py --out "$hierarchical_optimized"
cmp "$hierarchical_normal" "$hierarchical_optimized"
cmp "$hierarchical_normal" receipt_hierarchical_49_5.json

python3 check_recursive_local_19_2.py --out "$recursive_normal"
python3 -O check_recursive_local_19_2.py --out "$recursive_optimized"
cmp "$recursive_normal" "$recursive_optimized"
cmp "$recursive_normal" receipt_recursive_local_19_2.json

python3 -m py_compile \
  compiler_bridge_model.py \
  hierarchical_compiler_model.py \
  recursive_local_compiler_model.py \
  check_compiler_bridge.py \
  check_constant_15.py \
  check_adaptive_113_8.py \
  check_hierarchical_49_5.py \
  check_recursive_local_19_2.py

echo "compiler bridge and all integrated sharpenings: PASS"

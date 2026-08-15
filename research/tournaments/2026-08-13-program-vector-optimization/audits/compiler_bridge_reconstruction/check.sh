#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
normal="$(mktemp)"
optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized"' EXIT

cd "$lane_dir"
python3 check_compiler_bridge.py --out "$normal"
python3 -O check_compiler_bridge.py --out "$optimized"
cmp "$normal" "$optimized"
cmp "$normal" receipt.json

python3 -m py_compile compiler_bridge_model.py check_compiler_bridge.py

echo "compiler bridge reconstruction: PASS"

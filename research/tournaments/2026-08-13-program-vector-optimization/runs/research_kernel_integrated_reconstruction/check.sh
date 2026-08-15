#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
normal="$(mktemp)"
optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized"' EXIT

cd "$here"
python3 validate.py --out "$normal"
python3 -O validate.py --out "$optimized"
cmp "$normal" "$optimized"
cmp "$normal" receipt.json
python3 -m py_compile validate.py

echo "research-kernel reconstruction evidence: PASS"

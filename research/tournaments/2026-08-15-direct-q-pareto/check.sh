#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
normal="$(mktemp)"
optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized"' EXIT

cd "$here"
python3 check_direct_q_pareto.py --out "$normal"
python3 -O check_direct_q_pareto.py --out "$optimized"
cmp "$normal" "$optimized"
cmp "$normal" receipt.json
python3 -m py_compile direct_q_pareto_model.py check_direct_q_pareto.py

echo "direct-Q Pareto compiler: PASS"

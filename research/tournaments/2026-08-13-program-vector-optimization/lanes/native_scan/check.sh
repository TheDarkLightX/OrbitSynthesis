#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "$0")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"

cd "$repo_dir"
lake env lean -EwarningAsError \
  research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/OptimalRailSemantics.lean

if rg -n '(^|[^A-Za-z])(sorry|admit|axiom)([^A-Za-z]|$)|set_option[[:space:]]+warningAsError[[:space:]]+false' \
  research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/OptimalRailSemantics.lean
then
  echo "placeholder or trust override found" >&2
  exit 1
fi

python3 research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/check_optimal_scan.py \
  --max-width 6 --out "$lane_dir/receipts/receipt.json"
python3 -O research/tournaments/2026-08-13-program-vector-optimization/lanes/native_scan/check_optimal_scan.py \
  --max-width 6 --out "$lane_dir/receipts/receipt_optimized.json"
cmp -s "$lane_dir/receipts/receipt.json" "$lane_dir/receipts/receipt_optimized.json"

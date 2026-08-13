#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"
router_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean"
vector_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean"
cost_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean"
semantics_source="$lane_dir/OrderPairSemantics.lean"
ledger_source="$lane_dir/OrderPairLedger.lean"
expected_router_hash="687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a"
expected_vector_hash="c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd"
expected_cost_hash="ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2"

read -r router_hash _ < <(sha256sum "$router_source")
read -r vector_hash _ < <(sha256sum "$vector_source")
read -r cost_hash _ < <(sha256sum "$cost_source")
[[ "$router_hash" == "$expected_router_hash" ]] || {
  echo "frozen router source hash mismatch" >&2; exit 1;
}
[[ "$vector_hash" == "$expected_vector_hash" ]] || {
  echo "frozen program-vector source hash mismatch" >&2; exit 1;
}
[[ "$cost_hash" == "$expected_cost_hash" ]] || {
  echo "frozen cost source hash mismatch" >&2; exit 1;
}

cd "$repo_dir"
lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/StrongSignedRouter.olean" "$router_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVector.olean" "$vector_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVectorCost.olean" "$cost_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/OrderPairSemantics.olean" "$semantics_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/OrderPairLedger.olean" "$ledger_source"

python3 - "$semantics_source" "$ledger_source" <<'PY'
import re
import sys
for filename in sys.argv[1:]:
    text = open(filename, encoding="utf-8").read()
    text = re.sub(r"/-.*?-/", "", text, flags=re.S)
    text = re.sub(r"--.*", "", text)
    hit = re.search(r"\b(sorry|admit|axiom)\b", text)
    if hit:
        raise SystemExit(f"proof placeholder in {filename}: {hit.group(0)}")
PY

cd "$lane_dir"
python3 audit_order_pair_program_vector.py \
  --expected-receipt receipt.json > normal.out
python3 -O audit_order_pair_program_vector.py \
  --expected-receipt receipt.json > optimized.out
cmp normal.out optimized.out
sha256sum normal.out receipt.json
rm -f normal.out optimized.out

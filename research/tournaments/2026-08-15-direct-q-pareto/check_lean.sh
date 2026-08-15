#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
router_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean"
vector_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean"
cost_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean"
direct_source="$lane_dir/DirectQMux.lean"

expected_router_hash="687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a"
expected_vector_hash="c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd"
expected_cost_hash="ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2"

read -r router_hash _ < <(sha256sum "$router_source")
read -r vector_hash _ < <(sha256sum "$vector_source")
read -r cost_hash _ < <(sha256sum "$cost_source")
[[ "$router_hash" == "$expected_router_hash" ]] || { echo "router hash mismatch" >&2; exit 1; }
[[ "$vector_hash" == "$expected_vector_hash" ]] || { echo "vector hash mismatch" >&2; exit 1; }
[[ "$cost_hash" == "$expected_cost_hash" ]] || { echo "cost hash mismatch" >&2; exit 1; }

cd "$repo_dir"
lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/StrongSignedRouter.olean" "$router_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVector.olean" "$vector_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVectorCost.olean" "$cost_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/DirectQMux.olean" "$direct_source"

if grep -nE '\b(sorry|admit|axiom)\b' "$direct_source"; then
  echo "proof placeholder or axiom detected" >&2
  exit 1
fi

echo "direct-Q mux Lean semantics: PASS"

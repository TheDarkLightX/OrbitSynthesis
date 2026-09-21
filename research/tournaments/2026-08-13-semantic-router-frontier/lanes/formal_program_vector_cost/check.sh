#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"
router_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean"
vector_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean"
target_source="$lane_dir/ProgramVectorCost.lean"
expected_router_hash="687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a"
expected_vector_hash="c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd"

read -r router_hash _ < <(sha256sum "$router_source")
read -r vector_hash _ < <(sha256sum "$vector_source")
if [[ "$router_hash" != "$expected_router_hash" ]]; then
  echo "frozen router source hash mismatch" >&2
  exit 1
fi
if [[ "$vector_hash" != "$expected_vector_hash" ]]; then
  echo "frozen program-vector source hash mismatch" >&2
  exit 1
fi

cd "$repo_dir"
lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/StrongSignedRouter.olean" "$router_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVector.olean" "$vector_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVectorCost.olean" "$target_source"
python3 /home/trevormoc/.codex/skills/proof-engineering/scripts/scan_proof_placeholders.py \
  --flag-axiom "$target_source"

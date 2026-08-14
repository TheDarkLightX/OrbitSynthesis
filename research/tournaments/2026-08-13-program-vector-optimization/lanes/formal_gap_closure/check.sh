#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"
router_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean"
vector_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean"
cost_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean"
direct_source="$repo_dir/research/tournaments/2026-08-13-program-vector-optimization/lanes/formal_optimized/DirectRail.lean"
sibling_source="$repo_dir/research/tournaments/2026-08-13-program-vector-optimization/lanes/formal_optimized/SiblingShared.lean"
target_source="$lane_dir/DepthAndCensus.lean"
axiom_source="$lane_dir/AxiomAudit.lean"

check_hash() {
  local path="$1"
  local expected="$2"
  local observed
  read -r observed _ < <(sha256sum "$path")
  if [[ "$observed" != "$expected" ]]; then
    echo "frozen source hash mismatch: $path" >&2
    echo "expected: $expected" >&2
    echo "observed: $observed" >&2
    exit 1
  fi
}

check_hash "$router_source" "687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a"
check_hash "$vector_source" "c2f477edd110c4df96f3c30f31f02de09af93045720babfd38dd2dd79a5573dd"
check_hash "$cost_source" "ea516b085cdedd3f0ee70f83a9d0240df55e7e68cf0ad8ce77558efd91db55d2"
check_hash "$direct_source" "57963dadfb40cef30d94f630126f3179c55e98bea68e5974daa8e91913c404bd"
check_hash "$sibling_source" "8eb02a3e2e5a4f7531d740b704422d09724376821f83b921aec98b77a0277e77"

cd "$repo_dir"
lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/StrongSignedRouter.olean" "$router_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVector.olean" "$vector_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVectorCost.olean" "$cost_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/DirectRail.olean" "$direct_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/SiblingShared.olean" "$sibling_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/DepthAndCensus.olean" "$target_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 "$axiom_source"
python3 /home/trevormoc/.codex/skills/proof-engineering/scripts/scan_proof_placeholders.py \
  --flag-axiom "$target_source" "$axiom_source"

#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"
router_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean"
vector_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector/ProgramVector.lean"
cost_source="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal_program_vector_cost/ProgramVectorCost.lean"
state_source="$repo_dir/research/tournaments/2026-08-13-program-vector-optimization/STATE.md"
lower_report="$repo_dir/research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/REPORT.md"
lower_checker="$repo_dir/research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/check_lower_bound.py"
lower_receipt="$repo_dir/research/tournaments/2026-08-13-program-vector-optimization/lanes/lower_bound/receipt.json"
target_source="$lane_dir/DirectRail.lean"
sibling_source="$lane_dir/SiblingShared.lean"
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
check_hash "$state_source" "6f69bf83588e2b799aec60d0df900bd749b69b4e269bdce2f29ffe6461210cf6"
check_hash "$lower_report" "be6288a6eac7f2a34012eff9e3283bf1d99929fb34460050bd17d67f9d293751"
check_hash "$lower_checker" "3b02d4cd842e7b8b252a38b3cdcb4fb2fc6044cf04f72b0b0250709a6cda2785"
check_hash "$lower_receipt" "11daf965c409e41192e3be2cf81655e554a5881c60d1011b1f1e52259b93d20b"

cd "$repo_dir"
lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/StrongSignedRouter.olean" "$router_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVector.olean" "$vector_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVectorCost.olean" "$cost_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/DirectRail.olean" "$target_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/SiblingShared.olean" "$sibling_source"
LEAN_PATH="$lane_dir" lake env lean -t 0 "$axiom_source"
python3 /home/trevormoc/.codex/skills/proof-engineering/scripts/scan_proof_placeholders.py \
  --flag-axiom "$target_source" "$sibling_source" "$axiom_source"

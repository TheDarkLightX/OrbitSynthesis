#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"
frozen_file="$repo_dir/research/tournaments/2026-08-13-semantic-router-frontier/lanes/formal/StrongSignedRouter.lean"
target_file="$lane_dir/ProgramVector.lean"
expected_frozen_hash="687a77ed1f3b0bfe2a540bc670f6db942e15bddc339ccfbceffba9699766227a"

read -r frozen_hash _ < <(sha256sum "$frozen_file")
if [[ "$frozen_hash" != "$expected_frozen_hash" ]]; then
  echo "frozen source hash mismatch" >&2
  echo "expected: $expected_frozen_hash" >&2
  echo "actual:   $frozen_hash" >&2
  exit 1
fi

cd "$repo_dir"
lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/StrongSignedRouter.olean" "$frozen_file"
LEAN_PATH="$lane_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ProgramVector.olean" "$target_file"
python3 /home/trevormoc/.codex/skills/proof-engineering/scripts/scan_proof_placeholders.py \
  --flag-axiom "$target_file"

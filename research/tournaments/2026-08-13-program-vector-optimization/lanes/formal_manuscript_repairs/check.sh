#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"
dependency_dir="$repo_dir/research/tournaments/2026-08-13-program-vector-optimization/lanes/formal_optimized"

cd "$repo_dir"
env LEAN_PATH="$dependency_dir" lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/ManuscriptRepairs.olean" "$lane_dir/ManuscriptRepairs.lean"
env LEAN_PATH="$lane_dir:$dependency_dir" lake env lean -t 0 \
  "$lane_dir/AxiomAudit.lean"

if rg -n '(^|[^A-Za-z0-9_])(sorry|admit)([^A-Za-z0-9_]|$)|^[[:space:]]*(axiom|unsafe)[[:space:]]|native_decide' \
  "$lane_dir/ManuscriptRepairs.lean" "$lane_dir/AxiomAudit.lean"
then
  echo "forbidden placeholder, declaration, or native_decide found" >&2
  exit 1
fi

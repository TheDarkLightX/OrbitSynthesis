#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../../../.." && pwd)"
source_file="$lane_dir/NativeFirstMismatch.lean"

cd "$repo_dir"
lake env lean -t 0 -EwarningAsError=true \
  -o "$lane_dir/NativeFirstMismatch.olean" "$source_file"

if grep -nE '\b(sorry|admit|axiom)\b' "$source_file"; then
  echo "proof placeholder or axiom detected" >&2
  exit 1
fi

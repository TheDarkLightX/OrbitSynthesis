#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_practical_clone_pipeline.py"
primary_receipt="$lane_dir/receipt.json"
independent="$lane_dir/audits/independent/audit_practical_clone_pipeline.py"
artifacts="$(mktemp -d)"
normal="$(mktemp)"
optimized="$(mktemp)"
audit_normal="$(mktemp)"
audit_optimized="$(mktemp)"
trap 'rm -rf "$artifacts" "$normal" "$optimized" "$audit_normal" "$audit_optimized"' EXIT

cd "$repo_dir"
PYTHONPATH=src python3 "$primary" \
  --artifact-dir "$artifacts" \
  --expected "$primary_receipt" > "$normal"
PYTHONPATH=src python3 -O "$primary" \
  --artifact-dir "$artifacts" \
  --expected "$primary_receipt" > "$optimized"
cmp "$normal" "$optimized"
cmp "$normal" "$primary_receipt"

python3 "$independent" \
  --positive-model "$artifacts/positive_model.json" \
  --positive-certificate "$artifacts/positive_certificate.json" \
  --negative-model "$artifacts/negative_model.json" \
  --negative-certificate "$artifacts/negative_certificate.json" > "$audit_normal"
python3 -O "$independent" \
  --positive-model "$artifacts/positive_model.json" \
  --positive-certificate "$artifacts/positive_certificate.json" \
  --negative-model "$artifacts/negative_model.json" \
  --negative-certificate "$artifacts/negative_certificate.json" > "$audit_optimized"
cmp "$audit_normal" "$audit_optimized"
grep -q '2d7e394e5c4254d2e5dc95cbb147e87fa01feb07fee4be7051c3928966717c20' "$audit_normal"

python3 tools/orbit_synthesize.py \
  --example discriminator \
  --out "$artifacts/cli-positive.json" >/dev/null
python3 tools/orbit_synthesize.py \
  --example discriminator \
  --verify "$artifacts/cli-positive.json" >/dev/null
python3 tools/orbit_synthesize.py \
  --example coupling \
  --out "$artifacts/cli-negative.json" >/dev/null
python3 tools/orbit_synthesize.py \
  --example coupling \
  --verify "$artifacts/cli-negative.json" >/dev/null

sha256sum \
  "$primary" "$primary_receipt" "$normal" \
  "$independent" "$audit_normal"

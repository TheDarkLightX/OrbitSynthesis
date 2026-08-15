#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_proof_bundles.py"
binding="$lane_dir/check_bundle_binding.py"
independent="$lane_dir/audits/independent/audit_bundle_examples_independent.py"
validator="$lane_dir/validate_bundle_receipts.py"
cli="$repo_dir/tools/orbit_synthesize.py"
normal_dir="$(mktemp -d)"
optimized_dir="$(mktemp -d)"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
binding_normal="$(mktemp)"
binding_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
canonical_problem="$(mktemp)"
cli_bundle="$(mktemp)"
cli_generate="$(mktemp)"
cli_verify="$(mktemp)"
trap 'rm -rf "$normal_dir" "$optimized_dir"; rm -f "$primary_normal" "$primary_optimized" "$binding_normal" "$binding_optimized" "$independent_normal" "$independent_optimized" "$canonical_problem" "$cli_bundle" "$cli_generate" "$cli_verify"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/problem_io.py \
  src/orbitsynthesis/proof_bundle.py \
  src/orbitsynthesis/proof_bundle_io.py \
  src/orbitsynthesis/state_optimality_certificate.py \
  "$primary" "$binding" "$independent" "$validator" "$cli"
python3 -m json.tool schemas/finite_safety_problem_v1.schema.json > /dev/null
python3 -m json.tool schemas/proof_bundle_v1.schema.json > /dev/null
python3 -m json.tool examples/proof_bundle/discriminator_policy.json > /dev/null
python3 -m json.tool examples/proof_bundle/coupled_required_infeasible.json > /dev/null

PYTHONPATH=src python3 "$primary" \
  --require-highs \
  --out-dir "$normal_dir" > "$primary_normal"
PYTHONPATH=src python3 -O "$primary" \
  --require-highs \
  --out-dir "$optimized_dir" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"
cmp "$normal_dir/optimal.bundle.json" "$optimized_dir/optimal.bundle.json"
cmp "$normal_dir/infeasible.bundle.json" "$optimized_dir/infeasible.bundle.json"

PYTHONPATH=src python3 "$binding" > "$binding_normal"
PYTHONPATH=src python3 -O "$binding" > "$binding_optimized"
cmp "$binding_normal" "$binding_optimized"

python3 "$independent" \
  "$normal_dir/optimal.bundle.json" \
  "$normal_dir/infeasible.bundle.json" > "$independent_normal"
python3 -O "$independent" \
  "$normal_dir/optimal.bundle.json" \
  "$normal_dir/infeasible.bundle.json" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"
python3 "$validator" "$primary_normal" "$independent_normal"

PYTHONPATH=src python3 "$cli" canonicalize \
  --input examples/proof_bundle/discriminator_policy.json \
  --out "$canonical_problem" > /dev/null
PYTHONPATH=src python3 "$cli" synthesize \
  --input "$canonical_problem" \
  --out "$cli_bundle" \
  --backend native > "$cli_generate"
PYTHONPATH=src python3 "$cli" verify \
  --input "$cli_bundle" > "$cli_verify"
python3 -c 'import json,sys; a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); assert a==b and a["verified"] is True' "$cli_generate" "$cli_verify"

sha256sum \
  src/orbitsynthesis/problem_io.py \
  src/orbitsynthesis/proof_bundle.py \
  src/orbitsynthesis/proof_bundle_io.py \
  tools/orbit_synthesize.py \
  "$primary" "$primary_normal" \
  "$binding" "$binding_normal" \
  "$independent" "$independent_normal" \
  "$normal_dir/optimal.bundle.json" \
  "$normal_dir/infeasible.bundle.json"

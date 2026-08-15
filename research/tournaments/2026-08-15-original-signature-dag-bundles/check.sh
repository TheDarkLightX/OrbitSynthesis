#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_original_signature_dag.py"
envelope="$lane_dir/check_artifact_envelope.py"
independent="$lane_dir/audits/independent/audit_executable_bundle_independent.py"
validator="$lane_dir/validate_receipts.py"
cli="$repo_dir/tools/orbit_synthesize.py"
normal_dir="$(mktemp -d)"
optimized_dir="$(mktemp -d)"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
envelope_normal="$(mktemp)"
envelope_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
cli_bundle="$(mktemp)"
cli_generate="$(mktemp)"
cli_verify="$(mktemp)"
trap 'rm -rf "$normal_dir" "$optimized_dir"; rm -f "$primary_normal" "$primary_optimized" "$envelope_normal" "$envelope_optimized" "$independent_normal" "$independent_optimized" "$cli_bundle" "$cli_generate" "$cli_verify"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/original_signature_dag.py \
  src/orbitsynthesis/executable_bundle.py \
  src/orbitsynthesis/proof_bundle.py \
  src/orbitsynthesis/proof_bundle_io.py \
  "$primary" "$envelope" "$independent" "$validator" "$cli"

python3 -m json.tool schemas/controller_dag_artifact_v1.schema.json > /dev/null
python3 -m json.tool schemas/executable_proof_bundle_v1.schema.json > /dev/null

PYTHONPATH=src python3 "$primary" \
  --require-highs \
  --out-dir "$normal_dir" > "$primary_normal"
PYTHONPATH=src python3 -O "$primary" \
  --require-highs \
  --out-dir "$optimized_dir" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"
cmp "$normal_dir/optimal.executable.json" "$optimized_dir/optimal.executable.json"
cmp "$normal_dir/infeasible.executable.json" "$optimized_dir/infeasible.executable.json"

PYTHONPATH=src python3 "$envelope" > "$envelope_normal"
PYTHONPATH=src python3 -O "$envelope" > "$envelope_optimized"
cmp "$envelope_normal" "$envelope_optimized"

python3 "$independent" \
  "$normal_dir/optimal.executable.json" \
  "$normal_dir/infeasible.executable.json" > "$independent_normal"
python3 -O "$independent" \
  "$normal_dir/optimal.executable.json" \
  "$normal_dir/infeasible.executable.json" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"
python3 "$validator" "$primary_normal" "$independent_normal"

PYTHONPATH=src python3 "$cli" synthesize-executable \
  --input examples/proof_bundle/discriminator_policy.json \
  --out "$cli_bundle" \
  --backend native \
  --dag-policy required \
  --dag-max-depth 1 > "$cli_generate"
PYTHONPATH=src python3 "$cli" verify-executable \
  --input "$cli_bundle" > "$cli_verify"
python3 -c 'import json,sys; a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); assert a==b and a["verified"] is True and a["controller_dag_status"]=="compiled" and a["controller_dag_nodes"]==1' "$cli_generate" "$cli_verify"

sha256sum \
  src/orbitsynthesis/original_signature_dag.py \
  src/orbitsynthesis/executable_bundle.py \
  tools/orbit_synthesize.py \
  "$primary" "$primary_normal" \
  "$envelope" "$envelope_normal" \
  "$independent" "$independent_normal" \
  "$normal_dir/optimal.executable.json" \
  "$normal_dir/infeasible.executable.json" \
  "$cli_bundle"

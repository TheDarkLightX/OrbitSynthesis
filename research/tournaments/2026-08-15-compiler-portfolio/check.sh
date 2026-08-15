#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_compiler_portfolio.py"
selection="$lane_dir/check_portfolio_selection.py"
scale="$lane_dir/check_portfolio_scale_guards.py"
independent="$lane_dir/audits/independent/audit_portfolio_bundles.py"
validator="$lane_dir/validate_receipts.py"
cli="$repo_dir/tools/orbit_synthesize.py"
normal_dir="$(mktemp -d)"
optimized_dir="$(mktemp -d)"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
selection_normal="$(mktemp)"
selection_optimized="$(mktemp)"
scale_normal="$(mktemp)"
scale_optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
cli_bundle="$(mktemp)"
cli_generate="$(mktemp)"
cli_verify="$(mktemp)"
trap 'rm -rf "$normal_dir" "$optimized_dir"; rm -f "$primary_normal" "$primary_optimized" "$selection_normal" "$selection_optimized" "$scale_normal" "$scale_optimized" "$independent_normal" "$independent_optimized" "$cli_bundle" "$cli_generate" "$cli_verify"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/decision_diagram.py \
  src/orbitsynthesis/decision_diagram_runtime.py \
  src/orbitsynthesis/fixed_q_structural.py \
  src/orbitsynthesis/compiler_portfolio.py \
  src/orbitsynthesis/compiler_portfolio_runtime.py \
  src/orbitsynthesis/compiler_portfolio_policy.py \
  src/orbitsynthesis/portfolio_bundle.py \
  src/orbitsynthesis/portfolio.py \
  "$primary" "$selection" "$scale" "$independent" "$validator" "$cli"

python3 -m json.tool schemas/mdd_artifact_v1.schema.json > /dev/null
python3 -m json.tool schemas/compiler_portfolio_v1.schema.json > /dev/null
python3 -m json.tool schemas/portfolio_proof_bundle_v1.schema.json > /dev/null

PYTHONPATH=src python3 "$primary" --out-dir "$normal_dir" > "$primary_normal"
PYTHONPATH=src python3 -O "$primary" --out-dir "$optimized_dir" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"
for name in default structural mdd infeasible; do
  cmp "$normal_dir/$name.portfolio.json" "$optimized_dir/$name.portfolio.json"
done

PYTHONPATH=src python3 "$selection" > "$selection_normal"
PYTHONPATH=src python3 -O "$selection" > "$selection_optimized"
cmp "$selection_normal" "$selection_optimized"

PYTHONPATH=src python3 "$scale" > "$scale_normal"
PYTHONPATH=src python3 -O "$scale" > "$scale_optimized"
cmp "$scale_normal" "$scale_optimized"

python3 "$independent" \
  "$normal_dir/default.portfolio.json" \
  "$normal_dir/structural.portfolio.json" \
  "$normal_dir/mdd.portfolio.json" \
  "$normal_dir/infeasible.portfolio.json" > "$independent_normal"
python3 -O "$independent" \
  "$normal_dir/default.portfolio.json" \
  "$normal_dir/structural.portfolio.json" \
  "$normal_dir/mdd.portfolio.json" \
  "$normal_dir/infeasible.portfolio.json" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"
python3 "$validator" "$primary_normal" "$independent_normal"

PYTHONPATH=src python3 "$cli" synthesize-portfolio \
  --input examples/proof_bundle/discriminator_policy.json \
  --out "$cli_bundle" \
  --backend native \
  --portfolio-policy practical > "$cli_generate"
PYTHONPATH=src python3 "$cli" verify-portfolio \
  --input "$cli_bundle" > "$cli_verify"
python3 -c 'import json,sys; a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); assert a==b and a["verified"] is True and a["selected_backend"]=="exact-semantic-closure"' "$cli_generate" "$cli_verify"

sha256sum \
  src/orbitsynthesis/decision_diagram.py \
  src/orbitsynthesis/decision_diagram_runtime.py \
  src/orbitsynthesis/fixed_q_structural.py \
  src/orbitsynthesis/compiler_portfolio.py \
  src/orbitsynthesis/compiler_portfolio_runtime.py \
  src/orbitsynthesis/compiler_portfolio_policy.py \
  src/orbitsynthesis/portfolio_bundle.py \
  src/orbitsynthesis/portfolio.py \
  tools/orbit_synthesize.py \
  "$primary" "$primary_normal" \
  "$selection" "$selection_normal" \
  "$scale" "$scale_normal" \
  "$independent" "$independent_normal" \
  "$normal_dir/default.portfolio.json" \
  "$normal_dir/structural.portfolio.json" \
  "$normal_dir/mdd.portfolio.json" \
  "$normal_dir/infeasible.portfolio.json" \
  "$cli_bundle"

#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
primary="$lane_dir/check_weighted_optimizer.py"
independent="$lane_dir/audits/independent/audit_weighted_optimizer_independent.py"
independent_receipt="$lane_dir/audits/independent/receipt.json"
normal="$(mktemp)"
optimized="$(mktemp)"
independent_normal="$(mktemp)"
independent_optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized" "$independent_normal" "$independent_optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile \
  src/orbitsynthesis/domain_model.py \
  src/orbitsynthesis/domain_optimization.py \
  "$primary" \
  "$independent"

PYTHONPATH=src python3 "$primary" > "$normal"
PYTHONPATH=src python3 -O "$primary" > "$optimized"
cmp "$normal" "$optimized"

python3 "$independent" > "$independent_normal"
python3 -O "$independent" > "$independent_optimized"
cmp "$independent_normal" "$independent_optimized"
cmp "$independent_normal" "$independent_receipt"

python3 - "$normal" "$independent_normal" <<'PY'
import json
import sys

EXPECTED_CORPUS_SHA256 = (
    "ab589ba21f07278b82308c9a79dbc90b6846b882345764efb66df72c7e3e4346"
)
EXPECTED_INDEPENDENT_SEMANTIC = (
    "1893ead79ed69ff556dde90596d453df5bf3314677b6992f3b59d3dfd6d61aba"
)
primary = json.load(open(sys.argv[1], encoding="utf-8"))
independent = json.load(open(sys.argv[2], encoding="utf-8"))
p = primary["unary_corpus"]
i = independent["unary_corpus"]
assert p["relations"] == i["relations"] == 512
assert p["scenarios"] == i["scenarios"] == 6
assert p["instances"] == i["instances"] == 3072
assert p["feasible_instances"] == i["feasible_instances"] == 2880
assert p["infeasible_instances"] == i["infeasible_instances"] == 192
assert p["verified_instances"] == 2880
assert p["domain_model_masks"] == 4096
assert p["wcnf_instances"] == 3072
assert p["corpus_sha256"] == i["corpus_sha256"] == EXPECTED_CORPUS_SHA256
assert independent["semantic_sha256"] == EXPECTED_INDEPENDENT_SEMANTIC
assert primary["preference"]["action_preference_score"] == 13
assert independent["preference"]["score"] == 13
assert primary["nine_state_pruning"]["search_nodes"] < 512
assert len(primary["input_validation"]["rejected"]) == 3
print(json.dumps({
    "status": "PASS",
    "corpus_sha256": p["corpus_sha256"],
    "domain_model_masks": p["domain_model_masks"],
    "feasible_instances": p["feasible_instances"],
    "infeasible_instances": p["infeasible_instances"],
    "primary_semantic_sha256": primary["semantic_sha256"],
    "independent_semantic_sha256": independent["semantic_sha256"],
    "unary_instances": p["instances"],
    "wcnf_instances": p["wcnf_instances"],
    "nine_state_search_nodes": primary["nine_state_pruning"]["search_nodes"],
}, indent=2, sort_keys=True))
PY

sha256sum \
  src/orbitsynthesis/domain_model.py \
  src/orbitsynthesis/domain_optimization.py \
  "$primary" "$normal" \
  "$independent" "$independent_receipt" "$independent_normal"

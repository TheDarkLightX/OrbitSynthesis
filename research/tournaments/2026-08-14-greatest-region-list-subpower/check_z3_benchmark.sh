#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$lane_dir/../../.." && pwd)"
benchmark="$lane_dir/benchmark_z3_learning.py"
normal="$(mktemp)"
optimized="$(mktemp)"
trap 'rm -f "$normal" "$optimized"' EXIT

cd "$repo_dir"
python3 -m py_compile "$benchmark"
python3 "$benchmark" --repeats 1 --semantic-only > "$normal"
python3 -O "$benchmark" --repeats 1 --semantic-only > "$optimized"
cmp "$normal" "$optimized"

python3 - "$normal" <<'PY'
import json
import sys

receipt = json.load(open(sys.argv[1], encoding="utf-8"))
assert receipt["semantic_sha256"] == (
    "fa0020acc50e1a8afba3e3cf375d063206e11ebcefe7ef7b1b5fbc50083c1a80"
)
semantic = receipt["semantic"]
assert semantic["random"]["instances"] == 24
assert semantic["random"]["eager_variables_sum"] == 1067
assert semantic["random"]["lazy_variables_sum"] == 216
assert semantic["principal"]["eager_variables"] == 17255
assert semantic["principal"]["eager_hard_clauses"] == 17405
assert semantic["principal"]["lazy_variables"] == 81
assert semantic["principal"]["lazy_learned_clauses"] == 3
assert semantic["principal"]["objective"] == 78
assert all(semantic["checks"].values())
PY

sha256sum "$benchmark" "$normal"

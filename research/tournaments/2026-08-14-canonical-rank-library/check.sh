#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
primary="$lane_dir/check_canonical_rank_library.py"
primary_receipt="$lane_dir/receipt.json"
audit_dir="$lane_dir/audits/independent"
audit="$audit_dir/audit_canonical_rank_independent.py"
audit_receipt="$audit_dir/receipt.json"
primary_normal="$(mktemp)"
primary_optimized="$(mktemp)"
audit_normal="$(mktemp)"
audit_optimized="$(mktemp)"
trap 'rm -f "$primary_normal" "$primary_optimized" "$audit_normal" "$audit_optimized"' EXIT

python3 "$primary" > "$primary_normal"
python3 -O "$primary" > "$primary_optimized"
cmp "$primary_normal" "$primary_optimized"

python3 "$audit" > "$audit_normal"
python3 -O "$audit" > "$audit_optimized"
cmp "$audit_normal" "$audit_optimized"

python3 - \
  "$primary" "$primary_receipt" "$primary_normal" \
  "$audit" "$audit_receipt" "$audit_normal" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

for index in (0, 3):
    script = Path(sys.argv[index + 1])
    receipt_path = Path(sys.argv[index + 2])
    output_path = Path(sys.argv[index + 3])
    receipt = json.loads(receipt_path.read_text())
    output_bytes = output_path.read_bytes()
    output = json.loads(output_bytes)
    assert hashlib.sha256(script.read_bytes()).hexdigest() == receipt["checker_sha256"]
    assert hashlib.sha256(output_bytes).hexdigest() == receipt["stdout_sha256"]
    assert output["semantic_sha256"] == receipt["semantic_sha256"]
    assert receipt["status"] == "PASS"
PY

sha256sum \
  "$primary" "$primary_receipt" "$primary_normal" \
  "$audit" "$audit_receipt" "$audit_normal"

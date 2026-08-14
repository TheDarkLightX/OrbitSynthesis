#!/usr/bin/env bash
set -euo pipefail

lane_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
primary="$lane_dir/check_asymptotic_constant.py"
primary_receipt="$lane_dir/receipt.json"
audit_dir="$lane_dir/audits/independent"
audit="$audit_dir/audit_asymptotic_constant_independent.py"
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
  "$primary_receipt" "$primary_normal" \
  "$audit_receipt" "$audit_normal" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

for index in (0, 2):
    receipt = json.loads(Path(sys.argv[index + 1]).read_text())
    output_bytes = Path(sys.argv[index + 2]).read_bytes()
    output = json.loads(output_bytes)
    assert receipt["status"] == "PASS"
    assert hashlib.sha256(output_bytes).hexdigest() == receipt["stdout_sha256"]
    assert output["semantic_sha256"] == receipt["semantic_sha256"]
PY

sha256sum \
  "$primary" "$primary_receipt" "$primary_normal" \
  "$audit" "$audit_receipt" "$audit_normal"

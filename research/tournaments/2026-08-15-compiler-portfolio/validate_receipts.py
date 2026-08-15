#!/usr/bin/env python3
"""Cross-check primary and independent compiler-portfolio receipts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_receipts.py PRIMARY INDEPENDENT")
    primary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    independent = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

    assert primary["default"]["selected_backend"] == "exact-semantic-closure"
    assert primary["default"]["selected_kind"] == "original_signature"
    assert primary["default"]["original_nodes"] == 1
    assert primary["structural"]["selected_backend"] == "fixed-q-structural-router"
    assert primary["structural"]["selected_kind"] == "original_signature"
    assert primary["structural"]["original_nodes"] == 1
    assert primary["mdd"]["selected_backend"] == "reduced-vector-mdd"
    assert primary["mdd"]["selected_kind"] == "mdd"
    assert primary["mdd"]["mdd_nodes"] is not None
    assert primary["infeasible"]["status"] == "infeasible"
    assert primary["infeasible"]["selected_backend"] is None
    assert primary["nested_router"]["rows"] == 243
    assert primary["nested_router"]["nodes"] == 3
    assert primary["nested_router"]["depth"] == 3
    assert primary["mdd_compression"]["rows"] == 729
    assert primary["mdd_compression"]["nodes"] < 729
    assert primary["unsupported"]["status"] == "unsupported"
    assert all(primary["mutations"].values())

    rows = independent["rows"]
    assert [row["backend"] for row in rows[:3]] == [
        "exact-semantic-closure",
        "fixed-q-structural-router",
        "reduced-vector-mdd",
    ]
    assert rows[3]["status"] == "infeasible"
    assert independent["total_controller_rows_checked"] == 81

    result = {
        "status": "PASS",
        "primary_semantic_sha256": primary["semantic_sha256"],
        "independent_semantic_sha256": independent["semantic_sha256"],
        "nested_router_nodes": primary["nested_router"]["nodes"],
        "mdd_compression_nodes": primary["mdd_compression"]["nodes"],
        "controller_rows_independently_checked": independent[
            "total_controller_rows_checked"
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

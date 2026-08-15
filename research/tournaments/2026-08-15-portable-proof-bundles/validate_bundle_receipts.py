#!/usr/bin/env python3
"""Cross-check primary and independent portable-bundle receipts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_bundle_receipts.py PRIMARY INDEPENDENT")
    primary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    independent = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

    optimal = primary["optimal"]
    infeasible = primary["infeasible"]
    assert optimal["status"] == "optimal"
    assert optimal["domain"] == [[0], [1], [2]]
    assert optimal["signed_utility"] == 3
    assert optimal["strategy_rows"] == 27
    assert optimal["certificate"]["claim"] == "optimal"
    assert optimal["certificate"]["target_score"] == 3
    assert optimal["certificate"]["statistics"] == {
        "bound_leaves": 1,
        "branches": 0,
        "conflict_leaves": 0,
        "nodes": 1,
    }

    assert infeasible["status"] == "infeasible"
    assert infeasible["domain"] is None
    assert infeasible["signed_utility"] is None
    assert infeasible["strategy_rows"] == 0
    assert infeasible["certificate"]["claim"] == "infeasible"
    assert infeasible["certificate"]["target_score"] is None
    assert infeasible["certificate"]["statistics"] == {
        "bound_leaves": 0,
        "branches": 0,
        "conflict_leaves": 1,
        "nodes": 1,
    }

    assert primary["highs"]["available"] is True
    assert all(primary["mutations"]["optimal"].values())
    assert all(primary["mutations"]["infeasible"].values())

    assert independent["optimal"]["manifest_sha256"] == optimal["manifest_sha256"]
    assert independent["infeasible"]["manifest_sha256"] == infeasible["manifest_sha256"]
    assert independent["optimal"]["strategy_rows"] == 27
    assert independent["optimal"]["certificate_nodes"] == 1
    assert independent["infeasible"]["unary_term_tables_checked"] == 6
    assert independent["infeasible"]["candidate_domains_checked"] == 12
    assert independent["infeasible"]["certificate_nodes"] == 1

    result = {
        "status": "PASS",
        "optimal_manifest_sha256": optimal["manifest_sha256"],
        "infeasible_manifest_sha256": infeasible["manifest_sha256"],
        "primary_semantic_sha256": primary["semantic_sha256"],
        "independent_semantic_sha256": independent["semantic_sha256"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

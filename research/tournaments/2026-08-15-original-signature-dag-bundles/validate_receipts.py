#!/usr/bin/env python3
"""Cross-check primary and independent executable-DAG receipts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_receipts.py PRIMARY INDEPENDENT")
    primary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    independent = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

    optimal = primary["optimal"]
    assert optimal["status"] == "optimal"
    assert optimal["artifact_status"] == "compiled"
    assert optimal["dag_nodes"] == 1
    assert optimal["dag_depth"] == 1
    assert optimal["rows_checked"] == 27
    assert optimal["compilation_statistics"] == {
        "semantic_functions": 7,
        "combinations_tried": 9,
        "exploration_nodes": 4,
        "depth_reached": 1,
        "skipped_operations": 0,
    }

    infeasible = primary["infeasible"]
    assert infeasible["status"] == "infeasible"
    assert infeasible["artifact_status"] == "not_applicable"
    assert infeasible["dag_nodes"] is None
    assert infeasible["rows_checked"] is None

    direct = primary["direct_compiler"]
    assert direct["scalar"]["nodes"] == 1
    assert direct["scalar"]["depth"] == 1
    assert direct["scalar"]["rows"] == 27
    assert direct["shared_vector"]["nodes"] == 2
    assert direct["shared_vector"]["depth"] == 2
    assert direct["shared_vector"]["rows"] == 27
    assert direct["projection"] == {
        "nodes": 0,
        "root": {"kind": "input", "index": 1},
    }
    assert direct["unsupported"]["status"] == "unsupported"
    assert direct["unsupported"]["reason"] == "bounded_search_exhausted"
    assert all(primary["mutations"].values())

    independent_optimal = independent["optimal"]
    for key in (
        "artifact_sha256",
        "dag_sha256",
        "certificate_sha256",
        "rows",
        "nodes",
        "depth",
    ):
        expected_key = {
            "certificate_sha256": "equivalence_sha256",
            "rows": "rows_checked",
            "nodes": "dag_nodes",
            "depth": "dag_depth",
        }.get(key, key)
        assert independent_optimal[key] == optimal[expected_key]
    assert independent_optimal["operations"] == ["d"]
    assert independent["infeasible"]["artifact_status"] == "not_applicable"

    reference = independent["direct_reference"]
    assert direct["scalar"]["dag_sha256"] == reference["dag_sha256"]
    assert direct["scalar"]["certificate_sha256"] == reference["certificate_sha256"]
    assert direct["scalar"]["artifact_sha256"] == reference["artifact_sha256_depth1"]

    result = {
        "status": "PASS",
        "primary_semantic_sha256": primary["semantic_sha256"],
        "independent_semantic_sha256": independent["semantic_sha256"],
        "dag_sha256": optimal["dag_sha256"],
        "table_dag_certificate_sha256": optimal["equivalence_sha256"],
        "executable_manifest_sha256": optimal["executable_manifest_sha256"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

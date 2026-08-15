#!/usr/bin/env python3
"""Cross-check primary and independent state-search receipts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: validate_receipts.py PRIMARY INDEPENDENT")
    primary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    independent = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

    antichain = primary["antichain"]
    assert antichain["closed_form_maxima"] == 4
    assert antichain["preferred_score"] == 30
    assert antichain["certificate"]["claim"] == "optimal"
    assert antichain["certificate"]["target_score"] == 30
    assert antichain["certificate"]["statistics"]["nodes"] > 0
    assert antichain["certificate"]["statistics"]["conflict_leaves"] > 0
    assert antichain["certificate"]["statistics"]["bound_leaves"] > 0
    assert antichain["backend"]["optimality_authority"] == "state_search_certificate"
    assert antichain["backend"]["signed_utility"] == 30

    principal = primary["principal"]
    assert principal["states"] == 81
    assert principal["observations"] == 243
    assert principal["assignments_checked_by_calibration"] == 16
    assert principal["feasible_domains_checked_by_calibration"] == 8
    assert principal["optimum"]["score"] == 13
    assert principal["optimum"]["certificate"]["claim"] == "optimal"
    assert principal["optimum"]["backend_authority"] == "state_search_certificate"
    assert principal["forced_union"]["status"] == "infeasible"
    assert principal["forced_union"]["certificate"]["claim"] == "infeasible"
    assert principal["forced_union"]["backend_authority"] == "state_search_infeasibility"
    assert all(primary["mutations"].values())

    assert independent["semantic_sha256"] == (
        "d0788afe189c8db59c2b24719cc940b805ca5bafa278a2710217e4ef279e91a1"
    )
    assert independent["random"] == {
        "cases": 240,
        "certificate_nodes_max": 59,
        "certificate_nodes_total": 1182,
        "infeasible": 30,
        "optimal": 210,
        "rows_sha256": "8631689ef25e3bb7c7df396cfda15d6fdc07a34c37f508a626cb91cf91755c6d",
    }

    result = {
        "status": "PASS",
        "antichain_certificate_nodes": antichain["certificate"]["statistics"]["nodes"],
        "principal_optimum_nodes": principal["optimum"]["certificate"]["statistics"]["nodes"],
        "principal_infeasibility_nodes": principal["forced_union"]["certificate"]["statistics"]["nodes"],
        "primary_semantic_sha256": primary["semantic_sha256"],
        "independent_semantic_sha256": independent["semantic_sha256"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

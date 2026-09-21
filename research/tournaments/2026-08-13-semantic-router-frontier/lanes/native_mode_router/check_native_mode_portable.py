#!/usr/bin/env python3
"""Version-independent receipt wrapper for the native router oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from check_native_mode_router import (
    check_bounds,
    check_compiler,
    check_minimality,
    check_mutations,
    check_routers,
    check_semantics,
)


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "theorem": "native find-first mode vector and fused signed router",
        "status": (
            "independent executable oracle; paper proof separate; "
            "Lean compilation pending"
        ),
        "semantics": check_semantics(),
        "routers": check_routers(),
        "minimality": check_minimality(),
        "bounds": check_bounds(),
        "compiler": check_compiler(),
        "mutations": check_mutations(),
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(encoded).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_receipt(), sort_keys=True, indent=2) + "\n"
    if args.out is not None:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

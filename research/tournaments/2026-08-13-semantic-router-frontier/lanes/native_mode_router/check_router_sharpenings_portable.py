#!/usr/bin/env python3
"""Version-independent receipt wrapper for the sharpening checks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from check_router_sharpenings import check_compiler_constant, check_reusable_vector


def build_receipt() -> dict[str, object]:
    result: dict[str, object] = {
        "theorem": "sharpened reusable vector and conditional compiler constants",
        "status": "exact recurrences plus finite replay; analytic proof in note",
        "reusable_vector": check_reusable_vector(),
        "compiler": check_compiler_constant(),
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

#!/usr/bin/env python3
"""Validate the immutable external-referee target and its semantic receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "paper/CURRENT_EXTERNAL_REFEREE_MANIFEST.json"


def run(*args: str) -> bytes:
    completed = subprocess.run(
        list(args),
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(args)}\n"
            f"stdout:\n{completed.stdout.decode(errors='replace')}\n"
            f"stderr:\n{completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def git_bytes(commit: str, path: str) -> bytes:
    return run("git", "show", f"{commit}:{path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema") != "orbit-synthesis/external-referee-manifest/v1":
        raise AssertionError("manifest schema drift")

    review_commit = manifest["review_commit"]
    base_commit = manifest["order_pair_base_commit"]
    run("git", "cat-file", "-e", f"{review_commit}^{{commit}}")
    run("git", "cat-file", "-e", f"{base_commit}^{{commit}}")
    run("git", "merge-base", "--is-ancestor", base_commit, review_commit)
    run("git", "merge-base", "--is-ancestor", review_commit, "HEAD")

    documents = {}
    for path in manifest["authoritative_documents"]:
        content = git_bytes(review_commit, path)
        documents[path] = hashlib.sha256(content).hexdigest()

    receipts = {}
    for name, binding in manifest["semantic_receipts"].items():
        data = json.loads(git_bytes(review_commit, binding["path"]))
        if data.get("schema") != binding["schema"]:
            raise AssertionError(f"{name}: schema drift at review commit")
        if data.get("semantic_sha256") != binding["semantic_sha256"]:
            raise AssertionError(f"{name}: semantic drift at review commit")
        receipts[name] = {
            "path": binding["path"],
            "schema": binding["schema"],
            "semantic_sha256": binding["semantic_sha256"],
        }

    packet = git_bytes(review_commit, "paper/CURRENT_EXTERNAL_REFEREE_PACKET.md")
    if b"size  <(19/2)*3^r/r" not in packet:
        raise AssertionError("review packet is not the 19/2 theorem packet")
    if b"limsup_(r->infinity) N(r)r/3^r=9" not in packet:
        raise AssertionError("review packet lacks the architecture limsup boundary")

    result = {
        "schema": "orbit-synthesis/external-referee-manifest-receipt/v1",
        "status": "PASS",
        "review_commit": review_commit,
        "order_pair_base_commit": base_commit,
        "review_branch": manifest["review_branch"],
        "document_sha256": documents,
        "semantic_receipts": receipts,
        "main_claims": manifest["main_claims"],
        "deliberately_unpromoted": manifest["deliberately_unpromoted"],
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["semantic_sha256"] = hashlib.sha256(encoded).hexdigest()
    rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

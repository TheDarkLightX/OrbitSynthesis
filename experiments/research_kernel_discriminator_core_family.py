#!/usr/bin/env python3
"""Replay and record the bounded constructor campaign locally.

This writes an offline packet; it does not contact or promote Research Kernel
entries. A fresh producer replay detects stale or modified retained summaries.
It supplements the producer's exhaustive oracle, not an independent theorem.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON field')
        result[key] = value
    return result


def validate_summary(raw: bytes, fresh: str) -> dict:
    summary = json.loads(raw, object_pairs_hook=unique_object)
    expected = json.loads(fresh, object_pairs_hook=unique_object)
    # Ordinary Python equality identifies False with 0 and 6.0 with 6.
    # Compare canonical typed JSON instead and independently recompute its hash.
    need(canonical(summary) == canonical(expected), 'retained summary differs from fresh replay')
    semantic = {k: v for k, v in summary.items() if k not in {'schema', 'candidate_statuses', 'semantic_sha256'}}
    need(hashlib.sha256(canonical(semantic)).hexdigest() == summary.get('semantic_sha256'), 'semantic digest mismatch')
    need(summary.get('schema') == 'orbit-synthesis/zag-discriminator-core-family-realizability/v1', 'summary schema')
    need(type(summary.get('exact_max_carrier')) is int and summary['exact_max_carrier'] == 6, 'unselected campaign bound')
    for key in ('family_mismatch_count', 'foreign_core_mismatch_count'):
        need(type(summary.get(key)) is int and summary[key] == 0, 'constructor counterexample')
    need(summary.get('singleton_full_core_rejected') is True, 'missing singleton refutation')
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--out-root', type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    summary_path = root / 'runs/zag_discriminator_core_family/summary.json'
    paths = [summary_path, root / 'experiments/discriminator_core_family_realizability.py',
             root / 'experiments/research_kernel_discriminator_core_family.py',
             root / 'src/orbitsynthesis/discriminator_core_family.py',
             root / 'src/orbitsynthesis/discriminator_core.py',
             root / 'formal/OrbitSynthesis/CoreIntersection.lean',
             root / 'formal/OrbitSynthesis/CoreFamilyShape.lean']
    captured = {p: p.read_bytes() for p in paths}
    command = [sys.executable, str(root / 'experiments/discriminator_core_family_realizability.py'),
               '--exact-max-carrier', '6']
    replay = subprocess.run(command, cwd=root, check=True, capture_output=True, text=True, timeout=900)
    summary = validate_summary(captured[summary_path], replay.stdout)
    # Hash the captured, validated bytes. Later pathname replacement cannot
    # silently substitute a different summary into the successful report.
    artifacts = {str(p.relative_to(root)): 'sha256:' + hashlib.sha256(raw).hexdigest() for p, raw in captured.items()}
    atom = {'id': 'bounded_constructor', 'type': 'RESULT', 'status': 'CANDIDATE',
            'content': f"Fresh replay agrees on {summary['exact_family_count']} families for carriers 2 through 6; both mismatch counts are zero.",
            'parents': []}
    report = {'schema': 'research_kernel/report/v1', 'status': 'REPLAYED_LOCALLY',
              'semantic_sha256': summary['semantic_sha256'], 'artifacts': artifacts,
              'artifact_scope': 'Captured local input bytes; not immutable execution or current-file attestation.',
              'results': [atom], 'non_claims': ['No remote write or promotion.',
                  'No general theorem, novelty, controller deployment, or standalone Lean verification is inferred.']}
    args.out_root.mkdir(parents=True, exist_ok=True)
    (args.out_root / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    (args.out_root / 'atoms.jsonl').write_text(json.dumps(atom, sort_keys=True) + '\n')
    (args.out_root / 'edges.jsonl').write_text('')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()

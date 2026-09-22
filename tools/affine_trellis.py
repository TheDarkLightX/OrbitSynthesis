#!/usr/bin/env python3
"""Produce or independently verify a certificate against an original problem."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src' / 'orbitsynthesis'))
from affine_row_lists import Row
from affine_trellis import produce, problem_dict
from affine_trellis_check import canonical, read_json, verify


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='mode', required=True)
    for name in ('produce', 'verify'):
        sub = subs.add_parser(name)
        sub.add_argument('--problem', required=True, help='Caller-supplied original problem JSON')
        sub.add_argument('--certificate', required=True)
        if name == 'produce':
            sub.add_argument('--max-states', type=int, default=1 << 16)
            sub.add_argument('--max-transitions', type=int, default=1 << 22)
    sub = subs.add_parser('demo')
    sub.add_argument('--vertices', type=int, default=32)
    sub.add_argument('--directory', required=True)
    args = parser.parse_args()
    try:
        if args.mode == 'demo':
            if not 3 <= args.vertices <= 512:
                raise ValueError('demo vertices must be between 3 and 512')
            n = args.vertices
            rows = [Row((1 << i) ^ (1 << ((i+1) % n)), (1,2,3)) for i in range(n)]
            problem = problem_dict(n, 2, rows)
            cert = produce(n, 2, rows)
            summary = verify(problem, cert)
            if summary['solution_count'] != 3**n + 3*((-1)**n):
                raise RuntimeError('cycle formula disagreement')
            folder = Path(args.directory)
            folder.mkdir(parents=True, exist_ok=True)
            write(folder/'problem.json', problem)
            write(folder/'certificate.json', cert)
        else:
            problem = canonical(read_json(args.problem))
            if args.mode == 'verify':
                summary = verify(problem, read_json(args.certificate))
            else:
                rows = [Row(z, tuple(ys)) for z, ys in problem['rows']]
                cert = produce(problem['n'], problem['k'], rows,
                               max_states=args.max_states, max_transitions=args.max_transitions)
                if cert['kind'] == 'unsupported':
                    print(json.dumps(cert, sort_keys=True, indent=2))
                    return 3  # No certificate file is written for a budget miss.
                summary = verify(problem, cert)
                write(args.certificate, cert)
        print(json.dumps(summary, sort_keys=True, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

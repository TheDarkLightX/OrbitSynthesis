#!/usr/bin/env python3
"""Independent finite falsification and structural calibrations; no assert gates."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src' / 'orbitsynthesis'))
from affine_row_lists import Row, solve
from affine_trellis import produce, problem_dict
from affine_trellis_check import verify


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def brute_output(n, k, c, z):
    answer = 0
    for j in range(k):
        val = 0
        for i in range(n):
            val ^= ((c >> (n*j+i)) & 1) * ((z >> i) & 1)
        answer |= val << j
    return answer


def brute_count(n, k, rows):
    return sum(all(brute_output(n,k,c,r.observation) in r.allowed for r in rows)
               for c in range(1 << (n*k)))


def checked(n, k, rows, expected, order=None):
    original = problem_dict(n,k,rows)
    cert = produce(n,k,rows,order=order)
    result = verify(original, json.loads(json.dumps(cert)))
    need(result['solution_count'] == expected, 'wrong exact count')
    need(result['status'] == ('sat' if expected else 'unsat'), 'wrong status')
    need(solve(n,k,rows).solution_count == expected, 'old quotient disagreement')
    if expected:
        need(all(brute_output(n,k,cert['witness'],r.observation) in r.allowed for r in rows),
             'independent witness failure')
    return cert


def tables():
    options = [tuple(y for y in range(4) if (s >> y) & 1) for s in range(16)]
    traces = [[brute_output(2,2,c,z) for z in range(4)] for c in range(16)]
    counts = {'instances':0,'sat':0,'unsat':0,'certified_trellises':0}
    digest = sha256()
    for lists in product(options,repeat=4):
        rows = [Row(z,lists[z]) for z in range(4)]
        expected = sum(all(t[z] in lists[z] for z in range(4)) for t in traces)
        cert = checked(2,2,rows,expected)
        counts['instances'] += 1
        counts['sat' if expected else 'unsat'] += 1
        counts['certified_trellises'] += cert['kind'] == 'trellis'
        digest.update(f'{expected}:{cert["kind"]};'.encode())
    counts['semantic_sha256'] = digest.hexdigest()
    return counts


def graphs():
    digest = sha256()
    cases = 0
    for n in range(1,6):
        pairs = list(combinations(range(n),2))
        for mask in range(1 << len(pairs)):
            edges = [edge for t,edge in enumerate(pairs) if (mask >> t) & 1]
            expected = sum(all(col[i] != col[j] for i,j in edges) for col in product(range(4),repeat=n))
            rows = [Row((1<<i) ^ (1<<j),(1,2,3)) for i,j in edges]
            cert = checked(n,2,rows,expected)
            # Reverse order must preserve exact count, not necessarily table coordinates.
            reverse = list(reversed(range(len(rows))))
            checked(n,2,rows,expected,reverse)
            digest.update(f'{n}:{mask}:{expected}:{cert["exception_dimension"]};'.encode())
            cases += 1
    return {'graphs':cases,'certificates':cases*2,'semantic_sha256':digest.hexdigest()}


def xor_hull(ys):
    if not ys:
        return set()
    origin = ys[0]
    span = {0}
    for y in ys:
        span |= {v ^ y ^ origin for v in tuple(span)}
    return {origin ^ v for v in span}


def check_cut_formula(n,k,rows,cert):
    if cert['kind'] != 'trellis':
        return
    normalized = problem_dict(n,k,rows)['rows']
    hulls = [(z,xor_hull(ys)) for z,ys in normalized]
    exceptions = [(z,ys) for z,ys in normalized if len(xor_hull(ys)) != len(ys)]
    exceptions = [exceptions[i] for i in cert['order']]
    code = set()
    for c in range(1 << (n*k)):
        if all(brute_output(n,k,c,z) in ys for z,ys in hulls):
            word = sum(brute_output(n,k,c,z) << (k*i) for i,(z,ys) in enumerate(exceptions))
            code.add(word)
    need(len(code) == 1 << cert['exception_dimension'], 'wrong image dimension')
    for i,cut in enumerate(cert['cut_ranks']):
        prefix = {word & ((1 << (k*i))-1) for word in code}
        suffix = {word >> (k*i) for word in code}
        expected_states = len(prefix)*len(suffix)//len(code)
        need(expected_states == 1 << cut, 'independent cut rank mismatch')
        # For the relaxation, residual suffix-language classes attain the bound.
        residuals = {}
        for word in code:
            pre = word & ((1 << (k*i))-1)
            residuals.setdefault(pre,set()).add(word >> (k*i))
        need(len({frozenset(s) for s in residuals.values()}) == expected_states,
             'minimal relaxation trellis mismatch')


def random_cases():
    rng = random.Random(20260922)
    digest = sha256()
    for t in range(1200):
        n,k = rng.choice([(2,3),(3,2),(4,2)])
        rows = []
        for z in rng.sample(range(1<<n),rng.randrange(min(1<<n,9)+1)):
            ys = tuple(y for y in range(1<<k) if rng.random()<0.72)
            rows.append(Row(z,ys))
        if rows and t%7 == 0:
            rows.append(rows[0])
        expected = brute_count(n,k,rows)
        cert = checked(n,k,rows,expected)
        if t<200:
            check_cut_formula(n,k,rows,cert)
        digest.update(json.dumps(cert,sort_keys=True,separators=(',',':')).encode())
    return {'instances':1200,'cut_profile_calibrations_attempted':200,'semantic_sha256':digest.hexdigest()}


def adversarial():
    rows = [Row((1<<i) ^ (1<<j),(1,2,3)) for i,j in combinations(range(4),2)]
    p = problem_dict(4,2,rows)
    base = produce(4,2,rows)
    count = 0
    def reject(cert,problem=p,**kwargs):
        nonlocal count
        try:
            verify(problem,cert,**kwargs)
        except ValueError:
            count += 1
        else:
            raise RuntimeError('forged certificate accepted')
    for key,value in [('solution_count',base['solution_count']+1),('solution_count',True),
                      ('witness',0),('witness',True),('instance_sha256','0'*64),
                      ('schema','wrong'),('kind','empty'),('kind','unsupported'),
                      ('affine_dimension',True),('affine_dimension',9),
                      ('exception_dimension',base['exception_dimension']-1),
                      ('transition_checks',base['transition_checks']+1),('peak_live_states',0),
                      ('order',[0]),('order',[True,1,2,3,4,5]),
                      ('order',list(range(6))+[0]),('cut_ranks',[0]),('tables',base['tables'][:-1])]:
        c=deepcopy(base); c[key]=value; reject(c)
    c=deepcopy(base); c['extra']=0; reject(c)
    c=deepcopy(base); c['tables'][0]=[[0,2]]; reject(c)
    for layer in range(1,len(base['tables'])):
        c=deepcopy(base); c['tables'][layer]=[]; reject(c)
        for position in range(len(base['tables'][layer])):
            c=deepcopy(base); c['tables'][layer][position][1]+=1; reject(c)
            c=deepcopy(base); c['tables'][layer].pop(position); reject(c)
            c=deepcopy(base); c['tables'][layer][position][1]=True; reject(c)
    c=deepcopy(base); c['tables'][1].append(c['tables'][1][0]); reject(c)
    c=deepcopy(base); c['tables'][1][0][0]=1<<100; reject(c)
    c=deepcopy(base); c['tables'][1][0][1]=1<<100; reject(c)
    changed=deepcopy(p); changed['rows'][0][1]=[1]; reject(base,changed)
    for kw in ({'max_cells':1},{'max_transitions':1},{'max_code_bits':1}):
        reject(base,**kw)
    for kw in ({'max_states':1},{'max_transitions':1}):
        c=produce(4,2,rows,**kw)
        need(c['kind']=='unsupported' and 'solution_count' not in c and 'witness' not in c,
             'budget miss was promoted')
        reject(c)
    for p0 in ({'n':2,'k':2,'rows':[[0,[1,2,3]]]},
               {'n':2,'k':2,'rows':[[1,[]]]},
               {'n':2,'k':2,'rows':[[0,[1]]]},
               {'n':2,'k':2,'rows':[]}):
        rs=[Row(z,tuple(ys)) for z,ys in p0['rows']]
        c=produce(p0['n'],p0['k'],rs)
        verify(p0,c)
        bad=deepcopy(c); bad['solution_count']=False; reject(bad,p0)
        if c['solution_count']==0:
            bad=deepcopy(c); bad['witness']=0; reject(bad,p0)
    return {'rejected_mutations_and_limits':count}


def cycles():
    results=[]
    for n in (3,4,8,32,128,256):
        rows=[Row((1<<i)^(1<<((i+1)%n)),(1,2,3)) for i in range(n)]
        p=problem_dict(n,2,rows)
        cert=produce(n,2,rows)
        result=verify(p,cert)
        expected=3**n+3*((-1)**n)
        need(cert['solution_count']==expected,'cycle exact-count formula')
        need(result['exception_dimension']==2*n-2 and result['max_cut_rank']==2,'cycle dimensions')
        if n>=32:
            need(solve(n,2,rows,max_image_points=1<<20).status=='unsupported','old budget calibration')
        results.append({'vertices':n,**result,'prior_image_points':str(1<<(2*n-2))})
        if n==256:
            (ROOT/'research/replays/affine-cycle256.problem.json').write_text(json.dumps(p,sort_keys=True,indent=2)+'\n')
            (ROOT/'research/replays/affine-cycle256.certificate.json').write_text(json.dumps(cert,sort_keys=True,indent=2)+'\n')
    # Fixed-domain input-free safety, not just interpolation: re-use the K4 helper gadget.
    n=4; h1,h2=1<<n,1<<(n+1)
    helpers=(h1,h2,h1^h2)
    rows=[Row(h,(h,)) for h in helpers]
    rows += [Row((1<<i)^(1<<j),helpers) for i,j in combinations(range(n),2)]
    cert=produce(n+2,n+2,rows)
    result=verify(problem_dict(n+2,n+2,rows),cert)
    need(result['solution_count']==384,'K4 sparse-safety count')
    return {'cycles':results,'k4_fixed_domain_safety':result}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',choices=['tables','graphs','random','adversarial','cycles'],required=True)
    args=parser.parse_args()
    functions={'tables':tables,'graphs':graphs,'random':random_cases,'adversarial':adversarial,'cycles':cycles}
    print(json.dumps(functions[args.suite](),sort_keys=True,indent=2))

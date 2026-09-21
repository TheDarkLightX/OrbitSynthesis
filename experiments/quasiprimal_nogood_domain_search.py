#!/usr/bin/env python3
"""Exact ZAG differential campaign for pointed-domain nogood search."""
from __future__ import annotations
import argparse, hashlib, json, random, statistics, sys, time
from itertools import product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.parameter_core import BitsetNogoodDomainSearch,CompiledNogoodDomainSearch,CompiledParameterizedKernel,parameter_core_catalog
from orbitsynthesis.safety import FiniteSafetyGame
Q=(0,1,2); DEAD=(1,0); SPECIAL={(0,0,0),(1,1,1)}
def d(x,y,z): return z if x==y else x
def u(x): return {0:1,1:0,2:1}[x]
def alg(): return FiniteAlgebra.from_callables(Q,{'d':(3,d),'u':(1,u)})
def game():
    A=alg(); S=tuple(product(Q,repeat=2)); I=tuple((x,) for x in Q)
    def safe(s,i,o): return not (s==DEAD and i==(2,)) and not (s+i in SPECIAL and o in {(0,0),(1,1)})
    return FiniteSafetyGame(A,2,1,{(s,i,o) for s in S for i in I for o in S if safe(s,i,o)})
def domains(states):
    return tuple(frozenset(states[i] for i in range(len(states)) if m>>i&1) for m in range(1<<len(states)))
def domainset(rows): return {w for w,_ in rows}
def mask(states,w): return sum(1<<i for i,s in enumerate(states) if s in w)
def run_exact(G):
    Ds=domains(G.states); rows=[]; replays=unsound=nodes=nogoods=0
    for info in parameter_core_catalog(G.algebra):
        K=CompiledParameterizedKernel(G,info.core); O=CompiledNogoodDomainSearch(K); B=BitsetNogoodDomainSearch(K)
        feasible=0
        for W in Ds:
            r=K.strategy_pointed(W) is not None; o=O.is_feasible(W); b=B.is_feasible_mask(mask(B.states,W))
            assert r==o==b; feasible+=int(r)
        ex=K.maximal_domains(search='exhaustive')
        ob=O.maximal_domains(learn_nogoods=True,use_propagation=True)
        bi=B.maximal_domains(learn_nogoods=True,learn_propagation_nogoods=True)
        assert domainset(ex)==domainset(ob.maximal_domains)==domainset(bi.maximal_domains)
        for ng in bi.nogoods:
            for W in Ds:
                if ng.covers_domain(W):
                    replays+=1; unsound+=int(K.strategy_pointed(W) is not None)
        nodes+=bi.stats.nodes; nogoods+=len(bi.nogoods)
        rows.append({'core':sorted(info.core),'feasible':feasible,'nodes':bi.stats.nodes,'nogoods':len(bi.nogoods)})
    assert [r['feasible'] for r in rows]==[128,160,253]
    assert (nodes,nogoods,replays,unsound)==(227,8,1088,0)
    return {'instances':len(Ds)*len(rows),'rows':rows,'nodes':nodes,'nogoods':nogoods,'covered_replays':replays,'unsound':unsound}
def run_random(G,n):
    rng=random.Random(1); Ds=domains(G.states); total=0
    for _ in range(n):
        R={(s,i,o) for s in G.states for i in G.inputs for o in G.states if rng.randrange(1000)<430}
        H=FiniteSafetyGame(G.algebra,2,1,R)
        for info in parameter_core_catalog(H.algebra):
            K=CompiledParameterizedKernel(H,info.core); B=BitsetNogoodDomainSearch(K)
            for W in Ds:
                assert (K.strategy_pointed(W) is not None)==B.is_feasible_mask(mask(B.states,W)); total+=1
    return {'games':n,'instances':total,'mismatches':0}
def run_scale():
    A=alg(); S=tuple(product(Q,repeat=3)); dead={(1,0,0),(1,0,1),(1,0,2)}
    G=FiniteSafetyGame(A,3,0,{(s,(),s) for s in S if s not in dead}); expected=frozenset(set(S)-dead); rows=[]
    for info in parameter_core_catalog(A):
        R=BitsetNogoodDomainSearch(CompiledParameterizedKernel(G,info.core)).maximal_domains(learn_nogoods=True,learn_propagation_nogoods=True)
        assert len(R.maximal_domains)==1 and R.maximal_domains[0][0]==expected
        strategy=dict(R.maximal_domains[0][1]); assert all((s,(),strategy[s]) in G.safe_relation and strategy[s] in expected for s in expected)
        rows.append({'core':sorted(info.core),'nodes':R.stats.nodes,'nogoods':len(R.nogoods),'domain_size':len(expected)})
    return {'states':27,'lattice_per_core':1<<27,'rows':rows,'returned_witnesses_checked':3}
def samples(fn,n):
    out=[]
    for _ in range(n): t=time.perf_counter_ns(); fn(); out.append(time.perf_counter_ns()-t)
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument('--out-root',type=Path); p.add_argument('--repeats',type=int,default=3); p.add_argument('--random-games',type=int,default=8); a=p.parse_args(); G=game()
    semantic={'schema':'orbit-synthesis/zag-pointed-domain-nogood/v2','exact':run_exact(G),'random':run_random(G,a.random_games),'scale':run_scale(),'statuses':{'exhaustive':'TESTED_ONLY','object_nogood':'TESTED_ONLY','bitset_nogood':'TESTED_ONLY'}}
    semantic['semantic_sha256']=hashlib.sha256(json.dumps(semantic,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    timing={'exhaustive_ns':samples(lambda:[CompiledParameterizedKernel(G,i.core).maximal_domains(search='exhaustive') for i in parameter_core_catalog(G.algebra)],a.repeats),'object_ns':samples(lambda:[CompiledNogoodDomainSearch(CompiledParameterizedKernel(G,i.core)).maximal_domains() for i in parameter_core_catalog(G.algebra)],a.repeats),'bitset_ns':samples(lambda:[BitsetNogoodDomainSearch(CompiledParameterizedKernel(G,i.core)).maximal_domains() for i in parameter_core_catalog(G.algebra)],a.repeats)}
    out={**semantic,'timings':timing}
    if a.repeats: out['timing_medians_ns']={k:statistics.median(v) for k,v in timing.items()}
    if a.out_root: a.out_root.mkdir(parents=True,exist_ok=True); (a.out_root/'summary.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__': main()

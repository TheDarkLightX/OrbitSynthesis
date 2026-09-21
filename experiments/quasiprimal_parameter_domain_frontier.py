#!/usr/bin/env python3
"""ZAG-style exact differential campaign for parameter-core/domain synthesis.

Candidates:
- raw_groupoid_reference: exact but overparameterized reference;
- pointed_core_seed: minimum pointed-class seed solver;
- naive_local: deliberately drops cross-observation transport and must fail.

The benchmark is the three-element Quackenbush no-greatest-region game.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, re, sys, time
from pathlib import Path
from itertools import product

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from orbitsynthesis.finite_algebra import FiniteAlgebra
from orbitsynthesis.safety import FiniteSafetyGame
from orbitsynthesis.parameter_core import (
    CompiledParameterizedKernel,
    naive_local_domain_feasible,
    parameter_budget_frontier,
    parameter_core_catalog,
    parameter_domain_frontier,
    minimum_parameter_solutions,
    maximal_domains_for_allowed_parameters,
    parameterized_strategy_for_allowed_parameters,
    parameterized_strategy_pointed,
    parameterized_strategy_reference,
)

Q=(0,1,2); Q0=frozenset({0,1}); DEAD=(1,0); SPECIAL={(0,0,0),(1,1,1)}
def d(x,y,z): return z if x==y else x
def u(x): return {0:1,1:0,2:1}[x]
def safe(a, inp, out):
    x=inp[0]
    if a==DEAD and x==2: return False
    if a+(x,) in SPECIAL and out in {(0,0),(1,1)}: return False
    return True

def build_game():
    algebra=FiniteAlgebra.from_callables(Q,{"d":(3,d),"u":(1,u)})
    states=tuple(product(Q,repeat=2)); inputs=((0,),(1,),(2,))
    relation={(a,i,v) for a in states for i in inputs for v in states if safe(a,i,v)}
    return FiniteSafetyGame(algebra,2,1,relation)

def encode_set(values, order): return [value for value in order if value in values]
def ns_samples(fn, repeats):
    out=[]
    for _ in range(repeats):
        start=time.perf_counter_ns(); fn(); out.append(time.perf_counter_ns()-start)
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('--out-root',type=Path); p.add_argument('--repeats',type=int,default=5)
    args=p.parse_args(); game=build_game(); states=game.states
    infos=parameter_core_catalog(game.algebra)
    assert [(info.core,info.rank) for info in infos] == [
        (frozenset(),0),(frozenset({0,1}),1),(frozenset(Q),1)
    ]
    all_isos=game.algebra.internal_isomorphisms()
    feasibility_counts={}; mismatches=[]; rebuild_mismatches=[]; naive_false_positives=[]
    kernels={info.core:CompiledParameterizedKernel(game,info.core,internal_isomorphisms=all_isos) for info in infos}
    for info in infos:
        feasible=0; kernel=kernels[info.core]
        for mask in range(1<<len(states)):
            W=frozenset(states[i] for i in range(len(states)) if mask&(1<<i))
            ref=kernel.strategy_reference(W)
            opt=kernel.strategy_pointed(W)
            rebuild=parameterized_strategy_pointed(
                game, info.core, W, internal_isomorphisms=all_isos
            )
            if (ref is None)!=(opt is None):
                mismatches.append((info.core,W,ref is not None,opt is not None))
            if (ref is None)!=(rebuild is None):
                rebuild_mismatches.append(
                    (info.core,W,ref is not None,rebuild is not None)
                )
            feasible += int(ref is not None)
            if kernel.local_feasible(W) and ref is None:
                naive_false_positives.append((info.core,W))
        feasibility_counts[tuple(sorted(info.core))]=feasible
    assert not mismatches and not rebuild_mismatches
    union=frozenset({(0,0),(0,1),(1,1)})
    assert naive_local_domain_feasible(game,frozenset(),union)
    assert parameterized_strategy_pointed(game,frozenset(),union,internal_isomorphisms=all_isos) is None

    # Public raw-parameter API: {0} and {1} close to the same core, while
    # {2} closes to the full carrier.
    strategy_from_zero = parameterized_strategy_for_allowed_parameters(
        game, {0}, union, internal_isomorphisms=all_isos
    )
    strategy_from_one = parameterized_strategy_for_allowed_parameters(
        game, {1}, union, internal_isomorphisms=all_isos
    )
    assert strategy_from_zero is not None and strategy_from_one is not None
    max_from_zero = maximal_domains_for_allowed_parameters(
        game, {0}, internal_isomorphisms=all_isos
    )
    assert any(domain == frozenset(set(states)-{DEAD}) for domain, _ in max_from_zero)

    front=parameter_domain_frontier(game)
    expected_big=frozenset(set(states)-{DEAD})
    nd={(point.core,point.rank,point.domain) for point in front.nondominated}
    expected_nd={
        (frozenset(),0,frozenset(set(states)-{DEAD,(1,1)})),
        (frozenset(),0,frozenset(set(states)-{DEAD,(0,0)})),
        (Q0,1,expected_big),
    }
    assert nd==expected_nd, (nd,expected_nd)
    assert any(p.core==frozenset(Q) and p.domain==expected_big for p in front.all_points)
    assert not any(p.core==frozenset(Q) for p in front.nondominated)
    budget0=parameter_budget_frontier(game,0)
    assert len(budget0.nondominated)==2 and all(p.rank==0 for p in budget0.nondominated)
    paired_initials=minimum_parameter_solutions(game,{(0,0),(1,1)})
    assert len(paired_initials)==1
    assert paired_initials[0].rank==1 and paired_initials[0].core==Q0
    assert paired_initials[0].domain==expected_big
    singleton_initial=minimum_parameter_solutions(game,{(0,0)})
    assert singleton_initial and all(p.rank==0 for p in singleton_initial)

    # Deterministic adversarial differential corpus beyond the hand-built witness.
    rng=random.Random(1); random_game_count=16; random_instances=0; random_mismatches=[]
    for game_index in range(random_game_count):
        relation={
            (a,i,v)
            for a in states for i in game.inputs for v in states
            if rng.randrange(1000) < 430
        }
        random_game=FiniteSafetyGame(game.algebra,2,1,relation)
        random_isos=random_game.algebra.internal_isomorphisms()
        for info in infos:
            kernel=CompiledParameterizedKernel(random_game,info.core,internal_isomorphisms=random_isos)
            for mask in range(1<<len(states)):
                W=frozenset(states[i] for i in range(len(states)) if mask&(1<<i))
                ref=kernel.strategy_reference(W)
                opt=kernel.strategy_pointed(W)
                random_instances += 1
                if (ref is None)!=(opt is None):
                    random_mismatches.append((game_index,info.core,W))
    assert not random_mismatches

    def run_reference():
        for info in infos:
            kernel=kernels[info.core]
            for mask in range(1<<len(states)):
                W=frozenset(states[i] for i in range(len(states)) if mask&(1<<i))
                kernel.strategy_reference(W)
    def run_rebuild_pointed():
        for info in infos:
            for mask in range(1<<len(states)):
                W=frozenset(states[i] for i in range(len(states)) if mask&(1<<i))
                parameterized_strategy_pointed(
                    game, info.core, W, internal_isomorphisms=all_isos
                )
    def run_pointed():
        for info in infos:
            kernel=kernels[info.core]
            for mask in range(1<<len(states)):
                W=frozenset(states[i] for i in range(len(states)) if mask&(1<<i))
                kernel.strategy_pointed(W)

    slow_repeats=min(args.repeats,3)
    timings={
        'raw_groupoid_reference_ns':ns_samples(run_reference,args.repeats),
        'pointed_rebuild_each_domain_ns':ns_samples(run_rebuild_pointed,slow_repeats),
        'compiled_pointed_core_seed_ns':ns_samples(run_pointed,args.repeats),
    }
    lean_path=ROOT/'formal'/'OrbitSynthesis'/'ParameterClosure.lean'
    lean_text=lean_path.read_text(encoding='utf-8') if lean_path.is_file() else ''
    forbidden_lean_tokens=[token for token in ('sorry','admit','axiom') if token in lean_text]
    lean_source_gate={
        'path':str(lean_path.relative_to(ROOT)) if lean_path.is_file() else None,
        'present':lean_path.is_file(),
        'theorem_count':len(re.findall(r'(?m)^theorem\s', lean_text)),
        'forbidden_tokens':forbidden_lean_tokens,
        'compiler_status':'BLOCKED_NO_LOCAL_LEAN_AND_GITHUB_ACTIONS_BILLING',
    }
    assert lean_source_gate['present'] and not forbidden_lean_tokens
    summary={
        'schema':'orbit-synthesis/zag-parameter-domain-frontier/v1',
        'seed':1,
        'algebra':'Quackenbush Q=({0,1,2};d,u)',
        'state_count':len(states),
        'domain_count':1<<len(states),
        'parameter_cores':[
            {'core':encode_set(i.core,Q),'rank':i.rank,'witnesses':[encode_set(w,Q) for w in i.witnesses]}
            for i in infos
        ],
        'feasibility_counts':{str(k):v for k,v in feasibility_counts.items()},
        'reference_pointed_mismatches':len(mismatches),
        'reference_rebuild_mismatches':len(rebuild_mismatches),
        'random_game_count':random_game_count,
        'random_differential_instances':random_instances,
        'random_differential_mismatches':len(random_mismatches),
        'naive_false_positive_count':len(naive_false_positives),
        'naive_minimized_false_positive':encode_set(union,states),
        'all_maximal_points':len(front.all_points),
        'minimum_rank_for_paired_initials':paired_initials[0].rank,
        'minimum_core_for_paired_initials':encode_set(paired_initials[0].core,Q),
        'nondominated_points':[
            {'core':encode_set(p.core,Q),'rank':p.rank,'domain':encode_set(p.domain,states)} for p in front.nondominated
        ],
        'lean_source_gate':lean_source_gate,
        'candidate_statuses':{
            'raw_groupoid_reference':'TESTED_ONLY',
            'pointed_rebuild_each_domain':'TESTED_ONLY',
            'compiled_pointed_core_seed':'TESTED_ONLY',
            'naive_local':'FAILED',
        },
        'timings':timings,
        'environment':{'python':sys.version,'platform':platform.platform()},
    }
    semantic_projection={key:value for key,value in summary.items() if key not in {'timings','environment'}}
    summary['semantic_sha256']=hashlib.sha256(
        json.dumps(semantic_projection,sort_keys=True,separators=(',',':')).encode()
    ).hexdigest()
    if args.out_root:
        out=args.out_root; (out/'gates').mkdir(parents=True,exist_ok=True)
        (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        manifest={
            'schema':'zag/run-manifest/v1','run_id':out.name,'seed':1,
            'candidates':['raw_groupoid_reference','pointed_rebuild_each_domain','compiled_pointed_core_seed','naive_local'],
            'commands':[
                'python experiments/quasiprimal_parameter_domain_frontier.py --out-root '+str(out)+' --repeats '+str(args.repeats),
                'python -O experiments/quasiprimal_parameter_domain_frontier.py',
            ],
            'correctness_labels':summary['candidate_statuses'],
            'proof_requirement':'No candidate labeled PROVED without a Lean theorem.',
        }
        (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
        (out/'timings.json').write_text(json.dumps({'schema':'zag/timings/v1',**timings},indent=2,sort_keys=True)+'\n')
        (out/'gates'/'exhaustive.json').write_text(json.dumps({
            'status':'PASS','instances':len(infos)*(1<<len(states)),
            'random_instances':random_instances,
            'mismatches':0,'random_mismatches':0,
            'naive_false_positives':len(naive_false_positives)
        },indent=2,sort_keys=True)+'\n')
        (out/'gates'/'proofs.json').write_text(json.dumps({
            'raw_groupoid_reference':'NO_LEAN_PROOF',
            'pointed_rebuild_each_domain':'NO_LEAN_PROOF',
            'compiled_pointed_core_seed':'NO_LEAN_PROOF',
            'closure_obstruction_layer':'LEAN_SOURCE_NO_SORRY_COMPILER_BLOCKED',
            'naive_local':'REFUTED_BY_COUNTEREXAMPLE'
        },indent=2,sort_keys=True)+'\n')
        rows=[
            {'candidate_id':'raw_groupoid_reference','status':'TESTED_ONLY','notes':'Exact independent reference; exhaustive bounded agreement.'},
            {'candidate_id':'pointed_rebuild_each_domain','status':'TESTED_ONLY','notes':'Exact minimum abstraction, but rejected as a performance generation because it recompiles classes for every domain.'},
            {'candidate_id':'compiled_pointed_core_seed','status':'TESTED_ONLY','notes':'Minimum abstraction; exhaustive bounded agreement; Lean pending.'},
            {'candidate_id':'naive_local','status':'FAILED','notes':'Accepts the minimized no-greatest union incorrectly.'},
        ]
        (out/'archive.jsonl').write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows))
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__': main()

"""Deterministic differential and falsification campaign; no network required."""
from __future__ import annotations
from copy import deepcopy
from itertools import product
import hashlib
import json
from pathlib import Path
import random
import time
from q_obstruction import QGame, Engine, cnf_game, bits, digest
from independent_check import Reference, need, sat_assignments, total_q_tables_arity2

OUT=Path(__file__).resolve().parent
rng=random.Random(20260922)
summary={"schema":"orbit-synthesis/q-frontier-replay/v1","seed":20260922}
transcript=[]


def checked(game, *, required=0, forbidden=0, weights=None, decision=False, exhaustive=True):
    ws=list(weights) if weights is not None else [1]*game.n
    request={"required":hex(required),"forbidden":hex(forbidden),"weights":ws,"decision":decision}
    result=Engine(game).solve(required=required,forbidden=forbidden,weights=ws,decision=decision)
    ref=Reference(game.wire()); ref.verify(result,request)
    if exhaustive:
        domains=[w for w in ref.all_domains(set(range(game.n))-set(bits(forbidden))) if set(bits(required))<=w]
        need(bool(domains)==(result["status"]=="feasible"),"exhaustive feasibility disagreement")
        if domains and not decision:
            key=lambda w:(sum(ws[s] for s in w),len(w),sum(1<<s for s in w))
            need(int(result["domain"],16)==sum(1<<s for s in max(domains,key=key)),"exhaustive objective disagreement")
    transcript.append([digest(game.wire()),digest(request),result["status"],result["domain"],result["score"],result["stats"]])
    return result,request


# Exhaust an explicitly scoped 2,048-game coupled kernel, not all Q games.
count=0
for binary_mask in range(16):
    for a,b in product(range(8),repeat=2):
        for rigid_live in (False,True):
            rows=[0]*9
            rows[0]=binary_mask&3; rows[1]=(binary_mask>>2)&3
            swap=lambda m:((m&1)<<1)|((m&2)>>1)
            rows[4]=swap(rows[0]); rows[3]=swap(rows[1])
            rows[2]=a; rows[5]=b
            rows[6:9]=[4 if rigid_live else 0]*3
            game=QGame(1,tuple(rows))
            checked(game)
            checked(game,required=1<<(count%3),forbidden=(1<<((count+1)%3)) if count%4==0 else 0,
                    weights=[0,3,1])
            count+=1
summary["exhaustive_kernel"]={"games":count,"optimization_requests":2*count,"possible_domains_per_game":8}


def random_game(k,active=None,symmetric=True):
    n=3**k; eng=Engine(QGame(k,(0,)*(3*n)))
    if active is None: active=set(range(n))
    p=rng.choice((0.18,0.4,0.7,0.95))
    rows=[sum(1<<t for t in active if rng.random()<p) if s in active else 0
          for s in range(n) for i in range(3)]
    if symmetric:
        for s,t in eng.pairs:
            for i in (0,1):
                rows[3*t+1-i]=(rows[3*t+1-i]&~eng.bmask)|sum(1<<eng.bar[y] for y in bits(rows[3*s+i]&eng.bmask))
    return QGame(k,tuple(rows))

random_counts={1:0,2:0,3:0}; direct_games=[]
for k,total in ((1,160),(2,300),(3,200)):
    eng=Engine(QGame(k,(0,)*(3*3**k)))
    for j in range(total):
        active=None
        if k==3:
            selected=rng.sample(list(eng.pairs),2)
            active={s for pair in selected for s in pair}
            active.update(rng.sample([s for s in range(eng.game.n) if s not in eng.bar],3))
        game=random_game(k,active,symmetric=j%2==0)
        if k==1 and j<64: direct_games.append(game)
        if j%2==0: Reference(game.wire()).single_equation_compatible()
        checked(game)
        required=1<<rng.randrange(game.n) if j%3 else 0
        forbidden=1<<rng.randrange(game.n) if j%4==0 else 0
        checked(game,required=required,forbidden=forbidden,weights=[rng.randrange(6) for _ in range(game.n)])
        random_counts[k]+=1
summary["random_differential"]={"games_by_arity":random_counts,"optimization_requests":2*sum(random_counts.values()),
                                "includes_nonsymmetric_relations":True}

# A second tiny oracle enumerates all compatible total controller tables.
tables=list(total_q_tables_arity2()); need(len(tables)==972,"binary term-table census")
for game in direct_games:
    ref=Reference(game.wire())
    for mask in range(8):
        w=set(bits(mask))
        exists=any(all(table[3*s+i] in ref.raw[3*s+i] and table[3*s+i] in w
                       for s in w for i in range(3)) for table in tables)
        need(exists==ref.feasible(w),"total-table oracle disagreement")
summary["total_table_oracle"]={"complete_Q_compatible_tables":972,"games":len(direct_games),"domain_checks":8*len(direct_games)}

# All subsets of the eight nonempty non-tautological clauses on two variables.
clause_library=[tuple((j+1)*sign for j,sign in enumerate(signs) if sign)
                for signs in product((-1,0,1),repeat=2) if any(signs)]
formula_count=sat_count=unsat_count=separator_rows=0
formulas=[]
for mask in range(1<<len(clause_library)):
    formulas.append((2,[c for j,c in enumerate(clause_library) if mask>>j&1]))
# All subsets of the eight full-width 3-variable clauses.
full3=[tuple((j+1)*s for j,s in enumerate(signs)) for signs in product((-1,1),repeat=3)]
for mask in range(256): formulas.append((3,[c for j,c in enumerate(full3) if mask>>j&1]))
# Empty clauses, tautologies, repeats, zero-variable formula, seeded mixed 3-CNFs.
formulas += [(0,[]),(0,[()]),(1,[(1,-1)]),(1,[(1,1),(-1,)]),(1,[(1,),(-1,)])]
for j in range(400):
    n=rng.randrange(1,7); m=rng.randrange(1,26)
    clauses=[]
    for _ in range(m):
        width=rng.randrange(1,min(3,n)+1)
        clauses.append(tuple(v*rng.choice((-1,1)) for v in rng.sample(range(1,n+1),width)))
    formulas.append((n,clauses))
for n,clauses in formulas:
    game,meta=cnf_game(clauses,n)
    ref=Reference(game.wire()); ref.single_equation_compatible()
    result,request=checked(game,required=1<<meta["root"],decision=True,exhaustive=False)
    need(result["stats"]["initial_pairs"]==n,"SAT parameter preservation")
    expected=next(sat_assignments(clauses,n),None) is not None
    need((result["status"]=="feasible")==expected,"SAT reduction disagreement")
    # Decode the chosen domain's literals to an actual satisfying assignment.
    if expected:
        w=set(bits(int(result["domain"],16)))
        assignment=[meta["literals"][j+1] in w for j in range(n)]
        need(all(any(assignment[abs(v)-1]==(v>0) for v in c) for c in clauses),"assignment decoding")
        sat_count+=1
    else: unsat_count+=1
    if formula_count<16 or formula_count in (255,511,512,513,514,515,516):
        separator_rows+=ref.check_separator()
    formula_count+=1
summary["SAT_reduction"]={"formulas":formula_count,"satisfiable":sat_count,"unsatisfiable":unsat_count,
                          "separator_flattened_rows":separator_rows,
                          "all_safety_relations_complement_checked":True,
                          "parameter_equals_variable_count_checked":True}

# Caller-pinned proof bundle and mutation tests.
game,meta=cnf_game([(1,2),(-1,2),(1,-2)],2)
result,request=checked(game,required=1<<meta["root"],exhaustive=False)
ref=Reference(game.wire())
bundle={"game":game.wire(),"request":request,"result":result,"reduction":meta}
(OUT/'example_certificate.json').write_text(json.dumps(bundle,sort_keys=True,indent=2)+'\n')
mutations=[]
def mutate(label,fn):
    bad=deepcopy(result); fn(bad); mutations.append((label,bad))
mutate('game pin',lambda r:r.__setitem__('game_sha256','0'*64))
mutate('objective binding',lambda r:r['weights'].__setitem__(0,9))
mutate('required binding',lambda r:r.__setitem__('required','0x0'))
mutate('forbidden binding',lambda r:r.__setitem__('forbidden','0x1'))
mutate('status',lambda r:r.__setitem__('status','infeasible'))
mutate('score',lambda r:r.__setitem__('score',r['score']+1))
mutate('domain',lambda r:r.__setitem__('domain','0x0'))
mutate('strategy bounds',lambda r:r['strategy'].__setitem__(0,game.n))
mutate('inactive symmetry',lambda r:r['strategy'].__setitem__(3*meta['dead'],meta['sink']))
mutate('node count',lambda r:r['stats'].__setitem__('nodes',0))
mutate('false local envelope',lambda r:r['proof'].__setitem__('envelope','0x0'))
mutate('omitted branch',lambda r:r['proof']['children'].pop())
mutate('false obstruction',lambda r:r['proof'].__setitem__('pair',[meta['sink'],meta['dead']]))
mutate('missing deletions',lambda r:r['proof'].__setitem__('removed',[]))
mutate('unknown field',lambda r:r.__setitem__('trusted',True))
for label,bad in mutations:
    try: ref.verify(bad,request)
    except (ValueError,KeyError,IndexError,TypeError): pass
    else: raise ValueError('accepted mutation: '+label)
summary['mutations_rejected']=[label for label,_ in mutations]

# Negative weights are intentionally outside the envelope optimizer's contract.
try: Engine(game).solve(weights=[-1]+[1]*(game.n-1))
except ValueError: pass
else: raise ValueError('negative weights accepted')
# Hard requirements can conflict; that must be certified infeasible.
checked(game,required=1<<meta['root'],forbidden=1<<meta['root'],exhaustive=False)
summary['negative_weight_guard']=True

# Non-heredity: removing a required successor invalidates a previously winning set.
path=QGame(1,(2,2,2, 1,1,1, 0,0,0))
pathref=Reference(path.wire())
need(pathref.feasible({0,1}) and not pathref.feasible({0}),'non-heredity calibration')
summary['negative_knowledge']={'nonhereditary_domain':[[0,1],[0]],
                              'scope_of_conflicts':'valid only inside the recorded viability envelope'}

# Scaled deterministic UNSAT: every sign clause excludes one of 2^6 assignments.
clauses=[tuple((j+1)*s for j,s in enumerate(signs)) for signs in product((-1,1),repeat=6)]
game,meta=cnf_game(clauses,6,min_k=7,live_rigid_padding=True)
start=time.perf_counter()
result,request=checked(game,required=1<<meta['root'],decision=True,exhaustive=False)
elapsed=time.perf_counter()-start
need(result['status']=='infeasible','scaled complete-CNF verdict')
need(result['stats']['nodes']==127 and result['stats']['initial_pairs']==6,'scaled search tree')
summary['scaled_case']={'state_arity':game.k,'states':game.n,'environment_values':3,
                       'safe_edges':sum(r.bit_count() for r in game.rows),'clauses':64,
                       'literal_variables':6,'verdict':result['status'],'stats':result['stats'],
                       'game_sha256':digest(game.wire()),'proof_sha256':digest(result['proof']),
                       'not_a_3_CNF_instance':True,'exhaustive_domain_search_run':False}
(OUT/'timing_diagnostic.json').write_text(json.dumps({'seconds_solver_plus_independent_proof_check':elapsed,
    'diagnostic_only':True,'not_a_comparison_to_existing_backends':True},indent=2)+'\n')
summary['transcript_sha256']=digest(transcript)
summary['scope']={'formal_prover':'not available; not run',
                  'full_repository_tests':'not run; additive isolated prototype',
                  'novelty':'unverified outside targeted search',
                  'Tau_dependency':False,'original_signature_DAG_emitted':False}
(OUT/'replay.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
print(json.dumps(summary,sort_keys=True,indent=2))

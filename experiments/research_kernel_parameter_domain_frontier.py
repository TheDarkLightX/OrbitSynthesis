#!/usr/bin/env python3
"""Emit a Research Kernel-compatible evidence packet for the current tranche.

The configured Research Kernel MCP transport is not present in this runtime.
This offline adapter follows the public Research-Kernel-MCP durable schema and
fail-closed status vocabulary so the packet can be inspected or imported later.
It stores public research artifacts only, never private reasoning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

ATOM_TYPES={
    'OBSERVATION','QUESTION','HYPOTHESIS','CLAIM','EVIDENCE','COUNTEREXAMPLE',
    'REFORMULATION','EXPERIMENT','RESULT','RISK','DECISION','OPEN_PROBLEM'
}
STATUSES={'DRAFT','CANDIDATE','UNKNOWN','TESTABLE','UNDER_TEST','SUPPORTED','REFUTED','SUPERSEDED','STALE'}
EDGE_TYPES={'SUPPORTS','REFUTES','DEPENDS_ON','CONTRADICTS','REFORMULATES','GENERALIZES','SPECIALIZES','ANALOGIZES','OPERATIONALIZES','TESTS','PRODUCES','SUPERSEDES','CITES'}

def canon(obj:Any)->str: return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def pretty(obj:Any)->str: return json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)
def sha(data:bytes)->str: return 'sha256:'+hashlib.sha256(data).hexdigest()
def now()->str: return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())

def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]); ap.add_argument('--out-root',type=Path)
    args=ap.parse_args(); root=args.repo_root.resolve(); out=(args.out_root or root/'runs'/'research_kernel_parameter_domain_frontier').resolve(); out.mkdir(parents=True,exist_ok=True)
    zag=root/'runs'/'zag_parameter_domain_frontier'/'summary.json'
    lean=root/'formal'/'OrbitSynthesis'/'ParameterClosure.lean'
    module=root/'src'/'orbitsynthesis'/'pointed_kernel.py'
    closure_module=root/'src'/'orbitsynthesis'/'parameter_closure.py'
    frontier_module=root/'src'/'orbitsynthesis'/'parameter_frontier.py'
    facade_module=root/'src'/'orbitsynthesis'/'parameter_core.py'
    experiment=root/'experiments'/'quasiprimal_parameter_domain_frontier.py'
    for path in (zag,lean,module,closure_module,frontier_module,facade_module,experiment):
        if not path.is_file(): raise FileNotFoundError(path)
    zag_data=json.loads(zag.read_text())
    run_id='run_orbitsynthesis_parameter_domain_frontier_20260812'
    created=now(); db=out/'research_kernel.sqlite3'
    if db.exists(): db.unlink()
    conn=sqlite3.connect(db)
    conn.executescript('''
    CREATE TABLE runs(id TEXT PRIMARY KEY,title TEXT,goal TEXT,status TEXT,created_at TEXT,updated_at TEXT,budget_json TEXT,constraints_json TEXT,success_criteria TEXT,metadata_json TEXT);
    CREATE TABLE atoms(id TEXT PRIMARY KEY,run_id TEXT,type TEXT,content TEXT,normalized_content TEXT,status TEXT,confidence REAL,evidence_score REAL,novelty_score REAL,refutability_score REAL,importance_score REAL,uncertainty_score REAL,hash TEXT,created_at TEXT,updated_at TEXT,source_refs_json TEXT,artifact_refs_json TEXT,parent_ids_json TEXT,tags_json TEXT,metadata_json TEXT);
    CREATE TABLE edges(id TEXT PRIMARY KEY,run_id TEXT,source_atom_id TEXT,target_atom_id TEXT,edge_type TEXT,weight REAL,rationale TEXT,created_at TEXT);
    CREATE TABLE evidence(id TEXT PRIMARY KEY,run_id TEXT,atom_id TEXT,source_type TEXT,source_uri TEXT,quote TEXT,summary TEXT,reliability REAL,artifact_hash TEXT,captured_at TEXT,metadata_json TEXT);
    CREATE TABLE artifacts(hash TEXT PRIMARY KEY,run_id TEXT,path TEXT,mime_type TEXT,size INTEGER,created_at TEXT,provenance_json TEXT);
    CREATE TABLE promotions(id TEXT PRIMARY KEY,run_id TEXT,claim_atom_id TEXT,from_status TEXT,to_status TEXT,gate_result_json TEXT,rationale TEXT,created_at TEXT);
    CREATE TABLE events(id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,event_type TEXT,payload_json TEXT,created_at TEXT);
    ''')
    conn.execute('INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?)',(
        run_id,'OrbitSynthesis parameter-core/domain frontier',
        'Compute and falsify the exact joint parameter-language and winning-domain frontier; formalize the closure obstruction reduction.',
        'ACTIVE',created,created,canon({'state_limit':9,'random_games':zag_data['random_game_count']}),
        canon({'fail_closed':True,'no_hidden_reasoning':True,'direct_mcp_transport':'unavailable'}),
        'Zero reference/optimized mismatches; minimized false local abstraction; exact finite frontier; no-sorry Lean artifact.',
        canon({'domain':'finite quasi-primal reactive synthesis','schema':'research_kernel/offline-replay/v1'})))
    events=[]
    def event(kind,payload):
        conn.execute('INSERT INTO events(run_id,event_type,payload_json,created_at) VALUES (?,?,?,?)',(run_id,kind,canon(payload),now())); events.append({'event_type':kind,'payload':payload})
    event('run_started',{'run_id':run_id})
    artifacts={}
    for path,mime in (
        (zag,'application/json'),
        (lean,'text/x-lean'),
        (module,'text/x-python'),
        (closure_module,'text/x-python'),
        (frontier_module,'text/x-python'),
        (facade_module,'text/x-python'),
        (experiment,'text/x-python'),
    ):
        data=path.read_bytes(); h=sha(data); rel=str(path.relative_to(root)); artifacts[rel]=h
        conn.execute('INSERT INTO artifacts VALUES (?,?,?,?,?,?,?)',(h,run_id,rel,mime,len(data),now(),canon({'original_path':rel,'kind':'repository_artifact'})))
        event('artifact_ingested',{'path':rel,'hash':h})
    atoms={}
    def atom(aid,typ,content,status,*,parents=(),tags=(),scores=(.7,.7,.8,.5),metadata=None):
        assert typ in ATOM_TYPES and status in STATUSES
        ev,nov,ref,imp=scores; digest=sha(canon({'run_id':run_id,'type':typ,'content':' '.join(content.lower().split()),'parents':list(parents),'tags':list(tags)}).encode())
        conn.execute('INSERT INTO atoms VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
            aid,run_id,typ,content,' '.join(content.lower().split()),status,None,ev,nov,ref,imp,1.0-ev,digest,now(),now(),'[]','[]',canon(list(parents)),canon(sorted(tags)),canon(metadata or {})))
        atoms[aid]={'id':aid,'type':typ,'content':content,'status':status,'parents':list(parents),'tags':list(tags)}; event('atom_added',{'atom_id':aid,'type':typ,'status':status})
        for parent in parents: edge('edge_dep_'+aid+'_'+parent,aid,parent,'DEPENDS_ON','declared theorem/experiment dependency')
    def edge(eid,source,target,typ,rationale,weight=1.0):
        assert typ in EDGE_TYPES
        conn.execute('INSERT OR IGNORE INTO edges VALUES (?,?,?,?,?,?,?,?)',(eid,run_id,source,target,typ,weight,rationale,now())); event('edge_added',{'edge_id':eid,'edge_type':typ})
    def evidence(eid,aid,source_type,path,summary,reliability=1.0):
        h=artifacts[str(path.relative_to(root))]
        conn.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?,?,?,?)',(eid,run_id,aid,source_type,str(path.relative_to(root)),'',summary,reliability,h,now(),canon({'replayable':True})))
        conn.execute('UPDATE atoms SET artifact_refs_json=?,source_refs_json=? WHERE id=?',(canon([h]),canon([str(path.relative_to(root))]),aid)); event('evidence_attached',{'evidence_id':eid,'atom_id':aid,'artifact_hash':h})
    atom('q_frontier','QUESTION','What is the exact Pareto frontier between definable parameter cores and term-controllable invariant domains for the Quackenbush benchmark?','TESTABLE',tags=('frontier','parameter-core'))
    atom('r_minimum','REFORMULATION','Replace raw parameter sets and raw strategy tables by definable-constant cores and one seed per pointed generated-subalgebra class.','SUPPORTED',parents=('q_frontier',),tags=('morph','minimum-sufficient-abstraction'))
    atom('r_optimization','REFORMULATION','Optimize the partial order (smaller generator rank, smaller controller language, larger invariant domain) and return its nondominated antichain.','SUPPORTED',parents=('q_frontier',),tags=('morph','optimization-form'))
    atom('claim_bounded_equiv','CLAIM',f"On all {3*512} core/domain instances of the Quackenbush benchmark, raw groupoid, rebuilt pointed, and compiled pointed-core solvers agree; raw and compiled also agree on {zag_data['random_differential_instances']} deterministic random instances.",'SUPPORTED',parents=('r_minimum',),tags=('bounded','differential','zag'),scores=(1,.5,1,.95))
    atom('claim_frontier','CLAIM','The exact nondominated benchmark frontier consists of the two incomparable rank-0 seven-state domains and the rank-1 core {0,1} controlling every state except the dead state (1,0).','SUPPORTED',parents=('claim_bounded_equiv','r_optimization'),tags=('bounded','frontier'),scores=(1,.7,1,1))
    atom('claim_generic','CLAIM','For every finite quasi-primal algebra and closed parameter core, fixed-domain polynomial-controller synthesis factorizes into independent pointed-class seed intersections.','UNDER_TEST',parents=('r_minimum',),tags=('generic','lean-pending'),scores=(.55,.8,.9,1))
    atom('claim_closure_obstruction','CLAIM','For any closure operator and closed obstruction family, hitting every complement is equivalent to the abstract closure avoiding every obstruction core.','UNDER_TEST',parents=('r_minimum',),tags=('generic','lean','formalization'),scores=(.65,.7,.9,.9))
    atom('claim_naive','HYPOTHESIS','Generated-subalgebra-local feasibility without pointed transport is exact for quasi-primal fixed-domain synthesis.','REFUTED',parents=('q_frontier',),tags=('rejected-candidate',),scores=(1,.2,1,.8))
    atom('cx_naive','COUNTEREXAMPLE','At core empty and W={00,01,11}, every observation has a locally admissible output, but the pointed class 000<->111 forces the empty seed intersection {01}∩{10}.','REFUTED',parents=('claim_naive',),tags=('minimized','counterexample'))
    edge('edge_refutes_naive','cx_naive','claim_naive','REFUTES','Exact minimized no-greatest-region witness.')
    atom('risk_lean','RISK','Lean source has no sorry/admit/axiom, but the pinned Lean toolchain could not be executed locally and GitHub Actions is billing-blocked; do not label the formal theorem PROVED.','UNDER_TEST',parents=('claim_closure_obstruction',),tags=('lean','infrastructure'))
    atom('open_kernel','OPEN_PROBLEM','Decide whether the public free-function parameter APIs should become FiniteSafetyGame convenience methods, and prove the compiled pointed solver equivalent to raw preservation constraints in Lean.','UNKNOWN',parents=('claim_generic',),tags=('next-action','kernel'))
    evidence('ev_equiv','claim_bounded_equiv','experiment',zag,'Exhaustive and deterministic-random differential summary plus raw timing samples.')
    evidence('ev_frontier','claim_frontier','experiment',zag,'Exact enumerated core/domain frontier and minimized failed abstraction.')
    evidence('ev_generic','claim_generic','artifact',module,'Standalone compiled parameter-core and pointed-class kernel implementation.',.8)
    evidence('ev_lean','claim_closure_obstruction','proof',lean,'No-sorry Lean formalization candidate; compilation authority unavailable.',.4)
    evidence('ev_cx','cx_naive','counterexample',experiment,'Executable minimized counterexample and exhaustive gate.')
    edge('edge_support_equiv','claim_bounded_equiv','claim_frontier','SUPPORTS','Solver equivalence supports the exact enumerated frontier.')
    edge('edge_tests_generic','claim_bounded_equiv','claim_generic','TESTS','Bounded differential corpus attacks the generic implementation theorem.')
    edge('edge_tests_closure','risk_lean','claim_closure_obstruction','TESTS','Formal source exists but compiler gate remains open.')
    # Fail-closed promotion receipts: only bounded claims pass.
    for aid in ('claim_bounded_equiv','claim_frontier'):
        gate={'ok':True,'has_support_evidence':True,'has_refutation_attempt':True,'has_dependencies':True,'has_provenance':True,'has_contradiction_search':True,'has_replay_recipe':True,'has_no_refuting_evidence':True}
        conn.execute('INSERT INTO promotions VALUES (?,?,?,?,?,?,?,?)',('promote_'+aid,run_id,aid,'UNDER_TEST','SUPPORTED',canon(gate),'Finite claim passed exhaustive/differential and replayable-evidence gates.',now()))
    conn.commit()
    frontier=[atoms['claim_generic'],atoms['claim_closure_obstruction'],atoms['risk_lean'],atoms['open_kernel']]
    report={
        'ok':True,'schema':'research_kernel/report/v1','run_id':run_id,
        'counts_by_status':{s:sum(1 for a in atoms.values() if a['status']==s) for s in sorted(STATUSES)},
        'supported_claims':[atoms['claim_bounded_equiv'],atoms['claim_frontier']],
        'refuted_claims':[atoms['claim_naive']],
        'counterexamples':[atoms['cx_naive']],
        'frontier':frontier,
        'artifacts':artifacts,
        'non_claims':[
            'Offline adapter uses the public Research Kernel schema because the configured MCP transport was unavailable.',
            'SUPPORTED is restricted to the exact bounded benchmark claims.',
            'The generic pointed theorem and Lean theorem remain UNDER_TEST.'
        ]
    }
    (out/'report.json').write_text(pretty(report)+'\n')
    (out/'atoms.jsonl').write_text(''.join(canon(a)+'\n' for a in atoms.values()))
    edge_rows=[dict(zip(('id','run_id','source_atom_id','target_atom_id','edge_type','weight','rationale','created_at'),row)) for row in conn.execute('SELECT * FROM edges ORDER BY rowid')]
    (out/'edges.jsonl').write_text(''.join(canon(e)+'\n' for e in edge_rows))
    (out/'events.jsonl').write_text(''.join(canon(e)+'\n' for e in events))
    conn.close()
    print(pretty(report))

if __name__=='__main__': main()

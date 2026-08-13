#!/usr/bin/env python3
"""Write a fail-closed Research Kernel replay packet for the nogood campaign."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(p): return 'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument('--repo-root',type=Path,required=True); p.add_argument('--out-root',type=Path,required=True); a=p.parse_args(); root=a.repo_root.resolve()
    summary=json.loads((root/'runs/zag_nogood_domain_search/summary.json').read_text()); ex=summary['exact']; rnd=summary['random']; scale=summary['scale']
    assert ex['unsound']==rnd['mismatches']==0 and ex['instances']==1536 and ex['nogoods']==8
    paths=['runs/zag_nogood_domain_search/summary.json','experiments/quasiprimal_nogood_domain_search.py','src/orbitsynthesis/domain_search_bitset.py','formal/OrbitSynthesis/DomainNogood.lean']
    artifacts={x:digest(root/x) for x in paths}
    atoms=[
      {'id':'q','type':'QUESTION','status':'TESTABLE','content':'Can pointed conflicts replace exhaustive domain enumeration?','parents':[]},
      {'id':'bounded','type':'CLAIM','status':'SUPPORTED','content':f"Exact agreement on {ex['instances']} benchmark and {rnd['instances']} random instances; {ex['nogoods']} nogoods replayed over {ex['covered_replays']} covered domains.",'parents':['q']},
      {'id':'scale','type':'CLAIM','status':'SUPPORTED','content':f"Returned strategies checked on the {scale['states']}-state scale family; not exhaustive over 2^27 domains.",'parents':['bounded']},
      {'id':'generic','type':'CLAIM','status':'UNDER_TEST','content':'Two-sided pointed-class nogood search is sound and complete in general.','parents':['q']},
      {'id':'open','type':'OPEN_PROBLEM','status':'UNKNOWN','content':'Transport learned domain nogoods across the parameter-core lattice.','parents':['generic']}]
    edges=[{'source_atom_id':x['id'],'target_atom_id':y,'edge_type':'DEPENDS_ON'} for x in atoms for y in x['parents']]
    report={'schema':'research_kernel/report/v1','supported_claims':[x for x in atoms if x['status']=='SUPPORTED'],'frontier':[x for x in atoms if x['status'] in {'TESTABLE','UNDER_TEST','UNKNOWN'}],'artifacts':artifacts,'non_claims':['Generic theorem and Lean compiler status remain UNDER_TEST.']}
    a.out_root.mkdir(parents=True,exist_ok=True)
    for name,rows in [('atoms.jsonl',atoms),('edges.jsonl',edges)]: (a.out_root/name).write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in rows))
    (a.out_root/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); print(json.dumps(report,sort_keys=True))
if __name__=='__main__': main()

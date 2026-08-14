#!/usr/bin/env python3
"""Structural and semantic replay for the pivot-normalized fast anchor."""

from __future__ import annotations
import hashlib
import itertools
import json

Q=(0,1,2)
B=(0,1)

def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)

def d(x: int,y: int,z: int)->int:
    return z if x==y else x

def u(x: int)->int:
    return (1,0,1)[x]

def clog2(n: int)->int:
    need(n>=1,"clog2 domain")
    return (n-1).bit_length()

def profile(r: int)->tuple[int,int]:
    need(r>=1,"arity")
    if r==1:
        return 0,0
    if r==2:
        return 3,3
    total=2**clog2(r)
    def build(start: int,span: int,retained: int):
        if retained==0:
            return None
        if start==0 and span==2 and retained==2:
            return 4,3
        if span==1:
            if start==r-1:
                return 0,0
            need(start>=2,"unpaired pivot")
            return 1,2
        half=span//2
        left=build(start,half,min(retained,half))
        right=build(start+half,half,max(0,retained-half))
        need(left is not None,"missing left")
        if right is None:
            return left
        return left[0]+right[0]+1,max(left[1],right[1])+1
    result=build(0,total,r)
    need(result is not None,"missing root")
    return result

def merge(values: list[int],identity: int)->int:
    while len(values)>1:
        out=[]
        i=0
        while i+1<len(values):
            out.append(d(values[i],identity,values[i+1]))
            i+=2
        if i<len(values):
            out.append(values[i])
        values=out
    return values[0]

def anchor(point: tuple[int,...])->int:
    r=len(point)
    if r==1:
        return point[0]
    if r==2:
        return d(point[1],u(u(point[1])),point[0])
    y=point[1]
    e=u(y)
    values=[d(y,u(e),d(point[2],y,e))]
    values.extend(d(point[i],y,e) for i in range(3,r))
    values.append(point[0])
    return merge(values,e)

rows=[]
evaluations=0
for r in range(1,9):
    nodes,depth=profile(r)
    expected_nodes=0 if r==1 else 3 if r==2 else 2*r-1
    expected_depth=0 if r==1 else 3 if r==2 else clog2(r)+2
    need(nodes==expected_nodes,"node census")
    need(depth<=expected_depth,"depth census")
    for point in itertools.product(Q,repeat=r):
        expected=point[0] if all(v in B for v in point) else 2
        need(anchor(point)==expected,"semantic failure")
        evaluations+=1
    rows.append({"r":r,"nodes":nodes,"depth":depth,"depth_bound":expected_depth})

result={"schema":"orbit-synthesis/fast-anchor-profile/v1",
        "evaluations":evaluations,"rows":rows}
canonical=json.dumps(result,sort_keys=True,separators=(",",":"))
result["semantic_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
print(json.dumps(result,indent=2,sort_keys=True))

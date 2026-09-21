#!/usr/bin/env python3
"""Structural and semantic replay for the pivot-normalized fast anchor."""

from __future__ import annotations
import hashlib
import itertools
import json
from functools import cache

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

def anchor_term(r: int):
    """Materialize the original-signature DAG described by the manuscript."""
    need(r>=1,"arity")
    x=lambda i: ("x",i)
    unary=lambda a: ("u",a)
    disc=lambda a,b,c: ("d",a,b,c)
    if r==1:
        return x(0)
    if r==2:
        return disc(x(1),unary(unary(x(1))),x(0))
    e=unary(x(1))
    robust=disc(x(1),unary(e),disc(x(2),x(1),e))
    total=2**clog2(r)
    def build(start: int,span: int):
        if start>=r:
            return None
        if start==0 and span==2:
            return robust
        if span==1:
            if start==r-1:
                return x(0)
            need(start>=2,"unpaired pivot")
            return disc(x(start+1),x(1),e)
        half=span//2
        left=build(start,half)
        right=build(start+half,half)
        need(left is not None,"missing left")
        return left if right is None else disc(left,e,right)
    result=build(0,total)
    need(result is not None,"missing root")
    return result

def profile(term)->tuple[int,int]:
    nodes=set()
    @cache
    def depth(t):
        if t[0]=="x":return 0
        need(t[0] in ("u","d"),"foreign operation")
        nodes.add(t)
        return 1+max(depth(child) for child in t[1:])
    height=depth(term)
    return len(nodes),height

def evaluate(term,point: tuple[int,...])->int:
    @cache
    def run(t):
        if t[0]=="x":return point[t[1]]
        if t[0]=="u":return u(run(t[1]))
        need(t[0]=="d","foreign operation")
        return d(*(run(child) for child in t[1:]))
    return run(term)

rows=[]
evaluations=0
for r in range(1,9):
    term=anchor_term(r)
    nodes,depth=profile(term)
    expected_nodes=0 if r==1 else 3 if r==2 else 2*r-1
    expected_depth=0 if r==1 else 3 if r==2 else clog2(r)+2
    need(nodes==expected_nodes,"node census")
    need(depth<=expected_depth,"depth census")
    for point in itertools.product(Q,repeat=r):
        expected=point[0] if all(v in B for v in point) else 2
        need(evaluate(term,point)==expected,"semantic failure")
        evaluations+=1
    rows.append({"r":r,"nodes":nodes,"depth":depth,"depth_bound":expected_depth})

result={"schema":"orbit-synthesis/fast-anchor-profile/v1",
        "evaluations":evaluations,"rows":rows}
canonical=json.dumps(result,sort_keys=True,separators=(",",":"))
result["semantic_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
print(json.dumps(result,indent=2,sort_keys=True))

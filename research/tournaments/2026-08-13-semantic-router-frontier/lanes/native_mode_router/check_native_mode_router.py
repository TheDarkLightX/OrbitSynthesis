#!/usr/bin/env python3
"""Fail-closed independent oracle for the native find-first router refinement."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction

from native_mode_model import *


def check_semantics() -> dict[str,int]:
    expected = {"E":(0,0),"G":(1,0),"L":(0,1)}
    digit = pair = modes = support = 0
    for x,p in itertools.product(Q,repeat=2):
        name = first_mode((x,),(p,))
        req(gl_digit(x,p) == expected[name], "digit GL")
        req(mode_digit(x,p) == MODE[name], "digit mode")
        digit += 2
    states = ((0,0),(1,0),(0,1))
    for a,b,c in itertools.product(states,repeat=3):
        req(gl_comp(gl_comp(a,b),c) == gl_comp(a,gl_comp(b,c)), "GL assoc")
    for a,b,c in itertools.product(Q,repeat=3):
        req(mode_comp(mode_comp(a,b),c) == mode_comp(a,mode_comp(b,c)), "mode assoc")
    for w in range(1,6):
        words = list(itertools.product(Q,repeat=w))
        tables = set()
        for p in words:
            tables.add(tuple(balanced_mode(t,p) for t in words))
            for i in range(w):
                t = list(p)
                base = balanced_mode(tuple(t),p)
                t[i] = (t[i]+1)%3
                req(base != balanced_mode(tuple(t),p), "missing support")
                support += 1
        req(len(tables) == 3**w, "mode roots not distinct")
        for t in words:
            for p in words:
                name = first_mode(t,p)
                req(balanced_gl(t,p) == expected[name], "GL summary")
                req(balanced_mode(t,p) == MODE[name], "mode summary")
                modes += 2
                for root in (0,1):
                    req(gl_pair(root,t,p) == frozen_pair(root,t,p), "program pair")
                    for x in (0,1):
                        req(fused_bottom(root,t,p,x) == expected_bottom(root,t,p,x), "bottom")
                    pair += 1
    return {"digit":digit,"mode":modes,"pair":pair,"support":support}


def check_routers() -> dict[str,int]:
    exhaustive = sampled = 0
    for w in (0,1,2):
        words = list(itertools.product(Q,repeat=w))
        for bits in itertools.product((0,1),repeat=len(words)):
            payloads = dict(zip(words,bits,strict=True))
            for t in words:
                for root in (0,1):
                    want = u(payloads[t]) if root else payloads[t]
                    req(eval_full_router(root,t,payloads) == want, "full router")
                    exhaustive += 1
    for w in range(3,6):
        words = list(itertools.product(Q,repeat=w))
        targets = words[:7]+words[-7:]+[words[len(words)//2]]
        for seed in range(3):
            payloads = {p:(sum((i+1)*x for i,x in enumerate(p))+seed)&1 for p in words}
            for t in targets:
                for root in (0,1):
                    want = u(payloads[t]) if root else payloads[t]
                    req(eval_full_router(root,t,payloads) == want, "sampled router")
                    sampled += 1
    return {"exhaustive":exhaustive,"sampled":sampled}


def check_minimality() -> dict[str,object]:
    mode_min,mode_layers = minimum_roots({(2,0,0),(0,2,0)},5)
    gl_min,gl_layers = minimum_roots({(0,0,0),(0,1,1),(1,0,1),(0,1,0),(1,0,0)},6)
    req(mode_min == 5 and gl_min == 6, "one-digit minima")
    cases = [(m,x) for m in Q for x in (0,1)]
    target = tuple(0 if m == 0 else 1 if m == 1 else u(x) for m,x in cases)
    terms = ("m","x","0","1","2")
    def val(term,m,x): return {"m":m,"x":x,"0":0,"1":1,"2":2}[term]
    one_op = {tuple(u(val(a,m,x)) for m,x in cases) for a in terms}
    for a,b,c in itertools.product(terms,repeat=3):
        one_op.add(tuple(d(val(a,m,x),val(b,m,x),val(c,m,x)) for m,x in cases))
    req(target not in one_op, "negative bottom has one-op term")
    req(target == tuple(d(m,2,u(x)) for m,x in cases), "two-op bottom")
    return {"mode_nodes":mode_min,"gl_nodes":gl_min,"mode_layers":mode_layers,
            "gl_layers":gl_layers,"negative_bottom_nodes":2}


def check_bounds() -> dict[str,object]:
    worst_gl = (Fraction(0),0,0)
    worst_mode = (Fraction(0),0)
    worst_generic = (Fraction(0),0,0)
    worst_closed = (Fraction(0),0)
    for w in range(1,257):
        q = 3**w
        req(9*gl_nodes(w) <= 28*q, "GL recurrence")
        req(3*mode_nodes(w) <= 5*q, "mode recurrence")
        if w >= 8: req(27*mode_nodes(w) <= 28*q, "large mode recurrence")
        vm,vc = Fraction(mode_vector(w),q),Fraction(closed_router(w),q)
        worst_mode = max(worst_mode,(vm,w))
        worst_closed = max(worst_closed,(vc,w))
        req(9*mode_vector(w) <= 17*q, "mode bound")
        req(3*closed_router(w) <= 10*q, "closed router bound")
        for root in (0,1):
            vg,vr = Fraction(gl_vector(root,w),q),Fraction(generic_router(root,w),q)
            if vg > worst_gl[0]: worst_gl = (vg,root,w)
            if vr > worst_generic[0]: worst_generic = (vr,root,w)
            req(27*gl_vector(root,w) <= 100*q, "GL vector bound")
            req(9*generic_router(root,w) <= 35*q, "generic router bound")
    req(worst_mode == (Fraction(17,9),2), "mode extremum")
    req(worst_closed == (Fraction(10,3),2), "closed extremum")
    req(worst_gl == (Fraction(100,27),1,3), "GL extremum")
    req(worst_generic == (Fraction(35,9),1,2), "generic extremum")
    return {"widths":256,"mode":"17/9","gl":"100/27","generic":"35/9","closed":"10/3"}


def check_compiler() -> dict[str,object]:
    worst = (Fraction(0),0)
    min_slack = None
    checks = 0
    for r in range(64,16385):
        reserve,h,m,b,p = params(r)
        prefix = r-b
        req(8*ceil_log3(r*r) <= r, "reserve")
        req(16*h >= 13*r, "headroom")
        req(48*m > 13*r, "block lower")
        req(prefix >= 8 and 27*mode_nodes(prefix) <= 28*p, "prefix recurrence")
        n = nonbinary_nodes(r)
        req(n*r < 15*3**r, "nonbinary constant")
        req(n*r+3**r < 16*3**r, "total constant")
        ratio = Fraction(n*r,3**r)
        if ratio > worst[0]: worst = (ratio,r)
        depth,cap = nonbinary_depth(r),r+4*clog2(r)+9
        req(depth <= cap, "depth")
        slack = cap-depth
        min_slack = slack if min_slack is None else min(min_slack,slack)
        req(reserve+h == r and m == 3**b and m*p == 3**r, "parameters")
        checks += 12
    req(worst[1] == 93, "finite maximum moved")
    return {"arities":[64,16384],"checks":checks,"nonbinary":"<15*3^r/r",
            "total":"<16*3^r/r","depth":"<=r+4*ceil(log2 r)+9",
            "worst_arity":93,"worst_decimal":format(float(worst[0]),".15f"),
            "min_depth_slack":min_slack}


def check_mutations() -> dict[str,object]:
    a,b = (1,0),(0,0)
    mutant = (d(a[1],a[0],b[0]),d(a[0],a[1],b[1]))
    req(mutant != gl_comp(a,b), "swapped GL mutant")
    req(mode_comp(0,1) == 0 and mode_comp(1,0) == 1, "reversal witness")
    req(d(2,2,0) != fused_bottom(0,(1,),(1,),0), "payload complement mutant")
    r = 93
    _,_,_,bwidth,p = params(r)
    old,new = 10*p,3*p-1+mode_nodes(r-bwidth)
    req(new < old, "compiler mutant")
    return {"swapped_gl":True,"reversed_find_first":True,
            "missing_payload_complement":True,
            "repeated_boolean_controls":{"arity":r,"old":old,"new":new}}


def main() -> int:
    result = {
        "theorem":"native find-first mode vector and fused signed router",
        "status":"independent executable oracle; paper proof separate; Lean port pending",
        "python":sys.version.split()[0],
        "semantics":check_semantics(),
        "routers":check_routers(),
        "minimality":check_minimality(),
        "bounds":check_bounds(),
        "compiler":check_compiler(),
        "mutations":check_mutations(),
    }
    raw = json.dumps(result,sort_keys=True,separators=(",",":")).encode()
    result["semantic_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

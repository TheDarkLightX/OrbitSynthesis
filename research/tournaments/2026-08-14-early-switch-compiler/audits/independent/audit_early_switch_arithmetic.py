#!/usr/bin/env python3
"""Independent arithmetic reconstruction of the early-switch compiler."""
from __future__ import annotations
import hashlib, json, math, sys
from functools import cache
from pathlib import Path

def need(x,m):
    if not x: raise RuntimeError(m)

def clog(n,b):
    p=1; k=0
    while p<n:
        p*=b; k+=1
    return k

def floor3(n):
    p=1; b=0
    while 3*p<=n:
        p*=3; b+=1
    return b,p

@cache
def counts(w):
    if w==0: return (0,0,2)
    if w==1: return (4,4,5)
    a=(w+1)//2; b=w//2
    ra,_,_=counts(a); rb,eb,_=counts(b)
    cross=3**a*(3**b-1)//2
    r=ra+rb+3**w+cross
    e=ra+eb+2*3**w-3**(w-1)+cross
    s=2+ra+eb+cross+3**w-(3**(w-1)+1)//2
    return r,e,s

def vcount(w): return counts(w)[2]
def vdepth(w): return 2 if w==0 else 3+clog(w,2)

def binary(r):
    k=math.isqrt(r); q=3**k; w=q.bit_length()-1
    n=r-1; sizes=([n%w] if n%w else [])+[w]*(n//w)
    live=1; inst=ctrl=0
    for c in sizes:
        inst+=live; ctrl+=6*q*(2**c-1); live*=2**c
    need(live==2**(r-1),"binary leaves")
    return ((3*q-1)//2*inst,ctrl,(k+1)*len(sizes)+2*w+1)

def plan(r):
    L=4+clog(r*r,3); H=r-L; b,m=floor3(H)
    mode=2 if H>=2*m-4 else 1
    return L,H,b,m,mode

def total(r,mode):
    L,H,b,m,_=plan(r); C=clog(r,2); ad=C+2
    br,bc,bd=binary(r); anchor=2*r-1
    if mode==1:
        s=r-b; P=3**s
        T=(3*m-1)*3**m+(3*P-1)+vcount(b)+vcount(s)-2+anchor+6+br+bc
        local=ad+vdepth(b)+b+1
        nb=max(local,ad+vdepth(s))+s+5
    else:
        s=r-b-1; P=3**s
        T=((9*m-1)*3**(2*m)+(3*m-1)*3**m+(6*P-2)
           +vcount(b+1)+vcount(b)+vcount(s)-4+anchor+12+br+bc)
        wide=ad+vdepth(b+1)+b+2
        narrow=ad+vdepth(b)+b+1
        nb=max(wide,narrow,ad+vdepth(s))+s+7
    return T,max(ad+4,bd+2,nb)

def dec(n,d,k=18):
    q,r=divmod(n,d); a=[]
    for _ in range(k):
        r*=10; x,r=divmod(r,d); a.append(str(x))
    return str(q)+"."+"".join(a)

def audit():
    maximum=(-1,1,-1); trans=[]; mismatches=[]; modes={1:0,2:0}
    for r in range(64,16385):
        L,H,b,m,mode=plan(r); modes[mode]+=1
        chosen,depth=total(r,mode); unit=3**r
        need(5*chosen*r<46*unit,"size")
        need(depth<=r+math.ceil(7*clog(r,2)/5)+12,"depth")
        one,_=total(r,1); two,_=total(r,2)
        if (1 if one<=two else 2)!=mode: mismatches.append(r)
        if H in (2*m-5,2*m-4):
            trans.append({"r":r,"H":H,"m":m,"mode":mode,
                          "one":dec(one*r,unit),"two":dec(two*r,unit)})
        if chosen*r*maximum[1]>maximum[0]*unit:
            maximum=(chosen*r,unit,r)
    need(not mismatches,"crossover")
    need(maximum[2]==171,"maximum")
    return {"range":[64,16384],"modes":{str(k):v for k,v in modes.items()},
            "mismatches":mismatches,"transitions":trans,
            "maximum":{"r":maximum[2],"ratio":dec(maximum[0],maximum[1])},
            "size":"5*size*r<46*3^r",
            "depth":"r+ceil(7*ceil(log2 r)/5)+12"}

def bases():
    rows=[]
    for b in range(4,14):
        m=3**b; need(2*b+1<=m//9,"mode1")
        c=2*b+2
        for t in (0,1):
            r=2*m+c+t
            need(3**(c-1)<r*r<3**c,"ceiling")
            rows.append([b,t,r,c])
    for ok,name in [
        (5000*65<3**32,"half"),(7000*64**2<3**64,"fixed"),
        (1500*64**2<3**32,"residual"),(192*2**64<3**50,"router"),
        (24*64**2<3**42,"control")]: need(ok,name)
    return rows

def result():
    out={"schema":"orbit-synthesis/early-switch-independent-arithmetic/v1",
         "bases":bases(),"ledger":audit()}
    raw=json.dumps(out,sort_keys=True,separators=(",",":"))
    out["semantic_sha256"]=hashlib.sha256(raw.encode()).hexdigest()
    out["provenance"]={
        "schema":"orbit-synthesis/source-bound-replay/v1",
        "source":(
            "research/tournaments/2026-08-14-early-switch-compiler/"
            "audits/independent/audit_early_switch_arithmetic.py"
        ),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "replay_commands":[
            (
                "python3 research/tournaments/2026-08-14-early-switch-compiler/"
                "audits/independent/audit_early_switch_arithmetic.py --expected "
                "research/tournaments/2026-08-14-early-switch-compiler/"
                "audits/independent/receipt.json"
            ),
            (
                "python3 -O research/tournaments/2026-08-14-early-switch-compiler/"
                "audits/independent/audit_early_switch_arithmetic.py --expected "
                "research/tournaments/2026-08-14-early-switch-compiler/"
                "audits/independent/receipt.json"
            ),
        ],
        "required_equality":"normal_stdout == optimized_stdout == receipt_bytes",
    }
    return out

def main():
    expected=out=None; args=iter(sys.argv[1:])
    for a in args:
        if a=="--expected": expected=Path(next(args))
        elif a=="--out": out=Path(next(args))
        else: raise SystemExit(a)
    data=result(); text=json.dumps(data,indent=2,sort_keys=True)+"\n"
    if expected: need(data==json.loads(expected.read_text()),"receipt drift")
    if out: out.write_text(text)
    print(text,end="")

if __name__=="__main__": main()

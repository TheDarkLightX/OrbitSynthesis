#!/usr/bin/env python3
"""Standalone audit for the portfolio plane-shared fixed-Q compiler."""

from __future__ import annotations
import hashlib
import itertools
import json
import math
import random
import sys
from functools import cache
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

Q=(0,1,2)
B=(0,1)
OFFSETS=(2,3,4,5)

def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)

def clog2(n: int) -> int:
    require(n>=1,"clog2 domain")
    return (n-1).bit_length()

def floor3(n: int) -> tuple[int,int]:
    require(n>=1,"floor3 domain")
    p=1; b=0
    while 3*p<=n:
        p*=3; b+=1
    return b,p

def decimal(n: int,d: int,digits: int=18)->str:
    q,r=divmod(n,d); out=[]
    for _ in range(digits):
        r*=10; x,r=divmod(r,d); out.append(str(x))
    return f"{q}."+''.join(out)

def code(v:int)->tuple[int,int]:
    return ((0,0),(0,1),(1,0))[v]

def decode(h:int,l:int)->int:
    require((h,l) in ((0,0),(0,1),(1,0)),"legal code")
    return {(0,0):0,(0,1):1,(1,0):2}[(h,l)]

def semantic_factorization()->dict[str,object]:
    rows=0; widths={}
    for n in range(1,7):
        boolean=set(itertools.product(B,repeat=n))
        seen=set()
        for table in itertools.product(Q,repeat=n):
            high=tuple(code(v)[0] for v in table)
            low=tuple(code(v)[1] for v in table)
            rebuilt=tuple(decode(high[i],low[i]) for i in range(n))
            require(rebuilt==table,"plane factorization")
            seen.add(high);seen.add(low);rows+=n
        require(seen==boolean,"Boolean library saturation")
        widths[str(n)]={"q_tables":3**n,"boolean_roots":2**n}
    require(decode(0,0)!=2,"plane mutation")
    return {"rows":rows,"widths":widths,"mutation":{"input":2,"mutated":0}}

def reconstruction_audit()->dict[str,object]:
    local=list(itertools.product(Q,repeat=2))
    groups=[local[0:3],local[3:5],local[5:7],local[7:9]]
    owner={p:i for i,g in enumerate(groups) for p in g}
    points=list(itertools.product(Q,repeat=3))
    selectors=[
        ("p0",lambda x:0),("p1",lambda x:1),("p2",lambda x:2)
    ]
    for seed in range(61):
        rng=random.Random(0xC0DEC0+seed)
        table={x:rng.randrange(3) for x in points}
        selectors.append((f"s{seed}",lambda x,table=table:table[x]))
    rows=0; refs=0; labels=[]
    for label,sigma in selectors:
        labels.append(label); libraries={}
        for prefix in Q:
            for gi,g in enumerate(groups):
                hi=[];lo=[]
                for lp in g:
                    point=(prefix,)+lp
                    h,l=code(point[sigma(point)])
                    hi.append(h);lo.append(l)
                libraries[(prefix,gi)]=(tuple(hi),tuple(lo));refs+=2
        for point in points:
            prefix=point[0]; lp=point[1:]; gi=owner[lp]
            index=groups[gi].index(lp)
            hi,lo=libraries[(prefix,gi)]
            require(decode(hi[index],lo[index])==point[sigma(point)],
                    "selector reconstruction")
            rows+=1
    mutation=None
    for point in points:
        gi=owner[point[1:]]
        bad=(gi+1)%len(groups)
        bad_point=(point[0],)+groups[bad][0]
        if bad_point[2]!=point[2]:
            mutation={"point":list(point),"good":gi,"bad":bad,
                      "mutated":bad_point[2],"expected":point[2]}
            break
    require(mutation is not None,"group mutation")
    return {"selectors":len(selectors),"rows":rows,"plane_references":refs,
            "group_sizes":[len(x) for x in groups],
            "labels_sha256":hashlib.sha256('\n'.join(labels).encode()).hexdigest(),
            "mutation":mutation}

def split(w:int)->tuple[int,int]:
    return (w+1)//2,w//2

@cache
def generic(w:int)->int:
    if w==0:return 0
    if w==1:return 4
    a,b=split(w)
    return generic(a)+generic(b)+3**w+3**a*(3**b-1)//2

@cache
def extended(w:int)->int:
    if w==0:return 0
    if w==1:return 4
    a,b=split(w)
    return generic(a)+extended(b)+2*3**w-3**(w-1)+3**a*(3**b-1)//2

@cache
def vector(w:int)->int:
    if w==0:return 2
    if w==1:return 5
    a,b=split(w)
    return (2+generic(a)+extended(b)+3**a*(3**b-1)//2
            +3**w-(3**(w-1)+1)//2)

def vdepth(w:int)->int:
    return 2 if w==0 else 3+clog2(w)

@cache
def binary(r:int)->dict[str,int]:
    k=math.isqrt(r);q=3**k;w=q.bit_length()-1
    n=r-1;sizes=([n%w] if n%w else [])+[w]*(n//w)
    live=1;instances=controls=0
    for c in sizes:
        instances+=live;controls+=6*q*(2**c-1);live*=2**c
    require(live==2**(r-1),"binary leaves")
    return {"router":((3*q-1)//2)*instances,"control":controls,
            "depth":(k+1)*len(sizes)+2*w+1}

@cache
def budget(r:int)->tuple[int,int,int,int]:
    J=(3**r//(9*r**3)).bit_length()-1
    K=J-3
    b,m=floor3(K)
    return J,K,b,m

def candidate(r:int,c:int)->dict[str,object]:
    J,K,b,m=budget(r)
    t=b+c
    d=min(7,t)
    u=3**(t-d)
    h=K//u
    require(h>=1,"group capacity")
    splitter=3**d
    g=(splitter+h-1)//h
    q,rem=divmod(splitter,g)
    max_words=q+(1 if rem else 0)
    max_live=max_words*u
    require(max_live<=K,"live row overflow")
    table_sum=(rem*2**((q+1)*u)+(g-rem)*2**(q*u))
    N=3**t
    local=((3*N-1)//2)*table_sum
    s=r-t;require(s>=1,"prefix width")
    P=3**s
    prefix=g*(3*P-1)
    vectors=vector(t)+vector(s)+vector(d)-4
    group=3*3**d-1
    anchor=2*r-1
    br=binary(r)
    total=(local+prefix+vectors+group+anchor+6+
           br["router"]+br["control"])
    C=clog2(r);A=C+2
    local_depth=A+vdepth(t)+t+1
    prefix_depth=max(local_depth,A+vdepth(s))+s+1
    group_depth=max(prefix_depth,A+vdepth(d))+d+1
    final=max(A+4,br["depth"]+2,group_depth+4)
    return {"c":c,"J":J,"K":K,"b":b,"m":m,"t":t,"d":d,"u":u,
            "h":h,"g":g,"word_quotient":q,"word_remainder":rem,
            "live_row_max":max_live,"N":N,"s":s,"P":P,
            "local":local,"prefix":prefix,"vectors":vectors,
            "group_selector":group,"anchor":anchor,
            "binary_router":br["router"],"binary_control":br["control"],
            "total":total,"depth":final}

def selected_with_rows(r:int)->tuple[dict[str,object],dict[int,dict[str,object]]]:
    rows={c:candidate(r,c) for c in OFFSETS}
    best=min(rows.values(),key=lambda row:(row["total"],row["c"]))
    return best,rows

def analytic_tail()->dict[str,object]:
    bases=[]
    for r in (107,108,109):
        e=math.ceil(4*r/3)+3
        require(9*r**3*2**e<=3**r,"K base")
        bases.append([r,e])
    require(16*110**3<27*107**3,"K induction ratio")
    table=[];maximum=(-1,None,None,None)
    for h in range(27,81):
        g=(2187+h-1)//h
        numerator=(9*g+4)*(h+1)
        denominator=8748
        table.append([h,g,numerator,denominator])
        if maximum[1] is None or numerator*maximum[3]>maximum[0]*denominator:
            maximum=(numerator,h,g,denominator)
    require(maximum[1:3]==(78,29),"prefix argmax")
    require(maximum[0]==20935 and maximum[3]==8748,"prefix value")
    left=(20935*8*967*1000 + 2187*8748*1000 +
          4*8748*8*967)
    denominator=8748*8*967*1000
    require(25*left<67*denominator,"tail rational bound")
    require(5000*65<3**32,"prefix error")
    require(900000*967**2<3**967,"fixed group base")
    require(192*2**64<3**50,"binary router")
    require(24*64**2<3**42,"binary control")
    return {"K_bases":bases,"K_induction":"16*110^3<27*107^3",
            "prefix_table":table,
            "prefix_maximum":{"h":78,"g":29,"value":"20935/8748"},
            "local_bound":"2187/(8r)","lower_order":"4/1000",
            "tail_start":967,"target":"67/25",
            "tail_fraction":[left,denominator]}

def ledger_audit()->dict[str,object]:
    maximum=(-1,1,-1)
    finite=(-1,1,-1)
    choices={c:0 for c in OFFSETS}
    selected_rows=[]
    min_depth_slack=(10**9,-1)
    for r in range(64,16385):
        row,candidates=selected_with_rows(r);choices[row["c"]]+=1
        unit=3**r;numerator=row["total"]*r
        require(25*numerator<67*unit,"67/25 exact bound")
        C=clog2(r)
        depth_bound=r+math.ceil(7*C/5)+20
        require(row["depth"]<=depth_bound,"depth bound")
        slack=depth_bound-row["depth"]
        if slack<min_depth_slack[0]:min_depth_slack=(slack,r)
        if numerator*maximum[1]>maximum[0]*unit:
            maximum=(numerator,unit,r)
        if r<=966 and numerator*finite[1]>finite[0]*unit:
            finite=(numerator,unit,r)
        if r>=967:
            tail=candidates[4]
            require(3*tail["K"]>=4*r,"K lower")
            require(27<=tail["h"]<=80,"h range")
            require(8*tail["local"]*r*r<2187*unit,"local analytic")
            require(1000*5*3**((tail["s"]+1)//2)*r<unit,
                    "prefix error analytic")
            fixed=(tail["vectors"]-vector(tail["s"])+tail["group_selector"]
                   +tail["anchor"]+6)
            require(1000*fixed*r<unit,"fixed analytic")
            require(1000*tail["binary_router"]*r<unit,"binary router analytic")
            require(1000*tail["binary_control"]*r<unit,"binary control analytic")
            require((9*tail["g"]+4)*r*8748
                    <=20935*243*tail["m"],"prefix main analytic")
        if r in (64,65,66,67,72,94,107,184,500,966,967,1000,4096,16384):
            selected_rows.append({
                "r":r,"c":row["c"],"J":row["J"],"K":row["K"],
                "t":row["t"],"d":row["d"],"g":row["g"],
                "live_row_max":row["live_row_max"],
                "size_ratio":decimal(numerator,unit),
                "depth":row["depth"],"depth_bound":depth_bound})
    require(maximum[2]==64,"maximum location")
    require(finite[2]==64,"finite maximum")
    return {"range":[64,16384],"portfolio_offsets":list(OFFSETS),
            "choice_histogram":{str(k):v for k,v in choices.items()},
            "size_bound":"25*size*r<67*3^r",
            "depth_bound":"r+ceil(7*ceil(log2 r)/5)+20",
            "maximum":{"r":maximum[2],"ratio":decimal(maximum[0],maximum[1])},
            "finite_proof":{"range":[64,966],"maximum_r":finite[2],
                            "maximum_ratio":decimal(finite[0],finite[1])},
            "minimum_depth_slack":{"r":min_depth_slack[1],
                                   "value":min_depth_slack[0]},
            "selected":selected_rows}

def make_receipt()->dict[str,object]:
    result={"schema":"orbit-synthesis/plane-shared-portfolio/v1",
            "plane_factorization":semantic_factorization(),
            "selector_reconstruction":reconstruction_audit(),
            "analytic_tail":analytic_tail(),
            "ledger":ledger_audit()}
    canonical=json.dumps(result,sort_keys=True,separators=(",",":"))
    result["semantic_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
    return result

def main()->int:
    expected=output=None
    args=iter(sys.argv[1:])
    for arg in args:
        if arg=="--expected":expected=Path(next(args))
        elif arg=="--out":output=Path(next(args))
        else:raise SystemExit(arg)
    result=make_receipt()
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if expected is not None:
        require(result==json.loads(expected.read_text()),"receipt drift")
    if output is not None:output.write_text(text)
    print(text,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())

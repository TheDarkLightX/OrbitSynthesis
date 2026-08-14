#!/usr/bin/env python3
"""Independent no-import reconstruction of the recursive Boolean compiler."""

from __future__ import annotations
import hashlib
import itertools
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

if hasattr(sys,"set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

SHIFTS=(-2,-1,0,1,2)

def must(ok:bool,label:str)->None:
    if not ok:raise AssertionError(label)

def c2(n:int)->int:return (n-1).bit_length()

def low3(n:int)->tuple[int,int]:
    p=1;e=0
    while p*3<=n:p*=3;e+=1
    return e,p

def decimal(n:int,d:int,k:int=18)->str:
    q,r=divmod(n,d);out=[]
    for _ in range(k):
        r*=10;x,r=divmod(r,d);out.append(str(x))
    return str(q)+"."+''.join(out)

@lru_cache(None)
def rail(w:int)->tuple[int,int,int]:
    if w==0:return 0,0,2
    if w==1:return 4,4,5
    a=(w+1)//2;b=w//2
    x,_,_=rail(a);y,z,_=rail(b)
    cross=3**a*(3**b-1)//2
    regular=x+y+3**w+cross
    extended=x+z+2*3**w-3**(w-1)+cross
    vector=2+x+z+cross+3**w-(3**(w-1)+1)//2
    return regular,extended,vector

def V(w:int)->int:return rail(w)[2]
def VD(w:int)->int:return 2 if w==0 else 3+c2(w)

@lru_cache(None)
def binpart(r:int)->tuple[int,int,int]:
    k=math.isqrt(r);q=3**k;chunk=q.bit_length()-1
    left=r-1;widths=[]
    if left%chunk:widths.append(left%chunk)
    widths += [chunk]*(left//chunk)
    live=1;routers=controls=0
    for width in widths:
        routers+=live;controls+=6*q*(2**width-1);live*=2**width
    must(live==2**(r-1),"binary leaves")
    return routers*((3*q-1)//2),controls,(k+1)*len(widths)+2*chunk+1

@lru_cache(None)
def base(r:int)->tuple[int,int]:
    j=(3**r//(9*r**3)).bit_length()-1
    t,_=low3(r*j)
    return j,t

def option(r:int,shift:int)->dict[str,int]:
    j,t0=base(r);t=t0+shift
    must(1<=t<r,"width")
    n=3**t;groups=(n+j-1)//j
    small,large=divmod(n,groups)
    maxrow=small+(1 if large else 0)
    must(maxrow<=j,"row cap")
    sum_tables=large*2**(small+1)+(groups-large)*2**small
    local=4*t*sum_tables+5*t
    s=r-t;p=3**s
    prefix=groups*(3*p-1)
    vectors=V(t)+V(s)-2
    selector=3*n-1
    br,bc,bd=binpart(r)
    total=local+prefix+vectors+selector+(2*r-1)+6+br+bc
    C=c2(r);A=C+2
    local_d=A+2*t+3
    prefix_d=max(local_d,A+VD(s))+s+1
    select_d=max(prefix_d,A+VD(t))+t+1
    depth=max(A+4,bd+2,select_d+4)
    return {"shift":shift,"J":j,"T":t0,"t":t,"N":n,"groups":groups,
            "small":small,"large":large,"maxrow":maxrow,
            "sum_tables":sum_tables,"local":local,"s":s,"P":p,
            "prefix":prefix,"vectors":vectors,"selector":selector,
            "binary_router":br,"binary_control":bc,
            "total":total,"depth":depth}

def best(r:int)->tuple[dict[str,int],dict[int,dict[str,int]]]:
    options={s:option(r,s) for s in SHIFTS}
    chosen=min(options.values(),key=lambda x:(x["total"],x["shift"]))
    return chosen,options

def recursive_semantics()->dict[str,object]:
    universe=list(itertools.product(range(3),repeat=2))
    subset_count=0;table_count=0;eval_count=0
    def cost(points,level):
        if not points or level==2:return 0
        kids=[[p for p in points if p[level]==d] for d in range(3)]
        return 4*2**len(points)+sum(cost(tuple(k),level+1) for k in kids)
    def evaluate(points,table,target,level):
        if not points:return 0
        if level==2:return table.get(target,0)
        kid=tuple(p for p in points if p[level]==target[level])
        return evaluate(kid,table,target,level+1)
    cost_digest=[]
    for mask in range(1<<len(universe)):
        points=tuple(p for i,p in enumerate(universe) if (mask>>i)&1)
        subset_count+=1
        value=cost(points,0)
        must(value<=8*2**len(points),"cost bound")
        cost_digest.append(f"{mask}:{value}")
        for bits in itertools.product((0,1),repeat=len(points)):
            table=dict(zip(points,bits));table_count+=1
            for target in universe:
                must(evaluate(points,table,target,0)==table.get(target,0),
                     "recursive semantics")
                eval_count+=1
    return {"subsets":subset_count,"tables":table_count,
            "evaluations":eval_count,
            "cost_digest":hashlib.sha256('\n'.join(cost_digest).encode()).hexdigest(),
            "bound":"4*t*2^M"}

def plane_semantics()->dict[str,object]:
    counts={};rows=0
    for n in range(7):
        observed=set()
        for table in itertools.product(range(3),repeat=n):
            hi=tuple(int(x==2) for x in table)
            lo=tuple(int(x==1) for x in table)
            rebuilt=tuple(2 if hi[i] else (1 if lo[i] else 0)
                          for i in range(n))
            must(rebuilt==table,"plane")
            observed|={hi,lo};rows+=n
        must(len(observed)==2**n,"plane count")
        counts[str(n)]=len(observed)
    return {"rows":rows,"counts":counts}

def bases()->dict[str,object]:
    rows=[]
    for r in (340,341):
        e=math.ceil(3*r/2)
        must(9*r**3*2**e<=3**r,"J base")
        rows.append([r,e])
    must(8*342**3<9*340**3,"J step")
    must(33000*340**3<3**340,"fixed")
    must(5000*65<3**32,"prefix")
    must(192*2**64<3**50,"router")
    must(24*64**2<3**42,"control")
    numerator=(2*9*340*36*340*1000+26*36*340*1000+
               (3*340+1)*9*340*1000+4*9*340*36*340)
    denominator=9*340*36*340*1000
    must(25*numerator<62*denominator,"tail")
    return {"J_rows":rows,"J_step":"8*342^3<9*340^3",
            "tail":[numerator,denominator],"target":"62/25"}

def arithmetic()->dict[str,object]:
    maximum=(-1,1,-1);finite=(-1,1,-1)
    hist={s:0 for s in SHIFTS};selected=[]
    for r in range(64,16385):
        row,options=best(r);hist[row["shift"]]+=1
        U=3**r;num=row["total"]*r
        must(25*num<62*U,"size")
        C=c2(r);depth_bound=r+C+2*math.ceil((4*C+2)/3)+15
        must(row["depth"]<=depth_bound,"depth")
        if num*maximum[1]>maximum[0]*U:maximum=(num,U,r)
        if r<=339 and num*finite[1]>finite[0]*U:finite=(num,U,r)
        if r>=340:
            j,t0=base(r)
            delta=0 if 3**t0==r*j else 1
            tail=options[delta]
            must(2*j>=3*r,"J/r")
            must(tail["N"]>=r*j and tail["N"]<3*r*j,"N range")
            must(tail["groups"]<3*r+1,"groups")
            must(tail["t"]<=2*C,"t")
            skeleton=tail["local"]-5*tail["t"]
            must(9*skeleton*r**3<=4*tail["t"]*(3*r+1)*U,"local")
            must(32*C<=r,"C/r")
            must(1000*5*3**((tail["s"]+1)//2)*r<U,"prefix error")
            fixed=5*tail["t"]+V(tail["t"])+tail["selector"]+(2*r-1)+6
            must(1000*fixed*r<U,"fixed")
            must(1000*tail["binary_router"]*r<U,"binary router")
            must(1000*tail["binary_control"]*r<U,"binary control")
            must((9*tail["groups"]+4)*tail["P"]*r*j
                 <=(9*r+13)*U,"prefix main")
        if r in (64,65,66,100,339,340,1000,4096,16384):
            selected.append({"r":r,"shift":row["shift"],"t":row["t"],
                             "groups":row["groups"],"ratio":decimal(num,U),
                             "depth":row["depth"],"bound":depth_bound})
    must(maximum[2]==64,"maximum")
    must(finite[2]==64,"finite maximum")
    return {"range":[64,16384],"histogram":{str(k):v for k,v in hist.items()},
            "maximum":{"r":maximum[2],"ratio":decimal(maximum[0],maximum[1])},
            "finite":{"range":[64,339],"r":finite[2],
                      "ratio":decimal(finite[0],finite[1])},
            "selected":selected,
            "theorem":{"size":"25*size*r<62*3^r",
                       "depth":"r+C+2*ceil((4C+2)/3)+15"}}

def receipt()->dict[str,object]:
    result={"schema":"orbit-synthesis/recursive-boolean-independent/v1",
            "planes":plane_semantics(),"recursive":recursive_semantics(),
            "bases":bases(),"arithmetic":arithmetic()}
    raw=json.dumps(result,sort_keys=True,separators=(",",":"))
    result["semantic_sha256"]=hashlib.sha256(raw.encode()).hexdigest()
    return result

def main()->int:
    expected=output=None;args=iter(sys.argv[1:])
    for arg in args:
        if arg=="--expected":expected=Path(next(args))
        elif arg=="--out":output=Path(next(args))
        else:raise SystemExit(arg)
    data=receipt();text=json.dumps(data,indent=2,sort_keys=True)+"\n"
    if expected is not None:
        must(data==json.loads(expected.read_text()),"receipt")
    if output is not None:output.write_text(text)
    print(text,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())

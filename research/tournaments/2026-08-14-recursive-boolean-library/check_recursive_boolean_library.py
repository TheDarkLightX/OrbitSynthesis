#!/usr/bin/env python3
"""Standalone audit for the recursive Boolean-library fixed-Q compiler."""

from __future__ import annotations
import hashlib
import itertools
import json
import math
import random
import sys
from functools import cache
from pathlib import Path

if hasattr(sys,"set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

Q=(0,1,2)
B=(0,1)
DELTAS=(-2,-1,0,1,2)

def require(ok:bool,message:str)->None:
    if not ok:raise RuntimeError(message)

def clog2(n:int)->int:
    require(n>=1,"clog2")
    return (n-1).bit_length()

def floor3(n:int)->tuple[int,int]:
    require(n>=1,"floor3")
    p=1;e=0
    while 3*p<=n:p*=3;e+=1
    return e,p

def decimal(n:int,d:int,digits:int=18)->str:
    q,r=divmod(n,d);out=[]
    for _ in range(digits):
        r*=10;x,r=divmod(r,d);out.append(str(x))
    return f"{q}."+''.join(out)

def code(v:int)->tuple[int,int]:
    return ((0,0),(0,1),(1,0))[v]

def plane_audit()->dict[str,object]:
    rows=0;counts={}
    for width in range(0,7):
        expected=set(itertools.product(B,repeat=width));seen=set()
        for table in itertools.product(Q,repeat=width):
            high=tuple(code(v)[0] for v in table)
            low=tuple(code(v)[1] for v in table)
            rebuilt=tuple(2 if high[i] else (1 if low[i] else 0)
                          for i in range(width))
            require(rebuilt==table,"plane reconstruction")
            seen.add(high);seen.add(low);rows+=width
        require(seen==expected,"plane saturation")
        counts[str(width)]=len(seen)
    return {"rows":rows,"boolean_counts":counts}

def recursive_cost(points:tuple[tuple[int,...],...],level:int,width:int)->int:
    if not points or level==width:return 0
    children=[
        tuple(point for point in points if point[level]==digit)
        for digit in Q
    ]
    return 4*2**len(points)+sum(
        recursive_cost(child,level+1,width) for child in children
    )

def recursive_value(points:tuple[tuple[int,...],...],
                    values:dict[tuple[int,...],int],
                    target:tuple[int,...],level:int,width:int)->int:
    if not points:return 0
    if level==width:return values.get(target,0)
    child=tuple(point for point in points if point[level]==target[level])
    return recursive_value(child,values,target,level+1,width)

def recursive_library_audit()->dict[str,object]:
    universe=list(itertools.product(Q,repeat=2))
    subsets=0;functions=0;evaluations=0
    for mask in range(1<<len(universe)):
        points=tuple(
            point for index,point in enumerate(universe) if (mask>>index)&1
        )
        subsets+=1
        cost=recursive_cost(points,0,2)
        bound=4*2*2**len(points)
        require(cost<=bound,"recursive cost bound")
        for bits in itertools.product(B,repeat=len(points)):
            table=dict(zip(points,bits));functions+=1
            for target in universe:
                got=recursive_value(points,table,target,0,2)
                expected=table.get(target,0)
                require(got==expected,"recursive semantic mismatch")
                evaluations+=1
    rng=random.Random(0xB00B1E)
    width3=list(itertools.product(Q,repeat=3))
    width3_rows=[]
    for seed in range(64):
        points=tuple(point for point in width3 if rng.randrange(2))
        cost=recursive_cost(points,0,3)
        bound=4*3*2**len(points)
        require(cost<=bound,"width-three cost")
        width3_rows.append([seed,len(points),cost,bound])
    witness=None
    points=((0,0),(1,2))
    values={(0,0):1,(1,2):0}
    for target in itertools.product(Q,repeat=2):
        wrong=(target[0]+1)%3
        child=tuple(point for point in points if point[0]==wrong)
        bad=recursive_value(child,values,target,1,2)
        expected=values.get(target,0)
        if bad!=expected:
            witness={"target":list(target),"wrong_digit":wrong,
                     "mutated":bad,"expected":expected}
            break
    require(witness is not None,"recursive mutation")
    return {"exhaustive_width":2,"subsets":subsets,"functions":functions,
            "evaluations":evaluations,"width3_rows":width3_rows,
            "mutation_wrong_branch":witness,
            "cost_bound":"L(S)<=4*t*2^|S|"}

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
    left=r-1;sizes=([left%w] if left%w else [])+[w]*(left//w)
    live=1;instances=controls=0
    for width in sizes:
        instances+=live;controls+=6*q*(2**width-1);live*=2**width
    require(live==2**(r-1),"binary leaves")
    return {"router":((3*q-1)//2)*instances,"control":controls,
            "depth":(k+1)*len(sizes)+2*w+1}

@cache
def budget(r:int)->tuple[int,int,int]:
    J=(3**r//(9*r**3)).bit_length()-1
    T,_=floor3(r*J)
    return J,T,r*J

def candidate(r:int,delta:int)->dict[str,object]:
    J,T,_=budget(r)
    t=T+delta
    require(1<=t<r,"local width")
    N=3**t
    g=(N+J-1)//J
    q,rem=divmod(N,g)
    max_rows=q+(1 if rem else 0)
    require(max_rows<=J,"row budget")
    table_sum=rem*2**(q+1)+(g-rem)*2**q
    local=4*t*table_sum+5*t
    s=r-t;P=3**s
    prefix=g*(3*P-1)
    vectors=vector(t)+vector(s)-2
    group_selector=3*N-1
    anchor=2*r-1
    br=binary(r)
    total=(local+prefix+vectors+group_selector+anchor+6+
           br["router"]+br["control"])
    C=clog2(r);A=C+2
    local_depth=A+2*t+3
    prefix_depth=max(local_depth,A+vdepth(s))+s+1
    group_depth=max(prefix_depth,A+vdepth(t))+t+1
    depth=max(A+4,br["depth"]+2,group_depth+4)
    return {"delta":delta,"J":J,"T":T,"t":t,"N":N,"g":g,
            "row_quotient":q,"row_remainder":rem,"max_rows":max_rows,
            "table_sum":table_sum,"local":local,"s":s,"P":P,
            "prefix":prefix,"vectors":vectors,
            "group_selector":group_selector,"anchor":anchor,
            "binary_router":br["router"],"binary_control":br["control"],
            "total":total,"depth":depth}

def select(r:int)->tuple[dict[str,object],dict[int,dict[str,object]]]:
    rows={d:candidate(r,d) for d in DELTAS}
    best=min(rows.values(),key=lambda row:(row["total"],row["delta"]))
    return best,rows

def analytic_tail()->dict[str,object]:
    bases=[]
    for r in (340,341):
        exponent=math.ceil(3*r/2)
        require(9*r**3*2**exponent<=3**r,"J base")
        bases.append([r,exponent])
    require(8*342**3<9*340**3,"J two-step ratio")
    require(9<=340//32,"C/r base")
    require(33000*340**3<3**340,"fixed group base")
    require(5000*65<3**32,"prefix error")
    require(192*2**64<3**50,"binary router")
    require(24*64**2<3**42,"binary control")
    numerator=(2*9*340*36*340*1000
               +26*36*340*1000
               +(3*340+1)*9*340*1000
               +4*9*340*36*340)
    denominator=9*340*36*340*1000
    require(25*numerator<62*denominator,"tail rational")
    return {"J_bases":bases,"J_step":"8*342^3<9*340^3",
            "J_bound":"J>=3r/2",
            "local_bound":"8C(3r+1)/(9r^2)",
            "prefix_bound":"2+26/(9r)",
            "lower_order":"4/1000",
            "tail_start":340,"target":"62/25",
            "tail_fraction":[numerator,denominator]}

def ledger()->dict[str,object]:
    maximum=(-1,1,-1);finite=(-1,1,-1)
    choices={d:0 for d in DELTAS};selected=[]
    min_depth=(10**9,-1)
    for r in range(64,16385):
        row,rows=select(r);choices[row["delta"]]+=1
        unit=3**r;num=row["total"]*r
        require(25*num<62*unit,"62/25 size")
        C=clog2(r)
        depth_bound=r+C+2*math.ceil((4*C+2)/3)+15
        require(row["depth"]<=depth_bound,"depth")
        slack=depth_bound-row["depth"]
        if slack<min_depth[0]:min_depth=(slack,r)
        if num*maximum[1]>maximum[0]*unit:maximum=(num,unit,r)
        if r<=339 and num*finite[1]>finite[0]*unit:finite=(num,unit,r)
        if r>=340:
            J=row["J"]
            require(2*J>=3*r,"J/r")
            ceil_delta=0 if 3**row["T"]==r*J else 1
            tail=rows[ceil_delta]
            require(tail["N"]>=r*J and tail["N"]<3*r*J,"N interval")
            require(tail["g"]<3*r+1,"group count")
            C=clog2(r)
            require(tail["t"]<=2*C,"t bound")
            skeleton=tail["local"]-5*tail["t"]
            require(9*skeleton*r**3
                    <=4*tail["t"]*(3*r+1)*unit,"local analytic")
            require(32*C<=r,"C/r analytic")
            require(1000*5*3**((tail["s"]+1)//2)*r<unit,
                    "prefix error analytic")
            fixed=(5*tail["t"]+vector(tail["t"])
                   +tail["group_selector"]+tail["anchor"]+6)
            require(1000*fixed*r<unit,"fixed analytic")
            require(1000*tail["binary_router"]*r<unit,"binary router analytic")
            require(1000*tail["binary_control"]*r<unit,"binary control analytic")
            require((9*tail["g"]+4)*tail["P"]*r*J
                    <=(9*r+13)*unit,"prefix main analytic")
        if r in (64,65,66,67,100,128,339,340,500,1000,4096,16384):
            selected.append({"r":r,"delta":row["delta"],"J":row["J"],
                             "T":row["T"],"t":row["t"],"g":row["g"],
                             "max_rows":row["max_rows"],
                             "size_ratio":decimal(num,unit),
                             "depth":row["depth"],"depth_bound":depth_bound})
    require(maximum[2]==64,"maximum")
    require(finite[2]==64,"finite maximum")
    return {"range":[64,16384],"deltas":list(DELTAS),
            "choice_histogram":{str(k):v for k,v in choices.items()},
            "size_bound":"25*size*r<62*3^r",
            "depth_bound":"r+C+2*ceil((4C+2)/3)+15",
            "maximum":{"r":maximum[2],"ratio":decimal(maximum[0],maximum[1])},
            "finite":{"range":[64,339],"maximum_r":finite[2],
                      "maximum_ratio":decimal(finite[0],finite[1])},
            "minimum_depth_slack":{"r":min_depth[1],"value":min_depth[0]},
            "selected":selected}

def make_receipt()->dict[str,object]:
    result={"schema":"orbit-synthesis/recursive-boolean-library/v1",
            "planes":plane_audit(),"recursive_library":recursive_library_audit(),
            "analytic_tail":analytic_tail(),"ledger":ledger()}
    raw=json.dumps(result,sort_keys=True,separators=(",",":"))
    result["semantic_sha256"]=hashlib.sha256(raw.encode()).hexdigest()
    return result

def main()->int:
    expected=output=None;args=iter(sys.argv[1:])
    for arg in args:
        if arg=="--expected":expected=Path(next(args))
        elif arg=="--out":output=Path(next(args))
        else:raise SystemExit(arg)
    data=make_receipt();text=json.dumps(data,indent=2,sort_keys=True)+"\n"
    if expected is not None:
        require(data==json.loads(expected.read_text()),"receipt drift")
    if output is not None:output.write_text(text)
    print(text,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())

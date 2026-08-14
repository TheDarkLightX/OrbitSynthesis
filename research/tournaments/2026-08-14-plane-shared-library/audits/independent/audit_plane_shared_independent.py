#!/usr/bin/env python3
"""Independent no-import audit of the portfolio plane-shared compiler."""

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

CHOICES=(2,3,4,5)

def check(ok:bool,label:str)->None:
    if not ok: raise AssertionError(label)

def log2ceil(n:int)->int:
    check(n>0,"log domain")
    return (n-1).bit_length()

def pow3floor(n:int)->tuple[int,int]:
    p=1;e=0
    while 3*p<=n:p*=3;e+=1
    return e,p

def dec(n:int,d:int,k:int=18)->str:
    q,r=divmod(n,d);digits=[]
    for _ in range(k):
        r*=10;x,r=divmod(r,d);digits.append(str(x))
    return str(q)+"."+''.join(digits)

@lru_cache(None)
def rails(w:int)->tuple[int,int,int]:
    if w==0:return 0,0,2
    if w==1:return 4,4,5
    a=(w+1)//2;b=w//2
    ra,_,_=rails(a);rb,eb,_=rails(b)
    cross=3**a*(3**b-1)//2
    regular=ra+rb+3**w+cross
    ext=ra+eb+2*3**w-3**(w-1)+cross
    vec=2+ra+eb+cross+3**w-(3**(w-1)+1)//2
    return regular,ext,vec

def vnodes(w:int)->int:return rails(w)[2]
def vheight(w:int)->int:return 2 if w==0 else 3+log2ceil(w)

@lru_cache(None)
def binary(r:int)->tuple[int,int,int]:
    k=math.isqrt(r);q=3**k;w=q.bit_length()-1
    left=r-1;sizes=[]
    if left%w:sizes.append(left%w)
    sizes.extend([w]*(left//w))
    live=1;instances=controls=0
    for width in sizes:
        instances+=live;controls+=6*q*(2**width-1);live*=2**width
    check(live==2**(r-1),"binary leaves")
    return ((3*q-1)//2*instances,controls,(k+1)*len(sizes)+2*w+1)

@lru_cache(None)
def budget(r:int)->tuple[int,int,int,int]:
    j=(3**r//(9*r**3)).bit_length()-1
    k=j-3;b,m=pow3floor(k)
    return j,k,b,m

def build_candidate(r:int,offset:int)->dict[str,int]:
    j,k,b,m=budget(r)
    t=b+offset
    d=min(7,t)
    unit=3**(t-d)
    per_group=k//unit
    check(per_group>0,"group capacity")
    words=3**d
    groups=(words+per_group-1)//per_group
    small,large=divmod(words,groups)
    maxrows=(small+(1 if large else 0))*unit
    check(maxrows<=k,"row bound")
    table_sum=(large*2**((small+1)*unit)
               +(groups-large)*2**(small*unit))
    n=3**t
    local=((3*n-1)//2)*table_sum
    s=r-t;p=3**s
    prefix=groups*(3*p-1)
    vectors=vnodes(t)+vnodes(s)+vnodes(d)-4
    group_mux=3*3**d-1
    br,bc,bd=binary(r)
    total=local+prefix+vectors+group_mux+(2*r-1)+6+br+bc
    c=log2ceil(r);anchor=c+2
    local_depth=anchor+vheight(t)+t+1
    prefix_depth=max(local_depth,anchor+vheight(s))+s+1
    group_depth=max(prefix_depth,anchor+vheight(d))+d+1
    depth=max(anchor+4,bd+2,group_depth+4)
    return {"offset":offset,"J":j,"K":k,"b":b,"m":m,"t":t,"d":d,
            "unit":unit,"per_group":per_group,"groups":groups,
            "small":small,"large":large,"maxrows":maxrows,
            "local":local,"prefix":prefix,"vectors":vectors,
            "group_mux":group_mux,"binary_router":br,"binary_control":bc,
            "total":total,"depth":depth,"s":s,"P":p}

def choose(r:int)->tuple[dict[str,int],dict[int,dict[str,int]]]:
    rows={x:build_candidate(r,x) for x in CHOICES}
    best=min(rows.values(),key=lambda x:(x["total"],x["offset"]))
    return best,rows

def planes()->dict[str,object]:
    rows=0;counts={}
    for width in range(0,7):
        expected=set(itertools.product((0,1),repeat=width))
        observed=set()
        for table in itertools.product((0,1,2),repeat=width):
            high=tuple(int(v==2) for v in table)
            low=tuple(int(v==1) for v in table)
            rebuilt=tuple(2 if high[i] else (1 if low[i] else 0)
                          for i in range(width))
            check(rebuilt==table,"plane rebuild")
            observed.add(high);observed.add(low);rows+=width
        check(observed==expected,"plane saturation")
        counts[str(width)]=len(observed)
    bad=tuple(2 if x else 0 for x in (0,1))
    check(bad!=(0,1),"plane mutation")
    return {"rows":rows,"boolean_counts":counts,
            "mutation_low_as_high":list(bad)}

def proof_bases()->dict[str,object]:
    bases=[]
    for r in (107,108,109):
        exponent=math.ceil(4*r/3)+3
        check(9*r**3*2**exponent<=3**r,"K base")
        bases.append([r,exponent])
    check(16*110**3<27*107**3,"K step")
    table=[];winner=(-1,None,None)
    for h in range(27,81):
        g=(2187+h-1)//h
        value=(9*g+4)*(h+1)
        table.append([h,g,value,8748])
        if value>winner[0]:winner=(value,h,g)
    check(winner==(20935,78,29),"discrete maximum")
    lhs=(20935*8*967*1000+2187*8748*1000+4*8748*8*967)
    den=8748*8*967*1000
    check(25*lhs<67*den,"tail total")
    for ok,name in [
        (5000*65<3**32,"prefix"),
        (900000*967**2<3**967,"fixed"),
        (192*2**64<3**50,"binary router"),
        (24*64**2<3**42,"binary control")]:
        check(ok,name)
    return {"K_bases":bases,"K_step":"16*110^3<27*107^3",
            "table":table,"winner":{"h":78,"g":29,"value":"20935/8748"},
            "tail":[lhs,den],"target":"67/25"}

def arithmetic()->dict[str,object]:
    maximum=(-1,1,-1);finite=(-1,1,-1);counts={x:0 for x in CHOICES}
    selected=[]
    for r in range(64,16385):
        row,allrows=choose(r);counts[row["offset"]]+=1
        universe=3**r;num=row["total"]*r
        check(25*num<67*universe,"global size")
        c=log2ceil(r);db=r+math.ceil(7*c/5)+20
        check(row["depth"]<=db,"global depth")
        if num*maximum[1]>maximum[0]*universe:maximum=(num,universe,r)
        if r<=966 and num*finite[1]>finite[0]*universe:
            finite=(num,universe,r)
        if r>=967:
            tail=allrows[4]
            check(3*tail["K"]>=4*r,"K/r")
            check(27<=tail["per_group"]<=80,"h")
            check(8*tail["local"]*r*r<2187*universe,"local")
            check(1000*5*3**((tail["s"]+1)//2)*r<universe,
                  "prefix error")
            fixed=(tail["vectors"]-vnodes(tail["s"])
                   +tail["group_mux"]+(2*r-1)+6)
            check(1000*fixed*r<universe,"fixed")
            check(1000*tail["binary_router"]*r<universe,"binary router")
            check(1000*tail["binary_control"]*r<universe,"binary control")
            check((9*tail["groups"]+4)*r*8748
                  <=20935*243*tail["m"],"prefix main")
        if r in (64,66,67,107,966,967,4096,16384):
            selected.append({"r":r,"offset":row["offset"],"t":row["t"],
                             "d":row["d"],"groups":row["groups"],
                             "ratio":dec(num,universe),
                             "depth":row["depth"],"depth_bound":db})
    check(maximum[2]==64,"maximum")
    check(finite[2]==64,"finite maximum")
    return {"range":[64,16384],"offset_counts":{str(k):v for k,v in counts.items()},
            "maximum":{"r":maximum[2],"ratio":dec(maximum[0],maximum[1])},
            "finite":{"range":[64,966],"maximum_r":finite[2],
                      "ratio":dec(finite[0],finite[1])},
            "selected":selected,
            "theorem":{"size":"25*size*r<67*3^r",
                       "depth":"r+ceil(7*ceil(log2 r)/5)+20"}}

def receipt()->dict[str,object]:
    result={"schema":"orbit-synthesis/plane-shared-portfolio-independent/v1",
            "planes":planes(),"bases":proof_bases(),"arithmetic":arithmetic()}
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
        check(data==json.loads(expected.read_text()),"receipt mismatch")
    if output is not None:output.write_text(text)
    print(text,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())

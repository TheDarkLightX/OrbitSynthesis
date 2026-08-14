#!/usr/bin/env python3
"""Independent audit of exact balanced-group optimization."""
from __future__ import annotations
import hashlib,itertools,json,math,sys
from functools import lru_cache
from pathlib import Path
if hasattr(sys,'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
SHIFTS=(-2,-1,0,1,2)
def need(x,m):
    if not x: raise AssertionError(m)
def C2(n): return (n-1).bit_length()
def p3(n):
    p=1;e=0
    while 3*p<=n:p*=3;e+=1
    return e,p
def dec(n,d,k=18):
    q,r=divmod(n,d);s=[]
    for _ in range(k):r*=10;x,r=divmod(r,d);s.append(str(x))
    return str(q)+'.'+''.join(s)
@lru_cache(None)
def rails(w):
    if w==0:return (0,0,2)
    if w==1:return (4,4,5)
    a=(w+1)//2;b=w//2
    ra,_,_=rails(a);rb,eb,_=rails(b);x=3**a*(3**b-1)//2
    R=ra+rb+3**w+x;E=ra+eb+2*3**w-3**(w-1)+x
    V=2+ra+eb+x+3**w-(3**(w-1)+1)//2
    return R,E,V
def V(w):return rails(w)[2]
def VD(w):return 2 if w==0 else 3+C2(w)
@lru_cache(None)
def binary(r):
    k=math.isqrt(r);q=3**k;w=q.bit_length()-1;n=r-1
    sizes=([n%w] if n%w else [])+[w]*(n//w)
    live=1;inst=ctrl=0
    for z in sizes:inst+=live;ctrl+=6*q*(2**z-1);live*=2**z
    need(live==2**(r-1),'binary')
    return ((3*q-1)//2*inst,ctrl,(k+1)*len(sizes)+2*w+1)
@lru_cache(None)
def base(r):
    J=(3**r//(9*r**3)).bit_length()-1;T,_=p3(r*J);return J,T
def fvalue(N,t,P,g):
    q,rem=divmod(N,g);E=(g+rem)*2**q
    return 4*t*E+5*t+g*(3*P-1),E,q,rem
def endpoints(N,t,P):
    best=None;intervals=0;g=1
    while g<=N:
        q=N//g;right=N//q;intervals+=1
        for h in ((g,) if g==right else (g,right)):
            val,E,q2,rem=fvalue(N,t,P,h);need(q2==q,'interval')
            key=(val,h)
            if best is None or key<best[0]:best=(key,E,q,rem)
        g=right+1
    (val,g),E,q,rem=best
    return {'value':val,'g':g,'E':E,'q':q,'rem':rem,
            'maxrow':q+(1 if rem else 0),'intervals':intervals}
def optimizer_semantics():
    cases=0
    for N in range(1,181):
      for t in range(1,5):
       for P in (1,3,9,27):
        got=endpoints(N,t,P)
        brute=min((fvalue(N,t,P,g)[0],g) for g in range(1,N+1))
        need((got['value'],got['g'])==brute,'endpoint optimizer');cases+=1
    return {'bruteforce_cases':cases,
            'affine_identity':'F(g)=4tN2^q+g[(3P-1)-4t(q-1)2^q]+5t',
            'intervals':'floor(N/g)=q'}
def option(r,shift,optimize):
    J,T=base(r);t=T+shift;need(1<=t<r,'t')
    N=3**t;s=r-t;P=3**s
    if optimize:o=endpoints(N,t,P)
    else:
        g=(N+J-1)//J;val,E,q,rem=fvalue(N,t,P,g)
        o={'value':val,'g':g,'E':E,'q':q,'rem':rem,
           'maxrow':q+(1 if rem else 0),'intervals':0}
    local=4*t*o['E']+5*t;prefix=o['g']*(3*P-1);need(local+prefix==o['value'],'decomp')
    br,bc,bd=binary(r);selector=3*N-1
    total=local+prefix+V(t)+V(s)-2+selector+(2*r-1)+6+br+bc
    C=C2(r);A=C+2;ld=A+2*t+3;pd=max(ld,A+VD(s))+s+1;sd=max(pd,A+VD(t))+t+1
    depth=max(A+4,bd+2,sd+4)
    return {'shift':shift,'J':J,'T':T,'t':t,'N':N,'s':s,'P':P,
            **o,'local':local,'prefix':prefix,'selector':selector,
            'br':br,'bc':bc,'total':total,'depth':depth}
def choose(r):
    rows={s:option(r,s,True) for s in SHIFTS}
    return min(rows.values(),key=lambda x:(x['total'],x['shift'],x['g']))
def bases():
    rows=[]
    for r in (340,341):
        e=math.ceil(3*r/2);need(9*r**3*2**e<=3**r,'J base');rows.append([r,e])
    need(8*342**3<9*340**3,'J step')
    num=(2*9*340*36*340*1000+26*36*340*1000+(3*340+1)*9*340*1000+4*9*340*36*340)
    den=9*340*36*340*1000;need(50*num<123*den,'tail')
    return {'J_rows':rows,'J_step':'8*342^3<9*340^3','tail':[num,den],'target':'123/50'}
def audit():
    maximum=(-1,1,-1);finite=(-1,1,-1);hist={s:0 for s in SHIFTS};selected=[]
    for r in range(64,16385):
        if r<=339:row=choose(r)
        else:
            J,T=base(r);shift=0 if 3**T==r*J else 1;row=option(r,shift,False)
        hist[row['shift']]+=1;U=3**r;num=row['total']*r;need(50*num<123*U,'size')
        C=C2(r);bound=r+C+2*math.ceil((4*C+2)/3)+15;need(row['depth']<=bound,'depth')
        if num*maximum[1]>maximum[0]*U:maximum=(num,U,r)
        if r<=339 and num*finite[1]>finite[0]*U:finite=(num,U,r)
        if r>=340:
            J=row['J'];need(2*J>=3*r,'J/r');need(row['N']>=r*J and row['N']<3*r*J,'N')
            need(row['g']<3*r+1,'g');skeleton=row['local']-5*row['t']
            need(9*skeleton*r**3<=4*row['t']*(3*r+1)*U,'local');need(32*C<=r,'C/r')
            need(1000*5*3**((row['s']+1)//2)*r<U,'error')
            fixed=5*row['t']+V(row['t'])+row['selector']+(2*r-1)+6
            need(1000*fixed*r<U,'fixed');need(1000*row['br']*r<U,'br');need(1000*row['bc']*r<U,'bc')
            need((9*row['g']+4)*row['P']*r*J<=(9*r+13)*U,'prefix')
        if r in (64,65,66,67,100,339,340,1000,4096,16384):
            selected.append({'r':r,'shift':row['shift'],'t':row['t'],'g':row['g'],
                             'maxrow':row['maxrow'],'ratio':dec(num,U),
                             'depth':row['depth'],'bound':bound})
    need(maximum[2]==65,'maximum');need(finite[2]==65,'finite maximum')
    return {'range':[64,16384],'finite_optimizer':[64,339],
            'tail':'scheduled ceil(log_3(rJ)) candidate','histogram':{str(k):v for k,v in hist.items()},
            'maximum':{'r':maximum[2],'ratio':dec(maximum[0],maximum[1])},
            'finite':{'r':finite[2],'ratio':dec(finite[0],finite[1])},
            'selected':selected,'theorem':{'size':'50*size*r<123*3^r',
            'depth':'r+C+2*ceil((4C+2)/3)+15'}}
def receipt():
    out={'schema':'orbit-synthesis/optimal-grouping-independent/v1',
         'optimizer':optimizer_semantics(),'bases':bases(),'arithmetic':audit()}
    raw=json.dumps(out,sort_keys=True,separators=(',',':'));out['semantic_sha256']=hashlib.sha256(raw.encode()).hexdigest();return out
def main():
    expected=output=None;args=iter(sys.argv[1:])
    for a in args:
        if a=='--expected':expected=Path(next(args))
        elif a=='--out':output=Path(next(args))
        else:raise SystemExit(a)
    x=receipt();text=json.dumps(x,indent=2,sort_keys=True)+'\n'
    if expected:need(x==json.loads(expected.read_text()),'receipt')
    if output:output.write_text(text)
    print(text,end='')
if __name__=='__main__':main()

"""Independent mathematical model for the native find-first signed router."""
from __future__ import annotations

import itertools
from functools import lru_cache

Q = (0, 1, 2)
MODE = {"L": 0, "G": 1, "E": 2}


def req(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError(msg)


def d(x: int, y: int, z: int) -> int:
    return z if x == y else x


def u(x: int) -> int:
    return (1, 0, 1)[x]


def first_mode(t: tuple[int, ...], p: tuple[int, ...]) -> str:
    req(len(t) == len(p), "length mismatch")
    for a, b in zip(t, p, strict=True):
        if a != b:
            return "G" if (a, b) == (1, 2) else "L"
    return "E"


def gl_digit(x: int, p: int) -> tuple[int, int]:
    two = 2
    one = u(two)
    zero = u(one)
    not_one = u(x)
    gain_two = u(not_one)
    loss_zero = d(x, two, not_one)
    loss_two = u(loss_zero)
    return ((zero, loss_zero), (zero, not_one), (gain_two, loss_two))[p]


def gl_comp(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    ag, al = a
    bg, bl = b
    out = (d(ag, al,bg), d(al,ag,bl))
    req(out in ((0,0),(1,0),(0,1)), "invalid GL state")
    return out


def mode_digit(x: int, p: int) -> int:
    one = u(2)
    zero = u(one)
    m0 = d(zero,x,2)
    h1 = d(one,x,2)
    m1 = d(h1,one,zero)
    return (m0,m1,x)[p]


def mode_comp(a: int, b: int) -> int:
    return d(a,2,b)


def balanced_gl(t: tuple[int,...], p: tuple[int,...]) -> tuple[int,int]:
    if not t: return (0,0)
    if len(t) == 1: return gl_digit(t[0],p[0])
    c = len(t)//2
    return gl_comp(balanced_gl(t[:c],p[:c]), balanced_gl(t[c:],p[c:]))


def balanced_mode(t: tuple[int,...], p: tuple[int,...]) -> int:
    if not t: return 2
    if len(t) == 1: return mode_digit(t[0],p[0])
    c = len(t)//2
    return mode_comp(balanced_mode(t[:c],p[:c]), balanced_mode(t[c:],p[c:]))


def negative_leaf(root: int, p: tuple[int,...]) -> int:
    return root ^ (sum(x == 1 for x in p) & 1)


def frozen_pair(root: int, t: tuple[int,...], p: tuple[int,...]) -> tuple[int,int]:
    equal = int(t == p)
    gain = int(first_mode(t,p) == "G")
    return (gain,int(bool(equal or gain))) if negative_leaf(root,p) else (int(not bool(equal or gain)),gain)


def gl_pair(root: int, t: tuple[int,...], p: tuple[int,...]) -> tuple[int,int]:
    gain,loss = balanced_gl(t,p)
    return (gain,u(loss)) if negative_leaf(root,p) else (loss,gain)


def fused_bottom(root: int, t: tuple[int,...], p: tuple[int,...], x: int) -> int:
    payload = u(x) if negative_leaf(root,p) else x
    return d(balanced_mode(t,p),2,payload)


def expected_bottom(root: int, t: tuple[int,...], p: tuple[int,...], x: int) -> int:
    mode = first_mode(t,p)
    if mode == "L": return 0
    if mode == "G": return 1
    return u(x) if negative_leaf(root,p) else x


def child_mode(target: tuple[int,...] | None, constant: int | None, digit: int):
    if constant is not None: return None,constant
    req(target is not None and target, "missing target")
    if digit == target[0]: return target[1:],None
    return None,int((target[0],digit) == (1,2))


def eval_full_router(root: int, target: tuple[int,...], payloads: dict[tuple[int,...],int]) -> int:
    @lru_cache(None)
    def go(neg: int, current: tuple[int,...] | None, constant: int | None,
           prefix: tuple[int,...], left: int) -> int:
        if left == 0:
            mode = 2 if constant is None else constant
            req(constant is not None or current == (), "projection did not terminate")
            x = payloads[prefix]
            return d(mode,2,u(x) if neg else x)
        children = []
        for digit in Q:
            nxt,const = child_mode(current,constant,digit)
            children.append(go(neg ^ int(digit == 1),nxt,const,prefix+(digit,),left-1))
        return d(children[0],children[1],children[2])
    return go(root,target,None,(),len(target))


@lru_cache(None)
def gl_nodes(w: int) -> int:
    if w == 0: return 0
    if w == 1: return 4
    return gl_nodes(w//2)+gl_nodes((w+1)//2)+2*3**w


@lru_cache(None)
def mode_nodes(w: int) -> int:
    if w == 0: return 0
    if w == 1: return 3
    return mode_nodes(w//2)+mode_nodes((w+1)//2)+3**w


def neg_cells(root: int, w: int) -> int:
    even,odd = (3**w+1)//2,(3**w-1)//2
    return even if root else odd


def gl_vector(root: int, w: int) -> int:
    return 2+gl_nodes(w)+neg_cells(root,w)


def mode_vector(w: int) -> int:
    return 2+mode_nodes(w)


def skeleton(w: int) -> int:
    return (3**(w+1)-1)//2


def generic_router(root: int, w: int) -> int:
    return skeleton(w)+mode_vector(w)+neg_cells(root,w)


def closed_router(w: int) -> int:
    return skeleton(w)+mode_vector(w)


def clog2(n: int) -> int:
    return 0 if n <= 1 else (n-1).bit_length()


def ceil_log3(n: int) -> int:
    e,p = 0,1
    while p < n: e,p = e+1,3*p
    return e


def floor_log3(n: int) -> int:
    e,p = 0,1
    while 3*p <= n: e,p = e+1,3*p
    return e


def params(r: int) -> tuple[int,int,int,int,int]:
    reserve = 4+ceil_log3(r*r)
    headroom = r-reserve
    b = floor_log3(headroom)
    m = 3**b
    p = 3**(r-b)
    return reserve,headroom,m,b,p


def nonbinary_nodes(r: int) -> int:
    _,_,m,b,p = params(r)
    return (3*m-1)*3**m+mode_nodes(b)+(3*p-1)+mode_nodes(r-b)+4*r+7


def nonbinary_depth(r: int) -> int:
    _,_,_,b,_ = params(r)
    c = clog2(r)
    prefix = r-b
    local = 3*c+3+clog2(b)+b+1
    prefix_mode = 3*c+3+clog2(prefix)
    return max(local,prefix_mode)+prefix+1+4


def generated(state: frozenset[tuple[int,int,int]]) -> set[tuple[int,int,int]]:
    rows = list(state)
    out = {tuple(u(v) for v in row) for row in rows}
    for a,b,c in itertools.product(rows,repeat=3):
        out.add(tuple(d(a[i],b[i],c[i]) for i in range(3)))
    return out-set(state)


def minimum_roots(required: set[tuple[int,int,int]], limit: int) -> tuple[int,list[int]]:
    frontier = {frozenset(((0,1,2),(2,2,2)))}
    sizes = []
    for count in range(limit+1):
        sizes.append(len(frontier))
        if any(required <= state for state in frontier): return count,sizes
        frontier = {frozenset((*state,out)) for state in frontier for out in generated(state)}
    raise AssertionError("minimality target not reached")

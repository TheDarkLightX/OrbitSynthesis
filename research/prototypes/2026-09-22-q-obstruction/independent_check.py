"""Independent set/tuple oracle and proof checker; imports no solver code."""
from __future__ import annotations
import hashlib
import itertools
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Reference:
    def __init__(self, wire):
        need(set(wire)=={"schema","k","rows"},"game fields")
        need(wire["schema"]=="orbit-synthesis/q-obstruction-game/v1","game schema")
        k=wire["k"]
        need(type(k) is int and k>0,"arity")
        self.states=list(itertools.product((0,1,2),repeat=k))
        self.n=len(self.states); self.index={s:i for i,s in enumerate(self.states)}
        self.b={i for i,s in enumerate(self.states) if all(x<2 for x in s)}
        self.bar={i:self.index[tuple(1-x for x in self.states[i])] for i in self.b}
        need(type(wire["rows"]) is list and len(wire["rows"])==3*self.n,"row count")
        self.raw=[]
        for row in wire["rows"]:
            need(type(row) is list and all(type(t) is int and 0<=t<self.n for t in row),"row values")
            need(row==sorted(set(row)),"canonical row")
            self.raw.append(set(row))
        self.rows=[r & self.b if s in self.b and i<2 else set(r)
                   for s in range(self.n) for i,r in enumerate(self.raw[3*s:3*s+3])]
        self.wire=wire

    def unpack(self, value):
        need(type(value) is str,"mask type")
        try: mask=int(value,16)
        except ValueError: raise ValueError("mask syntax") from None
        need(mask>=0 and mask.bit_length()<=self.n and hex(mask)==value,"mask bounds/canonicalization")
        return {i for i in range(self.n) if mask>>i&1}

    def local(self, w):
        return {s for s in w if all(self.rows[3*s+i] & w for i in range(3))}

    def envelope(self,w):
        w=set(w)
        while True:
            nxt=self.local(w)
            if nxt==w: return w
            w=nxt

    def feasible(self, w):
        """Independent list-intersection oracle over observation-pair seeds."""
        if self.local(w)!=w: return False
        for s in sorted(self.b):
            t=self.bar[s]
            if s>t: continue
            for i in (0,1):
                seeds=set(self.b)
                if s in w: seeds &= self.rows[3*s+i] & w
                if t in w: seeds &= {self.bar[y] for y in self.rows[3*t+1-i] & w}
                if not seeds: return False
        return True

    def all_domains(self, allowed=None):
        candidates=sorted(self.envelope(set(range(self.n)) if allowed is None else set(allowed)))
        for choices in itertools.product((False,True), repeat=len(candidates)):
            w={s for s,yes in zip(candidates,choices) if yes}
            if self.feasible(w): yield w

    def strategy(self, w, table):
        need(type(table) is list and len(table)==3*self.n,"strategy size")
        need(all(type(y) is int and 0<=y<self.n for y in table),"strategy values")
        for s in range(self.n):
            for i in range(3):
                y=table[3*s+i]
                if s in w: need(y in self.raw[3*s+i] and y in w,"unsafe/nonclosed strategy")
                if s in self.b and i<2:
                    need(y in self.b,"subalgebra violation")
                    need(table[3*self.bar[s]+1-i]==self.bar[y],"internal symmetry violation")
        return True

    def single_equation_compatible(self):
        # For fixed Q, exactly the Boolean flattened rows need complement invariance.
        for s in self.b:
            for i in (0,1):
                need({self.bar[y] for y in self.raw[3*s+i] & self.b} ==
                     self.raw[3*self.bar[s]+1-i] & self.b,"nondefinable safety relation")
        return True

    def check_separator(self):
        """Exhaust all flattened rows; equality exactly R and g is Q-compatible."""
        def value(s,i,y):
            a=self.states[s][0]
            if y in self.raw[3*s+i]: return a
            if s in self.b and i<2 and y in self.b: return 1-a
            return (a+1)%3
        checked=0
        for s in range(self.n):
            for i in range(3):
                for y in range(self.n):
                    g=value(s,i,y); a=self.states[s][0]
                    need((g==a)==(y in self.raw[3*s+i]),"separator equality")
                    if s in self.b and i<2 and y in self.b:
                        need(g in (0,1),"separator subalgebra")
                        need(value(self.bar[s],1-i,self.bar[y])==1-g,"separator equivariance")
                    checked+=1
        return checked

    def verify(self,result,request):
        need(set(request)=={"required","forbidden","weights","decision"},"request fields")
        need(all(result.get(key)==value for key,value in request.items()),"caller request binding")
        expected_fields={"schema","game_sha256","required","forbidden","weights","decision",
                         "status","stats","domain","score","strategy","proof"}
        need(set(result)==expected_fields,"result fields")
        need(result["schema"]=="orbit-synthesis/q-obstruction-result/v1","result schema")
        canonical=json.dumps(self.wire,sort_keys=True,separators=(",", ":")).encode()
        need(result["game_sha256"]==hashlib.sha256(canonical).hexdigest(),"game binding")
        required=self.unpack(result["required"]); forbidden=self.unpack(result["forbidden"])
        weights=result["weights"]
        need(type(weights) is list and len(weights)==self.n and
             all(type(v) is int and v>=0 for v in weights),"objective")
        need(type(result["decision"]) is bool,"decision flag")
        initial=set(range(self.n))-forbidden
        re=self.envelope(initial)
        d=sum(s<self.bar[s] and s in re and self.bar[s] in re for s in self.b)
        stats={"nodes":0,"splits":0,"feasible_leaves":0,"required_rejections":0,
               "max_depth":0,"initial_pairs":d,"root_envelope_size":len(re)}
        leaves=[]
        def walk(node,allowed,depth):
            need(type(node) is dict,"proof node")
            kind=node.get("kind")
            fields={"allowed","envelope","removed","kind"}
            if kind=="split": fields|={"pair","input","children"}
            if "short_circuit" in node:
                need(kind=="split" and result["decision"] and node["short_circuit"] is True,"short-circuit use")
                fields.add("short_circuit")
            need(set(node)==fields,"node fields")
            stats["nodes"]+=1; stats["max_depth"]=max(stats["max_depth"],depth)
            need(self.unpack(node["allowed"])==allowed,"branch scope")
            w=set(allowed)
            need(type(node["removed"]) is list,"round list")
            for removed in node["removed"]:
                dead=self.unpack(removed)
                need(bool(dead) and dead==w-self.local(w),"deletion round")
                w-=dead
            need(self.local(w)==w and self.unpack(node["envelope"])==w,"greatest envelope")
            if kind=="required_missing":
                need(bool(required-w),"false required rejection")
                stats["required_rejections"]+=1
                return False
            need(required<=w,"required state omitted")
            if kind=="feasible":
                need(self.feasible(w),"false feasible leaf")
                leaves.append(w); stats["feasible_leaves"]+=1
                return True
            need(kind=="split","node kind")
            pair=node["pair"]; i=node["input"]
            need(type(pair) is list and len(pair)==2 and all(type(v) is int for v in pair),"pair fields")
            s,t=pair
            need(s in self.b and t==self.bar[s] and s<t and s in w and t in w,"split pair")
            need(type(i) is int and i in (0,1),"split input")
            left=self.rows[3*s+i]&w; right=self.rows[3*t+1-i]&w
            need(not any(self.bar[y] in right for y in left),"false obstruction")
            children=node["children"]
            need(type(children) is list and len(children) in (1,2),"branch count")
            stats["splits"]+=1
            first=walk(children[0],w-{s},depth+1)
            if len(children)==1:
                need(result["decision"] and node.get("short_circuit") is True and first,"omitted branch")
                return True
            second=walk(children[1],w-{t},depth+1)
            if "short_circuit" in node: need(second,"invalid short circuit")
            return first or second
        walk(result["proof"],initial,0)
        need(result["stats"]==stats,"stats")
        need(stats["max_depth"]<=d and stats["nodes"]<=2**(d+1)-1,"parameter bound")
        if not leaves:
            need(result["status"]=="infeasible" and result["domain"] is None and
                 result["strategy"] is None and result["score"] is None,"false infeasibility result")
        else:
            key=lambda w:(sum(weights[s] for s in w),len(w),sum(1<<s for s in w))
            best=max(leaves,key=key)
            need(result["status"]=="feasible" and self.unpack(result["domain"])==best,"wrong selected leaf")
            need(type(result["score"]) is int and result["score"]==sum(weights[s] for s in best),"score")
            self.strategy(best,result["strategy"])
        return True


def sat_assignments(clauses,nvars):
    for assignment in itertools.product((False,True),repeat=nvars):
        if all(any(assignment[abs(x)-1]==(x>0) for x in c) for c in clauses):
            yield assignment


def total_q_tables_arity2():
    """Independent enumeration of all 972 scalar Q-compatible binary tables."""
    binary={(0,0),(0,1),(1,0),(1,1)}
    allrows=list(itertools.product(range(3),repeat=2)); indices={v:i for i,v in enumerate(allrows)}
    rigid=[v for v in allrows if v not in binary]
    for a,b in itertools.product((0,1),repeat=2):
        base={(0,0):a,(1,1):1-a,(0,1):b,(1,0):1-b}
        for values in itertools.product(range(3),repeat=5):
            table=base|dict(zip(rigid,values))
            yield [table[v] for v in allrows]
